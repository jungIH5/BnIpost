import json
from sqlalchemy import update
from app.graph.state import PostState
from app.models.database import AsyncSessionLocal
from app.models.schemas import PostHistory, PostStatus, Platform


async def history_saver_node(state: PostState) -> PostState:
    """Save the post result to the database."""
    history_id = state.get("post_history_id")
    error = state.get("error")

    status = PostStatus.FAILED if error else PostStatus.PUBLISHED

    async with AsyncSessionLocal() as session:
        try:
            if history_id:
                await session.execute(
                    update(PostHistory)
                    .where(PostHistory.id == history_id)
                    .values(
                        status=status,
                        generated_title=state.get("generated_title"),
                        generated_content=state.get("generated_content"),
                        generated_hashtags=json.dumps(state.get("generated_hashtags", []), ensure_ascii=False),
                        published_url=state.get("published_url"),
                        retry_count=state.get("retry_count", 0),
                        error_message=error,
                    )
                )
            else:
                record = PostHistory(
                    user_id=state["user_id"],
                    platform=Platform(state["platform"]),
                    input_type=state.get("input_type", "keyword"),
                    input_keyword=state.get("keyword"),
                    generated_title=state.get("generated_title"),
                    generated_content=state.get("generated_content"),
                    generated_hashtags=json.dumps(state.get("generated_hashtags", []), ensure_ascii=False),
                    published_url=state.get("published_url"),
                    status=status,
                    retry_count=state.get("retry_count", 0),
                    error_message=error,
                )
                session.add(record)
                await session.flush()
                history_id = record.id

            await session.commit()
        except Exception as e:
            await session.rollback()
            # Don't fail the workflow for DB errors, just log
            return {**state, "post_history_id": history_id}

    return {**state, "post_history_id": history_id}
