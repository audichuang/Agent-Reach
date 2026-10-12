# Firecrawl MCP

## 使用入口

优先用当前会话已连接的 Firecrawl MCP（延迟加载时先发现工具与参数）。未连接时用技能自带的
`scripts/firecrawl.py`（从 `SKILL.md` 所在目录执行，或用绝对路径）：

```bash
python3 scripts/firecrawl.py list
python3 scripts/firecrawl.py firecrawl_scrape --args '{"url":"https://example.com","formats":["markdown"]}'
```

- 以实际 server 名与 schema 为准。成功 = 非空目标正文 + 正确来源 URL + 非错误结果；工具列表、HTTP 200、空正文、验证码页都不算。脚本退出码为零仍需验收正文。
- 渲染不完整时用 schema 里的 `waitFor` 等参数；不用交互动作登录或提交表单。
- 脚本只转交 scrape/map/crawl/check_crawl_status 参数并原样输出。
- `--timeout` 单位毫秒，默认 60000；超时不重提任务。

## 连接配置

脚本只需 Python 标准库，读 `~/.agent-reach/firecrawl.json`（或 `--config`），调用本地 mcporter 或经 SSH 调用远端 mcporter，固定 `--config` 与 `--root`，不受项目同名 server 影响，不把 NAS 凭证复制到调用端。已有配置不覆盖；不存在时从已确认的 MCP 主机建一种连接：

```json
{"transport":"ssh","ssh_host":"YOUR_EXISTING_SSH_ALIAS","server":"firecrawl","mcporter_config":"/absolute/remote/home/.agent-reach/firecrawl-mcp.json"}
```

本机时 `"transport":"local"`，去掉 `ssh_host`。

- `mcporter_config` 必填，是执行端绝对路径（SSH 时为远端路径，不用 `~`）；旧配置缺此字段会在请求前报错。
- 该文件在执行端只含目标 MCP：`{"imports":[],"mcpServers":{"firecrawl":{"command":"…","args":[],"env":{}}}}`，从已有 Claude/Codex 定义复制 command/args/env（保留实际 API URL 与认证），相对路径改为执行端绝对路径；权限 0600，内容和凭证不进日志或 Git。
- `ssh_host` 必须是已配置且获授权的 SSH 别名。缺配置时脚本报错退出：不猜 NAS 地址、不安装服务、不自动改走云端、不擅改 NAS 部署。
- `firecrawl-mcp` 是桥接进程，后端 API 由其环境 `FIRECRAWL_API_URL`（需要时加 `FIRECRAWL_API_KEY`）指定；API 地址不是 MCP endpoint，不能当 `mcporter --http-url`。地址与密钥只留本机配置，不写进 skill。
- 技能与连接配置分开分发：新机器需建立自己的连接，先 `list` 再对目标页 scrape 验收。
- MCP 暴露工具不等于自架 API 支持：scrape、map、crawl 分别验证；search、JSON/LLM 提取、agent 可能需额外服务，不能由抓页成功推断。全网搜索走 search reference 的 Exa。

## 网站探索与多页采集

单页 scrape；只找 URL 用 map；要多页正文用 crawl。URL、路径、页数收窄到任务范围：

```bash
python3 scripts/firecrawl.py firecrawl_map --args '{"url":"https://example.com","limit":20,"includeSubdomains":false}'
python3 scripts/firecrawl.py firecrawl_crawl --args '{"url":"https://example.com/docs/","includePaths":["^/docs/.*"],"limit":10,"allowExternalLinks":false,"allowSubdomains":false,"scrapeOptions":{"formats":["markdown"]}}'
python3 scripts/firecrawl.py firecrawl_check_crawl_status --args '{"id":"RETURNED_CRAWL_ID"}'
```

crawl 可能同步返回或返回任务 ID：保留 ID，未完成时查同一任务，不重复提交。超时且无 ID 时只沿已有响应/日志线索查询；无线索就停止并报告结果未知，不重提、不启动替代采集。完成后核对 status、失败页、正文和分页字段，说明实际覆盖了哪些页。

## 失败退回

- Jina 失败或只给验证页 → Firecrawl scrape → 仍失败 → 已配置的 web-reader 或浏览器。
- Firecrawl 未连接/认证失败/功能不支持 → 单页退回尚未失败的 Jina 或 web-reader；不重试同一错误。
- map 空列表只表示本次未发现 URL；可读目标页链接或已知 sitemap 再逐页 scrape。
- crawl 不支持或失败 → 对已知 URL 有界逐页 scrape 并说明覆盖不足；不能冒充整站采集。
- 每个替代后端试一次仍无正文就报告具体阻塞。用户指定只用 Firecrawl 时不静默改走其他服务。
