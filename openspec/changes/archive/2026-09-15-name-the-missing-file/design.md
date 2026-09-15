# Design — name the missing file

Every mechanism claim below cites `file:line` in this worktree at `55d16e7`;
every behavioural claim it rests on is a probe in `evidence.md`.

## The mechanism as it stands

### Four adapters bind a node to a file outside Python

| adapter | attribute | resolved at | stored on | returned by `get_source_file` |
| --- | --- | --- | --- | --- |
| `StlNode` | `stl_source` | `stl.py:167-170` | `self.stl_source` | `stl.py:182-183` |
| `StepNode` | `step_source` | `step.py:481-484` | `self.step_source` | `step.py:493-494` |
| `JScadNode` | `jscad_source` | `jscad.py:31-34` | `self.jscad_source` | `jscad.py:37-38` |
| `OpenScadNode` | `scad_source` | `openscad.py:38-41` | `self.openscad_source` | `openscad.py:52-54` |

All four resolve the declared name against the directory of the module that
defines the subclass and `os.path.realpath` the result; all four then hand
that path to `AbstractBaseNode.__init__`, which stores it as `self.src`
(`base.py:675`) and derives `basedir`, `build_dir` and every artifact path
from it (`base.py:682-702`). Every other leaf adapter authors its geometry in
Python and its `src` is the module file itself (`base.py:798-800`,
`inspect.getfile`), which exists by construction.

Three of the four already refuse a subclass that declares NO file, at
construction: `stl.py:161-165` and `step.py:475-479` raise `ValueError`
naming the class; `jscad.py:28-30` raises a bare `Exception` that names
only "OpenJScadNode subclass", not the class (reviewer's correction —
filed as a wart beside the `OpenScadNode` gap, not fixed here).
`OpenScadNode` has no such check (out of scope; see the proposal).

### The file itself is never checked

Nothing between the `realpath` and the first read asks whether the path is
there. The first thing that touches the filesystem is

    base.py:1039   return max(os.stat(path).st_mtime_ns for path in self.files)

inside `mtime_ns`, over `self.files` — which includes `self.src`. `os.stat`
raises `FileNotFoundError` with the bare path and no node context, and that is
the whole of today's failure for a missing file (`evidence.md`, measurement 1).

`OpenScadNode` is the one partial exception: it reads the file during
construction (`openscad.py:45`, `coherent_read(self.openscad_source)`), so it
fails at the right MOMENT already — with the same contextless
`FileNotFoundError` (`evidence.md`, measurement 1, `MissingScad`).

### A directory passes every check there is

`os.stat` succeeds on a directory, so `mtime_ns` answers a number for a
`stl_source`/`step_source` naming one (`evidence.md`, measurement 3). The build then reaches the
foreign reader: `trimesh.load` (`stl.py:63`) raises `string is not a file:
…`, and the STEP reader (`step.py`, `STEPCAFControl_Reader`) prints an OCCT
`Standard_Failure: input in flex scanner failed` to the terminal before the
framework's own `could not read this STEP file` (`evidence.md`,
measurement 4). Neither names the
node, and the OCCT dump is not even a Python exception message.

### When a node is actually constructed

This matters because the declarative API does not construct children where
they are written. Measured (`evidence.md`, measurement 2):

- **Class definition constructs nothing.** `Rig`'s body writes
  `part = MissingStl()`; `Rig.__dict__['part']` is a `ChildDeclaration`
  (`declarative.py:255`), not a node — importing the module with the file
  absent succeeds.
- **Instantiating the PARENT realizes the child.** `Rig()` returns, and
  `rig.part` is a `parts.MissingStl` instance whose `src` does not exist.
  `ChildDeclaration.realize` (`declarative.py:454`, driven by `realize_children`, `declarative.py:940`) is called from the
  parent's own `__init__`: `realize_children(self)` at `base.py:754`, "last,
  so a child is constructed by a parent that already knows its own name,
  source and artifact paths" (`base.py:750-754`).
- **The root is instantiated by the loader**, inside `load_node`
  (`builder.py:327-329`), after every project module has been imported.

So "at construction" is unambiguous: it is the adapter's own `__init__`, the
same instant at which the missing-attribute failure already fires, and it
happens during `solid build`'s load step — after any module-level fetch a
project performs, and before any geometry is read.

