# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in SuearchHermes, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email: leonardo.ferioli.12@gmail.com
3. Include: description, steps to reproduce, potential impact

You will receive a response within 48 hours.

## Scope

SuearchHermes is a thin wrapper around the `agy` CLI. Security of the underlying `agy` OAuth session, Gemini API, and Google Search Grounding is handled by Google. This plugin does not store, transmit, or log any API keys or OAuth tokens — it simply invokes `agy -p` as a subprocess.

## Best practices for users

- Keep `agy` updated to the latest version
- Do not share your `agy` OAuth session with untrusted parties
- The `--dangerously-skip-permissions` flag is used to allow non-interactive execution — this is safe for search queries but be aware of what it implies
