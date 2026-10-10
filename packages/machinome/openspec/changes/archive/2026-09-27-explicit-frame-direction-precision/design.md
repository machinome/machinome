## Context

Architecture's frame synthesis and ADR-147 define normalized z, x projected
across z and normalized, then y=z×x. `frames.Frame.resolve` currently snaps
every resulting direction component near 0/1/-1. The public resolved-readout
contract repeats that universal snapping and returns the same cached objects
that mates compose. Curta's source-derived zero-positioning pin needs the
tiny components recorded in `workflow/warts.md`; strict moving-pose comparison
fails by 1.4452851360147179e-8 mm while geometric checks pass 6/6. Diagnostic
removal of frame snap makes unchanged comparisons pass, but removing it
globally would exceed the ratified scope.

The pilot explicitly ratified retaining precision only when BOTH directions
are supplied, not changing omitted-axis behavior. This is a public numeric
contract refinement, unlike the prior internal axis-angle correction.

## Goals / Non-Goals

Goals: retain explicit attachment triad precision through direct resolution,
realized-node readout and actual mate composition; preserve old omitted-axis
defaults/refusals and final mate snap; align public documentation and companion
Studio runtime API with the ratified distinction.

Non-goals: new public switches/arguments, changed frame syntax, altered
parallel/zero thresholds, symbolic frames, global joint/rotation snapping
changes, looser caller tests, new viewer fields or project-file edits.

## Decisions

### Both explicit directions select unsnapped normalization

Track whether z was actually supplied to the constructor, not whether its
numeric value differs from the default. Track x as stated when it is not None.
Explicit positional vectors count just as keyword vectors do. Prefer internal
construction-time argument-presence capture (for example before the existing
`__init__` defaults are filled) so its tuple default need not change. A private
presence mechanism retains the omitted-z distinction while
`Frame.z` and declaration repr/readout still expose the existing default
vector, never an internal sentinel. No new author-facing option is introduced.
Keep the documented and introspected public call shape/default semantics and
existing arity/refusals for Frame and its constructor; no sentinel or generic
argument-capture signature may leak as the public signature.

For that both-explicit path, normalize z without component snap, use this
unsnapped z for x projection, normalize x without component snap, and compute
y from the same directions without component snap. Preserve ordinary
floating-point normalization/projection, not an impossible exact-arithmetic
promise. Existing parallel/zero detection thresholds and named errors remain;
precision retention cannot bypass degeneracy validation.

`Frame(x=...)` with z omitted stays snapped. `Frame(z=..., x=None)` stays
snapped with principal-axis inference, including its present near-principal
acceptance; genuinely nonprincipal z without x remains refused. An explicitly
supplied default z with explicit x uses full precision. Parameter/formula or
callable vectors count as explicit based on declaration presence, not resolved
values. Resolution remains once per instance.

Alternatives rejected: remove snap globally (changes default inference), add a
precision flag (unnecessary new API), infer explicitness from vector equality
(cannot distinguish omitted default), or preserve precision only in display
(would leave actual mate pose incorrect).

### One resolved basis for readout and composition

Keep `_frame_arguments` and `resolved_frames` returning the actual cached
ResolvedFrame objects. Both public direct `Frame.resolve` and node realization
use the same rule. No second basis or recomputation is allowed. Tests must
exercise composition with nonidentity endpoints: a same-frame identity pair
could hide snapping through cancellation. Compare independently calculated
frame matrices and physical bases, allowing existing final rotation snap and
normal floating-point error; do not demand machine-epsilon equality where
documented final snap intentionally changes an operation.

Final `mates._axis_angle` angle/axis snap remains exactly `1e-9`; translations
retain existing arithmetic. Joint axis normalization and every other snap rule
remain out of scope. The stabilized prior axis-angle implementation is reused,
not reopened.

A fresh-freedom mate's generated joint continues to normalize/snap its axis
independently under the existing Joint contract. Retaining Frame precision does
not promise an unsnapped joint axis or unsnapped final Rotation components.
Existing-joint attachment preserves the original joint axis as before.

### Documentation and ownership follow the public contract

Update Frame/ResolvedFrame public docstrings and the universal-snap wording in
`docs/concepts/joints.rst`, using write-the-manual before reader-facing edits.
Preserve practical examples and public default signatures. Root owns the
separate Studio companion worktree `machinome-studio/WTs/explicit-frame-precision-api`
at base `a42d45c4b4cee3aa9f8ee2a490c56007af973dec`; its API skill's Frame and
resolved-readout passages must state the same distinction. Never edit Studio
inside this framework cycle. No schema/viewer change follows from this numeric
contract; changed operation values are ordinary existing fields.

## Risks / Trade-offs

- Presence tracking can leak sentinel or alter accepted positional calls →
  pin defaults, declaration arguments/repr, positional/keyword equivalence and
  explicit-default versus omitted-default tests.
- Projection might still use a snapped z → independently assert all three
  directions, orthogonality and the actual composed nonidentity pose.
- Omitted-x inference may broaden or break → retain current near-principal
  snap, all six principal defaults, nonprincipal and degeneracy refusals.
- More precise vectors may change numeric types from ints to floats → document
  plain numeric components, not universal integer snap, and retain equivalent
  exact-principal values without requiring float/int identity on precise paths.

## Migration Plan

After root planning review/commit, another Sol implements red-first. No caller
syntax migration is required: authors already explicitly supplying both
directions receive the ratified precision behavior; omitted-axis callers keep
their old path. Root coordinates unchanged Curta red/green evidence and owns
pending project candidate files. Root adversarial review gates sync/archive.
Only after implementation is verified, record ADR disposition and any accepted
decision/architecture update proportional to this public numeric distinction.
Do not write an accepted ADR during planning. Preserve the two-commit cycle;
local FF/cleanup authority is root-owned, never inferred as push authority.

## Open Questions

None within ratified scope. In particular, explicit x with omitted z is NOT
included; any broader precision rule must return to the pilot first.
