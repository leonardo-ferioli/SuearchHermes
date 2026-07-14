# Changelog

All notable changes to SuearchHermes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
