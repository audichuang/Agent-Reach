---
name: agent-reach
description: >
  News and headlines: today's or this week's top tech or industry news, financial news, what moves a stock, more outlets' coverage to summarise (e.g. an earnings call); Google News, Hacker News; comparing or judging tools, products or repos ("which is better / what do people say / has anyone hit this / known issue?") by what people on Reddit, X and other communities say; search or read X/Twitter, Reddit, Bilibili, V2EX, Xueqiu, Xiaoyuzhou, Boss Zhipin/LinkedIn, Facebook/Instagram; pages built-in fetch cannot read (403, captcha, JS shell, PDF), listing every page URL under a site or path, or many pages on one site, via Firecrawl scrape, map, crawl. Also installs, adds/removes platforms, logs in/out, doctor/check, updates Agent Reach. Read-only: never posts, comments or messages. XiaoHongShu goes to redbook first; YouTube subtitles to yt-dlp-capture; 30-day multi-platform digests to last30days; repo files or repo research reports to research; official docs and plain reads stay with built-in tools.
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
  version: "{{VERSION}}"
---

# Agent Reach

One command for every platform: `agent-reach`. Read-only; prints one JSON object by default.

Before acting, say "using the agent-reach skill (channel X)". Once invoked, these rules apply for the whole session.

## Choosing a route

- When the user typed /agent-reach, run at least one Reach channel; answering only with gh, built-in search or other tools ignores what they asked for.
- For news, opinion, reputation and "has anyone else hit this", Reach is a primary source alongside built-in search, not a fallback: built-in search sees the web index, not discussions on X, Reddit, V2EX or Xueqiu, and cannot sort news by publication date.
- A platform with a dedicated skill installed here (e.g. redbook for XiaoHongShu) goes to that skill first; come back to Reach only when its real command fails. See [downstream notes](references/downstream.md).
- Added channels (defaults, or added with `add`) go straight to the site tool; channels not added first try anonymous public web (marked `backend: public-web`). A platform name or link only identifies the source; it never triggers install or login.
- Snippets, page shells, comment counts and subtitle track lists are not body text, comments or subtitles; say which you have.

```bash
agent-reach channels                      # actions and params per channel; run it when unsure
agent-reach <channel> <action> [args]     # e.g. agent-reach google-news search "TSMC" --lang en --region US
agent-reach read <url>                    # picks the channel from the URL
```

Call only through `agent-reach`, never `opencli`, `twitter`, `rdt` or `mcporter` directly (they live in a private folder and may not be on PATH). Limit time with `--timeout SECONDS`, not `timeout`/`gtimeout` (macOS lacks them). Reach queues and paces same-platform searches itself; do not sleep between calls.

## Research and news

Users have complained "analysing without checking the news is wrong" and "no big picture": concluding from search snippets or a single source is the most common mistake here.

