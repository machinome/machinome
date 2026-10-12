# OpenCode Backend Verification

**Date:** 2026-08-01

## Red-First Coverage

The focused acceptance tests were added before the adapter and initially
reported nine expected failures for the missing backend registration, CLI
selection, server lifecycle, role sessions, delivery correlation, and shutdown.
The completed fixture suite exercises an authenticated fake HTTP/SSE server,
unchanged Builder and Fordesmac profile manifests, generated configuration,
deny-by-default permissions, exact role contracts, root-guidance selection,
native message ancestry, active steering, idle-race resume, interruption,
session deletion, process loss, and bounded shutdown.

Real OpenCode 1.18.11 then exposed two fixture blind spots before acceptance:

1. Caller-supplied message IDs must use OpenCode's `msg_` shape and increasing
   timestamp encoding. A merely prefixed random ID was either rejected or made
   a completed user message remain logically newer than its assistant, causing
   repeated model turns.
2. A correction persisted during a busy-to-idle race can be orphaned. The
   adapter now reconciles accepted message ancestry on idle and resumes the
   same native message ID with no new parts at most once, so the persisted
   envelope is processed without duplicating its text.

Both failures were reproduced against the real server before their fixture
expectations and implementation fixes were accepted.

## Authenticated Runtime

The installed runtime reported OpenCode `1.18.11`. A temporary independent Git
project under `/tmp/opencode/` was used so no mechanical project was exposed.

- Builder opened one persistent session.
- Fordesmac opened Foreman, Designer, Machinist, and Librarian sessions in
  declaration order behind one server.
- A real Builder turn completed once with output `OPENCODE_SMOKE` using
  `openai/gpt-5.6-sol`; no variant was recorded. This identifies the tested
  operator environment and is not a shop default.
- The persisted user message contained the exact Builder profile prompt, both
  allowlisted skill documents, precedence framing, and a deliberately
  conflicting exact-root `AGENTS.md` after that framing.
- During a real `sleep 5` Bash tool call, one accepted correction changed the
  result to `CORRECTED`. The two unique accepted user messages each had an
  assistant descendant, the correction retained the original portable delivery
  identity, and the adapter emitted exactly one completion.
- Repeated server startup initially timed out when unrestricted external
  extensions were allowed. The accepted backend retains the measured `--pure`
  launch: operator authentication and provider defaults remain available while
  external plugins do not execute.

## Repository Validation

```text
PYTHONPATH="$PWD" pytest
138 passed before archival. The post-archive run reported 137 passed and one
existing 5-second initial-artifact browser timeout; that exact E2E passed on its
immediate isolated rerun.

python -m py_compile floor/backends/opencode.py \
  tests/fixtures/fake_opencode_server.py tests/test_opencode_backend.py
passed

openspec validate add-opencode-backend --strict
Change 'add-opencode-backend' is valid

git diff --check
passed
```
