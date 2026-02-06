# Promise Keeper

![CI](https://github.com/Promise-Foundation/promise-keeper/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

Protocol-first implementation for promise reliability, evidence, and assessment.

Status: **Phase 0 / experimental**. This repository ships a minimal, runnable slice: create a Promise Card, compute a CID, and verify it via a public endpoint.

## What is this?

Promise Keeper defines a lightweight protocol for testable commitments:

- Promise Cards with explicit success criteria and evidence plans
- Evidence entries with content-addressed identifiers (CIDs)
- Assessments with kept/broken/inconclusive verdicts

The Python package is `pkc`.

## Install (local dev)

```bash
uv sync --group dev --group api
```

Optional adapters:

```bash
uv sync --group dev --group api --group moltbook
uv sync --group dev --group api --group s3
```

## Run the API (Phase 0)

```bash
export PK_API_KEY="dev-key"
uv run uvicorn pkc.api.main:app --reload --host 0.0.0.0 --port 8080
```

Generate a secure API key:

```bash
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
```

Store it in a local `.env` file (do not commit). You can start from `.env.example`:

```bash
echo "PK_API_KEY=your_generated_key" > .env
export $(cat .env | xargs)
```

### Endpoints

- `GET /health`
- `POST /cards` (auth)
- `POST /evidence` (auth)
- `POST /assessments` (auth)
- `GET /verify/{cid}` (public)
- `GET /resolve/{cid}` (public)
- `GET /docs` (OpenAPI UI)

### Example: create a Promise Card

```bash
curl -X POST http://localhost:8080/cards \
  -H "Authorization: Bearer dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "promiser_id": "@agent",
    "domain": "/software/debug",
    "promise": "Fix IndexError in parser.py",
    "success_criteria": "Tests pass and error is resolved",
    "evidence_plan": "artifact_cid",
    "assessment_window": "2026-02-13"
  }'
```

### Example: verify a CID

```bash
curl http://localhost:8080/verify/<promise_card_cid>
```

## Tests

```bash
uv run ruff check .
uv run pytest -q
```

## Docs

- `QUICKSTART.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/protocol/`

## Project

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `CHANGELOG.md`

## License

MIT. See `LICENSE`.
