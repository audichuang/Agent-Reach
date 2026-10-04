"""Verify relay boundaries without contacting a server or starting crawl jobs."""

import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "agent_reach/skill/scripts/firecrawl.py"
REAL_HOME = str(Path.home())
spec = importlib.util.spec_from_file_location("firecrawl_relay", SCRIPT)
relay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(relay)


def test_ssh_preserves_payload_as_one_argument():
    payload = {"url": "https://example.com/a?q=';$(touch /tmp/unwanted)&x=`id`"}
    cmd = relay.command({"transport": "ssh", "ssh_host": "worker", "mcporter_config": "/srv/private MCP.json"}, "firecrawl_scrape", payload, 1000)
    remote = shlex.split(cmd[-1])
    assert cmd[-2] == "worker"
    assert remote[:3] == ["mcporter", "--config", "/srv/private MCP.json"]
    assert remote[remote.index("call") + 1] == "firecrawl.firecrawl_scrape"
    assert json.loads(remote[remote.index("--args") + 1]) == payload


@pytest.mark.parametrize("host", ["-oProxyCommand=id", "worker;id", "worker user", ""])
def test_rejects_ssh_options_or_shell_text(tmp_path, host):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"transport": "ssh", "ssh_host": host, "mcporter_config": "/tmp/mcp.json"}))
    with pytest.raises(ValueError):
        relay.load_config(path)


def test_missing_config_never_launches_process(tmp_path, monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("must not contact a service without connection config")
    monkeypatch.setattr(relay.subprocess, "run", unexpected)
    assert relay.main(["list", "--config", str(tmp_path / "absent")]) == 2


def test_timeout_does_not_resubmit_crawl(tmp_path, monkeypatch, capsys):
    path = tmp_path / "config.json"
    path.write_text('{"transport":"local","mcporter_config":"/tmp/mcp.json"}')
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
    path.write_text('{"transport":"local","server":"nas-firecrawl","mcporter_config":"/tmp/mcp.json"}')
    def failure(cmd, **kwargs):
        assert cmd[:3] == ["mcporter", "--config", "/tmp/mcp.json"]
        assert cmd[cmd.index("call") + 1] == "nas-firecrawl.firecrawl_scrape"
        return subprocess.CompletedProcess(cmd, 7)
    monkeypatch.setattr(relay.subprocess, "run", failure)
    assert relay.main(["firecrawl_scrape", "--config", str(path)]) == 7


@pytest.mark.parametrize("path_value", [None, "", "relative/mcp.json", "~/mcp.json"])
def test_requires_explicit_absolute_mcporter_config(tmp_path, path_value):
    path = tmp_path / "relay.json"
    path.write_text(json.dumps({"transport": "local", "mcporter_config": path_value}))
    with pytest.raises(ValueError, match="mcporter_config"):
        relay.load_config(path)


@pytest.mark.skipif(not shutil.which("mcporter"), reason="mcporter integration tool is not installed")
def test_real_mcporter_ignores_project_override(tmp_path):
    """A project server must not override the configured NAS connection."""
    # The suite isolates HOME; resolve the existing Node runtime before using that HOME.
    node = subprocess.check_output(
        ["node", "-p", "process.execPath"], text=True,
        env={**os.environ, "HOME": REAL_HOME},
    ).strip()
    env = {**os.environ, "PATH": str(Path(node).parent) + os.pathsep + os.environ["PATH"]}
    stub = tmp_path / "server.py"
    stub.write_text('''import json, sys
for line in sys.stdin:
    msg = json.loads(line)
    if "id" not in msg:
        continue
    method = msg["method"]
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "fixture", "version": "1"}}
    elif method == "tools/list":
        result = {"tools": [{"name": "firecrawl_scrape", "description": "fixture", "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}}}]}
    else:
        result = {"content": [{"type": "text", "text": sys.argv[1]}]}
    print(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": result}), flush=True)
''')
    def config(marker):
        return json.dumps({"imports": [], "mcpServers": {"firecrawl": {"command": sys.executable, "args": [str(stub), marker]}}})
    pinned = tmp_path / "pinned.json"
    pinned.write_text(config("PINNED_NAS"))
    project = tmp_path / "project"
    (project / "config").mkdir(parents=True)
    (project / "config/mcporter.json").write_text(config("WRONG_PROJECT"))
    connection = tmp_path / "relay.json"
    connection.write_text(json.dumps({"transport": "local", "mcporter_config": str(pinned)}))
    for cwd in [tmp_path, project]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "firecrawl_scrape", "--config", str(connection),
             "--args", '{"url":"https://example.test"}', "--timeout", "10000"],
            cwd=cwd, env=env, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert "PINNED_NAS" in result.stdout
        assert "WRONG_PROJECT" not in result.stdout
