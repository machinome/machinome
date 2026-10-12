# Finite convex-profile contact reader: implementation evidence

## Scope and provenance

This viewer cycle reads the framework's v13 pointwise `profileOverlap` call as
a numeric value inside an existing running Bound. It does not add a span kind,
change search samples or claim continuous/installed-print contact proof. The
originating Curta project's native-plus-mesh exploratory cover is
`_build_checks/reverser-native-and-mesh-profile-cover-4035917.jsonl`, SHA-256
`68ff82c84ff1faf157409b8a2e30708e71c63fd70d7c980f461a7b736c54577a`.
Its eight source-pose witnesses are SHA-256
`6b2f0848a51abb9aff1cdc90ec4b2d13f8f904e2b25f9e4ea817647608b13b66`.
The earlier native-only cover is not a complete installed-print witness.

The producer's exact v13 document fixture, outcome fixture and numeric corpus
were copied byte-for-byte into `widget/src/run/` and have respective SHA-256
`c13d22ed74de6b30dc256d4ec4cd5665e26ae3a8f4ae06feeffc2c44b5c723d0`,
`556da1c4afd0e5bc3501605f45ee8ed9c1815d26f0d7b124dd5aaca83bdac1c8`, and
`6d381e9c31c8633e4f3618b2ea0506a53638a2551c032760271503cb0ab92483`.
The framework test regenerates the document and pins its exact wire. The
viewer tests compare the one-tick stop, admitted IEEE bits, complete small bank,
stop record and snapshot replay against that producer outcome, and execute the
whole numeric/malformed corpus. Independent numeric evaluation of the four
complete Curta source profiles (694/689/306/1222 polygon loops) agreed on all
eight source-pose contact flags: one-tooth 0,0,1,0 and nine-tooth 1,0,1,0.

## Measured installed-trial integration

A read-only no-mesh document from the unadopted installed Curta contact trial
was pinned at `/tmp/curta-installed-profile-v13.json`, SHA-256
`2d62786b64c4f8f113fbd6224a1dca49b12bbfad0e37c8130c2b0840d208eb34`,
program identity `bfba823b90afb1b07a8759175ad7749675fbdf04288fcb74ae940847cc6c87e8`.
It is an eight-profile component fixture, not a production export. The
separate producer one-tick oracle at
`/tmp/curta-installed-profile-one-tick-bank.json` has SHA-256
`1872b5a9ca242df97d5f86f0050f7e1b94144b9f55c019a3db58ed1a7c50cc2e`.
The opt-in test reads both paths with `CURTA_INSTALLED_PROFILE_DOCUMENT` and
`CURTA_INSTALLED_PROFILE_ORACLE`; it does not depend on the project at test
collection time.

This document has eight indexed profile tables and is 3,889,917 serialized
bytes. Each of the two direct Curta contact expressions has 23 unique scalar
nodes; the earlier capped 256-pair symbolic diagnostic had 49,833 unique
nodes and was not a complete 633,552-pair contact. The loaded profile table
is program-owned, and the run cache has fixed entry caps; these are size and
retention bounds, not a measured resident-heap ceiling. Finite AABB rejection
precedes SAT pair work, after all placement validation.

With `Run(dt=.1)`, `crank_rotation` to 18 over .1 s, one integration attempt
made 1,560 predicate calls but only 780 distinct exact pair keys. The 3,120
potential placements held only 136 distinct exact profile/angle/XY keys.
The private per-attempt successful-value cache (pair cap 1,024, placement cap
256) recorded 780 pair hits and 1,424 placement hits, so only 136 placements
were executed. The same pinned CPU-13 test/harness, with caching disabled only
inside the diagnostic mock, measured these process CPU pairs in seconds:

| Instrumentation | Uncached | Cached | Reduction |
| --- | ---: | ---: | ---: |
| Contact+bank trace | 2.298 | 1.770 | 23.0% |
| Contact+bank trace, later host window | 1.814 | 1.577 | 13.1% |

