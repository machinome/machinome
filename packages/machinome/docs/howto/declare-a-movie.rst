# Declaring a movie in Python

A movie is declared in Python, in the project that owns the model, and
evaluated to the [movie document](movie-document.md), `machinome-movie/0.2`.
The declarations say what is on screen and when; the project's stage module,
a TypeScript or JavaScript file beside the movie, says how it looks. This
page teaches the declarations on a small example, a seesaw, whose complete
source is the test suite's fixture project. The declarations are provided by
the `machinome_movie` package in this repository's `python/` directory; its
status is Videomaker's, stated in the [README](../README.md). What the tool
does with the document, and whether it draws it yet, is stated on
[its page](movie-document.md); an episode can still be written as the YAML
screenplay of [the source contract](FORMAT.md).

## The shape of a movie

A movie is a tree of classes, written the way a machinome model is:

- a **`Movie`** orders **chapters** and declares the format, the narrator and
  the style;
- a **`Chapter`** owns its **`Narration`**, declares the **elements** its shots
  show, and orders its **`Shot`s**;
- a **`Shot`** places elements in the **slots** of one **set**, lasts until an
  **anchor**, and carries **cues**; a **`Cue`** makes elements perform
  **actions** at an anchor;
- a **set** is a layout, a template that owns the whole screen; an
  **element** is content: a view of the model, a source panel, a title, a
  picture, or anything the project draws;
- a **`Loop`** is the take the camera films: the model's posed loop, with its
  **marks**, **cameras**, **layers**, source excerpts and stills.

Nothing is found by its spelling. A chapter finds its narration, elements and
shots by their type, in the order they are written; a movie finds its
chapters the same way. The attribute that holds a declaration is its name:
`hook = Shot(...)` is the shot `hook`, `title_wide = Camera(...)` is the
camera `title-wide` (underscores become hyphens in the document).

## The take

Declare the take once, beside the model, and use it from any movie:

```python
class Playground(Loop):
    model = Seesaw
    export = "../export/seesaw"
    marks = {"rise": 5, "top": 10, "fall": 15}
    readiness = "Fixture export written by hand; nothing is simulated."
    far = Camera(position=(400, -600, 300), target=(0, 0, 50), fov=37)
    near = Camera(position=(200, -300, 150), target=(0, 0, 50), fov=37)
    rolled = Camera(position=(-150, 250, 120), target=(0, 0, 60), up=(0.15, 0, 1), fov=42)
    ground = Layer(Seesaw.base)
    load = Layer(Seesaw.beam.plank, Seesaw.beam.weight)
    declaration = Source("../models/seesaw.py", lines=(22, 24))
```

- `model` is the model's node class and `export` the directory of its export,
  relative to this file. Every path a declaration writes is relative to the
  file it is written in.
- `marks` name instants of the loop in model seconds, each named with
  letters, digits and underscores; `readiness` says what the export does and
  does not show.
- A `Camera`'s `up` is `(0, 0, 1)` unless written.
- A part is named by the model's own declarations: `Seesaw.beam.plank` is the
  child `plank` of the child `beam`. It is checked where it is written, so a
  misspelling fails at that line, and it is resolved to the names the export
  gives the parts when the movie is evaluated.

## The template: sets

A set is a template that owns the whole screen. The project writes its own,
declared in Python and drawn by its stage module:

```python
class Playbill(Set):
    module = "stage.tsx"
    series = "VIDEOMAKER · FIXTURES"
    stage = Slot()
    plate = Slot()
    headline = Slot()
    aside = Slot()


class PlaybillSplit(Playbill):
    left = Slot()
    right = Slot()
    headline = Slot()
```

- `module` is the stage module that draws the set, a `.ts`, `.tsx`, `.js` or
  `.jsx` file relative to this file and inside the project.
- Each `Slot()` is a named place that holds one element. A set does not know
  what it holds: any element can go in any slot.
- The other plain class attributes are the set's static props, which its
  component receives: `series` here. A prop is JSON: text, a number, `True`
  or `False`, `None`, or a list or dict of them.
