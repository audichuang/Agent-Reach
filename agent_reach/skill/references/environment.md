# 环境、安装与更新

`agent-reach` 直接在 PATH 上；用本机实际的 uv tool 或 pipx 安装，不加 conda 前缀。

## 诊断

`agent-reach doctor --json` 给出各通道当前状态。`active_backend: null` 可能表示未做
实时探测；专门平台技能的凭据也可能不在 doctor 视野内。以对应 reference 的检查和
实际非空内容验收，不把工具存在、登录状态检查或旧快照当作成功获取内容。

路由表未覆盖的平台，先用 `opencli list` 找适配器，再看 `opencli <平台> --help`。
只执行当前任务需要的查询；发现适配器不等于登录态或目标内容可用。

## 私有来源维护

本技能来源是私有独立仓库 `audichuang/Agent-Reach` 的 `local` 分支；派生自
`Panniantong/Agent-Reach`。上游资料是参考，安装和同步保持私有来源。

大型跨平台任务结束时运行一次 `agent-reach check-update`，只报告新版本，不在任务中升级。
用户要求更新时，先查实际安装器及来源，再用 `uv tool upgrade agent-reach` 或
`pipx upgrade agent-reach`，并用 aghub 同步技能。私有 GitHub 读取需要已授权凭证；
认证失败就报告，不切回公开上游来绕过。

CLI 包与 aghub 技能是两份安装；相同版本号不能证明同一来源。更新后核对来源、
技能链接和实际使用的脚本。`agent-reach install --system` 会用 CLI 包的技能覆盖
现有技能及 aghub 链接；Boss 渠道的必要安装与恢复流程见 [boss.md](boss.md)。

需要合并上游改动时先 `git fetch upstream`；确认有新提交，再按仓库规则把
`local` rebase 到 `upstream/main`。独立仓库不使用 GitHub fork 的同步功能。

## 临时资料

采集临时文件放 `/tmp/`，持久配置放 `~/.agent-reach/`。用户指定的输出位置优先。
