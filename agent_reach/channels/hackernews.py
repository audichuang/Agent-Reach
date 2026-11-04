# -*- coding: utf-8 -*-
"""Hacker News — search and story lists through OpenCLI, no browser needed."""

from agent_reach.backends.opencli import opencli_public_items
from agent_reach.runtime.result import BAD_INPUT, ReachError

from .base import Action, Channel, Param

_LIMIT = Param("limit", "max stories", required=False, type=int, default=10)
_LISTS = (("top", "Front-page stories"), ("new", "Newest stories"),
          ("best", "Best stories"), ("show", "Show HN posts"))


class HackerNewsChannel(Channel):
    name = "hackernews"
    description = "Hacker News 搜索与热门帖"

    level = "default"
    tools = ("opencli",)
    prereqs = ("node",)
    actions = (
        Action(
            "search",
            "Search stories. sort=relevance (default) ranks by match and points; "
            "sort=date is newest first and mostly returns low-score noise",
            (
                Param("query", "what to search for"),
                Param("limit", "max stories", required=False, type=int, default=10),
                Param("sort", "relevance or date", required=False, default="relevance"),
            ),
            (("opencli-public", "_search"),),
            live_test={"query": "rust", "limit": 2},
        ),
        *(Action(name, help_, (_LIMIT,), (("opencli-public", f"_{name}"),), live_test={"limit": 2})
          for name, help_ in _LISTS),
    )

    def can_handle(self, url: str) -> bool:
        return False  # item pages are plain web pages; use the generic reader

    def validate_params(self, action: str, params: dict) -> None:
        if action == "search" and params.get("sort", "relevance") not in {"relevance", "date"}:
            raise ReachError(BAD_INPUT, "sort must be relevance or date")

    def _search(self, *, query: str, limit: int, sort: str, timeout: float) -> list:
        return opencli_public_items(
            "hackernews", ["search", query, "--limit", str(limit), "--sort", sort], timeout=timeout)

    def _list(self, name: str, limit: int, timeout: float) -> list:
        return opencli_public_items("hackernews", [name, "--limit", str(limit)], timeout=timeout)

    def _top(self, *, limit: int, timeout: float) -> list:
        return self._list("top", limit, timeout)

    def _new(self, *, limit: int, timeout: float) -> list:
        return self._list("new", limit, timeout)

    def _best(self, *, limit: int, timeout: float) -> list:
        return self._list("best", limit, timeout)

    def _show(self, *, limit: int, timeout: float) -> list:
        return self._list("show", limit, timeout)
