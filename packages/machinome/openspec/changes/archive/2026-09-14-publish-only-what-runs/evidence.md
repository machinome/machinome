# Evidence: publish-only-what-runs

Proposed in the framework worktree `solid-node/WTs/fix-warts` (branch
`fix-warts`), at the commit cycle 1 landed on, with the workspace venv,
`PYTHONPATH="$PWD"`, every command run from inside the worktree.

```
$ git rev-parse --show-toplevel
/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts
$ git rev-parse HEAD
72bd1eb3cb1003ed2037a337330f7960bead236d
$ python -c "import sys; print(sys.version)"
3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]
$ python -c "import solid_node; print(solid_node.__file__)"
/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/__init__.py
```

The probes are under `evidence/`, beside a `pyproject.toml` that makes
that directory a Solid project, the way the framework's own fixtures
are. Running one writes a `_build/` directory there, which is a build
artifact and not part of the change.

- `probe_repeat_port.py` — finding (a), the lock's spring bank.
- `probe_omitted.py` — finding (b), the omitted optional part, and the
  two variants in which a KEPT edge still reaches the omitted node.
- `probe_repeat_joint.py` — the ADDENDUM measurement: a `.repeat()`
  child that owns a JOINT, which this change does not fix.
- `probe_pruned.py` — the candidate fix applied to an already-compiled
  program, without changing the framework: what it publishes, whether
  the identity moves, and the blast radius over the existing fixtures.

## 0. The base suite

The test files this change touches, green on the unchanged tree:

```
$ python -m pytest tests/test_running_document.py \
      tests/test_running_simulation.py tests/test_running_corpus.py -q
144 passed, 2 warnings, 141 subtests passed in 22.62s
```

Exit status 0. The two warnings are the pre-existing `FutureWarning`s of
the legacy `render()` fixtures.

## 1. Finding (a): a `.repeat()` child's port cannot be published

`Bank` is the lock's spring bank reduced to its shape: a running root, a
leaf on a `Prismatic`, and `PenSpring().repeat(3)` whose plain
`height` port the driver drives.

```
$ python openspec/changes/publish-only-what-runs/evidence/probe_repeat_port.py
repeat port    : nodes   [('PenSpring.height', 'intermediate', False), ('PenSpring.height', 'intermediate', False), ('PenSpring.height', 'intermediate', False), ('lift', 'input', True), ('slider.travel', 'bank', True)]
repeat port    : edges   ['lift drives slider.travel']
repeat port    : published -> UnsupportedLaw: the program names 'PenSpring.height', which is a FALLBACK derived from a class name rather than an instance path: the node it belongs to is not linked under the root, so its qualified id is not computable. A class name is not unique across two instances of that class, and publishing it would put two different coordinates under one name in one expression scope. Hold the node on its own attribute of its parent.
linked copies   ['springs-0', 'springs-1', 'springs-2']
instance_path   ('springs-0',)
driver_id      -> DriverIdError: cannot qualify driver 'height' through node segment 'springs-0': a qualified driver id must be a legal identifier in the runtimes that evaluate it, and 'springs-0' is not (a list-held child is named <attribute>-<index>). Hold the node on its own attribute, or move the driver off it.
```

Read off the output:

- the program's coordinate table holds FIVE nodes for a program with ONE
  edge: the input `lift`, the bank coordinate `slider.travel`, and three
  intermediates all named `PenSpring.height`, none of them qualified;
- the only compiled edge is `lift drives slider.travel`. The relation
  onto the springs was dropped by `_reaching_the_bank`, exactly as the
  simulation spec says it should be — and its three ends stayed in the
  table;
- `Program.published()` refuses the whole document.

The last three lines measure WHY the id is a fallback, and it is not the
reason the message gives. The copies ARE linked, under the list-held
names `springs-0`, `springs-1`, `springs-2`; `instance_path` succeeds
and returns `('springs-0',)`; it is `driver_id` that raises, because the
qualified-id grammar (`_LEGAL_SEGMENT`, `solid_node/node/qualified.py:157`)
does not admit a `-`. So the refusal's advice — "Hold the node on its own
attribute of its parent" — is inapplicable: the node IS held on its own
attribute, which is what `.repeat()` realizes into a list under.

