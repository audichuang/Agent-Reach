#!/usr/bin/env python3
"""Relay Firecrawl MCP calls through mcporter locally or over configured SSH."""

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

TOOLS = (
    "firecrawl_scrape",
    "firecrawl_map",
    "firecrawl_crawl",
    "firecrawl_check_crawl_status",
)


def load_config(path):
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("connection config must be a JSON object")
    if config.get("transport") not in ("local", "ssh"):
        raise ValueError("transport must be local or ssh")
    server = config.get("server", "firecrawl")
    if not isinstance(server, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_-]*", server):
        raise ValueError("server must be an MCP server name")
    if config["transport"] == "ssh":
        host = config.get("ssh_host", "")
        if not isinstance(host, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", host):
            raise ValueError("ssh_host must be an existing SSH alias, without options")
    return config


def command(config, tool, arguments, timeout_ms):
    server = config.get("server", "firecrawl")
    if tool == "list":
        cmd = ["mcporter", "list", server, "--schema"]
    else:
        cmd = ["mcporter", "call", f"{server}.{tool}", "--args", json.dumps(arguments)]
    cmd += ["--timeout", str(timeout_ms), "--no-oauth"]
    if config["transport"] == "ssh":
        # SSH passes its command through a remote shell: quote every argument once.
        return [
            "ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
            config["ssh_host"], shlex.join(cmd),
        ]
    return cmd


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=("list", *TOOLS))
    parser.add_argument("--args", default="{}", help="MCP tool arguments as a JSON object")
    parser.add_argument("--config", type=Path, default=Path.home() / ".agent-reach/firecrawl.json")
    parser.add_argument("--timeout", type=int, default=60000, help="MCP timeout in milliseconds")
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        payload = json.loads(args.args)
        if not isinstance(payload, dict):
            raise ValueError("--args must be a JSON object")
        config = load_config(args.config.expanduser())
    except FileNotFoundError:
        print(
            f"Firecrawl connection config missing: {args.config}. "
            "See the skill's references/web.md; no request was sent.", file=sys.stderr,
        )
        return 2
    except (OSError, ValueError) as exc:
        print(f"Invalid Firecrawl configuration or arguments: {exc}", file=sys.stderr)
        return 2
    try:
        # Inherit output so a crawl ID remains visible even if a later wait times out.
        result = subprocess.run(
            command(config, args.tool, payload, args.timeout),
            stdin=subprocess.DEVNULL, timeout=args.timeout / 1000 + 15, check=False,
        )
        return result.returncode
    except FileNotFoundError:
        print("Required executable missing: install/configure mcporter or SSH on this host.", file=sys.stderr)
        return 127
    except subprocess.TimeoutExpired:
        print(
            "Firecrawl relay timed out; no retry was made. A crawl may still be running. "
            "Use its returned ID to check status; without an ID, report the outcome as unknown.",
            file=sys.stderr,
        )
        return 124


if __name__ == "__main__":
    sys.exit(main())
