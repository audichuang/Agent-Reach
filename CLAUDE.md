# CLAUDE.md

## Project
Agent Reach — one read-only CLI (`agent-reach <channel> <action>`) that gives AI agents search/read access to internet platforms, returning one JSON envelope per call.
Private downstream of github.com/Panniantong/Agent-Reach | License: MIT | Version: 1.6.1.1

## Commands
- `uv venv && uv pip install -c constraints.txt -e '.[dev]'` — Dev install with pytest, ruff, mypy (keep it out of the user's real `~/.agent-reach`)
- `pytest tests/ -v` — All tests
- Live-test a channel that shells out (e.g. firecrawl) by calling its backend method under the real HOME; the CLI writes `~/.agent-reach/state.json` and has no state-dir override, while a fake HOME breaks npx-launched MCP servers
- `python scripts/render_skill.py` — Re-render `.aghub/agent-reach/` after touching `agent_reach/skill/` or any channel

## Structure
- `agent_reach/cli.py` — entry point only; commands live in `agent_reach/runtime/cli.py`
- `agent_reach/runtime/` — dispatch, management (`manage.py`: add/setup/update/skill), dedicated browser, state
- `agent_reach/channels/` — one file per platform, subclass of `channels/base.py` `Channel`, registered in `channels/__init__.py`
- `agent_reach/backends/` — shared upstream adapters (OpenCLI, CloakBrowser)
- `agent_reach/skill/` — SKILL.md template + references, rendered by `manage.render_skill()`
- `.aghub/agent-reach/` — rendered copy that aghub syncs (generated; never edit by hand). Keep it under a path that sorts before `agent_reach/`: aghub dedups same-name skills first-seen, so anywhere later loses to the raw template

## Downstream changes (keep through upstream syncs)
- `channels/firecrawl.py` — Firecrawl MCP via mcporter, config `~/.agent-reach/firecrawl.json`
- `manage.DOWNSTREAM_SOURCE` — `update` reinstalls `audichuang/Agent-Reach@local`, never the public release; an explicit `update` reinstalls it even when the version is unchanged (`reinstalled`, `reason` in the result), because fixes land on `local` without a bump
- `manage._externally_managed` — an aghub symlink at `~/.agents/skills/agent-reach` is left alone
- `backends/opencli._opencli_error` — OpenCLI "HTML instead of JSON" maps to UPSTREAM_BROKEN, not NEED_LOGIN, so added channels reach the public-web fallback
- `channels/google_news.py`, `channels/hackernews.py` — no-browser news channels over OpenCLI (`google news`, `hackernews`); default level, tools `opencli`+`node`, no login
- `backends/opencli.py` `opencli_public_items` — backend label `opencli-public` skips the browser binding, query slot and pacing in dispatch; use it for any OpenCLI site that needs no browser
- `runtime/session_reuse.prepare(self_heal=True)` / `login --self-heal` — agent-run re-import that refuses (NEED_LOGIN) when the record is `blocked` or `manual`; `--import-existing` stays upstream-forced
- Skill: narrowed description, dedicated skills (redbook) first, `references/downstream.md` and `references/firecrawl.md`

## Release and rollout
- PRs into `local` are merged by the agent (merge commit) once review and CI pass; `windows-test` has been red on `local` since before 1.6.1.1, so judge by the other jobs
- After merging into `local`: `agent-reach update` on ubuntu and macmini, then `aghub-cli -g source sync audichuang/Agent-Reach --skill agent-reach --update --yes` on all three machines. MacBook Pro's `agent-reach` is an SSH shim to ubuntu, so only its skill needs syncing
- Release: on a release branch run `python scripts/record_release_acceptance.py` on ubuntu, then from a clone of the same commit on macmini with `--only <channels that failed>` (macmini has the X login ubuntu lacks; rows are kept per source digest) and copy `.github/release-acceptance.json` back. Actions nobody can test go into `waived` by hand with a reason; tag `v<version>` on the merge commit in `local`
- After changing skill text, rerun `tests/skill_evals/research-depth/` with skillgenie (previous snapshot vs new, sonnet). Executors need the worktree venv first on PATH and log state-changing commands as WOULD RUN; ~40 live runs trip Exa's rate limit (about 1 h, `cooldowns.web` in `~/.agent-reach/state.json`), so run both arms under the same condition

## Rules
- NEVER modify upstream open source projects' source code; channels only route and call public APIs/CLIs
- Version in `pyproject.toml` and `agent_reach/__init__.py` must match
- Downstream releases use a fourth number on top of the upstream version (`1.6.1.1`, tag `v1.6.1.1`); `update_notice.version_tuple` only parses all-numeric parts, so no `.post`/`+local`. On upstream sync take upstream's version and CHANGELOG head
- Use a new branch for changes and target PRs to `local`, this private downstream's deployment branch. Keep `main` for upstream history.
- Upstream sync: fast-forward `main` to `upstream/main`, then merge `main` into a branch off `local`
- Before committing: `pytest -q` green and `ruff check` clean (the lint the user works with). The CI pytest workflow (upstream's) also runs `mypy agent_reach`, so run it before opening a PR
- Commit format: `type(scope): message` (one commit = one thing)
