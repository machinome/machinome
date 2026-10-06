# Declarative Python movies — a working note

Status: provisional, 30 September 2026. A design note written from a
conversation with the pilot, recording a direction the pilot settled and the
decisions taken in it. Nothing here is ratified, no OpenSpec change has been
cut from it, and no schedule is implied. The YAML formats 0.2, 0.3 and 0.4
remain the only implemented source, and `AGENTS.md`, `README.md` and
`docs/FORMAT.md` remain the authority over how an episode is written today.
Every name below is provisional; naming is the next conversation, not this
one. Where this note and a baseline spec disagree, the spec is right.

Revision note, 4 October 2026: step 5 of "Path from today" is built on
the Videomaker side as the player (`videomaker live`, the take transport
and the live server; `workflow/archive/player-2026-10-04/report.md`),
by the pilot's ruling that the viewer stays thin and the take transport
lives in Videomaker until the migration into the planned monorepo. The
studio mounting that page remains future studio work. Steps 4 and 6 are
unchanged.

## What it does not claim

- That the framework, the viewer or the studio have agreed to any of the
  requirements listed under "What it asks of the other repositories".
- That the current YAML episodes are to be rewritten. They keep loading
  until a change says otherwise.
- That the React stage, the take, the browser element or the studio preview
  exist. They do not.

## Where it comes from

The direction was reached by assessing the tool after the two September
campaigns, against the eight Leonardo episodes. Four findings, all in the
repository:

1. **Timing is hand arithmetic.** A shot carries absolute `start` and `end`
   that must be contiguous; model keyframes repeat the shot's duration and
   the simulation's endpoints; overlays use shot-local seconds. Lengthening
   one shot means editing numbers in several places, and `timeline.mjs`
   carries epsilon comparisons everywhere because seconds are floats.
2. **Speech measurements are hand-copied.** *Revolutions* has camera keys at
   5.727 and 9.821, overlays at 2.941 and 3.273 and a model keyframe at
   5.366, each read from the cached alignment and typed into YAML. Only word
   reveals and source emphasis can say "at this spoken phrase"; a camera key
   or a model keyframe cannot.
3. **Every real film grew code beside its YAML.** The release film has a
   170-line score and final-mix script (`finish.mjs`); its second direction
   has a 243-line rehearsal renderer with a private format
   (`rehearse.mjs`, `machinome-visual-experiment/revolutions-opening`); the
   pronunciation and one-take work has a 112-line adapter
   (`prepare-audio.mjs`); the syntax study has a third private format
   (`visual.yaml`, `machinome-visual-experiment/dark-source`) with its own
   renderer under `experiments/dark-source/`. The no-code rule held for the
   episode file and the code moved next door, each time with an ad-hoc
   schema. These scripts were escapes from missing features, a music bed, a
   continuous take with a pronunciation dictionary, a layout the format
   lacked, not from YAML as such; a screenplay language does not remove
   them, tool features do.
4. **Every new look is a format change.** Format 0.4 closed every field list;
   the validator in `episode.mjs` is some 380 lines of set membership; the
   film page (`film.html`, 62 lines, and `film.js`, 288 lines) is one fixed
   layout with a fixed inventory of elements. `roadmap.md` states the cost
   plainly under "Design constraint to keep".

The pilot's direction, stated on 30 September 2026, added the requirements
the findings alone would not have produced:

- The video is one output of a model, declared in `pyproject.toml` as a
  top-level artifact like the models, and live preview belongs in the
  studio, not in a contact sheet.
- Running and clocked machines must become filmable, through the
  simulation's scenarios (`machinome.simulation.scenario`). Today the tool
  refuses anything but a posed normalized loop.
- A film has pictures that are not machinome at all: a browser navigating
  the museum's page, in the Leonardo film.
- The picture is controlled in full from React, as the framework's 0.8 view
  layer is (`machinome/workflow/ongoing/roadmap-0.8.md`), and a set is a
  layout that places elements on the screen, never a type of content.
- The whole thing is declarative, a Python tree like a machinome model, and
  its chapters and shots are reusable between films.

## Options considered

- **Keep YAML and add derived timing** (durations instead of absolute ends,
  speech anchors on every cue, named cue presets, a JSON Schema). Fixes
  findings 1 and 2 and nothing else; leaves the scripts and the fixed page.