## 2. Finding (b): a relation onto an omitted part

The fixture is the one `workflow/warts.md` records under
`declare-controls-on-parts (2026-09-14)`, unchanged, plus two variants
that put the omitted node's coordinate on a KEPT edge.

```
$ python openspec/changes/publish-only-what-runs/evidence/probe_omitted.py
fitted=True : nodes   [('crank', 'input', True), ('first.turn', 'bank', True), ('spare.turn', 'bank', True)]
fitted=True : edges   ['crank drives first.turn', 'crank drives spare.turn']
fitted=True : published coordinates   ['crank', 'first.turn', 'spare.turn']
fitted=True : published intermediates []
fitted=False: nodes   [('Arbor.turn', 'intermediate', False), ('crank', 'input', True), ('first.turn', 'bank', True)]
fitted=False: edges   ['crank drives first.turn']
fitted=False: published -> UnsupportedLaw: the program names 'Arbor.turn', which is a FALLBACK derived from a class name rather than an instance path: the node it belongs to is not linked under the root, so its qualified id is not computable. A class name is not unique across two instances of that class, and publishing it would put two different coordinates under one name in one expression scope. Hold the node on its own attribute of its parent.
read=True   : nodes   [('crank', 'input', True), ('first.turn', 'bank', True), ('spare.turn', 'bank', True)]
read=True   : edges   ['crank drives spare.turn', 'spare.turn drives first.turn']
read=True   : published coordinates   ['crank', 'first.turn', 'spare.turn']
read=True   : published intermediates []
read=False  : nodes   [('Arbor.turn', 'intermediate', False), ('crank', 'input', True), ('first.turn', 'bank', True)]
read=False  : edges   ['crank drives spare.turn', 'spare.turn drives first.turn']
read=False  : published -> UnsupportedLaw: the program names 'Arbor.turn', which is a FALLBACK derived from a class name rather than an instance path: the node it belongs to is not linked under the root, so its qualified id is not computable. A class name is not unique across two instances of that class, and publishing it would put two different coordinates under one name in one expression scope. Hold the node on its own attribute of its parent.
source=True : compile -> UnreachedCoordinate: spare.turn drives second.turn: nothing bound either end. spare.turn and second.turn are both unbound when nothing changes any more, so the relation has no side to be read from. Bind one of them in simulate(), or state a relation that reaches one.
source=False: compile -> UnreachedCoordinate: spare.turn drives second.turn: nothing bound either end. spare (Arbor).turn and second.turn are both unbound when nothing changes any more, so the relation has no side to be read from. Bind one of them in simulate(), or state a relation that reaches one.
```

Read off the output:

- `Machine(fitted=True)` publishes: two edges, both coordinates banked,
  no intermediates. `Machine(fitted=False)` refuses. The difference is
  one `omit()`.
- The refusal is the same defect as (a) with the other cause: the
  omitted child is never linked, so `instance_path` raises, `_qualified`
  falls back to `Arbor.turn`, and the dropped edge's end sits in the
  table. The dropped edge is again absent from `edges` — the program
  never compiled it.
- `Reader(fitted=False)` is the case a pruning does NOT fix: the
  relations are chained (`crank -> spare.turn -> first.turn`), so both
  edges reach the bank, both are kept, and the omitted node's coordinate
  is an intermediate the program genuinely computes. It refuses today
  and must go on refusing.
- `Sourced` is the third variant, and it is unreachable through
  `omit()`: a relation whose source is a coordinate nothing binds is
  refused by the COUPLING layer with `UnreachedCoordinate`, fitted or
  not. So `_refuse_opaque` is not on this path and needs no change.

## 3. The ADDENDUM: a `.repeat()` child that owns a JOINT

