# Videomaker

Build narrated educational videos from a project's YAML screenplay, or the
movie document its declarations evaluate to, and its Machinome simulation. The first working consumer is Leonardo's hydraulic
sawmill: an 84-second rehearsal with scripted cameras, assembly reveals,
AI narration and aligned captions. The release-film source study adds real
Python typing beside the animation and expressive feminine narration.

This is a local production tool, not a publishing service. It films posed
models with a normalized animation timeline, and clocked machines through a
take: a movie declared in Python records a clocked machine's take (`Take`,
in [Declaring a movie in Python](docs/declaring-a-movie.md)), and the
commands film it, every frame posing on the viewer the bank the take gives
that instant, the viewer held to the recorded requests; running machines are
refused. The viewer executes the actual mechanical model.

Every frame is drawn by a React stage: a **set**, a template that owns the
whole screen, with **elements** in its slots (views of the model, source
panels, titles, pictures, or anything the project draws). A movie declared
by a project is drawn by the project's own template, its stage module
beside the movie; see [the stage](docs/stage.md). A YAML episode is drawn by
three sets the tool ships, which keep the film page every episode has had,
its layouts and its masthead. No film draws a progress indicator; showing a
viewer's place in a film is the player's job.

## Set up

Requires Node 22+, FFmpeg/ffprobe, and a Machinome Viewer API 21 bundle with
`setView` and on-demand rendering. Viewer API 27 is used by the release-film
study. Episodes in the draft format 0.3 that point at parts (`annotations`),
highlight them (`highlight`) or change field of view or up between cameras
need Viewer API 28, available in the machinome-viewer source checkout but not
yet declared by a published release; `check`, `preview` and `render` refuse them against an
older bundle. Format 0.4 needs no newer viewer than the cues it uses: easing
and transitions between shots run on Viewer API 21, and rings, being
annotations, need Viewer API 28 as annotations do. A movie on a clocked take
needs Viewer API 29, which mounts a clocked machine under on-demand
rendering and poses a restored bank; no published release declares it yet.
Text animation is page-only
and adds no viewer requirement. Stills and clips are page-only too; FFprobe
checks their frames and timestamps, while FFmpeg extracts clip frames for
preview and render. Linux/Chromium software rendering is the tested environment.

```sh
npm ci
npx playwright install chromium
```

Put the ElevenLabs key in this repository's ignored `.env`:

```dotenv
ELEVENLABS_API_KEY=your_key
```

The speech command takes the first key it finds: `ELEVENLABS_API_KEY` already
in the environment (even empty, which ends the search), then the `.env` of the
checkout it runs from, then, when that checkout is another work tree of the
repository, the `.env` of the repository's primary work tree. When it finds
none it names every place it looked, and it never prints a key.
The key is read only by the speech command and is never sent to the browser,
written into episode sources or included in build manifests. A key with text
to speech permission is enough; listing voices is not required when a voice ID
is supplied. The first episode uses George / `eleven_multilingual_v2`.
The source study uses Jessica / `eleven_v3` with lossless `pcm_24000` input.

## Produce an episode

A movie can also be declared in Python and evaluated to the movie document:
see [Declaring a movie in Python](docs/declaring-a-movie.md). The package that
does it, `machinome-movie`, lives in `python/` and is installed into the
workspace's Python environment with `pip install -e python`.

Every consuming project owns `videos/<episode-id>/episode.yaml` and
`production.yaml`. Read the screenplay directly: narration and plain-language
directions appear together in each shot. See [the source contract](docs/FORMAT.md).
In draft format 0.4, a shot with pinned `code` may opt into `layout: source-only`
to fill the existing main picture area with that literal, typed source instead
of the usual source/model split. Without the opt-in, both old layouts remain
unchanged. The film's current style and chrome remain; this is not a dark-theme
or multi-range source mode. Source-only refuses model-target annotations,
highlights and covering pictures rather than silently hiding them.

