# Agent Contributor Guide

This guide is for AI agents (Claude, GPT, Gemini, Hermes, etc.) that want to contribute to SuearchHermes.

## Project context

SuearchHermes is a **thin plugin** — two Python files that wrap the `agy` CLI as a Hermes `WebSearchProvider`. The codebase is intentionally minimal. Do not add complexity.

## What you can do

- **Bug fixes** — fix issues reported in GitHub Issues
- **Documentation** — improve README, add examples, translate
- **Tests** — add unit tests for the provider
- **Compatibility** — verify against new Hermes versions

## What you should NOT do

- Do not add external dependencies — the plugin must stay zero-dep
- Do not add abstraction layers — it's two files, keep it that way
- Do not change the `WebSearchProvider` interface — that's Hermes' contract
- Do not add configuration options unless there's a real user need

## How to make changes

1. Read `plugins/web/agy/provider.py` — it's ~150 lines, you can hold it all in context
2. Read `plugins/web/agy/__init__.py` — it's 10 lines
3. Make your change
4. Test locally:
   ```bash
   cp -r plugins/web/agy ~/.hermes/hermes-agent/plugins/web/agy
   cd ~/.hermes/hermes-agent
   ./venv/bin/python -c "from plugins.web.agy.provider import AgYWebSearchProvider; p = AgYWebSearchProvider(); print(p.name, p.is_available())"
   ```
5. Run a real search:
   ```bash
   ./venv/bin/python -c "
   import json
   from plugins.web.agy.provider import AgYWebSearchProvider
   p = AgYWebSearchProvider()
   r = p.search('test query', limit=5)
   print(json.dumps(r, indent=2))
   "
   ```
6. Commit and open a PR

## Code style

- Python 3.10+ type hints (`str | None` not `Optional[str]`)
- Docstrings on public methods
- Match the style of `plugins/web/ddgs/provider.py` in the Hermes repo
- Line length: 100 chars max

## File boundaries

| File | Responsibility |
|---|---|
| `__init__.py` | Only `register(ctx)` — nothing else |
| `provider.py` | All logic: class, search method, helpers |
| `install.sh` | Installation only — no runtime logic |
| `README.md` | User-facing docs |

Do not cross these boundaries.
