import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from app.auth.jwt_verify import verify_jwt
from app.graph.workflow import workflow

router = APIRouter(prefix="/api/posts", tags=["posts"])


class PostRequest(BaseModel):
    platform: str
    keyword: Optional[str] = None


class PostResponse(BaseModel):
    success: bool
    post_history_id: Optional[int] = None
    published_url: Optional[str] = None
    generated_title: Optional[str] = None
    generated_content: Optional[str] = None
    generated_hashtags: Optional[list] = None
    error: Optional[str] = None


@router.post("/generate", response_model=PostResponse)
async def generate_and_post(
    platform: str = Form(...),
    keyword: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(verify_jwt),
):
    if platform not in ("naver", "instagram"):
        raise HTTPException(status_code=400, detail="platform은 'naver' 또는 'instagram'이어야 합니다.")

    if not keyword and not image:
        raise HTTPException(status_code=400, detail="keyword 또는 image 중 하나는 필수입니다.")

    # Prepare state
    initial_state = {
        "user_id": current_user["user_id"],
        "platform": platform,
        "keyword": keyword,
        "retry_count": 0,
    }

    if image:
        image_bytes = await image.read()
        initial_state["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")
        initial_state["image_mime_type"] = image.content_type or "image/jpeg"

    # Run LangGraph workflow
    result = await workflow.ainvoke(initial_state)

    if result.get("error"):
        return PostResponse(success=False, error=result["error"])

    return PostResponse(
        success=True,
        post_history_id=result.get("post_history_id"),
        published_url=result.get("published_url"),
        generated_title=result.get("generated_title"),
        generated_content=result.get("generated_content"),
        generated_hashtags=result.get("generated_hashtags"),
    )


@router.post("/preview", response_model=PostResponse)
async def preview_post(
    platform: str = Form(...),
    keyword: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(verify_jwt),
):
    """Generate content without publishing (preview mode)."""
    if platform not in ("naver", "instagram"):
        raise HTTPException(status_code=400, detail="platform은 'naver' 또는 'instagram'이어야 합니다.")

    if not keyword and not image:
        raise HTTPException(status_code=400, detail="keyword 또는 image 중 하나는 필수입니다.")

    initial_state = {
        "user_id": current_user["user_id"],
        "platform": platform,
        "keyword": keyword,
        "retry_count": 0,
        # Mark as preview — skip publisher node by injecting a mock social token
        "social_token": "preview_mode",
    }

    if image:
        image_bytes = await image.read()
        initial_state["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")
        initial_state["image_mime_type"] = image.content_type or "image/jpeg"

    # Run only up to quality check (not publish)
    from app.graph.nodes.input_parser import input_parser_node
    from app.graph.nodes.image_analyzer import image_analyzer_node
    from app.graph.nodes.content_generator import content_generator_node
    from app.graph.nodes.quality_checker import quality_checker_node

    state = initial_state
    state = await input_parser_node(state)
    if state.get("input_type") == "image":
        state = await image_analyzer_node(state)
    state = await content_generator_node(state)
    state = await quality_checker_node(state)

    if state.get("error"):
        return PostResponse(success=False, error=state["error"])

    return PostResponse(
        success=True,
        generated_title=state.get("generated_title"),
        generated_content=state.get("generated_content"),
        generated_hashtags=state.get("generated_hashtags"),
    )
