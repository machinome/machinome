# Evidence — execute-running-play

Worktree `machinome-viewer/WTs/execute-running-play`, branch
`execute-running-play`, planning commit `091cb93` over clean viewer main
`2912006dd4864bc25aa4b7c0e11cd2e457dd5836`. The implementation remains
uncommitted for review. Widget `node_modules` is a symlink to the primary
checkout; `npm ci` was not run.

## Producer parity

The framework fixture was copied byte-for-byte after regeneration:
SHA-256 `3f3407c11f321e88d626565d97d43ff56ea63a6c1c1d19bfe8ca028cbd46eed6`,
289204 bytes, 22 scenarios over 19 machines and 378 ticks. Its complete
replay and widened feature census pass.

Focused tests cover strict loading, large-offset absolute handoff, the
`x=40,y=30,z=20` cascade stop, positive and negative stop recollection,
linear, nonlinear and multi-source downstream observers, and snapshot
parity from the producer corpus. A mounted Chromium page loads a version-9
document, requests `play_input: 0→100`, and observes retained value 90.
The corpus-width guard independently derives split requests, reversal release
after pickup, and a stop on an actual downstream play follower. Negative
mutations removing each behavior are refused by name.

## Validation

- `npm run typecheck`: pass.
- Focused Vitest after final adversarial changes: 87 passed.
- Final corpus/run-focused validation after the strengthened guard and
  legacy-path landing gate: 88 passed; typecheck passed.
- Full Vitest after final graph/landing hardening: 46 files, 1242 passed.
- Full Python/Playwright suite after API 22 build: 183 passed, 18 subtests,
  51 deprecation warnings, 235.80 seconds.
- `npm run build`: pass; bundle 795.4 kb.
- Real-page version-9 PLAY smoke: 1 passed.
- `openspec validate execute-running-play --strict`: valid.

The implementer performed no integration, archive, push or publication.

## Coordinator closeout

The pilot's explicit GO authorizes this companion and local main integration.
Root independently reviewed the loader, projection, original-input stop
localization, multi-source observers, exact landing propagation and legacy
fallback. Review found the multiple-source ancestry and tiny legacy-delta
hazards; their corrected paths and focused tests are included above.
Both delta specs were synchronized and every added requirement/scenario was
compared against its baseline. All six viewer baseline specs validate strictly.
The separate viewer repository and its AGPL boundary are retained. The cycle
has one planning commit and one completed implementation commit; the earlier
per-increment guidance does not override this explicitly coordinated cycle.
No push or publication is authorized or performed.