Not this change's to fix, and measured so the report can say where it
lives.

```
$ python openspec/changes/publish-only-what-runs/evidence/probe_repeat_joint.py
Traceback (most recent call last):
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/openspec/changes/publish-only-what-runs/evidence/probe_repeat_joint.py", line 53, in <module>
    print('bank           ', sorted(qualified_coordinates(node)))
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 233, in qualified_coordinates
    visit(root, ())
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 231, in visit
    visit(child, path + (child.name,))
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 227, in visit
    found[driver_id(path, name)] = (node, name)
          ^^^^^^^^^^^^^^^^^^^^^
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/node/qualified.py", line 169, in driver_id
    raise DriverIdError(
solid_node.node.qualified.DriverIdError: cannot qualify driver 'lift' through node segment 'pins-0': a qualified driver id must be a legal identifier in the runtimes that evaluate it, and 'pins-0' is not (a list-held child is named <attribute>-<index>). Hold the node on its own attribute, or move the driver off it.
Traceback (most recent call last):
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 2330, in program_of
    sim = Sim(root, 1.0)
          ^^^^^^^^^^^^^^
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/sim.py", line 158, in __init__
    release_tree(node)
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 2299, in release_tree
    for _identifier, (node, name) in qualified_coordinates(root).items():
                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 233, in qualified_coordinates
    visit(root, ())
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 231, in visit
    visit(child, path + (child.name,))
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 227, in visit
    found[driver_id(path, name)] = (node, name)
          ^^^^^^^^^^^^^^^^^^^^^
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/node/qualified.py", line 169, in driver_id
    raise DriverIdError(
solid_node.node.qualified.DriverIdError: cannot qualify driver 'lift' through node segment 'pins-0': a qualified driver id must be a legal identifier in the runtimes that evaluate it, and 'pins-0' is not (a list-held child is named <attribute>-<index>). Hold the node on its own attribute, or move the driver off it.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/openspec/changes/publish-only-what-runs/evidence/probe_repeat_joint.py", line 58, in <module>
    program, initial = program_of(Bench())
                       ^^^^^^^^^^^^^^^^^^^
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 2333, in program_of
    release_tree(root)
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 2299, in release_tree
    for _identifier, (node, name) in qualified_coordinates(root).items():
                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 233, in qualified_coordinates
    visit(root, ())
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 231, in visit
    visit(child, path + (child.name,))
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/simulation/program.py", line 227, in visit
    found[driver_id(path, name)] = (node, name)
          ^^^^^^^^^^^^^^^^^^^^^
  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/node/qualified.py", line 169, in driver_id
    raise DriverIdError(
solid_node.node.qualified.DriverIdError: cannot qualify driver 'lift' through node segment 'pins-0': a qualified driver id must be a legal identifier in the runtimes that evaluate it, and 'pins-0' is not (a list-held child is named <attribute>-<index>). Hold the node on its own attribute, or move the driver off it.
linked copies   ['pins-0', 'pins-1', 'pins-2']
qualified_coordinates raised:
program_of raised:
```

The joint half of the shop skill's claim is refused in a completely
different place: `qualified_coordinates` (`program.py:227`) calls
`driver_id` while enumerating the BANK, and the grammar raises
`DriverIdError` on `pins-0`. That happens inside `Sim.__init__`
(`sim.py:158` → `release_tree` → `qualified_coordinates`), before any
program exists, so the root cannot be SIMULATED, let alone published.
No pruning of the program's nodes can reach it; only the id grammar can.

## 4. The candidate fix, applied without changing the framework

`probe_pruned.py` reduces an already-compiled program's `nodes` to the
bank plus the ends of the kept edges, recomputes `sources` off the
reduced table, and publishes.

