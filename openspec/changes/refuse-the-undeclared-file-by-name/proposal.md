## Why

Two findings recorded together in `workflow/warts.md`, section
"name-the-missing-file (2026-09-15, found while fixing)", both left out of
that cycle's ratified scope. The cycle that found them gave every adapter
one refusal for a file that is declared but not there; it left alone the
refusal for a file that is not declared at all, and the builder's own line
around both.

**1. The four adapters refuse a missing declaration inconsistently.**

> **The four adapters refuse a missing DECLARATION inconsistently.**
> `StlNode` and `StepNode` raise `ValueError` naming the class
> (`stl.py:162`, `step.py:476`). `JScadNode` raises a bare `Exception`
> that names only `"OpenJScadNode subclass"`, never the actual subclass
> (`jscad.py:28-30`). `OpenScadNode` has no check at all: an
> undeclared `scad_source` reaches `os.path.join(basedir, None)` and
> raises `TypeError: join() argument must be str, bytes, or os.PathLike
> object, not 'NoneType'` (`openscad.py:40`), naming neither the class nor
> the attribute. [...]

Reproduced on the bench `fix-warts-3` at `bad5ebe` with a scratch fixture
project (design.md, Context). Constructing a subclass that declares no
source:

| Leaf | What construction raises |
|---|---|
| `BareStl(StlNode)` | `ValueError: BareStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it` |
| `BareStep(StepNode)` | `ValueError: BareStep is a StepNode and must declare "step_source", the path of a STEP file in the same directory as the python module defining it` |
| `BareJscad(JScadNode)` | `Exception: OpenJScadNode subclass must declare "jscad_source" property with path with a valid OpenJScad js file` |
| `BareScad(OpenScadNode)` | `TypeError: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'` |
| `EmptyScad(OpenScadNode)`, `scad_source = ''` | `ValueError: EmptyScad declares scad_source = '', resolved against .../parts.py, but .../probe_project is not a file.` |
| `BareMesh(MeshPart)`, the leaf-contract stand-in written outside the core (`tests/contract_package/faceted_stand_in.py`) | `TypeError: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'` |

Four shapes for one mistake. Two of the texts are also wrong about the
rule: a source is not required to sit "in the same directory as the python
module" (a relative path is resolved against that directory, and
`vendor/bracket.step` is the manual's own example). The adapters guard the
declaration themselves, each before it joins the declared value to its
module's directory, so the shared admission `require_source_file`
(`machinome/node/sources.py:129`) is reached only after the join, too
late for `None`; a leaf a node package writes in the documented pattern
fails the same way `OpenScadNode` does.

**2. The builder's wrapper reads as broken English and names the model,
not what failed.**

> **The builder's own wrapper text reads as broken English and names the
> model, not the node.** `Builder._start()` wraps a load-time failure as
> `f'{self.path}: failed to {stage} project: {exc}'` (`builder.py:356`,
> stage `'load'` or `'inspect initial sources'`), e.g. `parts:MissingStl:
> failed to load project: ...` — "failed to load project" reads oddly for
> a single model reference, and `self.path` is the CLI's model argument,
> not the node whose declaration was wrong; for a leaf nested inside an
> assembly the wrapper still names only the root [...].

Reproduced at `bad5ebe` with `machinome build` on the same fixture
project, one line per stage the wrapper serves (`builder.py:531`; stages
passed at `:332`, `:356` and `:487`):

```text
ERROR -    core.builder - assembly:Rig: failed to load project: BareStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it
ERROR -    core.builder - parts:GhostContributor: failed to inspect initial sources project: [Errno 2] No such file or directory: '.../probe_project/ghost.py'
ERROR -    core.builder - parts:FailingPreparation: failed to assemble project: preparation failed deliberately
```

`assembly:Rig` holds `arm = Arm()`, which holds `bracket = BareStl()`: the
faulty leaf is two levels below the root, and the line names only the
root. The third stage, `'assemble'`, is one the finding did not list; its
line reads the same way. The second is not English at all.

## What Changes

- **One refusal for an undeclared source, made by `require_source_file`.**
  `require_source_file(klass, attribute, declared, path=None)` refuses a
  declaration that names no file (`None` or the empty string) first, before
  it resolves, judges containment or looks for the file, with `ValueError`
  naming the class, the attribute and the module that defines the class:
  `BareStl does not declare stl_source. Set stl_source in /…/parts.py to
  the path of the file its part is read from, relative to that module's
  directory or absolute.` (for `''`: `EmptyScad declares scad_source = '',
  which names no file. Set …`).
