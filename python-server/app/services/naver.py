import httpx
from typing import Optional


NAVER_BLOG_POST_URL = "https://openapi.naver.com/blog/writePost.json"


async def post_to_naver_blog(
    access_token: str,
    title: str,
    content: str,
    hashtags: Optional[list] = None,
) -> str:
    """Post content to Naver Blog. Returns the post URL."""
    hashtag_str = " ".join(f"#{tag.lstrip('#')}" for tag in (hashtags or []))
    full_content = content + ("\n\n" + hashtag_str if hashtag_str else "")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "title": title,
        "contents": full_content,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(NAVER_BLOG_POST_URL, headers=headers, data=data)

    if resp.status_code not in (200, 201):
        raise RuntimeError(f"네이버 블로그 게시 실패: {resp.status_code} - {resp.text}")

    result = resp.json()
    # Naver blog API returns the post URL in the response
    post_url = result.get("postUrl") or result.get("url") or "https://blog.naver.com"
    return post_url
