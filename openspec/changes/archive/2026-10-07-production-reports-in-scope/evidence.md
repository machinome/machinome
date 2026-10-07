# Evidence — `production-reports-in-scope`

Cycle 11 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
890b6ed (`git -C <bench> rev-parse HEAD` printed
`890b6ed3119054fa8fe3801a1431f346b4b381a9`). Every framework command below
ran as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`,
with `-p no:cacheprovider` for pytest, one process at a time, never in
parallel (`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome
snapshot\|[m]achinome build'` listed no run but the checking shell itself
before each heavy run). The interpreter check,
`python -c 'import machinome; print(machinome.__file__)'`, printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

`<project>` is `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`,
branch `main`, head `1f3dc22` (`git -C <project> rev-parse --short HEAD`,
before and after). The production slice's worktree
`<project>/WTs/production-layer-3x` is at `7c9121e`. Both were read and run,
never written: `git -C <project> status --short` listed the same four
untracked entries as `<scratch>/curta-status.before` before and after every
Curta run (`"3D Printed Curta Calculator Assembly_720p.mp4"`, `CREDITS`,
`curta-2x-files/`, `screenshots/reverser_inspection.png`), and the
worktree's `git status --short` was empty before and after.

`<scratch>` is the campaign scratchpad's `cycle11/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle11/`),
holding a `pyproject.toml` (`[tool.machinome]`, empty) that gives its
scripts a project root. Scratch scripts ran as
`env -C <scratch> PYTHONPATH=<bench>:<scratch> PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/_build .venv/bin/python <scratch>/<script>`,
with ` INFO -` lines filtered out. The scratchpad is not durable; the
scripts this record depends on are copied below. `<focused>` is
`tests/test_model_consumption.py tests/test_production.py
tests/test_production_documentation.py`.

## 1. Baseline on the unmodified tree (890b6ed)

### 1.1 The scripts and the overlay

`<scratch>/repro_reports.py`:

```python
"""Stage P reproduction of the three production-report defects.

Run from the bench with PYTHONPATH=<bench>. Writes only under a fresh
directory in this script's own folder.
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

import machinome
from machinome.model import Reference
from machinome.node.assembly import AssemblyNode
from machinome.node.leaf import LeafNode
from machinome.parameters import Count
from machinome.components import Standard
from machinome.production.profile import Production, _markdown
from machinome.production.item import Item
from machinome.production.process import Sourced
from machinome.production.errors import (
    ProductionConflictError,
    ProductionExportError,
)

HERE = Path(__file__).resolve().parent
print("machinome:", machinome.__file__)


class Nut(LeafNode):
    def render(self):
        raise AssertionError("sourced reports must never render geometry")


class Submodel(AssemblyNode):
    count = Count(2)
    nuts = Nut().repeat(count)


class Root(AssemblyNode):
    left = Submodel(count=2)
    right = Submodel(count=3)


NUT = Standard("DIN 934", designation="M4x0.7")


class SubProduction(Production[Submodel]):
    arbitrary_name = Item(Submodel.nuts, Sourced(NUT))


class Twice(Production[Submodel]):
    a = Item(Submodel.nuts, Sourced(NUT))
    b = Item(Submodel.nuts, Sourced(NUT))


def attempt(label, read):
    try:
        value = read()
    except Exception as error:  # noqa: BLE001 - a probe prints every outcome
        print(f"  {label:<34} {type(error).__name__}: {error}")
    else:
        print(f"  {label:<34} {value}")


print("--- 1. Markdown gate, direct ---")
CASES = [
    ("inequality", "if a<b then c>d ok"),
    ("inequality, other letters", "keep x<y and z>w"),
    ("tag in code span", "write `<img src=\"x.png\">` to embed"),
    ("tag in fenced code", "```html\n<img src=\"x.png\">\n```\n"),
    ("harmless element", "press <kbd>Ctrl</kbd>"),
    ("<img src>", '<img src="x.png">'),
    ("<a href> local", '<a href="x.pdf">x</a>'),
    ("<a href> https", '<a href="https://example.com">x</a>'),
    ("<link href>", '<link rel="stylesheet" href="x.css">'),
    ("<script src>", '<script src="x.js"></script>'),
    ("<script> inline", "<script>fetch('x')</script>"),
    ("<style> inline", "<style>@import 'x.css';</style>"),
    ("<video src>", '<video src="x"></video>'),
    ("<object data>", '<object data="x"></object>'),
    ("link in code span", "`[x](local.png)`"),
]
for label, text in CASES:
    def read(text=text):
        _markdown(text, "step", Path("assembly.md"))
        return "accepted"

    attempt(label, read)


