from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.category import Category
from app.models.game import Game
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse


def get_all_categories(db: Session, search: Optional[str] = None) -> List[CategoryResponse]:
    """
    Retrieve all categories with their associated game counts.
    Supports optional case-insensitive substring search by category name.
    """
    try:
        stmt = (
            select(
                Category,
                func.count(Game.id).label("games_count")
            )
            .outerjoin(Game, Category.id == Game.category_id)
            .group_by(Category.id)
            .order_by(Category.name.asc())
        )

        if search:
            stmt = stmt.where(Category.name.ilike(f"%{search.strip()}%"))

        results = db.execute(stmt).all()
        categories: List[CategoryResponse] = []
        for cat, count in results:
            cat_dict = {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "created_at": cat.created_at,
                "updated_at": cat.updated_at,
                "games_count": count
            }
            categories.append(CategoryResponse.model_validate(cat_dict))
        return categories
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while querying categories: {str(err)}"
        )


def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    """
    Fetch a single Category entity by primary key ID.
    """
    try:
        stmt = select(Category).where(Category.id == category_id)
        return db.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching category {category_id}: {str(err)}"
        )


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    """
    Fetch a Category by exact name (case-insensitive).
    """
    try:
        stmt = select(Category).where(Category.name.ilike(name.strip()))
        return db.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching category by name: {str(err)}"
        )


def create_category(db: Session, category_in: CategoryCreate) -> Category:
    """
    Create a new category. Validates uniqueness of category name.
    """
    existing = get_category_by_name(db, category_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_in.name}' already exists."
        )

    category = Category(
        name=category_in.name.strip(),
        description=category_in.description.strip() if category_in.description else None
    )

    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity violation while creating category: {str(err)}"
        )
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating category: {str(err)}"
        )


def update_category(db: Session, category_id: int, category_in: CategoryUpdate) -> Optional[Category]:
    """
    Update an existing category. Validates uniqueness if name is modified.
    """
    category = get_category_by_id(db, category_id)
    if not category:
        return None

    if category_in.name is not None and category_in.name.strip().lower() != category.name.lower():
        conflict = get_category_by_name(db, category_in.name)
        if conflict and conflict.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_in.name}' already exists."
            )

    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(category, field, value)

    try:
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity violation while updating category: {str(err)}"
        )
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while updating category {category_id}: {str(err)}"
        )


def delete_category(db: Session, category_id: int) -> bool:
    """
    Delete a category. Associated games are cascade-deleted.
    Returns True if deleted, False if record not found.
    """
    category = get_category_by_id(db, category_id)
    if not category:
        return False

    try:
        db.delete(category)
        db.commit()
        return True
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while deleting category {category_id}: {str(err)}"
        )
