## Context

`loadEpisode(file)` in `src/episode.mjs` reads `episode.yaml` and its
`production.yaml`, merges them into one object `e`, validates it against the
export (`validateEpisode`), checks the project (layers, evidence, repository,
pinned revision, source excerpts, pictures) and returns it. Everything
downstream reads `e`: `frameAt` (pure, `src/timeline.mjs`), preview and render
(`src/render.mjs`), the shot cache, the review samples, word timing
(`src/words.mjs`) and speech (`src/speech.mjs`).

Narration belongs to the shot. `speech` synthesizes one take per shot, keyed
by `sha256({voice, request, format})` where the request carries the shot's
spoken text and, for models other than `eleven_v3`, its neighbours' texts; the
file is `_build/audio/<shot-id>-<key16>.<ext>` beside a `.json` record
`{cache, voice, model, format, request, alignment, sha256, duration}`. The
take is placed at `shot.start + (shot.speechOffset ?? 0.2)` and must end 0.1 s
before the shot does. Word timing (spoken reveals, source emphasis) reads the
shot's take at the shot-local offset `shot.speechOffset ?? 0.2`.

Relative paths (model manifest, evidence, source excerpts, pictures, the
description template) resolve against `dirname(e.paths.production)`.

The contract this change implements is the draft `docs/movie-document.md`.
The validation film is `videos/cut_and_advance/spec.md` in the Leonardo
project, the acceptance target of the campaign.

## Goals / Non-Goals

Goals: load a `machinome-movie/0.1` document into the same internal episode a
YAML source produces, with chapters, one take per chapter, spoken anchors,
marks and sets exactly as the contract states; keep every YAML episode's
frames, speech cache keys and captions identical; give both runtimes one
schema and one set of fixtures. Non-goals: the Python declarations, the film,
the React stage, any anchor form or set the contract does not name, any
change to `src/film.js`, `src/film.html` or `frameAt`.

## Decisions

### D1. Dispatch by extension, one internal episode

`loadEpisode(file)` loads a `.json` file as a movie document and anything
else exactly as today. Both return the episode object the tool consumes: the
format 0.4 shape (`format: machinome-video-draft/0.4` for a document), with
numeric `start`/`end` on every shot, plus `chapters`. A document's episode
also carries `movie: "machinome-movie/0.1"`, which marks narration as
chapter-owned for validation. `frameAt`, preview, render, the shot cache and
review packs read it unchanged.

Loading a document runs, in order: the format (refused by name before
anything else), the schema (D9), the static checks (D7, D8 and the phrase
and mark checks of D6), the cached takes of the chapters that have spoken
anchors (D5), the pure resolution (D6), then `validateEpisode` and the same
project checks a YAML episode gets. Each layer refuses before the next runs.

Paths: a document's `root` is relative to the document file (or absolute);
`e.paths.base` is that root, `e.paths.build` is `<root>/_build`, and both
`e.paths.episode` and `e.paths.production` name the document file, so the
manifest's `episodeSha256` is the document's hash. Every relative path
(model manifest, evidence, source excerpts, pictures, description template)
resolves against `e.paths.base ?? dirname(e.paths.production)`: for a YAML
episode that is today's directory. `src/code.mjs`, `src/pictures.mjs` and
`src/render.mjs` change only in that one expression.

### D2. The internal `chapters` field

```js
e.chapters = [{
  id: 'drive',                 // unique slug, the take's file name prefix
  narration: 'Water passes …', // the chapter's written narration
  speechOffset: 0.2,           // seconds from the chapter's start; always a number
  start: 11.4, end: 35.1,      // the first shot's start, the last shot's end
  shots: ['wheel', 'coupling', 'stroke'],  // shot ids, in order
  direction: '…'               // only when the document gives one
}, …]
```

Shots are named by id, not embedded, so the episode (which the render
manifest records whole) holds each shot once.

A YAML episode maps each shot to one chapter: `{id: shot.id, narration:
shot.narration, speechOffset: shot.speechOffset ?? 0.2, start: shot.start,
end: shot.end, shots: [shot.id]}`, set by `loadEpisode` after validation.
Episode objects built directly (as unit tests do) have no `chapters`; the
helpers of `src/chapters.mjs` derive the same mapping from the shots, so
every existing caller keeps working:

- `chaptersOf(e)`: `e.chapters`, or the per-shot mapping;
- `chapterOf(e, shot)`: the chapter whose `shots` names the shot;
- `narrationOf(e, shot)`: that chapter's narration (for a YAML shot, its own);
- `takeOffset(e, shot)`: the shot-local instant the chapter's take starts,
  `chapter.start + chapter.speechOffset − shot.start`, and exactly
  `chapter.speechOffset` when `chapter.start === shot.start`, so a YAML shot's
  offset keeps its bits (`5.366 + 0.2 − 5.366` is not `0.2` in floating point).

