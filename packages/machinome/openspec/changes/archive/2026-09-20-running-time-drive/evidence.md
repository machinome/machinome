# Running-time drive implementation evidence

Date: 2026-09-20. Standalone framework cycle; no viewer implementation,
historical reconstruction, push or publication is included. The pilot separately
authorized integration into framework `main` after archive and commit.

## Identity and authority

- Origin: parked `projects/astrarium`, checkpoint
  `67090d2829a4f5431e58ab7c11328ac3583774d8`.
- Framework base: `9fb5127fad62e6c66067b34e7d02dd389471fa2d`, primary `main`.
- Isolated branch/bench: `running-time-drive`,
  `/home/asa/devel/machinome-studio/machinome/WTs/running-time-drive`.
- Pilot ratification: “ratify, go on”. Strict planning validation passed;
  planning-only commit `03a3d0d` was clean and exactly one commit above base
  before implementation began.
- Integration target: framework `main`, separately authorized by the pilot's
  “integrate to main too”. The pre-integration check found it clean at the
  recorded base. Integration is fast-forward-only after commit two.

## Red-first chain

All Python commands below run from the bench with
`PYTHONPATH=. /home/asa/devel/machinome-studio/.venv/bin/python`.

`-m pytest -q tests/test_running_time_drive.py --tb=short` initially gave
**8 failed, 2 passed**: every new declaration failed at `ClockRef.check`;
the commanded-rate comparison and direct-joint double-binding control passed.
After admitting syntax, the same eight failed at compilation as unowned time.
After compiling time, they failed at their no-motion assertions. Only admitting
elapsed intervals made the initial ten pass. Removing the syntax refusal alone
was demonstrably insufficient.

Publication tests then failed because time-driven documents still selected
versions 5 or 6, before adding the explicit drive table and version-10 rule.
The new corpus tests first failed because its generator did not exist; they
now replay the actual producer output against the committed fixture.

An additional curved-path regression exposed a stop-localization defect:
`time -> shaft (t*t) -> follower (ratio 1, upper bound 2)` left the upstream
shaft at 1, 1.96 or 1.9999175091796186 for `dt` 2, 0.5 or 0.02, while
the follower was snapped to 2. Localization now evaluates the time-driven
determining prefix from its original sources, with the same arithmetic as
commit. All three cadences leave both coordinates at 2 within the existing
numerical contract. No new tolerance or search guarantee was introduced.

The inherited-clock regression failed with “TypeError not raised” when a
subclass replaced `time` but inherited a relation to the old declaration.
Resolution now refuses that mismatch rather than silently retargeting it.

## Green verification

| Check | Result |
| --- | --- |
| `-m pytest -q tests/test_running_time_drive.py tests/test_time_drive_corpus.py --tb=short` | 29 passed, 10 subtests passed, 3.70 s |
| Affected pre-existing suites listed below, before the final curved-path/ownership additions | 662 passed, 829 subtests passed, 2 warnings, 45.52 s |
| `-m pytest -q --tb=short` after all behavior changes | 3,439 passed, 4 skipped, 1,991 subtests passed, 53 warnings, 421.39 s |
| Final affected command below, also including `tests/test_running_time_drive.py tests/test_time_drive_corpus.py` | 691 passed, 839 subtests passed, 2 warnings, 60.93 s |
| Same affected command after archival, before commit two | 691 passed, 839 subtests passed, 2 warnings, 45.23 s |
| `tools/generate_time_drive_corpus.py` | Seven real documents and 54 recorded ticks; exact producer replay passes |
| `openspec validate running-time-drive --strict` | Pass after implementation and spec synchronization |
| `openspec validate --all --strict` | 35 passed, 0 failed |
| `openspec validate --all --strict` after archival | 34 baseline specs passed, 0 failed; no active change remains |
| `git diff --check` | Pass |

The affected command was:

```sh
PYTHONPATH=. /home/asa/devel/machinome-studio/.venv/bin/python -m pytest -q \
  tests/test_couplings.py tests/test_running_simulation.py \
  tests/test_running_jumps.py tests/test_running_reads.py \
  tests/test_running_paths.py tests/test_running_selection.py \
  tests/test_running_stops.py tests/test_running_play.py \
  tests/test_running_document.py tests/test_running_corpus.py \
  tests/test_clocked_time.py --tb=short
```

