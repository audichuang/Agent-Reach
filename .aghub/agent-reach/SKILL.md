---
name: agent-reach
description: >
  查新闻与头条：今天/本周科技圈或某行业有什么重要新闻、财经与个股消息面、要多家媒体报道或多查几家来统整（如法说会），Google News、Hacker News；比较或评价工具、产品、repo——"哪个好用/大家怎么说/口碑/有没有人遇到/是不是已知问题"，看 Reddit、X 等社区上的人怎么评价；搜索或读取 X/推特、Reddit、B站、V2EX、雪球、小宇宙播客、Boss直聘/LinkedIn、Facebook/Instagram；内置抓取读不到的网页（403、验证页、JS 空壳、PDF）、列出某站或某路径下全部页面 URL、读同站多页，用 Firecrawl 抓页、map、爬站。也负责 Agent Reach 的安装、加减平台、登录/退出、doctor/check 诊断与更新。只读，不发帖、评论、私信。小红书先用 redbook 技能；YouTube 字幕用 yt-dlp-capture；最近 30 天多平台热度汇总用 last30days；调研结果要写成仓库文件或 repo 调研报告用 research；查官方文档等普通读取用内置工具。
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
  version: "1.6.1.1"
---

# Agent Reach

一个命令读所有平台：`agent-reach`。只读，默认输出一行 JSON。

动手前先说一句"用 agent-reach skill（X 渠道）"。本 skill 被调用后全程有效，以下规则一直适用。

## 选路

- 用户打了 /agent-reach，至少要实际跑一条 Reach 渠道；只用 gh、自带搜索等其他工具答完，等于没照用户的意思做。
- 新闻、舆情、口碑、"有没有人遇到"这类问题，Reach 与自带搜索并列为主要来源，不是兜底：自带搜索偏网页索引，看不到 X、Reddit、V2EX、雪球里的讨论，也排不了新闻发布时间。
- 本机已装专门技能的平台（如小红书的 redbook）先用该技能，它的实际命令失败才回到 Reach；见 [下游说明](references/downstream.md)。
- 已加上的渠道（默认渠道或 `add` 过）直接走站内工具；没加的先试免登录公开网页（结果标 `backend: public-web`）。平台名或链接只用来认出来源，不自动触发安装或登录。
- 摘要、页面壳、评论计数、字幕轨道列表不等于正文、评论或字幕本身，要分别说明。

```bash
agent-reach channels                      # 每个渠道的动作和参数，不确定时先跑
agent-reach <渠道> <动作> [参数]          # 例：agent-reach google-news search "台积电" --lang zh-TW --region TW
agent-reach read <链接>                   # 按链接自动选渠道
```

只通过 `agent-reach` 调用，不直接跑 `opencli`、`twitter`、`rdt`、`mcporter`（装在私有目录，不一定在 PATH）。限时用 `--timeout 秒数`，不套 `timeout`/`gtimeout`（macOS 没有）。Reach 自己排队、控制同平台的搜索间隔，不要自己 sleep。

## 调研与新闻

用户抱怨过"没有对照新闻就胡乱分析""不够大局观"：只看搜索摘要、只查一个来源就下结论是这里最常见的错。

1. **先找带日期的报道**：`google-news search`（中文财经加 `--lang zh-TW --region TW` 或 `--lang zh-CN --region CN`）、科技/开发者话题加 `hackernews search`，再用自带搜索按时间收窄。
2. **读原文**：挑不同媒体的几篇读全文；摘要和标题不能当因果证据（"股价为什么跌"必须有原文里的说法）。`google-news` 的 `news.google.com/rss/articles/…` 链接是跳转页，谁去抓都只拿到空壳：用标题找原文 URL 再读，步骤见 [调研细节](references/research.md)。
3. **补社区视角**：按下表挑渠道；有人说法时尽量拿到原帖。
4. **交付**：每个论点、每家媒体附原文链接（不是 news.google.com）和发布日期；按平台列出跑了什么、拿到什么、哪些失败（`error.code`）。说"查无"之前要能列出查过的平台和查询词。

