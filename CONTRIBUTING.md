# Contributing to SuearchHermes

Thanks for your interest in contributing! This is a small, focused plugin — keep it simple.

## How to contribute

### Bug reports

1. Check existing issues first
2. Open a new issue with:
   - What you expected
   - What happened instead
   - Your Hermes version, agy version, OS
   - Steps to reproduce

### Feature requests

1. Check existing issues first
2. Open a new issue with the `enhancement` label
3. Describe the use case, not just the solution

### Pull requests

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test against your local Hermes:
   ```bash
   cp -r plugins/web/agy ~/.hermes/hermes-agent/plugins/web/agy
   cd ~/.hermes/hermes-agent
   ./venv/bin/python -c "from plugins.web.agy.provider import AgYWebSearchProvider; p = AgYWebSearchProvider(); print(p.name, p.is_available())"
   ```
5. Commit with a clear message
6. Push and open a PR

### Code style

- Python 3.10+ type hints
- Docstrings on all public methods
- Match the style of existing Hermes plugins (`plugins/web/ddgs/`, `plugins/web/brave_free/`)

### Project structure

```
plugins/web/agy/
├── __init__.py     # register(ctx) — keep this minimal
└── provider.py     # AgYWebSearchProvider — all logic here
```

Keep the plugin self-contained. No external dependencies beyond what Hermes already provides.
