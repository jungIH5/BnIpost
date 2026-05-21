from langgraph.graph import StateGraph, END
from app.graph.state import PostState
from app.graph.nodes.input_parser import input_parser_node
from app.graph.nodes.image_analyzer import image_analyzer_node
from app.graph.nodes.content_generator import content_generator_node
from app.graph.nodes.quality_checker import quality_checker_node
from app.graph.nodes.post_publisher import post_publisher_node
from app.graph.nodes.history_saver import history_saver_node


def should_analyze_image(state: PostState) -> str:
    if state.get("error"):
        return "save_history"
    if state.get("input_type") == "image":
        return "analyze_image"
    return "generate_content"


def after_image_analysis(state: PostState) -> str:
    if state.get("error"):
        return "save_history"
    return "generate_content"


def after_generation(state: PostState) -> str:
    if state.get("error"):
        return "save_history"
    return "check_quality"


def quality_decision(state: PostState) -> str:
    if state.get("error"):
        return "save_history"
    if state.get("quality_passed"):
        return "publish"
    return "generate_content"  # retry


def after_publish(state: PostState) -> str:
    return "save_history"


def build_workflow() -> StateGraph:
    graph = StateGraph(PostState)

    graph.add_node("parse_input", input_parser_node)
    graph.add_node("analyze_image", image_analyzer_node)
    graph.add_node("generate_content", content_generator_node)
    graph.add_node("check_quality", quality_checker_node)
    graph.add_node("publish", post_publisher_node)
    graph.add_node("save_history", history_saver_node)

    graph.set_entry_point("parse_input")

    graph.add_conditional_edges("parse_input", should_analyze_image, {
        "analyze_image": "analyze_image",
        "generate_content": "generate_content",
        "save_history": "save_history",
    })
    graph.add_conditional_edges("analyze_image", after_image_analysis, {
        "generate_content": "generate_content",
        "save_history": "save_history",
    })
    graph.add_conditional_edges("generate_content", after_generation, {
        "check_quality": "check_quality",
        "save_history": "save_history",
    })
    graph.add_conditional_edges("check_quality", quality_decision, {
        "publish": "publish",
        "generate_content": "generate_content",
        "save_history": "save_history",
    })
    graph.add_conditional_edges("publish", after_publish, {
        "save_history": "save_history",
    })
    graph.add_edge("save_history", END)

    return graph.compile()


# Singleton compiled workflow
workflow = build_workflow()
