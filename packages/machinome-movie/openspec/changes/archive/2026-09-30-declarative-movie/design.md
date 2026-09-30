## Context

The target is the Python source in the Leonardo project's
`videos/cut_and_advance/spec.md` ("The Python source"). It is written against
`docs/movie-document.md` (draft, 30 September 2026) and the domain model of
`workflow/ongoing/declarative-python-api.md`. The document's fields keep the
meaning `docs/FORMAT.md` gives them in format 0.4 and `production.yaml`.

Framework facts this design relies on, verified on the framework's 0.7.1
checkout: a node constructed in a node class body is a `ChildDeclaration`
(`node_class`, `kwargs`, `_name`); reading a child off a declaration yields a
`machinome.motion.couplings.PathRef` (`root`, `segments`, `written`), checked
against the classes when written, so `Mill.feed.pawll` is refused by the
framework at that line naming `feed.pawll`; `declared_children(cls)` lists a
class's children by attribute. An export names a child by its `name` keyword,
else its attribute. Importing a model builds nothing.

## Goals / Non-Goals

Goal: a source of the draft's shape evaluates, deterministically and without
building CAD, to a document the Node side loads; every mistake the draft can
contain is refused by name before speech is generated. Non-goals: resolving
anchors, speech, the React stage, running or clocked takes, and anything the
film does not use.

## Decisions

### D1. Found by type; named by attribute

A chapter scans its class body in declaration order and keeps what it
recognises by type: exactly one `Narration`, its elements (`View`, the
source panel), its `Shot`s. A movie keeps its `Chapter` instances, exactly
one `Format`, one `Narrator`, and at most one each of a style, `Evidence`,
`Credits` and `Release`. A `Loop` keeps its `Camera`, `Layer`, `Source` and
`Still` declarations. Other attributes are ignored. The attribute name is the
declaration's name: chapter id, shot id, camera preset, layer, snippet and
still names. Names in the document are slugs (`^[a-z0-9-]+$`, the 0.4 id
rule), so an attribute's underscores become hyphens (`title_wide` is camera
`title-wide`, `coupling_shot` is shot `coupling-shot`), and an attribute with
any other character outside `[a-z0-9_]` is refused.

The exceptions are values that have no type to be found by: a movie's
`title`, `series`, `status` and `learning_goal`, and a loop's `model`,
`export`, `marks` and `readiness`, are read by those attribute names, which
the draft spells. They are fields of the one object, not members of a
collection. `title`, `status` and `learning_goal` are required; `series` is
optional (the renderer defaults it to the title).

### D2. Sets and slots

`Set` is the base; `Paper` declares `stage`, `PaperSplit(Paper)` declares
`left` and `right`, `SourceOnly(Paper)` declares `source`. A set's slots are
the ones its own class body declares: a derived set inherits the chrome (and
`Paper.style`), not the layout, so `PaperSplit.stage` is refused as a slot
`PaperSplit` does not have. The document names are `paper`, `paper-split`,
`source-only`.

Reading a slot off its set (`Paper.stage`) hands back a fresh placement key
each time. This is what makes "a slot filled twice" detectable in a dict
literal, `{Paper.stage: a, Paper.stage: b}`, which would otherwise collapse to
one key before any code sees it. Every slot of the shot's set must be filled.
`Paper.stage` holds a `View`; `PaperSplit.left` a source panel and `.right` a
`View`; `SourceOnly.source` a source panel.

A `Set` or `Element` subclass declared outside `machinome_movie` is refused at
class creation: the stage that would draw it does not exist yet.

### D3. Elements are declared on the chapter

A shot may place only elements its chapter declares (identity); an inline
`View(...)` in a shot is refused naming the shot and the slot. The draft's
`carriage_shot` does exactly that and also calls `View.highlight(...)` on the
class; the evaluated form declares `wide = View(Sawmill, camera=Sawmill.whole_near,
hide=[Sawmill.structure, Sawmill.water])` on the chapter and cues
`wide.highlight(Mill.carriage, others="dim")`. A cue may act only on an
element the same shot places, since a view's actions become the shot's
camera keys and highlights and a panel's become its code.

