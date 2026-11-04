# -*- coding: utf-8 -*-
"""Google News — headlines and search through OpenCLI, no browser needed."""

from email.utils import parsedate_to_datetime

from agent_reach.backends.opencli import opencli_public_items

from .base import Action, Channel, Param

_NOTE = (
    "Links are news.google.com redirects that `agent-reach read` cannot open (403); "
    "to read an article, search its title with another tool"
)
_REGION = (
    Param("limit", "max results", required=False, type=int, default=10),
    Param("lang", "language code, e.g. en, zh", required=False, default="en"),
    Param("region", "region code, e.g. US, TW", required=False, default="US"),
)


class GoogleNewsChannel(Channel):
    name = "google-news"
    description = "Google News 新闻搜索与头条"

    level = "default"
    tools = ("opencli",)
    prereqs = ("node",)
    actions = (
        Action(
            "search",
            f"Search news. {_NOTE}",
            (Param("query", "what to search for"), *_REGION),
            (("opencli-public", "_search"),),
            live_test={"query": "Nvidia", "limit": 2},
        ),
        Action(
            "top",
            f"Top headlines. {_NOTE}",
            _REGION,
            (("opencli-public", "_top"),),
            live_test={"limit": 2},
        ),
    )

    def can_handle(self, url: str) -> bool:
        # Redirect links are unreadable, so leave them to the generic web reader.
        return False

    @staticmethod
    def _news(keyword, limit, lang, region, timeout):
        args = ["news", *([keyword] if keyword else []),
                "--limit", str(limit), "--lang", lang, "--region", region]
        items = opencli_public_items("google", args, timeout=timeout)
        for item in items:
            # Google's `source` is the publisher; surface it as the author.
            item["author"] = (item["raw"] or {}).get("source") or None
            try:  # RFC 822 -> ISO 8601 UTC; keep the original text if unparsable
                item["published_at"] = parsedate_to_datetime(item["published_at"]).strftime("%Y-%m-%dT%H:%M:%SZ")
            except (TypeError, ValueError):
                pass
        return items

    def _search(self, *, query: str, limit: int, lang: str, region: str, timeout: float) -> list:
        return self._news(query, limit, lang, region, timeout)

    def _top(self, *, limit: int, lang: str, region: str, timeout: float) -> list:
        return self._news(None, limit, lang, region, timeout)
