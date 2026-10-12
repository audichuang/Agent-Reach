# Boss直聘

## 安装与登录边界

- 未安装：获授权后运行 `agent-reach install --env=local --system --channels=boss`。
  `--system` 会换成 CLI 包随附的技能并替换 aghub 链接；先说明影响，装后用 aghub 恢复本私有来源，
  `aghub-cli -g doctor --verify-links` 验证。
- “帮我配 Boss直聘”：由 Agent 完成安装、拉起专用 Chrome、等用户手动登录、最终验证。
  别先把 9222 等细节甩给用户；不替用户输账号、扫码或过滑块。
- 上游锁定提交 `4c991b77086a203173bf08a4cb64a23af6514fe6`（非 branch）。

**登录门槛 ≠ 安全校验。** 落地页可能是已登录 `web/geek/job`、未登录 `web/user/`、或反爬安全校验页
（URL 含 `security-check` / `zhipin-security` / `_security_check`，带 CDP 的 Chrome 已登录也几乎必现）。
绝不用当前 URL 判断登录态；安全校验页等它自动放行或让用户手动过滑块，不要当未登录重新登录。

**两份凭据，都不能删：**
- `~/.boss-agent/auth/session.enc`：硬性门槛（缺失则 `AuthRequired`，CDP 搜索连浏览器前就失败）；
  只给 httpx 低危 op（`status`/`detail`/`cities`/`job_card_httpx`）当凭据。要刷新就跑 `login --cdp`。
- 专用 Chrome profile 的 cookie：CDP 下 search/greet 等实际用的凭据。

`boss status` / `status --live` 只校验 session.enc，`logged_in: true` 不代表浏览器已登录。
浏览器登录态以 `agent-reach doctor` boss 行的 wt2 cookie 探测为准，其次用户肉眼确认（右上角头像）。

## 体检与恢复

`agent-reach doctor`（无副作用）：boss 行 `off` = 未装或 CDP 不通；`warn` = 链路就绪，message 注明有无 wt2。
`off`/`warn` 时按序排查，不读源码瞎猜：

1. `curl -s http://localhost:9222/json/version` 有 `Browser` 字段 = 端口通。
2. 不通则启动专用 Chrome（只绑回环；任何能访问 9222 的进程都能完全控制该 Chrome）：
   ```bash
   # macOS 用 open -na "Google Chrome" --args ...；Windows 用 Start-Process chrome.exe -ArgumentList ...（profile 用 $env:USERPROFILE\.boss-chrome-profile）
   google-chrome --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 \
     --user-data-dir="$HOME/.boss-chrome-profile" "https://www.zhipin.com/web/geek/job"
   ```
   该 profile 长期复用以保留登录态：不要删除/新建，不默认切日常 Chrome，不用时关窗。
   **拉起后先暂停，让用户肉眼确认已登录**，再允许搜索。
3. 浏览器未登录（无 wt2）：让用户在专用窗口登录，确认后保存：
   `boss --cdp-url http://localhost:9222 login --cdp`

## 搜索

搜索时必须用严格 CDP 模式（全局选项放子命令前）：

```bash
boss --browser-source existing-browser --cdp-url http://localhost:9222 search "大模型" --city 广州 --page 1
```

搜索 + JD（隔离环境用 `uv run --with`，普通 `python` 不一定能 import）：

```bash
uv run --isolated --no-project \
  --with 'git+https://github.com/can4hou6joeng4/boss-agent-cli.git@4c991b77086a203173bf08a4cb64a23af6514fe6' \
  python - <<'PY'
from pathlib import Path
from boss_agent_cli.api.client import BossClient
from boss_agent_cli.auth.manager import AuthManager
from boss_agent_cli.platforms.zhipin import BossPlatform

auth = AuthManager(Path.home() / ".boss-agent")
# strict CDP: reuse logged-in browser, fail fast, never headless
with BossClient(auth, cdp_url="http://localhost:9222",
                browser_source="existing-browser") as boss:
    raw = boss.search_jobs("大模型", city="深圳", page=1)
    if raw.get("code") != 0:
        code, message = BossPlatform(boss).parse_error(raw)
        raise RuntimeError(f"{code}: {message}")
    for item in raw.get("zpData", {}).get("jobList", []):
        card = boss.job_card_browser(item["securityId"], item["lid"])
        print(item.get("jobName"),
              card.get("zpData", {}).get("jobCard", {}).get("postDescription", ""))
PY
```

串行、降频，不要无提示连续翻页。节流时 CLI 静默等 5–10 秒（`--json` 下无提示），属预期：
等待中不重试、不拉新浏览器、不换 profile。

## 错误码

- `AUTH_EXPIRED` = ground truth：浏览器未登录（不管 `boss status`），走上面第 3 步登录 + `login --cdp`，
  禁止解释成安全校验；安全校验页只在无 `AUTH_EXPIRED` 时按滑块处理。
- code 36（`AccountRiskError` / ACCOUNT_RISK）→ 立即停，用户到 BOSS 页面手动处理，不重试。
- code 37 + `环境存在异常` → `ENVIRONMENT_RISK`（`EnvironmentRiskError`）→ 立即停，不刷新 Token、不重登、不重试。
- 只有文案明确 token/stoken 过期的 code 37 才是 `TOKEN_REFRESH_FAILED`：客户端最多自动刷新重试一次，仍失败再重新登录。
- code 9（RATE_LIMITED）→ 冷却后重试。