- The set's kind is its class name as a slug: `Playbill` is `playbill` and
  `PlaybillSplit` is `playbill-split`. Write `kind = "…"` to choose another.
- A derived set inherits its base's chrome and module, not its layout: the
  slots of `PlaybillSplit` are the three its own body declares, so
  `PlaybillSplit.stage` is not a slot. The document names its base.

The tool ships two sets: `Frame`, whose one slot `stage` is the whole
picture, with no chrome; and `Split`, with `left` and `right`. A shot may
leave any slot empty.

## Elements the project writes

An element is content with state. The project declares its own the same way:

```python
class Tally(Element):
    module = "stage.tsx"
    light = Action(item=str)
```

- `module` is the stage module that draws it; its kind is its class name as
  a slug, `tally`.
- Each `Action(...)` is something the element does on cue, with typed
  parameters: `str`, `int`, `float` or `bool`.
- An instance's keyword arguments are its props, JSON values:
  `Tally(items=["Balance", "Tip"])`. Every instance of a kind in a movie gives
  the same props, of the same kinds, because the stage generates the
  component's types from them.
- Calling a declared action, `card.light(item="Balance")`, makes the action
  of a cue; its parameters are checked by name and type where it is written.

## A chapter

```python
class Opening(Chapter):
    lines = Narration("A seesaw balances a beam on a stand. How does the weight tip it?")
    wide = View(Playground, camera=Playground.far)
    card = Tally(items=["Balance", "Tip"])
    title = Title("SEESAW", subtitle="One beam, one stand")
    hook = Shot(Playbill, {Playbill.stage: wide, Playbill.aside: card}, until=lines.spoken("How"),
                fade_in=FadeIn(1.0), model=Playground.run(0, 4),
                cues=[Cue(0, wide.move(Playground.near, ease="out", until=lines.spoken("How"))),
                      Cue(lines.spoken("balances"), card.light(item="Balance"), until=lines.spoken("How"))])
    question = Shot(Playbill, {Playbill.stage: wide, Playbill.aside: card, Playbill.headline: title},
                    until=lines.end(plus=0.8), model=Playground.run(4, 8),
                    cues=[Cue(lines.spoken("tip it"), card.light(item="Tip"), until=lines.end(plus=0.8)),
                          Cue(0, title.show(enter=0.6, leave=0.6), until=lines.end())])
```

- The **narration** belongs to the chapter and is spoken as one take. Its
  phrases are the anchors shots cut on: `lines.spoken("How")` is the instant
  the narrator begins "How", `lines.spoken_end(phrase)` the instant a phrase
  ends, `lines.end()` the end of the whole narration, and each takes
  `plus=` seconds. A phrase must occur exactly once in the narration. A plain
  number is seconds from the shot's start.
- **Elements** are declared on the chapter and placed by its shots,
  `{Playbill.stage: wide, Playbill.aside: card}`. An element is one instance
  across the chapter's shots: `hook` moves `wide` to `near`, so `question`
  starts there.
- A **shot** names its set, places elements in that set's own slots, lasts
  `until` an anchor, and gives the model's time, `Playground.run(start, end)`.
- A **cue** makes placed elements act at an anchor, optionally `until`
  another. A move runs from its cue's anchor to its own `until`; an action
  that shows something (a highlight, a mark, a title, a picture, a project
  action) shows it for the cue's span and needs the cue's `until`.
- `Title(text, subtitle=)` is an element placed in a slot;
  `show(enter=, leave=)` shows it with fades of that many seconds.

## Source beside the model

