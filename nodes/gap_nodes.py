from __future__ import annotations

import json
from pathlib import Path

from ..debug import debug_state
from ..llm_utils import generate_text_with_usage, parse_json_model
from ..models import BRDState, GapReport
from ..template import build_template_spec


def gap_checker_node(state: BRDState) -> BRDState:
    print("[node] gap_checker")
    template_spec = build_template_spec(Path(state.template_path))
    prompt = f"""SYSTEM
You are a BRD template checker.

USER
Task:
- Compare the facts in FactPack against the provided BRDTemplateSpec.
- For each section in the template, check required fields.
- If a field cannot be derived from the facts, add it to a gap:
  - blocking if the section cannot be credibly produced
  - non_blocking if a short assumption would suffice
- For each missing field, add a short hint in suggested_evidence_to_provide.
- Provide light_assumption_template where reasonable.

Output:
Return valid JSON that matches the GapReport schema.

FACTS (FactPack instance):
{json.dumps(state.facts.model_dump(), indent=2)}

TEMPLATE (BRDTemplateSpec instance):
{json.dumps(template_spec.model_dump(), indent=2)}
"""
    raw, usage = generate_text_with_usage(prompt, max_tokens=1400)
    if not raw.strip():
        print("[warn] gap_checker empty response; retrying once")
        retry_prompt = "Return ONLY valid JSON.\n\n" + prompt
        raw, usage = generate_text_with_usage(retry_prompt, max_tokens=1400)
    if not raw.strip():
        print("[warn] gap_checker still empty; using fallback empty GapReport")
        state.gaps = GapReport()
    else:
        state.gaps = parse_json_model(raw, GapReport)
    print(
        f"[node] gap_checker tokens_used={usage['total_tokens']} "
        f"(prompt={usage['prompt_tokens']} completion={usage['completion_tokens']})"
    )
    debug_state("gap_checker", state)
    return state


def gap_human_review_node(state: BRDState) -> BRDState:
    print("[node] gap_human_review")
    has_gaps = bool(state.gaps.blocking or state.gaps.non_blocking)
    if not has_gaps:
        state.user_force_generate = False
        print("[node] gap_human_review tokens_used=0")
        debug_state("gap_human_review", state)
        return state
    print("Gaps detected.")
    choice = input("Generate anyway? (y/n): ").strip().lower()
    if choice in {"y", "yes"}:
        state.user_force_generate = True
        print("[node] gap_human_review tokens_used=0")
        debug_state("gap_human_review", state)
        return state

    more = input("Provide additional input paths (comma-separated) or leave empty to stop: ").strip()
    if more:
        for item in [p.strip() for p in more.split(",") if p.strip()]:
            state.inputs.append(item)
    state.user_force_generate = False
    print("[node] gap_human_review tokens_used=0")
    debug_state("gap_human_review", state)
    return state