### D4. Narration and anchors

`Narration(text)`: whitespace runs collapse to one space and the ends are
stripped, so a triple-quoted paragraph and a concatenated one are the same
narration (as YAML folding did). `lines.spoken(phrase, plus=0)`,
`lines.spoken_end(phrase, plus=0)` and `lines.end(plus=0)` make anchors;
the document gets `{"spoken": p}`, `{"spokenEnd": p}` and a `plus` only when
it is not zero. A number is shot-local seconds, as written.

A phrase must occur exactly once in its chapter's narration, counted as an
exact, case-sensitive substring, overlapping occurrences included, so
`"wheel"` in a narration holding "wheel" and "waterwheel" is refused as
repeated. An anchor made from another chapter's narration is refused.

`lines.end()` is "the end of the whole narration". The document has no such
anchor, and the renderer resolves spoken phrases only; it is emitted as
`spokenEnd` of the shortest run of the narration's last words that occurs
exactly once in it, with edge punctuation removed (`"moment"` for "…at just
the right moment?"). Rejected: the whole narration as the phrase (exact but
repeats every word of it in every anchor) and a new anchor kind (outside the
contract).

### D5. The take

`Loop` subclasses carry `model` (the node class), `export` (the export
directory), `marks` (name → model seconds of the loop), `readiness`, and
their cameras, layers, sources and stills. `Loop.run(a, b)` is a linear span
(numbers or mark names); `Loop.keys({anchor: mark | (mark, ease)})` are model
keyframes. A keys mapping must have a key at `0` and a key equal to the
shot's `until`; its values are marks, emitted as `{"mark": name}` in `from`,
`to` and each key's `seconds`. Numbers in `run` stay numbers. An unknown mark
is refused at the chapter's creation naming chapter, shot and mark. The
document carries one model: every take-bound declaration a movie uses (views,
panels, stills, simulations) must be of one `Loop`, or evaluation refuses
naming both.

A `Camera`'s `up` defaults to `(0, 0, 1)`, machinome's convention; the draft
omits it everywhere but `reduction_rolled`. A camera must be declared on the
view's loop (or a base of it), a layer likewise.

### D6. Paths

Every path written in a declaration is relative to the file of the class that
declares it (a loop's `export`, sources and stills; a movie's evidence,
licence file and description), as a YAML path was relative to its file. The
document carries each path relative to `root`, and `root` is the movie's
directory relative to where the document is written: `..` for the default
`<movie dir>/_build/movie.json`. So a loop declared in one module and used by
a movie in another keeps working. Paths are joined without touching the
filesystem and written with `/`.

### D7. Parts

A part is a `ChildDeclaration` of the loop's model (`Mill.carriage`) or a
`PathRef` through one (`Mill.feed.pawl`). Its root must be a child the model
declares (identity against `declared_children`); each segment walks
`declared_children` of the previous class; each step's export name is its
`name` keyword, else the attribute. A path that ends on something that is
not a child (a port, a joint) is refused. At evaluation every part path, and
every layer path, must exist in the export manifest's `root` tree, or
evaluation refuses naming the written spelling (`LeonardoHydraulicSawmill.feed.pawl`)
and the export path it resolved to.

### D8. Shots map onto the document

- `id` from the attribute; `set` from the set class; `until` from the anchor
  or number.
