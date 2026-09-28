from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.game import GameCreate, GameUpdate, GameResponse
from app.schemas.pagination import PaginatedResponse
import app.services.game_service as service

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)


@router.get(
    "/",
    response_model=PaginatedResponse[GameResponse],
    summary="List games with filters & pagination",
    description="Query games by category, text search, price range, rating threshold, and pagination."
)
def read_games(
    category_id: Optional[int] = Query(None, description="Filter games by Category ID"),
    search: Optional[str] = Query(None, description="Search term matching title or description"),
    min_price: Optional[float] = Query(None, ge=0.0, description="Minimum retail price"),
    max_price: Optional[float] = Query(None, ge=0.0, description="Maximum retail price"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0, description="Minimum rating score (0-10)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    return service.get_paginated_games(
        db=db,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        is_active=is_active,
        page=page,
        page_size=page_size
    )


@router.get(
    "/{game_id}",
    response_model=GameResponse,
    summary="Get game by ID",
    description="Retrieve full details of a video game including its nested relational category."
)
def read_game(
    game_id: int,
    db: Session = Depends(get_db)
):
    game = service.get_game_by_id(db=db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with id {game_id} not found."
        )
    return game


@router.post(
    "/",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new game",
    description="Insert a new game entry linked to an existing category."
)
def create_new_game(
    game_in: GameCreate,
    db: Session = Depends(get_db)
):
    return service.create_game(db=db, game_in=game_in)


@router.put(
    "/{game_id}",
    response_model=GameResponse,
    summary="Update an existing game",
    description="Update attributes of a game, including optional category reassignment."
)
def update_existing_game(
    game_id: int,
    game_in: GameUpdate,
    db: Session = Depends(get_db)
):
    updated = service.update_game(db=db, game_id=game_id, game_in=game_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with id {game_id} not found."
        )
    return updated


@router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a game",
    description="Permanently remove a game record from the catalog."
)
def remove_game(
    game_id: int,
    db: Session = Depends(get_db)
):
    deleted = service.delete_game(db=db, game_id=game_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with id {game_id} not found."
        )
    return None
