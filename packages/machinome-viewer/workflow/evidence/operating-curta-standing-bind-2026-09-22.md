# OperatingCurta standing Bound bind cache: exact paired evidence

The viewer-owned `cache-standing-bound-bind` cycle originates in the
OperatingCurta's actual default-`dt=1/240` crank. Before this change,
`searchedConstraint` discarded a successful `ExpressionPath` after every
Bound search. On the pinned 7586002 export, the first 48 ticks created
73,517 first binds; 71,675 repeated the same graph root, moving-name set and
bit-exact finite standing leaf values. The largest bound had 63,252 DAG
nodes, of which 61,630 stood, and repeated 47 times. This justified a
Run-local, per-constraint successful-path cache rather than a scope-object
identity cache (the scope is rebuilt on every sample).

The frozen manifest SHA256 was
`c36432b1080387eeb40234532f516a9ae05f8a9822fd3f47f44ffbbb42f889d1`.
A later, production pre-ball export was pinned separately at SHA256
`03099125a8642ee28c9dcfe73e2c6a82c3538794ba36ba0300eb738d5049ede9`.
Both comparisons used the same first 48 of 480 default ticks after setting
selector 1, on reserved CPU 15, without WebGL. The production baseline with
cache disabled took **20.0603 process-CPU seconds**; the candidate took
**17.1970 seconds** (14.3% less), with 4,027,665 fewer node resolutions.
Its 6,240 ordered Bound samples had identical IEEE-754 argument/result trace
SHA256 `56a038987bb74b125dc7161e6aa9946fbe2a158c61dcee45b3511c9d3bfb3a0d`;
the 213-coordinate bank digest was identical at
`c46fbef17ae093d94f00b576fd371fbe6f920bf5f95302e1ffb81c7da6869cc2`.
Both admitted 36°. The frozen-758 pair also matched all 6,240 sample bits
(`8d218d7462b0bea40a7665cb00b73155aaa7c915753b3fe8d9b3a29df509d69a`)
and the same bank digest; its paired CPU observations were 17.545 baseline
versus 15.594 seconds candidate, with host contention affecting later repeats.
These are measured prefixes, not complete-turn or interactive-tempo claims.

Red-first tests cover first-sample moving evaluation, changed standing values
and presence, signed zero, nonfinite scope, unsupported paths, a failed search,
competing standing/moving domain errors, `Math.random`, moving-set and
expression-generation changes, restore and independent runs. The exact
sample path retains existing operators, order, subdivisions and bisection.
The path is retained only after search success and is bounded to one entry
per constraint per Run; reset/restore and last-run lifetime release it. A
read-only peer review found no blocking error/lifetime issue.

The production export was also exercised as its **actual auto-mounted
standalone page**, not through a test remount or private handle. With candidate
bundle SHA256 `0d16382708d1672904572bf8f20277c5af60ed0ba8befc1c6cd53723423fdf84`,
the DOM exposed 24 input rows and the one instruction for its 25 physical
controls; a real canvas pointer gesture selected `digit_1` from 0 to 2 and
the public readout reported `completed`, with no page errors. The inspected
[screenshot](operating-curta-standing-bind-standalone-2026-09-22.png) shows
the assembled machine and terminal selector. This check took 151.08 wall
seconds with browser processes pinned to one CPU; it proves control and
terminal state, not interactive speed, all 25 gestures, or a full revolution.
The auto-mounted page has no public 213-bank enumeration surface; the exact
bank/trace proof above is the separate no-WebGL runtime check.

Typecheck and widget build passed; viewer-facing Python running-document and
widget E2E suites passed **49/49** with the candidate bundle. A first broad
Vitest run exited **1** with 1,476 tests passed and one environment-sensitive
quiet ShiftedCarry throughput floor missed (2,952 versus required >3,000
ticks/s) while other host jobs ran. That same test passed in isolation at
3,136 ticks/s. Preserve the broad process outcome as failed; the subsequent
full-suite rerun on reserved CPU 15 exited **0**, with **55/55 files and
1,476/1,476 tests passing** in 119.72 wall seconds, including all Curta source
timing and cost floors. No cost threshold, tick size, Bound sample or
mechanical tolerance was changed.

The reader-facing changelog keeps the 0.7.0 release entry intact and records
this source-only correction under Unreleased with API 24 unchanged. The
documentation structure suite passed 7/7, strict Sphinx HTML built without
warnings, and the browser documentation review passed 14 pages, 204 local
links, desktop/mobile layouts, search, and both running reference examples
with zero browser errors. No manual teaching page or public API was changed.
