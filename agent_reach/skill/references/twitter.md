# Twitter/X (twitter-cli)

## 认证前置条件

`agent-reach configure twitter-cookies` 通过隐藏输入保存的 Cookie 只供
`agent-reach doctor` 检查显式凭据是否齐全。`doctor` 不执行上游
`twitter status`，也不会设置当前 Shell。运行下面任何 `twitter` 命令前，
必须在同一个 Shell 或子进程环境中显式提供：

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
```

## 稳定命令

```bash
# 首页时间线（最稳定）
twitter feed -n 20

# 读取单条推文（含回复）
twitter tweet URL_OR_ID

# 读取长文 / X Article
twitter article URL_OR_ID

# 用户时间线
twitter user-posts @username -n 20

# 用户资料
twitter user @username
```

## 可能不稳定的命令

```bash
# 搜索推文（Twitter 频繁改 GraphQL 端点，可能 404）
twitter search "query" -n 10

# likes（2024 年后只能看自己的，平台限制）
twitter likes
```

## search 失败时的重试链（按序执行，成功即停）

1. 直接重试一次（偶发失败常见）：`twitter search "query" -n 10`
2. 升级后再试：`pipx upgrade twitter-cli && twitter search "query" -n 10`
3. 换 OpenCLI 备选（桌面，复用浏览器登录态）：`opencli twitter search "query" -f yaml`
4. 都不行就改用 `twitter feed` / `twitter user-posts @somebody` 等稳定命令绕路

## 重要注意事项

> **安装**: `pipx install twitter-cli`（确保 v0.8.5+）
>
> **认证**: 只用 Cookie-Editor 手工导出，再显式设置环境变量
> `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`；不要依赖自动浏览器读取。
>
> **IP 风控**: 不要在 VPS/数据中心 IP 上频繁调用，尤其是 followers/following，有封号风险。使用住宅代理或本地环境。
>
> **OpenCLI 备选**: 桌面装了 OpenCLI 的话，`opencli twitter search/article/user-posts -f yaml` 全套可用（浏览器登录态，无需 cookie 环境变量）。
>
> **输出格式**: 建议用 `--yaml` 或 `--json` 获得结构化输出，对 AI agent 更友好。
