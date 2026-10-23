"""The rendered skill aghub syncs must match what Reach would render now."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("render_skill", ROOT / "scripts" / "render_skill.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


def test_rendered_skill_is_current():
    want = render.expected()
    have = {str(p.relative_to(render.OUT)): p.read_text(encoding="utf-8")
            for p in render.OUT.rglob("*") if p.is_file()}
    assert have == want, "stale .aghub/agent-reach: run `python scripts/render_skill.py`"
    assert "{{" not in want["SKILL.md"]


def test_rendered_skill_routes_downstream_tools():
    text = render.expected()["SKILL.md"]
    for needle in ("references/downstream.md", "references/firecrawl.md", "| firecrawl |"):
        assert needle in text