- **`require_source_file` resolves the declaration when no path is given.**
  Called with the declared value alone, it resolves it against the
  directory of the module defining the class, exactly as the four adapters
  resolve it today, judges it as before, and returns the resolved absolute
  path; called with a path the caller resolved itself, it judges that path
  as before and returns it. The four core adapters drop their own guard and
  their own join and take the path from it in one call, so the refusal is
  made in one place and a leaf written outside the core that resolves its
  declaration the same way gets it unchanged. The contract stand-in
  `MeshPart` is rewritten in that form, as the pattern a node package
  follows.
- **The builder's line says what it was doing with the model.** An initial
  failure logs `The model <reference> could not be loaded: <message>`,
  `The sources of the model <reference> could not be read: <message>` or
  `The model <reference> could not be assembled: <message>`, by stage. The
  inner message stands as it is: for an undeclared or missing source it is
  the refusal above, which names the leaf's class, where the declaration
  is written. `errors.json` and the reload path are unchanged.

**Deliberately out**, with the reason:

- the leaf's position in the tree (`arm.bracket`) in the refusal. A leaf
  is refused while it is constructed, before its parent has linked it; its
  class, and the module defining it, is where the declaration is fixed.
  Naming the tree path would mean catching and re-raising in the
  declarative realization of every child, a change of its own;
- the exception's type in the builder's line (`KeyError: 'x'` reads as
  `'x'`). The finding is the sentence around the message; `errors.json`
  keeps the whole traceback;
- `Svg(None)` in a marking, which still fails in `Svg.resolve`'s own join
  before `require_source_file`; no project or test writes one, and a
  marking's artwork is not a leaf's source attribute. `Svg('')` reaches
  `require_source_file` in its four-argument form and is refused as naming
  no file, where it was refused as "not a file";
- the declared-but-absent and outside-the-project refusals: their text,
  type and `.filename` are unchanged;
- `machinome test`'s and `machinome build --all`'s own reports, which do not
  use the builder's line;
- every catalogue project: a scan of 16 791 Python files under `projects/`
  finds no test or code that asserts on or catches any of the old texts
  (design.md, Context); the workspace scripts, the studio's floor and
  skills and the viewer quote none of them either.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `node-model`: "A source-bound leaf names its missing file" — a subclass of
  any source-bound adapter that declares no source file is refused at
  construction with `ValueError` naming the class, the attribute and the
  defining module, in one shape for every adapter and for a leaf outside the
  core that resolves through `require_source_file`; three scenarios added,
  every existing scenario carried.
- `leaf-contract`: "A leaf states its source identity through declared
  members" — `require_source_file` resolves a declaration given alone and
  returns the path, and refuses an undeclared source; one scenario added,
  every existing scenario carried.
- `stl-import`: "STL source declaration and freshness" — the refusal of a
  subclass without `stl_source` is `ValueError` naming the class, the
  attribute and the defining module; its scenario says so, every other
  scenario carried.
- `step-import`: "STEP source declaration and freshness" — the same for
  `step_source`.
- `build-pipeline`: "File-based build error propagation" — an
  initial-launch failure logs one line naming the model reference and what
  was being done with it, followed by the failure's own message; one
  scenario added, every existing scenario carried.

`openscad-node` states nothing about `scad_source`'s refusal; the
`node-model` requirement is the one that governs `OpenScadNode` and
`JScadNode` here, and `openscad-node` is not modified.

## Impact

- Code: `machinome/node/sources.py` (`require_source_file`, one private
  helper beside it), `machinome/node/stl.py`, `machinome/node/step.py`,
  `machinome/node/jscad.py`, `machinome/node/openscad/__init__.py` (each
  constructor's guard and join replaced by one call),
  `machinome/core/builder.py` (`_on_reload_exception`'s line, one mapping
  beside it).
- Tests: `tests/test_missing_source_file.py` (the undeclared refusal for
  the four adapters and the stand-in, the resolving form, and
  `machinome build` on a scratch project whose nested leaf declares
  nothing), `tests/test_builder_lifecycle.py` (the line at each of the
  three stages), `tests/contract_package/faceted_stand_in.py` (`MeshPart`
  in the resolving form). The existing
  `test_a_missing_declaration_fails_naming_the_class` in
  `tests/test_stl_node.py` and `tests/test_step_node.py` assert the class
  and attribute only and stay green unedited.
- Public contract: `require_source_file` gains an optional fourth argument
  and returns the path it judged. The four-argument call keeps its meaning,
  so the leaf contract version stays `3` (design.md, Decision 5).
- Documents, artifacts, `errors.json`: unchanged.
- Manual: no page quotes a changed message or states the old rule (design.md,
  Decision 6); `docs/project/changelog.rst` takes one bullet under
  `Unreleased`.
- No ADR.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 12, `refuse-the-undeclared-file-by-name`,
validated in fixture projects: it is a framework message contract, so no
catalogue project is run, and the catalogue is scanned for any text it
changes. Design.md's Open Question 1 names the one interface choice in it
for the orchestrator's review.
