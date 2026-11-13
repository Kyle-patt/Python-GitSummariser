"""
API endpoints for retrieving and managing saved repository summary history.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.api.deps import get_db
from backend.app.models.summary import SummaryRecord
from backend.app.schemas.summary import SummaryResponse, HistoryListResponse
from backend.app.core.exceptions import SummaryNotFoundError

router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Summary History",
    description="Returns saved summaries in reverse chronological order with optional filtering by type."
)
def get_history(
    limit: int = Query(20, ge=1, le=100, description="Max number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    summary_type: Optional[str] = Query(None, description="Filter by 'repository' or 'commit'"),
    search: Optional[str] = Query(None, description="Optional search term matching owner or repo name"),
    db: Session = Depends(get_db)
):
    query = db.query(SummaryRecord)

    if summary_type:
        query = query.filter(SummaryRecord.summary_type == summary_type)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            (SummaryRecord.repo_name.ilike(search_filter)) |
            (SummaryRecord.repo_owner.ilike(search_filter)) |
            (SummaryRecord.title.ilike(search_filter))
        )

    total = query.count()
    records = query.order_by(desc(SummaryRecord.created_at)).offset(offset).limit(limit).all()

    return HistoryListResponse(
        total=total,
        items=records
    )


@router.get(
    "/{summary_id}",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Summary by ID",
    description="Retrieves a specific summary by its unique record ID."
)
def get_summary_by_id(
    summary_id: str,
    db: Session = Depends(get_db)
):
    record = db.query(SummaryRecord).filter(SummaryRecord.id == summary_id).first()
    if not record:
        raise SummaryNotFoundError(f"Summary record with ID '{summary_id}' was not found.")
    return record


@router.delete(
    "/{summary_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Summary by ID",
    description="Deletes a saved summary record from the database."
)
def delete_summary_by_id(
    summary_id: str,
    db: Session = Depends(get_db)
):
    record = db.query(SummaryRecord).filter(SummaryRecord.id == summary_id).first()
    if not record:
        raise SummaryNotFoundError(f"Summary record with ID '{summary_id}' was not found.")
    db.delete(record)
    db.commit()
    return None