- **A hermetic configuration language** evaluating once to data, Starlark or
  Jsonnet. Pure by construction, readable, and checked against Node on
  30 September 2026: Jsonnet has a maintained Node addon, Starlark has no
  usable npm implementation and would need the Go interpreter. Rejected
  when the direction above arrived: Starlark reuses Python's syntax but is
  its own language and cannot import a Python scenario, so it would have
  been a third language between the Python scenario and the React stage,
  with a data boundary on each side and nothing to show for it.
- **Python declarations in the project, evaluated once to a document.** The
  chosen direction. The hermeticity argument that motivated the old no-code
  rule dissolves once the movie is a project artifact: a project's Python
  already runs at every build. Reproducibility comes, as it does for the
  export, from hashing the evaluated document, the takes and the stage
  bundle, not from forbidding code in the source.

## The rule

**Python says what and when; React says how it looks.** The Python
declarations hold every word a reader reads and every number provenance
hashes. The React stage holds pixels. Nothing crosses back: a component
never invents timing, and Python never emits markup. Between them is one
contract, the **movie document**: for every frame, the set, the element in
each of its slots, and each element's state. It is what the stage renders,
the studio scrubs, the renderer encodes and the shot cache hashes. This is
today's `frameAt` output made explicit and made the boundary.

## Vocabulary

The rename first. **Scenario** stays with the simulation, where
`ScenarioTest` already gives it a ratified meaning. The video side drops
**scene** entirely and calls the grouping a **chapter**: the word viewers
know from timelines, and a movie's chapter marks fall out of it for free.

- **Movie**: the work, declared in `pyproject.toml` like a model. Ordered
  chapters, one format, one narrator.
- **Chapter**: an ordered part of the movie that owns its narration and
  declares the elements its shots place.
- **Shot**: one continuous composition: one set, elements placed in its
  slots, a span of time, cues, and how it comes in.
- **Set**: a layout. A React component with named slots and its own chrome,
  declared in Python as a class with `Slot` declarations. Sets inherit: the
  root set decides the logo, palette and type, and every set a movie uses
  derives from it. Whether the film carries a logo is a root-set fact.
- **Slot**: a named place on a set that holds one element.
- **Element**: content. A React component with a Python declaration: a view
  onto a take through a camera, a source panel, a picture, a card, or
  anything a project writes. An element declares the **actions** it can
  perform and what in it can be addressed, a part or a token.
- **Take**: one recorded run of a scenario, with marks. It belongs to the
  simulation; the movie only reads it. The posed loop is the trivial take.
- **Mark**: a named instant in a take, set by the scenario.
- **Narration**: a chapter's lines. A phrase of them is an anchor. Its
  recording is a speech take.
- **Anchor**: a named instant that resolves to video time: a phrase, a
  mark, or seconds into the shot.
- **Cue**: at an anchor, do these actions, optionally until another anchor.
  The cue is the only thing that synchronizes elements.
- **Action**: what an element does on cue: highlight a part, emphasize a
  token, move to a camera, zoom, retime, or an action a custom element
  declares.
- **Camera**: a setup on a model, declared with the model's view layer and
  reusable by any movie; a view element holds one and moves between them.
- **Format**, **Narrator**: output geometry and rate; voice, provider,
  pronunciation and delivery. Declared once, shared by a series.

## The tree

    Movie
    ├── Format, Narrator
    └── Chapter                     owns Narration; declares Elements; orders Shots
        ├── Narration               lines; phrases are anchors
        ├── Element                 content, declared once, placed by many shots
        │   View(take, camera)      a camera on a take; two Views may share one take
        │   Source(file, lines)     a pinned excerpt
        │   Picture, Card, ...
        │   <project element>       any React component with a Python declaration
        └── Shot                    a Set, placements into its Slots, span, Cues, Transition
            └── Cue(anchor, actions..., until=)

    Set                             layout; inherits; the root set carries the chrome
    └── Slot
    Scenario ─ Take ─ Mark          simulation side; the movie only reads them
    Camera                          a setup on a model, declared with its view layer

Three rules keep it flexible without being loose:

1. **Nothing is found by spelling.** A chapter finds its narration, elements
   and shots by type in declaration order, as an assembly finds its
   drivers. A shot places elements into slots by declaration reference,
   `Split.left`, never by string. Slot names, element names and chapter
   names are the author's, and follow the node tree's naming rule: an
   attribute's name is the declaration's name, a list gives indexed names.
   Chapters and shots are declared as attributes, so a movie class reads as
   its own table of contents and the names become the ids caches, review
   packs and refusals already rely on.
