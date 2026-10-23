#!/usr/bin/env python3
"""Downstream: write the rendered skill aghub syncs from (skills/agent-reach/).

The packaged SKILL.md is a template ({{CHANNEL_TABLE}}, {{VERSION}}); aghub copies
files verbatim, so it must point at this rendered copy instead.
Run after changing agent_reach/skill/ or any channel: python scripts/render_skill.py
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "skills" / "agent-reach"


def expected() -> dict:
    """Relative path -> text of every file in the rendered skill."""
    sys.path.insert(0, str(ROOT))
    from agent_reach.runtime.manage import render_skill

    files = {"SKILL.md": render_skill("zh")}
    for ref in sorted((ROOT / "agent_reach" / "skill" / "references").glob("*.md")):
        files[f"references/{ref.name}"] = ref.read_text(encoding="utf-8")
    return files


def main() -> None:
    shutil.rmtree(OUT, ignore_errors=True)
    for rel, text in expected().items():
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"rendered {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
