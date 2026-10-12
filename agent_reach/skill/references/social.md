# V2EX、Facebook、Instagram

其他平台见：[小红书](xiaohongshu.md)、[Twitter/X](twitter.md)、[Reddit](reddit.md)、[B站](video.md)。

## V2EX（公开 API，无需认证）

`curl -s URL -H "User-Agent: agent-reach/1.0"`，base `https://www.v2ex.com/api`：

- 热门：`/topics/hot.json`
- 节点：`/topics/show.json?node_name=python&page=1`（节点名如 tech/jobs/qna/programmer，全表见 https://www.v2ex.com/planes ）
- 主题详情：`/topics/show.json?id=TOPIC_ID`（ID 来自 `/t/1234567`）
- 回复：`/replies/show.json?topic_id=TOPIC_ID&page=1`
- 用户：`/members/show.json?username=USERNAME`

## Facebook / Instagram（OpenCLI，必须登录态）

复用用户 Chrome 里已登录的 facebook.com / instagram.com 会话（需 Chrome 打开并装 OpenCLI 扩展）。先 `agent-reach doctor --json` 确认 `active_backend` 为 `OpenCLI`。不要默认改用 Jina/Exa/Graph API 或 instaloader。

```bash
opencli facebook search "query" -f yaml
opencli facebook profile zuck -f yaml
opencli facebook feed --limit 10 -f yaml
opencli facebook groups --limit 20 -f yaml      # 仅当前账号可见群组列表/最近动态

opencli instagram search "query" -f yaml        # 只搜用户，不搜帖子
opencli instagram profile nasa -f yaml
opencli instagram user nasa --limit 12 -f yaml  # 读帖子：先确定 username
opencli instagram explore --limit 20 -f yaml
opencli instagram saved --limit 20 -f yaml
```

Facebook 不承诺任意群帖子/评论。Instagram 出现 429 / login required：让用户在 Chrome 重新登录并降低频率。
