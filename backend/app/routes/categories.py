from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
import app.services.category_service as service

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="List all categories",
    description="Retrieve all categories with their associated game counts and optional name search."
)
def read_categories(
    search: Optional[str] = Query(None, description="Filter categories by name substring"),
    db: Session = Depends(get_db)
):
    return service.get_all_categories(db=db, search=search)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category by ID",
    description="Retrieve specific details of a single category by its primary key ID."
)
def read_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = service.get_category_by_id(db=db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found."
        )
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        created_at=category.created_at,
        updated_at=category.updated_at,
        games_count=len(category.games)
    )


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    description="Add a new genre/category to classify games in the catalog."
)
def create_new_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db)
):
    category = service.create_category(db=db, category_in=category_in)
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        created_at=category.created_at,
        updated_at=category.updated_at,
        games_count=0
    )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update an existing category",
    description="Modify category name or description."
)
def update_existing_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db)
):
    updated = service.update_category(db=db, category_id=category_id, category_in=category_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found."
        )
    return CategoryResponse(
        id=updated.id,
        name=updated.name,
        description=updated.description,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        games_count=len(updated.games)
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
    description="Delete a category. Associated games are removed via cascade."
)
def remove_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    deleted = service.delete_category(db=db, category_id=category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found."
        )
    return None
