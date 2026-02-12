from __future__ import annotations

from ..debug import debug_state, format_sources
from ..file_loaders import iter_input_files, load_source_text
from ..llm_utils import generate_text_with_usage, parse_json_model
from ..models import BRDState, IntakeSummary


def load_sources_node(state: BRDState) -> BRDState:
    print("[node] load_sources")
    files = list(iter_input_files(state.inputs))
    texts = []
    for file_path in files:
        try:
            text = load_source_text(file_path)
        except Exception:
            continue
        if text.strip():
            texts.append(f"[SOURCE: {file_path.name}]\n{text}")
    state.source_texts = texts

    brownfield_files = list(iter_input_files(state.brownfield_inputs))
    brownfield_texts = []
    for file_path in brownfield_files:
        try:
            text = load_source_text(file_path)
        except Exception:
            continue
        if text.strip():
            brownfield_texts.append(f"[SOURCE: {file_path.name}]\n{text}")
    state.brownfield_texts = brownfield_texts
    print("[node] load_sources tokens_used=0")
    debug_state("load_sources", state)
    return state


def intake_node(state: BRDState) -> BRDState:
    print("[node] intake_and_classification")
    inputs_text = format_sources(state.source_texts)
    brownfield_text = format_sources(state.brownfield_texts)
    prompt = f"""SYSTEM
You are an expert Business Analyst. Use only the provided inputs.

USER
Task:
- Build an IntakeSummary with:
  - project_name (if present else None)
  - project_type: "greenfield" | "brownfield" | "unknown"
  - primary_workflows (list)
  - assumptions (list)
  - open_questions (list)

Output:
Return valid JSON that matches the IntakeSummary schema.

Constraints:
- Do not invent facts not in the inputs.

INPUTS:
{inputs_text}

OPTIONAL_BROWNFIELD:
{brownfield_text}
"""
    raw, usage = generate_text_with_usage(prompt, max_tokens=800)
    if not raw.strip():
        print("[warn] intake_and_classification empty response; retrying once")
        retry_prompt = "Return ONLY valid JSON.\n\n" + prompt
        raw, usage = generate_text_with_usage(retry_prompt, max_tokens=800)
    if not raw.strip():
        print("[warn] intake_and_classification still empty; using fallback IntakeSummary")
        state.intake = IntakeSummary(
            project_name=None,
            project_type="unknown",
            primary_workflows=[],
            assumptions=[],
            open_questions=["Intake model returned empty response; please confirm project details."],
        )
    else:
        state.intake = parse_json_model(raw, IntakeSummary)
    print(
        f"[node] intake_and_classification tokens_used={usage['total_tokens']} "
        f"(prompt={usage['prompt_tokens']} completion={usage['completion_tokens']})"
    )
    debug_state("intake_and_classification", state)
    return state
