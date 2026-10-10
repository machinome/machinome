## Why

The Curta Type I 3x operating simulation at project checkpoint `1aaad6c`
exposes a violation of ADR-105: when nested joints share a local coordinate
name, delivery of the run's qualified bank can bind a descendant to an
ancestor's retained value, leaving the bank, joint and rendered pose in
disagreement. The minimal three-level reproduction is insertion-order
dependent, so snapshots cannot yet be trusted to pose nested mechanisms.

## What Changes

- Deliver each qualified retained joint coordinate only to the node that owns
  it, including single-coordinate, multi-coordinate, class-declared and
  site-declared joints.
- Make full-bank rebinding independent of mapping insertion order while
  preserving supported bare driver propagation, global `time`, qualified-name
  validation, ambiguity refusals and run ownership.
- Prove parent and child movement, repeated rebinding, snapshot restore and
  reset keep every retained bank coordinate, bound joint and rendered pose in
  agreement.
- Preserve symbolic export and restore the live numeric pose after document
  publication; change no export schema or document version.
- Re-run the unchanged Curta carriage-shift and clearing geometry acceptance,
  including visual evidence, against the corrected framework.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `kinematics`: Clarify that a qualified joint-coordinate entry stops at its
  owner while an originally bare name retains ambiguity discovery and rollback.
- `simulation`: Clarify that delivery of the run's qualified bank is scoped by
  coordinate owner and is independent of bank mapping order, including during
  rebinding, restore and reset.

## Impact

The correction is confined to state delivery in `machinome/node/assembly.py`
and focused simulation/export regression coverage. It restores the existing
ADR-105 contract and changes no public API, architecture, dependency, document
schema or viewer behavior. Originating evidence is the Curta Type I 3x project
checkpoint `1aaad6c`; the framework cycle is based on
`c62319e1974b88d8cfd2dd13fd205c7bf2533991`.