A project may give a movie document instead of a YAML episode: JSON data,
`machinome-movie/0.2`, usually written by the project's declarations to
`videos/<movie>/_build/movie.json`. See [the movie document](docs/movie-document.md).
Its shots place the chapter's elements in the slots of sets the project's
stage module draws ([the stage](docs/stage.md)).
Its narration belongs to chapters, one take each spanning several shots, and
its cuts, keys and cues may be anchored to spoken phrases and its model times
to named marks. Every command below accepts it in place of `episode.yaml`.
Run `speech` first: it generates one take per chapter from the narration
alone, and `check`, `preview` and `render` resolve the anchors from the cached
takes (refusing, naming the chapter, when one is missing) and write the
resolution to `_build/movie-resolved.json` under the document's `root`.
A movie's resolved length is on its own frame grid; render it at its own rate.
The stage module is bundled with the tool's stage runtime into
`_build/stage/` under the document's `root`: once per movie, again only when
the content of what it reads changes.

From this repository in the development workspace:

```sh
node bin/videomaker.mjs check ../projects/Leonardo/videos/hydraulic-sawmill/episode.yaml

node bin/videomaker.mjs speech ../projects/Leonardo/videos/hydraulic-sawmill/episode.yaml

node bin/videomaker.mjs preview ../projects/Leonardo/videos/hydraulic-sawmill/episode.yaml \
  --viewer ../machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js

node bin/videomaker.mjs render ../projects/Leonardo/videos/hydraulic-sawmill/episode.yaml \
  --viewer ../machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js

node bin/videomaker.mjs review ../projects/Leonardo/videos/hydraulic-sawmill/_build/rehearsal-manifest.json
```

