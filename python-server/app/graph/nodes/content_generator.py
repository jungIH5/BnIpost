import json
import re
import anthropic
from app.graph.state import PostState
from app.config import get_settings

settings = get_settings()
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

NAVER_SYSTEM_PROMPT = """당신은 네이버 블로그 전문 작가입니다.
- 검색 최적화를 위해 자연스럽게 키워드를 반복 사용하세요.
- 소제목(##)을 적절히 활용하여 구조화된 글을 작성하세요.
- 본문은 600자 이상 1500자 이하로 작성하세요.
- 독자가 끝까지 읽고 싶어지는 흥미로운 내용을 담으세요.
- 마지막에 방문자 참여를 유도하는 문장을 추가하세요."""

INSTAGRAM_SYSTEM_PROMPT = """당신은 인스타그램 콘텐츠 전문가입니다.
- 캡션은 임팩트 있는 첫 줄로 시작하세요 (이모지 활용 권장).
- 감성적이고 공감 가는 스토리텔링을 사용하세요.
- 본문은 150자 이상 300자 이하로 간결하게 작성하세요.
- 해시태그는 관련성 높은 것 15-20개를 선별하세요.
- 팔로우/저장/공유를 유도하는 Call-to-Action을 포함하세요."""


def build_user_prompt(state: PostState) -> str:
    platform = state["platform"]
    quality_feedback = state.get("quality_feedback", "")
    retry_count = state.get("retry_count", 0)

    if state.get("image_description"):
        content_basis = f"[이미지 분석 결과]\n{state['image_description']}"
    else:
        content_basis = f"[주제 키워드]\n{state['keyword']}"

    retry_note = ""
    if retry_count > 0 and quality_feedback:
        retry_note = f"\n\n[이전 시도 피드백 - 반드시 반영할 것]\n{quality_feedback}"

    if platform == "naver":
        return (
            f"{content_basis}{retry_note}\n\n"
            "위 내용을 바탕으로 네이버 블로그 게시물을 작성해주세요.\n"
            "반드시 아래 JSON 형식으로만 응답하세요:\n"
            '{"title": "제목", "content": "본문 (마크다운 허용)", "hashtags": ["태그1", "태그2", ...]}'
        )
    else:
        return (
            f"{content_basis}{retry_note}\n\n"
            "위 내용을 바탕으로 인스타그램 게시물을 작성해주세요.\n"
            "반드시 아래 JSON 형식으로만 응답하세요:\n"
            '{"title": "첫 줄 (임팩트 있게)", "content": "캡션 본문", "hashtags": ["태그1", "태그2", ...]}'
        )


async def content_generator_node(state: PostState) -> PostState:
    """Generate platform-specific content using Claude."""
    platform = state["platform"]
    system_prompt = NAVER_SYSTEM_PROMPT if platform == "naver" else INSTAGRAM_SYSTEM_PROMPT

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": build_user_prompt(state)}],
        )

        raw = message.content[0].text.strip()

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not json_match:
            raise ValueError("응답에서 JSON을 찾을 수 없습니다.")

        data = json.loads(json_match.group())
        return {
            **state,
            "generated_title": data.get("title", ""),
            "generated_content": data.get("content", ""),
            "generated_hashtags": data.get("hashtags", []),
        }

    except (anthropic.APIError, json.JSONDecodeError, ValueError) as e:
        return {**state, "error": f"콘텐츠 생성 실패: {str(e)}"}
