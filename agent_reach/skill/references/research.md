# 调研细节：找原文与派子代理

按主文件"调研与新闻"做调研、要把 Google News 标题换成原文，或要派子代理时读这份。

## Google News 标题 → 原文

`google-news` 只给标题、媒体（`author`）和日期。它的 `news.google.com/rss/articles/…` 链接是跳转页，`read`、WebFetch、Firecrawl 都只拿到空壳，不要去抓。每篇要读的：

1. 拿整句标题，去掉结尾" - 媒体名"，不加引号（加引号实测返回空）。
2. 找原文 URL，按顺序试：
   - 会话有 `firecrawl_search` 就用它（实测第一条即原文）；
   - 否则 `agent-reach web search "<标题>"`；
   - 再不行用自带搜索加媒体名，或 `site:媒体域名`。
3. `agent-reach read <原文 URL>`；读不到或 web 被限流（`RATE_LIMITED`），改用 Firecrawl scrape。

## 派子代理前的预检

`agent-reach check <渠道1> <渠道2> --search --text` 验证的是你实际会走的路由（没 add 的渠道也会走 public-web），每行 PASS/FAIL，有 FAIL 时退出码为 1。

- PASS 要看行内 `[backend]` 是不是要派的那条路线：没 add 的渠道标 `[public-web]` 只证明公开网页能用，不证明站内动作能用。
- 没有 search 动作的渠道（如 v2ex、小宇宙）加 `--search` 会是 0/0：改用不带 `--search` 的 `check <渠道> --text`，或直接跑要派的那个动作。
- `doctor` 只读本地状态，看不出登录已过期，不能拿来预检。

交给子代理的任务里写明：

- 要跑的 `agent-reach …` 命令（只派 PASS 的渠道）；
- 命令同样照本 skill 选路：有专门技能的平台写专门技能的命令（如小红书用 redbook），不写直接跑 `opencli`、`twitter` 的命令，也不叫子代理自己 sleep 或套 `timeout`；
- 不跑 doctor、不读本 skill 的 references；
- 大 JSON 先用 `jq` 或 python 只取 `title/url/published_at/text`，不整段塞进上下文；
- 回报格式：每条论点附原文链接和发布日期；按平台列出跑了什么、拿到什么、哪些失败（`error.code`）。
