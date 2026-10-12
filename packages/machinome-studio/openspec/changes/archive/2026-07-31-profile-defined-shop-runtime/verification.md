# Verification evidence

Date: 2026-07-31

## Deterministic suites

- `python -m unittest discover -s tests -v`: 125 tests passed.
- `npm --prefix floor/frontend run test`: TypeScript project build passed.
- `npm --prefix floor/frontend run build`: Vite production build passed; 46 modules transformed.
- `scripts/test-e2e`: 20 tests passed, including explicit Builder direct lifecycle and Fordesmac four-agent delegated lifecycle scenarios.
- `openspec validate profile-defined-shop-runtime --strict`: passed.
- `git diff --check`: passed.

The first full-suite run was intentionally run concurrently with another Playwright suite and one artifact-render assertion exceeded its five-second timeout. The complete E2E suite passed in that same matrix, and the full 125-test suite passed when rerun alone.

## Real runtime matrix

Installed runtimes:

- Codex CLI 0.146.0
- Claude Code 2.1.220
- Hermes Agent 0.19.0

Each smoke used an isolated temporary primary shop checkout, a named temporary project, the real configured backend command, and the fake finite CAD builder so backend behavior was real while project scaffolding remained bounded.

### Builder

All three backends opened exactly one waiting Builder, served `/artifacts/viewer.json` with HTTP 200, accepted one direction and one steering correction under a single correlated delivery, published Builder output, emitted exactly one `direct_work_started` and one `direct_work_completed`, allocated no assignment IDs, returned Builder to waiting, exited zero, and left no backend child alive.

| Backend | Elapsed | Shutdown | Surviving children |
|---|---:|---:|---:|
| Codex | 12.082 s | 0.264 s | 0 |
| Claude | 6.059 s | 2.770 s | 0 |
| Hermes | 27.680 s | 1.317 s | 0 |

### Fordesmac

All three backends opened the declared Foreman, Designer, Machinist, and Librarian roster before user direction, served `/artifacts/viewer.json` with HTTP 200, published real Foreman backend output, exercised Designer and Librarian through assignment, acknowledgement, report, and completion, returned every agent to waiting, exited zero, and left no backend child alive.

| Backend | Elapsed | Shutdown | Surviving children |
|---|---:|---:|---:|
| Codex | 7.154 s | 0.515 s | 0 |
| Claude | 6.312 s | 2.018 s | 0 |
| Hermes | 36.613 s | 1.668 s | 0 |

The retained temporary JSON/log evidence was managed through one rolling GC manifest and removed after this durable summary was recorded.
