## Context

The target is "The Python source" of the Leonardo project's
`videos/cut_and_advance/spec.md`, version 2, and the document it must
evaluate to, `docs/movie-document.md` (`machinome-movie/0.2`) with
`schema/machinome-movie-0.2.json`. Both were written by the campaign's
orchestrator before this cycle; the contract is authority, and where it is
ambiguous this design names the reading it takes and records the finding in
`evidence.md` under "Contract findings". The previous cycle's design
(`openspec/changes/archive/2026-09-30-declarative-movie/design.md`) stands
where this one does not replace it: found by type, named by attribute (D1),
narration and anchors (D4), the take (D5 less its document shape), paths (D6),
parts (D7), canonical JSON (D10), the command line (D14).

## Goals / Non-Goals

Goal: the film's source, with the spellings recorded below, evaluates
deterministically and without building CAD to exactly the 0.2 document; every
mistake the contract refuses and Python can see before speech is refused by
name, at class creation where every class involved is known and at
evaluation otherwise. Non-goals: resolving anchors, speech, the stage runtime,
anything the film does not use.

## Decisions

### D1. Sets

`Set` is the base. A set's **kind** is the slug of its class name
(`Leonardo` → `leonardo`, `LeonardoSplit` → `leonardo-split`, `HTMLCard` →
`html-card`: a hyphen before an upper-case letter that follows a lower-case
letter or digit, or that starts a capitalised word after an acronym), unless
its own body writes `kind = "…"`, which must be a slug. The kind is never
inherited. Its **slots** are the `Slot()` declarations of its own body, in
declaration order, named by attribute (underscores become hyphens); a
derived set inherits the chrome, not the layout, so `LeonardoSplit.stage` is
not a slot of `LeonardoSplit`. `Slot()` takes no argument: the set does not
know what it holds, and `Slot("view")` is refused saying so. Reading a slot
off its set still returns a fresh placement key, so a slot written twice in
one dict literal stays detectable.

A set defined outside the package is the **project's**: it needs `module`, a
string ending `.ts`, `.tsx`, `.js` or `.jsx`, relative to the file of the
class that writes it (a derived set inherits its base's `module`, resolved
against the base's file). Its **props** are the other plain attributes of its
own body, by name as written, each a JSON value (str, int, float that is
finite, bool, None, list, dict with string keys, recursively); anything else
is refused naming the set and the attribute. Functions, static and class
methods and properties are Python machinery, not props. A project kind that
is a kind the tool ships (`frame`, `split`, `paper`, `paper-split`,
`source-only`) is refused. The **base** of a set is its nearest `Set`
ancestor other than `Set`, by kind.

The package ships `Frame` (`stage`) and `Split` (`left`, `right`); in the
document they carry only `slots`. `Paper`, `PaperSplit` and `SourceOnly`
leave the package: the stage runtime keeps them for YAML episodes.

### D2. Elements

`Element` is the base. The package's elements are `View`, the source panel
(`Source.panel`, kind `source`), `Title` and `Picture`. A subclass defined
outside the package is the **project's**: kind the class-name slug (D1's
rule; no override, no use for one), `module` as for a set, and
`Action(param=type, …)` declarations whose attribute is the action's name (a
slug) and whose parameters map a name to `str`, `int`, `float` or `bool`
(kinds `string`, `number`, `number`, `boolean`); any other type is refused
naming the element, the action and the parameter. Any other plain attribute
of the class is refused: an element's props are given where it is declared.
Deriving a project element from a shipped one is refused; from another
project element, the actions of both are its actions.

An instance takes keyword arguments only; they are its props, each a JSON
value whose kind is `string`, `number` (int or float, not bool), `boolean`,
`list` or `object`; `None` has no kind and is refused. Reading a declared
action off an instance returns a callable; calling it with keyword arguments
yields the cue's action. Every declared parameter is required, no other is
accepted, and each value must be of its declared type (`int` for `int`, `int`
or `float` for `float`, never a bool for a number); a refusal names the
element's kind, the action and the parameter.

