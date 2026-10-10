## Context

Curta's `simulation/reverser_contact_trial.py` already uses ordinary `Bound` expressions to select absolute lower and upper axial planes on the held coordinate's side of each forbidden band. Its temporary `active_contact` tests one hard-coded phase window. The missing operation is only the angular 0/1 flag; changing the Bound/stop solver would change a proven mechanism without evidence. The native-cover experiment (`_build_checks/reverser-native-profile-cover-intersection-4035917.jsonl`, SHA-256 `f81c846514f0432cacf9cfcf0158c344dc0dabe6091173d073d5d82cd7182c5e`) contains four finite convex decompositions. Their source-native remainder is zero, but both standalone drum meshes have positive outside remainder. A later exploratory native-plus-mesh union (`_build_checks/reverser-native-and-mesh-profile-cover-4035917.jsonl`, SHA-256 `68ff82c84ff1faf157409b8a2e30708e71c63fd70d7c980f461a7b736c54577a`) adds 103, 98, 45 and 150 separately supplied projected mesh triangles to the four respective native piece sets. It still does not prove complete installed-print or axial-band coverage; no current profile is authorized as the installed contact law.

The bounded symbolic-SAT diagnostic `/tmp/curta_sat_bounded_materialization.py` (SHA-256 `feba57d109e421ceb42013fef43f6113014dd599359b4f25a8b6c6d0d9e30b8e`) took only 256 of the 633,552 pinion/nine-drum pairs and already made 49,833 unique graph nodes. The accepted expression graph and serializer are for scalar mechanics, not hundreds of thousands of polygon-pair formulas. Both Python and the independent viewer need to evaluate the same finite profile data without importing CAD into the browser.

## Goals / Non-Goals

**Goals:** Supply one compact pointwise contact flag inside the existing numeric Bound expression; retain the authored full profile data exactly, use rigid planar placement, stop early on AABB separation or the first SAT contact, and publish a version-gated portable table. Preserve old Bounds, program identities, documents, stop search and rates when the new primitive is absent.

**Non-Goals:** A general collision engine, arbitrary 3-D solids, continuous collision certification between sampled instants, volume measurement, a new constraint or stop kind, a mesh repair/clearance epsilon, approval of the current Curta covers, or a promise that a full revolution becomes interactive.

## Decisions

### 1. Public value and pointwise operation

The public import is `from machinome.simulation.profile import ConvexProfile, profile_overlap`; this pure-data module uses no CAD or viewer import and need not be eagerly re-exported from the simulation package. `ConvexProfile(polygons)` is immutable finite data: an ordered sequence of independently supplied convex polygon loops, each an ordered sequence of binary-float `(x,y)` coordinates. Each loop has at least three distinct vertices, CCW orientation, convexity with collinear consecutive edges allowed, and nonzero area. Validation rejects missing, nonfinite, zero-length edge, repeated vertex (including nonadjacent), self-crossing or non-convex data without repairing, welding or taking a hull. Exact binary-rational orientation, area and nonadjacent segment-intersection checks certify the supplied binary values; same-sign local turns alone do not admit a self-crossing pentagram. No CAD shape or mesh is stored in this value. An indexed representation may be used *on the wire* without inferring shared topology or changing any vertex coordinate.

`profile_overlap(left, right, left_angle, right_angle, *, left_xy=(0,0), right_xy=(0,0))` is numeric on numeric placements, including standalone probes and ordinary numeric bind-time range evaluation, and symbolic when a placement contains a motion token. It applies each degree angle about the profile's own origin, then its planar translation. A pair contacts if its transformed AABBs are not strictly separated and no edge normal of either polygon strictly separates their projections. Axes are unnormalized; a shared projection endpoint is contact. It returns exactly `1.0` for at least one contacting pair and `0.0` otherwise. Inputs and intermediate placements/projections must remain finite; an invalid evaluation refuses rather than returning a contact guess. The project retains its existing independent axial-window arithmetic in `Bound`; this operation knows no axial coordinate.

The origin of the value is the producer-declared data, not a runtime tessellation. The caller must separately prove that its cover contains the actual source and published installed prints before interpreting this conservative flag as mechanical contact.

### 2. Compact graph ownership and publication

