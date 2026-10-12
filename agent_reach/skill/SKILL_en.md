---
name: agent-reach
description: >
  Reads and searches platforms that need dedicated CLI/MCP readers: X/Twitter, Reddit, Bilibili, V2EX, Xiaoyuzhou podcasts, Xueqiu, Boss Zhipin/LinkedIn, Facebook/Instagram, XiaoHongShu, plus Firecrawl scrapes and site crawls. Also installs those readers, configures their cookies and runs doctor on them. Plain web search and URL reads stay with built-in tools; platforms with their own skill go to that skill.
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
- Follow the reference's retry and stop conditions. After substantial research, check versions per
  [environment.md](references/environment.md); never upgrade mid-research.

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
