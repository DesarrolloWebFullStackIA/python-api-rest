from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.game import Game
from app.schemas.game import GameResponse
from app.schemas.steam import SteamSearchResponse, SteamStatsResponse
from app.services.steam_service import SteamService

router = APIRouter(tags=["Steam Integration"])


@router.get("/steam/search", response_model=SteamSearchResponse, summary="Search Steam Store")
async def search_steam_catalog(
    query: str = Query(..., min_length=1, description="Title or keyword to search on Steam"),
    limit: int = Query(10, ge=1, le=25, description="Maximum number of items to return")
):
    """
    Search official Steam Store games using public endpoints.
    Requires no developer API key.
    """
    return await SteamService.search_steam_games(query=query, limit=limit)


@router.post(
    "/games/steam/{app_id}",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
    summary="1-Click Import game from Steam"
)
async def import_game_from_steam(
    app_id: int = Path(..., ge=1, description="Steam Application ID (AppID) to import"),
    db: Session = Depends(get_db)
):
    """
    1-Click Import from Steam:
    - Fetches official game metadata (title, description, price, release year, Metacritic rating).
    - Automatically finds or creates the corresponding relational **Category**.
    - Stores the game in the database linked to that category and returns the created entity.
    """
    return await SteamService.import_game_from_steam(db=db, app_id=app_id)


@router.get(
    "/games/{id}/steam-stats",
    response_model=SteamStatsResponse,
    summary="Get real-time concurrent players for a game"
)
async def get_game_steam_stats(
    id: int = Path(..., ge=1, description="Internal database ID of the game"),
    db: Session = Depends(get_db)
):
    """
    Query real-time concurrent player counts from Steam for games linked to a Steam AppID.
    """
    game = db.query(Game).filter(Game.id == id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with ID {id} was not found."
        )

    if not game.steam_app_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Game '{game.title}' is not linked to a Steam Application ID."
        )

    player_count = await SteamService.get_concurrent_players(game.steam_app_id)

    return SteamStatsResponse(
        game_id=game.id,
        steam_app_id=game.steam_app_id,
        player_count=player_count,
        is_online=player_count is not None
    )
