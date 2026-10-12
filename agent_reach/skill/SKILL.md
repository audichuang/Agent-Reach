---
name: agent-reach
description: >
  读取或搜索需专用 CLI/MCP 的平台：X/推特、Reddit、B站、V2EX、小宇宙播客、雪球、Boss直聘/LinkedIn、Facebook/Instagram、小红书/小紅書，以及 Firecrawl 抓页/爬站；也负责这些读取工具的安装、Cookie 配置与 doctor 诊断。普通网页搜索、读 URL 用内置工具；有专门技能的平台交给该技能。
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach

选择互联网读取后端，直接使用对应工具。只读取当前任务需要的参考文件。

## 执行约定

- 已安装专门平台技能时先用它；实际命令失败才走本技能的回退链。
- 多后端或登录态平台先跑 Doctor：`agent-reach doctor --json`；专门技能的首次尝试不需要。
  `active_backend: null` 或 `warn` 不代表不可用，按平台 reference 复核。
- 说明使用的平台与后端；从实际取得的内容归纳并附来源，未取得的内容如实说明。
- 登录与验证码由用户处理；凭据和现有会话按平台 reference 规定的授权方式使用。
- 失败按对应 reference 的重试与停止条件处理。大型调研结束时按
  [environment.md](references/environment.md) 检查版本，不在调研中升级。

## 按需求读取

| 需求 | 参考文件 |
|---|---|
| 全网搜索、技术资料检索 | [search.md](references/search.md) |
| GitHub 仓库、代码及 Issue/PR 资料检索 | [dev.md](references/dev.md) |
| 小红书 / redbook | [xiaohongshu.md](references/xiaohongshu.md) |
| Twitter / X；凭据需传入 TWITTER_AUTH_TOKEN、TWITTER_CT0 | [twitter.md](references/twitter.md) |
| Reddit | [reddit.md](references/reddit.md) |
| V2EX、Facebook、Instagram | [social.md](references/social.md) |
| LinkedIn 资料与职位 | [career.md](references/career.md) |
| Boss直聘查询或“帮我配 Boss直聘” | [boss.md](references/boss.md) |
| 普通网页、RSS | [web.md](references/web.md) |
| Firecrawl 抓页、站内 URL 探索、多页采集 | [firecrawl.md](references/firecrawl.md) |
| YouTube、B站、小宇宙字幕与转写 | [video.md](references/video.md) |
| 雪球行情与讨论 | [finance.md](references/finance.md) |
| 工具不可用、适配器发现、安装或版本更新 | [environment.md](references/environment.md) |
