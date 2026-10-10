# Framework performance next steps

Provisional, 2026-09-19. Working record, not a promise: nothing here is
ratified, and an OpenSpec spec or accepted ADR outranks it. This note records
the current assessment and the evidence gates for any change cut from it. It
does not authorize implementation, integration, publication, or a reduction
in geometric accuracy.

## Question and answer

Building real models and running the complete framework suite take long enough
to interrupt development. The question was whether the Python interpreter is
the limiting factor, and whether PyPy or a Rust layer would materially improve
it.

The answer is **not generally**. There are measured Python hot paths in the
simulation layer, but build and full-suite wall time is presently dominated by
fresh-process isolation, loading the native CAD stack, native geometry work,
real subprocess-backed integration tests, and deliberate cold-build and
memory-retention proofs. PyPy is a poor match for that workload. A broad Rust
layer would wrap work already performed by OCCT, Manifold, NumPy, SciPy and
OpenSCAD rather than accelerate it.

The next work should reduce how often expensive boundaries are crossed, make
the local test loop proportional to the change under development, and remove
the one evidenced repeated Python traversal before considering another
runtime.

## Evidence

### Current full-suite observation

On 2026-09-19, from clean framework `main` at
`60c0f45761ca6897a4d115811426c80d55286302`, the serial command was:

```text
PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 \
  ../.venv/bin/python -m pytest -q -p no:cacheprovider \
  --durations=40 --junitxml=/tmp/machinome-current.xml
```

It completed in **328.58 seconds**: 3,392 passed, one failed, four skipped and
1,943 subtests passed. The failure was reproducible alone:
`PublishedPiecesInventoryTest::test_identical_classes_merge_into_one_piece_naming_both_sources`
found two bushing pieces rather than one. That is a current correctness
finding, not a performance result, and this note does not diagnose or absorb
it.

The seven largest modules accounted for 217.3 of 321.2 recorded testcase
seconds (67.7%):

| module | seconds | character of the work |
| --- | ---: | --- |
| `test_meta` | 82.75 | end-to-end CLI children, real STLs and real assertions |
| `test_lazy_test_framework` | 35.42 | fresh-interpreter import boundaries |
| `test_retained_builder_generation` | 35.15 | cold retained build versus a 25-child reference |
| `test_node_lazy_exports` | 24.98 | fresh-interpreter native-backend import boundaries |
| `test_running_simulation` | 16.29 | running simulation, including a `tracemalloc` retention soak |
| `test_build_lock` | 11.57 | real process, lock and publication behaviour |
| `test_mesh_engine_dependency` | 11.15 | isolated dependency-boundary processes |

The single 24-artifact retained/reference build proof took 35.11 seconds. Two
default-no-recording memory proofs took another 21.20 seconds under
`tracemalloc`. These are valuable full-validation contracts but poor members
of a change-local feedback loop.

No open-file exhaustion occurred. Archived notes about earlier parallel-load
file-descriptor failures are historical and are not a constraint or finding of
this assessment.

### Controlled build and startup evidence

The 2026-09-08 performance campaign remains the controlled comparison for the
mechanisms it measured:

- a bare Python control started in 0.092 seconds;
- importing `CadQueryNode` took 3.192 seconds;
- a cold CadQuery build took about 5.8--6.0 seconds for both one and eight
  simple artifacts;
- the retained builder reduced the synthetic 24-artifact Solid2 cold build
  from 29.910 to 1.961 seconds by using one child instead of 25; and
- settled warm builds measured 5.909 seconds for Abacus, 5.884 for V8 and
  11.170 for Metamaquina2.

Those numbers distinguish Python startup from CAD-stack import and native
work. They do not claim that the September 8 tree is the current tree or that
every project has the same profile.

The builder's use of a fresh spawned interpreter is a correctness boundary,
not accidental overhead. A late fork inherits OCCT/OpenMP state without its
worker threads and can deadlock on tessellation. Any optimization must retain
the fresh-process guarantee.

### Evaluable Python hotspot

The Curta `evaluate-only-what-moves` evidence names one substantial remaining
Python cost: `declared_ports(node_class)` repeatedly walks a declarative class
through `__getattr__`. It measured 61% of Curta construction and 12.5% of its
tick. A prototype memo reduced construction from 5.46 to 1.98 seconds and the
tick from 3.27 to 2.82 seconds; combined with ADR-124, the tick measured 0.294
seconds and construction 2.08 seconds.

This is an evidenced framework candidate. It needs a coherent answer for
dynamic `.repeat()` declarations and class lifetime, probably a weak-keyed
cache with explicit invariants. It does not need Rust to realize the measured
gain.

## Runtime choices

### PyPy — do not pursue

Machinome's required stack includes CadQuery/OCP, build123d, Molejo BREP,
Manifold, NumPy, SciPy and rtree. The pinned OCP release is distributed in
CPython-specific wheels rather than a PyPy wheel or source distribution.
PyPy's C-extension compatibility layer also adds overhead at the boundary,
while its JIT has a warm-up cost poorly suited to short-lived import probes and
spawned build children.

Revisit only if the complete required CAD stack publishes and tests a PyPy
path and a named machinome workload shows a long-lived pure-Python loop after
the algorithmic work below. Neither condition holds.

### Rust — no broad layer

Do not rewrite framework orchestration or add a general Rust acceleration
layer. It would not accelerate native kernel import, OCCT tessellation,
Manifold booleans or OpenSCAD rendering, and the declarative model would pay
for frequent object conversion across the binding.

