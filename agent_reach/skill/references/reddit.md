# Reddit（必须登录态）

匿名 `.json` 端点已封（403），官方 API 新申请基本不批。先 `agent-reach doctor --json`
看 reddit 的 `active_backend`。中国大陆需代理。

## A：OpenCLI（桌面首选；需 Chrome 已登录 reddit.com）

```bash
opencli reddit search "query" -f yaml
opencli reddit read POST_ID -f yaml          # 全文 + 评论
opencli reddit subreddit LocalLLaMA -f yaml
opencli reddit subreddit-info LocalLLaMA -f yaml
opencli reddit hot -f yaml                   # 另有 popular
```

## B：rdt-cli（服务器/存量备选，上游已停更）

```bash
rdt search "query" --limit 10 --yaml
rdt read POST_ID --yaml
rdt sub python --limit 20                    # 另有 popular、all
```

安装：`pipx install 'git+https://github.com/public-clis/rdt-cli.git'`（PyPI 版落后，需 v0.4.2+）。
需先由用户 `rdt login`；服务器无浏览器时按 doctor 提示手动写 Cookie。

已持有 2025-11 前 script app 凭证的用户可用 PRAW；不要推荐新用户申请官方 API。