```
$ python openspec/changes/publish-only-what-runs/evidence/probe_pruned.py
repeat port  : nodes before  ['PenSpring.height', 'PenSpring.height', 'PenSpring.height', 'lift', 'slider.travel']
repeat port  : removed       ['PenSpring.height', 'PenSpring.height', 'PenSpring.height']
repeat port  : identity unchanged: True
repeat port  : coordinates   ['lift', 'slider.travel']
repeat port  : intermediates []
repeat port  : sources       {"lift": ["lift"], "slider.travel": ["lift"]}
fitted=False : nodes before  ['Arbor.turn', 'crank', 'first.turn']
fitted=False : removed       ['Arbor.turn']
fitted=False : identity unchanged: True
fitted=False : coordinates   ['crank', 'first.turn']
fitted=False : intermediates []
fitted=False : sources       {"crank": ["crank"], "first.turn": ["crank"]}
read=False   : nodes before  ['Arbor.turn', 'crank', 'first.turn']
read=False   : removed       []
read=False   : identity unchanged: True
read=False   : published -> UnsupportedLaw: the program names 'Arbor.turn', which is a FALLBACK derived from a class name rather than an instance path: the node it belongs to is not linked under the root, so its qualified id is not computable. A class name is not unique across two instances of that class, and publishing it would put two different coordinates under one name in one expression scope. Hold the node on its own attribute of its parent.

Gauged: loses ['gauge.angle']; read by an expression: []; named in the bindings table: []
PortDrivenJoint: loses ['register']; read by an expression: []; named in the bindings table: []
Train: loses ['wheel.turn']; read by an expression: []; named in the bindings table: []

corpus Train dt=0.05: intermediates ['wheel.turn'], sources of each {'wheel.turn': []}
corpus Train dt=0.1: intermediates ['wheel.turn'], sources of each {'wheel.turn': []}
```

Read off the output:

- **The two refusals go away.** `Bank` publishes two coordinates, no
  intermediates, and names no copy. `Machine(fitted=False)` publishes
  the crank and the arbor that IS in the machine.
- **`Reader(fitted=False)` still refuses**, and the reduction removed
  nothing from it: both its edges are kept, so the unqualified end is a
  coordinate the program computes. That is the line this change draws.
- **The identity does not move** for any of the three. `described()`
  reads the inputs, the coordinates, the spans and the edges, never the
  node table, so a snapshot taken against a program compiled before this
  change restores into one compiled after it.
