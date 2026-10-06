## Context

### Where a copy's `index` is set, and what runs before it

`RepeatDeclaration.realize` (`machinome/node/declarative.py:693`) realizes
each copy through the declaration it holds,
`self.declaration.realize(values, owner)` (`:709`). It then stamps
`child.__dict__['index'] = index` (`:717`) after that construction has
returned. `ChildDeclaration.realize` (`:512`) constructs the child with a
plain call, `child = self.node_class(*args, **kwargs)` (`:543`).

Inside that call, `AbstractBaseNode.__init__` (`machinome/node/base.py`)
does the following, in order:

1. it resolves the declared parameters;
2. it runs `self.check()` (`:605`) on a declarative class;
3. it calls `resolve_declared_joints(self)` (`:625`,
   `machinome/motion/joints.py:1609`), which resolves every
   class-declared joint's `axis`, `at`, `range` and `carries` against the
   instance;
4. it calls `resolve_declared_frames(self)` (`:631`,
   `machinome/node/frames.py:337`), which does the same for every
   declared frame.

The children are realized only after all of these. ADR-088 put joint
resolution at this point on purpose: it is the earliest point a value
could be wrong, so a refused instance has realized nothing.

A function given as a whole argument is called with the node
(`resolved_vector`, `joints.py`; `Joint._span` for a whole `range`).
Any exception it raises is wrapped as `ParameterError: <Class>.<joint>:
<argument> -- the callable raised <Type>: <message>`. So on a copy, every
function that reads `node.index` runs before `index` exists, and is
refused. A relation's `law=` or `ratio=` is resolved when the parent
simulates, long after the stamp, which is why the same read works there
(ADR-096).

Two existing statements record this timing:

- the comment at `:710-716`: "No sighting needs `index` during
  construction";
- ADR-096's decision bullet: "stamped on `child.__dict__` AFTER
  construction".

The comment also says why the stamp was not made earlier through a
context slot: "a legacy (non-declarative) child calls super().__init__()
LAST, after building its own children, so a slot consumed during
__init__ would land on the wrong node."

### Reproduction at `20b3257`

