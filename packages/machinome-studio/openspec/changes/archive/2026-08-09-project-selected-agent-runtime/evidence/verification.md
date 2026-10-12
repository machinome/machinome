# Implementation verification

Verified on 2026-08-09 from the change worktree.

## Automated suite

- `PYTHONPATH="$PWD" python -m unittest discover -s tests -v`:
  178 tests passed.
- `npm --prefix floor/frontend run test`: passed.
- `npm --prefix floor/frontend run build`: passed (Vite production build).
- `scripts/test-e2e`: 36 tests passed.
- `openspec validate project-selected-agent-runtime --strict`: passed.

The first parallel validation attempt raced the frontend build replacing
`floor/static` against a floor health check. The failing health test passed
immediately in isolation and the complete Python suite passed when rerun after
the build. Validation commands that mutate the shared static output should not
run concurrently with floor tests.

The Python suite continues to emit pre-existing `ResourceWarning` messages for
unclosed AnyIO memory streams and one subprocess output file during cleanup;
they do not fail the suite but remain cleanup observability blind spots. `npm
ci` reported two dependency audit advisories (one moderate, one high); no
dependency versions were changed by this change.

## Real mixed-backend floor

An isolated independent Git project declared:

```toml
[tool.solid-node-studio.agents]
foreman = "codex:gpt-5.6-terra:medium"
designer = "claude:opus:medium"
machinist = "codex:gpt-5.6-terra:medium"
librarian = "codex:gpt-5.6-terra:medium"
```

The real installed Codex and Claude transports opened under the `fordesmac`
profile. The broker recorded all four manifested roles, delivered sequence 1
to the Codex-owned Foreman, delivered sequence 2 to the Claude-owned Designer,
and recorded Designer's `runtime-smoke-1` acknowledgment. SIGINT then closed
the floor, both transports, and the HTTP server with process exit 0. The
temporary project was removed after verification.
