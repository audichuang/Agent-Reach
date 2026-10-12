# 小红书 / XiaoHongShu（多后端）

**认证边界**：不替用户登录，不读取浏览器 Cookie，不自动登录。认证只用用户 Cookie-Editor 手工导出（OpenCLI 例外：只用用户已有会话）。

**xsec_token**：不能用裸 note_id 读；先搜索/feed，再用结果中的完整 URL/ID 读（所有后端都一样）。高频请求触发验证码无法绕过，操作间隔 2-3 秒。只读，不做发帖/评论/点赞。

## 1. redbook（已安装时先试：`command -v redbook`）

Doctor 检测不到 redbook 的 Cookie 文件，所以 Doctor 的 `warn` / `active_backend: null` 不说明 redbook 能否用。每条命令必须带 `REDBOOK_COOKIE_FILE` 前缀，否则文件缺失时 redbook 会自动读 Chrome Cookie，越过认证边界。

```bash
REDBOOK_COOKIE_FILE=~/.redbook/cookies.json redbook whoami
REDBOOK_COOKIE_FILE=~/.redbook/cookies.json redbook search "query" --json
REDBOOK_COOKIE_FILE=~/.redbook/cookies.json redbook read "NOTE_URL" --json
```

- `whoami` 通过不保证各命令可用，以实际结果为准；`search` 报 `-104` 是账号级限制，不重试，直接回退。
- 回报时说明 `whoami` 显示的是小红书还是 RedNote；不要用 `--platform` 切换。
- 回退：Cookie 文件不存在、`whoami` 或命令失败 → `agent-reach doctor --json`，按 xiaohongshu 的 `active_backend` 选下面后端。全部不可用就如实报告；`redbook auth export` 会读浏览器，留给用户自己跑。

## 2. 后端 A：OpenCLI（桌面首选）

```bash
opencli xiaohongshu search "query" -f yaml
opencli xiaohongshu note "NOTE_URL" -f yaml     # 完整 URL，含 xsec_token
opencli xiaohongshu comments NOTE_ID -f yaml
opencli xiaohongshu feed -f yaml
opencli xiaohongshu user USER_ID -f yaml
```

需 Chrome 打开并装 OpenCLI 扩展。OpenCLI 只使用用户已经存在且明确控制的 Chrome 会话；`agent-reach configure xhs-cookies` 不会把 Cookie 注入 OpenCLI。没有现成会话就改走 B/C。

## 3. 后端 B：xiaohongshu-mcp（服务器）

```bash
agent-reach configure xhs-cookies      # 用户先用 Cookie-Editor 导出，再显式导入
mcporter call xiaohongshu.check_login_status --timeout 120000
mcporter call xiaohongshu.search_feeds keyword="query" --timeout 120000
mcporter call xiaohongshu.get_feed_detail feed_id="..." xsec_token="..." --timeout 120000
```

首次调用会下载约 150MB 无头浏览器，必须带 `--timeout 120000`。导入后先跑 `check_login_status`。导入保存 xiaohongshu.com 同域 Cookie 集（用户确认范围），其他域被忽略。

## 4. 后端 C：xhs-cli（上游 2026-03 起停更，仅存量）

```bash
xhs search "query"
xhs read NOTE_ID_OR_URL      # 用搜索结果中的 URL/ID
xhs comments NOTE_ID_OR_URL
xhs hot
xhs feed
```

`xhs user` / `user-posts` / `favorites` 可能返回 API error；写操作可能 406。新装走 A/B。
