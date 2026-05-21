import httpx
from typing import Optional

INSTAGRAM_GRAPH_URL = "https://graph.instagram.com/v19.0"


async def post_to_instagram(
    access_token: str,
    instagram_user_id: str,
    caption: str,
    hashtags: Optional[list] = None,
    image_url: Optional[str] = None,
) -> str:
    """
    Post content to Instagram Business account via Graph API.
    Returns the published post ID/URL.

    Note: Instagram Graph API requires a public image URL for media posts.
    For text-only posts, we use a placeholder approach.
    """
    hashtag_str = " ".join(f"#{tag.lstrip('#')}" for tag in (hashtags or []))
    full_caption = caption + ("\n\n" + hashtag_str if hashtag_str else "")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Create media container
        container_payload: dict = {
            "caption": full_caption,
            "access_token": access_token,
        }

        if image_url:
            container_payload["image_url"] = image_url
            container_payload["media_type"] = "IMAGE"
        else:
            # Reels or carousel — for text posts use a stock image approach
            # In production, integrate image generation (DALL-E etc.)
            container_payload["media_type"] = "REELS"
            container_payload["video_url"] = image_url or ""

        create_resp = await client.post(
            f"{INSTAGRAM_GRAPH_URL}/{instagram_user_id}/media",
            data=container_payload,
        )

        if not create_resp.status_code == 200:
            raise RuntimeError(f"Instagram 미디어 컨테이너 생성 실패: {create_resp.status_code} - {create_resp.text}")

        creation_id = create_resp.json().get("id")

        # Step 2: Publish the container
        publish_resp = await client.post(
            f"{INSTAGRAM_GRAPH_URL}/{instagram_user_id}/media_publish",
            data={"creation_id": creation_id, "access_token": access_token},
        )

        if not publish_resp.status_code == 200:
            raise RuntimeError(f"Instagram 게시 실패: {publish_resp.status_code} - {publish_resp.text}")

        post_id = publish_resp.json().get("id")
        return f"https://www.instagram.com/p/{post_id}/"
