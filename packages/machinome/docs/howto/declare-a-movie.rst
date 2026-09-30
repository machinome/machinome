# Declaring a movie in Python

A movie can be declared in Python, in the project that owns the model, and
evaluated to the [movie document](movie-document.md). This page teaches the
declarations on a small example, a seesaw, whose complete source is the test
suite's fixture project. The declarations are provided by the
`machinome_movie` package in this repository's `python/` directory; its
status is Videomaker's, stated in the [README](../README.md). Whether the
renderer reads the movie document yet is stated on
[its page](movie-document.md); until it does, an episode is written as the
YAML screenplay of [the source contract](FORMAT.md).

## The shape of a movie

A movie is a tree of classes, written the way a machinome model is:

- a **`Movie`** orders **chapters** and declares the format and the narrator;
- a **`Chapter`** owns its **`Narration`**, declares the **elements** its shots
  show, and orders its **`Shot`s**;
- a **`Shot`** puts elements in the **slots** of one **set**, lasts until an
  **anchor**, and carries **cues**;
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
- `marks` name instants of the loop in model seconds; `readiness` says what
  the export does and does not show.
- A `Camera`'s `up` is `(0, 0, 1)` unless written.
- A part is named by the model's own declarations: `Seesaw.beam.plank` is the
  child `plank` of the child `beam`. It is checked where it is written, so a
  misspelling fails at that line, and it is resolved to the names the export
  gives the parts when the movie is evaluated.

## A chapter

```python
class Opening(Chapter):
    lines = Narration("A seesaw balances a beam on a stand. How does the weight tip it?")
    wide = View(Playground, camera=Playground.far)
    hook = Shot(Paper, {Paper.stage: wide}, until=lines.spoken("How"), fade_in=FadeIn(1.0),
                model=Playground.run(0, 4),
                cues=[Cue(0, wide.move(Playground.near, ease="out", until=lines.spoken("How")))])
    question = Shot(Paper, {Paper.stage: wide}, until=lines.end(plus=0.8),
                    model=Playground.run(4, 8),
                    cues=[Cue(0, Title("SEESAW", subtitle="One beam, one stand",
                                       enter=0.6, leave=0.6), until=lines.end())])
```

- The **narration** belongs to the chapter and is spoken as one take. Its
  phrases are the anchors shots cut on: `lines.spoken("How")` is the instant
  the narrator begins "How", `lines.spoken_end(phrase)` the instant a phrase
  ends, `lines.end()` the end of the whole narration, and each takes
  `plus=` seconds. A phrase must occur exactly once in the narration. A plain
  number is seconds from the shot's start.
- **Elements** are declared on the chapter and placed by the shots. `wide` is
  a `View`: a camera on the take. Its camera carries over from shot to shot:
  `hook` moves it to `near`, so `question` starts there.
- A **shot** names its set and places elements in that set's slots,
  `{Paper.stage: wide}`. It lasts `until` an anchor, and its model time is
  `Playground.run(start, end)`.
- A **cue** does its actions at an anchor, optionally `until` another. A
  move runs from its cue's anchor to its own `until`; a title, a highlight, an
  annotation or a picture shows for the cue's span and needs the cue's
  `until`.

## Sets

There are three sets, the layouts the film page draws:

- `Paper`, with the slot `stage`, holding a view;
- `PaperSplit`, with `left`, holding a source panel, and `right`, holding a view;
- `SourceOnly`, with `source`, holding a source panel. A source-only shot is
  still posed: it poses the chapter's view, so its chapter declares one.

A set's slots are those its own class declares, so `PaperSplit.stage` is not
a slot. A project cannot yet declare a set or an element of its own; the
stage that would draw it does not exist.

## Source beside the model

```python
    mill = View(Playground, camera=Playground.side, hide=[Playground.ground])
    code = Source.panel(Playground.declaration)
    source = Shot(PaperSplit, {PaperSplit.left: code, PaperSplit.right: mill},
                  until=lines.spoken("The weight"), transition=Dissolve(0.6),
                  model=Playground.run(10, 12),
                  cues=[Cue(0, code.type(through_line=24, over=1.2)),
                        Cue(lines.spoken("beam"), mill.highlight(Seesaw.beam, others="ghost"),
                            until=lines.spoken("pivot")),
                        Cue(lines.spoken("pivot"), mill.highlight(Seesaw.beam.pivot, others="ghost"),
                            until=lines.spoken("The weight")),
                        Cue(lines.spoken("the beam rests on its pivot"),
                            code.emphasize("beam"))])
```