1. **Find dated reports first**: `google-news search` (Chinese finance: `--lang zh-TW --region TW` or `--lang zh-CN --region CN`), `hackernews search` for tech/developer topics, then built-in search narrowed by date.
2. **Read originals**: read the full text of several articles from different outlets. Snippets and headlines are not evidence for causal claims ("why did the stock drop" needs the article's own explanation). `google-news` gives only headline, outlet (`author`) and date; its `news.google.com/rss/articles/…` links are redirects that `read`, WebFetch and Firecrawl all return as an empty shell, so never fetch them. For each article you need, take the whole headline (drop the trailing " - outlet", no quotes) and find the original URL: `firecrawl_search` if present (in tests the first hit was the original), else `agent-reach web search "<headline>"`, else built-in search with the outlet name or `site:outlet-domain`; then `agent-reach read` that URL, or Firecrawl scrape if it will not load or web is rate-limited.
3. **Add community angles**: pick channels from the table below; get the original post when quoting someone.
4. **Deliver**: the original link (not news.google.com) and publication date for every claim and every outlet; per platform, what ran, what came back and what failed (`error.code`). Before saying "nothing found", be able to list the platforms and queries you tried.

| Topic | Channels |
|---|---|
| Finance, single stocks | `google-news search`; `xueqiu quote`; Xueqiu discussion via `xueqiu hot_posts` or built-in search `site:xueqiu.com`; `twitter search` for English-language markets |
| Tech, developers | `hackernews search`, `reddit search`, `twitter search`, `v2ex hot` / `v2ex node` |
| Chinese communities | `v2ex`, `bilibili search`, Xueqiu; XiaoHongShu goes to redbook |
| English product reputation | `reddit search` / `reddit subreddit`, `twitter search`, `hackernews search`, `youtube search` |
| "Anyone else?", known issues | the official issue tracker first (`gh search issues`, `github read <issue link>`), then reddit / hackernews / v2ex |

## Delegating to subagents

When the user wants depth or several angles, split by topic across subagents in parallel:

1. Live-test the channels you will hand out first: `agent-reach check <ch1> <ch2> --search --text` (`--search` tests the route you will actually take, including public-web for channels not added; channels without a search action, such as v2ex and xiaoyuzhou, show 0/0 under it, so check those with `check <ch> --text` without `--search`, or just run the action you will hand out) and read each PASS/FAIL line (exit code 1 if any fails). Check that the inline `[backend]` is the route you will hand out; `[public-web]` on a channel not added only proves anonymous web works, not the in-site actions. `doctor` reads local state only and cannot see an expired login.
2. Hand out only PASS channels, with the exact `agent-reach ...` commands in the task.
3. Tell subagents: do not run doctor or read this skill's references; trim big JSON with `jq` or python to `title/url/published_at/text` instead of pasting it whole; report in the format of step 4 above.
4. Parallel limits: 2 per platform, 4 in total; Reach queues the rest.

## Pages you cannot read: Firecrawl

When WebFetch or `read` hits 403, a timeout, a connection reset, a Cloudflare/Vercel verification page, a JS-only shell, or a PDF, switch to Firecrawl instead of giving up or hand-parsing with curl. Use the session's `mcp__firecrawl__*` tools when it has them; for actions it lacks, use `agent-reach firecrawl scrape|map|crawl|status`.

- One page → scrape. Three or more pages on one site, or you need its URL list → map, then scrape page by page; many pages → crawl, narrowed with `--limit` and `--include`.
- Success = non-empty body text, not `ok`. Verification pages and empty shells do not count.
- Firecrawl does not find news (its search with news/time filters did not work in tests); using `firecrawl_search` to turn a known headline into the original URL is fine. Details in [Firecrawl](references/firecrawl.md).

## Results and errors

- `ok: true` → content in `items`; each has `title / url / author / published_at / text`, upstream data in `raw`. Empty `items` must be reported or routed around, not treated as "checked".
- `ok: false` → branch on `error.code` and follow `error.hint`:

| error.code | What to do |
|---|---|
| `NEED_SETUP` | Missing dependency or key. Run `agent-reach add <channel>` as hinted; for a key, the user provides it, then `agent-reach configure <key>` |
| `NEED_LOGIN` | If `message` mentions 403 or HTML instead of JSON, handle it as the `UPSTREAM_BROKEN` row. For browser-login channels (`login.via: browser` in `channels`; not Bilibili), and the user has never logged out of or manually logged in to that channel, first `agent-reach login <channel> --import-existing` (copies the login from the user's signed-in Chrome, no window), then re-run the action that failed (not `check --search`, which does not test in-site actions). If the user logged out or logged in manually, or you are unsure, ask the user and confirm the source account first; do not import automatically. Only if that returns `NEED_SETUP` or still fails, ask the user to run `agent-reach login <channel>` themselves; never log in for them or ask for a password |
| `UPSTREAM_BROKEN` | The platform is having trouble; `message` is what was reported. A 403 or "HTML instead of JSON" is usually a WAF or rate limit, not a logout: try `--backend public-web` only if `channels` shows a non-empty public_web for that action and `meta.attempts` has not tried public-web yet (google-news, hackernews and others do not support it; added channels already tried it once); otherwise run another action of the channel (e.g. `reddit subreddit <relevant sub>`, `reddit read`), do not just suggest it. Tell the user by platform name, without naming tools; run `agent-reach update` once, after they agree, only if the message points to an outdated tool; never retry in a loop |
| `TIMEOUT` | Check the failed stage and channel status; do not retry or reopen windows in a loop |
| `RATE_LIMITED` | From the site tool: the platform rate-limited and Reach pauses the whole channel for an hour; stop using it, do not switch backends. From `--backend public-web`: the shared web search (Exa) is limited, so `web search` and `read` of ordinary pages are paused too, but the platform is not; run another action of the channel as in the row above |
| `PLATFORM_BLOCKED` | The platform wants verification (captcha/risk check). Stop; the user resolves it on the official page. Do not switch accounts or backends |
| `BUSY` | The browser stayed full for the 2-minute wait, or the user has a login window open. Retry later, or after the user says they are logged in; do not close the window or switch profiles |
| `NOT_FOUND` | Content does not exist; check the link or ID |
| `BAD_INPUT` | Wrong arguments; run `agent-reach channels` for usage |

`PLATFORM_BLOCKED`, `RATE_LIMITED` and `BUSY` are hard stops: no retrying the stopped route with other accounts, backends or browsers (public-web rate limits: see above). A network failure or a failure on one machine does not mean "the platform requires login". If the user skips login, still deliver the public results already gathered.

## Login and the dedicated browser

Browser channels share one dedicated browser (CloakBrowser preferred, else installed Chrome). It runs headless, closes after 10 idle minutes and reopens on the next call. The first time a site is used, if the user's Chrome is connected to the OpenCLI extension, that site's login is copied automatically. Refreshing, choosing a source and logging out are in [Sessions](references/sessions.md): read it when the user wants to log in, log out or switch accounts, or when `--import-existing` does not fix a login.

## Platform notes

- X post links (`x.com/<user>/status/<id>`): `agent-reach read` or `twitter thread <link> --limit N` gives the post and replies.
- `xueqiu search` only finds stocks by name or code, not topics; `hot_posts` and `hot_stocks` need a browser session, `quote` does not. `github search` searches repositories only; for code use `gh search code`, for issues `gh search issues`. GitHub file or directory links go from `read` to web.
- Hacker News results have no date or text: the discussion and date are at `https://news.ycombinator.com/item?id=<raw.id>`, read with built-in tools or `web read`; `--sort date` is mostly low-score noise, keep the default relevance.
- Xiaohongshu read returns text descriptions only; never claim to understand the images or video.
- When a Boss Zhipin search result has `salary_encoded=true`, never guess the salary digits; read the job link for the readable salary in the detail.
- What each platform offers publicly and what Reach adds is in [Capability scope](references/capabilities.md): read it when the user asks "what can it get / is it complete".

## Channels

{{CHANNEL_TABLE}}

`default` channels are installed by default and can be removed; updates never add a removed one back. The `login` column is the authentication entry point, not a prerequisite for public content.

## After installation

After `agent-reach setup`, show `result.installation_report.markdown` to the user as is: no additions, removals, reordering, extra greeting or tables. The program generates it.

## When the user wants to manage Agent Reach

| User says | You run |
|---|---|
| Add a platform | `agent-reach add <channel>`; dependencies install automatically. Tell the user only what they must do (log in or provide a key) |
| Remove a platform | `agent-reach remove <channel>` |
| Log in / login expired | For browser-login channels the user has not logged out of or manually logged in to, first `agent-reach login <channel> --import-existing`; otherwise ask the user first. If that fails, `agent-reach login <channel>` and the user logs in themselves in the window that opens |
| Log out | `agent-reach logout <channel>` |
| Status / what works | `agent-reach doctor --text` (local state only); for a live test `agent-reach check <channel...> --text` |
| Upgrade / update | `agent-reach update` |
| Uninstall | show `agent-reach uninstall --dry-run` first, then `agent-reach uninstall` once they confirm |
| Another AI should use it | `agent-reach skill link <that AI's skills folder>`; `agent-reach skill` shows where it is placed now |

Troubleshooting, browser maintenance and uninstall details are in [Maintenance](references/maintenance.md): read it when an update fails, the browser will not start, or the user wants to uninstall.

## When there is a new version

Any result with `meta.update` means a newer version exists. This machine runs a private downstream: read [downstream notes](references/downstream.md) before answering. Mention it once per conversation, in the user's language and plain words:

1. Agent Reach has a new version (`meta.update.latest`).
2. What changed: 1 to 3 short points from `meta.update.notes`.
3. Ask whether to update; run `agent-reach update` only after the user agrees.

## Red lines

- Read only. Never post, comment, like or message.
- Never log in for the user; never ask for or print passwords, cookies or other credentials.
- Ordinary queries never change dependencies or update automatically.