### What the maker sees today, end to end (`evidence.md`, measurement 4)

```
ERROR - core.builder - parts:MissingStl: failed to inspect initial sources project: [Errno 2] No such file or directory: '…/absent.stl'
ERROR - core.builder - assembly:Rig: failed to assemble project: [Errno 2] No such file or directory: '…/absent.stl'
ERROR - core.builder - parts:DirectoryStl: failed to assemble project: string is not a file: …/a_directory
```

The first two name the MODEL reference (`builder.py:356-358` for the load-time one, and the `failed to assemble` wrapper for the other), never the node class or the attribute. For a
root that IS the leaf the model reference happens to name the class; for a
leaf inside an assembly — the normal case — it does not.

## The change

**One helper, called by the four adapters at the point they already
validate.**

1. A new function in `solid_node/node/sources.py` — the module that already
   owns "what files a node's source depends on", already imported by
   `stl.py:41` and `step.py:69`, and stdlib-only at the top (`ast`, `os`,
   `sys` plus `solid_node.source_generation`, itself stdlib-only,
   `source_generation.py:14-22`):

       require_source_file(klass, attribute, declared, path)

   It raises when `path` is absent or is not a regular file, and returns
   nothing otherwise. `os.path.exists` distinguishes the two cases so the
   messages differ.

2. Each adapter calls it immediately after its `realpath`, before
   `super().__init__` — `stl.py:170`, `step.py:484`, `jscad.py:34`,
   `openscad.py:41` (i.e. before `coherent_read` at `openscad.py:45`).

3. The message names, in one sentence: the class, the attribute and the value
   it was given, the module the path was resolved against, and the resolved
   absolute path. For a directory it says the path exists and is not a file.
   Shape (exact wording is the implementer's, these elements are the
   contract):

       Bracket declares stl_source = 'bracket.stl', resolved against
       …/parts.py, but …/parts/bracket.stl does not exist. An StlNode
       reads an existing STL file; create or fetch the file, or correct
       the declaration.

   `FileNotFoundError` for the absent case — it is what the framework raises
   today for a missing source and what a project's own `require()` raises
   (`Internal-Cycloidal-Actuator/simulation/actuator/source.py:51-56`);
   `ValueError` for the exists-but-is-not-a-file case, matching the other
   admission refusals in these adapters (`stl.py:162`, `step.py:476`).

4. `self.name` does not exist yet at that point (it is set by
   `super().__init__`), which is why the message is built from
   `self.__class__.__name__`, exactly as the missing-attribute failures above
   it already are.

### What deliberately does not change

- **A source removed after construction.** `mtime_ns` keeps raising
  `FileNotFoundError` from `base.py:1039`. That is a ratified behaviour with
  a test behind it — `tests/test_content_verified_currency.py:431-447`,
  "a missing file is a build failure, not a cache question" — and a build
  whose files move underneath it is a different event from a declaration that
  was wrong before anything ran. `tests/test_source_census.py:78-85` pins the
  same for a phase over a missing file.
- **The suite's own vanishing-source fixture.**
  `tests/test_builder_reload_resilience.py:68-78` declares a `JScadNode`
  whose `__init__` calls `super().__init__()` and THEN deletes its own
  `.js`, and the test asserts the builder reports a `FileNotFoundError` and
  waits for repair. Placing the check inside `JScadNode.__init__`, before
  that class's own `super().__init__()`, means the file is still present
  when the check runs — reproduced (`evidence.md`, measurement 5) — so that
  test's failure keeps coming from `mtime_ns`, unchanged.
- **The mesh-library deferral.** `tests/test_mesh_import_deferred.py` pins
  that importing `solid_node.node.base` must not import `trimesh`. The helper
  uses `os.path` only and lives in `sources.py`, so no import moves.
- **Scaffolds.** `solid new` writes a `Solid2Node`
  (`templates/project/root/__init__.py:1-4`); `solid import-step` reads the
  document through `StepAssembly` and writes source text
  (`import_step.py:1-20`, `_part_class_source` at `import_step.py:119-133`)
  — it constructs no `StepNode`, and its own input file must exist for it to
  read at all.
