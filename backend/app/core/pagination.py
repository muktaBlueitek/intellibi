from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters for API endpoints."""
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum number of records to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Maximum number of items requested")
    has_more: bool = Field(description="Whether there are more items available")

    class Config:
        from_attributes = True


def create_paginated_response(items: List[T], total: int, skip: int, limit: int) -> PaginatedResponse[T]:
    """Helper function to create a paginated response."""
    return PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(items)) < total
    )
