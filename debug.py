from __future__ import annotations

import json

from .models import BRDState


def format_sources(texts: list[str]) -> str:
    return "\n\n".join(texts)


def debug_state(node_name: str, state: BRDState) -> None:
    print(f"[debug] {node_name} state:")
    try:
        print(json.dumps(state.model_dump(), indent=2))
    except Exception:
        print(state)
