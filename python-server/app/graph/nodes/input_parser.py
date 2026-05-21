import httpx
from app.graph.state import PostState
from app.config import get_settings

settings = get_settings()


async def input_parser_node(state: PostState) -> PostState:
    """Validate input and fetch social token from Java server."""
    if not state.get("keyword") and not state.get("image_base64"):
        return {**state, "error": "키워드 또는 이미지를 입력해주세요."}

    input_type = "image" if state.get("image_base64") else "keyword"

    # Fetch social token from Java server
    platform = state["platform"]
    user_id = state["user_id"]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{settings.java_server_url}/api/users/internal/token",
                params={"userId": user_id, "platform": platform},
                headers={"X-Internal-Key": settings.internal_api_key}
            )
            if resp.status_code == 404:
                return {**state, "error": f"{platform} 계정이 연결되지 않았습니다. 로그인 후 다시 시도해주세요."}
            if resp.status_code != 200:
                return {**state, "error": "소셜 토큰 조회 실패"}

            token_data = resp.json()
            social_token = token_data.get("token")
            instagram_user_id = token_data.get("instagram_user_id")

    except httpx.RequestError as e:
        return {**state, "error": f"Java 서버 통신 오류: {str(e)}"}

    return {
        **state,
        "input_type": input_type,
        "social_token": social_token,
        "instagram_user_id": instagram_user_id,
        "retry_count": state.get("retry_count", 0),
    }
