# 下游说明（本机）

本机的 Agent Reach 来自私有仓库 `audichuang/Agent-Reach` 的 `local` 分支，派生自公开的 `Panniantong/Agent-Reach`。遇到专门技能、`meta.update` 或更新问题时读这份。

## 专门技能优先

- 小红书：本机装了 redbook 技能时先用它，命令前一律带 `REDBOOK_COOKIE_FILE=~/.redbook/cookies.json`（缺这个前缀时 redbook 会自己读 Chrome Cookie）。`whoami` 通过不代表每个命令都能用，以实际结果为准；`search` 报 `-104` 是账号级限制，不重试。
- redbook 的 Cookie 文件不存在、或命令真的失败，才改用 `agent-reach xiaohongshu …`。`redbook auth export` 会读浏览器，只能由用户自己跑。
- 其他平台同理：已装的专门技能先用，失败才回到 Reach。`doctor` 看不到专门技能的登录状态，doctor 的结果不代表那个技能能不能用。

## 版本与更新

- `meta.update` 表示公开上游出了新版，私有仓库需要先同步，不代表本机马上就能装到新版。告诉用户上游有新版、改了什么，并说明要先把上游合进私有 `local` 分支（照仓库 CLAUDE.md 的同步流程）；还没同步时跑 `agent-reach update` 只会重装同一版，所以不要把它当成"更新到新版"来提议。
- `agent-reach update` 只会重装私有 `local` 分支（`uv tool install --force git+https://github.com/audichuang/Agent-Reach.git@local`），不会装公开上游。私有 GitHub 认证失败就照实报告，不改用公开上游绕过。
- skill 由 aghub 从仓库 `.aghub/agent-reach/` 同步（那是渲染过的副本），不是 `agent-reach setup` 写入的；`~/.agents/skills/agent-reach` 是 aghub 的链接，Reach 不会覆盖它。更新 CLI 之后同步 skill：`aghub-cli source sync audichuang/Agent-Reach --update --yes`；从 1.5 首次切过来时 skill 路径换了，改用 `aghub-cli source sync audichuang/Agent-Reach --skill agent-reach --install-missing --yes`。
- CLI 包与 skill 是两份安装，版本号相同不代表来源相同；更新后两边都要核对。
