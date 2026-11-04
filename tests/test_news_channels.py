# -*- coding: utf-8 -*-
"""google-news and hackernews: no-browser OpenCLI channels (backend `opencli-public`)."""

from unittest.mock import Mock

import pytest

from agent_reach.backends import opencli as backend
from agent_reach.channels import get_channel
from agent_reach.channels.google_news import GoogleNewsChannel
from agent_reach.channels.hackernews import HackerNewsChannel
from agent_reach.runtime import dispatch
from agent_reach.runtime.dispatch import run_action

GN_ROWS = {"ok": True, "data": [{"title": "T", "source": "Reuters",
                                 "date": "Wed, 04 Nov 2026 14:56:24 GMT", "url": "https://news.google.com/rss/articles/x"}]}
HN_ROWS = {"ok": True, "data": [{"rank": 1, "id": 7, "title": "Rust", "score": 9, "author": "pg",
                                 "comments": 2, "url": "https://example.com"}]}


@pytest.fixture
def run(monkeypatch):
    """Mock the subprocess layer; fail loudly if the browser path is touched."""
    from agent_reach.runtime import browser, browser_binding, run as run_mod
    cmd = Mock(return_value="")
    monkeypatch.setattr(run_mod, "run_cmd", cmd)
    for mod, name in ((browser_binding, "environment"), (browser, "save_session"),
                      (dispatch, "query_slot"), (dispatch, "_pace_browser")):
        monkeypatch.setattr(mod, name, Mock(side_effect=AssertionError(f"browser path touched: {name}")))
    return cmd


def _go(run, channel, action, rows, **params):
    import json
    run.return_value = json.dumps(rows)
    return run_action(channel, action, params)


def test_registered_default_and_toolless_of_browser():
    for name in ("google-news", "hackernews"):
        ch = get_channel(name)
        assert ch.level == "default" and not ch.login_url and ch.tools == ("opencli",)
        assert all(b[0] == "opencli-public" for a in ch.actions for b in a.backends)


def test_google_news_search_maps_source_to_author(run):
    res = _go(run, GoogleNewsChannel(), "search", GN_ROWS, query="Nvidia", limit=3, lang="zh", region="TW")
    assert res["ok"] and res["backend"] == "opencli-public"
    assert res["items"][0]["author"] == "Reuters"
    assert res["items"][0]["published_at"] == "2026-11-04T14:56:24Z"
    assert run.call_args.args[0] == ["opencli", "google", "news", "Nvidia", "--limit", "3",
                                     "--lang", "zh", "--region", "TW", "-f", "json"]
    assert run.call_args.kwargs.get("env") is None


def test_google_news_top_omits_keyword(run):
    res = _go(run, GoogleNewsChannel(), "top", GN_ROWS)
    assert res["ok"]
    assert run.call_args.args[0][:4] == ["opencli", "google", "news", "--limit"]


def test_hackernews_search_passes_sort(run):
    res = _go(run, HackerNewsChannel(), "search", HN_ROWS, query="rust", sort="date")
    assert res["ok"] and res["items"][0]["title"] == "Rust"
    assert run.call_args.args[0] == ["opencli", "hackernews", "search", "rust", "--limit", "10",
                                     "--sort", "date", "-f", "json"]


def test_hackernews_search_defaults_to_relevance(run):
    _go(run, HackerNewsChannel(), "search", HN_ROWS, query="rust")
    assert "relevance" in run.call_args.args[0]


def test_hackernews_rejects_bad_sort(run):
    res = _go(run, HackerNewsChannel(), "search", HN_ROWS, query="rust", sort="hot")
    assert res["error"]["code"] == "BAD_INPUT" and not run.called


@pytest.mark.parametrize("name", ["top", "new", "best", "show"])
def test_hackernews_lists(run, name):
    res = _go(run, HackerNewsChannel(), name, HN_ROWS, limit=4)
    assert res["ok"]
    assert run.call_args.args[0] == ["opencli", "hackernews", name, "--limit", "4", "-f", "json"]


def test_empty_result_is_not_found(run):
    res = _go(run, HackerNewsChannel(), "top", {"ok": True, "data": []})
    assert res["error"]["code"] == "NOT_FOUND"


def test_upstream_not_found_error_is_not_found_and_does_not_pause(run):
    import json
    from agent_reach.runtime.run import CommandFailed
    payload = json.dumps({"ok": False, "error": {"code": "NOT_FOUND", "message": "No news articles found"}})
    run.side_effect = CommandFailed("UPSTREAM_BROKEN", "exit 1", stdout=payload)
    res = run_action(GoogleNewsChannel(), "search", {"query": "zzqx"})
    assert res["error"]["code"] == "NOT_FOUND"
    run.side_effect = None
    res = _go(run, GoogleNewsChannel(), "search", GN_ROWS, query="Nvidia")
    assert res["ok"] is True


def test_upstream_error_passes_through(run):
    res = _go(run, HackerNewsChannel(), "top", {"ok": False, "error": {"code": "X", "message": "boom"}})
    assert res["error"]["message"] == "boom"


def test_browser_backends_still_use_browser_path(monkeypatch):
    """opencli_call keeps binding and saving the session."""
    seen = []
    from agent_reach.runtime import browser, browser_binding
    monkeypatch.setattr(browser_binding, "environment", lambda site: seen.append("env") or {})
    monkeypatch.setattr(browser, "save_session", lambda: seen.append("save"))
    monkeypatch.setattr(backend, "_run_opencli", lambda *a, **k: {"ok": True, "data": []})
    backend.opencli_call("x", [], timeout=1)
    assert seen == ["env", "save"]
