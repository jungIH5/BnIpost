import base64
import anthropic
from app.graph.state import PostState
from app.config import get_settings

settings = get_settings()
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


async def image_analyzer_node(state: PostState) -> PostState:
    """Analyze image using Claude Vision and generate a description."""
    if state.get("input_type") != "image" or not state.get("image_base64"):
        return state  # Skip if not image input

    platform = state["platform"]
    platform_hint = "네이버 블로그" if platform == "naver" else "인스타그램"

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": state.get("image_mime_type", "image/jpeg"),
                                "data": state["image_base64"],
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                f"이 이미지를 분석해서 {platform_hint} 게시물 작성에 활용할 수 있도록 "
                                "다음을 한국어로 설명해주세요:\n"
                                "1. 이미지의 주요 피사체와 상황\n"
                                "2. 분위기와 감성\n"
                                "3. 게시물에 활용할 수 있는 키워드 5개\n"
                                "4. 추천 게시물 방향\n"
                                "JSON 형식 없이 자연스러운 텍스트로 작성해주세요."
                            ),
                        },
                    ],
                }
            ],
        )
        description = message.content[0].text
        return {**state, "image_description": description}

    except anthropic.APIError as e:
        return {**state, "error": f"이미지 분석 실패: {str(e)}"}
