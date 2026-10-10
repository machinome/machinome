# Implementation evidence: placed-profile AABB index

This cycle branches from framework `8d0fd156787f5136174fb752be78451ce172bce8`. It serves only the frozen Curta Type I installed-reverser trial: project reference `_build_checks/reverser-installed-profile-reference-a428dea.jsonl` (SHA-256 `d41e1b46ee7f4c92b61d2ddae586f01242574213942d7dd93f0e9c4aefad01a3`), old version-13 document `/tmp/curta-installed-profile-v13.json` (SHA-256 `2d62786b64c4f8f113fbd6224a1dca49b12bbfad0e37c8130c2b0840d208eb34`), and 214-key oracle `/tmp/curta-installed-profile-one-tick-bank.json` (SHA-256 `1872b5a9ca242df97d5f86f0050f7e1b94144b9f55c019a3db58ed1a7c50cc2e`). The project's revised covers remain unadopted and are not certified here. Temporary probes and generated output stayed under `/tmp`; no project or viewer file was edited.

## Red-first and semantic proof

New repeated-index tests initially failed on the tuple-only baseline because cached placed values had no `box_tree`; focused tests were then green after implementation. They cover first-use bypass, 1-by-N/2-by-N skew bypass, indexed last-polygon boundary touch versus one-ULP clearance, a spatially earlier valid pair that must not outrank the original first SAT projection refusal, a later collapsed right edge despite an apparently contacting first polygon, signed zero and extreme finite box coordinates, custom conversion bypass, tree-build/SAT failure leaving the prior cached placement untouched, and placement-LRU eviction. The original pair AABB and SAT arithmetic remain unchanged; only conservative tree queries skip strictly disjoint boxes, and candidate indices are restored to authored order before SAT.

The 18-degree/0.1-second tick returned the same ordered-contact digest `46cdac2bff6972f1cf4f3b9ba2a2ac1204c3a306212cbb0fac2cc9eb31582cd4` and bank-bit digest `3e44081383251e2e2c12b91a58f03336ff887a465e840b8a26d88788d686983d` in every paired run. Both sides evaluated 1,560 numeric calls, 780 distinct pair keys and 136 placements; the 214-key bank and completed crank/reverser readouts match. The project reference, not the mutable current covers, is the caller evidence.

## Paired CPU10 timing

Untraced, one pinned CPU, same `.venv`, same frozen input and no mesh, alternating immutable base and candidate after the direct-loop correction:

| Order | Source | Crank tick CPU s | `profile_overlap` CPU s |
| --- | --- | ---: | ---: |
| 1 | base `8d0fd15` | 8.650940 | 1.551016 |
| 2 | candidate | 7.653279 | 0.752644 |
| 3 | base `8d0fd15` | 8.464366 | 1.538608 |
| 4 | candidate | 6.826885 | 0.411959 |

The candidate saved 1.00–1.64 CPU seconds per tick in these pairs (roughly 12–19%) and 0.79–1.13 CPU seconds in the predicate. The candidate's first sample incurred more `_placed`/garbage-collection time than its second; performance is a measured range, not a deterministic speedup promise. A separate cold/direct and repeated-right crossover included 1-by-4,096 and 2-by-4,096 cases; these stayed on the ordinary scan under the 32-left/16-right private gate. Direct large scans retain the original inner loop and showed no material stable regression in microprobes; the matched Curta tick is the acceptance measure.

## Memory and bounded lifetime

A paired whole-run `tracemalloc` probe (same pinned document and CPU) measured baseline peak 234,301,384 bytes and candidate peak 235,962,453 (+1,661,069). An attribute-aware deep walk of the actual 136-placement crank cache measured baseline 14,691,688 bytes and candidate 16,305,965 (+1,614,277), including `_CachedPlaced` tuple-subclass dictionaries. The candidate retained 130 trees in that cache; a standalone walk of those trees is 2,011,892 bytes but shares coordinate objects with placed values and must not be added to the cache increment. The peak live tree graph at a build was about 2,011,748 bytes; the largest single tree was about 32,380. The 256-placement/1,024-pair entry limits and per-attempt release remain unchanged. The earlier 2-tree/+37.6 kB diagnostic selected the later reverser cache, not this crank cache, and is superseded.

## Validation and decision record

Focused profile, running-bound and documentation tests passed: 129 tests and 37 subtests. The final full suite after all adversarial additions passed 3,664 tests, skipped 4, and passed 2,155 subtests in 396.37 seconds; the 53 warnings were pre-existing deprecations/future notices. No new ADR or architecture rewrite is warranted: the index is a private implementation under accepted ADR-144's success-only, bounded per-integration cache and does not change the public profile, Bound, document, or viewer contract. The measured memory trade-off was explicitly re-ratified for this pinned case.
