import re
from typing import Optional, List
import httpx
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.game import Game
from app.schemas.steam import SteamSearchItem, SteamSearchResponse, SteamStatsResponse


class SteamService:
    """
    Service handling integration with official public Steam Web and Storefront endpoints.
    Requires no developer API key.
    """

    STEAM_SEARCH_URL = "https://store.steampowered.com/api/storesearch/"
    STEAM_APPDETAILS_URL = "https://store.steampowered.com/api/appdetails"
    STEAM_PLAYERS_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VaporStore/1.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    @classmethod
    async def search_steam_games(cls, query: str, limit: int = 10) -> SteamSearchResponse:
        """
        Search public Steam Store catalog by term.
        """
        clean_query = query.strip()
        if not clean_query:
            return SteamSearchResponse(total=0, query=query, items=[])

        params = {
            "term": clean_query,
            "l": "english",
            "cc": "US"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=cls.HEADERS) as client:
                response = await client.get(cls.STEAM_SEARCH_URL, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to communicate with Steam Store API: {str(exc)}"
            )

        items_raw = data.get("items", [])[:limit]
        items: List[SteamSearchItem] = []

        for raw in items_raw:
            price_val = 0.0
            price_obj = raw.get("price")
            if price_obj and isinstance(price_obj, dict):
                # Steam returns prices in cents
                price_val = round(price_obj.get("final", 0) / 100.0, 2)

            items.append(
                SteamSearchItem(
                    id=raw["id"],
                    name=raw["name"],
                    price=price_val,
                    image_url=raw.get("tiny_image")
                )
            )

        return SteamSearchResponse(
            total=data.get("total", len(items)),
            query=clean_query,
            items=items
        )

    @classmethod
    async def get_app_details(cls, app_id: int) -> dict:
        """
        Fetch complete metadata for a Steam Application ID.
        """
        params = {
            "appids": app_id,
            "cc": "US",
            "l": "en"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=cls.HEADERS) as client:
                response = await client.get(cls.STEAM_APPDETAILS_URL, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch Steam app details for AppID {app_id}: {str(exc)}"
            )

        app_key = str(app_id)
        if not payload or app_key not in payload or not payload[app_key].get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Steam application with AppID {app_id} was not found or has no public store page."
            )

        return payload[app_key]["data"]

    @classmethod
    async def get_concurrent_players(cls, app_id: int) -> Optional[int]:
        """
        Fetch real-time count of concurrent active players on Steam.
        """
        params = {"appid": app_id}

        try:
            async with httpx.AsyncClient(timeout=8.0, headers=cls.HEADERS) as client:
                response = await client.get(cls.STEAM_PLAYERS_URL, params=params)
                if response.status_code == 200:
                    payload = response.json()
                    res_body = payload.get("response", {})
                    if res_body.get("result") == 1:
                        return res_body.get("player_count")
        except Exception:
            # Stats failures should degrade gracefully without halting the application
            return None

        return None

    @classmethod
    async def import_game_from_steam(cls, db: Session, app_id: int) -> Game:
        """
        1-Click Import: fetches metadata from Steam, automatically links or creates
        the relational Category, and stores the Game in the database.
        """
        # Check if game with this Steam App ID already exists
        existing_steam_game = db.query(Game).filter(Game.steam_app_id == app_id).first()
        if existing_steam_game:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Game with Steam App ID {app_id} ('{existing_steam_game.title}') is already imported in your catalog."
            )

        # Retrieve metadata from Steam
        data = await cls.get_app_details(app_id)

        title = data.get("name", f"Steam App {app_id}")
        short_desc = data.get("short_description") or data.get("detailed_description") or ""
        # Clean HTML tags from description if present
        clean_desc = re.sub(r'<[^>]+>', '', short_desc).strip()
        if len(clean_desc) > 800:
            clean_desc = clean_desc[:797] + "..."

        # Calculate price
        price = 0.0
        if not data.get("is_free", False):
            price_overview = data.get("price_overview")
            if price_overview and isinstance(price_overview, dict):
                price = round(price_overview.get("final", 0) / 100.0, 2)

        # Extract release year
        release_year = None
        release_date_str = data.get("release_date", {}).get("date", "")
        year_match = re.search(r'\b(19\d\d|20\d\d)\b', release_date_str)
        if year_match:
            release_year = int(year_match.group(1))

        # Extract rating from Metacritic score
        rating = None
        metacritic = data.get("metacritic")
        if metacritic and isinstance(metacritic, dict) and "score" in metacritic:
            rating = round(metacritic["score"] / 10.0, 1)

        # Cover header image
        image_url = data.get("header_image")

        # Resolve or auto-create relational Category from Steam genres
        genres = data.get("genres", [])
        genre_name = genres[0]["description"].strip() if genres else "General"
        # Ensure category name doesn't exceed 50 chars
        genre_name = genre_name[:50]

        category = db.query(Category).filter(
            func.lower(Category.name) == genre_name.lower()
        ).first()

        if not category:
            category = Category(
                name=genre_name,
                description=f"Category automatically created from Steam genre: {genre_name}."
            )
            db.add(category)
            db.flush()

        # Create and persist Game
        new_game = Game(
            title=title[:150],
            description=clean_desc,
            price=price,
            release_year=release_year,
            rating=rating,
            is_active=True,
            image_url=image_url,
            steam_app_id=app_id,
            category_id=category.id
        )

        try:
            db.add(new_game)
            db.commit()
            db.refresh(new_game)
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while saving imported Steam game."
            )

        # Re-query with eager joinedload for full relationship response
        return db.query(Game).options(joinedload(Game.category)).filter(Game.id == new_game.id).first()
