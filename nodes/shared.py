from __future__ import annotations

from typing import Dict

from ..models import (
    BRDModel,
    BRDOutline,
    Evidence,
    Fact,
    FactPack,
    GapItem,
    GapReport,
    IntakeSummary,
    TemplateSectionSpec,
)


def allowed_models() -> Dict[str, object]:
    return {
        "IntakeSummary": IntakeSummary,
        "FactPack": FactPack,
        "GapReport": GapReport,
        "GapItem": GapItem,
        "BRDOutline": BRDOutline,
        "BRDModel": BRDModel,
        "Evidence": Evidence,
        "Fact": Fact,
        "TemplateSectionSpec": TemplateSectionSpec,
    }
