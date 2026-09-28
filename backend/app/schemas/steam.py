from typing import Optional, List
from pydantic import BaseModel, Field


class SteamSearchItem(BaseModel):
    """
    Item representation of a game returned from Steam Store search.
    """
    id: int = Field(..., description="Steam Application ID (AppID)")
    name: str = Field(..., description="Steam game title")
    price: Optional[float] = Field(None, description="Current price in USD or 0.0 for free-to-play")
    image_url: Optional[str] = Field(None, description="Small capsule/thumbnail image URL")


class SteamSearchResponse(BaseModel):
    """
    Search response envelope for Steam Store query.
    """
    total: int = Field(..., description="Total matching games found on Steam")
    query: str = Field(..., description="Original search term")
    items: List[SteamSearchItem] = Field(default_factory=list, description="List of matching games")


class SteamStatsResponse(BaseModel):
    """
    Live stats response for a game linked with Steam.
    """
    game_id: int = Field(..., description="Internal database game ID")
    steam_app_id: int = Field(..., description="Steam Application ID")
    player_count: Optional[int] = Field(None, description="Number of currently active players")
    is_online: bool = Field(..., description="Whether live stats were successfully retrieved")
    service: str = Field("Steam Web API", description="External stats provider")
