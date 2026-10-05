# V2EX、Facebook、Instagram

## Contents

- [V2EX](#v2ex-公开-api)
- [Facebook](#facebookopencli必须登录态)
- [Instagram](#instagramopencli必须登录态)

其他平台分开读取：[小红书](xiaohongshu.md)、[Twitter/X](twitter.md)、[Reddit](reddit.md)、[B站](video.md)。

## V2EX (公开 API)

无需认证，直接调用公开 API。

### 热门主题

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
```

### 节点主题

```bash
# node_name 如: python, tech, jobs, qna, programmers
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"
```

### 主题详情

```bash
# topic_id 从 URL 获取，如 https://www.v2ex.com/t/1234567
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"
```

### 主题回复

```bash
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"
```

### 用户信息

```bash
curl -s "https://www.v2ex.com/api/members/show.json?username=USERNAME" -H "User-Agent: agent-reach/1.0"
```

### Python 调用示例

```python
from agent_reach.channels.v2ex import V2EXChannel

ch = V2EXChannel()

# 获取热门帖子
topics = ch.get_hot_topics(limit=10)
for t in topics:
    print(f"[{t['node_title']}] {t['title']} ({t['replies']} 回复)")

# 获取节点帖子
node_topics = ch.get_node_topics("python", limit=5)

# 获取帖子详情 + 回复
topic = ch.get_topic(1234567)
print(topic["title"], "—", topic["author"])

# 获取用户信息
user = ch.get_user("Livid")
```

> **节点列表**: https://www.v2ex.com/planes

## Facebook（OpenCLI，必须登录态）

Facebook 走 OpenCLI，复用用户 Chrome 里的 facebook.com 登录态。先跑 `agent-reach doctor --json` 看 facebook 的 `active_backend`，正常应为 `OpenCLI`。不要推荐 Jina/Exa/Graph API 作为默认路径。

```bash
# 搜索用户 / 主页 / 帖子
opencli facebook search "query" -f yaml

# 用户或主页信息
opencli facebook profile zuck -f yaml

# 当前账号 News Feed
opencli facebook feed --limit 10 -f yaml

# 当前账号可见的群组列表/最近动态
opencli facebook groups --limit 20 -f yaml
```

> 要求 Chrome 打开且装了 OpenCLI 扩展，并已登录 facebook.com。Facebook Groups 当前只承诺读取当前账号可见的群组列表/最近动态，不承诺任意群帖子和评论 API。

## Instagram（OpenCLI，必须登录态）

Instagram 走 OpenCLI，复用用户 Chrome 里的 instagram.com 登录态。先跑 `agent-reach doctor --json` 看 instagram 的 `active_backend`，正常应为 `OpenCLI`。不要默认恢复 instaloader；历史上 cookies/401/429 不稳定。

```bash
# 搜索用户（不是全站帖子关键词搜索）
opencli instagram search "query" -f yaml

# 用户 Profile
opencli instagram profile nasa -f yaml

# 用户最近帖子
opencli instagram user nasa --limit 12 -f yaml

# Explore / Discover
opencli instagram explore --limit 20 -f yaml

# 当前账号收藏
opencli instagram saved --limit 20 -f yaml
```

> 要求 Chrome 打开且装了 OpenCLI 扩展，并已登录 instagram.com。`instagram search` 是用户搜索；读帖子需要先确定 username，再用 `instagram user USERNAME`。若出现 429 / login required，先让用户在 Chrome 里重新登录并降低频率。