| 话题 | 渠道 |
|---|---|
| 财经、个股 | `google-news search`；`xueqiu quote`；雪球讨论用 `xueqiu hot_posts` 或自带搜索 `site:xueqiu.com`；`twitter search` 看英文市场 |
| 科技、开发者 | `hackernews search`、`reddit search`、`twitter search`、`v2ex hot` / `v2ex node` |
| 中文社区 | `v2ex`、`bilibili search`、雪球；小红书交给 redbook |
| 英文产品口碑 | `reddit search` / `reddit subreddit`、`twitter search`、`hackernews search`、`youtube search` |
| "有人遇到吗"、已知问题 | 先查官方 issue tracker（`gh search issues`、`github read <issue 链接>`），再查 reddit / hackernews / v2ex |

## 派子代理

用户要深度或多方面调研时，按话题拆给几个子代理并行（同平台 2 条、合计 4 条，多出来的 Reach 自动排队）。派之前主代理先实测要派的渠道：`agent-reach check <渠道1> <渠道2> --search --text`，只派 PASS 的，把要跑的命令写进任务。读 PASS 的方式、没有 search 动作的渠道怎么测、任务里要交代什么，见 [调研细节](references/research.md)。

## 读不到的网页：Firecrawl

WebFetch 或 `read` 遇到 403、超时、连线重置、验证页、JS 空壳、PDF 时，换 Firecrawl 抓（会话里的 `mcp__firecrawl__*`，或 `agent-reach firecrawl scrape|map|crawl|status`），不要放弃或自己用 curl 拼。成功 = 拿到非空正文，不是 `ok`。单页 scrape、多页先 map、选哪个动作和配置见 [Firecrawl](references/firecrawl.md)。

## 结果与错误

- `ok: true` → 内容在 `items`，每条有 `title / url / author / published_at / text`，原始数据在 `raw`。`items` 为空要说出来或换路，不当成"查过了"。
- `ok: false` → 看 `error.code`，照 `error.hint` 做：

| error.code | 怎么办 |
|---|---|
| `NEED_SETUP` | 缺依赖或密钥。按提示 `agent-reach add <渠道>`；要密钥时请用户本人提供，再 `agent-reach configure <key>` |
| `NEED_LOGIN` | `message` 提到 403 或 HTML instead of JSON 时按 `UPSTREAM_BROKEN` 处理。浏览器登录的渠道（`channels` 里 `login.via: browser`）先自己跑 `agent-reach login <渠道> --self-heal`，再重跑原来失败的动作。它被拒绝（用户退出过或手动选过账号）或仍失败才问用户，细节见 [会话与专用浏览器](references/sessions.md)；你绝不代登、不要密码 |
| `UPSTREAM_BROKEN` | 平台暂时有问题，`message` 是原话；403、"HTML instead of JSON" 多半是风控，不代表登出。`channels` 里该动作的 public_web 非空、且 `meta.attempts` 没试过 public-web 时换 `--backend public-web`；否则直接跑同渠道其他动作（如 `reddit subreddit <相关板块>`、`reddit read`）。用平台名告诉用户，不说工具名；不循环重试 |
| `TIMEOUT` | 看失败阶段和渠道状态；不反复重试、不反复开窗 |
| `RATE_LIMITED` | 站内工具返回的：Reach 暂停整个渠道一小时，停用该渠道、不换后端。`--backend public-web` 返回的：限流的是共用的网页搜索（`web search`、普通网页 `read` 同时停用），平台本身没停，照上一行跑同渠道其他动作 |
| `PLATFORM_BLOCKED` | 平台要求验证（验证码/风控）。停下，请用户在官方页面处理；不换账号、不换后端 |
| `BUSY` | 浏览器排队 2 分钟仍满，或用户正开着登录窗口。过一会儿、或等用户说登好了再试；不关窗口、不切换配置 |
| `NOT_FOUND` | 内容不存在，核对链接或 ID |
| `BAD_INPUT` | 参数不对，跑 `agent-reach channels` 看用法 |

`PLATFORM_BLOCKED`、`RATE_LIMITED`、`BUSY` 是硬停：被停的那条路不换账号、后端或浏览器反复请求（public-web 的限流例外见上）。网络失败或某台机器的失败不能说成"平台必须登录"。用户跳过登录时，已拿到的公开结果照样交付。原话说明工具过时，才在用户同意后跑一次 `agent-reach update`。

## 登录与专用浏览器

浏览器渠道共用一个专用浏览器（优先 CloakBrowser，否则本机 Chrome），默认无头，闲置 10 分钟自动关闭，下次调用自动重开。第一次用某站时，若用户 Chrome 连着 OpenCLI 扩展，会自动复制该站登录。刷新、选来源、退出等见 [会话与专用浏览器](references/sessions.md)：用户要登录、退出、换账号，或 `--self-heal` 也救不回时读它。

