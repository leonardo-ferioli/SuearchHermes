# SuearchHermes

**Google Search via Antigravity CLI (agy) for Hermes Agent**

A free web search plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent) that uses Google's Search Grounding through the [Antigravity CLI](https://github.com/google-antigravity/antigravity-cli) (`agy`). No API key, no billing, no DuckDuckGo — just real Google results synthesized by Gemini.

## Why?

Hermes Agent ships with `web_search` support, but the built-in backends all have problems:

| Backend | Problem |
|---|---|
| Firecrawl | Paid API key required |
| Tavily | Paid API key required |
| Exa | Paid API key required |
| Brave | Free tier limited to 2,000 queries/month, requires API key |
| DDGS (DuckDuckGo) | Free but poor quality, rate-limited, often blocked |

**SuearchHermes** replaces all of that with `agy` — Google's own Antigravity CLI — which has Google Search Grounding built in via Gemini. It's free, uses your existing Google account OAuth, and returns **synthesized answers with cited sources** instead of raw SERP links.

## How it works

```
User: "search for X"
  → Hermes web_search tool
    → SuearchHermes plugin (agy backend)
      → agy -p "Search the web for: X..."
        → Gemini + Google Search Grounding
          → Synthesized answer + source domains
      ← Normalized to Hermes' expected format
    ← Returned to Hermes
  ← User gets a real answer with sources
```

## Requirements

1. **Hermes Agent** installed (`~/.hermes/hermes-agent/`)
2. **Antigravity CLI** (`agy`) installed and authenticated:
   ```bash
   curl -fsSL https://antigravity.google/cli/install.sh | bash
   agy  # authenticate with your Google account
   ```
3. **Python** (comes with Hermes)

## Installation

### Option A: Install script (recommended)

```bash
git clone https://github.com/leonardo-ferioli/SuearchHermes.git
cd SuearchHermes
./install.sh
```

The script will:
1. Copy the plugin to `~/.hermes/hermes-agent/plugins/web/agy/`
2. Check that `agy` is installed
3. Add `web.search_backend: agy` to `~/.hermes/config.yaml`

### Option B: Manual install

1. Copy the `plugins/web/agy/` directory to `~/.hermes/hermes-agent/plugins/web/agy/`:
   ```bash
   mkdir -p ~/.hermes/hermes-agent/plugins/web/agy
   cp plugins/web/agy/__init__.py ~/.hermes/hermes-agent/plugins/web/agy/
   cp plugins/web/agy/provider.py ~/.hermes/hermes-agent/plugins/web/agy/
   ```

2. Add this to your `~/.hermes/config.yaml`:
   ```yaml
   web:
     search_backend: agy
   ```

3. Restart Hermes.

## Verification

After installation, verify the plugin is loaded:

```bash
cd ~/.hermes/hermes-agent
./venv/bin/python -c "from plugins.web.agy.provider import AgYWebSearchProvider; p = AgYWebSearchProvider(); print(p.name, p.is_available())"
```

Expected output:
```
agy True
```

## Usage

Just ask Hermes to search for something:

- "search for the latest rust version"
- "investiga sobre rust9x"
- "what does the internet say about Windows XP Rust support"
- "busca esto: best Python web frameworks 2026"

Hermes will use Google via agy automatically.

## Configuration

The plugin responds to these config keys in `~/.hermes/config.yaml`:

```yaml
web:
  search_backend: agy      # use agy for web_search
  # backend: agy           # alternatively, set shared backend
```

## How it works under the hood

The plugin implements Hermes' `WebSearchProvider` ABC:

- **`name`**: `"agy"`
- **`display_name`**: `"Google via Antigravity (agy)"`
- **`is_available()`**: checks if `agy` binary exists at `~/.local/bin/agy` or in PATH
- **`supports_search()`**: `True`
- **`supports_extract()`**: `False` (agy doesn't do page extraction)
- **`search(query, limit)`**: calls `agy -p` with a prompt that asks for a concise answer + source domains, then normalizes the output to Hermes' `{"web": [{"title", "url", "description", "position"}]}` format

No API keys, no environment variables, no billing. Just `agy` and your Google account.

## Files

```
SuearchHermes/
├── install.sh                    # One-command installer
├── README.md                     # This file
├── LICENSE                       # MIT
└── plugins/
    └── web/
        └── agy/
            ├── __init__.py       # Plugin registration
            └── provider.py       # AgYWebSearchProvider implementation
```

## Compatibility

- Hermes Agent (any version with the plugin system, post-PR #25182)
- Linux, macOS (where `agy` is supported)
- Python 3.10+ (comes with Hermes)

## Uninstall

```bash
rm -rf ~/.hermes/hermes-agent/plugins/web/agy
# Remove from config.yaml:
#   web:
#     search_backend: agy
```

## License

MIT

## Author

Leonardo Ferioli
