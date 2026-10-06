## Why

Originating findings: `workflow/warts.md`, "Findings from the framework
cycle `lean-install` (3 October 2026)", the entry on
Actuators/Internal-Cycloidal-Actuator and its addendum from the
`mesh-engine` cycle:

> **A `machinome build` in a fresh project worktree hung for three hours.**
> During the cycle's deep validation, a `machinome build` of
> Actuators/Internal-Cycloidal-Actuator in a fresh git worktree [...] with
> the ignored 35 MB vendor STEP copied in) hung: the `machinome build`
> process alive with 4 s of CPU, an empty `_build/actuator.lock`, no
> artifact written and no child process; killed by the orchestrator after
> three hours [...]. The same build in the project's primary checkout,
> where artifacts exist, completed in under a minute. Not reproduced
> [...]. **Untriaged.**
>
> *4 October 2026, the framework cycle `mesh-engine`:* a `machinome build`
> in a project whose sources were written moments earlier restarts every
> second without end: each build generation, a fresh spawned interpreter,
> ends `SOURCE_CHANGED` (11), and `machinome build` starts the next,
> printing `START` once a second. [...] with every source dated an hour
> back, the same build printed one `START` and exited 0. [...]
> **Reproduced, mechanism found; untriaged.**

The cycle `snap-keeps-the-triad-unit` (6 October 2026) met the same loop on
this bench: seven tests of `tests/test_scad_presentation.py` that build
`tests/scad_where_read_project/native.py:StlBench` or `machine.py:Machine`
never finish, and the full suite could only be run with them deselected
(`openspec/changes/archive/2026-10-06-snap-keeps-the-triad-unit/evidence.md`,
§4.3).

Reproduced on the bench `fix-warts-3` at `2acba68` (design.md, Context, has
every command and number):

- `machinome build tests/scad_where_read_project/native.py:StlBench`, bounded
  at 30 s, exits 124 after 9 `START` lines; `machine.py:Machine`, bounded at
  60 s, after 17. `ExactBench` and `Mixed` exit 0 after one `START`.
- A fresh detached worktree of `Robots/hexapod_spiderbot_model`, built
  against the bench and bounded at 120 s, exits 124 after 34 `START` lines.
- A scratch project of one `StlNode` whose mesh is dated 1 ms, or 1 s, after
  its module, every file an hour older than the build, loops the same way
  (36 `START` lines in 45 s, each).

**The mechanism.** `Builder._start` remembers `loaded_source_mtime_ns`, the
largest mtime of the root's source set right after load. Assembly then adds
every part's own sources to that set: an `StlNode`'s mesh, a STEP or SCAD
file, a module a part imports. After assembly the builder compares the
largest mtime of the grown set with the remembered one and returns
`SOURCE_CHANGED` when they differ. A mesh dated even 1 ms after the module
makes them differ, with no file having changed; every fresh generation sees
the same, so the build restarts without end. A git checkout writes a
project's files in path order, so in a fresh clone or worktree every mesh
under a directory sorting after the modules' (`stl/` after `simulation/`)
is newer than they are. The source generation's own census, which compares
every contributor with its own observation, found nothing changed in any of
these generations: the stand-down comes from the aggregate comparison alone.

The comparison has been wrong since `769486f` (7 September 2026, "fix: lock
artifact-producing assembly"), which moved assembly after the moment the
loaded maximum is taken; before it, that maximum was taken after assembly.
ADR-084, the next day, made the per-contributor generation the authority on
whether loaded classes still describe disk ("Source correctness now has an
explicit generation and phase boundary rather than depending on aggregate
mtime"), and kept the comparison beside it. The baseline requirement
"Superseded and redundant builds do not publish" already refuses to let an
equal maximum hide a contributor that changed; this change states the
converse, that a different maximum does not invent one.

## What Changes

- **A contributor is judged by its own observation.** With a source
  generation (every real build), the post-assembly comparison of the grown
  set's largest mtime with the loaded maximum goes. A contributor that joins
  during assembly is observed when it joins and checked again, uncached, at
  the assembly phase's closing check and at every later phase and
  publication boundary, as ADR-084 and the baseline already require; an edit
  after it joined still stands the build down. Its timestamp relative to
  the modules, to the build's start or to the present is not consulted.
- **Where:** one condition in `machinome/core/builder.py`, `Builder._start`,
  and the comment above it. The comparison stays where no source generation
  exists, a branch reached only with a patched loader (design.md,
  Decision 2).
- **Tests:** an in-process builder test with a real source generation (a
  joiner dated 1 ms, 1 s, and an hour in the future), red today; a
  supervisor test spawning real builders for a project whose mesh is newer
  than its module, bounded by refusing a second builder, red today; a guard
  that a joiner replaced after it joined still stands the build down. The
  seven `test_scad_presentation.py` tests run again.
- **Words:** one changelog bullet under `Unreleased`; the warts entry's
  addendum moves to the campaign's resolved record.

**Deliberately out**, with the reason:

- the lock-wait comparison (`self.node.mtime_ns != loaded_source_mtime_ns`
  right after `checkpoint('after_lock')`): it compares the same set the
  loaded maximum was taken over, so it cannot misfire this way, and it is the
  no-generation branch's only lock-wait guard, pinned by
  `test_source_moving_under_a_waiting_build_stands_it_down`;
- comparing a joiner with the time the build started (design.md,
  Alternative A): it would mix the filesystem's timestamps with the
  process clock and loop forever on a file dated in the future;
- the three-hour hang itself. Its project read a STEP copied in after the
  checkout, the newest file, so the same mechanism is plausible; but its
  recorded observations (no child process, no artifact after three hours)
  are not what this loop shows, and the 35 MB vendor STEP makes the build
  slow to repeat. The entry stays in `warts.md` with a "Remaining" note;
- the Cycloidal actuator project; the validation uses a small STL project
  instead, in a fresh worktree created and removed for the purpose.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `build-pipeline`: "Superseded and redundant builds do not publish" — one
  bullet added: a different aggregate maximum does not stand a builder
  down while every contributor agrees with its own observation, and a
  contributor joining during assembly is compared with its observation at
  joining, not with the loaded maximum or the build's start; two scenarios
  added, every existing scenario carried.
- `one-shot-build-and-notification`: "One-shot conventional node build" —
  one sentence added: the order of a project's file timestamps does not by
  itself make its builder stand down; one scenario added, every existing
  scenario carried.

## Impact

- Code: `machinome/core/builder.py` (`Builder._start`: one condition and
  its comment).
- Tests: `tests/test_retained_builder_generation.py` (three tests); the
  existing stand-down tests of `tests/test_builder_lifecycle.py`,
  `tests/test_retained_builder_generation.py` and
  `tests/test_source_generation.py` unchanged and green.
- Behaviour: a build or development session in a project whose part
  sources are newer than its modules publishes in one generation instead of
  restarting. No artifact, stamp or document changes for a project that
  built before; a published artifact's stamp is still the node's largest
  source mtime over the grown set.
- No ADR: this is conformance with ADR-084, which already made the
  per-contributor generation the authority (design.md, Decision 4).

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is cycle 2 of that note's table, promoted ahead of the rest on
6 October because it blocks the full suite on the campaign's bench.
