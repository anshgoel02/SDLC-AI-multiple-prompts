from __future__ import annotations

import json
from typing import List

from ..debug import debug_state, format_sources
from ..llm_utils import generate_text_with_usage
from ..models import BRDState


def section_writer_node(state: BRDState) -> BRDState:
    print("[node] section_writer")
    inputs_text = format_sources(state.source_texts)
    drafts: List[str] = []
    total_tokens = 0
    total_prompt = 0
    total_completion = 0
    for section_name in state.outline.ordered_sections:
        gap_slice = state.gaps.for_section(section_name).model_dump()
        prompt = f"""SYSTEM
You write ONE BRD section. Use only extracted facts and (if allowed) assumptions.

USER
Task:
- Generate the {section_name} section content.
- If the section is in GapReport.non_blocking, append a short "Assumptions" subsection.
- Add a "Citations" list showing (source_name, locator).

Output:
Return the section as clean markdown text (no JSON).

CONTEXT:
- Facts (FactPack): {json.dumps(state.facts.model_dump(), indent=2)}
- Gaps for this section (GapReport slice): {json.dumps(gap_slice, indent=2)}
- User inputs (for quoting): {inputs_text}
"""
        draft, usage = generate_text_with_usage(prompt, max_tokens=1400)
        total_tokens += usage["total_tokens"]
        total_prompt += usage["prompt_tokens"]
        total_completion += usage["completion_tokens"]
        drafts.append(draft.strip())
    state.section_drafts = drafts
    print(
        f"[node] section_writer tokens_used={total_tokens} "
        f"(prompt={total_prompt} completion={total_completion})"
    )
    debug_state("section_writer", state)
    return state
