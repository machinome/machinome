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