These are bounded no-WebGL component measurements under other host load, not
interactive frame-rate claims. Every pair made the same 1,560 ordered contact
input/result bit trace, SHA-256 `b22c81a32434b60cd49696cf2969dfa470c1902d21a069d9d00955604aea231a`,
the same 4,322 ordered numeric Bound input/value bit trace, SHA-256
`b129d71fe62a4949999f3fcb58c95d55710a3e8c2801b393c099e1e5c18a049a`,
and the same 214-coordinate bank digest
`c0eee932cdbd18a5b9384060aa104669b4d0ca7b17386323f6cce2ed9159ecf7`.
The producer oracle and viewer bank were also compared **element by element**:
all 214 named IEEE-754 hex values, completed status, admitted bits
`4032000000000000`, tick 1 and zero stops were exact. The bank digest above
uses JSON of sorted `[coordinate,bits]` pairs; applying that encoding to the
Python oracle yields the same digest. An earlier Python digest `3e440813…`
used a different aggregate encoding and was not compared as an equal-format
hash.

The cache is private to one synchronous integration attempt, including a
zero-duration attempt; it does not persist across ticks, snapshots, mounts or
direct numeric calls. Exact finite IEEE keys retain signed-zero distinction;
either ineligible placement bypasses both maps. All expression operands are
evaluated before a lookup. Both placements and SAT must succeed before new
entries publish. Replaced numeric builtins bypass reuse. Tests cover failed
right placement, failed SAT projection, bounded eviction, invalid operands,
cross-table isolation and attempt cleanup.

Root review identified that the new structural profile-call inspection also
walked ordinary expressions and binding aliases recursively. A new
10,000-alias inspection test, run both with and without a profile-call tail,
was red with `Maximum call stack size exceeded`. The inspection now uses an
explicit LIFO walk, preserving callee-before-arguments and left-to-right
visit/error order, the original seen-set behavior and direct-call validation.
Extending the red test to full `loadProgram` exposed a second recursive
Bound-alias marking path, then a quadratic per-binding rescan. Alias marking
is now iterative, while forward-ordered bindings carry a profile-call bit
from each local graph and its earlier aliases. The full 10,000-alias load
with either tail completes; the focused profile/cache suite passed 28 tests
with one optional skip and typecheck exited 0. These are load-time changes
only, not numeric evaluation or Bound search changes.
The complete widget suite after this final load-path fix passed 1,531 tests
with two optional skips across 58 passing test files (exit 0, 51.67 s).

## Browser, distribution and regression gates

- `npm run typecheck --prefix machinome_viewer/widget`: passed after final
  numeric-order fix.
- `npm test --prefix machinome_viewer/widget` before the final polygon-order
  correction: 1,525 passed, 2 skipped. After that correction and the combined
  Follow/v13 test: 1,528 passed, 2 skipped, **one cost-floor failure**:
  legacy Curta fixture 889 ticks/s against branch floor >900. Current viewer
  main `dc0b484` independently measured 838 ticks/s on the same CPU 13 and
  intentionally lowered that floor to >130. This stale-base timing threshold
  was not evidence of a v13 behavior regression. After rebasing the cycle on
  `dc0b484`, the complete widget suite passed: **1,530 passed, 2 skipped**
  (58 test files passed, one skipped); typecheck again exited 0. The two skips
  are the existing optional/environment-gated profile benchmark and one
  optional profile-contact case, not failures.
- `python -m pytest -q` on the candidate bundle: 195 passed, 22 subtests,
  **three failed** in 500.16 s. Two were stale expected API 25/documents
  1–12 assertions; both were corrected and the targeted package/CLI/browser
  set passed 35/35. The third was an unrelated gesture screenshot timing
  assertion under a loaded SwiftShader run; the exact test passed alone
  1/1 in 32.88 s without a runtime change. The original broad exit was 1,
  not relabeled green.
- `tests/test_profile_document.py`: hosted real Chromium loaded the producer
  v13 Bound with a clearly identified stand-in STL; the public run handle
  blocked a 5° request around 0.5°, then restored and replayed the same bank
  and outcome at default dt=1/240, with no browser error. It passed again
  after the final bundle rebuild. Screenshot
  `tests/_shots/profile-contact-v13.png` was inspected and shows the visible
  stand-in wheel and control/readout, not Curta installed geometry.
- Documentation tests: 8/8; strict Sphinx 9.1 HTML build passed; the browser
  manual check visited 14 pages at 1440/390 widths, validated 204 local links,
  menu/search/live examples and reported no browser errors. The 0.7.0/API-25
  baseline record remains separate from current-source API 26/documents 1–13;
  no push/upload or new release is claimed.

The framework owns producer numeric validation, the public Python API and v13
serialization. The viewer owns this reader and its browser execution. The
project still owes complete installed-print/axial/full-motion proof before
adopting contact in production; none of the primitive or component gates here
waives that obligation.
