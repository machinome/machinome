# The movie document — `machinome-movie/0.2`

Status: contract of `machinome-movie/0.2`, written 30 September 2026 for the
react-stage campaign, replacing `machinome-movie/0.1` (a step of the previous
campaign, not a protocol, by the pilot's ruling of the same day; nothing of
its shape is preserved or owed). It is implemented by the `react-stage`
change (the Node side: loading, resolution, the timeline and the stage) and
the `declarative-stage` change (the Python side: declarations evaluating to
it). Where an archived change's spec and this page disagree, the spec is
right. No format is a protocol before the pilot makes a release.

## What it is

The seam between the declarations a project writes and the stage that draws
them. A movie evaluates once to this document; the tool loads it, resolves
its anchors against the cached speech, checks it completely before a browser
opens, and produces the film. The document carries the declarations' shape:
**sets** with **slots**, **elements** placed in them by **shots**, and
**cues** that fire **actions** on elements at **anchors**. It is data: no
code, no markup, no expressions. The React components a set or an element is
drawn with live in the project's stage modules, which the document names and
the tool bundles.

Two rules hold across the seam. *Python says what and when; React says how it
looks*: every word a reader reads and every number provenance hashes is in
this document, and a component never invents timing. *A frame is a pure
function of video time*: the tool resolves the document to one **frame** per
output instant, the set, the element in each slot and each element's state,
and the stage only draws what a frame says.

The document is a build output, written by default to
`<movie-dir>/_build/movie.json`. Every relative path in it resolves against
`root`, itself relative to the document file (or absolute), and the tool's
own outputs go to `<root>/_build/`. A YAML episode (`docs/FORMAT.md`) loads
into the same resolved shape through the sets the tool ships, so episodes
written before the stage keep producing.

## Top level

```json
{
  "format": "machinome-movie/0.2",
  "id": "cut-and-advance",
  "title": "Cut and Advance",
  "series": "LEONARDO · HOW IT WORKS",
  "status": "rehearsal",
  "learningGoal": "…",
  "root": "..",
  "output": {"width": 1920, "height": 1080, "fps": 30},
  "model": {"manifest": "../../export/hydraulic_sawmill/manifest.json",
            "expectedDurationSeconds": 1460, "timeMode": "normalized-loop",
            "sourceRevision": "28b43bce1b88446995f0ff231dd9075d1a839ab3",
            "readiness": "…"},
  "marks": {"pull_start": 436, "return_start": 438, "cycle_end": 440},
  "audio": {…}, "style": {…}, "cameras": {…}, "layers": {…},
  "evidence": {…}, "sourceCode": {…}, "stills": {…}, "clips": {…},
  "credits": {…}, "release": {…},
  "stage": {…},
  "chapters": [ … ]
}
```

- `output` carries no duration: the film's length is the last shot's
  resolved end.
- `marks` names model seconds of the posed loop, the trivial take.
- `audio`, `cameras`, `layers`, `evidence`, `sourceCode`, `stills`, `clips`,
  `credits` and `release` keep the meaning `docs/FORMAT.md` gives them. A
  camera is `{"position", "target", "up", "fov"}`; a layer is a list of
  assembly paths; a source excerpt is `{"file", "lines": [first, last]}`.
- `style` is the palette and type the movie's root set reads:
  `background`, `foreground`, `accent` (`#rrggbb`), `fontFamily`,
  `safeInsetFraction`. Every field is optional; the stage supplies its
  defaults and reports them. It is not layout: layout is the set's.
- Every id, kind, key and slot name in the document is a slug,
  `^[a-z][a-z0-9-]*$`.

## The stage block

```json
"stage": {
  "modules": ["stage.tsx"],
  "sets": {
    "leonardo": {"module": "stage.tsx", "slots": ["stage", "plate", "headline", "aside"],
                 "props": {"series": "LEONARDO · HOW IT WORKS"}},
    "leonardo-split": {"module": "stage.tsx", "base": "leonardo",
                       "slots": ["left", "right", "headline"], "props": {}},
    "frame": {"slots": ["stage"]}
  },
  "elements": {
    "jobs": {"module": "stage.tsx",
             "props": {"jobs": "list"},
             "actions": {"light": {"job": "string"}}}
  }
}
```

