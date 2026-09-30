# The movie document — `machinome-movie/0.1`

Status: contract of `machinome-movie/0.1`, written 30 September 2026 for the
declarative-python campaign. The Node tool loads it through the
`movie-document` OpenSpec change (archived on the campaign branch; its
integration is the pilot's); the Python declarations that emit it are a later
change. Where the archived change's spec (`openspec/specs/movie-document/`)
and this page disagree, the spec is right. "Implementation notes" at the end
records where the implementation departs from the draft.

## What it is

The seam between the declarations a project writes and the renderer. The
Python declarations (`machinome_movie`) evaluate once to this document; the
Node tool loads it, resolves its anchors against the cached speech, validates
the result as it validates a format 0.4 episode today, and produces the film.
A YAML episode loads into the same resolved shape, each shot becoming a
one-shot chapter, so nothing changes for existing episodes.

The document is a build output, written by default to
`<movie-dir>/_build/movie.json`. It is data: no code, no expressions. Every
relative path in it resolves against `root`, itself relative to the document
file (or absolute), and the tool's own outputs go to `<root>/_build/`.

## Top level

```json
{
  "format": "machinome-movie/0.1",
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
  "chapters": [ … ]
}
```

`output` carries no `durationSeconds`: the film's length is the last shot's
resolved end. `marks` names model seconds of the posed loop, the trivial take;
a mark is the author's word for an instant of the machine. `audio`, `style`,
`cameras`, `layers`, `evidence`, `sourceCode`, `stills`, `clips`, `credits`
and `release` keep the meaning `docs/FORMAT.md` gives them in
`production.yaml`.

## Chapters and shots

```json
{"id": "drive", "speechOffset": 0.2,
 "narration": "Water passes beneath the wheel and turns a shaft. In the model, the waterwheel drives the crankshaft.",
 "direction": "…",
 "shots": [
   {"id": "wheel", "set": "paper", "until": {"spoken": "In the model"},
    "direction": "…",
    "simulation": {"from": 428, "to": {"mark": "pull_start"}},
    "camera": [{"at": 0, "preset": "drive"}],
    "hiddenLayers": ["structure", "foundation", "carriage"],
    "overlays": [], "evidence": ["model"]},
   {"id": "coupling", "set": "paper-split",
    "until": {"spokenEnd": "drives the crankshaft", "plus": 0.9},
    "transition": {"kind": "dissolve", "duration": 0.6},
    "code": {"snippet": "coupling", "typing": [{"from": 0, "to": 1.2, "throughLine": 415}],
             "emphasis": [{"line": 415, "phrase": "the waterwheel drives the crankshaft",
                           "words": ["waterwheel", "drives", "crankshaft"], "hold": 0.9}]},
    "highlight": [{"from": {"spoken": "waterwheel"}, "to": {"spoken": "crankshaft"},
                   "parts": [["Water drive", "Undershot waterwheel"]], "others": "ghost"}],
    "simulation": {"from": {"mark": "pull_start"}, "to": {"mark": "cycle_end"}},
    "camera": [{"at": 0, "preset": "drive"}], "hiddenLayers": ["structure", "foundation", "carriage"],
    "overlays": [], "evidence": ["model"]}
 ]}
```

- A **chapter** has a unique `id`, a non-empty `narration`, an optional
  `speechOffset` (default 0.2 s from the chapter's start), an optional
  editorial `direction`, and ordered `shots`. One speech take is generated
  per chapter and placed at its start plus the offset.
- A **shot** has a unique `id`, a `set`, an `until`, an optional `direction`,
  and the format 0.4 shot fields with their 0.4 meaning: `simulation`,
  `camera`, `hiddenLayers`, `overlays`, `evidence`, `code`, `annotations`,
  `highlight`, `pictures`, `transition`, `fadeIn`, `fadeOut`. It has no
  `start`, `end`, `narration` or `layout`: the first two are resolved, the
  third belongs to the chapter, the fourth is the set.
- `set` is one of `paper` (the model stage alone), `paper-split` (source
  left, model right) and `source-only`. `paper-split` and `source-only`
  require `code`; `paper` refuses it. When `set` is omitted it is `paper`
  without `code` and `paper-split` with it, which is today's rule. These are
  the three layouts the film page draws; a set the page does not have is
  refused by name. The document grows slots and elements when the React
  stage arrives.
- `fadeIn` is accepted only on the film's first shot and `fadeOut` only on
  its last, across chapters.

## Anchors

Wherever a 0.4 field takes shot-local seconds (`until`, a camera key's `at`,
a model keyframe's `at`, a cue's `from` and `to`, a typing cue's `from` and
`to`), the document accepts either a number or an anchor:

- a **number** is seconds as today: shot-local for cues and keys; for `until`,
  the shot's duration;
- `{"spoken": "<phrase>"}` is the instant the narrator begins the phrase:
  the onset of the first letter or digit of its first word, the rule word
  reveals already use;
- `{"spokenEnd": "<phrase>"}` is the instant the phrase's last character
  ends;
- either may carry `"plus": <seconds>`, positive or negative.

The phrase must occur exactly once in the chapter's written narration, and
its spoken form (after `audio.replacements`) exactly once in the chapter's
cached alignment; otherwise the document is refused naming the chapter, the
shot, the field and the phrase. A spoken anchor resolves to absolute film
time: chapter start + `speechOffset` + the alignment time + `plus`.

Wherever a field takes **model seconds** (`simulation.from`, `simulation.to`,
a model keyframe's `seconds`), it accepts a number or `{"mark": "<name>"}`
with optional `"plus"`, resolved from `marks`; an unknown mark is refused
naming the shot and the mark.

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
5. Cue anchors become shot-local by subtracting the shot's resolved start. A
   cue anchored before its shot's start or after its end is refused as the
   0.4 rules refuse an out-of-range cue, naming the anchor.
6. `output.durationSeconds` is the last shot's end. The narration take must
   fit its chapter as a shot's take must fit its shot today.
7. The result is a format 0.4 episode with `chapters`, and every 0.4
   validation, refusal and frame rule applies unchanged. Word timing for
   reveals and source emphasis reads the shot's chapter take with the offset
   `chapter.start + speechOffset − shot.start`.
8. `check` writes the resolved document to `<root>/_build/movie-resolved.json`
   for inspection and for the shared fixtures; `preview` and `render` write
   the same file before capturing.

## Schema and fixtures

`schema/machinome-movie-0.1.json` is the JSON Schema of the unresolved
document: field names, types and closed field lists. Both runtimes validate
against this one file before any semantic check. `fixtures/` holds the
documents both suites run; see `fixtures/README.md`.

## Implementation notes

What the `movie-document` change implemented differently from the draft
above, and why (its `design.md`, D9 to D14):

- **Picture view keys take anchors.** A picture's `view` key `at` accepts a
  time anchor like the other shot-local times: the validation film's `still`
  shot ends its push half a second before "Explore".
- **Anchor fields are named by their path in the shot** in every refusal:
  `until`, `camera[1].at`, `simulation.keyframes[2].at`,
  `simulation.from`, `overlays[0].to`, `code.typing[0].from`,
  `pictures[0].view[1].at`.
- **Refused before any take, besides the draft's rules**: a camera key whose
  preset is not in `cameras`; a model keyframe list whose last `at` is not the
  shot's `until` (the same number or the same anchor, so the keys end at the
  shot's end whatever the take); and, reading the export's manifest, a layer
  path, a highlighted part or an annotated part the export does not contain,
  or a layer name the document does not declare.
- **Chapter and shot ids are slugs** (`^[a-z0-9-]+$`), since a chapter id
  names its take's file and a shot id already had to be one.
- **What may be left out.** A chapter's `speechOffset` (0.2 s) and
  `direction`; a shot's `set`, `direction` (resolved as `""`) and every cue
  list but `hiddenLayers`, `overlays` and `evidence`; the document's
  `series`, `status`, `learningGoal`, `marks`, `sourceCode`, `stills`,
  `clips`, `style` (resolved as `{}`), `credits` and `release`. A render
  without `release.descriptionTemplate` writes no `description.md` and is
  not release-ready.
- **Closed lists outside the shot.** `audio` accepts `provider`, `model`,
  `voice`, `voiceLabel`, `outputFormat`, `voiceSettings`, `replacements`
  and `direction`; `style` its five fields; `release` `simulationUrl`,
  `sourceUrl`, `descriptionTemplate` and `publish`; `credits` is open.
- **Every command that loads a document writes `movie-resolved.json`**,
  `speech` and `build` included, since they resolve after generating the
  takes.
- **The schema is checked by a small validator of the keywords it uses**
  (`src/schema.mjs`), not by a dependency; a test keeps the two in step.
- **A resolved film lasts a whole number of frames at its own rate**, not
  necessarily at another: `render --fps` at a lower rate may be refused
  (`Frame count is not integral`). Render movies at their own rate.
