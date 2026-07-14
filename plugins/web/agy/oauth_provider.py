"""Google Search via Antigravity OAuth — provider.

Subclasses :class:`agent.web_search_provider.WebSearchProvider`.
Uses the Antigravity OAuth flow directly to obtain tokens and call the
Google Gemini API with Search Grounding. Results are normalized into the
``{"web": [{"title", "url", "description", "position"}]}`` shape that
Hermes' ``web_search`` tool expects.

No API key required. The user authenticates via Google OAuth once, and
tokens are stored in ``~/.config/antigravity/tokens.json``.
"""

from __future__ import annotations

import hashlib
import base64
import secrets
import urllib.parse
import http.client
import json
import logging
import os
import ssl
import time
from typing import Any, Dict

from agent.web_search_provider import WebSearchProvider

logger = logging.getLogger(__name__)

# OAuth2 configuration — extracted from Antigravity CLI (agy)
_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
_CLIENT_SECRET = "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"
_REDIRECT_URI = "https://antigravity.google/oauth-callback"
_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/auth"
_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/cclog",
    "https://www.googleapis.com/auth/experimentsandconfigs",
    "openid",
]

_TOKEN_FILE = os.path.expanduser("~/.config/antigravity/tokens.json")
_TIMEOUT_SECS = 30