- `modules` are the project's stage modules, paths relative to `root`,
  TypeScript (`.ts`, `.tsx`) or JavaScript (`.js`, `.jsx`), inside the
  project repository. The tool bundles them with its own stage runtime into
  one script per movie. A module registers the sets and elements it draws
  under their kinds (see "The stage").
- `sets` lists **every set kind a shot of the movie uses, and the project
  sets those derive from**, by kind. An entry with a `module` is the
  project's: `slots` are the slots its own body declares (a derived set
  inherits its base's chrome, not its layout, so it lists its own slots in
  full), `base` names the set it derives from (a kind in this table or a
  shipped kind), `props` is a JSON object of static values the component
  receives: the set's own class attributes over the ones it inherits from
  its base, so a derived set's entry carries the merged props and the chrome
  it inherits reads them from that entry (left out when empty). An entry
  without a `module` is a set the
  tool ships (`frame`, with the slot `stage`; `split`, with `left` and
  `right`); its `slots` must equal the shipped ones, so both runtimes check
  placements against one table.
- `elements` lists the **project's element kinds** (never the shipped ones).
  `props` maps each prop name to its kind, one of `string`, `number`,
  `boolean`, `list`, `object`; `actions` maps each action name to its
  parameters, each of kind `string`, `number` or `boolean`. A kind's prop
  kinds come from the instances the movie declares: every instance of a kind
  gives the same props of the same kinds, or evaluation refuses by name.
  From this block the tool generates the TypeScript types of the
  components' props.

## Chapters

```json
{"id": "drive", "speechOffset": 0.2,
 "narration": "Water passes beneath the wheel and turns a shaft. In the model, the waterwheel drives the crankshaft. …",
 "direction": "…",
 "elements": {
   "mill": {"kind": "view", "camera": "drive", "hide": ["structure", "foundation", "carriage"]},
   "code": {"kind": "source", "source": "coupling"},
   "title": {"kind": "title", "text": "CUT AND ADVANCE", "subtitle": "One wheel, two jobs"},
   "iso": {"kind": "picture", "still": "isometric", "fit": "contain"},
   "card": {"kind": "jobs", "props": {"jobs": ["Cut", "Advance"]}}
 },
 "shots": [ … ]}
```

A chapter has a unique `id`, a non-empty `narration`, an optional
`speechOffset` (default 0.2 s from the chapter's start), an optional
editorial `direction`, its `elements` and its ordered `shots`. One speech
take is generated per chapter and placed at its start plus the offset.

An element is declared once on the chapter and placed by any of its shots;
it keeps its state across a cut inside the chapter (a view keeps the camera
its last move ended at, a source panel keeps its typed text). The shipped
element kinds and their declarations:

| kind | declaration | what it is |
|---|---|---|
| `view` | `camera` (a key of `cameras`), `hide` (layer names, optional) | the model through a camera; the loop's posed take |
| `source` | `source` (a key of `sourceCode`) | a pinned excerpt, typed and emphasised on cue |
| `title` | `text`, `subtitle` (optional) | words on the frame; shown on cue |
| `picture` | `still` or `clip` (a key of `stills` or `clips`), `fit` (`contain` or `cover`, optional), `inPoint` (clips, optional) | a project picture; shown on cue |
| a project kind | `props`, a JSON object matching the kind's declared props | anything the project's module draws |

## Shots

```json
{"id": "coupling", "set": "leonardo-split",
 "places": {"left": "code", "right": "mill"},
 "until": {"spokenEnd": "drives the crankshaft", "plus": 0.9},
 "direction": "…",
 "model": {"from": 444, "to": 450},
 "transition": {"kind": "dissolve", "duration": 0.6},
 "cues": [
   {"at": 0, "actions": [{"element": "code", "action": "type", "throughLine": 415, "over": 0.6}]},
   {"at": {"spoken": "waterwheel"}, "until": {"spoken": "crankshaft"},
    "actions": [{"element": "mill", "action": "highlight",
                 "parts": [["Water drive", "Undershot waterwheel"]], "others": "ghost"}]},
   {"at": {"spoken": "the waterwheel drives the crankshaft"},
    "actions": [{"element": "code", "action": "emphasize", "hold": 0.6,
                 "words": [{"spoken": "waterwheel", "token": "waterwheel"},
                           {"spoken": "drives", "token": "drives"},
                           {"spoken": "crankshaft", "token": "crankshaft"}]}]}
 ]}
```

- A shot has a unique `id`, a `set` (a kind in `stage.sets`), `places`, an
  `until`, an optional `direction`, its `model` time, optional `transition`,
  `fadeIn`, `fadeOut`, and `cues`. It has no start, end or narration: the
  first two are resolved, the third is the chapter's.
- `places` maps slot names of the set to element keys of the chapter. A
  slot not named is empty. A slot the set does not declare, an element the
  chapter does not declare, and an element placed in two slots of one shot
  are refused by name.
- `model` is the loop's time over the shot: `{"from", "to"}` in model
  seconds (a number or `{"mark": name, "plus"?: seconds}`), or
  `{"keys": [{"at": time, "seconds": model-time, "ease"?: curve}, …]}`
  whose first key is at 0 and whose last key is at the shot's `until` (the
  same number or the same anchor). Segments are linear unless the key a
  segment ends at names a curve (`linear`, `smooth`, `in`, `out`,
  `in-out`). Every view of the shot sees this time.
