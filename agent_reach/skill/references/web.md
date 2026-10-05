# 网页与 RSS

| 需求 | 后端 |
|---|---|
| 普通单页正文 | Jina Reader |
| Jina 返回错误、空正文或验证页；需要渲染抓页 | 已配置的 Firecrawl，读 [firecrawl.md](firecrawl.md) |
| 站内 URL 探索、多页采集 | 直接读 [firecrawl.md](firecrawl.md)，分别用 map / 有界 crawl |
| 图片或输出格式控制 | 已配置的 web-reader MCP |
| RSS 订阅内容 | feedparser |

只有目标正文和正确来源才能算成功，HTTP 200 或验证码页不算。后端失败时尝试尚未失败
且已配置的替代后端；仍无正文就说明阻塞。用户限定后端时遵守该限制。
当前 Python reader / doctor 的 web 检查仍只走 Jina，不会自动切换到 Firecrawl。

## 通用网页 (Jina Reader)

```bash
# 读取任意网页内容
curl -s "https://r.jina.ai/URL"

# 示例
curl -s "https://r.jina.ai/https://example.com/article"
```

**适用场景**: 大多数网页可以直接用 Jina Reader 读取。

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