The document's `stage.elements[kind]` is `{module, props, actions}`: `props`
maps each prop name to its kind, taken from the instances the movie declares;
all instances of a kind must give the same names with the same kinds, or the
movie is refused naming the kind, the prop and the two chapters. `actions`
lists every declared action with its parameters' kinds.

### D3. Shipped elements and their actions

- `View(loop, camera=, hide=[layers])` → `{"kind": "view", "camera", "hide"?}`
  (`hide` when not empty). Actions: `move(camera, until=, ease=)`,
  `highlight(*parts, others=)`, `ring(part, enter=, leave=)`,
  `label(part, text, offset=, enter=, leave=)`, `arrow(part, text=None,
  place=, enter=, leave=)`. A camera must be declared on the view's loop; a
  part is a declaration path of the loop's model, resolved to export names.
  The free-standing `Ring`, `Label` and `Arrow` leave.
- `Source.panel(excerpt)` → `{"kind": "source", "source"}`. Actions:
  `type(through_line=, over=)` → `{throughLine, over}`; `emphasize(*words,
  hold=)` → `{words: [{spoken, token}], hold?}`, a word being `"token"`
  (spoken and token equal) or `("spoken words", "token")`.
- `Title(text, subtitle=None)` → `{"kind": "title", "text", "subtitle"?}`.
  Action `show(enter=, leave=, reveal=)`; `reveal` is `Reveal.spoken()`,
  `{"timing": "spoken"}`, whose phrase is the title's text.
- `Picture(still, fit=None)` → `{"kind": "picture", "still", "fit"?}`, `fit`
  `contain` or `cover`. Action `show(enter=, leave=, view=[(at, center, zoom[,
  ease]), …])`.

An entrance or exit is a number (a fade of that many seconds) or `(kind,
duration[, ease])`; `draw` is accepted on the entrance of a ring or an arrow
only. `move` and `type` do not span; `emphasize` spans its phrase and its
hold on its own; every other action spans and needs its cue's `until`.

### D4. Emphasis

The cue's anchor must be `lines.spoken(phrase)` with no `plus`. Each spoken
part must occur exactly once in that phrase, word-bounded: not preceded or
followed by `[A-Za-z0-9_]`. Each token must match `[A-Za-z_][A-Za-z0-9_.]*`
and occur exactly once in the whole excerpt, on any line, identifier-bounded:
not preceded or followed by `[A-Za-z0-9_.]`. So `feed.pawl.turn` is one token
and neither `pawl` nor `feed.pawl` occurs in it. Both character classes are
ASCII so the two runtimes agree. The phrase checks are made at class
creation; the token checks need the excerpt's text, so evaluation reads the
source file of every excerpt an `emphasize` lights (only those) and refuses a
token absent from or repeated in it, naming the chapter, the shot, the cue,
the token and the excerpt. This amends the previous cycle's purity rule
(D11): evaluation opens the export's manifest and revision and those source
files, nothing else.

### D5. Chapters, shots and cues

A chapter finds its elements by type (any `Element` instance) in declaration
order; the element's key is its attribute's slug. A shot's placements are
`{Set.slot: element}`: the slot must be one of the shot's set's own slots,
filled once; the element must be one the chapter declares, and placed in at
most one slot of the shot. Slots not named are empty. Every shot needs
`model=` (every view of the shot sees that time). A cue's actions must act on
elements the shot places.

