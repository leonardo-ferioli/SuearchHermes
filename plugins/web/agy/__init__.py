"""Google Search via Antigravity CLI (agy) — plugin form.

Uses the agy CLI's built-in Google Search Grounding (via Gemini) to perform
web searches. No API key, no billing — uses the user's existing agy OAuth
session. Returns synthesized answers with source domains.

Config keys::

    web:
      search_backend: "agy"
      backend: "agy"
"""

from __future__ import annotations

from plugins.web.agy.provider import AgYWebSearchProvider


def register(ctx) -> None:
    """Register the agy provider with the plugin context."""
    ctx.register_web_search_provider(AgYWebSearchProvider())
