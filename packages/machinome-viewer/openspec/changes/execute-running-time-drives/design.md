## Context

The pilot asked to implement viewer support after Astrarium's verified migration.
This consumes framework ADR-133 and the v10 export contract at `0ce71cd` rather
than designing a new authoring interface. Viewer ADR-045 (shared engine/worker),
ADR-047 (producer corpus), and ADR-067 (narrow play topology) remain in force.

## Goals / Non-Goals

Goals: actual retained time-drive execution, independent admission/stop paths,
strict document refusals, legacy parity, producer-corpus parity and real-browser
Astrarium operation. No fabricated controls, physical clock state or startup
rate command. No expanded play topology, dynamics engine, framework import,
historical reconstruction, push or release.

## Decisions

### Validate and load the published mapping

Load ordered `program.time_drives` entries keyed by `@time:<edge-index>` against
the original flattened edge list, before contracting any selector blocks. Require
v10, a nonempty mapping, unique ascending valid indices and IDs, clock `time`,
source-only time on mapped law edges, and no unlisted time-reading edge. Clock
and reserved admission IDs cannot be bank values, intermediates or drivers.
Source candidates may name the declared independent admissions as well as inputs.
Malformed documents fail at load, with the source URL and offending field.

### Reuse the retained-motion algorithm with independent local time paths

Each advancing tick admits `dt` per time-drive ID beside commanded input travel.
Tick-local values start every relation at global elapsed seconds; after a stop,
that relation holds its admitted endpoint for the tick remainder. The next tick
rebases to global time without adding the skipped interval. Zero-duration input
commands admit no time. Keep time outside the bank, snapshots and operator table.

Edge evaluation receives its mapped relation's local clock value and delta;
all existing jump subtraction, self-read and block machinery keeps its meaning.
Stop candidates include time-drive IDs, but stop records separate real `inputs`
from optional nonempty `time_drives`. The finite segment limit counts all moving
admissions. Only real commands retire; declarative drives retry next tick.

Time-driven downstream stop searches replay the determining prefix from its
original admitted sources. Dividing by a downstream edge's endpoint delta would
misplace a stop reached through a nonlinear upstream law. Prefix evaluation and
truncated commit must use the same arithmetic, within existing published limits.
No-time-drive programs keep their existing execution path and record shape.

### One engine, existing browser transport

Worker and in-thread execution use the same engine. Existing play/step/pause and
save/restore/reset operate it; mounting remains paused by default. Copy the
producer corpus byte for byte into this repository and replay every recorded
step using its own tolerance and exact discrete fields. Add malformed-document
tests, atomic-failure and nonlinear-stop checks, and Astrarium browser acceptance
in worker and fallback modes using a committed project export.

### Distribution and documentation

Declare API 23 and document versions 1–10 in the existing single metadata source,
rebuild the single bundle, update compatibility and run/stop documentation. Keep
package 0.2.0 unreleased. Record the extension in an accepted viewer ADR and sync
implemented requirements; do not rewrite historical API claims in old records.

## Risks / Trade-offs

- Shared time could couple unrelated stops → independent admissions and corpus.
- Selector block flattening could lose mapping → attach mapping before grouping.
- Nonlinear localization could snap only a follower → original-source replay.
- Regression in older runs → complete existing corpus and test suites, unchanged
  old fixtures and no tolerance widening.
- Python success could mask browser failure → real browser, both transports,
  actual Astrarium history and inspected screenshot.

## Migration Plan

Commit the scoped planning record under the pilot's implementation instruction;
implement red-first, validate, record evidence and commit the completed increment.
Existing unrelated changes remain untouched. No upstream integration or release
is required: this is the viewer's own independent repository. An unsuccessful
implementation remains clearly incomplete and does not advertise support.

## Open Questions

No new authoring decision is needed: the producer contract is accepted. Any
incompatibility revealed by replay is investigated before claiming completion;
do not silently alter the producer fixture or semantics.
