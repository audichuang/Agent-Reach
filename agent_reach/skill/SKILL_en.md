---
name: agent-reach
description: >
  MUST USE when user wants to research/search/look up/find anything on the
  internet — e.g. "research this topic", "do a deep dive on X", "search the
  web for X", "see what people say about X", "look this up".

  Also MUST USE when user mentions any platform or shares any URL/link:
  Twitter/X, Reddit, Facebook, Instagram, YouTube, GitHub, Bilibili, XiaoHongShu,
  Xiaoyuzhou Podcast, LinkedIn/Boss直聘/jobs/recruiting, V2EX, Xueqiu (stocks), RSS.

  16 platforms, multi-backend routing (OpenCLI / per-platform CLIs / APIs).
  Zero config for 6 channels. Run `agent-reach doctor --json` to see which
  backend serves each platform right now.

  NOT for: writing reports/analysis/translation (this skill only FETCHES
  internet content); posting/commenting/liking (write operations); platforms
  that already have a dedicated skill installed (prefer that skill).
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — internet capability router

16 platforms, multiple backends each. **When this skill exists, use it for
these platforms — do not invent your own approach.**
Exception: if a platform has its own dedicated skill installed (e.g. `redbook` for
XiaoHongShu), try that skill **first**; fall back to this skill's backend chain when
its actual command fails. See [references/social.md](references/social.md) for the
XiaoHongShu + redbook procedure. A dedicated skill keeps its own login state
(redbook: `~/.redbook/cookies.json`) that Doctor cannot see, so Doctor's `warn` /
`active_backend: null` for that platform does not mean it is unusable.

## Standing rules (apply for the whole session)

