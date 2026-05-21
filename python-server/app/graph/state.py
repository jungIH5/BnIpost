from typing import Optional, List, Annotated
from typing_extensions import TypedDict


class PostState(TypedDict):
    # Input
    user_id: int
    platform: str               # "naver" | "instagram"
    input_type: str             # "keyword" | "image"
    keyword: Optional[str]
    image_base64: Optional[str] # base64 encoded image
    image_mime_type: Optional[str]

    # Intermediate
    image_description: Optional[str]
    generated_title: Optional[str]
    generated_content: Optional[str]
    generated_hashtags: Optional[List[str]]

    # Quality control
    quality_passed: Optional[bool]
    quality_feedback: Optional[str]
    retry_count: int

    # Social tokens (fetched from Java server)
    social_token: Optional[str]
    instagram_user_id: Optional[str]

    # Output
    published_url: Optional[str]
    post_history_id: Optional[int]
    error: Optional[str]
