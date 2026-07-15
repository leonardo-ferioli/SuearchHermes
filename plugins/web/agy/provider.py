"""Google Search via Antigravity CLI (agy) — provider.

Subclasses :class:`agent.web_search_provider.WebSearchProvider`.
Calls ``agy -p`` under the hood with a prompt engineered to return a
concise answer and source domains. Results are normalized into the
``{"web": [{"title", "url", "description", "position"}]}`` shape that
Hermes' ``web_search`` tool expects.

No API key required. The user must have ``agy`` installed and authenticated
(``~/.local/bin/agy``).
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from typing import Any, Dict, List

from agent.web_search_provider import WebSearchProvider

logger = logging.getLogger(__name__)

_AGY_TIMEOUT_SECS = 120

# v1.3.0 — Configurable prompt templates (overridable via env vars)
_DEFAULT_SEARCH_PROMPT = (
    'Search the web for: "{query}"\n\n'
    "Respond in this exact format and nothing else:\n\n"
    "ANSWER: <one or two sentences answering the question, in English>\n"
    "SOURCES: <comma-separated list of source domain names or clean URLs, "
    "not vertexaisearch redirect links>"
)
_DEFAULT_EXTRACT_PROMPT = (
    "Extract the main text content from this URL: {url}\n\n"
    "Return ONLY the main article/text content. No HTML, no navigation, "
    "no ads, no menus. Just the readable text content."
)

# v1.4.0 — Response caching
_CACHE: Dict[str, Any] = {}
_CACHE_TTL_SECS = 300  # 5 minutes


def _find_agy() -> str | None:
    """Locate the agy binary."""
    candidates = [
        os.path.expanduser("~/.local/bin/agy"),
        shutil.which("agy"),
    ]
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


class AgYWebSearchProvider(WebSearchProvider):
    """Google Search provider via Antigravity CLI (agy).

    Free, no API key. Uses agy's built-in Google Search Grounding via Gemini.
    Returns synthesized answers with source domains — not raw SERP links.
    """

    @property
    def name(self) -> str:
        return "agy"

    @property
    def display_name(self) -> str:
        return "Google via Antigravity (agy)"

    def is_available(self) -> bool:
        """Return True when agy binary exists and is executable."""
        return _find_agy() is not None

    def supports_search(self) -> bool:
        return True

    def supports_extract(self) -> bool:
        return True

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Execute a Google search via agy and return normalized results."""
        # v1.4.0 — Check cache first
        cache_key = f"search:{query}"
        cached = _CACHE.get(cache_key)
        if cached and time.time() - cached["ts"] < _CACHE_TTL_SECS:
            logger.info("agy search '%s': cache hit", query)
            return cached["data"]

        agy_path = _find_agy()
        if not agy_path:
            return {
                "success": False,
                "error": "agy binary not found — install with: curl -fsSL https://antigravity.google/cli/install.sh | bash",
            }

        # v1.3.0 — Use configurable prompt template
        template = os.environ.get("AGY_SEARCH_PROMPT", _DEFAULT_SEARCH_PROMPT)
        prompt = template.replace("{query}", query)

        try:
            result = subprocess.run(
                [agy_path, "-p", prompt, "--dangerously-skip-permissions"],
                capture_output=True,
                text=True,
                timeout=_AGY_TIMEOUT_SECS,
                env={**os.environ, "PATH": os.path.expanduser("~/.local/bin") + ":" + os.environ.get("PATH", "")},
            )
        except subprocess.TimeoutExpired:
            logger.warning("agy search timed out after %ds for query: %r", _AGY_TIMEOUT_SECS, query)
            return {
                "success": False,
                "error": f"agy search timed out after {_AGY_TIMEOUT_SECS}s",
            }
        except Exception as exc:
            logger.warning("agy search error: %s", exc)
            return {"success": False, "error": f"agy search failed: {exc}"}

        raw = (result.stdout or "").strip()
        if not raw:
            stderr = (result.stderr or "").strip()
            return {"success": False, "error": f"agy returned empty output. stderr: {stderr[:300]}"}

        answer_match = raw.split("ANSWER:", 1)
        answer = answer_match[1].split("SOURCES:", 1)[0].strip() if len(answer_match) > 1 else raw

        sources: list[str] = []
        if "SOURCES:" in raw:
            sources_raw = raw.split("SOURCES:", 1)[1].strip()
            sources = [s.strip().strip(",") for s in sources_raw.split(",") if s.strip()]

        web_results = []
        if answer:
            web_results.append({
                "title": answer[:200],
                "url": sources[0] if sources else "https://www.google.com/search?q=" + query.replace(" ", "+"),
                "description": answer,
                "position": 1,
            })
        for i, src in enumerate(sources[:max(0, limit - 1)]):
            clean = src if src.startswith("http") else f"https://{src}"
            web_results.append({
                "title": src,
                "url": clean,
                "description": "",
                "position": i + 2,
            })

        logger.info("agy search '%s': %d results", query, len(web_results))
        result = {"success": True, "data": {"web": web_results}}
        # v1.4.0 — Cache the result
        _CACHE[cache_key] = {"ts": time.time(), "data": result}
        return result

    def extract(self, urls: list[str], **kwargs: Any) -> list[Dict[str, Any]]:
        """Extract content from one or more URLs via agy."""
        agy_path = _find_agy()
        if not agy_path:
            return [{"url": u, "title": "", "content": "", "error": "agy binary not found"} for u in urls]

        results = []
        for url in urls:
            # v1.4.0 — Check cache first
            cache_key = f"extract:{url}"
            cached = _CACHE.get(cache_key)
            if cached and time.time() - cached["ts"] < _CACHE_TTL_SECS:
                logger.info("agy extract '%s': cache hit", url)
                results.append(cached["data"])
                continue

            # v1.3.0 — Use configurable prompt template
            template = os.environ.get("AGY_EXTRACT_PROMPT", _DEFAULT_EXTRACT_PROMPT)
            prompt = template.replace("{url}", url)
            try:
                result = subprocess.run(
                    [agy_path, "-p", prompt, "--dangerously-skip-permissions"],
                    capture_output=True,
                    text=True,
                    timeout=_AGY_TIMEOUT_SECS,
                    env={**os.environ, "PATH": os.path.expanduser("~/.local/bin") + ":" + os.environ.get("PATH", "")},
                )
                content = (result.stdout or "").strip()
                if content:
                    result = {
                        "url": url,
                        "title": "",
                        "content": content,
                        "raw_content": content,
                        "metadata": {"sourceURL": url},
                    }
                    # v1.4.0 — Cache the result
                    _CACHE[cache_key] = {"ts": time.time(), "data": result}
                    results.append(result)
                else:
                    results.append({"url": url, "title": "", "content": "", "error": "Empty response from agy"})
            except subprocess.TimeoutExpired:
                results.append({"url": url, "title": "", "content": "", "error": f"agy timed out after {_AGY_TIMEOUT_SECS}s"})
            except Exception as exc:
                results.append({"url": url, "title": "", "content": "", "error": str(exc)})

        return results

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "Google via Antigravity (agy)",
            "badge": "free · no key · google grounding",
            "tag": "Search Google via agy CLI with Gemini Search Grounding — free, no API key, synthesized answers with sources",
            "env_vars": [],
        }
