"""Google Search via Antigravity OAuth — provider.

Subclasses :class:`agent.web_search_provider.WebSearchProvider`.
Uses the Antigravity OAuth flow directly to obtain tokens and call the
Google Gemini API with Search Grounding. Results are normalized into the
``{"web": [{"title", "url", "description", "position"}]}`` shape that
Hermes' ``web_search`` tool expects.

No API key required. The user authenticates via Google OAuth once, and
tokens are stored in ``~/.config/antigravity/tokens.json``.

Communication reverse-engineered from Antigravity CLI (agy) v1.1.2 via
mitmproxy traffic interception. The exact headers, body format, and
API call sequence match what agy sends to ``daily-cloudcode-pa.googleapis.com``.
"""

from __future__ import annotations

import gzip
import hashlib
import base64
import secrets
import urllib.parse
import http.client
import json
import logging
import os
import platform
import ssl
import time
import uuid
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

# API endpoint — same as agy
_API_ENDPOINT = "daily-cloudcode-pa.googleapis.com"

# User-Agent — exact string agy sends (captured via mitmproxy)
_ARCH = "amd64" if platform.machine() in ("x86_64", "AMD64") else platform.machine()
_USER_AGENT = f"antigravity/cli/1.1.2 (aidev_client; os_type=linux; arch={_ARCH}; auth_method=consumer)"

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


# ---------------------------------------------------------------------------
# API communication — exact replication of agy's HTTP calls
# ---------------------------------------------------------------------------

_PROJECT_CACHE: Dict[str, Any] = {}


def _api_headers(access_token: str) -> Dict[str, str]:
    """Build the exact headers agy sends to the API."""
    return {
        "Host": _API_ENDPOINT,
        "User-Agent": _USER_AGENT,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
    }


def _load_code_assist(access_token: str) -> str:
    """Call loadCodeAssist to get the real Cloud AI Companion project ID.

    agy sends ``{"metadata":{"ideType":"ANTIGRAVITY"}}`` — NOT
    ``{"cloudaicompanionProject":"default-cli-project"}``. The response
    contains the auto-assigned project for the free-tier OAuth user.
    """
    if "project" in _PROJECT_CACHE:
        return _PROJECT_CACHE["project"]

    headers = _api_headers(access_token)
    body = json.dumps({"metadata": {"ideType": "ANTIGRAVITY"}})

    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection(_API_ENDPOINT, context=context, timeout=_TIMEOUT_SECS)
    conn.request("POST", "/v1internal:loadCodeAssist", body=body, headers=headers)
    response = conn.getresponse()
    raw_data = response.read()

    content_encoding = response.getheader("Content-Encoding", "")
    if "gzip" in content_encoding:
        raw_data = gzip.decompress(raw_data)

    response_body = raw_data.decode("utf-8")

    if response.status != 200:
        raise Exception(f"loadCodeAssist failed: {response.status} - {response_body[:200]}")

    data = json.loads(response_body)
    project = data.get("cloudaicompanionProject", "")
    if not project:
        raise Exception("loadCodeAssist did not return a cloudaicompanionProject")

    _PROJECT_CACHE["project"] = project
    logger.info("loadCodeAssist returned project: %s", project)
    return project


