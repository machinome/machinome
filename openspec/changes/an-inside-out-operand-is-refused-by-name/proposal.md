## Why

OCCT's solid classifier reads an inside-out solid, one whose faces are
oriented inward and whose signed volume is negative, as everything outside
it: a point ten metres away classifies inside. The B-rep engine consults
that classifier in two places and trusts it in both. ADR-142's false-empty
witness asks it whether a candidate lies inside both operands, so after an
empty common with an inside-out operand the first candidate inside the
other operand reads inside both, its neighbours agree, and the engine
refuses a common that was probably right as an inconsistency with a
claimed shared point. ADR-092's containment guard asks it whether a
representative point of each solid lies outside the other, and an
inside-out partner answers inside, so the guard declines to the Boolean,
which happens to be right. Thor keeps its `Art2MotorGear` and `Art4BodyBot`
inside out on purpose, because that is the orientation whose Booleans are
correct, and 13 of its 22 refused pairs are refusals of nothing
(`workflow/warts.md`, "Findings from investigation 4 of fix-warts-3",
7 October 2026; folded on 8 October into "The overlap question is asked of
a Boolean that is only needed at zero distance" as the precondition of any
classifier verdict). The pilot's ruling of 8 October 2026: an inside-out
operand is refused by name wherever the classifier would be consulted,
and never in the Boolean.

## What Changes

- **The guard refuses an inside-out operand by name.** When a common is
  empty and a solid of either operand has negative signed volume,
  `intersect_shapes` raises `BrepCommonVerificationError` naming that
  operand as inside out, with its signed volume, before any classifier is
  built; it does not claim a shared point.
- **The containment guard declines without consulting.** `mutually_outside`
  answers `False` for an operand holding an inside-out solid without
  loading a classifier, so the Boolean decides the pair as it does today.
- **The Boolean is untouched.** `intersect_shapes` and `fuse_shapes` run
  the common and the fusion on an inside-out operand exactly as before;
  a non-empty common is returned with its volume.
- ADR-142 gains an amendment recording that a classifier is never
  consulted on an inside-out solid.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `brep-engine`: "An empty common is verified before it is returned" gains
  the inside-out refusal; "Measurements are functions of the B-rep
  geometry" gains the containment guard's decline without a classifier.

## Impact

- `machinome/engine/brep.py`: one `_inside_out` test, used in
  `intersect_shapes` before the witness and in `mutually_outside` before the
  classifiers.
- `tests/test_brep_common_guard.py`: the reversed box beside a normal box,
  refused by name instead of as an inconsistency; the containment guard's
  decline without a classifier.
- `docs/adrs/TEST-FRAMEWORK/ADR-142-...md`: an amendment.
- `docs/project/changelog.rst`: one bullet under Unreleased.
- Thor: its 13 pairs become verification errors naming `Art4BodyBot`;
  still red, now for the stated reason. Validated read-only on its
  published STEP.