- `transition` (`dissolve`, `fade`, `wipe`, `slide`, with `duration`,
  optional `ease`, `direction` on a wipe or slide, `color` on a fade) is how
  the shot comes in from the one before it; `fadeIn` is accepted only on the
  film's first shot and `fadeOut` only on its last, across chapters.

### Cues and actions

A cue is `{"at": time, "until"?: time, "actions": [ … ]}`. `at` is when it
fires; `until`, when the actions that show something end. Every action
names the `element` it acts on, which the shot must place, and its `action`.
The shipped actions:

| element | action | fields | spans |
|---|---|---|---|
| `view` | `move` | `camera`, `until` (time), `ease`? | its own `until` |
| `view` | `highlight` | `parts` (layer names or paths), `others`? (`keep`, `dim`, `ghost`), `color`? | yes |
| `view` | `ring` | `part`, `padding`?, `enter`?, `leave`? | yes |
| `view` | `label` | `part`, `text`, `offset`? ([x, y]), `enter`?, `leave`? | yes |
| `view` | `arrow` | `part` or `point`, `text`?, `place` ([x, y]), `enter`?, `leave`? | yes |
| `source` | `type` | `throughLine`, `over` (seconds) | no |
| `source` | `emphasize` | `words` ([{`spoken`, `token`}]), `hold`?, `line`? | the phrase and its hold |
| `title` | `show` | `enter`?, `leave`?, `reveal`? | yes |
| `picture` | `show` | `enter`?, `leave`?, `view`? ([{`at`, `center`, `zoom`, `ease`?}]) | yes |
| a project kind | a declared action | `params`, matching the declared parameters | yes |

- An action that **spans** needs the cue's `until`; a cue whose actions all
  fire and finish on their own (`type`, `move`) needs none.
- `enter` and `leave` are `{"kind": "fade" | "draw", "duration", "ease"?}`;
  `draw` only on the entrance of a ring or an arrow; an exit is a fade.
- A mark's `offset` and an arrow's `place` are fractions of the **view
  element's box**, not of the frame: a set may put the view anywhere.
- `emphasize` lights each `token` of the excerpt from the onset of its
  `spoken` words in the narrator's take until the cue's phrase ends plus
  `hold`. The cue's `at` must be `{"spoken": phrase}` with no `plus`. Each
  `spoken` must occur exactly once in that phrase, **word-bounded**: not
  preceded or followed by an ASCII letter, digit or underscore. A `token` is
  an identifier or a dotted path of identifiers
  (`[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*`), and it occurs
  where its text is word-bounded the same way: **a dot is a boundary**, so
  `waterwheel` occurs in `water_drive.waterwheel.spin`, `feed.pawl` occurs
  in `feed.pawl.turn`, and `pawl` does not occur in `pawl_mount`. Each token
  must occur exactly once in the whole excerpt, on any line, or, when the
  action names a `line` (a file line number inside the excerpt), exactly
  once on that line; both runtimes refuse an absent or ambiguous token
  naming it, and evaluation reads the excerpt's source file to do so. A
  token must be typed by the time its word is spoken. `spoken` and `token`
  may differ: *the driving pawl* may light `feed.pawl.turn`.