def _stream_generate_content(
    access_token: str,
    project: str,
    prompt: str,
    *,
    model: str = "gemini-3.5-flash-low",
    tools: list | None = None,
) -> str:
    """Call streamGenerateContent and return the full text response.

    Replicates the exact body format agy sends, including requestId,
    userAgent, requestType, generationConfig, and sessionId fields.
    """
    headers = _api_headers(access_token)

    session_id = str(uuid.uuid4())

    request_body: Dict[str, Any] = {
        "project": project,
        "requestId": f"agent/{uuid.uuid4()}/{int(time.time() * 1000)}/{uuid.uuid4()}/1",
        "request": {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 65536,
                "thinkingConfig": {
                    "includeThoughts": True,
                    "thinkingBudget": 4000,
                },
            },
            "sessionId": session_id,
        },
        "model": model,
        "userAgent": "antigravity",
        "requestType": "agent",
    }

    if tools:
        request_body["request"]["tools"] = tools
        request_body["request"]["toolConfig"] = {}

    body = json.dumps(request_body)

    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection(_API_ENDPOINT, context=context, timeout=_TIMEOUT_SECS)
    conn.request("POST", "/v1internal:streamGenerateContent?alt=sse", body=body, headers=headers)

    response = conn.getresponse()
    raw_data = response.read()

    # agy sends Accept-Encoding: gzip, so the response may be compressed
    content_encoding = response.getheader("Content-Encoding", "")
    if "gzip" in content_encoding:
        raw_data = gzip.decompress(raw_data)

    response_body = raw_data.decode("utf-8")

    if response.status != 200:
        raise Exception(f"streamGenerateContent failed: {response.status} - {response_body[:300]}")

    # Parse SSE response — agy wraps responses in a "response" key
    text_parts = []
    for line in response_body.split("\n"):
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                # agy responses have a "response" wrapper
                resp = data.get("response", data)
                if "candidates" in resp:
                    for candidate in resp["candidates"]:
                        if "content" in candidate:
                            for part in candidate["content"].get("parts", []):
                                if "text" in part:
                                    text_parts.append(part["text"])
            except json.JSONDecodeError:
                continue

    return " ".join(text_parts).strip()


def _extract_grounding_sources(raw_response: str) -> list[str]:
    """Extract source URLs from grounding metadata in SSE response."""
    sources = []
    for line in raw_response.split("\n"):
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                resp = data.get("response", data)
                if "candidates" in resp:
                    for candidate in resp["candidates"]:
                        metadata = candidate.get("groundingMetadata", {})
                        if "groundingChunks" in metadata:
                            for chunk in metadata["groundingChunks"]:
                                if "web" in chunk:
                                    uri = chunk["web"].get("uri", "")
                                    if uri:
                                        sources.append(uri)
            except json.JSONDecodeError:
                continue
    return sources


class AgYOAuthWebSearchProvider(WebSearchProvider):
    """Google Search provider via Antigravity OAuth.

    Free, no API key. Uses OAuth tokens directly with Google Gemini API
    Search Grounding. Returns synthesized answers with source domains.

    Communication is reverse-engineered from agy v1.1.2 — exact same
    headers, body format, and API call sequence.
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
        return True

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Execute a Google search via Gemini API with Search Grounding."""
        access_token = _get_valid_access_token()
        if not access_token:
            return {
                "success": False,
                "error": "Not authenticated. Run: python3 -c 'from plugins.web.agy.oauth_provider import get_auth_url; url, _, _ = get_auth_url(); print(url)'",
            }

        try:
            project = _load_code_assist(access_token)
            prompt = f'Search the web for: "{query}"'
            answer = _stream_generate_content(
                access_token,
                project,
                prompt,
                tools=[{"googleSearch": {}}],
            )

            if not answer:
                return {"success": False, "error": "No response from Gemini API"}

            web_results = [{
                "title": answer[:200],
                "url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "description": answer,
                "position": 1,
            }]

            logger.info("OAuth search '%s': %d results", query, len(web_results))
            return {"success": True, "data": {"web": web_results}}

        except Exception as exc:
            logger.warning("OAuth search error: %s", exc)
            return {"success": False, "error": f"Search failed: {exc}"}

    def extract(self, urls: list[str], **kwargs: Any) -> list[Dict[str, Any]]:
        """Extract content from one or more URLs via Gemini API."""
        access_token = _get_valid_access_token()
        if not access_token:
            return [{"url": u, "title": "", "content": "", "error": "Not authenticated"} for u in urls]

        results = []
        for url in urls:
            try:
                project = _load_code_assist(access_token)
                prompt = (
                    f'Extract the main text content from this URL: {url}\n\n'
                    "Return ONLY the main article/text content. No HTML, no navigation, "
                    "no ads, no menus. Just the readable text content."
                )
                content = _stream_generate_content(access_token, project, prompt)
                results.append({
                    "url": url,
                    "title": "",
                    "content": content,
                    "raw_content": content,
                    "metadata": {"sourceURL": url},
                })
            except Exception as exc:
                logger.warning("OAuth extract error for %s: %s", url, exc)
                results.append({"url": url, "title": "", "content": "", "error": str(exc)})
        return results

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
