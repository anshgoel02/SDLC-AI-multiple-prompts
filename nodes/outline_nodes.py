from __future__ import annotations

import json
from pathlib import Path

from ..debug import debug_state
from ..llm_utils import generate_text_with_usage, parse_json_model
from ..models import BRDOutline, BRDState
from ..template import build_template_spec


def outline_builder_node(state: BRDState) -> BRDState:
    print("[node] outline_builder")
    template_spec = build_template_spec(Path(state.template_path))
    prompt = f"""SYSTEM
You are a BRD editor.

USER
Task:
- Using BRDTemplateSpec and the GapReport:
  - Include sections in the given order when feasible.
  - Omit sections that are blocking (unless the user insists "make anyway").
  - Include partially available sections if non_blocking (assumptions OK).

Output:
Return valid JSON that matches the BRDOutline schema.

FACTS (FactPack instance):
{json.dumps(state.facts.model_dump(), indent=2)}

TEMPLATE (BRDTemplateSpec instance):
{json.dumps(template_spec.model_dump(), indent=2)}

GAPS (GapReport instance):
{json.dumps(state.gaps.model_dump(), indent=2)}
"""
    raw, usage = generate_text_with_usage(prompt, max_tokens=800)
    if not raw.strip():
        print("[warn] outline_builder empty response; retrying once")
        retry_prompt = "Return ONLY valid JSON.\n\n" + prompt
        raw, usage = generate_text_with_usage(retry_prompt, max_tokens=800)
    if not raw.strip():
        print("[warn] outline_builder still empty; using fallback outline from template sections")
        state.outline = BRDOutline(
            ordered_sections=[s.name for s in template_spec.sections]
        )
    else:
        state.outline = parse_json_model(raw, BRDOutline)
    print(
        f"[node] outline_builder tokens_used={usage['total_tokens']} "
        f"(prompt={usage['prompt_tokens']} completion={usage['completion_tokens']})"
    )
    debug_state("outline_builder", state)
    return state
