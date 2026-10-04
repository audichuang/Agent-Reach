"""Verify relay boundaries without contacting a server or starting crawl jobs."""

import importlib.util
import json
import shlex
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "agent_reach/skill/scripts/firecrawl.py"
spec = importlib.util.spec_from_file_location("firecrawl_relay", SCRIPT)
relay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(relay)


def test_ssh_preserves_payload_as_one_argument():
    payload = {"url": "https://example.com/a?q=';$(touch /tmp/unwanted)&x=`id`"}
    cmd = relay.command({"transport": "ssh", "ssh_host": "worker"}, "firecrawl_scrape", payload, 1000)
    remote = shlex.split(cmd[-1])
    assert cmd[-2] == "worker"
    assert remote[:3] == ["mcporter", "call", "firecrawl.firecrawl_scrape"]
    assert json.loads(remote[remote.index("--args") + 1]) == payload


@pytest.mark.parametrize("host", ["-oProxyCommand=id", "worker;id", "worker user", ""])
def test_rejects_ssh_options_or_shell_text(tmp_path, host):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"transport": "ssh", "ssh_host": host}))
    with pytest.raises(ValueError):
        relay.load_config(path)


def test_missing_config_never_launches_process(tmp_path, monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("must not contact a service without connection config")
    monkeypatch.setattr(relay.subprocess, "run", unexpected)
    assert relay.main(["list", "--config", str(tmp_path / "absent")]) == 2


def test_timeout_does_not_resubmit_crawl(tmp_path, monkeypatch, capsys):
    path = tmp_path / "config.json"
    path.write_text('{"transport":"local"}')
    calls = []
    def timeout(cmd, **kwargs):
        calls.append(cmd)
        raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])
    monkeypatch.setattr(relay.subprocess, "run", timeout)
    assert relay.main(["firecrawl_crawl", "--config", str(path)]) == 124
    assert len(calls) == 1
    assert "unknown" in capsys.readouterr().err


def test_local_relay_preserves_failure(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text('{"transport":"local","server":"nas-firecrawl"}')
    def failure(cmd, **kwargs):
        assert cmd[:3] == ["mcporter", "call", "nas-firecrawl.firecrawl_scrape"]
        return subprocess.CompletedProcess(cmd, 7)
    monkeypatch.setattr(relay.subprocess, "run", failure)
    assert relay.main(["firecrawl_scrape", "--config", str(path)]) == 7