- **The blast radius is three fixtures**, each losing one name:
  `Gauged` (`gauge.angle`), `PortDrivenJoint` (`register`) and `Train`
  (`wheel.turn`, the wiring into the wheel's plain port). In none of the
  three does any operation or `params` expression of the published
  document read the name it loses, before or after the bindings table is
  resolved, and none is a `bindings` entry.
- **The conformance corpus carries one of them.** Both `Train` entries
  of `tests/running-corpus.json` publish `wheel.turn` with an empty
  `sources` list, so the fixture must be regenerated.

`Gauged` is worth naming twice: the export capability's own scenario
"A plain port is an intermediate, not a bank entry" is written about it
and says "the edge that computes it names it in `gives`". Today no edge
computes it — `Gauged`'s only edge is `crank -> first.turn` — and the
name is published anyway, with `sources` `[]`. The ratified definition
of `intermediates` is "every value a compiled edge determines that the
bank does not hold". The producer publishes more than that definition
allows, which is the defect this change removes.

## 5. What the change does not touch

Read, not run, and recorded so the reviewer can check it:

- `_refuse_opaque` (`program.py:2160`) reads `nodes[key]` only for the
  needs of KEPT edges; every such key survives the reduction.
- `_ordered` (`:2180`) seeds `resolved` with every node no kept edge
  determines. Removing keys that no kept edge NEEDS cannot change which
  edges become ready, so the topological order is the same list.
- `_reaching_inputs` (`:1199`) and `_constraint_table` (`:828`) walk
  `nodes` but index only bank keys and kept edges' keys.
- `values_of` (`:894`) and `deltas_of` (`:920`) address the bank through
  `keys`, which holds only nodes of kind `input` and `bank`.
- `run.py`'s three reads of `program.nodes` (`:1092`, `:1107`, `:1111`)
  are message paths keyed by an edge's own keys.
- `published_names()` is read in exactly one place,
  `solid_node/core/serializer.py:562`, where it is the set a MINTED
  binding name must not collide with. Shrinking it cannot make a
  collision; the minted names are `_b<n>`/`_j<n>` under a prefix
  lengthened while any published id matches, and a removed name is a
  qualified id or a `<ClassName>.<name>` fallback.

## 6. RED: the fixtures and the new tests, before the change

`SpringBank`/`SpringBankBody`, `Optional`/`OptionalBody` and
`OptionalRead` added to `tests/running_project/machine.py` (task 1.2),
with a new `PenSpring` leaf (a plain `TranslationalPort`) added to
`tests/running_project/parts.py` so the repeated leaf's port matches the
lock's shape. `tests/test_running_document.py` gained a
`NothingLeftOfADroppedEdgeTest` class (task 1.3) and two refusal tests in
`RefusalTest`; `tests/test_running_simulation.py` gained a
`ProgramReductionRunTest` class (task 1.4).

```
$ python -m pytest tests/test_running_document.py -q
...
SUBFAILED(machine='SpringBank') tests/test_running_document.py::PoseTest::test_every_free_name_the_document_reads_is_declared
FAILED tests/test_running_document.py::CoordinateTableTest::test_the_intermediates_are_the_plain_ports_the_program_computes
FAILED tests/test_running_document.py::NothingLeftOfADroppedEdgeTest::test_a_repeated_ports_document_publishes
FAILED tests/test_running_document.py::NothingLeftOfADroppedEdgeTest::test_a_wiring_a_kept_edge_computes_is_untouched
FAILED tests/test_running_document.py::NothingLeftOfADroppedEdgeTest::test_an_omitted_parts_driven_coordinate_publishes
5 failed, 67 passed, 2 warnings, 82 subtests passed in 6.10s
```

All five failures are the unfixed refusal, exactly as findings (a) and
(b) predict: `SpringBank`, `Optional(fitted=False)`, `Gauged` and
`PortDrivenJoint` still carry a name the old table kept. The other new
tests — `OptionalRead`'s two-way refusal test, and the three
`ProgramReductionRunTest` tests (the repeated bank's run follows the
untimed pose, and the identity is stable both in-process and against the
corpus) — are GREEN already on the unfixed tree, which is exactly what
design decision 2 and the proposal's "Nothing about the run changes"
claim: the run and the identity were never wrong, only publication was.

**Two pre-existing tests break as a direct, unavoidable consequence of
the fix, not anticipated by name in tasks.md, and corrected as part of
implementing 1.3** (the proposal's own "Impact" section calls for "the
publication tests for those [`Train`, `Gauged`, `PortDrivenJoint`]" to be
updated, which is exactly what these are):

- `CoordinateTableTest.test_the_intermediates_are_the_plain_ports_and_nothing_else`
  asserted `Train`'s `intermediates == ['wheel.turn']`. `wheel.turn` is
  `Train`'s ONLY intermediate (`wheel = Wheel(turn=spindle)`, a wiring
  OUT of the bank that nothing reads back), so after the fix `Train` has
  none. Renamed to
  `test_the_intermediates_are_the_plain_ports_the_program_computes` and
  rewritten to assert `Train`'s `intermediates == []` alongside
  `PortDrivenSmooth`'s `['register']` — the port a KEPT edge genuinely
  computes, the positive case the old test's name promised and never
  tested.
- `RefusalTest.test_an_id_that_cannot_be_qualified_is_refused` corrupted
  an arbitrary node of `Train`'s `program.nodes` of kind `intermediate`
  to synthesize the unqualified-fallback shape, with the docstring
  "nothing in the framework's suite or in any surveyed project produces
  an unlinked end today". After the fix `Train` has no intermediate node
  left to corrupt (`self.fail('the fixture has no intermediate to
  unqualify')` would fire), so the corruption is retargeted at
  `PortDrivenSmooth` (whose `register` survives the reduction). The
  docstring's claim is also now literally false — `OptionalRead(fitted=False)`
  is a REAL, non-synthetic machine that reaches this refusal — so a new
  test, `test_an_omitted_part_a_kept_edge_still_reads_is_refused`, asserts
  that directly and the old docstring's sentence was dropped.

