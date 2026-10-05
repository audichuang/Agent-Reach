---
name: agent-reach
description: >
  Routes internet research, search and external-link reading through installed tools. Use before fetching web/RSS, GitHub, XiaoHongShu, X/Twitter, Reddit, Facebook, Instagram, V2EX, LinkedIn/Boss Zhipin, YouTube, Bilibili, Xiaoyuzhou, Xueqiu or Firecrawl content, and for reader setup. Dedicated platform skills take priority. Excludes supplied-content processing, code edits, posting, forms and service deployment.
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach

Select an internet-reading backend and call its tools directly. Read only the reference needed for the task.

## Working rules

- Try an installed dedicated platform skill first; enter this skill's fallback chain after its command fails.
- For multi-backend or authenticated platforms, run Doctor (`agent-reach doctor --json`) first, except for the first
  dedicated-skill attempt. A `warn` or `active_backend: null` is not proof of failure; check the platform reference.
- State the platform/backend, use retrieved content and cite its sources; identify content you could not obtain.
- Users handle login and challenges. Follow each platform reference's authorization rules for credentials and existing sessions.
- Follow the reference's retry and stop conditions. Version checks after substantial research, installation and
  updates are covered in [environment.md](references/environment.md); do not interrupt research to upgrade Agent Reach.

## Read by intent

| Intent | Reference |
|---|---|
| Web research and technical source search | [search.md](references/search.md) |
| GitHub repository, code and Issue/PR research | [dev.md](references/dev.md) |
| XiaoHongShu / redbook | [xiaohongshu.md](references/xiaohongshu.md) |
| Twitter / X; pass TWITTER_AUTH_TOKEN and TWITTER_CT0 into the process environment | [twitter.md](references/twitter.md) |
| Reddit | [reddit.md](references/reddit.md) |
| V2EX, Facebook, Instagram | [social.md](references/social.md) |
| LinkedIn profiles and jobs | [career.md](references/career.md) |
| Boss Zhipin search or setup | [boss.md](references/boss.md) |
| Ordinary web pages and RSS | [web.md](references/web.md) |
| Firecrawl scraping, URL discovery and bounded crawling | [firecrawl.md](references/firecrawl.md) |
| YouTube, Bilibili and Xiaoyuzhou Podcast transcripts | [video.md](references/video.md) |
| Xueqiu quotes and discussions | [finance.md](references/finance.md) |
| Unavailable tools, adapter discovery, installation or updates | [environment.md](references/environment.md) |

When Firecrawl is not attached to the session, use the bundled [firecrawl.py](scripts/firecrawl.py).
Connection setup and success criteria are in the Firecrawl reference above.
