# 网页与 RSS

| 需求 | 后端 |
|---|---|
| 普通单页正文 | Jina Reader：`curl -s "https://r.jina.ai/URL"` |
| Jina 返回错误、空正文或验证页；需要渲染抓页 | 已配置的 Firecrawl，读 [firecrawl.md](firecrawl.md) |
| 站内 URL 探索、多页采集 | 直接读 [firecrawl.md](firecrawl.md)，分别用 map / 有界 crawl |
| 图片或输出格式控制 | web-reader MCP（见下） |
| RSS | `feedparser`：`feedparser.parse(URL).entries` |

只有目标正文和正确来源才算成功，HTTP 200 或验证码页不算。后端失败时尝试尚未失败
且已配置的替代后端；仍无正文就说明阻塞。用户限定后端时遵守该限制。
Python reader / doctor 的 web 检查只走 Jina，不会自动切换到 Firecrawl。

```bash
mcporter call web-reader.webReader url="https://example.com"   # Markdown
# 可加 retain_images=true 或 return_format="text"
```
