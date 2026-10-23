# Firecrawl

用户点名 Firecrawl、要站内 URL 列表或多页正文，或 web read 只拿到验证页/空壳时读这份。

## 动作

```bash
agent-reach firecrawl scrape <链接>                       # 渲染后的 Markdown
agent-reach firecrawl map <站点> --limit 20               # 只找 URL
agent-reach firecrawl crawl <起点> --limit 10 --include '^/docs/.*'
agent-reach firecrawl status <crawl 任务 ID>
```

- 单页用 scrape；只要 URL 用 map；要多页正文才 crawl。URL、路径、页数收窄到任务需要的范围。
- 成功 = 非空正文 + 正确来源 URL；空正文、验证码页不算。
- crawl 可能直接返回页面，也可能只返回任务 ID（在 `items[].raw.id`）。保留 ID，用 `status` 查同一任务，不重复提交。`TIMEOUT` 且没拿到 ID 时，结果未知：照实报告，不重提、不改用别的采集方式。
- 完成后说明实际覆盖了哪些页，对照 `raw.status`、`raw.total`。
- map 空列表只表示本次没发现 URL；可从目标页链接或已知 sitemap 逐页 scrape。crawl 失败时对已知 URL 有界逐页 scrape，并说明覆盖不足，不能当成整站采集。
- 用户指定只用 Firecrawl 时，失败就报告，不静默改走其他服务。

## 连接配置

`firecrawl` 是可选渠道：先 `agent-reach add firecrawl`，再 `agent-reach doctor --text` 看 `needs_setup` 的原因。

渠道读 `~/.agent-reach/firecrawl.json`，经本机或 SSH 上的 mcporter 调用 Firecrawl MCP：

```json
{"transport":"ssh","ssh_host":"已有的 SSH 别名","server":"firecrawl","mcporter_config":"/执行端绝对路径/firecrawl-mcp.json"}
```

- 本机执行用 `"transport":"local"`，去掉 `ssh_host`。`mcporter_config` 必须是执行端的绝对路径（SSH 时是远端路径，不用 `~`）。
- 那个 mcporter 配置只包含目标 server：`{"imports":[],"mcpServers":{"firecrawl":{"command":"…","args":[],"env":{}}}}`，command/args/env 从已有的 Claude/Codex MCP 定义复制。文件权限 0600，地址与密钥不进日志、Git 或 skill。
- 已有配置不覆盖。缺配置时只从用户确认过的 MCP 主机建立连接：不猜 NAS 地址、不装服务、不改 NAS 部署、不自动改走云端。
- MCP 列出工具不等于自架 API 都支持：scrape、map、crawl 分别实测。search、JSON 提取、agent 可能要额外服务，不能从抓页成功推断。
