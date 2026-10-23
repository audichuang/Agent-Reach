"""Firecrawl channel boundaries, without contacting a server or starting crawl jobs."""

import json
import shlex

import pytest

from agent_reach.channels import firecrawl
from agent_reach.runtime.result import NEED_SETUP, TIMEOUT, ReachError


def _config(tmp_path, monkeypatch, data):
    path = tmp_path / "firecrawl.json"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(firecrawl, "config_path", lambda: path)
    return path


def test_ssh_preserves_payload_as_one_argument():
    payload = {"url": "https://example.com/a?q=';$(touch /tmp/unwanted)&x=`id`"}
    cmd = firecrawl.command({"transport": "ssh", "ssh_host": "worker", "mcporter_config": "/srv/private MCP.json"},
                            "firecrawl_scrape", payload, 1000)
    remote = shlex.split(cmd[-1])
    assert cmd[-2] == "worker"
    assert remote[:3] == ["mcporter", "--config", "/srv/private MCP.json"]
    assert remote[remote.index("call") + 1] == "firecrawl.firecrawl_scrape"
    assert json.loads(remote[remote.index("--args") + 1]) == payload


@pytest.mark.parametrize("host", ["-oProxyCommand=id", "worker;id", "worker user", ""])
def test_rejects_ssh_options_or_shell_text(tmp_path, host):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"transport": "ssh", "ssh_host": host, "mcporter_config": "/tmp/mcp.json"}))
    with pytest.raises(ReachError) as exc:
        firecrawl.load_config(path)
    assert exc.value.code == NEED_SETUP


def test_missing_config_never_launches_process(tmp_path, monkeypatch):
    monkeypatch.setattr(firecrawl, "config_path", lambda: tmp_path / "absent")
    monkeypatch.setattr(firecrawl, "run_cmd", lambda *a, **k: pytest.fail("must not contact a service"))
    ch = firecrawl.FirecrawlChannel()
    assert ch.setup_problems()
    with pytest.raises(ReachError) as exc:
        ch._scrape(target="https://example.com", timeout=5)
    assert exc.value.code == NEED_SETUP


def test_timeout_does_not_resubmit_crawl(tmp_path, monkeypatch):
    _config(tmp_path, monkeypatch, {"transport": "local", "mcporter_config": "/tmp/mcp.json"})
    calls = []

    def timeout(argv, **kwargs):
        calls.append(argv)
        raise ReachError(TIMEOUT, "firecrawl did not finish")

    monkeypatch.setattr(firecrawl, "run_cmd", timeout)
    with pytest.raises(ReachError):
        firecrawl.FirecrawlChannel()._crawl(target="https://example.com", timeout=5)
    assert len(calls) == 1


def test_async_crawl_keeps_job_id(tmp_path, monkeypatch):
    _config(tmp_path, monkeypatch, {"transport": "local", "mcporter_config": "/tmp/mcp.json"})
    monkeypatch.setattr(firecrawl, "run_cmd", lambda *a, **k: '{"id": "job-1", "status": "scraping"}')
    [item] = firecrawl.FirecrawlChannel()._crawl(target="https://example.com", timeout=5)
    assert item["raw"]["id"] == "job-1"


def test_crawl_pages_carry_job_fields(tmp_path, monkeypatch):
    _config(tmp_path, monkeypatch, {"transport": "local", "mcporter_config": "/tmp/mcp.json"})
    out = {"id": "job-2", "status": "completed", "data": [
        {"markdown": "# A", "metadata": {"title": "A", "sourceURL": "https://example.com/a"}}]}
    monkeypatch.setattr(firecrawl, "run_cmd", lambda *a, **k: json.dumps(out))
    [item] = firecrawl.FirecrawlChannel()._crawl(target="https://example.com", include="^/a", timeout=5)
    assert (item["url"], item["text"], item["raw"]["id"]) == ("https://example.com/a", "# A", "job-2")


def test_read_never_routes_to_firecrawl():
    assert not firecrawl.FirecrawlChannel().can_handle("https://example.com")


def test_failure_reports_first_stderr_line(tmp_path, monkeypatch):
    from agent_reach.runtime.run import CommandFailed

    _config(tmp_path, monkeypatch, {"transport": "local", "mcporter_config": "/tmp/mcp.json"})

    def fail(*args, **kwargs):
        raise CommandFailed("UPSTREAM_BROKEN", "firecrawl exited 1: }",
                            stderr="[mcporter] firecrawl appears offline\n    at x\n}\n")

    monkeypatch.setattr(firecrawl, "run_cmd", fail)
    with pytest.raises(ReachError) as exc:
        firecrawl.FirecrawlChannel()._scrape(target="https://example.com", timeout=5)
    assert "appears offline" in exc.value.message