A native implementation becomes a candidate only when a profiler identifies
one stable, isolated, data-oriented pure-Python kernel that retains at least
30% of a named real workload after caching and algorithmic fixes. The spike
must include binding-conversion cost, packaging on supported platforms and
semantic parity. Rust, Cython and mypyc would then be alternatives for that
kernel, not a prior architectural commitment.

### CPython — retain, benchmark 3.13 separately

Keep CPython as the supported runtime. A CPython 3.13 experiment is a cheap
comparison once the pinned native dependency set is proven installable and
the suite is green there, but it is an incremental benchmark, not the main
performance programme and not a substitute for the structural work below.

## Proposed sequence

Each numbered item is a separate decision and, where it changes framework
behaviour, a separate framework-change cycle. Later items are not implied by
accepting an earlier one.

### 1. Give maintainers a proportional local test loop

This is a framework-maintenance need supported by the current suite itself.
Classify tests by what they prove:

- ordinary deterministic framework behaviour;
- subprocess/native-backend integration;
- cold-build equivalence and performance structure; and
- memory/retention soak.

Keep the complete suite as the integration/release gate. Add explicit commands
for a fast change-local lane and the complete lane; do not silently stop
running any category in CI. The classification must follow test semantics,
not a duration threshold alone. Record the selected and deselected counts so
the fast command cannot gradually become an undocumented partial suite.

Success is a materially shorter local command with the full command proving
the same contracts and no test weakened or deleted. This improves feedback
time; it does not claim to make the product faster.

### 2. Make parallel pytest execution an honest option

The current test base shares and deletes `tests/_build`, and meta-tests share
`tests/_build_meta` plus a process-local result cache. Running `pytest -n`
without adapting those boundaries would race or duplicate expensive fixture
runs.

First give each worker its own build roots. Preserve file-local reuse by
starting with `pytest-xdist --dist loadfile`, then compare serial, two-worker
and four-worker runs on the same clean commit. Record wall time, CPU, peak RSS,
test counts and failures. Native kernels already use threads, so `-n auto` is
not presumed optimal.

Success is two consecutive green parallel full runs with materially lower
wall time and no serial-only test semantics. If speedup is small or memory
cost disproportionate, keep the worker isolation if useful but do not make
parallel execution the default.

### 3. Memoise `declared_ports` under an explicit class-lifetime contract

Use the Curta finding and its existing probes as the originating evidence.
Specify when a declarative class's port enumeration becomes immutable, how
dynamic `.repeat()` affects that point, how cache entries cease to retain
classes, and how tests can reset or observe the cache without creating a
production API.

The acceptance proof must reproduce the named Curta construction and tick
measurements, retain declaration and naming behaviour, and include class
lifetime and dynamically constructed declaration cases. Prefer removing the
repeated walk in Python over translating it into another language.

### 4. Establish a current OpenSCAD producer baseline

The installed OpenSCAD is 2021.01 and the framework invokes it without a
backend selection. Current OpenSCAD exposes the Manifold backend as the new,
fast default, but changing producer version or backend can change emitted
triangulation and numerical edge cases.

Before proposing a framework change, select a named existing Solid2/OpenSCAD
project whose cold build is presently painful. Capture its current cold and
settled build time, artifact map, volume/bounds and project assertions. Then
run the same input under a current OpenSCAD release with an explicit Manifold
backend. Synthetic boxes alone are not empirical evidence for changing the
producer.

If outputs and contracts agree within already ratified semantics and the real
project improves materially, propose capability detection and an explicit
backend policy. If they disagree, bring the geometric difference to the pilot;
do not trade correctness for speed silently.

### 5. Consider bounded parallel OpenSCAD rendering only after item 4

Sequential STL rendering remains a known architecture gap. It becomes a
feature proposal only if the named cold-project baseline shows independent
OpenSCAD jobs are still a meaningful share after the backend experiment.

Measure a fixed small concurrency range rather than mapping one job to every
CPU. Preserve source-generation sealing, per-artifact locks, atomic
publication, failure cleanup and deterministic documents. The acceptance
proof needs identical artifact identities and error semantics, not only lower
elapsed time.

### 6. Re-profile before any native-language work

After items 1--5 that are justified have landed, profile construction, one
representative tick, cold build and settled build for the named projects. A
new profile supersedes this note's optimization ordering. Do not implement a
Rust layer merely to complete this sequence: absence of a qualifying isolated
Python kernel is the expected and acceptable result.

## Explicit non-goals

- Reducing tessellation resolution or geometric precision by default.
- Replacing exact assertions with approximate GPU checks.
- Removing fresh-process isolation around OCCT.
- Weakening cold-build, retention, import-boundary or end-to-end contracts.
- Treating current OpenSCAD source documentation as proof that a particular
  packaged release is geometrically interchangeable with 2021.01.
- Treating an old file-descriptor incident as a current blocker.
- Making PyPy, Rust, parallel pytest or parallel rendering a framework feature
  without the evidence gates above.

## Candidate cycle boundaries

If the pilot takes up this plan, the smallest coherent cycles are:

1. `classify-framework-test-lanes` — maintainer workflow and CI contract;
2. `isolate-parallel-test-workers` — worker-specific artifacts and measured
   xdist command;
3. `memoise-declared-ports` — Curta-originated runtime improvement;
4. `select-openscad-backend` — only after a named project baseline; and
5. `parallelise-openscad-artifacts` — only if the same evidence still asks.

The first two improve framework development rather than machine behaviour.
The third already has named project evidence. The last two are deliberately
conditional: design symmetry and an old performance report are not enough to
create them.
