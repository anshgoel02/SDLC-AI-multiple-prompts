from __future__ import annotations

from dataclasses import dataclass
from typing import Set


SUPPORTED_EXTENSIONS: Set[str] = {".txt", ".md", ".pdf", ".pptx", ".docx"}


@dataclass(frozen=True)
class Settings:
    default_template_path: str = "R&D Analytics Finalised Requirements Document.pdf"
    default_chunk_size: int = 3000
    default_max_chunks: int = 40
    default_output_dir: str = "brd_agent_2"