def _generate_pkce() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge (S256)."""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("ascii")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


def _build_auth_url(code_challenge: str, state: str) -> str:
    """Build the Google OAuth authorization URL."""
    params = {
        "access_type": "offline",
        "client_id": _CLIENT_ID,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "prompt": "consent",
        "redirect_uri": _REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(_SCOPES),
        "state": state,
    }
    return f"{_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"


def _exchange_code(code: str, code_verifier: str) -> Dict[str, Any]:
    """Exchange authorization code for tokens."""
    data = {
        "client_id": _CLIENT_ID,
        "client_secret": _CLIENT_SECRET,
        "code": code,
        "code_verifier": code_verifier,
        "grant_type": "authorization_code",
        "redirect_uri": _REDIRECT_URI,
    }

    parsed = urllib.parse.urlparse(_TOKEN_ENDPOINT)
    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection(parsed.hostname, context=context, timeout=_TIMEOUT_SECS)

    body = urllib.parse.urlencode(data)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    conn.request("POST", parsed.path, body=body, headers=headers)
    response = conn.getresponse()
    response_body = response.read().decode("utf-8")

    if response.status != 200:
        raise Exception(f"Token exchange failed: {response.status} - {response_body}")

    return json.loads(response_body)


def _refresh_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh an expired access token."""
    data = {
        "client_id": _CLIENT_ID,
        "client_secret": _CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    parsed = urllib.parse.urlparse(_TOKEN_ENDPOINT)
    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection(parsed.hostname, context=context, timeout=_TIMEOUT_SECS)

    body = urllib.parse.urlencode(data)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    conn.request("POST", parsed.path, body=body, headers=headers)
    response = conn.getresponse()
    response_body = response.read().decode("utf-8")

    if response.status != 200:
        raise Exception(f"Token refresh failed: {response.status} - {response_body}")

    return json.loads(response_body)


def _load_tokens() -> Dict[str, Any] | None:
    """Load stored tokens from disk."""
    try:
        if os.path.exists(_TOKEN_FILE):
            with open(_TOKEN_FILE, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load tokens: %s", exc)
    return None


def _save_tokens(tokens: Dict[str, Any]) -> None:
    """Save tokens to disk."""
    try:
        os.makedirs(os.path.dirname(_TOKEN_FILE), exist_ok=True)
        tokens["stored_at"] = int(time.time())
        with open(_TOKEN_FILE, "w") as f:
            json.dump(tokens, f, indent=2)
    except OSError as exc:
        logger.warning("Failed to save tokens: %s", exc)


def _get_valid_access_token() -> str | None:
    """Get a valid access token, refreshing if necessary."""
    tokens = _load_tokens()
    if not tokens:
        return None

    access_token = tokens.get("access_token")
    refresh_token_val = tokens.get("refresh_token")
    stored_at = tokens.get("stored_at", 0)
    expires_in = tokens.get("expires_in", 3600)

    # Check if token is expired (with 5-minute buffer)
    if time.time() > stored_at + expires_in - 300:
        if refresh_token_val:
            try:
                new_tokens = _refresh_token(refresh_token_val)
                _save_tokens(new_tokens)
                return new_tokens.get("access_token")
            except Exception as exc:
                logger.warning("Token refresh failed: %s", exc)
                return None
        return None

    return access_token


class AgYOAuthWebSearchProvider(WebSearchProvider):
    """Google Search provider via Antigravity OAuth.

    Free, no API key. Uses OAuth tokens directly with Google Gemini API
    Search Grounding. Returns synthesized answers with source domains.
    """

    @property
    def name(self) -> str:
        return "agy-oauth"

    @property
    def display_name(self) -> str:
        return "Google via Antigravity OAuth"

    def is_available(self) -> bool:
        """Return True when valid OAuth tokens exist."""
        return _get_valid_access_token() is not None

    def supports_search(self) -> bool:
        return True

    def supports_extract(self) -> bool:
        return False

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Execute a Google search via Gemini API with Search Grounding."""
        access_token = _get_valid_access_token()
        if not access_token:
            return {
                "success": False,
                "error": "Not authenticated. Run: python3 -c 'from plugins.web.agy.oauth_provider import *; print(_build_auth_url(*_generate_pkce()))'",
            }

        # Call Gemini API with Search Grounding
        try:
            result = self._call_gemini_search(query, access_token)
            return result
        except Exception as exc:
            logger.warning("OAuth search error: %s", exc)
            return {"success": False, "error": f"Search failed: {exc}"}

    def _call_gemini_search(self, query: str, access_token: str) -> Dict[str, Any]:
        """Call Gemini API with Search Grounding."""
        # Use the daily-cloudcode-pa endpoint (same as agy)
        endpoint = "daily-cloudcode-pa.googleapis.com"
        path = "/v1internal:streamGenerateContent?alt=sse"

        # Build the request body
        body = json.dumps({
            "project": "default-cli-project",
            "model": "gemini-3.5-flash",
            "request": {
                "contents": [{"role": "user", "parts": [{"text": f'Search the web for: "{query}"'}]}],
                "tools": [{"googleSearch": {}}],
            },
        })

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "google-cloud-sdk vscode_cloudshelleditor/0.1",
        }

        context = ssl.create_default_context()
        conn = http.client.HTTPSConnection(endpoint, context=context, timeout=_TIMEOUT_SECS)
        conn.request("POST", path, body=body, headers=headers)

        response = conn.getresponse()
        response_body = response.read().decode("utf-8")

        if response.status != 200:
            raise Exception(f"Gemini API error: {response.status} - {response_body[:300]}")

        # Parse SSE response
        return self._parse_sse_response(response_body, query)

    def _parse_sse_response(self, raw: str, query: str) -> Dict[str, Any]:
        """Parse SSE response from Gemini API."""
        # Extract text from SSE events
        text_parts = []
        for line in raw.split("\n"):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if "candidates" in data:
                        for candidate in data["candidates"]:
                            if "content" in candidate:
                                for part in candidate["content"].get("parts", []):
                                    if "text" in part:
                                        text_parts.append(part["text"])
                except json.JSONDecodeError:
                    continue

        answer = " ".join(text_parts).strip()
        if not answer:
            return {"success": False, "error": "No response from Gemini API"}

        # Extract sources from grounding metadata
        sources = []
        for line in raw.split("\n"):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if "candidates" in data:
                        for candidate in data["candidates"]:
                            metadata = candidate.get("groundingMetadata", {})
                            if "groundingChunks" in metadata:
                                for chunk in metadata["groundingChunks"]:
                                    if "web" in chunk:
                                        sources.append(chunk["web"].get("uri", ""))
                except json.JSONDecodeError:
                    continue

        web_results = []
        if answer:
            web_results.append({
                "title": answer[:200],
                "url": sources[0] if sources else f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "description": answer,
                "position": 1,
            })

        for i, src in enumerate(sources[:max(0, limit - 1)]):
            if src:
                web_results.append({
                    "title": src.split("/")[-1] if "/" in src else src,
                    "url": src,
                    "description": "",
                    "position": i + 2,
                })

        logger.info("OAuth search '%s': %d results", query, len(web_results))
        return {"success": True, "data": {"web": web_results}}

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "Google via Antigravity OAuth",
            "badge": "free · no key · google grounding · OAuth",
            "tag": "Search Google via Antigravity OAuth with Gemini Search Grounding — free, no API key, direct API access",
            "env_vars": [],
        }


def get_auth_url() -> str:
    """Get the OAuth authorization URL for manual login."""
    code_verifier, code_challenge = _generate_pkce()
    state = secrets.token_urlsafe(16)
    return _build_auth_url(code_challenge, state), code_verifier, state


def complete_login(code: str, code_verifier: str) -> bool:
    """Complete the OAuth login with the authorization code."""
    try:
        tokens = _exchange_code(code, code_verifier)
        _save_tokens(tokens)
        return True
    except Exception as exc:
        logger.warning("Login failed: %s", exc)
        return False