```python
    mill = View(Playground, camera=Playground.side, hide=[Playground.ground])
    code = Source.panel(Playground.declaration)
    source = Shot(PlaybillSplit, {PlaybillSplit.left: code, PlaybillSplit.right: mill},
                  until=lines.spoken("The weight"), transition=Dissolve(0.6),
                  model=Playground.run(10, 12),
                  cues=[Cue(0, code.type(through_line=24, over=0.8)),
                        Cue(lines.spoken("the stand holds"), mill.highlight(Seesaw.stand, others="ghost"),
                            until=lines.spoken("the beam")),
                        Cue(lines.spoken("the beam"), mill.highlight(Seesaw.beam, others="ghost"),
                            until=lines.spoken("The weight")),
                        Cue(lines.spoken("the stand holds the beam"),
                            code.emphasize(("stand", "Stand"), "beam", hold=0.6))])
    push = Shot(Split, {Split.left: code, Split.right: mill}, until=lines.end(plus=0.6),
```

- `Source.panel(excerpt)` shows a source excerpt the take declares.
  `type(through_line=, over=)` types from where the typing stopped through
  that line, in `over` seconds from the cue's anchor. A shot that places the
  panel types it through its last line, unless an earlier shot of the
  chapter did: `push` places the completed panel again and types nothing.
- `emphasize(*words, hold=)` lights tokens of the excerpt as the narrator
  speaks their words in the cue's phrase, and holds them `hold` seconds after
  it. A word is a token spoken as it is spelled, `"beam"`, or a pair of the
  spoken words and the token they light, `("stand", "Stand")`, on any line of
  the excerpt. The cue's anchor is a spoken phrase with no `plus`; each
  spoken part occurs exactly once in it, as whole words; each token occurs
  exactly once in the excerpt, as a whole identifier, dots included, so
  `feed.pawl.turn` is one token and `pawl` does not occur in it.
- `hide=` on a view names the take's layers; `highlight(*parts, others=)`
  tints parts and keeps, dims or ghosts the rest.
- One anchor can drive two elements: the source and the model light together.

## Marks on the view and model time on marks

```python
                model=Playground.keys({0: "rise", lines.spoken("On the way down"): ("top", "out"),
                                       lines.spoken("Up."): "fall"}),
                cues=[Cue(0, heading.show(enter=0.4), until=lines.spoken("Up.")),
                      Cue(lines.spoken("the plank"),
                          close.ring(Seesaw.beam.plank, enter=("draw", 0.8), leave=("fade", 0.4)),
                          close.label(Seesaw.beam.plank, "Plank", offset=(0.12, -0.08),
                                      enter=("fade", 0.4), leave=("fade", 0.4)),
                          close.highlight(Seesaw.beam.plank, Seesaw.beam.weight, others="ghost"),
                          until=lines.spoken("On the way down")),
```

`keys` pins marks of the take to anchors of the shot: the first key at `0`,
the last at the shot's `until`, and an easing name on a key shapes the
segment that ends there. The easings are `linear`, `smooth`, `in`, `out` and
`in-out`.

The marks belong to the view they point into: `ring(part)`, `label(part,
text, offset=)` and `arrow(part, text, place=)`. An offset or a place is a
fraction of the view's own box, wherever the set puts it. An entrance or exit
is a number, a fade of that many seconds, or `(kind, duration)` with an
optional easing third: `draw` or `fade` in on a ring or an arrow, `fade`
otherwise.

## Titles, pictures and joins

```python
    beat = Title("Up. Down.")
    plate = Picture(Playground.plate, fit="contain")
                  cues=[Cue(0, close.move(Playground.rolled, ease="smooth", until=lines.spoken("Explore"))),
                        Cue(0, beat.show(reveal=Reveal.spoken()), until=lines.spoken("Explore"))])
                 cues=[Cue(0, plate.show(enter=0.5, leave=0.5,
                                         view=[(0, (0.5, 0.5), 1.0),
                                               (lines.spoken("the model", plus=-0.2), (0.5, 0.42), 1.4,
                                                "in-out")]),
```

- `show(reveal=Reveal.spoken())` shows each word of a title as the narrator
  speaks it; the title's text is then a phrase of the narration.
- `Picture(still, fit=)` places a still the take declares, fit `contain` or
  `cover`; `show(enter=, leave=, view=)` shows it, each view key `(at,
  center, zoom)` with an optional easing, `at` a time or an anchor.