- `Source.panel(excerpt)` shows a source excerpt the take declares. A shot
  that places it types it: `type(through_line=, over=)` types through that
  line in `over` seconds from the cue's anchor.
- `emphasize(*words, hold=)` lights words of the excerpt's last line as the
  narrator speaks them in the cue's phrase, so its cue's anchor is a spoken
  phrase, with no `plus`.
- `hide=` on a view names the take's layers; `highlight(*parts, others=)`
  tints parts and keeps, dims or ghosts the rest.
- One anchor can drive two elements: the source and the model light together.

## Model time on marks

```python
                model=Playground.keys({0: "rise", lines.spoken("On the way down"): ("top", "out"),
                                       lines.spoken("Up."): "fall"}),
```

`keys` pins marks of the take to anchors of the shot: the first key at `0`,
the last at the shot's `until`, and an easing name on a key shapes the
segment that ends there. The easings are `linear`, `smooth`, `in`, `out` and
`in-out`.

## Marks on the picture

```python
                      Cue(lines.spoken("the plank"),
                          Ring(Seesaw.beam.plank, enter=("draw", 0.8), leave=("fade", 0.4)),
                          Label(Seesaw.beam.plank, "Plank", offset=(0.12, -0.08),
                                enter=("fade", 0.4), leave=("fade", 0.4)),
                          close.highlight(Seesaw.beam.plank, Seesaw.beam.weight, others="ghost"),
                          until=lines.spoken("On the way down")),
```

`Ring`, `Label` and `Arrow(part, text, place=)` point at parts and follow
them. An entrance or exit is a number, a fade of that many seconds, or
`(kind, duration)` with an optional easing third: `draw` or `fade` in, `fade`
out. `Title(text, position=)` writes on the frame at `title`, `top`,
`lower-third` or `center`; only a title takes a `subtitle`, `enter` and
`leave`, and `reveal=Reveal.spoken()` shows each word as it is spoken.

## Pictures and joins

```python
                 cues=[Cue(0, Playground.plate.show(area="frame", fit="contain", enter=0.5, leave=0.5,
                                                    view=[(0, (0.5, 0.5), 1.0),
                                                          (lines.spoken("the model", plus=-0.2),
                                                           (0.5, 0.42), 1.4, "in-out")]),
                           until=lines.spoken("the model"))])
```

A `Still` the take declares is shown with `show(area=, fit=, enter=, leave=,
view=)`; each view key is `(at, center, zoom)` with an optional easing, and
`at` may be an anchor. A shot comes in with `transition=Dissolve(d)`,
`Fade(d)`, `Wipe(d, direction=)` or `Slide(d, direction=)`; the film's first
shot may `fade_in=FadeIn(d)` and its last `fade_out=FadeOut(d)`.

## The movie

```python
class Tour(Movie):
    title = "Tour"
    series = "VIDEOMAKER · FIXTURES"
    status = "rehearsal"
    learning_goal = "Exercise every construct the validation film uses."
    format = Format(1280, 720, fps=30)
    narrator = fixture_voice
    style = Paper.style(background="#faf7ef", foreground="#222222", accent="#237c86",
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
The movie needs one `Format` and one `Narrator`; the style, evidence, credits
and release are optional. Credits are recorded for the upload description and
never drawn in the film. A `None` address in the release is unresolved and
blocks a release; it is never replaced by an invented one. Chapters are
instances, so one chapter can be used by several movies.

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
`_build/movie.json` beside the movie's module, or the `--out` file. It reads
only the export's manifest and source revision: no clock, no randomness, no
network, and no CAD is built, so two evaluations write the same bytes. The
anchors stay phrases and marks; the renderer measures them in the recorded
speech.

## What is refused

Every refusal names where it is: the movie or chapter, the shot, the field
and the thing at fault. When the chapter or movie class is created:

- a slot the shot's set does not have, a slot filled twice or left empty, and
  an element of the wrong kind in a slot;
- an element the chapter does not declare, and a cue acting on an element
  the shot does not place;
- a phrase absent from the chapter's narration or occurring more than once,
  and an anchor made from another chapter's narration;
- an unknown mark, and model keys that do not start at `0` and end at the
  shot's `until`;
- a camera or a layer not declared on the view's take;
- an `emphasize` whose cue is not anchored on a spoken phrase, a span with no
  `until`, a placed source panel no cue types, a shot with no model time;
- a project's own set or element;
- a movie without a format, a narrator or a chapter, and a shot id used twice.

When the movie is evaluated: a part the export does not contain (the export is
older than the model), an export that is not a posed loop, and a movie that
films more than one take.