## 平台注意

- X 帖子链接（`x.com/<用户>/status/<id>`）用 `agent-reach read` 或 `twitter thread <链接> --limit N` 读正文与回复。
- `xueqiu search` 只按名称或代码找股票，不搜话题；`hot_posts`、`hot_stocks` 需要浏览器会话，`quote` 不需要。`github search` 只搜仓库；搜代码用 `gh search code`，搜 issue 用 `gh search issues`。GitHub 文件或目录链接由 `read` 交给 web。
- Hacker News 结果没有日期和正文：讨论与日期在 `https://news.ycombinator.com/item?id=<raw.id>`，用自带工具或 `web read` 读；`--sort date` 多是低分噪音，默认相关度即可。
- 小红书 read 只返回文字描述，不要声称看懂了图片或视频。
- Boss 直聘搜索结果 `salary_encoded=true` 时绝不猜薪资数字；read 职位链接拿详情里的可读薪资。
- 各平台公开能做什么、Reach 补什么，见 [能力边界](references/capabilities.md)：用户问"能查什么/查得全吗"时读它。

## 渠道

| channel | level | actions | login |
|---|---|---|---|
| github | default | search, read | - |
| twitter | experimental | search, profile, tweets, thread | `agent-reach login twitter` |
| youtube | default | read, search, subtitle, transcribe | - |
| reddit | optional | search, read, subreddit | 浏览器路径按需 |
| facebook | experimental | search, profile | `agent-reach login facebook` |
| instagram | experimental | search, profile, posts | `agent-reach login instagram` |
| bilibili | default | search, read, hot, subtitle | `agent-reach login bilibili` |
| xiaohongshu | optional | search, read, comments | `agent-reach login xiaohongshu` |
| linkedin | optional | jobs, read | `agent-reach login linkedin` |
| boss | optional | search, read | `agent-reach login boss` |
| v2ex | default | hot, node, read, user | - |
| google-news | default | search, top | - |
| hackernews | default | search, top, new, best, show | - |
| xueqiu | optional | quote, search, hot_posts, hot_stocks | `agent-reach login xueqiu` |
| xiaoyuzhou | optional | transcribe | - |
| web | default | search, read | - |
| firecrawl | optional | scrape, map, crawl, status | - |

`default` 是默认安装的渠道，也可以去掉，去掉后更新不会加回来。`login` 列是认证入口，不是查公开内容的前提。

## 安装完成时

`agent-reach setup` 后，把 `result.installation_report.markdown` 原样展示给用户，不增删、不重排、不自己补问候或表格；报告由程序生成。

## 用户要管理 Agent Reach 时

| 用户说 | 你运行 |
|---|---|
| 加上某个平台 | `agent-reach add <渠道>`，依赖自动装好；只告诉用户他必须做的事（登录或提供密钥） |
| 去掉某个平台 | `agent-reach remove <渠道>` |
| 登录 / 登录过期 | 照上面 `NEED_LOGIN` 那行；用户要自己登录时 `agent-reach login <渠道>`，由本人在打开的窗口里登录 |
| 退出登录 | `agent-reach logout <渠道>` |
| 看看状态 / 哪些能用 | `agent-reach doctor --text`（只看本地状态）；实测跑 `agent-reach check <渠道…> --text` |
| 升级 / 更新 | `agent-reach update` |
| 卸载 | 先 `agent-reach uninstall --dry-run` 给用户看，确认后 `agent-reach uninstall` |
| 让另一个 AI 也能用 | `agent-reach skill link <那个 AI 的 skill 目录>`；`agent-reach skill` 查看现在放在哪 |

故障排查、浏览器维护和卸载细节见 [维护说明](references/maintenance.md)：更新失败、浏览器起不来或要卸载时读它。

## 有新版本时

结果里出现 `meta.update` 就说明有新版本。本机是私有下游，先读 [下游说明](references/downstream.md) 再回应。每次对话只提一次，用用户的语言、大白话：

1. 告诉用户有新版本（`meta.update.latest`）。
2. 从 `meta.update.notes` 挑 1 到 3 个要点说清改了什么。
3. 问要不要更新；用户同意后才跑 `agent-reach update`。

## 红线

- 只读。发帖、评论、点赞、私信一律不做。
- 不替用户登录，不索要或输出密码、Cookie 等凭据。
- 普通查询不改依赖、不自动更新。
