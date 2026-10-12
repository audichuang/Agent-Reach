# 雪球

行情可能延迟，不构成投资建议。先 `agent-reach doctor --json`：`xueqiu.active_backend`
有值就按它用；`null` 只表示 Doctor 未做实时验证。雪球需要已登录会话或最小 Cookie。

## OpenCLI（桌面已有 Chrome 登录态时优先）

```bash
opencli xueqiu whoami -f yaml           # 验证登录态
opencli xueqiu search "英伟达" -f yaml
opencli xueqiu stock NVDA -f yaml
opencli xueqiu hot -f yaml
opencli xueqiu hot-stock -f yaml
opencli xueqiu --help                    # 其他只读命令
```

只复用用户已经存在且明确控制的浏览器会话，不自动执行 `opencli xueqiu login`。
无登录态时让用户先在 Chrome 登录，或显式导入最小 Cookie（只读取保存 `xq_a_token`）：

```bash
agent-reach configure --from-browser chrome --platform xueqiu
```

## 验收

- 成功 = 返回股票名称、代码、价格或非空列表；退出码 0 但字段为空不算。
- HTTP 400 通常是会话/Cookie 问题，不表示股票代码不存在。
- `whoami` 成功而 `stock`/`hot` 失败：报告为适配器解析或平台接口问题，不误诊成未登录。