- `type` types the excerpt from where the previous typing stopped through
  `throughLine`, over `over` seconds from the cue's `at`. The typing cues of
  a shot run in order and must complete the excerpt before the shot ends,
  unless the panel was completed in an earlier shot of the chapter.
- `reveal` is `{"timing": "spoken", "phrase"?}` (each word of the title
  appears as it is spoken; `phrase` defaults to the title's text, must match
  it word for word and must occur exactly once in the chapter's narration)
  or `{"timing": "even", "duration", "ease"?}`.

### Anchors

Wherever a shot takes a **time** (`until`, a cue's `at` and `until`, a
`move`'s `until`, a model key's `at`, a picture view key's `at`), the
document accepts a number or an anchor:

- a **number** is shot-local seconds; for `until`, the shot's duration;
- `{"spoken": "<phrase>"}` is the instant the narrator begins the phrase:
  the onset of the first letter or digit of its first word;
- `{"spokenEnd": "<phrase>"}` is the instant the phrase's last character
  ends;
- either may carry `"plus": <seconds>`, positive or negative.

The phrase must occur exactly once in the chapter's written narration and,
after `audio.replacements`, exactly once in the chapter's cached alignment;
otherwise the document is refused naming the chapter, the shot, the field
and the phrase. A spoken anchor resolves to absolute film time: chapter
start + `speechOffset` + the alignment time + `plus`.

Wherever a shot takes **model seconds** (`model.from`, `model.to`, a key's
`seconds`), it accepts a number or `{"mark": "<name>", "plus"?}`, resolved
from `marks`; an unknown mark is refused naming the shot and the mark.

Refusals name an anchor's field by its path in the shot: `until`,
`model.from`, `model.keys[2].at`, `cues[1].at`, `cues[1].until`,
`cues[0].actions[0].until`, `cues[3].actions[0].view[1].at`.

## Resolution

1. Chapters play in order; shots play in order within them; the film starts
   at 0 and a shot starts where the previous one ended.
2. `speech` needs only the narration and runs on the unresolved document. It
   caches one take per chapter under `_build/audio/`, keyed as today.
3. `check`, `preview`, `render` and `build` resolve every anchor against the
   cached takes. A document with spoken anchors and no cached take for a
   chapter is refused, naming the chapter and asking for `speech` first;
   `check` never generates speech.
4. A resolved anchor is snapped to the output frame grid (nearest frame).
   Literal numbers are kept as written. A shot whose `until` resolves at or
   before its start is refused, naming the shot and the anchor.
5. Cue times become shot-local by subtracting the shot's resolved start. A
   cue anchored before its shot's start or after its end is refused, naming
   the anchor. A spanning action whose `until` is at or before its `at` is
   refused.
6. The film's duration is the last shot's end. The narration take must fit
   its chapter.
7. The **resolved document** is the same document with `"resolved": true`,
   `output.durationSeconds`, `start` and `end` on every chapter and shot,
   and every time numeric. `check` writes it to
   `<root>/_build/movie-resolved.json`; `preview` and `render` write the
   same file before capturing. A YAML episode loads into exactly this
   shape: one chapter per shot, the shipped sets `paper`, `paper-split` and
   `source-only`, and elements synthesized from its fields.

## The frame

`frameAt(resolved, t)` is a pure function of the resolved document and a
video time. It is what the stage receives, the studio scrubs, the renderer
encodes and the shot cache hashes:

```json
{"time": 12.4, "chapterId": "drive", "shotId": "coupling",
 "set": "leonardo-split",
 "slots": {"left": "drive.code", "right": "drive.mill"},
 "elements": {
   "drive.mill": {"kind": "view", "time": 0.3041, "view": {"camera": […], "target": […]},
                  "up": [0, 0, 1], "fov": 37, "hidden": [[…]],
                  "highlight": {"paths": [[…]], "others": "ghost", "color": "#237c86"},
                  "marks": [{"id": "cues[4].actions[0]", "kind": "ring", "target": {"paths": [[…]]},
                             "padding": 0.01, "opacity": 1, "drawn": 0.62}]},
   "drive.code": {"kind": "source", "file": "models/hydraulic_sawmill/model.py",
                  "firstLine": 413, "lastLine": 415, "text": "…", "html": "…", "cursor": false,
                  "emphasis": [{"token": "waterwheel", "start": 18, "end": 28}]}
 },
 "transition": null}
```

- An element key is `<chapter id>.<element key>`, so a chapter's element is
  one instance across its shots and two chapters' elements never collide.
- Only placed elements appear, each with its complete state for this
  instant; nothing is carried from the frame before. A `title` or `picture`
  that is placed and not shown appears with `"shown": false`.
- `title` state: `shown`, `text`, `subtitle`?, `opacity`, and with a reveal
  `words` (the text split into words and spaces) and `revealed` (how many
  words are visible). `picture` state: `shown`, `kind` (`still` or `clip`),
  `name`, `frame`? (clips), `opacity`, `rect` ([x, y, w, h] as fractions of
  the slot's box), `fit`. A project element's state: `props` and `actions`,
  the active actions as `{action, params, since, until, progress}` with
  `since` and `until` shot-local and `progress` in [0, 1].
- `transition` is as before: `null`, or the join in progress with the
  outgoing shot's frame under `outgoing`.
- The frame carries no film-wide position: showing where a viewer is in a
  film is the player's job, not the video's (the pilot's ruling of
  30 September 2026, `remove-progress-rule`).

## The stage

The stage is the React page that draws frames. It is built once per movie
from the tool's runtime and the document's `stage.modules`, and served to
headless Chromium by the renderer. Its contract with the renderer:

- `window.film.setFrame(frame)` draws a frame synchronously and returns
  what it measured: `{"frame": {"width", "height"}, "chrome": [rects],
  "slots": {"<slot>": rect}, "elements": {"<key>": report}}`. A view reports
  its camera, target, up, field of view, navigation and the on-screen
  geometry of its marks; a source panel its lit tokens and whether the
  excerpt fits its box; a title its box and revealed count; a picture its
  drawn rect and natural size; a project element whatever its component
  reports, always with its box. The renderer checks the report against the
  request, as it does today, and refuses a frame that differs.
- `window.film.compose(request)` and `composeMarkBlend(pictures)` draw
  transition and blended frames over the page from same-instant captures,
  as today, in a layer above every set's content and below its chrome.
- **Chrome** is what a set draws above pictures and transitions: a masthead,
  a series label, whatever the template decides. A set marks it with the
  runtime's `Chrome` component; the stage lifts it above the transition
  layer, hides it in picture-only captures and reports its rects, which the
  pixel proofs mask. Nothing else in the page is fixed: no bar, no brand,
  no series label the document did not ask for.
- A set is a React component the module registers under its kind with the
  slots it declares; an element likewise. At mount the stage refuses, by
  name, a set or element kind the bundle does not register, a set whose
  registered slots differ from the document's, and a runtime API version
  below what the movie needs.
- Components are pure in video time: no wall clock, no asynchronous state
  between frames, no measurement that changes what is drawn. The viewer
  mounts once outside React's reconciliation and is positioned over the
  view element's box; two views in one shot are two viewer instances.

The authoring contract, `docs/stage.md`, says how a project writes a set or
an element. The tool ships the sets `frame` (one slot, `stage`, the whole
picture, no chrome) and `split` (`left`, `right`), the element kinds above,
and, for YAML episodes only, the sets `paper`, `paper-split` and
`source-only` that reproduce the earlier film page's layouts with its
masthead and no progress rule.

## Schema and fixtures

`schema/machinome-movie-0.2.json` is the JSON Schema of the unresolved
document: field names, types and closed field lists. Both runtimes validate
against this one file before any semantic check. `fixtures/` holds the
documents both suites run; see `fixtures/README.md`.