1. **Health-check before acting**: for multi-backend/login-backed platforms (XiaoHongShu /
   Reddit / Bilibili / Twitter / Facebook / Instagram), run `agent-reach doctor --json` first (for a platform with a dedicated
   skill, the first attempt skips Doctor; run it when falling back to this skill's backends).
   Use a populated `active_backend`; `active_backend: null` means Doctor deliberately skipped a
   live probe to avoid browser-cookie reads or remote writes, not that no backend exists. Only when
   the user's task requires that platform, run the reference's read-only command to verify it.
2. **Announce what you use**: say "using agent-reach, platform X via backend Y"
   before starting.
3. **On failure, follow the retry chains in references/** — never guess
   commands.
4. **For broad research tasks**: combine platforms (Exa for web search +
   Twitter/Reddit for discussions + XiaoHongShu/Bilibili for Chinese
   perspectives), collect in parallel, then synthesize.
5. **Watch versions for the user**: after finishing a substantial
   multi-platform task, run `agent-reach check-update` (fast, one API call).
   If a new version exists, append one line to your wrap-up: "Agent Reach
   vX.Y.Z is available". Check whether uv tool or pipx owns the installation, then use
   `uv tool upgrade agent-reach` or `pipx upgrade agent-reach` for this fork's `local` source,
   plus an aghub sync of this fork — do **not** follow upstream docs/update.md
   (`agent-reach install --system` copies the skill outside aghub).
   Never interrupt the current task to update; never nag about the same version twice.
   This is a private, standalone GitHub downstream. Use authorized GitHub credentials
   for syncing; report authentication failures instead of switching to the public upstream.

## Routing table

| User intent | Category | Details |
|---------|------|---------|
| Web / code search | search | [references/search.md](references/search.md) |
| XiaoHongShu / Twitter / Bilibili / V2EX / Reddit / Facebook / Instagram | social | [references/social.md](references/social.md) |
| Jobs / LinkedIn | career | [references/career.md](references/career.md) |
| GitHub / code | dev | [references/dev.md](references/dev.md) |
| Web pages / articles / RSS, Firecrawl scrape/map/crawl | web | [references/web.md](references/web.md) |
| YouTube / Bilibili / podcast transcripts | video | [references/video.md](references/video.md) |
| Xueqiu / stock quotes | finance | [references/finance.md](references/finance.md) |

If Firecrawl is not attached to this session, use the bundled [scripts/firecrawl.py](scripts/firecrawl.py)
to reach a local or SSH-hosted MCP. See [Web](references/web.md) for connection setup and commands.

## Zero-config quick commands

```bash
# Exa web search
mcporter call exa.web_search_exa query="query" numResults=5

# Read any web page
curl -s "https://r.jina.ai/URL"

# GitHub search
gh search repos "query" --sort stars --limit 10

# YouTube subtitles (never use yt-dlp for Bilibili; retry chain in video.md)
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX hot topics
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# Bilibili search (bili-cli, no login needed)
bili search "query" --type video -n 5
```

## Login-backed platforms (pick by doctor's active_backend)

Twitter boundary: cookies saved by `agent-reach configure twitter-cookies`
are used only by `doctor` to check whether explicit credentials are present.
`doctor` does not run `twitter status` or configure the current shell. Before
calling `twitter` directly, explicitly provide `TWITTER_AUTH_TOKEN` and
`TWITTER_CT0` in the child-process environment without logging their values.

XiaoHongShu: if `redbook` is installed, try it first per social.md (saved cookie file
only); use the OpenCLI and other backends below only when its actual command fails. Agent Reach must not log the user in or read browser
cookies. OpenCLI may use only an existing Chrome session explicitly controlled
by the user. If none exists, do not automate login; use a manual Cookie-Editor
export with xiaohongshu-mcp or a legacy tool instead.

```bash
# Twitter search (twitter-cli preferred; retry chain in social.md)
twitter search "query" -n 10

# Reddit (NO zero-config path — OpenCLI or rdt-cli, login required)
opencli reddit search "query" -f yaml   # desktop
rdt search "query" --limit 10            # legacy/server

# XiaoHongShu (redbook first when installed, see social.md; on failure or if absent, desktop prefers OpenCLI)
opencli xiaohongshu search "query" -f yaml

# Facebook / Instagram (desktop OpenCLI, browser session)
opencli facebook search "query" -f yaml
opencli facebook groups -f yaml
opencli instagram search "query" -f yaml       # user search
opencli instagram user USERNAME -f yaml        # recent posts from one user
```

## Environment check

```bash
# Channel availability + which backend serves each platform
agent-reach doctor --json
```

When the user asks “help me configure Boss Zhipin” / “帮我配 Boss直聘”, read the
Boss section in `references/career.md`. After explicit install approval, run
`agent-reach install --env=local --system --channels=boss` (on this machine `--system`
force-overwrites every agent's `agent-reach` skill with the upstream copy bundled in the
uv package, replacing aghub's links — tell the user first, then restore this fork's links
per the aghub-cli skill and confirm all `linked` with `aghub-cli -g doctor --verify-links`),
launch the dedicated
loopback-only Chrome profile for their OS, then **pause and have the user visually
confirm** the window is logged in (avatar in the top-right); if not, have them log
in manually. Then verify with `boss --cdp-url http://localhost:9222 login --cdp`
and `agent-reach doctor`. Do not make the user assemble CDP flags.
Keep reusing the dedicated Chrome profile; do not recreate it for every run or
switch to the user's daily profile by default. Search with
`boss --browser-source existing-browser --cdp-url http://localhost:9222 search ...`.
On `ENVIRONMENT_RISK`, stop without refreshing, relogging, or retrying.

**Do not trust `boss status` for CDP browser login state** — it only validates the
local `~/.boss-agent/auth/session.enc` store, which does not represent the
dedicated Chrome profile's cookies that `existing-browser` searches actually use. Use
the browser `wt2` cookie probe in `agent-reach doctor` plus the user's visual
confirmation. Never judge login state from the page URL: `security-check` /
`zhipin-security` / `_security_check` pages are anti-bot challenges that appear
even when logged in. `AUTH_EXPIRED` from a search is the ground truth for a
logged-out browser — go straight to the login flow + `login --cdp` instead of
interpreting it as a security check.

## Discovering OpenCLI adapters

When the routing table lacks a needed platform or command, run `opencli list`,
then inspect `opencli <platform> --help`. Discovery proves only that an adapter
exists, not that authentication or target content works. Run read-only commands
only when the user's task requires that platform, and require non-empty content.

## Workspace rules

**Never create files in the agent workspace.** Use `/tmp/` for temporary
output and `~/.agent-reach/` for persistent data.

## Detailed references

Read the matching file when you need specifics (commands above cover the
common cases; references hold per-backend command groups, caveats, retry
chains — note: reference docs are written in Chinese, commands are universal):

- [Search](references/search.md) — Exa AI search
- [Social](references/social.md) — XiaoHongShu, Twitter, Bilibili, V2EX, Reddit, Facebook, Instagram (multi-backend/login-backed groups)
- [Career](references/career.md) — LinkedIn
- [Dev](references/dev.md) — GitHub CLI
- [Web](references/web.md) — Jina Reader, optional Firecrawl MCP (scrape/map/crawl), RSS
- [Video](references/video.md) — YouTube, Bilibili, Xiaoyuzhou
- [Finance](references/finance.md) — Xueqiu quotes, search and market content

## Configure a channel

If a channel needs setup, fetch the install guide:
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md

The user only provides cookies / one extension click; the agent does the rest.