- `check` validates YAML, timelines, named cameras/layers/evidence, the real model
  duration, and the export's source revision. After its summary line it prints
  one line per chapter from the cached takes, which is where a film's length
  comes from: `  drive: take 5.68 s, chapter 7.20 s, tail 1.32 s` (the take's
  measured length, the chapter's resolved length, and the tail after its
  speech offset and take), or `no cached take`. A movie on a clocked take
  adds one line, after the take's document checks and the replay of its
  steps against its recorded banks have passed:
  `Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s long; the replay of its steps gives the recorded bank at every mark`.
  For a 0.3 episode that needs
  Viewer API 28 it also reads the selected bundle's `viewer API` banner. An
  episode with spoken reveals or source emphasis needs its cached speech first:
  run `speech` before `check`. `check` reads the verified alignment but never
  generates speech. For format 0.4 pictures it also reads the project media,
  refuses unsafe or unfilmable assets, and prints each peak enlargement and
  allowance plus clip rate and dropped/repeated cadence. It bundles the stage
  (the tool's runtime and, for a movie, its stage modules), type-checks
  TypeScript modules against the types generated from the document, and
  prints the bundle it built or reused, with the hash of its script and of
  its stylesheet, so a change to either shows:
  `Stage: bundled <path>/stage.js (sha256 <prefix>) and stage.css (sha256 <prefix>) from stage.tsx; types checked`.
  When a movie shows a picture, it then measures, before reading any take,
  the layout of each set the movie uses in one headless Chromium served that
  bundle (no viewer is mounted and no `--viewer` is needed for it), prints a
  `Layout` line per set, refuses a picture enlarged beyond its allowance in
  its slot's measured box before `speech` is run, and, once the takes place
  the cues, a picture view that leaves the picture; a slot whose box depends
  on what it holds is left to `preview` and `render`. A YAML episode, whose
  paper sets' boxes are known, and a movie without pictures open no
  browser. It does not extract clip frames.
- `speech` generates narration through ElevenLabs, caches each segment and its
  character timestamps, checks it fits, then mixes audio and writes captions.
  It makes chargeable requests only for missing cached segments.
- `preview` creates three stills per shot, a midpoint for each typing cue, and
  a contact sheet. It also
  checks real-browser pixel replay, requested camera readback, visible canvas
  layout on model/split shots and positive fitted source visibility on source-only
  shots, without calling projection through a hidden canvas visible lens proof.
  Every check reads what the stage reports for each element it drew. It also checks
  invalid camera refusal. Annotated shots add stills at each arrow or label's
  start, quarters and end; every posed frame refuses an annotation whose part
  is off screen or whose text leaves the frame. Each highlight cue is posed
  with and without its cue and must change the pixels and restore them exactly.
  Each transition between shots (format 0.4) adds stills at its first frame,
  quarters, midpoint and last frame, and is proved in pixels against the plain
  pictures it is made of: a dissolve blends them within 2 levels, a wipe and a
  slide reproduce them exactly, a fade reaches exactly its colour, and a
  revisited instant replays exactly. A movie's reframe is proved live: every
  posed frame of it draws each moving view within a pixel of the box its
  frame gives and every other element at the join's progress as opacity;
  its first frame draws the view in its outgoing slot's box, its end at full
  progress is exactly the incoming frame, and its midpoint replays exactly.
  A movie on a clocked take first replays every step on the viewer's
  machine and refuses a request that differs from the recorded one, naming
  the step and the field; every posed frame then refuses a view whose
  machine holds another bank than its frame's, or at a mark than the take's.
  A ring (format 0.4) is refused on any
  frame where its part is not wholly on its view or the ring leaves the
  frame. Each annotation's entrance and exit adds stills at its first frame,
  midpoint and end while the cue is active, and is proved in pixels against the same instant with the
  mark drawn plainly and not drawn: a fade's midpoint is the blend its easing
  predicts within 2 levels, a draw-on's midpoint shows part of its stroke and
  not the rest, an entrance starts from nothing, its end and an exit's start
  are the mark drawn plainly, and a half-drawn instant replays exactly. No
  speech generation occurs. Format 0.4 text animation also reports
  `revealChecks`, `fadeChecks` and `emphasisChecks`: it verifies drawn word
  counts, same-instant title fade states over the moving model, source marks,
  title bounds and exact replay. Its `pictureChecks` save keyed still views and
  clip frames, verify page geometry and source frame identity, replay a visible
  still/clip exactly, and compare picture fades at the same model instant.
- `render` requires cached speech and renders the film. Add
  `--width 960 --fps 10 --silent` for a quick silent video. Measured text still
  requires the cached take with `--silent`; neither render
  nor silent build purchases speech. An FPS override that skips a revealed word
  is refused. A frame inside a transition is composed from captures of the same instant: a fade costs one
  pose and capture, a dissolve, wipe or slide two, each several times a plain
  frame's time; a reframe's frame is posed live, but waits each time for the
  view's canvas to fill its moving box. A picture with `n` simultaneous partly faded annotations needs
  `2^n` same-instant captures to preserve exact text pixels; schedule review
  renders accordingly. Picture fades similarly compose opaque and absent
  same-instant captures. `render --width` rechecks any authored `upscale`
  allowance before opening the browser.
- `build` combines speech generation/cache reuse and final rendering.
- `review` uses only a compatible published manifest and its hash-matching MP4;
  it never reopens the episode, model, speech, viewer or browser. A render
  attempts this encoded-film pack automatically after the film is published.
  If pack generation fails, the film still succeeds and prints a distinct
  warning with this standalone retry command. Older manifests without a
  recorded review plan need a rerender before automatic event review.

`check`, `preview` and `render` each print what they know of the two Git
trees a render names the heads of, the project's and Videomaker's own:
`Project tree: clean at <head>`, or, when Git lists a changed tracked file
or an untracked file it does not ignore,
`Project tree: dirty at render, 1 path differs from its head <head> (notes.txt); the manifest's projectHead is not the content rendered, and the film is not release-ready`,
and the same for `Videomaker tree`. `preview` and `render` read both trees
once, before the first frame. Nothing is refused: a dirty tree still makes
a rehearsal, and the records say it was dirty.

Without `--viewer`, the bundle beside the model manifest is used. Older
exports must be regenerated with the new viewer or use the explicit bundle.
Paths are arguments, not assumptions about a neighboring workspace. The
loopback asset server exposes the export's manifest and the files the viewer
reads from it (each part's `model` and each marking's under the manifest's
`root`, nothing else: the piece inventory's source files are provenance and
are neither served nor opened), the film page and, for format 0.4 pictures,
the referenced project media and extracted clip frames, and the movie's
stage bundle. A file the viewer reads that the export does not hold is
refused before a browser opens, naming its field in the manifest; export
the model again.

## Output

Each episode's ignored `_build/` contains:

- `rehearsal.mp4`: H.264 video and AAC narration, no burned or embedded subtitles.
- `rehearsal.srt`, `captions.srt` and `captions.json`: separate timed subtitles.
- `narration.wav` and `audio/`: mixed audio, cached segments and alignments.
- `thumbnail.png`, `storyboard.jpg`, `preview/`: presentation review assets.
- `description.md`: draft release copy with missing public URLs explicitly marked
  (not written for a movie document without `release.descriptionTemplate`).
- `movie-resolved.json` (a movie document only): the document with every anchor
  resolved to numbers, as the film is produced from it.
- `rehearsal-manifest.json`: resolved screenplay/settings, model and viewer
  hashes, the stage bundle's `stageSha256` and `stageCssSha256`, the
  project's and Videomaker's heads (`projectHead`, `workflowHead`), each
  beside whether its tree was dirty (`projectDirty`, `workflowDirty`), audio
  hashes, browser/encoder versions, font record, encoded checks,
  picture provenance/cadence with `pictureReleaseIssues`, `releaseIssues`
  (every reason `releaseReady` is false, in words), and a versioned
  resolved visual-review sample plan. `preview/report.json` records the
  same heads and their dirt.
- `review-packs/<generation>/`: exact selected full-frame PNGs decoded from
  the published MP4, bounded overview/event sheets and an integrity-checked
  `index.json` with frame indices and actual encoded PTS. A complete index
  says `generated, not reviewed`; it is not an aesthetic, audio, rights or
  publication approval. Old complete generations are preserved.
- `clips/<content-hash>/`: lossless extracted source frames and their index;
  unchanged source files and decoder settings reuse an extraction.
- `shot-cache/shot-v1/`: complete, integrity-checked shot generations, plus
  assembled global-frame sequences for encoding. A first render captures every
  shot. Later renders reuse complete shots whose actual frame requests and
  reached visual inputs are unchanged; a changed shot and a following shot
  that composites it as outgoing may be recaptured. The manifest's `cache`
  record lists each shot's key, generation, originating capture and frame
  counts. A hit verifies every PNG's hash and dimensions before reuse. An
  interrupted or damaged shot is recaptured whole, while other completed shots
  remain reusable. Old `frames/<content-hash>/` directories are left untouched
  but are not imported into this cache.

The shared cache key includes the mounted first frame, so changing the first
shot can conservatively recapture all shots. It also includes the model, viewer,
film page, stage bundle (so a changed template recaptures every shot, and
the same template bundled from another checkout of the tool does not, since
the bundle names its files by the tool and the project, never by the
machine's paths), rendering code, browser, the known regular/bold film and mono font
faces in the tested environment, style, dimensions, FPS and duration; whether
a Git tree was dirty is provenance, not a key, so a dirty tree reuses the
frames of a clean one and the reverse. Only
media actually reached by a shot enters that shot's key;
unused stills/clips and release copy do not force a visual recapture. Captions
remain external, so SRT/audio-only changes reuse PNGs and produce a fresh MP4.
The output manifest is authoritative only when its `outputSha256` matches the
MP4 at `output`; a publication interrupted between those two paths leaves a
visible hash mismatch and a recoverable prior film at
`<label>.mp4.previous-<id>`. Preflight and measured-take checks rerun on
every render; a reused shot inherits its frame-level browser pose checks from
its identical-input, attested capture.

The final encode is checked for its frame count, dimensions and audio stream.
Generated media stays out of Git. Missing public URLs make `releaseReady`
false but do not prevent a rehearsal. Nothing uploads or publishes.
Shown pictures whose credit or rights are unresolved, whose files are not
committed, or whose description template lacks `{{pictureCredits}}` also make
`releaseReady` false. The placeholder expands to `name: credit` lines (with
an explicit pending marker for missing credit); it is not a rights judgement.
A film rendered while the project's tree or Videomaker's was dirty is not
release-ready either: its heads are not what made it. Each reason is a line
of the manifest's `releaseIssues`, and `releaseReady` is true exactly when
that list is empty.

## Timing and revisions

Model seconds are independent of video seconds. Linear spans or explicit model
keyframes can slow a mechanism or align a stroke with a word. In format 0.4 a
model keyframe or a camera key can name an easing curve (`linear`, `smooth`,
`in`, `out`, `in-out`) for the segment that ends at it, so a mechanism can leave
a hold gently or settle into a pause while every key stays exact. The sawmill's
completed pass is 296 seconds; the 84-second film uses seconds 8–80.
That was the first rehearsal export; the current release-film export records
1460 seconds. Production always verifies the selected manifest's duration.

If speech overruns a shot, the command stops after caching it and names the
needed duration. Edit YAML timing and cues, then rerun. Audio is never truncated
or silently stretched. Cached segments are keyed by voice/model, text, neighbor
text, voice settings and pronunciation replacements; editing narration may
regenerate adjacent segments to preserve delivery continuity.

The narrator says “mah-SHEEN-ohm,” as confirmed by the pilot. The episode uses
a speech alias while keeping “Machinome” in captions. Beat timestamps come
from actual synthesized speech, not estimated reading speed.

## Validation and boundaries

`npm test` runs the Node suite under vitest: the pure tests under `test/`
(parsing refusals, stale model duration, timeline continuity, camera
interpolation, visibility reset, model keyframes, speech timestamps, the
movie document, the generated stage types) and the stage's component tests
beside its sources (`stage/**/*.test.tsx`, under jsdom) in parallel, then the
browser tests (`test/browser/`) and the pipeline tests (`test/pipeline/`) one
at a time on one headless Chromium. A slow test that passed is remembered in
one memo the repository's worktrees share, `videomaker-test-memo/` beside the
common Git directory (`git rev-parse --git-common-dir`), under the content of
everything it can reach (the modules it imports, what they serve and read,
the test helpers) and the versions of Node, Chromium, FFmpeg, Git and the
fonts; while none of that changes, the next run, in any worktree, reports it
as "passed from the memo" instead of running it. `npm test -- --cold` runs
everything and leaves the memo alone; run it before a change integrates.
With `VIDEOMAKER_VIEWER_BUNDLE=/path/to/machinome-viewer.js npm test` the
suite also runs the viewer layer (`test/viewer/`) against that real
machinome-viewer bundle; without it those tests are reported skipped, "no
viewer bundle selected". The Python package's suite is `python -m pytest` in
`python/`.
The originating sawmill's browser preview exercises the real viewer and pixels.
See [production evidence](docs/first-rehearsal.md) for the actual run.

Behavioral changes use this repository's OpenSpec records. The inaugural
[`first-narrated-rehearsal`](openspec/changes/archive/2026-09-29-first-narrated-rehearsal/proposal.md)
change was adopted during implementation at the pilot's request. It records
what was already built and how it was verified, not prior spec-first approval.
Future behavioral changes start with a proposal before implementation.

Original CAD, evidence and video sources belong to each project repository.
The viewer's public API and tests belong to its separate repository. This
tool neither modifies mechanical geometry nor implements a second simulation.
No remote is configured. A distribution license for Videomaker itself remains
unselected; the Leonardo sources follow the gallery's AGPL-3.0-only license.