The probes are in the campaign scratchpad
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle4/`).
Each is run as `env -C <bench> PYTHONPATH=<bench> .venv/bin/python <probe>`.
`machinome.__file__` printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.
`repro_repeat_index.py` sits beside a throwaway `pyproject.toml`, which
gives its fixture classes a project root. It builds six cases. Each has a
`Solid2Node` cube leaf, repeated twice by an `AssemblyNode`:

| Case | Declared on the repeated class | Unmodified bench | With `PROBE_SEED=1` |
|---|---|---|---|
| axis, at, range | `Revolute(axis=λ (0,0,±1), at=λ (10·index,0,0), range=λ (0, 90+index))` | `ParameterError: Guide.turn: axis -- the callable raised AttributeError: 'Guide' object has no attribute 'index'` | `((0,0,1),(0,0,0),(0,90))`, `((0,0,-1),(10,0,0),(0,91))` |
| each copy bound to 30 | the same | the same refusal | copy 0: `[['r','30',[0,0,1]]]`; copy 1: `[['t',['-10.0','-0.0','-0.0']], ['r','30',[0,0,-1]], ['t',['10.0','0.0','0.0']]]` |
| carries | `Orbit(axis=(0,0,1), carries=λ (5+index,0,0))` | `ParameterError: Roller.spin: carries -- ... no attribute 'index'` | `(5,0,0)`, `(6,0,0)` |
| frame | `Frame(at=λ (0,0,3·index))` | `ParameterError: Seated.seat: frame argument at -- ... no attribute 'index'` | frames at `(0,0,0)`, `(0,0,3)` |
| check() | `size = Length(1.0)`; `check()` stores `self.index` | `AttributeError: 'Checked' object has no attribute 'index'` | `[0, 1]` |
| another failure | `Revolute(axis=λ node.no_such_thing)` | `ParameterError: Wrong.turn: axis -- the callable raised AttributeError: 'Wrong' object has no attribute 'no_such_thing'` | the same |

(`λ` abbreviates `lambda node:`; the script's source is in `evidence.md`.)
`PROBE_SEED=1` patches `ChildDeclaration.realize` and
`RepeatDeclaration.realize` at run time into Decision 2's shape. Its
output is `repro-probe-seed.txt`, and the unmodified run's is
`repro-unmodified.txt`.

### Suite under the probe

`seed_probe.py` installs the same shape from outside the bench as a
pytest plugin. A copy goes through the seeding path, and a child that is
not a copy is constructed by the original method. Each seeded copy is
logged. The run was the full suite at the bench root, alone:
`env -C <bench> PYTHONPATH=<bench>:<scratch> SEED_PROBE_LOG=<scratch>/seed-probe.log
.venv/bin/pytest -p seed_probe -q -p no:cacheprovider`, and it ended
with exit 0 after 652 s wall. Its result: **4634 passed, 4 skipped, 55
warnings, 6619 subtests passed in 649.29 s.** The probe log recorded 379
copies, from 20 distinct repeated classes, constructed through the
seeding path. A build that a test runs in a subprocess does not carry
the probe, so the count covers only the suite's in-process paths.

For comparison, the unmodified bench at `20b3257` reads `4634 passed,
4 skipped, 6619 subtests passed`. That count is from the final suite of
`children-refuse-early-reads`, whose implementation commit is
`20b3257`.

### The catalogue

A grep of `projects/` on 6 October 2026 (worktrees and `_build` excluded)
found these reads of `index`:

- `lambda node: ... node.index` appears once:
  `3DPrintedClocks/simulation/shared/motion.py:684`, an `at=` on
  `MotionWorksPart`. There `index` is a declared `Count` parameter, the
  working case, and `_check_index` refuses such a class as a repeat.
- Two `hasattr(self, 'index')` guards, in Vibecoded-demos/v8-engine
  (`valvetrain/valve_motion.py:84` and `cylinders/cylinder_unit.py:93`).
  They tell a repeat's copy from a standalone root. Both are in
  `simulate()`, after construction, where a copy has `index` today and
  will still have it.

A read of a copy's `index` during construction raises today, so no
working model makes one. Nothing that realizes today reads differently
after this change: the only reads that change are ones that used to fail.

### The originating project at `20b3257`

`projects/3D-Printers/Prusa3-vanilla`, branch `master`, `77bf9d8`, clean
tree. Its README documents `machinome test --faceted simulation/prusa_i3.py`.
`--faceted` is now `--mesh` (`machinome test --help`). The run was
`env -C <Prusa> PYTHONPATH=<bench> .venv/bin/machinome test --mesh
simulation/prusa_i3.py`, exit 1, 169 s wall, with this result: `Ran 19
tests in 164.90 seconds: 17 passed, 2 failed (mesh engine, volume
epsilon 0 mm³)`. The two failures are both `assertBlockedBeyond` under
the mesh engine:

- `test_the_gear_pair_drives_at_every_feed`: `big_gear should be blocked
  at 1.5deg against small_gear (no intersection)`;
- `test_x_home_meets_the_switch`: `bearings-0 should be blocked
  displaced 1.0mm along [-1, 0, 0] against switch (no intersection)`.

Neither involves a function of `index`, and both are present on the
unmodified bench, so they are not this change's. The project's
`XAxis.guides` and `YAxis` guides declare their `spin` at the site
(ADR-098), and its repeats (`bed.py`, `extruder.py`, `endstop.py` and
others) declare no function of `index`. The project is the check that a
repeat-heavy machine realizes, binds and measures unchanged.

## Goals / Non-Goals

**Goals:** a `.repeat()` copy's `index` is readable by everything its
own construction runs, so a class-declared joint or frame argument given
as a function of the copy's position resolves per copy. Everything else
stays as it is: when arguments resolve, what a site's or a mate's
function is handed, a repeat's single identity, and the refusal of a
function that fails for another reason.

**Non-goals:**

- moving joint resolution;
- retrying a failed function;
- a new message for a non-repeated `index` read;
- handing a site's function the copy;
- any change to a project;
- any new public name.

## Decisions

### 1. The copy carries `index` before its construction; resolution does not move

The finding names two candidates.

- **Resolve a repeated class's joint arguments after `index` is
  assigned.** Taken literally, `resolve_declared_joints` would skip a
  copy inside `__init__` and `RepeatDeclaration.realize` would resolve
  its joints after the stamp. Inside `__init__`, though, nothing says the
  node is a copy. Telling it so needs a value placed before `__init__`
  runs, which is the channel this decision uses for `index` itself. It
  would also realize the copy's children before its joints resolve,
  breaking ADR-088's "a refused instance has realized nothing". And it
  would leave frames and `check()` unable to read `index`, so each would
  need the same move.
- **Defer an `AttributeError` and retry.** This would change when the
  refusal comes, for every class, to serve one case:
  - every function failure would be held, not only one reading `index`;
  - frames would need the same treatment;
  - the realization path would need a second resolution site.

  The message the candidate asks for already exists:
  `resolved_vector` names the class, the joint, the argument and the
  underlying `AttributeError` with its attribute.

**Taken: the first candidate's intent, made smaller.** Resolution does
not move. What moves is the stamp, to before the copy's construction. One
allocation-time write into the copy's own instance dictionary makes
`index` readable by `check()`, joint arguments and frame arguments alike,
at ADR-088's point. No signal crosses into `__init__`, no resolution site
is added and no refusal changes timing.

The concern the stamp's comment records is a slot consumed during
`__init__` landing on the wrong node. It does not arise: the value is
written on the one object being constructed, not into any shared slot,
so a grandchild a legacy `__init__` builds first never sees it.

### 2. The code shape

In `machinome/node/declarative.py`:

```python
class ChildDeclaration:
    def realize(self, values, owner, index=None):
        """... `index`, given only by `RepeatDeclaration.realize`, is the
        copy's position: it is in the copy's instance dictionary before
        the copy's constructor runs (see `_construct`)."""
        ...                                   # unchanged up to the call
        child = self._construct(args, kwargs, index)
        ...                                   # unchanged after it

    def _construct(self, args, kwargs, index):
        """Construct this declaration's child. A repeat's copy is
        allocated, given its `index`, and only then initialized, so
        everything its construction runs -- `check()`, its class-declared
        joint and frame arguments -- reads its position. This is the
        protocol `type.__call__` follows, with one write between its two
        steps. Any other child is a plain call of its class."""
        node_class = self.node_class
        if index is None:
            return node_class(*args, **kwargs)
        child = node_class.__new__(node_class, *args, **kwargs)
        if isinstance(child, node_class):
            child.__dict__['index'] = index
            type(child).__init__(child, *args, **kwargs)
        return child