print("--- 1. Markdown gate, through steps ---")
work = Path(tempfile.mkdtemp(prefix="md-", dir=HERE))
(work / "assembly.md").write_text("if a<b then c>d ok\n")
(work / "production_md.py").write_text(
    "from repro_reports import Submodel, NUT\n"
    "from machinome.production.profile import Production\n"
    "from machinome.production.item import Item\n"
    "from machinome.production.process import Sourced\n"
    "from machinome.production.instruction import Step, Markdown\n"
    "class Profile(Production[Submodel]):\n"
    "    nuts = Item(Submodel.nuts, Sourced(NUT))\n"
    "    step = Step(nuts, instructions=Markdown('assembly.md'))\n"
)
sys.modules.setdefault("repro_reports", sys.modules[__name__])
spec = importlib.util.spec_from_file_location(
    "production_md", work / "production_md.py"
)
module = importlib.util.module_from_spec(spec)
sys.modules["production_md"] = module
spec.loader.exec_module(module)
attempt("steps of 'if a<b then c>d ok'", lambda: len(module.Profile(Submodel()).steps))


print("--- 2. Overlap inside right; reading left ---")


class OverlapInRight(Production[Root]):
    left = SubProduction(Root.left)
    right = Twice(Root.right)


profile = OverlapInRight(Root())
attempt("root findings codes", lambda: [f.code for f in profile.findings])
attempt(
    "overlap finding",
    lambda: [
        (f.occurrences, f.declarations)
        for f in profile.findings
        if f.code == "overlap"
    ],
)
attempt("left.findings", lambda: profile.left.findings)
attempt("left.bom quantities", lambda: [l.quantity for l in profile.left.bom])
attempt("left.mass.complete", lambda: profile.left.mass.complete)
attempt("left.steps", lambda: profile.left.steps)
attempt("right.bom", lambda: profile.right.bom)
attempt("root.bom", lambda: profile.bom)

print("--- 2. Parent reaches inside left; reading right ---")


class ParentReachesLeft(Production[Root]):
    left = SubProduction(Root.left)
    right = SubProduction(Root.right)
    extra = Item(Reference(Root, ("left", "nuts")), Sourced(NUT))


reach = ParentReachesLeft(Root())
attempt(
    "overlap finding",
    lambda: [
        (f.occurrences, f.declarations)
        for f in reach.findings
        if f.code == "overlap"
    ],
)
attempt("left.bom", lambda: reach.left.bom)
attempt("right.bom quantities", lambda: [l.quantity for l in reach.right.bom])
attempt("root.bom", lambda: reach.bom)


print("--- 3. Declaration paths by repetition count ---")
for n in (1, 2):

    class Holder(AssemblyNode):
        n_kids = Count(n)
        kids = Submodel(count=1).repeat(n_kids)

    class HolderProduction(Production[Holder]):
        kids = SubProduction(Holder.kids)

    bound = HolderProduction(Holder())
    kids = bound.kids
    print(
        f"  repeat n={n}: type={type(kids).__name__} paths="
        f"{[k.arbitrary_name.declaration_path for k in kids]} "
        f"bom.declarations={[l.declaration_paths for l in bound.bom]}"
    )

for refs in (
    (Reference(Root, ("left",)),),
    (Reference(Root, ("left",)), Reference(Root, ("right",))),
):

    class TupleProduction(Production[Root]):
        kids = SubProduction(refs)

    bound = TupleProduction(Root())
    kids = bound.kids
    print(
        f"  tuple of {len(refs)}: type={type(kids).__name__} paths="
        f"{[k.arbitrary_name.declaration_path for k in kids]}"
    )


class Single(Production[Root]):
    kid = SubProduction(Root.left)


single = Single(Root())
print(
    f"  single reference: type={type(single.kid).__name__} path="
    f"{single.kid.arbitrary_name.declaration_path}"
)
```

`<scratch>/probe_holder.py` (it imports `repro_reports`, so its output
begins with the reproduction's):

```python
"""Stage P probe: a repeated child binding over a Count, at 0, 1 and 2."""

import tempfile
from pathlib import Path

from machinome.node.assembly import AssemblyNode
from machinome.parameters import Count
from machinome.production.profile import Production

from repro_reports import Submodel, SubProduction

HERE = Path(__file__).resolve().parent


class Holder(AssemblyNode):
    n = Count(1)
    kids = Submodel(count=1).repeat(n)


class HolderProduction(Production[Holder]):
    kids = SubProduction(Holder.kids)


out = Path(tempfile.mkdtemp(prefix="holder-", dir=HERE))
for n in (0, 1, 2):
    bound = HolderProduction(Holder(n=n))
    kids = bound.kids
    result = bound.export(out / f"n{n}")
    import json

    manifest = json.loads((result.path / "production.json").read_text())
    print(
        f"n={n}: {type(kids).__name__} of {len(kids)}; item paths "
        f"{[k.arbitrary_name.declaration_path for k in kids]}; manifest "
        f"bindings {[b['declaration_path'] for b in manifest['bindings']]}; "
        f"owners {sorted(set(v for v in manifest['owners'].values() if v))}"
    )
```

`<scratch>/curta_bindings.py`:

```python
"""Stage P evidence: the Curta slice's child bindings and their paths.

Run in the cycle-10 overlay with the bench first on PYTHONPATH. Structural
only: reads findings, which builds no geometry.
"""

from production.profile import CurtaDraft
from simulation.mechanistic import MechanisticCurta

