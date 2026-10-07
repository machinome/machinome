## Context

Three defects of the production layer (`machinome/production/profile.py`,
the archived change `2026-10-04-production-layer`, the spec
`production-assets`), each a report refused or renamed for something that
is not the reader's concern. Line numbers are at the bench commit
`cd43432`.

### The Markdown gate

`_markdown(text, declaration, path)` (`profile.py:143-181`) runs when a
Step's instruction file is read (`_Shared.read_file`, `:1150-1174`), for
`steps`, for `export`, and for a manufactured `bom` line's Step
fingerprints. It refuses, in order: an unresolved reference link; any text
matching `</?[a-z][a-z0-9:-]*(?:\s[^>]*|/?)>` as an "unsupported HTML
dependency"; an image without an inline destination; a link or reference
definition whose destination is not `http://`, `https://` or `#`; an
autolink whose scheme is not HTTP(S); a `<file:` or `<data:` anywhere.
Every check runs over the whole text, code included.

The spec says what version 1 refuses ("Instructions remain local and
ordered"): "local links/images, raw HTML dependencies, file/data URLs and
unresolved referenced dependencies"; the production-layer design says
"raw HTML image/link sources". The HTML check refuses every tag-shaped
string instead. `if a<b then c>d ok` matches it (`<b then c>`: a letter
after `<`, then whitespace, then anything up to `>`), as does `x<y and
z>w`, `<kbd>Ctrl</kbd>`, and every tag written inside a code span or a
fenced block to quote markup. A Markdown link written inside a code span
(`` `[x](local.png)` ``) is refused as a local dependency, and a reference
definition inside a fenced block resolves a reference outside it. In
CommonMark none of these is a dependency: code is shown literally, and an
element that names no resource loads nothing.

### The overlap gate

`Production._read(name, build)` (`:366-385`) serves `bom`, `stock`,
`steps` and `mass`; `export` reads all four. Before building, it refuses
with `ProductionConflictError` if any finding of the shared root has code
`"overlap"`. The bindings of one root share one `_Shared`, so an overlap
under `right` refuses `left.bom`.

An overlap finding is built in `_Shared.resolve` (`:1112-1127`) for two
declarations of one binding whose reservations intersect:
`Finding("overlap", "error", overlaps, competitors, message)`, where
`overlaps` is the sorted tuple of the intersecting root-relative
occurrence paths (never empty) and `competitors` the two declaration
paths. A reservation is an Item's obligation set (the occurrence itself,
or every candidate within an assembly) or a delegated child's whole
subtree.

A binding's reports read the records whose occurrence lies within its
occurrence scope (`_records`, `:387-392`, `_within(record[2].path,
self._scope.path)`); the records of a parent Item that reaches inside a
child's subtree are among them. `findings` (`:394-416`) already keeps
exactly the findings whose occurrences lie within that scope (or, for a
finding with no occurrence, whose declarations lie within the declaration
scope). An overlap that names no occurrence within the reader's scope
cannot change any record the reader reads; one that names any can.

### Declaration paths of a tuple binding

`_Shared.resolve.populate` (`:1070-1110`) binds each selected occurrence of
a child-production declaration and names it:

```python
child._declaration_scope = (
    path if len(selected) == 1 else f"{path}-{index}"
)
...
# A repeat or tuple remains a tuple even with one member.
is_many = isinstance(target, tuple) or len(selected) != 1
is_many = is_many or self.snapshot.selection_is_many(
    target, scope=binding._scope
)
binding._children[name] = tuple(children) if is_many else children[0]
```

