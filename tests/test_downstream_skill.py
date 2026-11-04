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


def test_skill_text_guards_session_overwrite_and_check_misuse():
    skill = ROOT / "agent_reach" / "skill"
    files = {n: (skill / n).read_text(encoding="utf-8")
             for n in ("SKILL.md", "SKILL_en.md", "references/sessions.md")}
    for name in files:
        t = files[name]
        assert "check <渠道> --search" not in t and "check <channel> --search" not in t
    for name in ("SKILL.md", "SKILL_en.md"):
        # search channels must be pre-checked via the route the agent really takes (public-web)
        assert "check <渠道1> <渠道2> --search --text" in files[name] or "check <ch1> <ch2> --search --text" in files[name]
    for name in ("SKILL.md", "SKILL_en.md"):
        t = files[name]
        assert "public_web" in t
        assert ("没退出过" in t) or ("never logged out" in t)
