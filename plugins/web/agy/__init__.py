"""Google Search via Antigravity — plugin form.

Provides two backends:

1. **agy** (default) — calls the ``agy`` CLI binary. Requires ``agy``
   installed and authenticated.
2. **agy-oauth** — uses Antigravity OAuth tokens directly with the
   Google Gemini API. No binary required, only OAuth tokens.

Both use Google Search Grounding via Gemini — free, no API key.

Config keys::

    web:
      search_backend: "agy"        # use agy binary (default)
      search_backend: "agy-oauth"  # use OAuth directly
      backend: "agy"               # shared fallback
"""

from __future__ import annotations

from plugins.web.agy.provider import AgYWebSearchProvider
from plugins.web.agy.oauth_provider import AgYOAuthWebSearchProvider


def register(ctx) -> None:
    """Register both agy providers with the plugin context."""
    ctx.register_web_search_provider(AgYWebSearchProvider())
    ctx.register_web_search_provider(AgYOAuthWebSearchProvider())
