## Why

Curta Type I's unchanged bulk crank request loses an earlier carry merely when
later result stations join the running graph: six stations give the expected
`tens.turn = 704`, seven give `698.464`, and the full eleven give `632`.
The traced executor changes the motion supplied downstream when unrelated
selector cuts subdivide a request; Curta needs its complete result bank to carry
correctly without subdividing commands or removing parts and contact checks.

## What Changes

- Preserve the timing of determined motion read by selected dependency blocks
  and affected ordinary chains, including their upstream motion, instead of replacing
  it by a straight line through each interval's endpoints.
- Make graph-extension and request-partition invariance explicit for the
  originating carry. Keep the unchanged physical laws, 704-degree oracle,
  full bank, and constrained bulk request as acceptance gates.
- Explicitly revise the endpoint-increment handoff in the existing selection
  requirement and ADR-122 design; this is a semantic correction, not merely a
  cache optimization. Retain branch selection, causal ordering, jump removal,
  self-read landing, refusal, and transactional guarantees.
- Add framework regressions distilled from Curta, and validate the unchanged
  project reproductions against the candidate framework before adoption.
- Publish newly exported running programs as document v11 and include the
  source-timing semantic generation in snapshot identity. Generate separately
  consumed parity fixtures; posed/looping and clocked documents are unchanged.
- Do not add project knobs, fixed microsteps, a coupled solver, or Curta-specific
  knowledge to the framework. Do not change the public authoring syntax.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `export`: Newly published running documents use v11 and source-timed identity;
  revise the older running, Play and time-drive version-selection promises
  without changing their payloads or the committed legacy conformance corpus.
- `simulation`: Determined motion feeding selected and ordinary dependencies retains its
  timing, so irrelevant later stations and internal partition boundaries cannot
  alter an earlier carry. This clarifies the existing partition-agreement
  promise and replaces its conflicting endpoint-handoff prescription.
  The same frozen physical laws must agree in both graph forms; the blanket
  no-block preservation guarantee is narrowed to paths where the existing
  affine handoff is exact. No-block timing defects are corrected too.

## Impact

- Python running executor: `machinome/simulation/program.py` and narrowly
  necessary path plumbing in `run.py`; selection, self-read, stop, replay and
  conformance tests. Actual changes remain subject to red-first implementation.
- Origin: independent project `projects/Calculators/Curta-Type-I-3x`, branch
  `direct-operation`, diagnostic checkpoint `1c3dfde`, current checkpoint
  `8852677`. Its laws and physical oracle are not implementation targets.
- Consumer parity: independent viewer change `preserve-running-source-timing`
  implements API 24/v1–11 support. No viewer source is included here. Paired
  proof and old-consumer rejection remain adoption gates, not current claims.
  The pilot's 2026-09-22 autonomous evidence-led direction authorizes this
  compatibility amendment and fixes without per-issue approval; no push or
  publication is authorized.
- Standalone framework branch/worktree `preserve-carry-across-graph-expansion`,
  based on committed main `e6a42c80e6dcc686c180b8a6d94037301c4213a5`;
  intended integration target `main`, only on later explicit authority.
  The pilot approved direct Git worktree creation after the launcher refused
  primary's unrelated untracked `docs/examples/v8-engine/`. That directory is
  untouched. This proposal-only bench has no launcher manifest entry or port
  allocation; no launcher behavior has been changed.
- Ratified by the pilot's “go on” on 2026-09-22 following proposal review.
  Re-ratified by the subsequent “go on” after the ordinary-chain scope conflict
  was presented; see `apply-findings.md` for the measured frozen twin.
  No solver fix, ADR promotion, integration, publication, or project adoption
  has occurred at this planning boundary. See `evidence.md`.