2. **One video clock per shot, one take clock per take.** A view maps video
   time onto its take's time from the mark it starts at. Two views of the
   same take see the same instant from two cameras. A second, independently
   timed view of the same scenario is a second take. Retiming is an action,
   so slow motion or a seek is a cue like any other. Time is never typed as
   an absolute: a shot has a duration, or runs from a mark to a mark, or
   until a phrase, and starts are computed by order. Internally the unit is
   the frame, an integer.
3. **The element is the extension point.** A project adds a custom
   animation by declaring an `Element` subclass with its actions in Python
   and writing its component in React. The set does not know or care what
   it holds. The Python declaration is the type; the tool generates the
   TypeScript type of the component's props from it; the component
   registers under the kind the class publishes; a mismatch fails the build.

## A sketch

Names provisional; the shape is what is being recorded.

```python
class Paper(Set):                      # root: logo bug, series label, palette, progress rule
    stage = Slot()

class PaperSplit(Paper):               # inherits the chrome, adds a layout
    left = Slot()
    right = Slot()

drive = Camera(position=(330, -630, 300), target=(0, -135, 145), fov=37)   # beside the model's view layer

class Coupling(Chapter):
    lines = Narration("""A waterwheel. A saw. A carriage. Here, the waterwheel
        drives the crankshaft.""")

    wheel = View(Sawmill.full_pass, camera=drive)            # a take, one camera
    crank = View(Sawmill.full_pass, camera=crank_close)      # same take, second camera
    code  = Source(model_py, lines=(366, 376))

    machine = Shot(Paper, {Paper.stage: wheel},
                   until=lines.spoken("Here"))
    both = Shot(PaperSplit, {PaperSplit.left: crank, PaperSplit.right: code},
                until=lines.end(tail=0.8), transition=Dissolve(0.6),
                cues=[Cue(lines.spoken("waterwheel"),
                          crank.highlight(HydraulicSawmill.waterwheel),
                          code.emphasize("waterwheel")),
                      Cue(lines.spoken("crankshaft"),
                          crank.highlight(HydraulicSawmill.crankshaft),
                          code.emphasize("crankshaft"),
                          until=lines.end())])

class ForceArrows(Element):            # a project's own element; React component of the same name
    scale = Number(1.0)
    push = Action(magnitude=Number)

class Revolutions(Movie):
    format = Landscape
    narrator = Jessica
    coupling = Coupling()
```

The synchronization the pilot asked for is the second cue: one anchor, two
actions, two elements. Nothing in `Source` knows about `View`, and the shot
needed no type for that pairing. A set with two slots both holding views of
one take is two cameras on one scenario, which the fixed film page cannot
show today (roadmap item 4).

## Decisions taken

Accepted by the pilot on 30 September 2026:

- **Narration belongs to the chapter**, as lines, and shots cut on its
  phrases. Today narration is per shot. The second *Revolutions* rehearsal
  found that one continuous take reads better than a take per shot, and
  phrases are the anchors that remove the hand-copied decimals.
- **Elements are declared on the chapter, not inside the shot**, so
  consecutive shots can keep the same view and its take keeps running
  through the cut. Continuity of model time across a cut is a real gap in
  the current format, where each shot maps its own `from` and `to`.
- **A camera change inside a shot is a move action on the view; a camera
  change at a cut is a different view.** One mechanism for both.
- **The look lives in the root set.** There is no separate look
  declaration. Format and narrator stay on the movie because they are not
  layout.
- **A shot is on exactly one set.** A cutaway to the museum page is a new
  shot in the same chapter.
- **Takes are the only way a running or clocked machine appears**, and the
  posed loop is the trivial take.
- **Chapter replaces scene; scenario stays the simulation's word.**
- **A movie evaluates to a data document**, as an episode does today, and
  every guarantee built on that document is kept: validation before a
  browser opens, the shot cache, the pixel proofs, the review packs and the
  provenance manifest. The stage's flexibility costs none of them.

## Anchors and their resolution

Anchors stay symbolic in the movie document and are resolved against the
takes by the renderer and the preview, which is how word reveals and source
emphasis already work. Evaluation of the Python checks that a mark exists in
the scenario and that a phrase occurs once in the narration; the renderer
fills in the seconds. This avoids the ordering trap: speech needs the
narration before anyone can know when a word is spoken, and a browser take
needs its session recorded before its marks have times.

## Elements the tool ships, and the page take

