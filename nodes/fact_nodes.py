from __future__ import annotations

from ..debug import debug_state, format_sources
from ..llm_utils import generate_text_with_usage, parse_json_model
from ..models import BRDState, FactPack


def fact_extractor_node(state: BRDState) -> BRDState:
    print("[node] fact_extractor")
    inputs_text = format_sources(state.source_texts)
    brownfield_text = format_sources(state.brownfield_texts)
    # Prints the meeting transcript
    # print(inputs_text)
    prompt = f"""SYSTEM
You are a forensic BA. Do NOT invent. Every fact must include evidence.

USER
Task:
- Build a FactPack from the provided inputs.
- For each fact, attach 1-3 Evidence items (source_name, locator, quote).
- If a category has no facts, keep it empty.

Output:
Return valid JSON that matches the FactPack schema.

INPUTS:
{inputs_text}

OPTIONAL_BROWNFIELD:
{brownfield_text}
"""
    raw, usage = generate_text_with_usage(prompt, max_tokens=1800)
    if not raw.strip():
        print("[warn] fact_extractor empty response; retrying once")
        retry_prompt = "Return ONLY valid JSON.\n\n" + prompt
        raw, usage = generate_text_with_usage(retry_prompt, max_tokens=1800)
    if not raw.strip():
        print("[warn] fact_extractor still empty; using fallback empty FactPack")
        state.facts = FactPack()
    else:
        state.facts = parse_json_model(raw, FactPack)
    print(
        f"[node] fact_extractor tokens_used={usage['total_tokens']} "
        f"(prompt={usage['prompt_tokens']} completion={usage['completion_tokens']})"
    )
    debug_state("fact_extractor", state)
    return state