An immutable profile reference is a leaf of the bound's native expression graph, carrying its data and content identity by reference rather than expanding polygon arithmetic. Arithmetic enclosing `profile_overlap` keeps the reference reachable. Only the running-Bound compiler admits this **symbolic** leaf and contact operation; unrelated symbolic pose, law, clocked or SCAD expression paths refuse it by name rather than emitting an unreadable function. This does not reject a plain numeric result that a numeric call already produced, or change ordinary numeric posing/range evaluation. Evaluation treats the leaf as a standing constant and the eight contact-call arguments in written order. The profile objects live with the expression/program; no process-global mutable registry can cross-contaminate two runs.

When a running program uses the primitive, the producer deduplicates profiles by canonical finite binary content, orders them deterministically, and publishes `program.profiles` as an array of `{points:[[x,y],...], polygons:[[index,...],...]}`. Flattening independently supplied loops into this indexed table preserves exact supplied coordinates and per-loop order; it does not assert shared topology. It rewrites each contact call to the scalar expression `profileOverlap(leftIndex,rightIndex,leftAngleDeg,leftTx,leftTy,rightAngleDeg,rightTx,rightTy)`; the first two arguments are literal nonnegative integer indices into that table, not motion expressions. The table and call participate in `Program.described()`/identity so a changed profile refuses old snapshots. The table is absent and the previous published bytes/identity stay unchanged when no contact call exists. A document with this feature declares running document version 13; an older viewer refuses it through the existing capability gate. The paired viewer validates the table, literal indices and finite operands at load/evaluation, scopes any parsed-expression cache to the owning program/table, and either extends its determined Bound path evaluator with the same operation or falls back *before* partial evaluation to the ordinary evaluator. It does not change the numeric span shape or `Run` algorithm.

The exact wire above is shared with the viewer's separate proposal; a cross-runtime fixture must pin one profile pair, touching, strict separation, near-contact, placement translation, two independent mounts with distinct tables and snapshot/replay. The published predicate call must remain a pointwise numeric term in the existing Bound's expression and binding table, never a top-level Boolean limit.

### 3. Numeric and solver boundary

The SAT test uses the project's strict-separation order: prepare *both complete transformed profiles* in declared polygon/vertex order and validate every transformed vertex and edge/axis **before any pair AABB early return**; then visit polygon pairs in table order, AABB first, then edge normals of left followed by right in loop order. A separating axis is one whose `max(left) < min(right)` or reverse is true. The two runtimes compute `theta = angle * 0.017453292519943295` (the binary64 constant `0x1.1df46a2529d39p-6`, one multiplication, no angle reduction), then `c = cos(theta)` and `s = sin(theta)`. Each supplied vertex is transformed as `rx = (c*x - s*y) + tx`, `ry = (s*x + c*y) + ty`, with those parentheses and operations in that order. Every input, theta, trig result, product, sum and placed coordinate must be finite. AABB min/max initialize from the first vertex and update in loop order with strict `<`/`>` (ties, including signed zero, retain the first value). For each transformed edge `u→v`, the unnormalized axis is `nx = u.y - v.y`, `ny = v.x - u.x`; a nonfinite or both-zero axis, including one collapsed by a huge finite translation, refuses the evaluation even if all profile pairs would later reject at AABB. Projection is `px = x*nx`, `py = y*ny`, `p = px+py` in that order, each step finite, with the same first/strict min/max fold. A finite binary64 angle cannot overflow when multiplied by this factor below one, so even a huge finite angle follows the same unreduced calculation with no arbitrary cutoff; later invalid geometry still refuses. A non-binary64 numeric input whose conversion cannot produce a finite binary64 operand is refused. The predicate's two exact return values are positive `1.0` for contact and positive `0.0` for strict separation. No normalization, epsilon, absolute volume or negative-volume reinterpretation is introduced. With a numeric 0/1 result, the existing Bound arithmetic still computes an *absolute axial limit* and existing `value - upper`/`lower - value` levels, 64 samples, bisection and group attribution remain the only stop semantics. A sampled path can miss a contact window narrower than its sampling interval; neither producer nor viewer may market this as swept collision detection.

