from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_

from app.models.game import Game
from app.schemas.game import GameCreate, GameUpdate, GameResponse
from app.schemas.pagination import PaginatedResponse
from app.services.category_service import get_category_by_id


def get_paginated_games(
    db: Session,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 10
) -> PaginatedResponse[GameResponse]:
    """
    Retrieve a paginated collection of games with multi-criteria filtering:
    - category_id filter
    - search query (matches title or description)
    - price ranges (min_price, max_price)
    - rating threshold (min_rating)
    - active status
    """
    try:
        conditions = []

        if category_id is not None:
            conditions.append(Game.category_id == category_id)

        if search and search.strip():
            term = f"%{search.strip()}%"
            conditions.append(
                or_(
                    Game.title.ilike(term),
                    Game.description.ilike(term)
                )
            )

        if min_price is not None:
            conditions.append(Game.price >= min_price)

        if max_price is not None:
            conditions.append(Game.price <= max_price)

        if min_rating is not None:
            conditions.append(Game.rating >= min_rating)

        if is_active is not None:
            conditions.append(Game.is_active == is_active)

        # Count total matching rows
        count_stmt = select(func.count(Game.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = db.execute(count_stmt).scalar() or 0

        # Query paginated rows with joinedload to eliminate N+1 queries
        query_stmt = (
            select(Game)
            .options(joinedload(Game.category))
            .order_by(Game.id.desc())
        )
        if conditions:
            query_stmt = query_stmt.where(*conditions)

        offset = (page - 1) * page_size
        query_stmt = query_stmt.offset(offset).limit(page_size)

        games_entities = db.execute(query_stmt).scalars().unique().all()
        items = [GameResponse.model_validate(g) for g in games_entities]

        return PaginatedResponse.create(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while querying games: {str(err)}"
        )


def get_game_by_id(db: Session, game_id: int) -> Optional[Game]:
    """
    Fetch a single game by ID with its eager-loaded category.
    """
    try:
        stmt = select(Game).options(joinedload(Game.category)).where(Game.id == game_id)
        return db.execute(stmt).scalars().first()
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching game {game_id}: {str(err)}"
        )


def create_game(db: Session, game_in: GameCreate) -> Game:
    """
    Create a new game record.
    Enforces relational integrity: validates that the referenced category_id exists.
    """
    category = get_category_by_id(db, game_in.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {game_in.category_id} does not exist. Cannot create game."
        )

    game = Game(
        title=game_in.title.strip(),
        description=game_in.description.strip() if game_in.description else None,
        price=game_in.price,
        release_year=game_in.release_year,
        rating=game_in.rating,
        is_active=game_in.is_active,
        image_url=game_in.image_url,
        steam_app_id=game_in.steam_app_id,
        category_id=game_in.category_id
    )

    try:
        db.add(game)
        db.commit()
        db.refresh(game)
        return game
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity violation while creating game: {str(err)}"
        )
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating game: {str(err)}"
        )


def update_game(db: Session, game_id: int, game_in: GameUpdate) -> Optional[Game]:
    """
    Update an existing game's attributes.
    If category_id is modified, validates referential integrity.
    """
    game = get_game_by_id(db, game_id)
    if not game:
        return None

    if game_in.category_id is not None and game_in.category_id != game.category_id:
        target_category = get_category_by_id(db, game_in.category_id)
        if not target_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target category with id {game_in.category_id} does not exist."
            )

    update_data = game_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(game, field, value)

    try:
        db.commit()
        db.refresh(game)
        return game
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity violation while updating game: {str(err)}"
        )
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while updating game {game_id}: {str(err)}"
        )


def delete_game(db: Session, game_id: int) -> bool:
    """
    Delete a game by ID. Returns True if deleted, False if not found.
    """
    game = get_game_by_id(db, game_id)
    if not game:
        return False

    try:
        db.delete(game)
        db.commit()
        return True
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while deleting game {game_id}: {str(err)}"
        )