production = CurtaDraft(MechanisticCurta())
findings = production.findings
print("findings:", len(findings), sorted({f.code for f in findings}))
for binding in production._shared.bindings:
    print(f"  {binding._declaration_scope or '.':<40} {binding._scope.path}")
for name in ("crank", "frame_nuts", "upper_frame_nuts", "result_wires",
             "turns_wires"):
    child = getattr(production, name)
    springs = getattr(child, "springs", None)
    print(
        f"{name}: {type(child).__name__}"
        + (
            f", springs: {type(springs).__name__} of {len(springs)}"
            if springs is not None
            else ""
        )
    )
```

`<scratch>/probe_markdown.py` carries its own copy of the proposed gate,
which is the bench's code after the change. Compared by syntax tree
(docstrings set aside, function names normalised), its seven constants
`_FENCE`, `_CONTAINER`, `_HTML_BLOCKS`, `_SPAN_OR_TAG`, `_TAG`,
`_EMBEDDING` and `_DEPENDENCY_ATTRIBUTES` are the bench's, its
`_dependency_tag` is the bench's `_html_dependency` and its `markdown` the
bench's `_markdown`; its `_read_text` differs from the bench's
`_rendered_text` only in that the bench binds the fence-closing pattern to
a local `closing` before `re.match(closing, line)`:

```
--- probe
+++ bench
@@ -10 +10,2 @@
-            if re.match(f'^ {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}\\s*$', line):
+            closing = f'^ {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}\\s*$'
+            if re.match(closing, line):
```

So the gate's source is the one in `machinome/production/profile.py`. Its two case lists, `ACCEPT` and `REFUSE`, are exactly the
parameters of the two new tests of section 2 plus the refused rows already
pinned by `test_markdown_refusal_is_contextual_and_leaves_no_target` and
`test_requested_steps_and_export_refuse_unsupported_dependencies`
(`<iframe src>`, `<video src>`, `<object data>`, `<script src>`,
`![x](local.png)`, `[x](../outside.md)`, `[x][ref]` with `[ref]:
local.pdf`, `[x][missing]`, `<mailto:…>`, `<ftp://…>`). Its main loop:

```python
if __name__ == "__main__":
    failures = 0
    for expected, cases in (("accepted", ACCEPT), ("refused", REFUSE)):
        for text in cases:
            try:
                markdown(text, "step", Path("assembly.md"))
                outcome = "accepted"
            except ProductionExportError as error:
                outcome = f"refused ({str(error).split(': ', 1)[1]})"
            ok = outcome.startswith(expected)
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {expected:<8} {text!r}: {outcome}")
    print("failures:", failures)
```

The overlay, `<overlay>` =
`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle10/curta-overlay/`,
is cycle 10's, unchanged: a copy of the production slice's `production/`
package from `<project>/WTs/production-layer-3x` (`7c9121e`), its
`__pycache__` directories removed and the one line
`from machinome.node import AssemblyNode, StepNode` of
`production/test_production.py` rewritten as
`from machinome.node.assembly import AssemblyNode` and
`from machinome.node.step import StepNode`; beside it, symbolic links
`simulation`, `pyproject.toml` and `CAD` to the same names in `<project>`.
Checked before the first run:
`diff -r -x __pycache__ <project>/WTs/production-layer-3x/production <overlay>/production`
reports that one line and nothing else (exit 1):

```
10c10,11
< from machinome.node import AssemblyNode, StepNode
---
> from machinome.node.assembly import AssemblyNode
> from machinome.node.step import StepNode
```

The Curta command, `<curta>`:

```sh
env -C <overlay> PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH="<bench>:<project>:<overlay>" \
  SOLID_BUILD_DIR=<scratch>/curta-build \
  /usr/bin/time -f 'wall %e s' /home/asa/devel/machinome/.venv/bin/python \
  -m pytest -q -p no:cacheprovider --basetemp=<scratch>/curta-basetemp \
  --rootdir=<overlay> <overlay>/production/test_production.py
```

`<curta-bindings>` is the same environment running
`/usr/bin/time -f 'wall %e s' .venv/bin/python <scratch>/curta_bindings.py`.

### 1.2 The reproduction

`repro_reports.py` (`<scratch>` abbreviated), identical to Stage P's
`repro_reports.before.out` but for the random name of the step's scratch
directory:

```
--- 1. Markdown gate, direct ---
  inequality                         ProductionExportError: step: unsupported HTML dependency in assembly.md
  inequality, other letters          ProductionExportError: step: unsupported HTML dependency in assembly.md
  tag in code span                   ProductionExportError: step: unsupported HTML dependency in assembly.md
  tag in fenced code                 ProductionExportError: step: unsupported HTML dependency in assembly.md
  harmless element                   ProductionExportError: step: unsupported HTML dependency in assembly.md
  <img src>                          ProductionExportError: step: unsupported HTML dependency in assembly.md
  <a href> local                     ProductionExportError: step: unsupported HTML dependency in assembly.md
  <a href> https                     ProductionExportError: step: unsupported HTML dependency in assembly.md
  <link href>                        ProductionExportError: step: unsupported HTML dependency in assembly.md
  <script src>                       ProductionExportError: step: unsupported HTML dependency in assembly.md
  <script> inline                    ProductionExportError: step: unsupported HTML dependency in assembly.md
  <style> inline                     ProductionExportError: step: unsupported HTML dependency in assembly.md
  <video src>                        ProductionExportError: step: unsupported HTML dependency in assembly.md
  <object data>                      ProductionExportError: step: unsupported HTML dependency in assembly.md
  link in code span                  ProductionExportError: step: unsupported local or URL dependency 'local.png' in assembly.md
--- 1. Markdown gate, through steps ---
  steps of 'if a<b then c>d ok'      ProductionExportError: step: unsupported HTML dependency in <scratch>/md-x949b1c3/assembly.md
--- 2. Overlap inside right; reading left ---
  root findings codes                ['overlap', 'overlap', 'overlap']
  overlap finding                    [(('right/nuts-0',), ('right/a', 'right/b')), (('right/nuts-1',), ('right/a', 'right/b')), (('right/nuts-2',), ('right/a', 'right/b'))]
  left.findings                      ()
  left.bom quantities                ProductionConflictError: overlapping ownership: right/a, right/b claim right/nuts-0; right/a, right/b claim right/nuts-1; right/a, right/b claim right/nuts-2
  left.mass.complete                 ProductionConflictError: overlapping ownership: right/a, right/b claim right/nuts-0; right/a, right/b claim right/nuts-1; right/a, right/b claim right/nuts-2
  left.steps                         ProductionConflictError: overlapping ownership: right/a, right/b claim right/nuts-0; right/a, right/b claim right/nuts-1; right/a, right/b claim right/nuts-2
  right.bom                          ProductionConflictError: overlapping ownership: right/a, right/b claim right/nuts-0; right/a, right/b claim right/nuts-1; right/a, right/b claim right/nuts-2
  root.bom                           ProductionConflictError: overlapping ownership: right/a, right/b claim right/nuts-0; right/a, right/b claim right/nuts-1; right/a, right/b claim right/nuts-2
--- 2. Parent reaches inside left; reading right ---
  overlap finding                    [(('left/nuts-0',), ('extra', 'left')), (('left/nuts-1',), ('extra', 'left'))]
  left.bom                           ProductionConflictError: overlapping ownership: extra, left claim left/nuts-0; extra, left claim left/nuts-1
  right.bom quantities               ProductionConflictError: overlapping ownership: extra, left claim left/nuts-0; extra, left claim left/nuts-1
  root.bom                           ProductionConflictError: overlapping ownership: extra, left claim left/nuts-0; extra, left claim left/nuts-1
--- 3. Declaration paths by repetition count ---
  repeat n=1: type=tuple paths=['kids/arbitrary_name'] bom.declarations=[('kids/arbitrary_name',)]
  repeat n=2: type=tuple paths=['kids-0/arbitrary_name', 'kids-1/arbitrary_name'] bom.declarations=[('kids-0/arbitrary_name', 'kids-1/arbitrary_name')]
  tuple of 1: type=tuple paths=['kids/arbitrary_name']
  tuple of 2: type=tuple paths=['kids-0/arbitrary_name', 'kids-1/arbitrary_name']
  single reference: type=SubProduction path=kid/arbitrary_name
```

### 1.3 The manifest of a one-member repetition