## 7. GREEN: the fix

`compile_program` (`solid_node/simulation/program.py`), immediately
after `kept = _reaching_the_bank(candidates, bank_keys)` and before
`_refuse_opaque`:

```python
    kept = _reaching_the_bank(candidates, bank_keys)
    # `_register` made a node for every end of every CANDIDATE, before
    # `_reaching_the_bank` decided which ones survive -- it cannot know
    # a candidate will be dropped until the walk above has run. A
    # coordinate no kept edge reads or gives is not part of the
    # program: its relation is left to the ordinary enumeration, and
    # the table the rest of `Program` reads as "what this program
    # computes" must not go on carrying it.
    touched = set(bank_keys)
    for edge in kept:
        touched.update(edge.needs)
        touched.update(edge.gives)
    nodes = {key: node for key, node in nodes.items() if key in touched}
    _refuse_opaque(kept, bank_keys, nodes)
```

`_Node`'s class docstring and a new comment on `Program.__init__`'s
`self.nodes = nodes` line (task 2.2) say what the reduced table holds and
why; `published`'s, `published_names`' and `_refuse_unqualified`'s own
docstrings needed no change; they already describe their behaviour in
terms of `self.nodes`; whatever `self.nodes` holds.

**Task 2.3, confirmed by reading:** `_refuse_opaque` reads `nodes[key]`
only for the needs of KEPT edges, all of which survive the reduction by
construction (`touched` is built from `kept`'s own `needs`/`gives`).
`_ordered` seeds `resolved` with every node no kept edge determines;
dropping a key no kept edge NEEDS cannot change which edges become ready,
so the topological order is the same list either way. `_reaching_inputs`
and `_constraint_table` walk `nodes` but index only bank keys and kept
edges' keys — both present either way. `values_of` and `deltas_of`
address the bank through `self.keys`, which holds only nodes of kind
`input` and `bank` (never dropped). `described()` reads the inputs, the
coordinates, the spans and the edges, and reaches `nodes` only through
`edge.needs`/`edge.gives` — kept edges' own keys. `run.py`'s three reads
of `program.nodes[...]` (`:1092`, `:1107`, `:1111`) are all keyed by a
compiled edge's own `slot_key` or by keys drawn from `edge.needs`/
`edge.gives` of an edge the run is executing — always a kept edge's own
ends. No other line in `program.py` reads `Program.nodes` or the local
`nodes` inside `compile_program`.

```
$ python -m pytest tests/test_running_document.py -q
...
71 passed, 2 warnings, 83 subtests passed in 5.75s
```

Every RED test above is GREEN (the one `ByteIdentityTest` subtest that
newly fails at this point, `running_train`, is task 3.1's recapture,
below — expected, and closed before this count).

## 8. The recorded documents

**`tests/base_documents/running_train.json` (task 3.1).** Recaptured
with `test_running_document.py`'s own `document()` helper and
`ByteIdentityTest.normalized`'s `mtime` blanking, exactly the recipe
`test_every_document_with_no_control_is_unchanged_in_every_byte` reads
it back with. The diff is two edits, nothing else:

```diff
-    "intermediates": [
-      "wheel.turn"
-    ],
+    "intermediates": [],
@@
       "spindle": [
         "crank"
-      ],
-      "wheel.turn": []
+      ]
```

**`tests/running-corpus.json` (task 3.2).** Regenerated with
`python tools/generate_running_corpus.py`
(`14 scenarios over 12 machines ..., 276 ticks, 185444 bytes`, same
machine count and byte count order as before regeneration). A structural
diff (parsed JSON, not text) shows exactly two changes, both inside the
two `Train` entries (`machines[0]`, dt=0.05; `machines[1]`, dt=0.1):

```
DIFF machines[0].document.program.intermediates ['wheel.turn'] -> []
ONLY IN BEFORE: machines[0].document.program.sources.wheel.turn
DIFF machines[1].document.program.intermediates ['wheel.turn'] -> []
ONLY IN BEFORE: machines[1].document.program.sources.wheel.turn
```

No tick, no script, and no machine list entry changed; `CORPUS` in
`tools/generate_running_corpus.py` was not touched, so no machine was
added. `tests/test_running_corpus.py` is green after the regeneration
(`8 passed, 42 subtests passed`).

**The browser viewer carries a stale copy.** The solid-node-viewer
repository (`solid-node-viewer/solid_node_viewer/widget/src/running-corpus.json`,
per the shop's CLAUDE.md "solid-node-viewer work") carries a
byte-for-byte COPY of this framework's `tests/running-corpus.json`, kept
in step by hand rather than by any build step. This change makes that
copy stale in exactly the two bytes above (`Train`'s `intermediates` and
`sources`). Refreshing the viewer's copy is a viewer-repository
follow-up outside this change's scope — the viewer repository is not
touched here, per this task's instructions and the shop's own repository
boundary (CLAUDE.md, "solid-node-viewer work": its own history,
OpenSpec records and changelog, never folded into a framework cycle).

**The other six base documents (task 3.3).** `git status` after the
recapture shows exactly one modified file,
`tests/base_documents/running_train.json`; the other six
(`deep_project`, `meta_project`, `flexible_project`, `expression_project`,
`looping`, `untimed_train`) are untouched, and
`ByteIdentityTest.test_every_document_with_no_control_is_unchanged_in_every_byte`
passes over all seven (part of the 83 subtests above).

## 9. Proof

**Task 4.1.** The five files tasks.md names, green:

```
$ python -m pytest tests/test_running_document.py tests/test_running_simulation.py \
      tests/test_running_stops.py tests/test_running_jumps.py tests/test_running_corpus.py -q
250 passed, 2 warnings, 483 subtests passed in 31.99s
```

The whole suite, green, run from the worktree root:

```
$ python -m pytest -q
2647 passed, 4 skipped, 50 warnings, 1493 subtests passed in 373.47s (0:06:13)
```

Zero `FAILED`/`ERROR` lines. The 4 skips are pre-existing (unrelated to
this change; not investigated further, per the briefing's scope).
Against the task 1.1 baseline (`144 passed, 2 warnings, 141 subtests
passed` over the three touched files alone), the touched-file counts grew
by the new fixtures' tests (144 -> 250 across five files, most of that
increase from files not in the 1.1 baseline: `test_running_stops.py` and
`test_running_jumps.py`), and no count anywhere shrank.

**Task 4.2.** `probe_repeat_port.py` and `probe_omitted.py` re-run
against the changed worktree; both refusals are gone:

```
repeat port    : nodes   [('lift', 'input', True), ('slider.travel', 'bank', True)]
repeat port    : edges   ['lift drives slider.travel']
repeat port    : published intermediates []
repeat port    : published sources       ['lift', 'slider.travel']
...
fitted=False: nodes   [('crank', 'input', True), ('first.turn', 'bank', True)]
fitted=False: published intermediates []
read=False  : published -> UnsupportedLaw: the program names 'Arbor.turn', ...
```

`Reader`(`read=False`)'s refusal is unchanged, exactly as design decision
4 requires — its `spare.turn` is read by a KEPT edge.
`probe_repeat_joint.py` re-run: unchanged, still `DriverIdError` inside
`qualified_coordinates` during bank enumeration, before any program
exists — out of this cycle's reach, exactly as design decision 6 says.
`probe_pruned.py` re-run against the fixed framework: its own pruning
step now removes nothing (`removed []` for all three probes, where it
previously removed the dropped nodes), because `compile_program` already
returns the reduced table; every downstream reading (`coordinates`,
`intermediates`, `sources`, `identity unchanged: True`,
`Reader`(`read=False`) still refusing) is identical to what the real fix
produces. `probe_pruned.py`'s predictions all matched; nothing it
predicted differed from `probe_repeat_port.py`/`probe_omitted.py`'s own
direct measurement.

**Task 4.3.** `projects/Locks/Pin_tumbler_lock`'s working tree was never
touched. A copy (rsync, excluding `_build` and `.git`) was made at
`/tmp/claude-1000/-home-asa-devel-libresolid-studio/dce8b626-1634-48d1-bcc7-241282565e40/scratchpad/lock-copy/`, and its springs restored to the shape
the project's own git history carried before the migration to
`Time.running()` (commit `72df8b9`, `simulation/lock.py`, before the
`s1`…`s5` workaround): `springs = PenSpring().repeat(5)`, driven by ONE
relation grouping the five key-pin lifts with `&` and a law factory
reading `target.index` to pick each copy's own source —

```python
springs = PenSpring().repeat(5)
...
(plug.p1.lift & plug.p2.lift & plug.p3.lift & plug.p4.lift
 & plug.p5.lift).drives(springs.height, law=spring_height)
```

— with `spring_height` in `simulation/flexibles.py` restored from the
migrated single-source factory `(key_pin, spring) -> lambda lift: ...`
to the original grouped factory `(sources, target) -> lambda *lifts:
SPRING_HEIGHT - lifts[target.index]`, and the now-redundant `springs`
property on `PinTumblerLock` removed (`.repeat()` already provides
`self.springs` as the realized list). `solid build`, run from the copy
with `PYTHONPATH="/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts"`,
exits 0 and writes
`_build/viewer.json` (version 5, `program` present). Read back:

```
program present: True
intermediates: []
springs children: ['springs-0', 'springs-1', 'springs-2', 'springs-3', 'springs-4']
PenSpring in program: False
springs-0 in program: False
```

— the document publishes, no copy's name appears anywhere in `program`,
and the tree still carries all five copies. A `Sim` run confirms the
restored grouped law is not merely publishable but PHYSICALLY correct:
after withdrawing the key (cuts 6, 1, 2, 5, 0), the five springs' heights
diverge independently (`18.991, 22.741, 21.991, 19.741, 23.491`),
matching each spring's own pin rather than one shared value. This is
strictly more than the fallback tasks.md allows for — the originating
project's own shape (not the reduced `SpringBank` fixture) is confirmed
to build and publish. Build artifacts (`_build/`) were removed from the
scratchpad copy after the check; the copy itself is left at
`/tmp/claude-1000/-home-asa-devel-libresolid-studio/dce8b626-1634-48d1-bcc7-241282565e40/scratchpad/lock-copy/` for the reviewer's own
inspection, and `projects/Locks/Pin_tumbler_lock` shows no `git status`
change at any point during this work.

One thing worth recording for the reviewer: the naive restoration —
`springs = PenSpring().repeat(5)` with FIVE separate
`plug.pN.lift.drives(springs.height, law=spring_height)` calls, one per
pin, each addressing the same broadcast — is NOT how the framework
expresses "N independent sources into N repeat copies". `RepeatDeclaration`
has no `__getitem__` (`'RepeatDeclaration' object is not subscriptable`,
confirmed live), so a copy cannot be indexed at class-body declaration
time; and two separate relations into the same broadcast driven end
raise `DoublyBound` at `Sim()` construction (confirmed live:
`springs-0.height would be bound by the relation d2.lift drives
springs.height, copy springs-0 and by the relation d1.lift drives
springs.height, copy springs-0`), because a broadcast relation expands to
EVERY copy, not to one. The `&` group-plus-index-selecting-law shape
above is the framework's actual, and only, mechanism for this — it is
what the lock's own author used before the migration, not something
invented for this evidence.
