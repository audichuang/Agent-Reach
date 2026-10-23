# -*- coding: utf-8 -*-
"""Firecrawl — scrape, map and crawl through a configured Firecrawl MCP server.

Downstream channel: calls go through mcporter, locally or over an existing SSH
alias, as described by ~/.agent-reach/firecrawl.json. Nothing is installed and
no API address or key lives in this package.
"""

import json
import re
import shlex
import shutil
from pathlib import Path
from typing import List, Optional

from agent_reach.runtime.result import BAD_INPUT, NEED_SETUP, UPSTREAM_BROKEN, ReachError, make_item
from agent_reach.runtime.run import CommandFailed, run_cmd

from .base import Action, Channel, Param

_SETUP_HINT = "See the agent-reach skill's references/firecrawl.md; no request was sent."


def config_path() -> Path:
    return Path.home() / ".agent-reach" / "firecrawl.json"


def load_config(path: Path) -> dict:
    """Validated connection config; raises ReachError(NEED_SETUP) when unusable."""
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ReachError(NEED_SETUP, f"Firecrawl connection config missing: {path}", hint=_SETUP_HINT)
    except (OSError, ValueError) as exc:
        raise ReachError(NEED_SETUP, f"Firecrawl connection config unreadable: {exc}", hint=_SETUP_HINT)
    problem = None
    if not isinstance(config, dict):
        problem = "connection config must be a JSON object"
    elif config.get("transport") not in ("local", "ssh"):
        problem = "transport must be local or ssh"
    elif not isinstance(config.get("mcporter_config"), str) or not Path(config["mcporter_config"]).is_absolute():
        problem = "mcporter_config must be an absolute path on the execution host"
    elif not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_-]*", str(config.get("server", "firecrawl"))):
        problem = "server must be an MCP server name"
    elif config["transport"] == "ssh" and not re.fullmatch(
            r"[A-Za-z0-9_][A-Za-z0-9_.-]*", str(config.get("ssh_host", ""))):
        problem = "ssh_host must be an existing SSH alias, without options"
    if problem:
        raise ReachError(NEED_SETUP, f"Invalid Firecrawl config: {problem}", hint=_SETUP_HINT)
    return config


def command(config: dict, tool: str, arguments: dict, timeout_ms: int) -> List[str]:
    server = config.get("server", "firecrawl")
    # Explicit config bypasses cwd-dependent project and editor discovery.
    cmd = ["mcporter", "--config", config["mcporter_config"],
           "--root", str(Path(config["mcporter_config"]).parent),
           "call", f"{server}.{tool}", "--args", json.dumps(arguments),
           "--timeout", str(timeout_ms), "--no-oauth"]
    if config["transport"] == "ssh":
        # SSH passes its command through a remote shell: quote every argument once.
        return ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                config["ssh_host"], shlex.join(cmd)]
    return cmd


def _http_url(value: str) -> str:
    url = str(value).strip()
    if not re.match(r"https?://", url, re.IGNORECASE):
        raise ReachError(BAD_INPUT, "target must be an http(s) URL")
    return url


def _page(page: dict, job: dict) -> dict:
    meta = page.get("metadata") or {}
    return make_item(title=meta.get("title"), url=meta.get("sourceURL") or meta.get("url"),
                     text=page.get("markdown"), raw={"metadata": meta, **job})


def _job_items(data: dict) -> list:
    """Crawl/status result; the job id stays in every item so nobody resubmits."""
    job = {k: data.get(k) for k in ("id", "status", "completed", "total", "next") if k in data}
    pages = [_page(p, job) for p in data.get("data") or [] if isinstance(p, dict)]
    if pages:
        return pages
    if not job.get("id"):
        raise ReachError(UPSTREAM_BROKEN, f"Firecrawl returned no pages and no job id: {str(data)[:300]}")
    return [make_item(title=f"crawl {job['id']}: {job.get('status') or 'unknown'}", raw=job)]


class FirecrawlChannel(Channel):
    name = "firecrawl"
    description = "Firecrawl 抓页、站内 URL 探索、多页采集（自架 MCP）"

    level = "optional"

    actions = (
        Action("scrape", "Rendered page as Markdown",
               (Param("target", "page URL"),),
               (("firecrawl-mcp", "_scrape"),),
               live_test={"target": "https://example.com"}),
        Action("map", "Discover URLs on a site",
               (Param("target", "site URL"),
                Param("limit", "max URLs", required=False, type=int, default=20)),
               (("firecrawl-mcp", "_map"),)),
        Action("crawl", "Multi-page crawl; returns pages or a job id to poll with `status`",
               (Param("target", "start URL"),
                Param("limit", "max pages", required=False, type=int, default=10),
                Param("include", "regex of paths to keep, e.g. ^/docs/.*", required=False)),
               (("firecrawl-mcp", "_crawl"),), timeout=300),
        Action("status", "Progress and pages of a crawl job",
               (Param("target", "crawl job id"),),
               (("firecrawl-mcp", "_status"),)),
    )

    def setup_problems(self):
        try:
            config = load_config(config_path())
        except ReachError as exc:
            return [exc.message]
        need = "ssh" if config["transport"] == "ssh" else "mcporter"
        return [] if shutil.which(need) else [f"{need} not found on PATH"]

    def can_handle(self, url: str) -> bool:
        # Any URL qualifies, so `read` must never pick this channel implicitly.
        return False

    def _call(self, tool: str, arguments: dict, timeout: float) -> dict:
        config = load_config(config_path())
        try:
            out = run_cmd(command(config, tool, arguments, int(timeout * 1000)),
                          timeout=timeout + 15, label="firecrawl")
        except CommandFailed as exc:
            # mcporter ends stderr with a stack trace; its first line carries the reason.
            first = next((ln.strip() for ln in exc.stderr.splitlines() if ln.strip()), "")
            raise ReachError(UPSTREAM_BROKEN, f"Firecrawl: {first[:300]}" if first else exc.message)
        try:
            data = json.loads(out)
        except ValueError:
            raise ReachError(UPSTREAM_BROKEN, f"Firecrawl: {out.strip()[:300] or 'empty response'}")
        if not isinstance(data, dict):
            raise ReachError(UPSTREAM_BROKEN, f"Firecrawl returned unexpected data: {str(data)[:300]}")
        return data

    def _scrape(self, *, target: str, timeout: float) -> list:
        data = self._call("firecrawl_scrape", {"url": _http_url(target), "formats": ["markdown"]}, timeout)
        if not (data.get("markdown") or "").strip():
            raise ReachError(UPSTREAM_BROKEN, "Firecrawl returned an empty page")
        return [_page(data, {})]

    def _map(self, *, target: str, limit: int = 20, timeout: float) -> list:
        data = self._call("firecrawl_map", {"url": _http_url(target), "limit": int(limit),
                                             "includeSubdomains": False}, timeout)
        return [make_item(title=link.get("title"), url=link.get("url"), text=link.get("description"), raw=link)
                for link in data.get("links") or [] if isinstance(link, dict) and link.get("url")]

    def _crawl(self, *, target: str, limit: int = 10, include: Optional[str] = None, timeout: float) -> list:
        args = {"url": _http_url(target), "limit": int(limit), "allowExternalLinks": False,
                "allowSubdomains": False, "scrapeOptions": {"formats": ["markdown"]}}
        if include:
            args["includePaths"] = [str(include)]
        return _job_items(self._call("firecrawl_crawl", args, timeout))

    def _status(self, *, target: str, timeout: float) -> list:
        return _job_items(self._call("firecrawl_check_crawl_status", {"id": str(target).strip()}, timeout))
