import json
import re
import anthropic
from app.graph.state import PostState
from app.config import get_settings

settings = get_settings()
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

MAX_RETRIES = 3

QUALITY_RULES = {
    "naver": {
        "min_content_length": 600,
        "max_content_length": 1500,
        "min_hashtags": 3,
        "max_hashtags": 30,
    },
    "instagram": {
        "min_content_length": 100,
        "max_content_length": 350,
        "min_hashtags": 10,
        "max_hashtags": 30,
    },
}


def rule_check(state: PostState) -> tuple[bool, str]:
    """Fast rule-based pre-check before expensive AI evaluation."""
    platform = state["platform"]
    rules = QUALITY_RULES[platform]
    content = state.get("generated_content", "")
    hashtags = state.get("generated_hashtags", [])

    if len(content) < rules["min_content_length"]:
        return False, f"본문이 너무 짧습니다. 최소 {rules['min_content_length']}자 이상 작성해주세요. (현재 {len(content)}자)"
    if len(content) > rules["max_content_length"]:
        return False, f"본문이 너무 깁니다. {rules['max_content_length']}자 이내로 줄여주세요. (현재 {len(content)}자)"
    if len(hashtags) < rules["min_hashtags"]:
        return False, f"해시태그가 부족합니다. 최소 {rules['min_hashtags']}개 이상 추가해주세요. (현재 {len(hashtags)}개)"
    if not state.get("generated_title"):
        return False, "제목이 없습니다."

    return True, ""


async def quality_checker_node(state: PostState) -> PostState:
    """Check content quality. On failure, provide feedback for regeneration."""
    retry_count = state.get("retry_count", 0)

    if retry_count >= MAX_RETRIES:
        return {**state, "quality_passed": False, "error": f"최대 재시도 횟수({MAX_RETRIES}회)를 초과했습니다."}

    # Rule-based check first
    rule_passed, rule_feedback = rule_check(state)
    if not rule_passed:
        return {
            **state,
            "quality_passed": False,
            "quality_feedback": rule_feedback,
            "retry_count": retry_count + 1,
        }

    # AI-based quality evaluation
    platform_name = "네이버 블로그" if state["platform"] == "naver" else "인스타그램"
    eval_prompt = (
        f"다음 {platform_name} 게시물의 품질을 평가해주세요.\n\n"
        f"제목: {state.get('generated_title')}\n"
        f"본문: {state.get('generated_content')}\n"
        f"해시태그: {', '.join(state.get('generated_hashtags', []))}\n\n"
        "평가 기준:\n"
        "1. 자연스럽고 매력적인 문체인가?\n"
        "2. 주제에 집중하고 있는가?\n"
        "3. 독자가 관심을 가질 만한 내용인가?\n\n"
        "아래 JSON 형식으로만 응답하세요:\n"
        '{"passed": true/false, "feedback": "개선이 필요한 경우 구체적인 피드백, 통과면 빈 문자열"}'
    )

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": eval_prompt}],
        )
        raw = message.content[0].text.strip()
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not json_match:
            # If can't parse, assume passed to avoid infinite loop
            return {**state, "quality_passed": True}

        result = json.loads(json_match.group())
        passed = result.get("passed", True)
        feedback = result.get("feedback", "")

        return {
            **state,
            "quality_passed": passed,
            "quality_feedback": feedback if not passed else "",
            "retry_count": retry_count + 1 if not passed else retry_count,
        }

    except Exception:
        # On evaluation error, pass through to avoid blocking the workflow
        return {**state, "quality_passed": True}