- A shot comes in with `transition=Dissolve(d)`, `Fade(d)`, `Wipe(d,
  direction=)` or `Slide(d, direction=)`; the film's first shot may
  `fade_in=FadeIn(d)` and its last `fade_out=FadeOut(d)`.

## The movie

```python
class Tour(Movie):
    title = "Tour"
    series = "VIDEOMAKER · FIXTURES"
    status = "rehearsal"
    learning_goal = "Exercise every construct the validation film uses."
    format = Format(1280, 720, fps=30)
    narrator = fixture_voice
    style = Style(background="#faf7ef", foreground="#222222", accent="#237c86",
                  font="DejaVu Sans, sans-serif", safe_inset=0.08)
    evidence = Evidence(model="../../models/seesaw.py")
    credits = Credits(project="Videomaker fixtures", creator="The Videomaker test suite",
                      copyright="No copyright is claimed for this fixture",
                      license="None", license_file="../../NOTICE")
    release = Release(simulation_url=None, source_url=None, description="description.md")
    opening = Opening()
    balance = Balance()
    tip = Tip()
```

`title`, `status` and `learning_goal` are required, `series` is optional.
The movie needs one `Format` and one `Narrator`; the `Style` (the palette and
type the root set reads), evidence, credits and release are optional.
Credits are recorded for the upload description and never drawn in the film.
A `None` address in the release is unresolved and blocks a release; it is
never replaced by an invented one. Chapters are instances, so one chapter can
be used by several movies.

## Declaring and evaluating

A project lists its movies in `pyproject.toml`, beside its models:

    [tool.machinome.movies]
    minimal = "videos.minimal.movie:Minimal"
    tour = "videos.tour.movie:Tour"

With the workspace's Python environment:

    python -m machinome_movie list <project-dir>
    python -m machinome_movie evaluate <project-dir> tour
    python -m machinome_movie evaluate <project-dir> tour --out other/place.json

`evaluate` imports the movie from the project and writes
`_build/movie.json` beside the movie's module, or the `--out` file. It opens
only the export's manifest and source revision and the source files of the
excerpts an emphasis lights, and checks that each stage module exists: no
clock, no randomness, no network, and no CAD is built, so two evaluations
write the same bytes. The anchors stay phrases and marks; the tool measures
them in the recorded speech.

The document's `stage` block lists what the stage bundles: the stage
modules, every set a shot uses (with the project sets they derive from),
and the project's element kinds with the kinds of their props and of their
actions' parameters.

## What is refused

Every refusal names where it is: the movie or chapter, the shot, and the
thing at fault. When the class is created:

- a set without a stage module, a slot that says what it holds, a prop that
  is not JSON, a project kind that is one the tool ships;
- an element without a stage module, a plain attribute on an element, an
  action parameter of another type, a prop that is not JSON or is `None`, and
  an action called with a parameter missing, unknown or of the wrong type;
- a slot the shot's set does not declare, a slot filled twice, an element the
  chapter does not declare, an element in two slots of one shot;
- a phrase absent from the chapter's narration or occurring more than once,
  and an anchor made from another chapter's narration;
- an unknown mark, and model keys that do not start at `0` and end at the
  shot's `until`;
- a camera or a layer not declared on the view's take;
- an action on an element the shot does not place, and an action that shows
  something without the cue's `until`;
- an emphasis whose cue is not anchored on a spoken phrase without `plus`, a
  spoken word absent from or repeated in that phrase, a panel typed outside
  its excerpt, backwards or again once complete, and a placed panel no shot
  of the chapter completes;
- a spoken reveal whose title the narration does not say exactly once;
- a movie without a format, a narrator or a chapter, a shot id used twice,
  and elements of one kind whose props disagree.

When the movie is evaluated: a part the export does not contain (the export is
older than the model), a token absent from or repeated in its excerpt, a stage
module that does not exist or lies outside the project, an export that is not
a posed loop, and a movie that films more than one take.