### D3. One take per chapter, today's cache key

`speech` iterates chapters where it iterated shots. The request's `text` is
the chapter's spoken narration (after `audio.replacements`), `previous_text`
and `next_text` its neighbour chapters' (omitted for `eleven_v3`, as today);
the key and file name are computed by the same expression with the chapter's
id in place of the shot's. For a YAML episode chapters are shots with the same
ids and texts, so every key and file name is unchanged and the Leonardo
project's cached takes stay valid; a test pins the names, request hashes,
records and captions computed on the base commit.

The take is placed at `chapter.start + chapter.speechOffset` and must end
0.1 s before the chapter does; an overflow is refused after caching, naming
the chapter, as a shot's is today. Captions are the chapter's alignment at
that offset; the mix places one file per chapter. The refusal keeps its YAML
wording (`Narration exceeds shot timing; revise YAML (audio is cached)`); a
document says `Narration exceeds chapter timing; revise the movie (audio is
cached)`.

The provider key is read when a take is actually missing, not before the
loop. The behaviour for a missing take is unchanged; a `speech` whose takes
are all cached no longer needs a key, which is what lets the pipeline tests
run the command path with no key in the environment, as the testing policy
requires.

### D4. Speech on the unresolved document

`speech` needs only narration, so on a document it first generates the
missing takes from the unresolved document (format, schema and static
checks passed, nothing resolved), then loads the document as every command
does, resolving the anchors against the takes it just cached, and then fits,
captions, measures words and mixes exactly as for a YAML episode. `build`
without `--silent` does the same. A refusal after generation (a phrase the
take does not contain, a take that overflows its chapter) leaves the takes
cached, as today.

### D5. Takes are read, never requested, by check, preview and render

Resolution needs the take of every chapter with at least one `spoken` or
`spokenEnd` anchor. It reads the cached record and verifies the audio's
checksum and the alignment, as word timing does. A missing take is refused:

    Chapter drive has spoken anchors and no cached narration take; run the
    speech command first (check, preview and render never generate speech)

A chapter without spoken anchors needs no take to resolve. Word timing, when
a shot has a spoken reveal or emphasis, still reads the take through
`readSpeechTake`, whose refusal now names the shot and, when they differ, its
chapter.

### D6. Anchors and marks

Forms, as the contract states: a number; `{"spoken": phrase, "plus"?}`;
`{"spokenEnd": phrase, "plus"?}`; for model seconds a number or `{"mark":
name, "plus"?}`.

Fields that take a time anchor, named in refusals by their path inside the
shot: `until`; `camera[i].at`; `simulation.keyframes[i].at`;
`overlays[i].from`/`.to`, `annotations[i].from`/`.to`,
`highlight[i].from`/`.to`, `pictures[i].from`/`.to`; `code.typing[i].from`/`.to`;
and `pictures[i].view[j].at` (D11). Fields that take a mark:
`simulation.from`, `simulation.to`, `simulation.keyframes[i].seconds`. All
other numbers (durations of transitions, fades, entrances; `inPoint`;
`hold`; places and offsets) are literal only.

