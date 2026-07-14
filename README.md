<div align="center">

<img src="assets/banner.svg" alt="SuearchHermes" width="720"/>

# SuearchHermes

**Google Search via Antigravity (agy) for Hermes Agent — Free, No API Key**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Hermes](https://img.shields.io/badge/Hermes-Agent-6E40C9?style=flat&logo=gnometerminal&logoColor=white)](https://github.com/NousResearch/hermes-agent)
[![agy](https://img.shields.io/badge/Antigravity%20CLI-agy-4285F4?style=flat&logo=google&logoColor=white)](https://github.com/google-antigravity/antigravity-cli)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](./LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-blue?style=flat&logo=linux&logoColor=white)]()
[![Price](https://img.shields.io/badge/Cost-Free%20%E2%80%A2%20No%20API%20Key-brightgreen?style=flat)]()

[Features](#-features) · [Why](#-why) · [How It Works](#-how-it-works) · [Quick Start](#-quick-start) · [Manual Install](#-manual-install) · [Configuration](#-configuration) · [Architecture](#-architecture) · [Uninstall](#-uninstall) · [Contributing](#-contributing)

</div>

---

## 📰 News

- **2026-07-14** 🚀 **v1.0.0 released**: Initial public release. Google Search via Antigravity CLI (agy) plugin for Hermes Agent. Free, no API key, Google Search Grounding via Gemini. Includes one-command installer, full Hermes `WebSearchProvider` ABC implementation, and automatic config wiring.

---

## 🎯 Why?

Hermes Agent ships with `web_search` support, but the built-in backends all have problems:

| Backend | Cost | Problem |
|---|---|---|
| **Firecrawl** | 💰 Paid | API key required, billing per request |
| **Tavily** | 💰 Paid | API key required, limited free tier |
| **Exa** | 💰 Paid | API key required |
| **Parallel** | 💰 Paid | API key required |
| **Brave (free)** | ⚠️ Limited | 2,000 queries/month, requires API key |
| **DDGS** | ✅ Free | Poor quality, rate-limited, often blocked, no synthesis |

**SuearchHermes** replaces all of that with `agy` — Google's own Antigravity CLI — which has **Google Search Grounding** built in via Gemini.

| SuearchHermes | |
|---|---|
| **Cost** | Free, forever |
| **API key** | None — uses your Google account OAuth |
| **Search engine** | Google (via Gemini Search Grounding) |
| **Result quality** | Synthesized answers + cited source domains |
| **Rate limit** | Subject to agy/Gemini fair use |

---

## ✨ Features

- 🔍 **Real Google Search** — via Gemini Search Grounding, not scraping
- 🆓 **Zero cost** — no API key, no billing, no credit card
- 🧠 **Synthesized answers** — Gemini reads the results and gives you a concise answer with sources
- 🔌 **Drop-in Hermes plugin** — implements the `WebSearchProvider` ABC, integrates natively
- ⚡ **One-command install** — `./install.sh` does everything
- 🔄 **Auto config** — wires `web.search_backend: agy` into `config.yaml` automatically
- 🌐 **Source domains** — returns clean domain names, not redirect URLs
- 🖥️ **Cross-platform** — Linux, macOS (wherever agy runs)

---

## 🏗️ How It Works

```
┌─────────┐     ┌──────────┐     ┌───────────────┐     ┌────────────┐     ┌──────────┐
│  User   │────▶│  Hermes  │────▶│ SuearchHermes │────▶│    agy     │────▶│  Google  │
│ "busca" │     │ web_search│     │   (plugin)    │     │   -p       │     │ Grounding│
└─────────┘     └──────────┘     └───────────────┘     └────────────┘     └──────────┘
                                          │                                      │
                                          │     ┌──────────────────────────┐      │
                                          └────▶│ Synthesized answer +     │◀─────┘
                                                │ source domains (JSON)    │
                                                └──────────────────────────┘
```

1. User asks Hermes to search → Hermes calls `web_search("query")`
2. `web_search` checks `config.yaml` → finds `search_backend: agy`
3. SuearchHermes plugin receives the query
4. Plugin calls `agy -p "Search the web for: query..."` with a structured prompt
5. `agy` uses Google Search Grounding via Gemini to search + synthesize
6. Plugin parses the response → normalizes to Hermes' `{"web": [...]}` format
7. Hermes receives results as if it were any other backend

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
```

Expected output:
```
agy True
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

## 🔧 Manual Install

If you prefer to do it manually:

### 1. Copy plugin files

```bash
mkdir -p ~/.hermes/hermes-agent/plugins/web/agy
cp plugins/web/agy/__init__.py  ~/.hermes/hermes-agent/plugins/web/agy/
cp plugins/web/agy/provider.py  ~/.hermes/hermes-agent/plugins/web/agy/
```

### 2. Configure Hermes

Add this to your `~/.hermes/config.yaml`:

```yaml
web:
  search_backend: agy
```

### 3. Restart Hermes

```bash
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

| Property | Value |
|---|---|
| `name` | `agy` |
| `display_name` | `Google via Antigravity (agy)` |
| `supports_search` | ✅ Yes |
| `supports_extract` | ❌ No (agy doesn't do page extraction) |
| `is_available()` | Checks for `agy` binary at `~/.local/bin/agy` or in `PATH` |

### How agy is invoked

The plugin calls `agy` with a structured prompt:

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
      {"title": "...", "url": "...", "description": "...", "position": 1},
      {"title": "...", "url": "...", "description": "", "position": 2}
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
├── README.md                           # This file
├── LICENSE                             # MIT
├── assets/
│   └── banner.svg                      # Logo banner
└── plugins/
    └── web/
        └── agy/
            ├── __init__.py             # Plugin registration (register(ctx))
            └── provider.py             # AgYWebSearchProvider implementation
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
├── config.yaml                          # web.search_backend: agy
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
                └── provider.py
```

---

## 🧪 Verification

After installation, run these checks:

```bash
# 1. Plugin loads
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

# 2. Plugin registers
./venv/bin/python -c "
from plugins.web.agy import register
class FakeCtx:
    def __init__(self): self.providers = []
    def register_web_search_provider(self, p): self.providers.append(p)
ctx = FakeCtx()
register(ctx)
print([p.name for p in ctx.providers])
"
# Expected: ['agy']

# 3. Search works
./venv/bin/python -c "
import json
from plugins.web.agy.provider import AgYWebSearchProvider
p = AgYWebSearchProvider()
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

Contributions are welcome. This is a small, focused plugin — keep it simple.

1. Fork the repo
2. Create a branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add your feature'`)
4. Push (`git push origin feature/your-feature`)
5. Open a PR

### Development setup

```bash
git clone https://github.com/leonardo-ferioli/SuearchHermes.git
cd SuearchHermes

# Test the plugin against your local Hermes
cp -r plugins/web/agy ~/.hermes/hermes-agent/plugins/web/agy

# Run verification (see above)
```

---

## 📋 Requirements

| Requirement | Version | Notes |
|---|---|---|
| Hermes Agent | any (with plugin system, post-PR #25182) | `~/.hermes/hermes-agent/` |
| Antigravity CLI | 1.1.0+ | `curl -fsSL https://antigravity.google/cli/install.sh \| bash` |
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

---

<div align="center">

**SuearchHermes** — Google Search, free, for Hermes Agent.

Built because DuckDuckGo scraping and paid SERP APIs are not good enough.

</div>