- `View`, `Source`, `Picture`, `Card`, `Title` and the marks a `View`
  exposes (highlight, label, arrow, ring, move, retime) are today's film
  page cut into elements: `Paper` is its layout, and the three current
  presentations, model, split and source-only, are three sets deriving
  from it.
- `Page` shows a web page. Its take is a short Playwright session script in
  the project that navigates the page and emits marks. The session runs once
  against the live site with recording on, which writes a HAR archive; every
  later run replays from the archive with unrecorded requests aborted, so
  the page is served from the archive and looks the same on every render,
  and frames are captured at the film's rate. Verified on 30 September 2026
  against Playwright's documentation: `routeFromHAR` with its update mode
  and `notFound: 'abort'`. A live iframe was rejected: cross-origin,
  unrepeatable, and impossible to scrub. Filming another's page is a rights
  question and goes where credits go today, into the description, by the
  pilot's decision.

Components accept four constraints or the proofs stop meaning anything:
pure in time, no wall clock, no asynchronous state, and they report their
measurements back for the checks. The machinome viewer mounts once outside
React's reconciliation, as the film page does now.

## What it asks of the other repositories

None of this is agreed there; each is a requirement to be born from the
first episode that needs it, through that repository's own process.

- **Framework.** A movie as a top-level artifact in `pyproject.toml`; the
  `Movie`, `Chapter`, `Shot`, `Set`, `Slot`, `Element`, `Cue`, `Action`,
  `Narration`, `Camera`, `Format` and `Narrator` declarations, in whichever
  package the pilot decides; a **take** as a build output: a scenario's
  request stream with tick times, its marks, the events the run produced
  (commits, crossings, stops), the program identity and `dt`; a way for a
  scenario to name a mark. The 0.8 view layer already places scripted
  actions in the project.
- **Viewer.** Posing a running or clocked machine at a frame by replaying a
  take up to that frame's tick. The pieces exist: `reset`, `snapshot`,
  `restore`, `move`, `trigger` on the clocked handle, `step` on the running
  handle; `setTime` stays for posed models, since it neither advances a
  program nor seeks a clocked bank. The hard requirement is **parity**: the
  viewer's engine and the Python `Sim` must land on the same bank at the
  same tick for the same program. The framework already publishes a program
  identity for that reason; a take can record the bank at its marks and the
  stage can check the viewer's bank against them, the discipline the
  renderer applies to camera readback today.
- **Studio.** Mount the stage with a scrubber over the movie document and
  re-evaluate on change, as the floor already rebuilds models. This is
  roadmap item 13 and the pilot's stated home for it.
- **Licence.** The stage binds to the AGPL viewer, so it and a project's
  elements carry AGPL; `roadmap-0.8.md` already holds the open line that the
  Foundry licensing policy needs for project views, and movies fall under
  it. The Python declarations belong with the framework under its licence,
  GPL-2.0-or-later OR CERN-OHL-S-2.0-or-later.

## Left out on purpose

Several formats from one movie and per-format reframing (roadmap item 15);
music and sound design (item 10); live embedding of a web page. Each has a
place in the tree when an episode asks for it.

## Path from today

Each step leaves a working tool behind it; the Leonardo film is the evidence
for steps 3 and 4.

1. Make the movie document the seam between declarations and renderer for
   this step. It is not a protocol: the pilot ruled on 30 September 2026 that
   the shapes of mid-campaign steps are not preserved and that no format is a
   protocol before a release. Today's YAML episodes load
   into it unchanged.
2. Port the film page to the React stage with sets, slots and an element
   registry. Its current behaviour becomes the `Paper` set and the `View`,
   `Source` and `Picture` elements; the three current presentations become
   three sets.
3. Add the Python declarations that evaluate to the document, with
   symbolic anchors.
4. Add the page take and the `Page` element, driven by the Leonardo museum
   shot.
5. Mount the stage in the studio with a scrubber.
6. Add machine takes when the first running or clocked episode asks for
   them, together with the viewer parity requirement.

## Relation to other records

- `roadmap.md` items 4, 12, 13 and 15 (multiple views, free layouts, live
  preview, several outputs) find their place in this tree; the roadmap stays
  as the historical wishlist and is not edited by this note.
- `AGENTS.md` ("do not require executable code to read or edit an
  episode"), `docs/FORMAT.md` ("No executable episode code") and
  `roadmap.md` ("Design constraint to keep") state the rule this note
  proposes to reverse. Until an OpenSpec change does so, they stand.
- The findings above belong in `warts.md` once triaged; they are recorded
  here first because the direction was settled before the triage.
