## Why

The complex Vault with Combination Lock (checkpoint `78d4ceb`) needs a running dial to collect each wheel at either contact flank, release it immediately on reversal, and retain it while crossing the clearance.  ADR-121's admitted positional self-read gate instead keeps an inclusive comparison engaged while driver and follower move together, so it pulls the wheel on reversal; strict comparisons and smaller `dt` do not supply a reliable workaround.

This is a missing running-mechanism capability, not a regression in ADR-121.  The project must keep `Time.running()` and must not duplicate the wheel bank in project or host state.

## What Changes

- Add one explicit running-only play/backlash law for a source coordinate and the retained coordinate it drives.  Given ordered contact offsets `low < high`, it projects the retained value to `max(source - high, min(retained, source - low))`, which states unilateral pickup at either flank and release on reversal without a tolerance.
- Admit the law only where its path is answerable exactly: one banked driven coordinate reads itself, and its source is either a run-owned driver or a coordinate produced by another play law.  Refuse unsupported or potentially reversing source paths at compile time rather than integrating their net displacement.
- Preserve every existing `drives(..., law=...)` and ADR-121 self-read meaning byte-for-byte.  This is opt-in behavior, not a changed interpretation of comparisons.
- Publish enough explicit program data for another runtime to execute the play law and raise the lowest document version carrying one to version 9.  Older consumers therefore refuse it by version instead of silently applying version-6 self-read semantics.
- Prove the originating Vault path against an independent play-operator oracle, including both directions, reversal at exact and non-integer contacts, split commands, cadence, a three-wheel cascade, snapshot/restore/reset, stops, and atomic refusal.  Extend the running conformance corpus with the new semantics.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `couplings`: add the explicit play/backlash law declaration and its structural refusals.
- `simulation`: integrate a supported play chain under `Time.running()` with deterministic contact, release, retention, stops, and state lifecycle behavior.
- `export`: publish play-law semantics as document version 9 and extend the cross-runtime conformance contract.

## Impact

The public coupling/simulation API gains one opt-in law declaration.  Compilation and running execution gain a narrow play edge; serializers and the running corpus gain its explicit representation.  Existing models and documents are unchanged.  `machinome-viewer` does not yet accept version 9 and is an independent AGPL repository, so browser execution of a model using this capability requires a separate viewer OpenSpec cycle; this framework change neither edits nor silently assumes that consumer work.
