## Why

Dragon R1's suspension repeats a driven four-bar closure and output-link
bearings; Strandbeest's Jansen legs construct two four-bar closures about the
same crank. Both need the same planar geometry in different source frames.

## What Changes

- Add `four_bar_pose(angle, crank_pivot, rocker_pivot, crank_length,
  coupler_length, rocker_length, side=1)` returning moving pivots and bearings.
- Preserve explicit circle-side selection and numeric/deferred arithmetic,
  including the constructed, unnormalized rocker bearing Dragon already uses.
- Migrate both projects with Sol agents and require independent legacy parity,
  CAD contracts, builds and fresh inspected images before local integration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: a driven planar four-bar pose with explicit closure branch.

## Impact

Independent mechanics linkages module, exports, tests, manual and distribution
smoke. Separate Dragon R1 and Strandbeest consumer commits, including a
mechanics dependency declaration where a consumer first imports it. The
mechanics package itself gains no new runtime dependency. No framework change,
general constraint solver, collision claim or publication.
Pilot waived per-cycle ratification; empirical evidence gates integration.
