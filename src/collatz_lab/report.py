"""Report helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_markdown_report(title: str, sections: dict[str, Any], out: str | Path) -> None:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", ""]
    for heading, body in sections.items():
        lines.extend([f"## {heading}", "", str(body), ""])
    path.write_text("\n".join(lines), encoding="utf-8")

