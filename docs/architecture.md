# Architecture

## Goals
- Domain-first: protocol logic lives independent of Moltbook.
- Ports & adapters: infrastructure is swappable.
- Event-driven core: actions emit auditable events.
- Phase evolution: Phase 0 -> PKC without rewrites.

## Layers and Boundaries
1) Domain (`src/pkc/domain`)
- Pure logic: models, policies, state machines, validations.
- No IO, no HTTP, no DB.

2) Application (`src/pkc/app`)
- Use-cases and workflows that orchestrate domain logic.
- Talks to ports only.

3) Ports (`src/pkc/ports`)
- Interfaces for social platform, storage, registry, event log, KV, etc.

4) Adapters (`src/pkc/adapters`)
- Moltbook, storage, persistence, crypto implementations.
- Owns retries, rate-limits, auth, JSON mapping.

5) Runtime (`src/pkc/runtime`)
- Config, DI container, CLI/daemon wiring.

## Behave Strategy
- Acceptance tests for workflows and cross-adapter behavior.
- Use in-memory adapters for local CI, real Moltbook for staging.

## Phase Evolution
- Phase 0: minimal promise cards + evidence + assessment; Moltbook adapter.
- Phase 1: validator circle + auditable assignment.
- Phase 2: anti-gaming policies + domain weights/evidence floors.
- Phase 3: PKC metrics + governance + abductio.
