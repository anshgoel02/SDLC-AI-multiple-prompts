from __future__ import annotations

from ..debug import debug_state
from ..models import BRDState


def human_review_node(state: BRDState) -> BRDState:
    print("[node] human_review")
    print("\n--- GENERATED BRD ---\n")
    print(state.brd_markdown)
    choice = input("Approve BRD? (y/n): ").strip().lower()
    if choice in {"y", "yes"}:
        state.approved = True
        state.human_feedback = None
    else:
        state.approved = False
        state.human_feedback = input("Provide feedback or corrections: ").strip()
    print("[node] human_review tokens_used=0")
    debug_state("human_review", state)
    return state


def apply_feedback_node(state: BRDState) -> BRDState:
    print("[node] apply_feedback")
    if not state.human_feedback:
        print("[node] apply_feedback tokens_used=0")
        debug_state("apply_feedback", state)
        return state
    state.section_drafts = []
    print("[node] apply_feedback tokens_used=0")
    debug_state("apply_feedback", state)
    return state
