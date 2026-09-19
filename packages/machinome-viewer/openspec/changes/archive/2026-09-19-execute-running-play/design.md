## Context

Pilot ratification on 2026-09-19 explicitly includes the independent viewer companion to framework change `unilateral-running-pickup`. This standalone viewer cycle starts from clean main `2912006dd4864bc25aa4b7c0e11cd2e457dd5836`; no integration, push, publication, or release is implied.

The framework publishes a version-9 running program when any edge has this exact shape: `kind: "play"`, `needs: [source, retained]`, `gives: [retained]`, `description`, `stated_by`, finite `low`, and finite `high`. Its endpoint rule is `y' = max(x' - high, min(y, x' - low))`. Play edges are one linear chain rooted at one driver, with no play fan-out. The ordinary bank is all history.

The viewer already mirrors the running engine in `src/run/`, validates documents before execution, runs the same engine in a worker or in-thread, and replays the framework's corpus copied byte-for-byte. The implementation must extend those boundaries rather than create a browser-only controller.

## Goals / Non-Goals

**Goals:**

- Strictly load and execute the producer's version-9 play edge.
- Match single-edge and chained play, reversal, stops, commands, snapshots, reset, and rollback.
- Preserve documents and behavior for versions 1 through 8.
- Advertise the new capability before a host mounts a document.

**Non-Goals:**

- Inferring play from version-6 self-read comparisons.
- Accepting arbitrary reversing source graphs, branching play, or malformed producer shapes.
- A general contact/physics engine or any epsilon around contact.
- Regenerating the producer corpus in this repository.

## Decisions

### Validate the producer's decision at load

`loadProgram` admits `play` only with two distinct declared bank ids in `needs`, exactly one `gives` equal to the second need, finite `low < high`, and an initially retained value in `[source-high, source-low]`. It derives the play subgraph and refuses a source that is neither a driver nor the preceding play output, cycles, multiple writers, and play fan-out. The errors name the edge and failed field. Existing edge kinds and self-read derivation are untouched.

### Add a dedicated edge, not an expression convention

The loaded edge carries play metadata and its ordinary program identity. Propagation projects the source endpoint against the retained start using the published formula. A follower inside clearance contributes exact zero. A chain is evaluated in published program order. The implementation lives in the reusable running engine; worker and in-thread modes therefore share it.

### Replay the original input prefix for a stop

The existing stop locator scales immediate-source deltas. That is insufficient through play: with two gaps of 10, `x:0→100` produces `y=90,z=80`, while a high stop `z=20` belongs at `x=40,y=30,z=20`, not at one third of the request. Candidate evaluation therefore replays the full program prefix from the original driver at the candidate fraction before judging a play-chain follower. The commit uses that same replayed prefix. A released stationary follower is not pushing and cannot block its source. Refusal keeps bank, tick, records and posed tree unchanged while attempted commands retire `refused` with no newly admitted travel, preserving the engine's existing transaction.

### Parity is producer-owned data

After the framework implementer regenerates `tests/running-corpus.json`, copy those exact bytes once to `src/running-corpus.json`. Extend the viewer's coverage census for the producer's named play features, never edit expected values locally, and add focused unit tests for malformed documents and algorithmic hazards not guaranteed by the corpus.

### Capability declarations move together

Add document version 9 and raise viewer API 21 to 22 in `widget/package.json`, the source for both the bundle and Python `describe`. Version 9 with no play still loads according to content, like versions 6 and 7; malformed play never becomes a version-number inference. README and changelog state 0.2.0 remains unreleased.

## Risks / Trade-offs

- **A superficially correct endpoint implementation clips cascades wrongly.** → Pin the `40/30/20` stop and original-input replay.
- **Framework and viewer schemas drift while developed concurrently.** → Coordinate exact keys and corpus case names with the framework implementer; consume only its planning commit and regenerated fixture.
- **The corpus can omit a critical branch.** → Keep explicit coverage guards and focused malformed, reversal, release-side, and stop tests.
- **Worker-only bugs escape in-thread parity.** → Retain protocol/runtime tests and a real mounted-page smoke using a version-9 document.
- **A stale bundle advertises the wrong versions.** → Existing currency checks rebuild from the single package declaration; test both JS and Python reports.
