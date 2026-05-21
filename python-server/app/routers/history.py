import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from app.auth.jwt_verify import verify_jwt
from app.models.database import get_db
from app.models.schemas import PostHistory
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/history", tags=["history"])


class HistoryItem(BaseModel):
    id: int
    platform: str
    input_type: str
    input_keyword: Optional[str]
    generated_title: Optional[str]
    generated_content: Optional[str]
    generated_hashtags: Optional[List[str]]
    published_url: Optional[str]
    status: str
    retry_count: int
    error_message: Optional[str]
    created_at: Optional[datetime]


@router.get("/", response_model=List[HistoryItem])
async def get_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
    platform: Optional[str] = Query(default=None),
    current_user: dict = Depends(verify_jwt),
    db=Depends(get_db),
):
    user_id = current_user["user_id"]
    offset = (page - 1) * size

    stmt = (
        select(PostHistory)
        .where(PostHistory.user_id == user_id)
        .order_by(desc(PostHistory.created_at))
        .offset(offset)
        .limit(size)
    )
    if platform:
        stmt = stmt.where(PostHistory.platform == platform)

    result = await db.execute(stmt)
    rows = result.scalars().all()

    items = []
    for row in rows:
        hashtags = []
        if row.generated_hashtags:
            try:
                hashtags = json.loads(row.generated_hashtags)
            except Exception:
                hashtags = []
        items.append(HistoryItem(
            id=row.id,
            platform=row.platform.value,
            input_type=row.input_type,
            input_keyword=row.input_keyword,
            generated_title=row.generated_title,
            generated_content=row.generated_content,
            generated_hashtags=hashtags,
            published_url=row.published_url,
            status=row.status.value,
            retry_count=row.retry_count,
            error_message=row.error_message,
            created_at=row.created_at,
        ))

    return items