- **A project that fetches its source.** The catalogue's fetch scripts are
  standalone commands run before a build
  (`projects/Locks/Pin_tumbler_lock/tools/fetch-source.py`, a `main()`
  downloading into `upstream/`); they construct no nodes. A project that
  instead extracts at module import — the actuator's `require()` preamble —
  still runs strictly before `load_node` instantiates anything. Eager is what
  these projects already chose.

## Alternatives rejected

**A. Check in `AbstractBaseNode.__init__`, right after
`self.src = self.get_source_file()` (`base.py:675`).** One line covers every
adapter. Rejected: the base cannot name the DECLARING ATTRIBUTE — `src` is
just a path by then, and "which of `stl_source`/`step_source`/`jscad_source`/
`scad_source` do I fix" is most of the value of the message. It would also
legislate for every node kind, converting `inspect.getfile`'s own failure
mode for a Python-authored node into something else for no user-visible gain,
and it would move validation to a place that currently performs none.

**B. Check lazily, inside `mtime_ns`.** Rejected: `mtime_ns` is a currency
question asked repeatedly through a build, including on sources that have
legitimately moved mid-build, where `FileNotFoundError` is the ratified
answer (alternative A's tests above). Putting the diagnosis there would both
slow the hot path and overwrite a contract this change is not touching.

**C. Wrap the `FileNotFoundError` that `mtime_ns` raises with the node's
name.** Rejected on two counts: it still fails late, after the loader has
imported the whole project and the builder has taken the build directory; and
it cannot address the directory case at all, because there is no exception to
wrap — `mtime_ns` returns a number (`evidence.md`, measurement 3).

**D. Warn and substitute a placeholder shape.** Rejected: the originating
project's own rule is "a build never substitutes a placeholder shape for an
absent file" (`Internal-Cycloidal-Actuator/simulation/actuator/source.py:1-8`),
and a silently smaller machine is the failure mode ADR-116's cycle had just
finished removing.

**E. Check only `StlNode` and `StepNode`, as the wart names them.**
Rejected: `JScadNode` was measured to have the identical gap (`evidence.md`,
measurement 1), and
`OpenScadNode` has the identical message defect at the right moment. One
helper called four times is smaller than two helpers and a follow-up wart.

**F. Have `solid import-step` emit a `require()`-style preamble so the
generated source keeps the actuator's failure.** Rejected: it puts the
framework's job in generated project source, which the project then owns and
must maintain; the framework should simply fail well. The actuator's
`require()` keeps earning its place for the part the framework cannot know —
the extract command.

## Why this is not an ADR

No boundary moves. Each of these adapters already validates its own
declaration in its own `__init__` (`stl.py:161-165`, `step.py:475-479`,
`jscad.py:28-30`); this change adds a second condition at that same moment,
in a helper placed in the module those adapters already import. No new
component, no new lifecycle stage, no reversal of a recorded decision, and
nothing another change would need to read an ADR to understand.

If the reviewer rules that stating the rule family-wide in `node-model`
constitutes an architectural boundary, the next free number is **ADR-117**
(`docs/adrs/` ends at ADR-116, "an artifact import is anchored on the build
directory").

## Reviewer's notes (ratification, 2026-09-15)

Ratified as written, with these corrections and additions binding on the
implementation:

1. **`jscad.py:28-30` does not name the class.** The sentence above claiming
   three adapters "name the class" was wrong for `JScadNode`, whose
   missing-declaration failure is a bare `Exception` saying "OpenJScadNode
   subclass must declare". Corrected in place. Not fixed by this change —
   it goes to `workflow/warts.md` with the `OpenScadNode` `TypeError`, as one
   entry: the missing-declaration refusals are inconsistent across the four
   adapters.
2. **The message must not say "committed".** The originating project's rule
   is that its vendor STEP is obtained, never committed; the hint reads
   "reads an existing STL file" (corrected above). Same for the other three.
3. **The new test module is self-contained.** `tests/test_missing_source_file.py`
   creates and removes its own directory fixture in its own
   `setUpModule`/`tearDownModule`; it never depends on
   `tests/test_stl_node.py`'s `setUpModule` having authored anything, and the
   absent/directory classes are constructed nowhere else. Verified while
   reviewing: every STL/STEP fixture file is authored at test time by the
   module that uses it (none is tracked), and the other STEP test modules
   import `step_project.parts` only for its `__file__` — so no existing test
   constructs a fixture leaf before its file exists. Keep it that way.
4. **Prove the develop-mode reload path, not just the exception.** The
   builder wraps `load_node` with the same `_on_reload_exception(e, 'load')`
   (`builder.py:327-333`) it uses for the inspect stage, so a construction-
   time refusal should surface and wait for repair exactly as the vanishing-
   source case does — but that is a reading, not a measurement. Task 3.1b
   adds the test.
5. **`ValueError` for a directory** is accepted; `IsADirectoryError` was
   considered and rejected so that every declaration refusal in these
   adapters is one family.
6. **No ADR** is accepted: the rule is stated in `node-model` and no
   component or lifecycle stage moves.

### Amendment at implementation (reviewer, 2026-09-15)

Task 3.1b did its job: with the check placed before `super().__init__`, a
`JScadNode` root whose `.js` was absent from the start makes `load_node`
raise, so the builder handles it at stage `load` with no node and no file
set (`_on_reload_exception`, `builder.py:505-536`), falls back to
`_watch_broadly(())` — the entry directory, `.py` files only
(`builder.py:538-580`, filter at `builder.py:807-821`) — and a develop
session never notices the `.js` being created. Before this change the same
project failed one stage later, at `inspect initial sources`, where
`self.node.files` named the missing path and the watch was precise.

Ratified fix, preserving both the placement rule and the reload-repair
behaviour (no spec delta: the contract "a develop session waits for the
repair of a missing source" is unchanged, and the new test guards it):

1. `require_source_file` sets `filename` on the exception it raises to the
   resolved path — for `FileNotFoundError` and for the `ValueError` alike,
   as an attribute assigned after construction so `str(error)` stays the
   one-sentence message (constructing `FileNotFoundError(errno, msg, path)`
   would prefix `[Errno 2]` and append the path a second time).
2. `Builder._on_reload_exception`, on the reload path, adds
   `getattr(exc, 'filename', None)` (when set) to the sources handed to
   `_watch_broadly`, so a construction-time refusal is watched exactly like
   a missing contributor found at the inspect stage: the smallest existing
   parent is subscribed and the filter admits that exact path. The startup
   (non-reload) branch is unchanged: a broken project still fails fast.

Alternatives rejected: checking after `super().__init__` (the failure is
still at `load`; nothing gained); moving the check to the inspect stage
(alternative B above, and it would not name the attribute); having the
builder re-run `load_node` under a broad watch until it succeeds (already
what happens for `.py` repairs, and it cannot see a foreign file appear).

**Correction (reviewer, 2026-09-15, after the amendment's first test run).**
Point 1 above was wrong about Python: `OSError.__str__` renders
`[Errno None] None: '<path>'` as soon as `filename` is set, however it was
set, so assigning the attribute after construction breaks the message
(reproduced in `evidence.md`, "Reload-repair regression — fix"). The
ratified mechanism is instead a named subclass in `sources.py`:

    class MissingSourceFile(FileNotFoundError):
        def __init__(self, message, path):
            super().__init__(errno.ENOENT, message, path)
        def __str__(self):
            return self.strerror

so `errno`, `strerror` and `filename` are the standard `OSError`
attributes (the builder keeps reading `filename`, which also lets it watch
the file any other `OSError` raised at load names), `isinstance(error,
FileNotFoundError)` stays true for every caller, and `str(error)` is the
one-sentence message. The directory case stays a `ValueError` with
`filename` assigned after construction: `ValueError.__str__` reads only
`args`, so that rendering is unaffected (the two directory tests passed in
the same run). Point 2 (the builder) is unchanged.

**Second correction (reviewer, 2026-09-15).** The develop-mode error text
(`errors.json`, built from `traceback.format_exc()`) names the concrete
class, `solid_node.node.sources.MissingSourceFile`, not the literal
`FileNotFoundError` the 3.1b test asserted. That is the intended
user-visible spelling — a maker reading the develop error sees the
refusal's own name above the one-sentence message — so the test asserts
`MissingSourceFile` in that text; the type relationship
(`isinstance(error, FileNotFoundError)`, `errno == ENOENT`) is asserted in
`tests/test_missing_source_file.py`.
