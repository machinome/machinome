## Why

Operating Curta at project checkpoint `c76f230` exposes a framework failure:
after withdrawing a selector at crank 120°, an immediate request to 840°
raises `StopInvariantError` instead of stopping at the first lockout contact,
125.22°. The identical short or timed request stops correctly; the long
request's later return to an open window must not erase the earlier contact.

## What Changes

- Determine which admissions push a moving-read constraint at its located
  contact, instead of comparing clearance only over the entire remaining
  request. Preserve the existing search bracket as the evidence of contact.
- Preserve atomic commits, own-coordinate freezing, independent time-drive
  admissions, inclusive limits, relief, replay and the existing search limits.
- Add regression and producer-conformance evidence for periodic requests whose
  endpoints conceal an intermediate obstruction, then validate the actual
  Curta source-backed reproduction and measured five-flat candidate.
- Amend ADR-113's explicit whole-stretch pushing decision only after the
  implementation proves the replacement. No new public declaration or document
  field is proposed; this is a correction to running constraint execution.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: moving-read constraints identify pushing admissions at the
  encountered contact, including long periodic requests that end free again.
- `export`: producer conformance evidence must cover a periodic constraint
  stopping such a request, so the independent viewer can test the correction.

## Impact

Primary implementation scope is `machinome/simulation/run.py`, its stop tests,
running fixtures and corpus generator. Update architecture, the relevant ADR
decision and user-facing search-limit explanation as warranted by the final
implementation. No CAD dependencies, source geometry, Curta production law,
public API or serialization format changes are included.

The browser executor belongs to the independent `machinome-viewer` repository.
This framework cycle supplies producer evidence, not a viewer implementation
or a claim of browser parity. Any required viewer correction needs its own
authorized repository cycle before operating Curta is declared complete.
