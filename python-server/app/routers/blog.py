from fastapi import APIRouter, Depends, HTTPException
from app.auth.jwt_verify import verify_jwt
from app.services.rss import fetch_naver_blog

router = APIRouter(prefix="/api/blog", tags=["blog"])


@router.get("/naver/{blog_id}")
async def get_naver_blog(
    blog_id: str,
    current_user: dict = Depends(verify_jwt),
):
    """네이버 블로그 RSS를 읽어 게시물 목록과 블로그 정보를 반환합니다."""
    try:
        return await fetch_naver_blog(blog_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