The project's first installed-profile trial measured a real repeat cost: one
0→18° tick called the predicate 1,560 times (the paired numeric Bounds visit
780 identical pair inputs twice) and prepared profiles 3,120 times although
only 136 profile/angle/XY tuples were distinct by IEEE bits. A process-local
diagnostic successful-result memo reduced that one tick from 13.72 to 8.34
CPU seconds with identical ordered contact-input/result and full-bank bit
hashes; it was not adopted as a process-global cache. The production design
instead scopes two private bounded successful-value maps to one running
integration attempt (an advancing tick or a zero-duration current-tick
settlement): at most 1,024 pair results and 256 complete placed profiles,
LRU eviction,
cleared on every exit (including refusal), reset/replay and new Run. A key
uses exact immutable `ConvexProfile` object identity and the binary64 bits of
all finite builtin bool/int/float placement operands, including signed zero.
Custom objects, nonfinite or unrepresentable conversions and uncertain keys
bypass both maps and execute the original numeric path; key inspection never
invokes author `__float__`. A successful pair hit may skip a repeated pure
placement/SAT only after it was fully validated on an earlier call in the
same tick. On a pair miss each placement is independently looked up or fully
prepared before pairwise AABB; a placement is published only after complete
successful preparation and a pair only after a complete successful contact
decision. Errors and partial placements are never cached. Entry limits do
not truncate profiles or alter contact results; eviction merely recomputes.
There is no public cache control, change to sample count, Bound search, or
cross-program/mount reuse. Direct standalone numeric calls outside a running
tick remain uncached.

### 4. Project and release gates

The implementation must preserve the bounded red graph-materialization record, then test the compact operation on the actual four source profiles against their pinned native contact witnesses without claiming their current native-only covers are installation-safe. Capability acceptance additionally requires a bounded Curta local trial in which the flag selects the existing axial planes and produces stop, relief and snapshot/replay; the trial's limited phase window and source-profile scope must be stated. Producer/framework and viewer conformance must agree before either repo claims portable operation. **Separately**, production adoption requires complete native-plus-published-mesh installed-print and axial-band coverage and full operating admission; those project obligations are not a gate to archival/integration of a correctly scoped pointwise capability. An integrated framework capability is not a declaration that the Curta geometry is safe or the production restraint adopted.

Public `machinome.simulation.profile` docstrings and import tests will describe the numeric operation and its limits. `docs/project/status.rst` and the `Unreleased` section of `docs/project/changelog.rst` will name the current-source capability and paired v13 consumer; 0.7 release-record metadata, substitutions and teaching pages will remain 0.7-current without asserting that an index upload or remote push occurred. The strict docs build and structure checks will verify that split. A later publication/release pass, not this current-source cycle, will fold the new operation into `docs/reference/api.rst` and `docs/concepts/running.rst`.

## Risks / Trade-offs

- **A finite sample misses a narrow collision island** → state the existing 64-subinterval limit and require project-specific interval evidence; do not invent a continuous certificate.
- **Float trig/SAT differs at a near-tangent threshold between Python and JS** → fixed arithmetic/axis order, inclusive equality, cross-runtime near-contact fixtures and actual Curta stops; do not silently apply an epsilon. A material discrepancy returns to the design decision before implementation is accepted.
- **Large tables or pair counts remain slow despite avoiding graph blow-up** → benchmark the actual accepted profile data and bounded requests in both runtimes; AABB and first-contact exit keep point evaluation compact, not automatically real-time. If measured cost is unacceptable, revise the plan rather than changing `dt` or truncating data.
- **Malformed/hostile tables or stale cache context** → validate finite coordinates, polygon indices/orientation and literal table references; cache by the exact program/table identity or conservatively bypass; refuse invalid input before publishing or mounting.
- **Native-only cover is not an installed-print cover** → keep that result as exploratory evidence, never authorize Curta source adoption from it.

## Migration Plan

No old program is rewritten. Producer v13 publication occurs only when the contact operation is actually present; a nonmatching viewer refuses v13 through existing version checks. Rollback is to a document/model with no profile contact call, which retains the old running document and Bound semantics. No release, push or publication is part of this cycle.

## Open Questions

The project's final installed-print cover may have more points/pieces than the exploratory union. This change introduces **no arbitrary geometry-size ceiling** and never truncates a profile; benchmark the actual finite payload and use the current finite document/resource discipline. A measured resource problem would return to a separately justified plan rather than creating an unrecorded public limit. The project also must settle the exact installed-print axial band and tolerance-free safety proof before production adoption; this framework change does not decide it.
