from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """
    Shared attributes for categories.
    """
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Unique name of the category/genre",
        examples=["Action", "Role-Playing (RPG)", "Strategy"]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Detailed description of the category",
        examples=["Fast-paced games focusing on physical challenges and reflexes."]
    )


class CategoryCreate(CategoryBase):
    """
    Schema for creating a new category.
    """
    pass


class CategoryUpdate(BaseModel):
    """
    Schema for updating an existing category. All fields are optional.
    """
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Updated name of the category"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated description of the category"
    )


class CategoryResponse(CategoryBase):
    """
    Output representation of a category including database metadata and games count.
    """
    id: int = Field(..., description="Unique database identifier", examples=[1])
    created_at: datetime = Field(..., description="Timestamp of creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")
    games_count: int = Field(default=0, description="Total number of games in this category")

    model_config = ConfigDict(from_attributes=True)