The shape of the binding (`is_many`) and the shape of its members' names
are decided by two different tests. A repeat or tuple with one member is
a tuple, as the design requires ("instance access returns a tuple for
repetitions"), but its member is named `kids`, while two members are
`kids-0` and `kids-1`. Every declaration path below a child binding is
built from its `_declaration_scope`: `BoundItem.declaration_path`,
`BomLine.declaration_paths`, `Finding.declarations`, `ResolvedStep.step_id`,
and in the draft manifest `bindings[].declaration_path`, the `owners`
values and the `instruction_files` keys. The production-layer design says
"Declaration paths likewise use `/` separators, with repetition indices
retaining model identity."

## Goals / Non-Goals

**Goals:**

- The Markdown gate refuses an HTML tag only when it can carry a
  dependency, and reads no code for dependencies, while every refusal the
  suite pins today stands.
- A binding's reports refuse only for an overlap that names an occurrence
  within its own scope; the root still refuses on any overlap; `findings`
  stays readable everywhere.
- A tuple binding's members are named by index at every count, so a
  declaration path keeps its shape when a count moves from one to two.

**Non-Goals:**

- Accepting HTML that names an external HTTP(S) resource (`<a
  href="https://...">`): it stays refused (Decision 1).
- The other items of the review's section: the bundle's absolute paths,
  `Finding.check_status`, the facade's copy of the lifecycle and the bytes
  held in memory are left to the pilot or untriaged.
- A Markdown parser dependency, or reading Markdown the way any renderer
  other than CommonMark does.
- Changing the manifest's `version`.

## Decisions

### 1. The gate reads what CommonMark renders, and refuses a tag that can carry a dependency

**What counts as a dependency tag.** A tag (`<name ...>` or `</name>`,
the name a letter followed by letters, digits or `-`, attribute values
quoted with `"` or `'` allowed to contain `>`) is a dependency when:

- its element is one that embeds, loads or executes content:
  `applet audio base embed frame iframe img link meta object picture
  script source style svg track video`; or
- it carries an attribute that names a resource: `action background data
  formaction href poster src srcdoc srcset style`, or any attribute whose
  name ends in `:href` (`xlink:href`).

Attribute names are read from the tag with its quoted values removed,
case-insensitively; a bare word in the tag counts as an attribute name,
so `<a title=src>` is refused (a word that happens to be an attribute name
refuses more, never less). `data-*` attributes are not `data`. The message
is unchanged: `unsupported HTML dependency in <path>`.

Every refusal the suite pins stays: `<video src>`, `<object data>`,
`<script src>`, `<iframe src>`. `<a href="https://...">` stays refused:
version 1 accepts external links in Markdown syntax, and taking HTML links
by their value would be a second link grammar for no project that needs
it.

**What is read.** Before any check, the text is reduced to what a
CommonMark renderer reads as Markdown or HTML, by a line scan:

- A fenced code block (a line of three or more backticks, with no
  backtick after them, or three or more tildes, indented at most three
  spaces) is dropped through its closing fence (the same character, at
  least as many, nothing else but whitespace), or through the end of the
  text when it is never closed.
- An HTML block is kept whole and nothing inside it is dropped. It opens
  at a line that begins, after any block-quote markers, list markers and
  indentation, with `<` followed by a letter, `/`, `!` or `?`. It closes
  as CommonMark closes it: at the line containing `</script>`, `</pre>`,
  `</style>` or `</textarea>` for those four elements, `-->` for a
  comment, `?>` for a processing instruction, `]]>` for CDATA, `>` for a
  declaration, and otherwise at the next blank line. Fences are not
  recognised inside it.
- Every other run of non-blank lines is a paragraph, whose code spans (a
  run of backticks, not preceded by a backtick or a backslash, closed by a
  run of exactly as many) become one space. A tag that starts before a
  backtick takes precedence over the code span, as in CommonMark: the
  scan matches `<[^<>]*>` and code spans left to right and keeps the tag.

Every existing check, references, images, link destinations, autolinks
and `file:`/`data:`, then runs over the reduced text, so a link or a
definition inside code is not a dependency either.

The scan reads more as HTML than CommonMark would wherever the two could
differ (an HTML block recognised inside any container, at any indentation;
a fence recognised only at the top level); every such difference makes
the gate refuse more. Indented code blocks are not dropped, for the same
reason: telling one from a paragraph continuation needs the full block
grammar.

**Cases** (the Stage P probe, `probe_markdown.py`, runs the proposed gate
on all of them; 46 of 46 as listed):

| Accepted after the change (refused today unless marked) | Refused before and after (unless marked) |
|---|---|
| `if a<b then c>d ok`, `keep x<y and z>w` | `<img src="x.png">`, `<IMG SRC=x.png>` |
| `5 < 6 > 4` (accepted today) | `<a href="x.pdf">`, `<a href="https://example.com">` |
| `` write `<img src="x.png">` to embed `` | `<link rel="stylesheet" href="x.css">` |
| ``` ``a ` <script src=x> ` b`` ``` | `<script src="x.js">`, `<script>fetch('x')</script>` |
| a fenced (backtick or tilde) block holding `<img src>` or `<link href>` | `<style>@import 'x.css';</style>` |
| `press <kbd>Ctrl</kbd> and <br/> then <sub>2</sub>` | `<video src>`, `<object data>`, `<iframe src>` |
| `<div class="note">` … `</div>` | `<span style="background:url(x.png)">` |
| `` `[x](local.png)` `` | `<svg><use xlink:href="x.svg#a"/></svg>` |
| a fenced `[ref]: local.pdf`, then HTTPS and `#` links | `<a title="x>y" href="z">` |
| `` > quoted `<img src=x.png>` code `` | ``<img src="`x.png"> ` `` (the tag precedes the backtick) |
| `` - item `<script src=x>` code `` | ``\` <img src=x.png> ` `` (an escaped backtick opens nothing) |
| an unclosed fence, then `<img src=x>` | a backtick pair across a blank line around `<img src>` |
| `` Plain *Markdown* with `code` and <https://example.com>. `` (accepted today) | `` `<img src>` `` inside a `<div>`, `<pre>` (across a blank line), block-quoted or listed HTML block |
| | a fence inside an HTML block; a comment holding a fence, then `<img src>` after it |
| | `![x](local.png)`, `[x](../outside.md)`, `[x][ref]` + `[ref]: local.pdf`, `[x][missing]`, `<mailto:...>`, `<ftp://...>` |
| | `[x][ref]` whose only definition is in a fenced block (accepted today) |

**Alternatives.** (a) A CommonMark parser: the framework declares none
(`pyproject.toml`'s dependencies), and the spec forbids a mandatory heavy
dependency; refused. (b) Stripping backtick pairs with one regular
expression and keeping the tag check as it is: a backtick inside an HTML
block or after a tag would excuse a real `<img src>` (the refused column's
precedence and HTML-block rows are exactly those), and the inequality
would still be refused; refused. (c) Accepting HTML whose resource
attributes all hold HTTP(S) values: a second link grammar with no project
asking for it; left as it is.

**Code shape.** In `machinome/production/profile.py`, above `_markdown`:
module constants `_FENCE`, `_CONTAINER`, `_HTML_BLOCKS` (the six start
and end patterns), `_SPAN_OR_TAG`, `_TAG`, `_EMBEDDING` and
`_DEPENDENCY_ATTRIBUTES`; a function `_rendered_text(text)` doing the line
scan; a function `_html_dependency(tag)` taking a `_TAG` match. In
`_markdown`, `text = _rendered_text(text)` first, and the HTML check
becomes `if any(_html_dependency(tag) for tag in _TAG.finditer(text)):`.
The code is the probe's (`probe_markdown.py`, copied into evidence.md at
task 1.1), formatted by `black` (the repository sets no line length,
so its default) and passing `flake8 --max-line-length=89`. All names are private.

### 2. A binding refuses for the overlaps in its own scope

`Production` gains a private method `_in_scope(finding)` holding the
predicate `findings` uses today:

```python
def _in_scope(self, finding):
    if finding.occurrences:
        return any(
            _within(path, self._scope.path) for path in finding.occurrences
        )
    return any(
        _within(path, self._declaration_scope or ".")
        for path in finding.declarations
    )
```

`findings` keeps `f for f in self._shared.findings if self._in_scope(f)`
(the same set as today). `_read` refuses with the overlap findings for
which `self._in_scope(f)` holds, and its message joins only theirs:

```python
if name != "findings":
    overlaps = [
        f
        for f in self._shared.findings
        if f.code == "overlap" and self._in_scope(f)
    ]
    if overlaps:
        raise ProductionConflictError(
            "overlapping ownership: "
            + "; ".join(f.message for f in overlaps)
        )
```

An overlap always names at least one occurrence, so only the occurrence
half applies to it. The test is the one `_records` uses for what the
reports read, so a reader refuses exactly when an overlap names an
occurrence it reads. The root's scope is `.`, within which every path
lies: the root refuses on any overlap, as today. A parent Item reaching
inside a delegated child's subtree names occurrences within the child's
scope: the child refuses, its sibling does not. A child's `export` reads
its four reports and so succeeds or refuses with them; its bundle's
findings are its own scoped findings, as today.

The Stage P probe (`probe_remedies.py`, which patches `_read` in its own
process) printed, for the overlap under `right`: `left.bom` quantities
`[2]`, `left.mass.complete False`, `left.steps ()`, `left.export(...)`
`coverage_complete True`; `right.bom`, the root's `bom` and the root's
`export` refused, the root's export target not created; `right.findings`
and the root's `findings` the three overlaps. For the parent Item reaching
inside `left`: `left.bom` and the root's `bom` refused, `right.bom`
quantities `[3]`.

**Alternative.** Testing the overlap's competing declaration paths against
the reader's declaration scope: a parent Item reaching into `left` is
declared at the root (`extra`), outside `left`'s declaration scope, so
`left` would read a BOM counting its nuts twice. Refused; occurrences are
what the reports read.

### 3. A tuple binding's members are always indexed

In `populate`, the tuple test moves above the loop and names the members:

```python
target = self.child_targets[id(declaration)]
selected = self.selected(binding, target, path)
# A repeat or tuple remains a tuple even with one member, and
# its members are named by index at every count.
is_many = isinstance(target, tuple) or len(selected) != 1
is_many = is_many or self.snapshot.selection_is_many(
    target, scope=binding._scope
)
children = []
for index, occurrence in enumerate(selected):
    ...
    child._declaration_scope = f"{path}-{index}" if is_many else path
    ...
binding._children[name] = tuple(children) if is_many else children[0]
```

The expression and its short-circuit order are today's, so
`selection_is_many` is still never handed a tuple. A single non-repeated
reference still binds one production named `path`. The index is the
member's position in the selection, as today.

This changes published values for one case only: a repeated or tuple
child binding that selects exactly one occurrence. Its members' paths
gain `-0` in every record listed in Context, the draft manifest included;
the manifest's shape and `version` (1) do not change. The Stage P probe
(`probe_holder.py`) shows the manifest today: a `Holder` with `n = Count(1)`
and `kids = Submodel(count=1).repeat(n)`, under `kids =
SubProduction(Holder.kids)`, exports `bindings` `['', 'kids']` and owners
`['kids/arbitrary_name']` at `n=1`, and `['', 'kids-0', 'kids-1']` with
`kids-0/arbitrary_name` and `kids-1/arbitrary_name` at `n=2`.

**Who reads these paths.** The framework's tests pin no declaration path
of a one-member tuple binding (`test_zero_repeat_is_not_absent_and_
single_repeat_child_stays_tuple` asserts the tuple only). A search of
every `*.py` under `projects/` finds `machinome.production` only in the
Curta slice; its child bindings, listed through the overlay at Stage P
(`curta_bindings.py`), are three single references (`crank`,
`frame_nuts`, `upper_frame_nuts`), two single references (`result_wires`,
`turns_wires`) and their tuples `springs` of ten and five members, already
`springs-0` to `springs-9` and `springs-0` to `springs-4`. Its test pins
no declaration path. Nothing the slice reads or pins changes.

**Alternative.** Indexing only repeats and leaving a one-member tuple of
references unindexed: the spec and the design make both tuples, and a
tuple's member count is the author's to change, so the same break would
remain. Refused.

### 4. Tests

In `tests/test_production.py`:

- `test_markdown_gate_accepts_what_is_not_a_dependency`, parametrized
  over the accepted column of Decision 1 (each `_markdown(text,
  "declared/step", tmp_path / "instruction.md")` returns `None`). RED
  today for every case but `5 < 6 > 4` and the plain-Markdown line, which
  stay as guards.
- `test_markdown_gate_refuses_html_dependencies_outside_code`,
  parametrized over the refused column's HTML, precedence, escape,
  blank-line and HTML-block rows, and the fenced-definition row
  (`pytest.raises(ProductionExportError)`). Guards, green today, except
  the fenced-definition row, RED today.
- `test_an_inequality_in_a_step_is_read`: a `_profile_module` profile
  over `Submodel` whose Step's `assembly.md` is `"if a<b then c>d ok\n"`;
  `profile.steps[0].instruction_text` is that text, and
  `profile.export(tmp_path / "bundle")` succeeds with the text in
  `instructions.md`. RED today with `unsupported HTML dependency`.
- `test_an_overlap_refuses_only_the_reports_of_its_scope`: a `Twice`
  child profile (two Items on `Submodel.nuts`) bound at `Root.right`,
  `SubProduction` at `Root.left`. `left.bom` is one assigned line of
  quantity 2, `left.stock`, `left.steps` and `left.mass` read, and
  `left.export(tmp_path / "left")` succeeds; `right.bom`, the root's
  `bom`, `mass` and `export(tmp_path / "root")` raise
  `ProductionConflictError` and leave no target; `right.findings` and the
  root's `findings` each hold the three overlap findings and `left.findings`
  is empty. RED today at `left.bom`.
- `test_a_parent_reaching_into_one_child_leaves_its_sibling_readable`:
  `left = SubProduction(Root.left)`, `right = SubProduction(Root.right)`,
  `extra = Item(Reference(Root, ("left", "nuts")), Sourced(NUT))`;
  `right.bom` is one line of quantity 3, `left.bom` and the root's `bom`
  raise. RED today at `right.bom`.
- `test_tuple_binding_members_are_always_indexed`: the `Holder` of
  Decision 3 at `n=1` and `n=2`, a one-member tuple of references
  (`SubProduction((Reference(Root, ("left",)),))`) and a two-member one;
  for each, `[k.arbitrary_name.declaration_path for k in bound.kids]` is
  `[f"kids-{i}/arbitrary_name" ...]`, the BOM's `declaration_paths`
  match, and at `n=1` the exported manifest's `bindings` declaration
  paths are `["", "kids-0"]`. A single reference (`kid =
  SubProduction(Root.left)`) stays `kid/arbitrary_name` (guard). RED
  today at `n=1` with `['kids/arbitrary_name']`.

The two existing Markdown tests (`test_requested_steps_and_export_refuse_
unsupported_dependencies`, `test_markdown_refusal_is_contextual_and_
leaves_no_target`) and the two existing overlap tests
(`test_delegation_ownership_conflict_has_all_declarations`,
`test_empty_assembly_delegation_is_an_ownership_boundary`) are unchanged
and must stay green.

### 5. Records

- **Manual.** `docs/reference/api.rst`, production section: after
  "Unsupported local links, images, reference dependencies and raw HTML
  dependencies are refused.", add: "An HTML tag is a dependency when its
  element embeds or loads content or an attribute names a resource;
  other text, such as ``a<b``, is not. Text in code spans and fenced code
  blocks is not read for dependencies." After "Repeated child bindings are
  tuples, including a one-member repetition.", add: "Their members'
  declaration paths carry the member's index at every count, as
  ``kids-0/nut``." Replace "Overlapping owners remain inspectable in
  ``findings`` and refuse other reports with ``ProductionConflictError``."
  with "Overlapping owners remain inspectable in ``findings`` and refuse
  the other reports, with ``ProductionConflictError``, of every binding
  whose scope holds an occurrence they both claim; the root's scope holds
  every occurrence."
- **Changelog**, one bullet appended to the `Unreleased` section:

  ```rst
  * **A production reports what is in its scope.** An instruction's
    Markdown is refused for an HTML tag only when the tag can carry a
    dependency, an element that embeds or loads content or an attribute
    that names a resource, and code spans and fenced code blocks are not
    read for dependencies, so ``if a<b then c>d`` and a quoted
    ``<img src>`` in code no longer refuse ``steps`` and ``export``. A
    child binding's reports are refused only for an overlap that claims an
    occurrence within its scope, so an overlap under one child no longer
    refuses its sibling; the root still refuses on any overlap. And the
    members of a repeated or tuple child binding are named by index at
    every count: a one-member repetition's member is ``kids-0``, as the
    first of two is, where it used to be ``kids``, in every declaration
    path and in the draft manifest (production-reports-in-scope).
  ```
- **Warts.** The three items move verbatim to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
  `` ## `production-reports-in-scope` ``, with a "What shipped" paragraph.
- **No ADR.** The decisions apply the spec's own rules (what version 1
  refuses, ambiguous totals, tuple bindings) to the code; no architecture
  moves.

