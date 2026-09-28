from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryResponse


class GameBase(BaseModel):
    """
    Shared attributes for video game entities.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the video game",
        examples=["The Witcher 3: Wild Hunt"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description or synopsis of the game",
        examples=["An open world story-driven action RPG set in a dark fantasy universe."]
    )
    price: float = Field(
        default=0.0,
        ge=0.0,
        description="Retail price in USD/EUR. 0.0 for free-to-play games.",
        examples=[29.99]
    )
    release_year: Optional[int] = Field(
        None,
        ge=1970,
        le=2100,
        description="Year of official release",
        examples=[2015]
    )
    rating: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="Average review rating out of 10.0",
        examples=[9.8]
    )
    is_active: bool = Field(
        default=True,
        description="Denotes whether the game is currently listed/active",
        examples=[True]
    )
    image_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL pointing to the game cover or header artwork"
    )
    steam_app_id: Optional[int] = Field(
        None,
        gt=0,
        description="Optional Steam AppID for live player statistics and store sync",
        examples=[292030]
    )


class GameCreate(GameBase):
    """
    Schema for manual creation of a game. Requires a valid category_id.
    """
    category_id: int = Field(
        ...,
        gt=0,
        description="Foreign key identifier of the parent category",
        examples=[1]
    )


class GameUpdate(BaseModel):
    """
    Schema for updating a game. All fields are optional.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0.0)
    release_year: Optional[int] = Field(None, ge=1970, le=2100)
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    is_active: Optional[bool] = None
    image_url: Optional[str] = Field(None, max_length=500)
    steam_app_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)


class GameResponse(GameBase):
    """
    Output representation of a video game, including database metadata and nested category.
    """
    id: int = Field(..., description="Unique database identifier", examples=[1])
    category_id: int = Field(..., description="Foreign key of the associated category")
    created_at: datetime = Field(..., description="Timestamp of record creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")
    category: Optional[CategoryResponse] = Field(
        default=None,
        description="Nested relational details of the parent category"
    )

    model_config = ConfigDict(from_attributes=True)
