# GitHub 与开发资料

用 `gh`（先 `gh auth status`，未登录让用户自己 `gh auth login`）：

```bash
gh search repos "query" --sort stars --limit 10
gh search code "query" --language python
gh repo view owner/repo
gh api repos/owner/repo/contents/PATH
```

Issue/PR/Actions/Release 用常规 `gh issue|pr|run|release` 子命令加 `-R owner/repo`。

另有 my-mcp-tools 时：读仓库内容用 zread，查库/框架文档用 context7。
