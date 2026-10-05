# 小红书 / XiaoHongShu（多后端）

## 先试 redbook（已安装时：`command -v redbook`）

redbook 用自己保存的 Cookie 文件，Doctor 检测不到，所以 Doctor 对小红书的 `warn` /
`active_backend: null` 不说明 redbook 能不能用。每条 redbook 命令都带
`REDBOOK_COOKIE_FILE` 前缀：不带时如果 `~/.redbook/cookies.json` 不存在，redbook 会自动去读
Chrome Cookie，越过下面「不读取浏览器 Cookie」的边界；带上后文件缺失就直接报错。

```bash
REDBOOK_COOKIE_FILE=~/.redbook/cookies.json redbook whoami
REDBOOK_COOKIE_FILE=~/.redbook/cookies.json redbook search "query" --json
REDBOOK_COOKIE_FILE=~/.redbook/cookies.json redbook read "NOTE_URL" --json   # 用搜索结果里的 URL
```

- `whoami` 通过只说明账号连得上，不保证每个命令可用，以实际命令结果为准。例如 `search` 报
  `-104` 是账号级接口限制（redbook 文档），不要重试，直接回退。
- `whoami` 会显示账号属于小红书（xiaohongshu.com）还是 RedNote（rednote.com），回报时说明用的是哪个。
  Cookie 文件只对应一个平台，不要用 `--platform` 去切换。
- **回退**：Cookie 文件不存在、`whoami` 失败、或要用的命令失败 → 跑 `agent-reach doctor --json`，
  按下面三个后端继续。全部不可用就如实报告；不要替用户登录或导出 Cookie
  （`redbook auth export` 会读浏览器，留给用户自己在终端跑）。

## Agent Reach 自带的三个后端

小红书有三个后端，**先跑 `agent-reach doctor --json` 看 xiaohongshu 的 `active_backend` 是哪个**，再用对应命令组。

## 后端 A：OpenCLI（桌面首选）

```bash
# 搜索笔记
opencli xiaohongshu search "query" -f yaml

# 读笔记正文+互动数据（用搜索结果里的完整 URL，含 xsec_token）
opencli xiaohongshu note "NOTE_URL" -f yaml

# 评论（支持楼中楼）
opencli xiaohongshu comments NOTE_ID -f yaml

# 首页推荐 feed
opencli xiaohongshu feed -f yaml

# 用户主页公开笔记
opencli xiaohongshu user USER_ID -f yaml
```

> 要求 Chrome 打开且装了 OpenCLI 扩展。OpenCLI 只使用用户已经存在且明确控制
> 的 Chrome 会话；Agent Reach 不替用户登录，也不读取浏览器 Cookie。
> `agent-reach configure xhs-cookies` 不会把 Cookie 注入 OpenCLI。
> 如果没有现成会话，不要自动登录；改走后端 B/C，并按对应的
> Cookie-Editor 手工导出流程配置。

## 后端 B：xiaohongshu-mcp（服务器场景）

```bash
# 认证前先让用户用 Cookie-Editor 手工导出，再显式导入
agent-reach configure xhs-cookies

# 只读检查当前状态
mcporter call xiaohongshu.check_login_status --timeout 120000

# 搜索
mcporter call xiaohongshu.search_feeds keyword="query" --timeout 120000

# 笔记详情+评论（feed_id 和 xsec_token 从搜索结果取）
mcporter call xiaohongshu.get_feed_detail feed_id="..." xsec_token="..." --timeout 120000
```

> 首次调用会自动下载约 150MB 无头浏览器，务必带 `--timeout 120000`。
> 认证只走 Cookie-Editor 手工导出；导入后先运行 `check_login_status`。
> 该显式命令会保存/导入用户提供的 xiaohongshu.com 同域 Cookie 集，用户应
> 确认范围；非 xiaohongshu.com 域 Cookie 会被忽略。

## 后端 C：xhs-cli（存量备选，上游 2026-03 起停更）

```bash
xhs search "query"          # 搜索
xhs read NOTE_ID_OR_URL     # 读笔记（必须用搜索结果中的 URL/ID，不能裸 note_id）
xhs comments NOTE_ID_OR_URL # 评论
xhs hot                     # 热门
xhs feed                    # 推荐
```

> 已知不稳定：`xhs user` / `xhs user-posts` / `xhs favorites` 可能返回 API error（上游停更无人修）。新装用户建议直接走后端 A/B。

## 通用注意事项

> **认证边界**: Agent Reach 不得替用户执行小红书登录，也不得读取浏览器
> Cookie。OpenCLI 只能使用用户已有且明确控制的 Chrome 会话；
> xiaohongshu-mcp / 存量工具使用 Cookie-Editor 手工导出。
>
> **xsec_token 限制**: 小红书强制 xsec_token 机制，**不能直接用裸 note_id 去读**。正确流程：先搜索/feed 拿结果，再用结果中的完整 URL/ID 去读。三个后端都一样。
>
> **频率控制**: 高频请求（批量搜索、深翻评论）会触发验证码，平台限制无法绕过。每次操作间隔 2-3 秒。
>
> **写操作（发帖/评论/点赞）**: 建议只读。xhs-cli v0.6.x 写操作可能因签名问题返回 406。
