# CLAUDE.md

## Project
Agent Reach — one read-only CLI (`agent-reach <channel> <action>`) that gives AI agents search/read access to internet platforms, returning one JSON envelope per call.
Private downstream of github.com/Panniantong/Agent-Reach | License: MIT | Version: 1.6.0

## Commands
- `uv venv && uv pip install -e . pytest` — Dev install (keep it out of the user's real `~/.agent-reach`)
- `pytest tests/ -v` — All tests
- `python scripts/render_skill.py` — Re-render `.aghub/agent-reach/` after touching `agent_reach/skill/` or any channel

## Structure
- `agent_reach/cli.py` — entry point only; commands live in `agent_reach/runtime/cli.py`
- `agent_reach/runtime/` — dispatch, management (`manage.py`: add/setup/update/skill), dedicated browser, state
- `agent_reach/channels/` — one file per platform, subclass of `channels/base.py` `Channel`, registered in `channels/__init__.py`
- `agent_reach/backends/` — shared upstream adapters (OpenCLI, CloakBrowser)
- `agent_reach/skill/` — SKILL.md template + references, rendered by `manage.render_skill()`
- `.aghub/agent-reach/` — rendered copy that aghub syncs (generated; never edit by hand)

## Downstream changes (keep through upstream syncs)
- `channels/firecrawl.py` — Firecrawl MCP via mcporter, config `~/.agent-reach/firecrawl.json`
- `manage.DOWNSTREAM_SOURCE` — `update` reinstalls `audichuang/Agent-Reach@local`, never the public release
- `manage._externally_managed` — an aghub symlink at `~/.agents/skills/agent-reach` is left alone
- Skill: narrowed description, dedicated skills (redbook) first, `references/downstream.md` and `references/firecrawl.md`

## Rules
- NEVER modify upstream open source projects' source code; channels only route and call public APIs/CLIs
- Version in `pyproject.toml` and `agent_reach/__init__.py` must match
- Use a new branch for changes and target PRs to `local`, this private downstream's deployment branch. Keep `main` for upstream history.
- Upstream sync: fast-forward `main` to `upstream/main`, then merge `main` into a branch off `local`
- Run `pytest tests/ -v` before committing — all tests must pass
- Commit format: `type(scope): message` (one commit = one thing)
