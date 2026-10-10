# Implementation and acceptance evidence

Base `0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc`; planning commit `644f5b2`.
Standalone framework cycle, no viewer changes. See
`workflow/docs/curta-ancestor-joint-constraints.md` for ratification and baseline.

## Framework red → green

Before implementation, the flat positive control passed and the nested test
failed at declaration: `TypeError: cannot read 'constrain' through
drive.disc.turn`. **1 failed, 1 passed, 1.11 s**. After declaration resolution
but before span compilation, the same pair produced **1 failed, 1 passed,
1.44 s**: the nested request was `completed`, not `blocked`. The final test
stops the unchanged descendant at 124 degrees with the shaft held at 4.

Focused coverage grew to **36 passed, 5 subtests, 1.69 s**: instance/scope
isolation, inheritance/overrides, original-range intersection, parameters,
untimed judgment, known/unknown reads, moving-read restraint, committed-own
freezing, transactional bank/time/record preservation, replay/reset, clocked
stops and curved-level refusal, independent running-time admissions, invalid
targets/reads and publication equivalence. Refused command bookkeeping is
not claimed to be absent from a snapshot: committed mechanical state and
records remain atomic, as in the existing request contract.

Full relevant run from the framework worktree:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
/home/asa/devel/machinome-studio/.venv/bin/python -m pytest -q \
tests/test_ancestor_constraints.py tests/test_joints.py tests/test_couplings.py \
tests/test_declarative_nodes.py tests/test_running*.py tests/test_clocked*.py \
tests/test_time_drive_corpus.py
```

**1283 passed, 1342 subtests passed, 60.27 s**, seven pre-existing render-read
and build123d deprecation warnings. The existing byte-identity and producer
corpus tests pass unchanged, including ADR-133. An earlier narrower run had
842 passing tests and 847 subtests.

The equivalent-native-publication test compares two forms of the same named
model, including program identity, normalizing only root source-file mtime.
Different model class identities are intentionally not interchangeable.
No executor, serializer or viewer implementation changed.

## Curta acceptance

Recorded in the independent project's
`simulation/docs/ancestor-lockout-2026-09-20.md`, committed with the diagnostic,
tests and reproduction tools at Curta
`331081436ed3d4e79890e07843f93f82e2d71f2a`. Its actual full-tree red test
failed with `completed != blocked` in 129.27 s. The complete bell and held ones
locking assembly bracket native contact at 125.33065796..125.33068657 degrees
and published-mesh contact at 125.32258987..125.32261848. Both are free at the
diagnostic's rounded 125.32-degree stop. The retained test passes (175.85 s;
final rerun with explicit Manifold status checks: **1 passed, 174.24 s**),
including both kernels, held shaft, existing pawl restraint, .05-degree reverse
relief, no backlog and exact replay. The production manifest is unchanged;
only the prepared 120..150-degree, 189.6-degree retained-shaft history is
accepted. Other phases, channels, modes, carry positions and revolutions remain
project work, not silently certified by this framework cycle.

The separate actual-geometry export stays version 7. Hosted public requests
and a real 240-pixel crank-handle drag both stop at 125.32 degrees; all 608
descendant assembly paths, 25 controls and bank declarations/defaults compare
unchanged. Browser relief and replay pass; zero page errors. Inspected image:
project `_build_ancestor_lockout/stopped-lockout.png`, showing the actual bell
and locking assembly with the blocked 125.3200-degree panel state. Kernels
prove clearance below the image's resolution. No pilot Studio session changed.

Viewer content advanced independently during validation and is clean at
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f` (API 23, version 0.2.0).
The tested bundle SHA-256 is
`427e5090bc8119fa0e4cf80e0ca2366a72567cb5c945adddfc60631d5dc6944d`;
the diagnostic document is
`ff5d9e6b9b41c84433753311ee1a9993208973d486f2413875253eb310686c0d`.
No viewer change belongs to this cycle. The project record preserves both
successful evidence and probe setup failures, with the baseline document hash.

Focused unmodified operating-model regressions: **3 passed, 871.17 s**.
These are the four-turn counter-direction/arithmetic-history test, the
partial-input retention/replay test and the reverser detent/travel-limit test;
their exact selectors are recorded in the project evidence. The project
OpenSpec change also validates strictly; its broader operating tasks remain open.

The seven changed framework implementation files have combined SHA-256
`3e48841917e38e79cbf44e51ff5659e9a09c4b5cfb0ae52c009315cb4f27261c`.
The project record gives the ordered filenames and exact hash construction,
pinning the tested code independently of this later documentation/archive commit.

## Documentation and synchronization

ADR-134 records the implemented additive composition and explicitly amends
ADR-113; its index, synthesis, public driving/API/scenario docs and changelog
are updated. Documentation suites: **27 passed, 40 subtests, 2.92 s**.
CLI/lazy-import suites: **18 passed, 18 subtests, 3.18 s**.
Current implementation regression total: **1328 tests and 1400 subtests**.

The OpenSpec synchronization workflow added two requirements to each of
`joints` and `simulation`. Read-back verification compares their appended text
exactly with each accepted delta and proves the complete original main spec
remains byte-preserved. Strict validation: **35 items passed** (the active
change and all 34 baseline specs). All project acceptance checks are complete.
Archival uses `--skip-specs` only to avoid applying the already synchronized and
verified deltas twice; no accepted requirement is skipped.

## Final closeout

The supported archive command completed with all 17 tasks checked, moving the
spec-driven change to
`openspec/changes/archive/2026-09-20-ancestor-joint-constraints/`.
Post-archive validation passes for **all 34 baseline specs**. The complete
relevant test selection above plus the documentation and CLI/lazy-import suites
was rerun as one process: **1328 passed, 1400 subtests passed, 64.52 s**, with
the same seven deprecation warnings. The source fingerprint remains unchanged;
the existing running, clocked and time-drive corpus files have no diff.

Primary framework `main` was rechecked clean at the recorded base `0ce71cd`.
The completion commit contains this archive, implementation, tests, synchronized
specs, accepted ADR and documentation. It is not integrated into main; the
cycle worktree is retained pending separate integration authority. No remote
push, publication or viewer mutation was performed.
