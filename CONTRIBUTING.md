# Contributing

Thanks for helping improve Promise Keeper.

## Quick Start

1. Install dependencies:

```bash
uv sync --group dev --group api
```

2. Run checks:

```bash
uv run ruff check .
uv run pytest -q
```

3. (Optional) Run the API locally:

```bash
export PK_API_KEY="dev-key"
uv run uvicorn pkc.api.main:app --reload --host 0.0.0.0 --port 8080
```

## Pull Requests

- Keep PRs focused and small.
- Add or update tests when behavior changes.
- Update documentation when you change public-facing behavior.
- Ensure CI passes before requesting review.

## Code Style

- Linting: `ruff`
- Formatting: `ruff format` (optional, but preferred)

## Reporting Issues

Please use GitHub Issues for bugs and feature requests.
For security issues, see `SECURITY.md`.
