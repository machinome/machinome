# finite-convex-profile-contact Specification

## Purpose

Validate and evaluate finite producer-supplied planar convex profiles as pointwise numeric contact values in running Bounds.

## Requirements

### Requirement: A serialized finite convex profile is validated before running

The viewer SHALL load the producer's version-13 ordered profile table as finite planar points and indexed simple convex polygons, preserving their exact published values and order. It SHALL refuse a missing or malformed table, nonfinite coordinate, invalid index, repeated vertex, zero edge, adjacent backtrack, self-intersection, zero-area loop, or nonconvex loop. It SHALL validate the producer's finite binary coordinates without a floating epsilon, and SHALL accept every well-formed producer-valid loop, including collinear and near-collinear corners. It SHALL neither infer a hull nor silently repair the data.

#### Scenario: Curta cover table loads without scalar expansion
- **WHEN** a producer document carries the finite Curta pinion and drum polygons as table data
- **THEN** the viewer loads their ordered points and polygons without generating a scalar expression node for every polygon pair

#### Scenario: Malformed or self-crossing geometry refuses
- **WHEN** a profile contains a nonfinite point, invalid polygon index, repeated vertex, zero-length or backtracking edge, a concave corner, or a crossing such as a pentagram whose local turns are positive
- **THEN** loading refuses it by name before the machine can run

#### Scenario: Valid near-collinear geometry is accepted
- **WHEN** a producer-valid simple convex loop has exact-binary positive area and a collinear or near-collinear corner
- **THEN** the viewer accepts its supplied values without welding or an epsilon-based convexity decision

### Requirement: A pointwise rigid profile call returns inclusive contact

For a well-formed `profileOverlap` call with literal valid profile indices and finite rigid XY angle and translation operands, the viewer SHALL return numeric `+1.0` when any placed polygon pair overlaps or touches and numeric `+0.0` only when all pairs are strictly separated. Its degree conversion (`angle * 0.017453292519943295` without explicit reduction), trig evaluation, parenthesized rotate-then-translate products/sums, first/strict world-AABB extrema, transformed-edge SAT axes, ordered projection products/sums, and first/strict projection extrema SHALL reproduce the producer's serialized numeric corpus. A nonfinite intermediate, transformed coordinate or projection, or both-zero world axis SHALL refuse rather than guess. It SHALL check transformed edges for collapse before disjoint-pair AABB early return, so an invalid placement cannot be masked by a distant profile. It SHALL use strict separation, with no clearance epsilon, overlap volume, symmetry inference or continuous-contact claim.

#### Scenario: Overlap, touch and strict gap
- **WHEN** two placed finite convex polygons overlap, share only a projection boundary, or have a strict separating gap
- **THEN** the call returns `1`, `1`, or `0`, respectively

#### Scenario: Any pair in a finite union
- **WHEN** two profiles contain several ordered polygons and only one polygon pair touches or overlaps
- **THEN** the call returns `1` without requiring every pair to be evaluated

#### Scenario: Invalid call or placement
- **WHEN** a call has a nonliteral, negative or out-of-range table index, wrong arity, unsupported reachability, or a placement operand becomes nonfinite
- **THEN** loading or the current tick refuses by name without treating the value as clearance or committing a partial bank

#### Scenario: Huge finite angle and transformed overflow
- **WHEN** a finite but very large placement angle or coordinate causes a nonfinite intermediate, collapsed edge, or producer-defined representability failure during transform or projection
- **THEN** the current tick refuses rather than classifying the profiles as separated or in contact

#### Scenario: Huge but representable angle
- **WHEN** a finite large angle and all its declared intermediate calculations remain finite and the placed polygon remains nondegenerate
- **THEN** the viewer evaluates the same unreduced ordered transform as the producer rather than applying an arbitrary angle cutoff

### Requirement: Profile contact composes with existing numeric running bounds

The viewer SHALL evaluate a profile call reachable from a running Bound expression, including through a document binding, in that document's own table context. The Bound SHALL still yield an absolute numeric coordinate limit; the viewer SHALL retain its existing samples, search, admission, first-error, committed-bank, snapshot and replay rules. It SHALL NOT create a new span or solver operation from the predicate.

#### Scenario: Curta axial band selection
- **WHEN** a Curta running Bound uses the 0/1 angular contact flag to select its authored axial low or high plane
- **THEN** the ordinary numeric Bound stops, relief and replay use those planes and match the producer's paired corpus

#### Scenario: Bound binding and optimized path
- **WHEN** a Bound reads an alias of a profile call and the determined-bound fast path cannot evaluate that call in the same document context
- **THEN** it uses ordinary evaluation before partial fast-path work, preserving the first error and the Bound result

### Requirement: Repeated profile work preserves observable evaluation

The viewer MAY reuse successful identical placed profiles and profile-contact results only within one running integration attempt, using exact finite IEEE-754 numeric placement bits and loaded-profile identity, with bounded private storage. Such reuse SHALL preserve operand evaluation order, signed-zero distinction, every running Bound sample, first error, atomic refusal, bank, stop, restore and replay. It SHALL NOT cache a failure, publish a partial placement from a failed pair, retain results across attempts/ticks/mounts, or introduce a public input-size limit. If either placement has a nonfinite or coercing operand, the whole predicate call SHALL use the original uncached evaluation path.

#### Scenario: Repeated paired Bounds
- **WHEN** two Curta running Bounds evaluate the same valid contact placements and pair more than once in a tick
- **THEN** successful deterministic preparation may be reused while their ordered bound samples and final bank remain unchanged

#### Scenario: Failed second placement and later retry
- **WHEN** the left placement succeeds but the right placement fails, and a later attempt supplies valid coordinates
- **THEN** no left preparation or pair result from the failed call is available to the later attempt, which produces the same first error or successful result as uncached evaluation

#### Scenario: Independent attempts and mounts
- **WHEN** an attempt ends, a snapshot is restored, or another document with different profile data runs the same expression and bank values
- **THEN** no prior attempt's cached placement or contact result is reused