The full suite includes all of these again after the final fixes. Its warnings
are dependency deprecations, multiprocessing fork warnings, and existing
deprecated render-time reads/bindings; no environmental failure was reported.
Four tests were skipped, not passed. Deterministic no-time-drive cost pins
remain `Train` 8.0 and `Clearing` 98.6 expression evaluations per tick
(`tests/test_running_paths.py`). This is operation-count evidence, not a claim
of zero wall-clock overhead. Existing running/document/corpus fixtures remain
unmodified and their replay/identity checks pass.

## Originating acceptance and boundaries

`tests/running_project/time_drive.py::astrarium` is the framework-owned
two-cube representative caller, using explicit time, enable, wind and a
retained-angle exhaustion gate. With no startup rate it runs two seconds,
holds for two, winds by two, and resumes for one: shaft 3, weight 1, time 5.
Running to exhaustion holds shaft/weight at 10; rewinding five and running
another second yields shaft 11 and weight 6, without recovering missed travel.
Snapshots, reset, independent stops, grouped targets, mixed commanded sources,
same-tick release policy, action ordering, ownership and late-conflict rollback
are covered by the new tests. Joint placement operations follow the bank.

The project's own six-test baseline is **prior evidence**: three inert captured
clock acceptance failures and three artificial-driver/rate comparison passes.
The parked project was neither edited nor rerun as if it already used the new
spelling. It is still planning/research plus diagnostic cubes, not historical
CAD. No visual historical validation or physical escapement claim is made.
Framework primary, project and viewer checkouts remained clean.

## Independent viewer handoff

The schema is described in the delta export spec, ADR-133 and the public
API reference. `tests/time-drive-corpus.json` is the producer-owned transfer
artifact. Consumer requirements include:

- Read ordered `program.time_drives` entries as independent admissions,
  indexed into flattened `program.edges`; never fabricate a driver or bank
  coordinate for `time` or `@time:<edge-index>`.
- Admit each tick from global seconds; hold a stopped relation's local read
  only for that tick's remainder. Retry the next interval without catch-up.
- Preserve jump subtraction, retained gates, coherent downstream stop paths,
  command retirement, atomic rollback and snapshot/reset semantics.
- Record real drivers in stop `inputs`; add `time_drives` only when nonempty.
- Replay the same corpus, using its float tolerance and exact discrete fields,
  before advertising version 10. Script `tick` means sequence step; expected
  `tick`/`time` may rewind after restore/reset. Those operations clear rings.

The older consumer's refusal was exercised read-only in `machinome-viewer`:

```sh
npm test --prefix machinome_viewer/widget -- \
  src/document.test.ts -t 'refuses a version it does not render'
```

Result: **1 passed, 63 skipped**. The current viewer reports versions 1–9 and
rejects 10 before execution. This is refusal evidence, not time-drive parity.
Viewer work and subsequent Astrarium resumption require separate authority.

## Decision record

ADR-133 records the implemented architecture and its rejected alternatives;
ADR-127 is amended only at the running-clock source refusal. The architecture
synthesis and public authoring guide describe the implemented distinction
between absolute posing and retained incremental motion. The historical
research record remains project-owned and unchanged.

## Completed record

All implementation and validation tasks are finished. All ten delta
requirements were compared with their synchronized baseline blocks and match;
unrelated requirements and scenarios were preserved. The pilot confirmed
“Archive and commit”, then separately authorized main integration. The installed
OpenSpec archival workflow moved the complete change, including its metadata,
to `openspec/changes/archive/2026-09-20-running-time-drive/` with specs synced.
ADR and finding links now resolve to this archive. This record belongs to the
second and final cycle commit; the first is `03a3d0d`, based on `9fb5127`.
Git ancestry records the subsequent authorized fast-forward of those two
commits to `main`; no merge commit or extra implementation commit is needed.
Neither approval authorizes a push, release, viewer change or Astrarium
resumption.