Static checks, before any take is read (the Python side can make the same
ones): every phrase occurs exactly once in its chapter's written narration,
else `Spoken phrase is absent from the narration of chapter <c>: <phrase>
(<field> of shot <s>)` or `Spoken phrase is ambiguous in the narration of
chapter <c>: <phrase> (<field> of shot <s>)`; every mark is in `marks`, else
`Unknown mark: <name> (<field> of shot <s> in chapter <c>)`; a literal `until`
greater than zero (D8's wording).

Resolution, pure (`resolveMovie(document, takes)`):

1. Chapters in order, shots in order; the film starts at 0 and a shot starts
   where the previous one ended. A chapter starts where its first shot does.
2. A phrase's spoken form (after `audio.replacements`) must occur exactly
   once in the chapter take's alignment text, else `Spoken phrase is absent
   from the recorded narration of chapter <c>: …` or `… is ambiguous in the
   recorded narration …`. `spoken` is the start time of the first letter or
   digit of the phrase's first word (the rule word reveals use); `spokenEnd`
   the end time of the phrase's last character.
3. The instant is `chapter.start + speechOffset + alignment time + plus`,
   snapped to the nearest frame of `output.fps` (`round(t × fps) / fps`).
   Literal numbers are kept as written: a literal `until` is the shot's
   duration, a literal cue time is shot-local.
4. `until` resolves the shot's end; a shot whose end is at or before its
   start is refused: `Shot <s> ends at or before its start: until <anchor>
   (chapter <c>)`, with the resolved instants for an anchor.
5. Every other time anchor becomes shot-local by subtracting the shot's
   resolved start. A value within 1e-9 of 0 or of the shot's duration is set
   to exactly that bound, so a cue or key anchored at the same phrase as the
   `until` lands exactly on the shot's duration (a model keyframe's last `at`
   must equal it exactly). An anchor before the shot's start or after its end
   is refused: `Anchor <anchor> of <field> in shot <s> (chapter <c>) falls
   outside the shot`.
6. Marks resolve to `marks[name] + plus`, not snapped (model seconds).
7. `set` becomes the layout (D7); `until` and `set` are dropped; the chapter
   records its resolved `start`, `end` and `speechOffset` (default 0.2).
   `output.durationSeconds` is the last shot's end.

The result is the 0.4 episode, validated by `validateEpisode` with every 0.4
rule and refusal unchanged. There is no "end of the narration" anchor in the
contract; the film spec's `lines.end(plus=…)` is a `spokenEnd` on a phrase
that ends the narration (its last words, or the whole narration), which the
Python side emits. Adding a dedicated form is not needed by any shot.

### D7. Sets

`paper` is today's model stage and refuses `code` (`Set paper has no source
panel: shot <s> (chapter <c>) has code; use paper-split or source-only`);
`paper-split` is today's split and needs `code` (`Set paper-split needs code:
shot <s> (chapter <c>)`); `source-only` is today's `layout: source-only` and
needs `code` likewise. Without `set`, a shot is `paper` without `code` and
`paper-split` with it. Any other value: `Unknown set: <v> (shot <s> in
chapter <c>); a set is paper, paper-split or source-only`. The schema types
`set` as a string, not an enum, so the refusal's wording is this one in both
runtimes.

### D8. Fades across chapters, and the literal `until`

`fadeIn` only on the film's first shot and `fadeOut` only on its last, across
chapters: `fadeIn is accepted only on the film's first shot: shot <s>
(chapter <c>)`, `fadeOut is accepted only on the film's last shot: shot <s>
(chapter <c>)`. These are static, so a document refused for them needs no take.
A literal `until` of zero or less is refused statically with D6.4's wording.
Duplicate chapter or shot ids are refused statically: `Duplicate chapter id:
<c>`, `Duplicate shot id: <s> (chapter <c>)`.

### D9. The schema and its validator

`schema/machinome-movie-0.1.json` (JSON Schema 2020-12) states the unresolved
document's field names, types, required fields and closed field lists. It is
closed at the top level, on chapters, shots, `simulation`, keys, cues,
entrances, typing and emphasis cues, transitions, fades, `output`, `model`,
cameras, source excerpts and stills/clips entries; `audio`, `style` and
`release` are closed to the fields the tool reads plus the editorial `label`
and `direction` on `audio` and `publish` on `release`; `credits` is an open
object, since the tool reads none of it and FORMAT.md does not enumerate it.
Required at the top level: `format`, `id`, `title`, `root`, `output`,
`model`, `audio`, `cameras`, `layers`, `evidence` and `chapters` (D14); on a
chapter `id`, `narration` and `shots`; on a shot `id`, `until`,
`simulation`, `camera`, `hiddenLayers`, `overlays` and `evidence`. Required
fields inside cues are left to the 0.4 rules, which name them.
Value rules (a set's name, easing names, ranges, the format string) are not
in the schema: they are refused by the semantic layers with one wording in
both runtimes. Chapter and shot ids match `^[a-z0-9-]+$`, the YAML shot-id
rule, because a chapter id names its take's file.

The contract allows a validator dependency. None is added: installing one
needs the network, and this worktree's `node_modules` is a link into the
primary checkout, which this cycle must not write. `src/schema.mjs` validates
the keywords the schema uses (`$ref` to `$defs`, `type` including `integer`
and `null`, `properties`, `required`, `additionalProperties` as `false` or a
schema, `items`, `anyOf`, `minItems`, `minLength`, `pattern`) and nothing
else; a test fails if the schema uses any other keyword, so the file cannot
silently outgrow the validator. Replacing it with a maintained validator
later is a reversible choice for the pilot. Its messages:

- `Unknown field: <name> (<path>)`, `Missing field: <name> (<path>)`,
- `Invalid movie document: <path> must be <type>`,
- `Invalid movie document: <path> must be one of: <titles>` (anyOf),
- `Invalid movie document: <path> must match <pattern>`, and length/count
  messages likewise,

where `<path>` is slash-separated from the root (`chapters/0/shots/1`), `/`
for the root.

### D10. The resolved document

`resolveMovie` returns the numeric episode: `format:
machinome-video-draft/0.4`, `movie: machinome-movie/0.1`, the document's
fields without `root` and `marks`, `output` with `durationSeconds`,
`chapters` as D2, `shots` resolved. Loading a document writes it, pretty
printed, to `<root>/_build/movie-resolved.json`. Every command that loads a
document therefore writes it before doing anything else with it: `check`,
`preview` and `render` as the contract says, and also `speech` and `build`,
which resolve after generating takes (D4). `fixtures/resolved/<name>.json`
is the same output for a fixture document and its takes.

### D11. Deviations from `docs/movie-document.md`

Each is recorded in the contract page under "Implementation notes":

1. **Picture view keys take anchors.** The contract's list of anchorable
   fields does not name `pictures[i].view[j].at`; the film's `still` shot ends
   its push at `lines.spoken("Explore", plus=-0.5)`, a view key. It takes a
   time anchor like the other shot-local times.
2. **No validator dependency** (D9).
3. **`speech` and `build` write the resolved file too** (D10), since they
   resolve after generating the takes.
4. **Chapter and shot ids are slugs** (D9), a rule the contract leaves to
   format 0.4 for shots and does not state for chapters.
5. **Whole-frame duration tolerance** (D12).

### D12. A whole number of frames, in floating point

A resolved end is `k / fps`, and `(k / fps) × fps` is not always `k` in
floating point (`31 / 30 × 30` is `31.000000000000004`). The whole-frame test
of `validateEpisode` and the frame count of `outputShotUnits` accept a
product within 1e-6 of an integer and use the rounded count. Every duration
that passed before gives the same count; only values that differ from an
integer by rounding error newly pass.

### D13. Tests and fixtures

Timeline (pure, `test/movie-document.test.mjs`): the schema's keywords are
the validator's; every manifest document validates, resolves against its
takes to exactly `fixtures/resolved/<name>.json`, resolves twice to the same
result, and snaps every resolved anchor to the frame grid; every invalid
fixture is refused with each `must_mention` substring; anchor arithmetic,
`plus`, marks, picture view keys, sets, the missing take, a phrase the take
lacks, an anchor outside its shot, an anchored `until` at or before the start,
word timing from the chapter take at its offset.

Pipeline (`test/movie-pipeline.test.mjs`, Chromium, FFmpeg, the viewer
double moved from `test/render.test.mjs` into `test/viewer-double.mjs`): the
fixture project (`test/project-fixture.mjs`: one deterministic commit, so a
document pins its revision literally); the two-chapter document is refused
before its takes exist, then loads with the fixture takes installed, writes
`movie-resolved.json` equal to the pinned resolution, runs `speech` without
generating (one take per chapter, captions at chapter offsets), `preview` and
`render` at the document's size and rate (frames, dimensions, audio stream,
the SRT); `fetch` is replaced by a function that fails the test, and the
environment carries no key. The YAML identity test loads a three-shot 0.4
YAML episode of the same project and asserts, literally as computed on the
base commit before any source change, the take file names, the speech
records, the captions, the word timing and every output frame's `frameAt`
request (a SHA-256 of all 70, and five whole frames). Frame requests are
what the page draws from, and the page is unchanged, so equal requests are
equal pictures; PNG hashes are not pinned because they depend on the
machine's fonts and renderer, which the suite does not control.

No test is memoized: the new pipeline test renders about 90 frames at
320×180 and 10 fps and is well under the slowest existing test.

### D14. What a document may leave out

Following the orchestrator's review of the Python side's design (30 September
2026): a shot may omit `direction` (the resolved shot carries `""`, since the
0.4 validator requires a string); shot `evidence` may be `[]`; `style`,
`credits` and `release` may be absent from a document, while the top-level
`evidence` map is always present. The resolved episode carries `style: {}`
when the document has none, so the film page and the 0.4 defaults read it as
today (a default colour that must come from `style` is then refused by the
existing 0.4 rules). A render of a source without `release.descriptionTemplate`
writes no `description.md`, says so, and records `releaseReady: false`,
instead of failing on a missing template after the film is encoded; a YAML
episode always has one, so nothing changes for it.

## Risks / Trade-offs

- A document's resolved duration is on its own frame grid, not necessarily
  on another rate's: `render --fps 10` of a 30 fps document whose end is
  `k / 30` with `k` not a multiple of 3 is refused (`Frame count is not
  integral`), as a YAML episode's non-integral duration is today. The quick
  silent look at a lower rate therefore does not always work for a movie.
  Padding the film's end or snapping to a common grid would change the
  contract; the choice is the pilot's (Open Questions).
- Changing hashed modules (`words.mjs`, `code.mjs`, `pictures.mjs`,
  `render.mjs`, `shot-cache.mjs`) invalidates existing shot-cache generations
  once; the first render after this change is cold.
- A YAML episode's render manifest now records `chapters` inside `episode`;
  the review pack reads only the fields it read before.

## Open Questions

- The quick render at a lower frame rate (Risks, first item).
- Whether the schema validator should become a maintained dependency.

## Ratification

Ratification is the orchestrator's adversarial review after the report
(the campaign's gate under the pilot's delegation); integration of
`movie-document` into `declarative-python` is the pilot's.