## Proof plan

- **Red first.** The tests of Decision 4, run on the unmodified code:
  every one marked RED fails for the reason named.
- **Reproductions.** `repro_reports.py` before and after: the gate's
  direct cases (the inequalities, code span, fenced code and `<kbd>`
  accepted; the dependency rows refused); the step reading the
  inequality; `left`'s reports readable, `right`'s and the root's refused,
  in the first fixture; `right` readable, `left` and the root refused, in
  the second; `kids-0/arbitrary_name` at `n=1`, a one-member tuple
  `kids-0/arbitrary_name`, a single reference `kid/arbitrary_name`.
  `probe_holder.py`: `bindings` `['', 'kids-0']` at `n=1`.
- **Originating project.** The Curta slice through cycle 10's overlay,
  before and after, with counts and times, and `git status --short` of the
  Curta unchanged; `curta_bindings.py` before and after, the same 21
  binding paths. The proposed gate accepts the slice's twelve Markdown
  files, as the present one does (Stage P, both gates run on each).
- **Suites.** The focused production and model-consumption suites, then
  the full suite once, alone.

## Risks / Trade-offs

- [The gate's line scan is not a CommonMark parser] → Every place it can
  differ from one reads more text, so it refuses more; the refused column
  of Decision 1 pins the precedence, escape, blank-line, container and
  HTML-block cases that a looser scan would excuse.
- [A one-member tuple's paths change in a released format] → The
  manifest's version stays 1: its shape is unchanged, and the old value
  broke the design's own rule that repetition indices are kept. No project
  pins such a path (Decision 3). The changelog states it.
- [A child export succeeds while its root refuses] → That is the intended
  scope: the child's totals are not ambiguous. Its bundle lists its own
  findings, which do not include the sibling's overlap; the root's
  bundle, which would, is still refused.

## Open Questions

1. **Should version 1 accept an HTML link to an external HTTP(S)
   resource?** Markdown links to one are accepted; `<a
   href="https://...">` stays refused. No project asks for it.
   Recommendation: leave it refused until a project's instructions need
   HTML for something Markdown cannot say. For the pilot, if ever.
   Answered at review (7 October 2026): left refused.
2. **Does a one-member tuple's path change need the manifest version to
   move?** Recommendation: no (Decision 3, Risks). For the orchestrator's
   review. Answered at review (7 October 2026): no; the shape is
   unchanged and the old value broke the design's own rule.
