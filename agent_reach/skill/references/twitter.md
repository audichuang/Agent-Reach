# Twitter/X (twitter-cli)

## 认证

`agent-reach configure twitter-cookies` 隐藏输入保存的 Cookie 只供 `agent-reach doctor`
检查凭据是否齐全；doctor 不执行 `twitter status`，也不设置当前 Shell。运行任何
`twitter` 命令前，必须在同一 Shell 或子进程环境中显式提供：

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
```

凭据只用 Cookie-Editor 手工导出，不依赖自动浏览器读取。安装：`pipx install twitter-cli`（v0.8.5+）。

## 命令（可加 `--yaml`/`--json`）

```bash
twitter feed -n 20                 # 最稳定
twitter tweet URL_OR_ID            # 含回复
twitter article URL_OR_ID          # 长文 / X Article
twitter user-posts @username -n 20
twitter user @username
twitter search "query" -n 10       # 不稳定，GraphQL 常变可能 404
twitter likes                      # 只能看自己的
```

## search 失败重试链（按序，成功即停）

1. 直接重试一次。
2. `pipx upgrade twitter-cli` 后再试。
3. 桌面 OpenCLI（浏览器登录态，无需环境变量）：`opencli twitter search "query" -f yaml`；
   也支持 `article`、`user-posts`。
4. 改用 `twitter feed` / `twitter user-posts` 绕路。

IP 风控：不要在 VPS/数据中心 IP 频繁调用（尤其 followers/following），有封号风险。
