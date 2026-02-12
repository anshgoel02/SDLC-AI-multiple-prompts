from __future__ import annotations

from langgraph.graph import END, StateGraph

from .models import BRDState
from .nodes.assembly_nodes import assembler_node, persist_doc_node
from .nodes.fact_nodes import fact_extractor_node
from .nodes.gap_nodes import gap_checker_node, gap_human_review_node
from .nodes.intake_nodes import intake_node, load_sources_node
from .nodes.outline_nodes import outline_builder_node
from .nodes.review_nodes import apply_feedback_node, human_review_node
from .nodes.section_nodes import section_writer_node


def build_graph() -> StateGraph:
    graph = StateGraph(BRDState)
    graph.add_node("load_sources", load_sources_node)
    graph.add_node("intake", intake_node)
    graph.add_node("fact_extractor", fact_extractor_node)
    graph.add_node("gap_checker", gap_checker_node)
    graph.add_node("gap_human_review", gap_human_review_node)
    graph.add_node("outline_builder", outline_builder_node)
    graph.add_node("section_writer", section_writer_node)
    graph.add_node("assembler", assembler_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("persist_doc", persist_doc_node)
    graph.add_node("apply_feedback", apply_feedback_node)

    graph.set_entry_point("load_sources")
    graph.add_edge("load_sources", "intake")
    graph.add_edge("intake", "fact_extractor")
    graph.add_edge("fact_extractor", "gap_checker")
    graph.add_edge("gap_checker", "gap_human_review")

    def gap_branch(state: BRDState) -> str:
        has_gaps = bool(state.gaps.blocking or state.gaps.non_blocking)
        if not has_gaps:
            return "outline_builder"
        return "outline_builder" if state.user_force_generate else "fact_extractor"

    graph.add_conditional_edges(
        "gap_human_review",
        gap_branch,
        {"outline_builder": "outline_builder", "fact_extractor": "fact_extractor"},
    )

    graph.add_edge("outline_builder", "section_writer")
    graph.add_edge("section_writer", "assembler")
    graph.add_edge("assembler", "human_review")

    def review_branch(state: BRDState) -> str:
        return "persist_doc" if state.approved else "apply_feedback"

    graph.add_conditional_edges(
        "human_review",
        review_branch,
        {"persist_doc": "persist_doc", "apply_feedback": "apply_feedback"},
    )
    graph.add_edge("apply_feedback", "outline_builder")
    graph.add_edge("persist_doc", END)

    return graph
