## Context

A running root can render and compile a valid square-root law at `feed=0`, then receive a command to `feed=0.2` where that law's numeric graph evaluation raises `ValueError: math domain error`. `Run.integrate` stages the bank and records, so they stand; its typed refusal handler does not see that raw error, leaving the command active and its input owned. At the same law-result seam, a valid `feed*feed` law at `feed=1e308` returns infinity, which the producer banks and records. Both violate the running-tick failure/command-retirement contract in the simulation spec and ADR-105. An invalid authored default fails the rest render and cannot publish a program, so the executable paths begin at valid rest.

## Goals / Non-Goals

**Goals:**

- Convert a numeric domain `ValueError` or non-finite numeric result from an already-performed compiled running-law evaluation into the existing `UnsupportedLaw` path, naming the relation, the author class, and driven coordinate.
- Let the current `Run.integrate` transaction retire commands that moved in the failing tick while preserving bank, tick, tree, record, earlier successful ticks and admitted travel.
- Preserve evaluation order and normal finite arithmetic, including a legal square-root boundary.

**Non-Goals:**

- Catching every `ValueError` in integration, swallowing unrelated bound, loader, pose or author errors; pre-evaluating future states; changing an authored declaration or public method; changing export schema or corpus by hand.
- Repairing the independent viewer in this repository, or treating its invalid-start synthetic document as producer-exportable.

## Decisions

1. Handle domain errors and non-finite values at the compiled running-law numeric-evaluation seam, where the relation and target are known, rather than adding `ValueError` to `Run.integrate`'s broad catch or checking the whole bank afterward. Preserve existing typed `UnsupportedLaw` and other exceptions and their first-error order. Inspect only the graph result already computed; no additional evaluation point or tolerance is introduced.
2. Reuse `UnsupportedLaw` and the existing integration catch so command retirement and atomic staging take their established path. The exception message identifies the relation, its `stated_by` class, driven coordinate, and the underlying numeric failure without promising that all expression errors are the same kind.
3. Keep the viewer companion as a distinct cycle. After both sides are corrected, compare their observable bank, tick, command status and refusal names for this probe before widening any producer-generated corpus coverage; no fixture is hand-edited here.

## Risks / Trade-offs

- **[Several law evaluators]** Direct, jumping, self-read and traced paths reach graph evaluations through different helpers. → Audit the actual compiled-law evaluation paths and guard only those proven to surface a numeric domain error or non-finite law value; test direct domain and overflow paths red first and preserve existing error-order tests.
- **[Overbroad exception conversion]** A global `except ValueError` could mislabel a Bound or pose refusal. → Keep conversion local to law evaluation and assert an unrelated refusal retains its existing type/message.
- **[Multi-tick state]** Treating the whole command as atomic would erase valid earlier ticks. → Assert only the failing tick stands, while the command reports earlier admitted travel and retires `refused`.

## Migration Plan

No migration. Run focused running tests, the broader simulation suite and a representative public `Sim` probe; sync the delta spec and archive only after ratified implementation. Rollback is the isolated implementation commit.

## Open Questions

No interface decision is requested. If a path raises a different error kind or a domain failure occurs outside law evaluation, record it separately for review rather than adding a broad catch.
