from app.graph.state import PostState
from app.services.naver import post_to_naver_blog
from app.services.instagram import post_to_instagram


async def post_publisher_node(state: PostState) -> PostState:
    """Publish the generated content to the target platform."""
    platform = state["platform"]
    social_token = state.get("social_token")

    if not social_token:
        return {**state, "error": "소셜 토큰이 없습니다."}

    try:
        if platform == "naver":
            url = await post_to_naver_blog(
                access_token=social_token,
                title=state.get("generated_title", ""),
                content=state.get("generated_content", ""),
                hashtags=state.get("generated_hashtags", []),
            )
        elif platform == "instagram":
            instagram_user_id = state.get("instagram_user_id")
            if not instagram_user_id:
                return {**state, "error": "Instagram 사용자 ID가 없습니다."}

            caption = f"{state.get('generated_title', '')}\n\n{state.get('generated_content', '')}"
            url = await post_to_instagram(
                access_token=social_token,
                instagram_user_id=instagram_user_id,
                caption=caption,
                hashtags=state.get("generated_hashtags", []),
            )
        else:
            return {**state, "error": f"지원하지 않는 플랫폼: {platform}"}

        return {**state, "published_url": url}

    except RuntimeError as e:
        return {**state, "error": str(e)}