The document keeps the declarations' shape: a chapter is `{id, narration,
elements, shots}`; a shot `{id, set, places, until, model, cues,
transition?, fadeIn?, fadeOut?}`; a cue `{at, until?, actions}`; an action
`{element, action, …fields}` or, for a project action, `{element, action,
params}`. `model` is `{from, to}` from `Loop.run(a, b)` or `{keys: [{at,
seconds, ease?}]}` from `Loop.keys({...})`, marks written `{"mark": name}`.

### D6. State across a chapter's shots

An element is one instance across its chapter's shots; the timeline carries
its state (the Node side). Python's part is static: a source panel's typing
cues in a shot, in cue order, must each type through a line of the excerpt
beyond where the previous one stopped, and a shot that places the panel must
complete the excerpt (the last typing reaches its last line) unless an
earlier shot of the chapter completed it; typing a completed panel again is
refused. A view needs nothing from Python: its camera continues from its last
move by the timeline's rule.

### D7. The stage block

`stage.sets` lists every set kind a shot uses and every project set those
derive from (so a `base` is always a kind in the table or a shipped kind);
`stage.elements` the project kinds any chapter declares; `stage.modules` the
distinct modules of both, relative to `root`, sorted. At evaluation each
module must exist as a file inside the project, the nearest directory above
the movie's file that holds a `pyproject.toml`; the check stats files and
opens none.

### D8. The top level

As the previous D9, with `format` `machinome-movie/0.2`, `style` from a
`Style(background, foreground, accent, font, safe_inset)` found on the movie
by type, `stage`, and chapters as D5. `marks` names must match
`[A-Za-z_][A-Za-z0-9_]*` (the schema's), refused at the loop's creation.

### D9. The document check

`check_document(document, manifest=None, sources=None)` validates the 0.2
schema, then the rules Python can check before speech: unique chapter and
shot ids; the stage block (module extensions, every set's and element's
module listed, shipped sets `frame` and `split` with exactly their slots, no
other set without a module, bases known, element kinds not shipped ones);
each chapter's elements (a known kind, the fields that kind takes, known
cameras, layers, excerpts and stills, a project element's props matching its
declared kinds); each shot (a known set, places on its slots and on declared
elements, no element in two slots, a literal `until` after the start, `fadeIn`
first and `fadeOut` last, marks known, model keys from 0 to the `until`,
phrases once in the narration); each cue (actions on placed elements, an
action the kind has with the fields it takes, spans with an `until`, eases,
entrances, cameras, parts and layers, typing and completion, emphasis
anchors, spoken parts and, given `sources`, tokens, a reveal's phrase). Given
the export's manifest, every part path is checked. Evaluation applies it to
its own output with the manifest and the excerpts it read. The invalid
fixtures run through it; the test reads their manifest and excerpt files
through their `root`, as the Node side does.

### D10. Schema and fixtures

The package ships `schema/machinome-movie-0.2.json` through a link, and the
0.1 file and link are removed. The fixture project's movies are rewritten:
`minimal` on `Frame`; `tour`, the Leonardo-shaped example on the seesaw, with
a project root set `Playbill` and its split `PlaybillSplit`, a project
element `Tally` with `light(item=str)`, the shipped `Frame` and `Split`, a
title with fades, a spoken reveal, a picture with keyed view, marks on the
view, emphasis pairs on two lines of the excerpt, a completed panel placed
again untyped, model keys on marks, and every join; `stage.tsx` beside it is a
placeholder whose path must exist. Documents, takes (0.06 s per character,
duration plus 0.1 s) and the revision are rewritten by the fixtures README's
recipes; `resolved/` is the Node cycle's.

## Spellings that differ from the film's source

- Chapter `drive`, shot `coupling`: `code.emphasize("waterwheel", "drives",
  "crankshaft")` cannot hold under D4 on lines 413–415 of the model, where
  `waterwheel`, `drives` and `crankshaft` are never whole tokens (they are
  segments of `water_drive.waterwheel.spin.drives` and the like). The film
  spells the pairs `("waterwheel drives", "water_drive.waterwheel.spin.drives"),
  ("crankshaft", "water_drive.crankshaft.spin")`, each once in the excerpt;
  recorded in `evidence.md` for the orchestrator to carry into the spec.
- Everything else in the source is the spelling this change implements.

## Risks / Trade-offs

- Reading the excerpt files makes evaluation depend on them; they are the
  project's own source, pinned by the revision, and only emphasised excerpts
  are read.
- Props' kinds come from use, not declaration: a prop no instance gives is
  not in the generated types. The film declares none that way.
- The stricter identifier reading refuses a token that is a segment of a
  dotted path; the refusal names the token and the excerpt, and a longer
  token is the remedy.

## Open Questions

None blocking. The contract findings in `evidence.md` are for the
orchestrator; the reading chosen for each keeps both runtimes able to agree.
