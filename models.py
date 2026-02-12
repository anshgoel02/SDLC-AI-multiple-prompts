from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class IntakeSummary(BaseModel):
    project_name: Optional[str] = None
    project_type: str = "unknown"
    primary_workflows: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)


class Evidence(BaseModel):
    source_name: str
    locator: str
    quote: str


class Fact(BaseModel):
    statement: str
    evidence: List[Evidence] = Field(default_factory=list)


class FactPack(BaseModel):
    goals: List[Fact] = Field(default_factory=list)
    scope_in: List[Fact] = Field(default_factory=list)
    scope_out: List[Fact] = Field(default_factory=list)
    stakeholders: List[Fact] = Field(default_factory=list)
    requirements: List[Fact] = Field(default_factory=list)
    constraints: List[Fact] = Field(default_factory=list)
    risks: List[Fact] = Field(default_factory=list)
    assumptions: List[Fact] = Field(default_factory=list)
    data_sources: List[Fact] = Field(default_factory=list)
    integrations: List[Fact] = Field(default_factory=list)
    security_compliance: List[Fact] = Field(default_factory=list)


class TemplateSectionSpec(BaseModel):
    name: str
    required_fields: List[str] = Field(default_factory=list)


class BRDTemplateSpec(BaseModel):
    sections: List[TemplateSectionSpec] = Field(default_factory=list)


class GapItem(BaseModel):
    section: str
    field: str
    severity: str  # "blocking" | "non_blocking"
    suggested_evidence_to_provide: str
    light_assumption_template: Optional[str] = None


class GapReport(BaseModel):
    blocking: List[GapItem] = Field(default_factory=list)
    non_blocking: List[GapItem] = Field(default_factory=list)

    def for_section(self, section_name: str) -> "GapReport":
        return GapReport(
            blocking=[g for g in self.blocking if g.section == section_name],
            non_blocking=[g for g in self.non_blocking if g.section == section_name],
        )


class BRDOutline(BaseModel):
    ordered_sections: List[str] = Field(default_factory=list)


class BRDModel(BaseModel):
    sections: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)


class BRDAssemblyOut(BaseModel):
    brd_model: BRDModel
    brd_markdown: str


class BRDState(BaseModel):
    template_path: str
    inputs: List[str] = Field(default_factory=list)
    brownfield_inputs: List[str] = Field(default_factory=list)
    source_texts: List[str] = Field(default_factory=list)
    brownfield_texts: List[str] = Field(default_factory=list)
    intake: Optional[IntakeSummary] = None
    facts: FactPack = Field(default_factory=FactPack)
    gaps: GapReport = Field(default_factory=GapReport)
    outline: BRDOutline = Field(default_factory=BRDOutline)
    section_drafts: List[str] = Field(default_factory=list)
    brd_markdown: str = ""
    brd_model: Optional[BRDModel] = None
    user_force_generate: bool = False
    human_feedback: Optional[str] = None
    approved: bool = False
    output_docx_path: Optional[str] = None
    chunk_size: int = 3000
    max_chunks: int = 40
