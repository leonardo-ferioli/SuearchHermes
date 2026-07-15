# Changelog

All notable changes to SuearchHermes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-07-14

### Added
- Configurable prompt templates via `AGY_SEARCH_PROMPT` and `AGY_EXTRACT_PROMPT` env vars
- Response caching with 5-minute TTL — avoids repeated API calls within a session
- Rate limit awareness — checks `retrieveUserQuotaSummary` before search, surfaces reset time
- Both providers (binary and OAuth) support all three features

### Changed
- Updated roadmap — all planned features through v1.5.0 are now complete

## [1.1.0] - 2026-07-14

### Added
- `AgYOAuthWebSearchProvider` — direct Gemini API integration via OAuth
- No `agy` binary required — uses OAuth tokens directly with Google Gemini API
- OAuth flow: PKCE + authorization code + token refresh
- Token storage in `~/.config/antigravity/tokens.json`
- Automatic token refresh when expired
- New config option: `web.search_backend: agy-oauth`

### Changed
- Updated `__init__.py` to register both `agy` and `agy-oauth` providers
- Updated documentation with OAuth provider setup instructions
- Updated roadmap to mark v1.1.0 as completed

### Notes
- `agy-oauth` mode doesn't require Antigravity CLI binary
- Tokens are stored locally and refreshed automatically
- Same Google Search Grounding quality as `agy` mode

## [1.0.0] - 2026-07-14

### Added
- Initial release
- `AgYWebSearchProvider` — implements Hermes' `WebSearchProvider` ABC
- Calls `agy -p` with structured prompt for Google Search Grounding via Gemini
- Normalizes response to Hermes' `{"web": [{"title", "url", "description", "position"}]}` format
- One-command installer (`install.sh`)
- Automatic `config.yaml` wiring (`web.search_backend: agy`)
- Clean source domains (not `vertexaisearch` redirect URLs)
- 120-second timeout with graceful error handling
- Full documentation (README.md)
- MIT license

### Notes
- Requires [Hermes Agent](https://github.com/NousResearch/hermes-agent) with plugin system
- Requires [Antigravity CLI](https://github.com/google-antigravity/antigravity-cli) (`agy`) installed and authenticated
- No API key, no billing — uses existing `agy` OAuth session
