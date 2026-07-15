**English** | [Español](./README_es.md) | [中文](./README_zh.md)

<div align="center">

<img src="assets/banner.svg" alt="SuearchHermes" width="720"/>

# SuearchHermes

**Free Google Search for Hermes Agent — No API Key, No Billing, Real Google Results**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Hermes](https://img.shields.io/badge/Hermes-Agent-6E40C9?style=flat&logo=gnometerminal&logoColor=white)](https://github.com/NousResearch/hermes-agent)
[![agy](https://img.shields.io/badge/Antigravity%20CLI-agy-4285F4?style=flat&logo=google&logoColor=white)](https://github.com/google-antigravity/antigravity-cli)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](./LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-blue?style=flat&logo=linux&logoColor=white)]()
[![Price](https://img.shields.io/badge/Cost-Free%20%E2%80%A2%20No%20API%20Key-brightgreen?style=flat)]()
[![Release](https://img.shields.io/badge/Release-v1.0.0-blue?style=flat)](https://github.com/leonardo-ferioli/SuearchHermes/releases/tag/v1.0.0)
[![CI](https://github.com/leonardo-ferioli/SuearchHermes/actions/workflows/ci.yml/badge.svg)](https://github.com/leonardo-ferioli/SuearchHermes/actions)
[![GitHub stars](https://img.shields.io/github/stars/leonardo-ferioli/SuearchHermes?style=flat&color=yellow)](https://github.com/leonardo-ferioli/SuearchHermes/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/leonardo-ferioli/SuearchHermes?style=flat&color=red)](https://github.com/leonardo-ferioli/SuearchHermes/issues)
[![Last commit](https://img.shields.io/github/last-commit/leonardo-ferioli/SuearchHermes?style=flat&color=orange)](https://github.com/leonardo-ferioli/SuearchHermes/commits)

[Features](#-key-features) · [Why](#-why) · [Demo](#-demo) · [Quick Start](#-quick-start) · [Examples](#-examples) · [Architecture](#-architecture) · [Roadmap](#-roadmap) · [Contributing](#-contributing) · [Changelog](./CHANGELOG.md)

</div>

---

## 📰 News

- **2026-07-14** 🚀 **v1.0.0 released**: Initial public release. Google Search via Antigravity CLI (agy) plugin for Hermes Agent. Free, no API key, Google Search Grounding via Gemini. Includes one-command installer, full Hermes `WebSearchProvider` ABC implementation, and automatic config wiring. ([Release notes](https://github.com/leonardo-ferioli/SuearchHermes/releases/tag/v1.0.0))

<details>
<summary><b>Earlier news</b></summary>

- **2026-07-14** 🎉 **Project created**: SuearchHermes born from the frustration of Hermes' built-in web search backends being either paid (Tavily, Firecrawl, Exa) or low quality (DuckDuckGo). Decided to use Google's own Antigravity CLI as the backend.

</details>

---

## 🎯 Why?

Hermes Agent ships with `web_search` support, but the built-in backends all have problems:

| Backend | Cost | API Key | Quality | Problem |
|---|---|---|---|---|
| **Firecrawl** | 💰 Paid | Required | ⭐⭐⭐⭐ | Billing per request |
| **Tavily** | 💰 Paid | Required | ⭐⭐⭐⭐ | Limited free tier |
| **Exa** | 💰 Paid | Required | ⭐⭐⭐ | API key required |
| **Parallel** | 💰 Paid | Required | ⭐⭐⭐ | API key required |
| **Brave (free)** | ⚠️ Limited | Required | ⭐⭐⭐ | 2,000 queries/month |
| **DDGS** | ✅ Free | None | ⭐ | Poor quality, rate-limited, blocked |
| **SuearchHermes** | ✅ Free | **None** | ⭐⭐⭐⭐⭐ | **Uses Google via Gemini** |

**SuearchHermes** replaces all of that with `agy` — Google's own Antigravity CLI — which has **Google Search Grounding** built in via Gemini.

| | SuearchHermes |
|---|---|
| **Cost** | Free, forever |
| **API key** | None — uses your Google account OAuth |
| **Search engine** | Google (via Gemini Search Grounding) |
| **Result quality** | Synthesized answers + cited source domains |
| **Rate limit** | Subject to agy/Gemini fair use |
| **Setup time** | 30 seconds |

---

## ✨ Key Features

### 🔍 Real Google Search

Not scraping. Not a SERP API. Actual Google Search Grounding via Gemini — the same grounding API that powers Gemini's own "search the web" capability. Gemini reads the results, synthesizes a concise answer, and returns source domains.

### 🆓 Zero Cost, Zero API Keys

Uses your existing `agy` OAuth session — the one you already created when you ran `agy` and logged in with your Google account. No `BRAVE_SEARCH_API_KEY`, no `TAVILY_API_KEY`, no `FIRECRAWL_API_KEY`, no credit card, no Cloud Console.

### 🔌 Drop-in Hermes Plugin

Implements Hermes' `WebSearchProvider` ABC — the same interface that `ddgs`, `brave-free`, `firecrawl`, `tavily`, `exa`, `parallel`, and `searxng` implement. No monkey-patching, no fork, no core edits.

### ⚡ One-Command Install

`./install.sh` copies the plugin, verifies `agy` is installed, and wires `web.search_backend: agy` into your `config.yaml`.

### 🌐 Clean Source Domains

Returns clean domain names (`github.com`, `rust-lang.org`), not opaque `vertexaisearch.cloud.google.com/grounding-api-redirect/...` URLs.

### 🖥️ Cross-Platform

Linux, macOS — wherever `agy` runs.

---

## 🎬 Demo

After installing SuearchHermes, just ask Hermes to search:

```
> search for the latest rust version

Hermes: The latest stable version of Rust is 1.97.0, released on July 9, 2026.
         Sources: rust-lang.org, releases.rs
```

```
> investiga sobre rust9x

Hermes: Rust9x is an unofficial fork of the Rust compiler that restores
         compatibility for Windows 9x/ME/NT/2000/XP/Vista. It provides custom
         target triples and API fallbacks for legacy systems.
         Sources: github.com, seri.tools, reddit.com
```

```
> what does the internet say about Hermes Agent Nous Research

Hermes: Hermes Agent by Nous Research is an open-source autonomous AI agent
         platform with a CLI, TUI, persistent memory, tool integration, and
         connectivity with messaging channels.
         Sources: hermes-agent.org, nousresearch.com, github.com
```

---

## 🚀 Quick Start

### Prerequisites

1. **Hermes Agent** installed (`~/.hermes/hermes-agent/`)
2. **Antigravity CLI** (`agy`) installed and authenticated:

```bash
# Install agy
curl -fsSL https://antigravity.google/cli/install.sh | bash

# Authenticate with your Google account
agy
```

3. **Python 3.10+** (comes with Hermes)

### Install

```bash
git clone https://github.com/leonardo-ferioli/SuearchHermes.git
cd SuearchHermes
./install.sh
```

That's it. The script will:
- ✅ Copy the plugin to `~/.hermes/hermes-agent/plugins/web/agy/`
- ✅ Check that `agy` is installed
- ✅ Add `web.search_backend: agy` to `~/.hermes/config.yaml`

### Verify

```bash
cd ~/.hermes/hermes-agent
./venv/bin/python -c "from plugins.web.agy.provider import AgYWebSearchProvider; p = AgYWebSearchProvider(); print(p.name, p.is_available())"
# Expected: agy True
```

### Use

Just ask Hermes to search for something:

```
> search for the latest rust version
> investiga sobre rust9x
> what does the internet say about Windows XP Rust support
> busca esto: best Python web frameworks 2026
```

Hermes will use Google via agy automatically. No extra commands needed.

---

## 📝 Examples

### Example 1: Version check

```
> search for the latest stable version of rust
```

**Result:**
```json
{
  "success": true,
  "data": {
    "web": [
      {"title": "Rust 1.97.0 released July 9, 2026", "url": "rust-lang.org", "description": "The latest stable version of Rust is 1.97.0...", "position": 1},
      {"title": "rust-lang.org", "url": "https://rust-lang.org", "description": "", "position": 2},
      {"title": "releases.rs", "url": "https://releases.rs", "description": "", "position": 3}
    ]
  }
}
```

### Example 2: Research

```
> research rust9x windows xp fork
```

**Result:**
```json
{
  "success": true,
  "data": {
    "web": [
      {"title": "Rust9x is an unofficial fork...", "url": "github.com", "description": "Rust9x restores compatibility for Windows 9x/ME/NT/2000/XP/Vista", "position": 1},
      {"title": "github.com", "url": "https://github.com", "description": "", "position": 2},
      {"title": "seri.tools", "url": "https://seri.tools", "description": "", "position": 3}
    ]
  }
}
```

### Example 3: Multi-language queries

SuearchHermes works with queries in any language — Gemini processes them natively:

```
> busca: mejores frameworks de Python 2026
> 搜索: Rust Windows XP 支持
> recherche: version la plus récente de Rust
```

---

## 🔧 Manual Install

If you prefer to do it manually:

```bash
# 1. Copy plugin files
mkdir -p ~/.hermes/hermes-agent/plugins/web/agy
cp plugins/web/agy/__init__.py  ~/.hermes/hermes-agent/plugins/web/agy/
cp plugins/web/agy/provider.py  ~/.hermes/hermes-agent/plugins/web/agy/

# 2. Configure Hermes — add to ~/.hermes/config.yaml
echo 'web:
  search_backend: agy' >> ~/.hermes/config.yaml

# 3. Restart Hermes
hermes gateway restart
```

---

## ⚙️ Configuration

### Config keys

All configuration lives in `~/.hermes/config.yaml`:

```yaml
web:
  search_backend: agy      # Use agy for web_search
  # backend: agy           # Or set as shared backend for search + extract
```

### Plugin properties

#### agy (binary)

| Property | Value |
|---|---|
| `name` | `agy` |
| `display_name` | `Google via Antigravity (agy)` |
| `supports_search` | ✅ Yes |
| `supports_extract` | ✅ Yes |
| `is_available()` | Checks for `agy` binary at `~/.local/bin/agy` or in `PATH` |

#### agy-oauth (direct API)

| Property | Value |
|---|---|
| `name` | `agy-oauth` |
| `display_name` | `Google via Antigravity OAuth` |
| `supports_search` | ✅ Yes |
| `supports_extract` | ✅ Yes |
| `is_available()` | Checks for valid OAuth tokens in `~/.config/antigravity/tokens.json` |

**agy-oauth** calls the Google Gemini API directly using OAuth tokens — no `agy` binary required. To use it:

```bash
# 1. Get the OAuth URL
python3 -c "from plugins.web.agy.oauth_provider import get_auth_url; url, _, _ = get_auth_url(); print(url)"

# 2. Open the URL in your browser, authorize, copy the code

# 3. Complete login
python3 -c "from plugins.web.agy.oauth_provider import complete_login; complete_login('<code>', '<code_verifier>')"

# 4. Configure Hermes
echo 'web:
  search_backend: agy-oauth' >> ~/.hermes/config.yaml
```

### How agy is invoked

```bash
agy -p "Search the web for: <query>

Respond in this exact format and nothing else:

ANSWER: <one or two sentences answering the question, in English>
SOURCES: <comma-separated list of source domain names>" \
  --dangerously-skip-permissions
```

The response is parsed and normalized into Hermes' expected format:

```json
{
  "success": true,
  "data": {
    "web": [
      {"title": "...", "url": "...", "description": "...", "position": 1}
    ]
  }
}
```

---

## 🏛️ Architecture

### Files

```
SuearchHermes/
├── install.sh                          # One-command installer
├── README.md                           # English docs (this file)
├── README_es.md                        # Spanish docs
├── README_zh.md                        # Chinese docs
├── CHANGELOG.md                        # Version history
├── CONTRIBUTING.md                     # Contribution guide
├── AGENT_CONTRIBUTOR_GUIDE.md          # Guide for AI agents
├── CODE_OF_CONDUCT.md                  # Community standards
├── SECURITY.md                         # Security policy
├── LICENSE                             # MIT
├── NOTICE                              # Third-party notices
├── pyproject.toml                      # Python package metadata
├── assets/
│   ├── banner.svg                      # Logo banner
│   └── social-preview.png              # OG/social preview image
├── .github/
│   ├── FUNDING.yml                     # Sponsorship
│   ├── ISSUE_TEMPLATE/                 # Bug report + feature request
│   └── workflows/
│       └── ci.yml                      # CI checks
└── plugins/
    └── web/
        └── agy/
            ├── __init__.py             # Plugin registration
            ├── provider.py             # AgYWebSearchProvider (binary)
            └── oauth_provider.py       # AgYOAuthWebSearchProvider (direct API)
```

### Plugin interface

The plugin implements Hermes' `WebSearchProvider` ABC:

```python
class AgYWebSearchProvider(WebSearchProvider):
    @property
    def name(self) -> str:           # "agy"
    @property
    def display_name(self) -> str:   # "Google via Antigravity (agy)"
    def is_available(self) -> bool:  # checks agy binary exists
    def supports_search(self) -> bool:  # True
    def supports_extract(self) -> bool: # False
    def search(self, query, limit=5) -> Dict:  # calls agy -p
    def get_setup_schema(self) -> Dict:        # UI metadata
```

### Integration with Hermes

```
~/.hermes/
├── config.yaml                          # web.search_backend: agy or agy-oauth
└── hermes-agent/
    └── plugins/
        └── web/
            ├── brave_free/              # built-in
            ├── ddgs/                    # built-in
            ├── exa/                     # built-in
            ├── firecrawl/               # built-in
            ├── parallel/                # built-in
            ├── searxng/                 # built-in
            ├── tavily/                  # built-in
            └── agy/                     # ← SuearchHermes installs here
                ├── __init__.py
                ├── provider.py          # Binary mode (agy -p)
                └── oauth_provider.py    # OAuth mode (direct API)
```

---

## 🛣️ Roadmap

- [x] v1.0.0 — Core plugin, installer, docs
- [x] **v1.1.0** — Direct Gemini API integration via OAuth (bypass agy CLI)
- [x] **v1.2.0** — Extract support (page content extraction via agy and OAuth)
- [x] **v1.3.0** — Configurable prompt template (env vars: `AGY_SEARCH_PROMPT`, `AGY_EXTRACT_PROMPT`)
- [x] **v1.4.0** — Response caching (5-minute TTL, avoids repeated searches within a session)
- [x] **v1.5.0** — Rate limit awareness (checks `retrieveUserQuotaSummary` before search)

---

## 🧪 Verification

After installation, run these checks:

```bash
# 1. Plugin loads (binary mode)
cd ~/.hermes/hermes-agent
./venv/bin/python -c "
from plugins.web.agy.provider import AgYWebSearchProvider
p = AgYWebSearchProvider()
print(f'name: {p.name}')
print(f'available: {p.is_available()}')
print(f'supports_search: {p.supports_search()}')
print(f'supports_extract: {p.supports_extract()}')
"
# Expected:
# name: agy
# available: True
# supports_search: True
# supports_extract: False

# 2. Plugin loads (OAuth mode)
./venv/bin/python -c "
from plugins.web.agy.oauth_provider import AgYOAuthWebSearchProvider
p = AgYOAuthWebSearchProvider()
print(f'name: {p.name}')
print(f'available: {p.is_available()}')
print(f'supports_search: {p.supports_search()}')
print(f'supports_extract: {p.supports_extract()}')
"
# Expected:
# name: agy-oauth
# available: True (if tokens exist)
# supports_search: True
# supports_extract: False

# 3. Search works (binary mode)
./venv/bin/python -c "
import json
from plugins.web.agy.provider import AgYWebSearchProvider
p = AgYWebSearchProvider()
r = p.search('latest stable version of rust', limit=5)
print(json.dumps(r, indent=2))
"
# Expected: {"success": true, "data": {"web": [...]}}

# 4. Search works (OAuth mode)
./venv/bin/python -c "
import json
from plugins.web.agy.oauth_provider import AgYOAuthWebSearchProvider
p = AgYOAuthWebSearchProvider()
r = p.search('latest stable version of rust', limit=5)
print(json.dumps(r, indent=2))
"
# Expected: {"success": true, "data": {"web": [...]}}
```

---

## ❌ Uninstall

```bash
# 1. Remove plugin
rm -rf ~/.hermes/hermes-agent/plugins/web/agy

# 2. Remove from config.yaml — delete or comment out:
#    web:
#      search_backend: agy

# 3. Restart Hermes
hermes gateway restart
```

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

For AI agents contributing to this repo, see [AGENT_CONTRIBUTOR_GUIDE.md](./AGENT_CONTRIBUTOR_GUIDE.md).

### Contributors

<a href="https://github.com/leonardo-ferioli">
  <img src="https://avatars.githubusercontent.com/u/221494455?v=4" width="50" height="50" alt="Leonardo Ferioli"/>
</a>

---

## 📋 Requirements

| Requirement | Version | Notes |
|---|---|---|
| Hermes Agent | any (with plugin system, post-PR #25182) | `~/.hermes/hermes-agent/` |
| Antigravity CLI | 1.1.0+ | Only for `agy` mode. `agy-oauth` mode doesn't need it |
| Python | 3.10+ | comes with Hermes |
| OS | Linux, macOS | wherever `agy` runs |
| Google account | any | for agy OAuth (free) |

---

## 📄 License

MIT — see [LICENSE](./LICENSE)

---

## 👤 Author

**Leonardo Ferioli**

- GitHub: [@leonardo-ferioli](https://github.com/leonardo-ferioli)
- Email: leonardo.ferioli.12@gmail.com

---

## ⭐ Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=leonardo-ferioli/SuearchHermes&type=Date)](https://star-history.com/#leonardo-ferioli/SuearchHermes&Date)

</div>

---

<div align="center">

**SuearchHermes** — Google Search, free, for Hermes Agent.

Built because DuckDuckGo scraping and paid SERP APIs are not good enough.

If this project helped you, consider ⭐ starring the repo.

</div>