```

and in `RepeatDeclaration.realize`:

```python
        for index in range(count):
            child = self.declaration.realize(values, owner, index=index)
            # Seeded before construction (ChildDeclaration._construct) and
            # stamped again here, so the copy ends with its position even
            # if its own constructor assigned an `index`.
            child.__dict__['index'] = index
            copies.append(child)
```

- `isinstance` before `__init__`, and `type(child).__init__`, are what
  `type.__call__` does. No metaclass in `machinome/` or in the catalogue
  defines `__call__` (grep of 6 October 2026), so the two-step call
  constructs exactly what the plain call did.
- `realize_children` keeps calling `realize(values, owner)`, so a
  listed or single child takes the plain call, unchanged.
- The stamp after construction is kept, so a legacy constructor that
  assigns its own `index` still ends with the framework's position, as
  today. `_check_index` already refuses a class that declares `index`.
- `_check_index`'s docstring ("stamped as a plain instance attribute")
  stays true. The `resolve_declared_joints` docstring describes site and
  mate joints only, and is untouched.

### 3. What a function of a copy sees

A function given as a class-declared joint or frame argument of a
repeated class is called with the copy itself, exactly as it is for any
class-declared argument. During construction the copy has:

- its `index`;
- its resolved declared parameters (`node.<parameter>`);
- everything its class carries: declarations, methods and constants;
- whatever its own constructor set before the joint resolution point. On
  a legacy class that is what its `__init__` assigns before
  `super().__init__()`. On a declarative class it is `_parameters`,
  `uniq_id`, and a `name` that is the class name or the `name=` passed.

The copy does not yet have:

- the name its parent gives it (`guides-0`, set by `realize_children`
  after realization);
- a parent (not linked);
- children (realized after its joints and frames);
- a placement;
- anything its `render()` produces.

Everything above is what a non-repeated instance's function sees, plus
`index`. A site-declared joint's function and a mate's freedom function
are handed the declaring parent or the assembly (ADR-098, ADR-150), never
the copy, so they cannot read the copy's `index`. That is unchanged.

### 4. ADR-096 is amended, not superseded

ADR-096's decision bullet "A copy carries `index`" states the stamp is
made "AFTER construction". The decision itself stands: `index` is a
plain 0-based attribute, not a parameter, not identity, not a child
name, and refused where the class already answers to it. Only when it
becomes readable changes. Following the log's own rule
(`docs/adrs/README.md`: "amend it in place with a dated *Amendment*
section"), ADR-096 gets an "Amendment (2026-10-06, change
`resolve-repeated-joints-per-copy`)" that says:

- the copy's `index` is written into its instance dictionary before its
  constructor runs, and again after;
- so a class-declared joint or frame argument and `check()` read it;
- the identity, naming and refusal rules are unchanged.

The ADR index line for ADR-096 gains "amended 2026-10-06". ADR-098 is
not edited. Its Callables section gives the stamp's timing as the reason
a site's function cannot see a copy's `index`. That reason is now stated
differently (the function is handed the parent), but the decision it
supports, handing a site's function the parent, is unchanged. No new
ADR: this adds no mechanism and moves no responsibility (Open Question
1).

### 5. Spec: one requirement added to `declarative-nodes`

"A repeated copy carries its position throughout its own construction",
with five scenarios:

- per-copy `axis`, `at` and `range`, resolved and bound (the finding);
- `carries`;
- a frame argument and `check()`;
- a function failing for another reason, and a non-repeated instance
  reading `index`;
- a site's function and a legacy constructor's own `index`.

It sits beside the requirement "Class-body child declarations", whose
sentence "Every child a repeat realizes SHALL carry its own 0-based
position in the repeat, readable on the realized node as `index`" it
refines in time. No existing requirement is edited, because nothing in
them states the old timing. In the `joints` spec, "Joint arguments
resolve against the instance at realization" already calls a
class-declared argument's function with "the node itself", and its
sentence "a copy's own position SHALL NOT be handed to the callable"
concerns a site joint on a repeat. That stays true.

### 6. Manual and changelog

- `docs/concepts/joints.rst`, "Arguments": the sentence "A `repeat()`
  copy's `index` does not exist yet when its joint arguments resolve, so
  derive a per-copy joint argument from the parent's placement, or drive
  the per-copy difference through a broadcast relation's `law=`." is now
  wrong. It is replaced in place by one sentence no longer than it:
  "A ``repeat()`` copy carries its ``index`` while it is constructed, so
  a callable declared on the repeated class may read ``node.index``; one
  passed where the child is declared is handed that parent instead."
- `docs/architecture.md`:
  - `:877`: the parenthetical "(not yet assigned when a site's arguments
    resolve)" becomes "(it is handed the parent, not the copy)".
  - `:1150`: "`RepeatDeclaration.realize` stamps AFTER construction"
    becomes "that `RepeatDeclaration.realize` writes before the copy's
    construction runs".
- `docs/project/changelog.rst`: one bullet under `Unreleased` naming
  `resolve-repeated-joints-per-copy`. A `repeat()` copy's `index` is now
  readable while the copy is constructed, so a joint's `axis`, `at`,
  `range` or `carries`, a frame argument and `check()` can read it, where
  realization used to refuse with `... has no attribute 'index'`.

`docs/howto/repeat-and-vary.rst` says only that every copy carries
`index`, which stays true, so it is not edited.

## Proof plan

- **Red** (tests/test_declarative_nodes.py, a new
  `RepeatIndexDuringConstructionTest` after `RepeatIndexTest`; tasks §2):
  - per-copy `axis`, `at` and `range`, read through
    `declared_joints(type(copy))['turn'].arguments(copy)`;
  - the bound placements of both copies at 30;
  - per-copy `carries`;
  - a frame `at` read through `resolved_frames`;
  - `check()` reading `self.index`.

  Each is refused on the unmodified bench with the reproduction's
  messages.
- **Guards** (green before and after):
  - the other-failure refusal, naming `no_such_thing`;
  - the same class realized as one plain declared child, refused naming
    `index`;
  - the copies' shared `uniq_id`;
  - a legacy repeated class that assigns `self.index = -1` before
    `super().__init__()` ends with `0` and `1`;
  - a legacy repeat (`Guard`) realizes with names and positions;
  - the existing `RepeatIndexTest`, `SiteJointCallableTest` (its
    site-callable test included) and `ArgumentResolutionTest` in
    `tests/test_joints.py`.
- **Framework reach:** the full suite, which under the outside probe
  measured every repeat a test realizes (Context, "Suite under the
  probe").
- **Originating project:** Prusa3-vanilla's documented run before and
  after, at its count (17 passed, 2 failed, the same two), its tree
  unchanged.

## Risks / Trade-offs

- **A construction-time `hasattr(self, 'index')`.** Code that asked,
  during construction, whether the node is a repeat's copy used to get
  `False` and now gets `True` on a copy. The catalogue's two such guards
  are in `simulate()`, where the answer does not change (Context).
- **A class overriding `__new__` or a metaclass overriding `__call__`.**
  The copy is built by the two steps `type.__call__` takes. A metaclass
  `__call__` would be bypassed for copies only. None exists in the
  framework or the catalogue. A `__new__` override still runs, and a
  `__new__` that returns another type skips `__init__`, as the plain
  call does.
- **Per-copy arguments under one identity.** Copies now can resolve
  different joint arguments while sharing one `uniq_id`. The `joints`
  requirement already says joint arguments are not identity, and two
  instances that differ only in a joint argument share artifacts. The
  copies' geometry is still one.

## Migration Plan

None. A model that realizes today realizes identically. A project that
worked around the finding may move its per-copy argument back into the
repeated class as a function of `node.index`, in its own repository, when
it chooses.

## Open Questions

1. **Amend ADR-096, or leave the ADRs alone?** Answered by the
   orchestrator at review. There are two choices, and both fix the
   finding:
   - **(a) Amend** (delivered here): a dated Amendment section on
     ADR-096 and its index line. This follows the ADR log's own rule for
     a decision whose stated mechanism changes.
   - **(b) Leave the ADRs.** The ADR keeps saying "AFTER construction",
     and the code and spec say otherwise.

   Recommendation: (a). ADR-096 states the timing as part of its
   decision, so leaving it would leave the decision log contradicting
   the code. Answered at review (6 October 2026): (a).
2. **A catalogue load sweep?** Answered by the orchestrator at review.
   This change alters how every repeated copy in the catalogue is
   constructed. `scripts/load-projects` (about 22 minutes on 4 October)
   would load every model before and after. Recommendation: not
   required for this cycle. The only reads whose outcome changes are
   construction-time reads of a copy's `index`, which raise today, and
   the catalogue grep finds none (Context). The full suite under the
   probe and Prusa3-vanilla's repeat-heavy machine cover the
   construction path itself. If the orchestrator runs one, it is a
   workspace command run by the orchestrator, and the brief keeps
   hangprinter and OpenCycloid out. Answered at review (6 October
   2026): not required for this cycle; the campaign loads every
   catalogue model once at close.
