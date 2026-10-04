# 网页阅读

通用网页、网站探索、多页采集、RSS。平台专用后端仍按对应 reference 路由。

## Contents

- [选择指南](#选择指南)
- [Jina Reader](#通用网页-jina-reader)
- [Firecrawl：连接、采集与退回](#firecrawl-可选-mcp)
- [Web Reader](#web-reader-mcp)
- [RSS](#rss-feedparser)

## 选择指南

| 场景 | 推荐工具 |
|-----|---------|
| 普通单页阅读 | Jina Reader |
| Jina 失败、正文缺失，或明确要求 Firecrawl/渲染抓页 | 已配置的 Firecrawl `firecrawl_scrape` |
| 寻找站内页面 URL | Firecrawl `firecrawl_map`，再抓选中的页面 |
| 采集多页正文 | Firecrawl `firecrawl_crawl`，限定路径与页数 |
| 需要图片/格式控制 | 已配置的 web-reader MCP，或按 Firecrawl schema 选择输出格式 |
| RSS 订阅 | feedparser |

Firecrawl 是可选的 skill 路由：当前 `agent-reach doctor` 的 web 检查和 Python
`read()` 仍走 Jina，不探测或自动回退到 Firecrawl。检查 Firecrawl 要直接调用它。

## 通用网页 (Jina Reader)

```bash
# 读取任意网页内容
curl -s "https://r.jina.ai/URL"

# 示例
curl -s "https://r.jina.ai/https://example.com/article"
```

**适用场景**: 大多数网页可以直接用 Jina Reader 读取。

## Firecrawl (可选 MCP)

先用当前 agent 已连接的 Firecrawl MCP；工具延迟加载时先发现工具与参数。
CLI 场景可用 mcporter，它也可能从 Claude/Codex 配置导入服务：

```bash
mcporter list firecrawl --schema
mcporter call firecrawl.firecrawl_scrape --args '{"url":"https://example.com","formats":["markdown"]}'
```

以实际 server 名与 schema 为准。只有非空目标正文、正确来源 URL 和非错误结果
才能证明抓页成功；工具列表、HTTP 200、空正文或验证码页都不算。
渲染不完整时，按 schema 使用 `waitFor` 等抓页参数，避免把交互动作用于登录或提交表单。

### 连接与自架边界

`firecrawl-mcp` 是客户端桥接进程；NAS 上的 Firecrawl API 是它的后端。
自架连接读取 MCP 进程环境中的 `FIRECRAWL_API_URL`，需要认证时另配
`FIRECRAWL_API_KEY`。API 的 HTTP 地址不是 MCP endpoint，不能直接当作
`mcporter --http-url` 的地址。主机地址与密钥留在机器本地配置，不写入 skill。

配置只在另一台机器时，使用已获授权的 SSH 别名在该机执行相同 mcporter 命令；
本机未发现服务不代表远端没装。没有可用配置时先用其他阅读后端，安装/连接配置
作为单独步骤处理，不擅自改 NAS 部署。

MCP 暴露工具不等于自架 API 支持它们。分别验证 scrape、map、crawl；
search、JSON/LLM 提取、agent 等功能可能需要额外服务或凭证，不能用抓页成功
推断它们可用。全网搜索继续走 search reference 的 Exa 路由。

### 网站探索与多页采集

先按任务选择 map（只找 URL）或 crawl（取多页正文），单页任务直接 scrape。
以下为参数示例；将 URL、路径与页数收窄到用户任务范围：

```bash
mcporter call firecrawl.firecrawl_map --args '{"url":"https://example.com","limit":20,"includeSubdomains":false}'
mcporter call firecrawl.firecrawl_crawl --args '{"url":"https://example.com/docs/","includePaths":["^/docs/.*"],"limit":10,"allowExternalLinks":false,"allowSubdomains":false,"scrapeOptions":{"formats":["markdown"]}}'
mcporter call firecrawl.firecrawl_check_crawl_status --args '{"id":"RETURNED_CRAWL_ID"}'
```

crawl 可能等待任务完成才返回，也可能返回任务 ID；按实际结果处理。保留 ID，
未完成时查询同一任务，不重复提交。超时且未拿到 ID 时报告结果未知，先查已有
任务证据。完成后核对 status、失败页、实际正文和分页字段，明确说明只覆盖了哪些页。

### 失败退回

- Jina 失败或只给验证页 → 已配置的 Firecrawl scrape；Firecrawl 仍失败 → 已配置的 web-reader 或浏览器读取。
- Firecrawl 未连接/认证失败/功能不支持 → 单页退回尚未失败的 Jina 或 web-reader；停止重试同一错误。
- map 返回空列表只说明本次没有发现 URL；可读目标页链接或已知 sitemap，再逐页 scrape。
- crawl 不支持或失败 → 对已知 URL 做有界逐页 scrape，说明覆盖不足；单页工具不能冒充完整整站采集。

每个替代后端尝试一次后仍无正文，就报告具体阻塞；用户明确指定只用 Firecrawl 时，
尊重该约束，不静默改走其他服务。

## Web Reader (MCP)

```bash
# 读取网页内容 (Markdown 格式)
mcporter call web-reader.webReader url="https://example.com"

# 保留图片
mcporter call web-reader.webReader url="https://example.com" retain_images=true

# 纯文本格式
mcporter call web-reader.webReader url="https://example.com" return_format="text"
```

**适用场景**: 需要更精确控制输出格式时使用。

## RSS (feedparser)

```python
python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:5]:
    print(f'{e.title} — {e.link}')
"
```

**适用场景**: 订阅博客、新闻源、播客等 RSS feed。