`probe_holder.py`, its own lines (after the reproduction's), identical to
Stage P's `probe_holder.before.out`:

```
n=0: tuple of 0; item paths []; manifest bindings ['']; owners []
n=1: tuple of 1; item paths ['kids/arbitrary_name']; manifest bindings ['', 'kids']; owners ['kids/arbitrary_name']
n=2: tuple of 2; item paths ['kids-0/arbitrary_name', 'kids-1/arbitrary_name']; manifest bindings ['', 'kids-0', 'kids-1']; owners ['kids-0/arbitrary_name', 'kids-1/arbitrary_name']
```

### 1.4 The Curta production slice through the overlay

`<curta>`, the build directory Stage P left warm:

```
......                                                                   [100%]
6 passed in 118.81s (0:01:58)
wall 120.41 s
```

(Stage P, a new build directory: `6 passed in 134.08s`, wall 135.36 s.)

`<curta-bindings>`: identical to Stage P's `curta_bindings.before.out` but
for the wall time (29.61 s; Stage P 29.03 s):

```
findings: 417 ['unassigned']
  .                                        .
  crank                                    main_drive/crank
  frame_nuts                               frame/fasteners
  upper_frame_nuts                         frame/upper_frame
  result_wires                             carry_mechanism/result_carries
  result_wires/springs-0                   carry_mechanism/result_carries/results_tens_lever_assembly_1/carry_lever_spring
  … (springs-1 to springs-8, assemblies 2 to 9)
  result_wires/springs-9                   carry_mechanism/result_carries/results_tens_lever_assembly_10/carry_lever_spring
  turns_wires                              carry_mechanism/turns_carries
  turns_wires/springs-0                    carry_mechanism/turns_carries/turns_tens_lever_assembly_1/carry_lever_spring
  … (springs-1 to springs-3, assemblies 2 to 4)
  turns_wires/springs-4                    carry_mechanism/turns_carries/turns_tens_lever_assembly_5/carry_lever_spring
crank: CrankDraft
frame_nuts: FrameNuts
upper_frame_nuts: UpperFrameNuts
result_wires: ResultWireNotes, springs: tuple of 10
turns_wires: TurnsWireNotes, springs: tuple of 5
```

21 binding paths. The slice, searched for the brief's two questions: its
`production/` holds twelve `*.md` files, and `grep -l '[<>]'` over them
finds none (exit 1); `grep -rn 'declaration_path\|step_id'` and a search
for quoted `a/b` strings over its `*.py` find two occurrence paths in
`test_production.py` (`"right_arm/body"`-style suffixes and
`"main_drive/crank"`), no declaration path. Its repeated bindings are the
two `springs = UnassignedWire(tuple(...))` of `production/carry/profile.py`,
already indexed above.

### 1.5 The focused suites

`pytest -q -p no:cacheprovider <focused>`: `57 passed, 4 warnings in
7.31s` (wall 8.35 s). Stage P: 57 passed in 7.27 s.

## 2. Red tests on the unmodified code

Added to `tests/test_production.py`, as design.md Decision 4 gives them:

- after `test_delegation_ownership_conflict_has_all_declarations`, the
  module-level `Twice(Production[Submodel])` (Items `a` and `b` on
  `Submodel.nuts`), `test_an_overlap_refuses_only_the_reports_of_its_scope`
  and `test_a_parent_reaching_into_one_child_leaves_its_sibling_readable`;
- after `test_zero_repeat_is_not_absent_and_single_repeat_child_stays_tuple`,
  `test_tuple_binding_members_are_always_indexed`, parametrized over the
  count (1 and 2): the `Holder` repetition (binding a tuple, item paths,
  BOM `declaration_paths`, exported manifest `bindings`), the tuple of the
  first one or two references of `(Root.left, Root.right)`, and the single
  reference `kid = SubProduction(Root.left)` named `kid/arbitrary_name`;
- after `test_markdown_refusal_is_contextual_and_leaves_no_target`,
  `test_markdown_gate_accepts_what_is_not_a_dependency` (15 cases, the
  probe's `ACCEPT`), `test_markdown_gate_refuses_html_dependencies_outside_code`
  (21 cases, the probe's `REFUSE` without the ten rows the two existing
  Markdown tests already pin), and `test_an_inequality_in_a_step_is_read`.

`pytest -q -p no:cacheprovider tests/test_production.py -rA -k
"not_a_dependency or outside_code or inequality_in_a_step or
only_the_reports_of_its_scope or leaves_its_sibling_readable or
always_indexed"` on the unmodified code: `18 failed, 23 passed, 34
deselected in 0.96s`. The red, each for the reason tasks.md names:

```
FAILED tests/test_production.py::test_an_overlap_refuses_only_the_reports_of_its_scope
E               machinome.production.errors.ProductionConflictError: overlapping ownership: right/a, right/b claim right/nuts-0; right/a, right/b claim right/nuts-1; right/a, right/b claim right/nuts-2
  (raised at the first read of left.bom)
FAILED tests/test_production.py::test_a_parent_reaching_into_one_child_leaves_its_sibling_readable
E               machinome.production.errors.ProductionConflictError: overlapping ownership: extra, left claim left/nuts-0; extra, left claim left/nuts-1
  (raised at profile.right.bom)
FAILED tests/test_production.py::test_tuple_binding_members_are_always_indexed[1]
E       AssertionError: assert ['kids/arbitrary_name'] == ['kids-0/arbitrary_name']
E         At index 0 diff: 'kids/arbitrary_name' != 'kids-0/arbitrary_name'
FAILED test_markdown_gate_accepts_what_is_not_a_dependency, 13 cases:
  [if a<b then c>d ok] [keep x<y and z>w] [write `<img src="x.png">` to embed]
  [``a ` <script src=x> ` b``] [```html\n<img src="x.png">\n```\n]
  [~~~\n<link href="x.css">\n~~~] [press <kbd>Ctrl</kbd> and <br/> then <sub>2</sub>]
  [<div class="note">\nplain\n</div>]
  [unclosed fence swallows the rest\n```\n<img src=x>]
  [> quoted `<img src=x.png>` code] [- item `<script src=x>` code]
E           machinome.production.errors.ProductionExportError: declared/step: unsupported HTML dependency in …/instruction.md
  [`[x](local.png)`]
E               machinome.production.errors.ProductionExportError: declared/step: unsupported local or URL dependency 'local.png' in …/instruction.md
  [```\n[ref]: local.pdf\n```\n[x](https://example.com) and [y](#here)]
E               machinome.production.errors.ProductionExportError: declared/step: unsupported local or URL dependency 'local.pdf' in …/instruction.md
FAILED tests/test_production.py::test_markdown_gate_refuses_html_dependencies_outside_code[[x][ref]\n\n```\n[ref]: https://example.com\n```]
E       Failed: DID NOT RAISE ProductionExportError
FAILED tests/test_production.py::test_an_inequality_in_a_step_is_read
E           machinome.production.errors.ProductionExportError: step: unsupported HTML dependency in …/profile/assembly.md
  (raised at profile.steps)
```

Green before the change (guards): the accepted `5 < 6 > 4` and
`Plain *Markdown* with `code` and <https://example.com>.`; the other 20
refused cases; `test_tuple_binding_members_are_always_indexed[2]`. 18 red,
23 green.

## 3. The change

- `machinome/production/profile.py`, above `_markdown`: the private module
  constants `_FENCE`, `_CONTAINER`, `_HTML_BLOCKS`, `_SPAN_OR_TAG`, `_TAG`,
  `_EMBEDDING` and `_DEPENDENCY_ATTRIBUTES`, and the private functions
  `_rendered_text(text)` and `_html_dependency(tag)`, the probe's code. Two
  layout differences, neither changing behaviour: the fence-closing pattern
  of `_rendered_text` is bound to a local `closing` before `re.match`, so
  the line stays within 79 columns, and each function carries a docstring.
  In `_markdown`: `text = _rendered_text(text)` first, and the HTML check
  is `if any(_html_dependency(tag) for tag in _TAG.finditer(text)):`. The
  message is unchanged.
- `Production._in_scope(finding)`, the predicate `findings` used inline;
  `findings` is `tuple(f for f in self._shared.findings if
  self._in_scope(f))`; `_read` refuses with the overlap findings for which
  `_in_scope` holds and joins only their messages.
- `_Shared.resolve.populate`, the child-binding branch: the `is_many`
  expression (unchanged, the same short-circuit order) moves above the
  loop, and each member's `_declaration_scope` is `f"{path}-{index}" if
  is_many else path`.

No divergence from design.md.

The 2.5 selection after the change: `41 passed, 34 deselected in 0.70s`.
`<focused>`: `98 passed, 4 warnings in 8.54s` (wall 9.66 s), 1.5's 57 plus
the 41 new cases. `git -C <bench> status --short`: ` M
machinome/production/profile.py`, ` M tests/test_production.py` (the
change directory is committed and was unchanged at that point).

## 4. The reproductions and the originating project after the change

### 4.1 The reproduction and the probes

`repro_reports.py` (printed by `probe_holder.py`, which imports it):

```
--- 1. Markdown gate, direct ---
  inequality                         accepted
  inequality, other letters          accepted
  tag in code span                   accepted
  tag in fenced code                 accepted
  harmless element                   accepted
  <img src>                          ProductionExportError: step: unsupported HTML dependency in assembly.md
  <a href> local                     ProductionExportError: step: unsupported HTML dependency in assembly.md
  <a href> https                     ProductionExportError: step: unsupported HTML dependency in assembly.md
  <link href>                        ProductionExportError: step: unsupported HTML dependency in assembly.md
  <script src>                       ProductionExportError: step: unsupported HTML dependency in assembly.md
  <script> inline                    ProductionExportError: step: unsupported HTML dependency in assembly.md
  <style> inline                     ProductionExportError: step: unsupported HTML dependency in assembly.md
  <video src>                        ProductionExportError: step: unsupported HTML dependency in assembly.md
  <object data>                      ProductionExportError: step: unsupported HTML dependency in assembly.md
  link in code span                  accepted
--- 1. Markdown gate, through steps ---
  steps of 'if a<b then c>d ok'      1
--- 2. Overlap inside right; reading left ---
  root findings codes                ['overlap', 'overlap', 'overlap']
  overlap finding                    [(('right/nuts-0',), ('right/a', 'right/b')), (('right/nuts-1',), ('right/a', 'right/b')), (('right/nuts-2',), ('right/a', 'right/b'))]
  left.findings                      ()
  left.bom quantities                [2]
  left.mass.complete                 False
  left.steps                         ()
  right.bom                          ProductionConflictError: overlapping ownership: right/a, right/b claim right/nuts-0; right/a, right/b claim right/nuts-1; right/a, right/b claim right/nuts-2
  root.bom                           ProductionConflictError: overlapping ownership: right/a, right/b claim right/nuts-0; right/a, right/b claim right/nuts-1; right/a, right/b claim right/nuts-2
--- 2. Parent reaches inside left; reading right ---
  overlap finding                    [(('left/nuts-0',), ('extra', 'left')), (('left/nuts-1',), ('extra', 'left'))]
  left.bom                           ProductionConflictError: overlapping ownership: extra, left claim left/nuts-0; extra, left claim left/nuts-1
  right.bom quantities               [3]
  root.bom                           ProductionConflictError: overlapping ownership: extra, left claim left/nuts-0; extra, left claim left/nuts-1
--- 3. Declaration paths by repetition count ---
  repeat n=1: type=tuple paths=['kids-0/arbitrary_name'] bom.declarations=[('kids-0/arbitrary_name',)]
  repeat n=2: type=tuple paths=['kids-0/arbitrary_name', 'kids-1/arbitrary_name'] bom.declarations=[('kids-0/arbitrary_name', 'kids-1/arbitrary_name')]
  tuple of 1: type=tuple paths=['kids-0/arbitrary_name']
  tuple of 2: type=tuple paths=['kids-0/arbitrary_name', 'kids-1/arbitrary_name']
  single reference: type=SubProduction path=kid/arbitrary_name
```

`probe_holder.py`, its own lines:

```
n=0: tuple of 0; item paths []; manifest bindings ['']; owners []
n=1: tuple of 1; item paths ['kids-0/arbitrary_name']; manifest bindings ['', 'kids-0']; owners ['kids-0/arbitrary_name']
n=2: tuple of 2; item paths ['kids-0/arbitrary_name', 'kids-1/arbitrary_name']; manifest bindings ['', 'kids-0', 'kids-1']; owners ['kids-0/arbitrary_name', 'kids-1/arbitrary_name']
```

`probe_markdown.py`: `failures: 0`, its output identical to Stage P's
`probe_markdown.out`.

### 4.2 The Curta production slice through the overlay

`<curta>` again, the same build directory:

```
......                                                                   [100%]
6 passed in 119.63s (0:01:59)
wall 120.72 s
```

Before: 6 passed in 118.81 s, wall 120.41 s. After: 6 passed in 119.63 s,
wall 120.72 s. `git -C <project> status --short` matched
`<scratch>/curta-status.before` before and after; `git -C <project>
rev-parse --short HEAD` printed `1f3dc22`; the slice worktree's status was
empty. `<curta-bindings>`: the output of 1.4 line for line (417 findings,
all `unassigned`, the same 21 binding paths), wall 29.20 s.

The bench's gate after the change, run over the slice's twelve Markdown
files (`env -C <bench> … python -c` calling `_markdown(f.read_text(),
'step', f)` for each `*.md` under `<project>/WTs/production-layer-3x/production`):
`12 accepted`.

## 5. Records

- 5.1 `docs/reference/api.rst`, the production section, the three edits of
  design.md Decision 5 and nothing else: after "Repeated child bindings
  are tuples, including a one-member repetition.", "Their members'
  declaration paths carry the member's index at every count, as
  ``kids-0/nut``."; after "… raw HTML dependencies are refused.", "An HTML
  tag is a dependency when its element embeds or loads content or an
  attribute names a resource; other text, such as ``a<b``, is not. Text in
  code spans and fenced code blocks is not read for dependencies."; the
  overlap sentence replaced by "Overlapping owners remain inspectable in
  ``findings`` and refuse the other reports, with
  ``ProductionConflictError``, of every binding whose scope holds an
  occurrence they both claim; the root's scope holds every occurrence."
  The three paragraphs were rewrapped at 79 columns.
- 5.2 `docs/project/changelog.rst`: design.md Decision 5's bullet appended
  to the one `Unreleased` section, after the `production-reads-once`
  bullet.
- 5.3 `grep -rn 'ProductionConflictError\|overlap\|HTML\|Markdown\|declaration_path\|repetition' docs --exclude-dir=adrs --exclude-dir=releases`
  (changelog set aside): outside `api.rst`'s production section, the hits
  are about geometric overlap (`performance-improvement.md`,
  `architecture.md:1472` and `:2580`, `reference/assertions.rst`,
  `concepts/running.rst`, `howto/fast-tests.rst`, `api.rst:991-992`),
  Sphinx's HTML output (`conf.py`, `reference/sphinx.rst`), and
  `api.rst:164`, where `selection_is_many` distinguishes absent targets
  from repetition shape, still true. In the production section,
  `api.rst:19-42` (the example's Markdown files) and `:63`
  (`BoundItem.declaration_path`) stay true. `docs/architecture.md`,
  "Independent production consumption", says nothing about the gate,
  overlaps or member names. No other page changes. The studio's
  `shop-skills/machinome-api/SKILL.md` was searched (read only) for
  `raw html`, `ProductionConflictError`, `one-member`, `kids-0` and
  `overlap`: no hit.

## 6. Warts

- 6.1 The three items, from "- **The Markdown gate refuses text that is
  not a dependency.**", "- **An overlap anywhere in the root blocks an
  unambiguous child's reports.**" and "- **Declaration paths change shape
  with the repetition count.**" each to its "**Untriaged.**", moved
  verbatim from `workflow/warts.md`, section "Findings from the
  adversarial review of the framework cycle `production-layer` (4 October
  2026)", to `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
  `` ## `production-reports-in-scope` ``, after the `production-reads-once`
  entry, with the "From …" line and a "What shipped" paragraph. The
  section's introduction and its other four items (the bundle's absolute
  paths, `Finding.check_status`, the facade's copied lifecycle, the bytes
  held in memory) and its "Checked and found sound" note stay in
  `warts.md`.
- `workflow/ongoing/fix-warts-3.md`: a Progress line for this cycle after
  cycle 10's.

## 7. Sync and archive

- 7.1 By hand. In `openspec/specs/production-assets/spec.md`: "Actual
  nested delegation and traceable quantity" takes its added sentence
  before "A child subtotal or Step SHALL add no extra BOM item." and the
  scenario "A count moves from one to two" after "Differently sized
  repeated children"; "Honest exclusive ownership" takes its added
  sentence after "while findings remains inspectable." and the scenario
  "An overlap under one child leaves its sibling readable" after "Purchase
  replaces internal delegation"; "Instructions remain local and ordered"
  takes its two added sentences after "… rather than exported with broken
  paths." and the scenarios "An inequality is not a dependency" and
  "Markup quoted in code is not a dependency" after "Child and parent use
  the same filename". Before the edit, `python <scratch>/diff_delta.py
  <bench> <bench>/openspec/changes/production-reports-in-scope` (it splits
  each spec into requirement blocks and prints a unified diff of each
  delta requirement against its baseline) showed, for each of the three,
  only the statement line replaced by itself with the added sentence or
  sentences, and the added scenario lines. After it, the script prints the
  three requirement headers and no diff line. `git diff --stat --
  openspec/specs`: `production-assets/spec.md | 22 +++++++++++++++++++---`
  (19 insertions, 3 deletions). `openspec validate
  production-reports-in-scope`: "Change 'production-reports-in-scope' is
  valid"; `openspec validate production-assets`: "Specification
  'production-assets' is valid".

  `<scratch>/diff_delta.py`:

  ```python
  import difflib
  import pathlib
  import re
  import sys

  bench, change = sys.argv[1], pathlib.Path(sys.argv[2])


  def blocks(text):
      found = {}
      parts = re.split(r"(?m)^(?=### Requirement: )", text)
      for part in parts:
          if part.startswith("### Requirement: "):
              title = part.splitlines()[0][len("### Requirement: "):].strip()
              body = re.split(r"(?m)^## ", part)[0]
              found[title] = body.rstrip("\n").splitlines()
      return found


  for delta_file in sorted(change.glob("specs/*/spec.md")):
      spec = delta_file.parent.name
      base = open(f"{bench}/openspec/specs/{spec}/spec.md").read()
      old, new = blocks(base), blocks(delta_file.read_text())
      for title, lines in new.items():
          print(f"=== {spec}: {title}: in baseline: {title in old}")
          for line in difflib.unified_diff(
              old.get(title, []), lines, "baseline", "delta", n=0, lineterm=""
          ):
              print(line)
  ```

- 7.3 On `machinome/production/profile.py` and `tests/test_production.py`,
  on the working tree and on the two files as they are at HEAD (extracted
  with `git show HEAD:<file>` into `<scratch>/head/`):
  - `flake8 --max-line-length=89` (pyenv shim, flake8 7.3.0): no finding,
    exit 0, after and at HEAD.
  - `black --check` (26.5.1, default line length): both files "would
    reformat" at HEAD and after; the files follow black at line length 79,
    as cycle 10 recorded. At `-l 79 -t py311 --diff`, the first check after
    the change found one line of this change, the signature of
    `test_markdown_gate_refuses_html_dependencies_outside_code`, which fits
    on one line at 79 columns; it was joined. After that, `black -l 79 -t
    py311 --diff` changes the same two lines after as at HEAD, the
    pre-existing slice `local[index + 1:]` in `profile.py`, and nothing
    this change wrote. flake8 rerun after the join: exit 0.
- 7.2 `openspec archive production-reports-in-scope --yes --skip-specs`
  (the specs were synced by hand in 7.1, so the CLI's own sync was
  skipped): "Change 'production-reports-in-scope' archived as
  '2026-10-07-production-reports-in-scope'". Its warnings: the Why
  section's length, and 23 of 25 tasks complete (7.2 and 7.4, done after
  it and ticked in the archived copy). `openspec validate --specs`:
  `Totals: 45 passed, 0 failed (45 items)`.
- 7.4 `<focused>`, on the final tree: `98 passed, 4 warnings in 8.95s`
  (wall 10.07 s). The full suite, on the final tree, alone (`ps` showed no
  run of ours), `pytest -q -p no:cacheprovider` at the bench root: exit 0,
  wall 654.25 s, `4718 passed, 4 skipped, 55 warnings, 6665 subtests
  passed in 651.74s (0:10:51)` (cycle 10 closed at 4677 passed; this
  change adds 41 cases). No failure, no `Too many open files`.

Nothing is committed. `git -C <bench> status --short` lists the changed
`docs/project/changelog.rst`, `docs/reference/api.rst`,
`machinome/production/profile.py`,
`openspec/specs/production-assets/spec.md`, `tests/test_production.py`,
`workflow/warts.md`, `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
and `workflow/ongoing/fix-warts-3.md`, the change's directory moved to
`openspec/changes/archive/2026-10-07-production-reports-in-scope/`.
