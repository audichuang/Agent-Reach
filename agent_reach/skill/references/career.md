# LinkedIn

Boss直聘见 [boss.md](boss.md)。

```bash
mcporter call linkedin.get_person_profile linkedin_username="username" sections="experience,education"
mcporter call linkedin.search_people keywords="AI engineer" location="Shanghai"
mcporter call linkedin.get_company_profile company_name="openai" sections="posts,jobs"
mcporter call linkedin.search_jobs keywords="software engineer" location="Remote" max_pages=2
```

需要登录态：首次由用户运行 `uvx mcp-server-linkedin@latest --login`。
MCP 不可用时回退 `curl -s "https://r.jina.ai/https://linkedin.com/in/username"`。
