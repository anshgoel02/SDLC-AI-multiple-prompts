from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from brd_agent_2.config import Settings
from brd_agent_2.models import BRDState
from brd_agent_2.graph import build_graph


def parse_args() -> argparse.Namespace:
    settings = Settings()
    parser = argparse.ArgumentParser(description="BRD generation agent v2")
    parser.add_argument(
        "--template",
        default=settings.default_template_path,
        help="Path to BRD template PDF",
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Input files or directories containing transcripts and documents",
    )
    parser.add_argument(
        "--brownfield-inputs",
        nargs="*",
        default=[],
        help="Optional existing system docs for brownfield context",
    )
    parser.add_argument(
        "--output-docx",
        default=None,
        help="Optional path to save BRD as .docx (default in brd_agent_2 folder)",
    )
    parser.add_argument("--chunk-size", type=int, default=settings.default_chunk_size)
    parser.add_argument("--max-chunks", type=int, default=settings.default_max_chunks)
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    output_docx = args.output_docx
    if not output_docx:
        output_docx = str(Path(Settings().default_output_dir) / "brd_output.docx")

    graph = build_graph().compile()
    initial_state = BRDState(
        template_path=args.template,
        inputs=args.inputs,
        brownfield_inputs=args.brownfield_inputs,
        output_docx_path=output_docx,
        chunk_size=args.chunk_size,
        max_chunks=args.max_chunks,
    )
    graph.invoke(initial_state)


if __name__ == "__main__":
    main()
