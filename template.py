from __future__ import annotations

import re
from pathlib import Path
from typing import List

from pypdf import PdfReader

from .models import BRDTemplateSpec, TemplateSectionSpec


def extract_template_sections(template_path: Path) -> List[TemplateSectionSpec]:
    reader = PdfReader(str(template_path))
    toc_text = ""
    for page in reader.pages[:2]:
        toc_text += (page.extract_text() or "") + "\n"

    sections: List[TemplateSectionSpec] = []
    for line in toc_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.search(r"\.{5,}\s*\d+$", line):
            title = re.sub(r"\.{5,}\s*\d+$", "", line).strip()
            if title:
                sections.append(TemplateSectionSpec(name=title, required_fields=["content"]))

    if not sections:
        sections = [
            TemplateSectionSpec(name="Technology Platform and Tools", required_fields=["content"]),
            TemplateSectionSpec(name="Initiating a Workflow", required_fields=["content"]),
            TemplateSectionSpec(name="User Roles/Responsibilities", required_fields=["content"]),
            TemplateSectionSpec(name="Workflow 1: SensoryUX Workflow", required_fields=["content"]),
            TemplateSectionSpec(name="Workflow 2: Analytical Workflow", required_fields=["content"]),
            TemplateSectionSpec(name="Out of Scope", required_fields=["content"]),
            TemplateSectionSpec(name="Appendix and Supporting Documents", required_fields=["content"]),
        ]
    return sections


def build_template_spec(template_path: Path) -> BRDTemplateSpec:
    return BRDTemplateSpec(sections=extract_template_sections(template_path))