- `simulation` from `model=`, which every shot needs (a shot is always posed).
- `camera`: the placed view's current camera at `0`; each `move(camera,
  ease=, until=)` adds a hold key at its cue's anchor (unless that is `0`) and
  a key at its `until` with the target and its `ease`. A move's end is its own
  `until`, not the cue's. The view's camera after the shot is the last move's
  target, and the next shot of the chapter placing that view starts there
  (the draft's `question` shot holds `title-near` this way). Moves are emitted
  in cue order; ordering them in time is the resolver's check.
- `hiddenLayers` from the placed view's `hide`.
- A shot that places no view (`SourceOnly`) is still posed, as the contract
  says; it poses the chapter's view, which must then be the only view the
  chapter declares.
- `highlight` from `view.highlight(*parts, others=)`, from the cue's anchor
  to its `until`.
- `annotations` from `Ring`, `Label` and `Arrow`, from the cue's anchor to its
  `until`; they need a view placed in the shot.
- `overlays` from `Title(text, subtitle=, position="title", enter=, leave=,
  reveal=)`; `position` is `title`, `top`, `lower-third` or `center`, and
  `subtitle`, `enter` and `leave` belong to a title only. `Reveal.spoken()`
  is `{"timing": "spoken"}`.
- `code` when the shot places a source panel: `snippet`, `typing` from
  `type(through_line=, over=)` (`from` the cue's anchor, `to` that anchor plus
  `over`), `emphasis` from `emphasize(*words, hold=0)`. The emphasis `phrase`
  is the phrase of the cue's anchor, which must be `spoken` with no `plus`
  (the words light at their own onsets, so a shifted anchor would be ignored
  silently). Its `line` is the excerpt's last line: Python does not read the
  source file, and the film emphasises the line it types through. A panel
  placed with no typing cue is refused (the renderer requires one).
- `pictures` from `still.show(area=, fit=, enter=, leave=, view=[(at, center,
  zoom[, ease]), …])`, from the cue's anchor to its `until`.
- `transition`, `fadeIn`, `fadeOut` from `Dissolve(d)`, `Fade(d, color=)`,
  `Wipe(d, direction=)`, `Slide(d, direction=)`, `FadeIn(d)`, `FadeOut(d)`,
  each with an optional `ease`.
- An entrance or exit is a number (a fade of that duration) or a tuple
  `(kind, duration[, ease])`.
- A cue that shows something for a span (highlight, annotation, title,
  picture) needs `until`; a cue whose actions carry their own end (move,
  type, emphasize) does not.
- `hiddenLayers`, `overlays` and `evidence` are always emitted, as lists;
  shots cite no evidence, since the draft names none per shot (`[]`).
  `annotations`, `highlight`, `pictures`, `code` and optional fields are
  emitted only when present, and optional values only when written.

### D9. The movie maps onto the top level

`format` `machinome-movie/0.1`; `id` the slug of the name the movie is
declared under in `pyproject.toml`; `output` from `Format(w, h, fps=)`;
`model` from the loop and its export (`manifest`, `expectedDurationSeconds`
from the manifest's `animation.loop`, `timeMode` `normalized-loop`,
`sourceRevision` from `source-revision.txt` or `null` when the export has
none, `readiness`); `marks`; `audio` from `Narrator(provider, model, voice,
label=, output=, settings=, direction=)` as `provider`, `model`, `voice`,
`voiceLabel`, `outputFormat`, `voiceSettings`, `direction`; `style` from
`Paper.style(background, foreground, accent, font, safe_inset)` as
`background`, `foreground`, `accent`, `fontFamily`, `safeInsetFraction`;
`cameras`, `layers`, `sourceCode`, `stills` from the loop (all it declares);
`clips` `{}`; `evidence` from `Evidence(**names)`; `credits` from
`Credits(project, creator, copyright, license, license_file)`; `release` from
`Release(simulation_url, source_url, description)` as `simulationUrl`,
`sourceUrl`, `descriptionTemplate`. `publish` is not emitted; nothing reads it.

### D10. Canonical JSON

Sorted keys, two-space indent, UTF-8 without escaping, a trailing newline;
a float with an integral value is written as an integer (`1460`, not
`1460.0`), as JavaScript writes it. Two evaluations are byte-identical.

### D11. Purity

Evaluation reads the export's `manifest.json` and `source-revision.txt`;
the command line also reads the project's `pyproject.toml` and imports the
movie's module. Nothing else: no clock, randomness, network or CAD build. The
document schema is read once, when the package is imported, as part of the
code.

### D12. The document check

`check_document(document, manifest=None)` validates the schema and the
refusals Python can make before speech: unique chapter and shot ids, phrases
once in their chapter's narration, known marks, model keys from `0` to the
shot's `until`, known camera presets, layers, snippets and stills, the set's
code rule (`paper` without code, `paper-split` and `source-only` with it),
and, given the manifest, every part path. Evaluation applies it to its own
output. The shared invalid fixtures run through it; those only the resolver
can refuse (an anchor that resolves before its shot starts) are skipped by
name, with the reason, in the test.

### D13. Schema and validator

The Node side has not written `schema/machinome-movie-0.1.json` in this
worktree, so this change writes it from the contract page (JSON Schema
2020-12, closed field lists); the Node side may replace it. The package
depends on `jsonschema` and validates with its 2020-12 validator; the
schema ships inside the package through a symbolic link to the repository
file, so there is one schema file.

Amended 30 September 2026 at the orchestrator's review of the planning
commit: the first version of this decision wrote a subset validator, because
`jsonschema` was not installed and the no-network rule was read as covering
`pip`. The rule covers the package's code and its tests, not installing a
declared dependency; `jsonschema` is installed and the subset validator and
its cross-check test are dropped.

### D14. Command line and project table

`[tool.machinome.movies]` maps a name (the model-name rule: letters, digits,
`_`, `-`) to `module:Class`. `python -m machinome_movie evaluate <project>
<movie> [--out FILE]` puts the project on `sys.path`, imports the module,
evaluates, and writes `<movie dir>/_build/movie.json` (or `--out`); `list`
prints the table. A refusal prints `machinome-movie: <message>` and exits 1.

### D15. Fixtures

The fixture project is `python/tests/fixtures/project/`: a pyproject with a
`[tool.machinome.models]` and a `[tool.machinome.movies]` table, a trivial
`AssemblyNode` model, a hand-written export whose `root` names its children,
a still, and two movies at `videos/minimal/movie.py` and `videos/tour/movie.py`
laid out as a project lays its films out. The fixtures README said
`python/tests/movies/<name>.py`; that cannot satisfy "declared in the
project's `pyproject.toml`", which imports movies from the project, so the
README is corrected to the project path. `source-revision.txt` is the commit
a test makes of the fixture project (the export excluded) in a temporary
repository with a fixed author, committer and date, so it is reproducible and
the source pinning the renderer does can be exercised. `fixtures/manifest.json`
lists the two document names; `takes/` is left to the Node side, since the
contract page does not give the speech cache's record shape.

## Spellings that differ from the draft source

- `carriage_shot`: the inline `View(...)` and `View.highlight(...)` become a
  declared `wide` view and `wide.highlight(...)` (D3). The film's spec has
  since been updated with this spelling.
- Shot ids come from attributes: `coupling_shot`, `pawls_shot` and
  `carriage_shot` give `coupling-shot`, `pawls-shot` and `carriage-shot`. To
  get the shot list's `coupling`, `pawls` and `carriage`, the source spells
  the attributes that way; nothing collides.
- The movie's paths are relative to `movie.py`, as the draft writes them.

## Deviations from the contract page

- `lines.end()` is emitted as a `spokenEnd` phrase (D4); the renderer needs
  nothing new.
- A picture's view key `at` may be an anchor (the draft keys the still's push
  on a phrase); the contract page lists anchors for `until`, camera and model
  keys, cues and typing, not view keys.
- Documents without `style`, `credits` or `release` are valid (the minimal
  fixture has none); `evidence` is always present, possibly empty.
- Shot `evidence` is `[]` (D8).

## Risks / Trade-offs

- Substring counting refuses some phrases a word-level rule would accept;
  it is the stricter reading and the refusal names the phrase.
- Emphasis on the excerpt's last line only: a film that needs another line
  asks for a `line=` then.

## Open Questions

None blocking; the Node side's acceptance of the deviations above is the
merge's question.
