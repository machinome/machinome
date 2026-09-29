## Context

- A frame is a pure function of video time: `frameAt(e, t, captions)` in
  `src/timeline.mjs` returns, among other things, `overlays` (the shot's overlay
  objects whose half-open `[from, to)` contains the shot-local time, as authored)
  and `code` (`codeAt`: typed text, highlighted HTML, cursor). `film.js` rebuilds
  `#overlays` from scratch every frame (one `div.overlay.<position>` per cue, with
  `white-space: pre-line`) and sets `#source-code`'s HTML. Positions are `top`,
  `lower-third`, `center`; only `lower-third` has a background plate.
- `frameAt` receives `captions` and ignores them. Captions are grouped cues of up
  to 56 characters with the written spelling restored from `audio.replacements`;
  they carry no per-word or per-character times.
- `speech(e, {generate})` keys each shot's take by
  `hash({voice, request, format})`, where `request` holds the spoken text (after
  `audio.replacements`), the model, voice settings, seed and, for models other than
  `eleven_v3`, the neighbouring shots' spoken text. The take and its record are
  `_build/audio/<shot>-<key16>.{mp3|wav}` and `.json`; the record holds the
  `alignment` (`characters`, `character_start_times_seconds`,
  `character_end_times_seconds`; the provider's normalized alignment when it gives
  one) and the audio's SHA-256. With `generate: false`, a missing take is refused
  ("Missing speech for <shot>; run the speech command first") and nothing is
  requested. The take is mixed at video time `start + (speechOffset ?? 0.2)`.
- `bin/videomaker.mjs`: `check` validates and, for API 28 episodes, reads the
  bundle banner; `preview` passes no captions; `render` calls
  `speech(e, {generate: false})` unless `--silent`; `build` generates, then renders.
- `experiments/dark-source/emphasis.mjs` (`resolveEmphasis`, `activeEmphasis`)
  proved source-word emphasis on a fixed, fully shown excerpt: the spoken `phrase`
  must occur exactly once in the joined alignment characters; each word must be an
  identifier, unique in the list, found exactly once as a whole word (`\b`) in the
  phrase and exactly once in the one source `line`; a word's highlight starts at
  `offset + start time` of its first spoken character, all highlights end together
  at `offset + end time` of the phrase's last character `+ holdSeconds`; words must
  follow narration order strictly; the alignment is refused unless its three arrays
  have equal length, every time is finite and non-negative, each end is at least its
  start, and starts never decrease. The page wraps each word's character range in
  `mark.spoken` and refuses a range whose text is not the word.
- Measured facts from the Leonardo speech cache (read-only): in *Revolutions*
  `judgment` (default speech offset 0.2 s), "Propose." starts at 3.532 s, "Inspect."
  at 4.716 s and "Correct." at 5.703 s shot-local; the overlay today appears at
  1.933 s. In `genome`, "Pause" starts at 6.899 s, exactly where its overlay begins:
  authors already align text to measured onsets by hand. The syntax study's approved
  take (IPA pronunciation, imported by `prepare-audio.mjs` under a name of its own)
  puts `waterwheel`, `drives`, `crankshaft` at 11.910, 12.540 and 13.110 s.
- `keyframes-and-easing` (ratified) provides `ease(name, u)` over `linear`,
  `smooth`, `in`, `out`, `in-out`, format 0.4, and closed field lists for shots,
  `simulation`, model keyframes and camera keys; overlay cues and `code` are not yet
  closed. `shot-transitions` (ratified) continues an outgoing shot's cues that run
  to its end through a transition, at shot-local times past the shot's duration.

## Goals / Non-Goals

Let an author make an overlay's words appear as the narrator says them, or at an
even pace; set a title with a line beneath it over the model and let it fade in and
out; light source words as they are spoken, as the syntax study did; keep every
frame a function of video time, the episode and the speech cache; never purchase
speech outside the `speech` command; keep 0.2 and 0.3 frames bit-exact. Not goals:
burned captions, covering cards, letter-level animation, fades on other overlays,
viewer changes (see Non-goals in the proposal and D10).

## Decisions

### D1. `reveal` on an overlay, and what "a word" is

```yaml
# format machinome-video-draft/0.4 — Revolutions judgment and genome, restaged
    overlays:
      - from: 3.5
        to: 6.767
        text: Propose. Inspect. Correct.
        position: top
        reveal: {timing: spoken}
      - from: 6.899
        to: 12.5
        text: Pause. Inspect. Test.
        position: top
        reveal: {timing: even, duration: 2.4}
```

- `reveal` is a mapping with `timing: spoken` (D2) or `timing: even` (D3). It is
  accepted on every overlay position, `title` included (where it applies to `text`,
  not to `subtitle`).
- The words of `text` are its maximal runs of non-whitespace characters, in order;
  the whitespace between them (spaces and the newlines of a `|-` block) is kept as
  written. `Propose. Inspect. Correct.` has three words.
- At each instant the timeline says how many words are shown, `k`: the first `k`
  words are drawn and the rest are drawn invisible in their place (the page sets
  `visibility: hidden` on them), so line breaks, centring and a lower third's plate
  are those of the whole text from the cue's first frame, and nothing reflows as
  words arrive. A lower third's plate is therefore visible, empty, until its first
  word; an author who does not want that starts the cue at the first word.
- A word, once shown, stays until the cue ends. There is no per-word fade: the
  experiment's emphasis switched on in one frame and read well; a softer arrival is
  a later change if the pilot asks for it after the demo.

### D2. Spoken timing: the experiment's rule, applied to an overlay's words

`reveal: {timing: spoken, phrase?}`. The overlay's words appear as the shot's own
narration speaks them.

- **The phrase.** `phrase` is a passage of this shot's narration, written as it is
  written there; it defaults to the overlay's `text`. It must occur exactly once in
  the shot's written `narration` (checked without any audio), and its spoken form
  exactly once in the characters of the shot's cached alignment. The spoken form is
  the phrase with `audio.replacements` applied, as the `speech` command applies them
  to the narration. Unambiguous or refused, as in the experiment: `the` is refused
  because it is spoken many times.
- **Pairing words.** The overlay's words are paired one to one, in order, with the
  phrase's words. Each pair must be equal after lowercasing and removing leading and
  trailing punctuation (Unicode class P); otherwise the reveal is refused, naming the
  first pair that differs. So `phrase` exists only to let the displayed text differ
  from the spoken in case and punctuation: `text: PROPOSE · INSPECT · CORRECT` is
  refused (the `·` tokens are not spoken), `text: "PROPOSE. INSPECT. CORRECT."` with
  `phrase: Propose. Inspect. Correct.` is accepted. A word that is all punctuation
  cannot be spoken and is refused. `genome`'s "Pause. Inspect. Test." against "Pause
  it. Look inside. Test a connection." is refused (`Inspect.` is not `it.`); that
  overlay uses an even reveal instead.
- **Replacements.** Each written word's spoken piece is that word with the
  replacements applied; the pieces joined with the phrase's own separators must equal
  the spoken form of the whole phrase, which fails only when a replacement term spans
  two words, and is then refused (a word would have no spoken piece of its own).
  *Revolutions* speaks `Machinome` as `machine-ohm`; a displayed `Machinome` is timed
  at the onset of `machine-ohm`.
- **Onset.** A word's onset is `speechOffset` (default 0.2, the same offset the mix
  uses) plus the alignment start time of the first letter or digit of its spoken
  piece within the phrase's occurrence, in shot-local seconds. Character positions
  are counted as the experiment counts them (the joined alignment string, indexed by
  code point).
- **Order and fit.** Onsets must increase strictly (otherwise the alignment is
  refused as the experiment refuses it). A word spoken earlier than the cue's `from`
  by one output frame (`1/output.fps`) or more is refused: it would appear later than
  it is said. A word spoken less than one frame early appears at `from`. Every word
  must appear on at least one output frame before the cue's `to`; otherwise it is
  refused, naming the word.

Word `k` (1-based) is shown from its onset (or `from`, if later) to the cue's end.
For `judgment` above: nothing from 3.5 s (a `top` overlay has no plate), "Propose."
from 3.532 s, "Propose. Inspect." from 4.716 s, all three from 5.703 s to 6.767 s.

### D3. Even timing: an eased share for each word

`reveal: {timing: even, duration, ease?}`. The words appear across the first
`duration` seconds of the cue, `0 < duration`, `from + duration <= to`. `ease` is a
name from `keyframes-and-easing` (`ease(name, u)`), default `linear`: "even" means
an even pace unless the author names a curve. There is no smoothstep here today, so
the campaign's `smooth` default does not apply; `linear` says what the field's name
promises.

With `n` words and `p = ease(name, (local − from) / duration)` (clamped by `ease`),
the number shown is `k = min(n, floor(n · p) + 1)`: the first word appears with the
cue, each word owns an equal share of eased progress, and word `i` appears when `p`
reaches `(i − 1)/n`. After the span every word is shown. `genome` above: "Pause." at
6.899 s, "Inspect." at 7.699 s, "Test." at 8.499 s. The rule mirrors the typing
cue's count (`floor` of a share of progress) with the first word at the start,
because a reveal that shows nothing for its first share reads as a late cue.

`check` refuses a reveal in which some word would appear on no output frame before
`to` (a span too short for its words at the output frame rate appears as several
words per frame, which is allowed; only a word that never appears is refused).

### D4. Where measured onsets come from, and who may read them

Measured onsets come only from the speech cache, the same takes the film's audio is
mixed from. Nothing but `speech` and `build` ever calls the provider.

- **The reader.** `speech.mjs` gains a cache-only reader that computes a shot's
  cache key and path exactly as `speech` does (one shared function, so the two can
  never disagree), verifies the take's SHA-256 against its record, and returns the
  record's alignment and SHA-256. It never loads the API key. A missing take is
  refused: `Word timing needs cached speech for shot judgment; run the speech command
  first (check, preview and render never generate speech)`. Because the key contains
  the spoken text (and the neighbours' where the model uses them), a take for edited
  narration is simply missing: stale timing cannot be read.
- **Resolving.** `words.mjs` resolves every measured cue of the episode (spoken
  reveals, D2; emphasis, D6) from those alignments into plain numbers attached to the
  loaded episode, `e.wordTiming`: per shot, the take's SHA-256 and, per cue, its
  onsets (and, for emphasis, its character ranges and clear time). Only shots with a
  measured cue are read; an episode without one reads nothing and behaves as today.
  `frameAt` reads `e.wordTiming`; a spoken reveal without resolved timing throws
  (`Word timing is not resolved: shot judgment`) rather than showing all words.
- **Purity.** The resolved timing is a deterministic function of the episode and the
  cached take, so a frame is a function of its video time, the episode and the speech
  cache, as the campaign requires. The `captions` argument of `frameAt` stays unused:
  captions are grouped, spelling-restored and have no per-word times, so onsets
  cannot be recovered from them.
- **By command.**
  - `check`: the static rules need no audio (field lists, the phrase occurring once
    in the written narration, word pairing, identifiers and source tokens). If the
    episode has a measured cue, `check` then resolves it and refuses as above when a
    take is missing, so a passing `check` means the episode can be previewed and
    rendered. For a new episode the order is `speech`, then `check`.
  - `speech`: validates statically (as today, through `loadEpisode`), caches every
    take, then resolves the measured cues and refuses a mismatch with the words and
    shot named, after caching, as it already does for overruns ("audio is cached").
  - `preview` and `render`: resolve before opening the browser.
  - `render --silent` resolves from the cache too, and refuses when a take is
    missing. A silent render is a quick look at the same film without its sound
    track; revealing evenly instead would show words at instants the narrated film
    does not, and would look correct. The house rule is to refuse a film that cannot
    be drawn truthfully, not to draw a different one. A silent render of an episode
    without measured cues needs no speech, as today.
  - `build`: generates, then resolves, then renders.

### D5. Titles: an overlay position, over the running model

```yaml
# format machinome-video-draft/0.4 — Revolutions revolution and river, restaged
      - {from: 2.941, to: 8.5, position: title, text: REVOLUTIONS,
         enter: {kind: fade, duration: 1}}
      - from: 3.273
        to: 9
        position: title
        text: Leonardo's hydraulic sawmill
        subtitle: Digital reconstruction of a later museum interpretation
        enter: {kind: fade, duration: 0.6}
        leave: {kind: fade, duration: 0.6, ease: in}
```

- **A position, not a shot field.** A title is an overlay with `position: title`:
  it has `from`/`to` like any overlay, may start after the first sentence (as the
  *Revolutions* title does) and may have a reveal. A shot field would need its own
  timing rules and could not share a shot with the narration it follows.
- **Look.** `text` is set large and centred in the frame (about twice the size of a
  `top` overlay, weight 600), `subtitle` (optional, non-empty) beneath it at about the
  size of a `lower-third`, both in `style.foreground`, with no plate, above the
  model and the annotations like every overlay. Exact sizes are the implementer's and
  the pilot's review, in `vw` units as every overlay is. `subtitle` is accepted only on
  a title. Two titles of one shot may not overlap in time (they would be drawn on top
  of each other).
- **The model beneath.** Unchanged: posed, moving and visible as its shot says. A
  title adds nothing to the viewer's state, so the shot after it, or the rest of the
  shot, continues exactly as it would without it.
- **Fades.** `enter` and `leave` are `{kind: fade, duration, ease?}`, accepted on a
  title only, `duration > 0`, the two together no longer than the cue; `ease` defaults
  to `smooth`, the campaign's default for a transition-like curve. The title's
  opacity is `ease(enter.ease, (local − from)/enter.duration)` during the entrance,
  `1 − ease(leave.ease, (local − (to − leave.duration))/leave.duration)` during the
  exit and 1 between; `ease` clamps its argument, so an entrance starts at exactly 0
  (the first frame shows no title) and, when `shot-transitions` continues a title that
  runs to its shot's end past that end, a title that fades out stays faded out. The
  whole title (text and subtitle, shown or hidden words) takes the one opacity.
  `kind: fade` is the only kind. If `graphic-overlays`, applied before this change,
  ratifies a different spelling for entrances and exits, the title uses that spelling
  (one spelling in 0.4; Open Questions).
- **Refusal at the posed frame.** A title whose drawn box leaves the frame is refused
  in `preview` and `render`, naming the shot, the overlay and the time, as an
  annotation's text is (`Title leaves the frame: river #0 at 11.80 s`).
- **Left out: a card that covers the model.** No episode hides the model behind a
  title; *Revolutions* sets its titles over the moving wheel and the sawmill, and two
  of its directions refuse cards. Should an episode ask, the smallest addition is a
  title field `cover: true` that draws `style.background` over the model stage for the
  cue's interval (fading with the title), while the model stays posed beneath so that
  the frame after the card is the frame the shot would have shown; annotations and
  highlights would be refused while covered. It is not built now.

### D6. Source words lit as they are spoken: `code.emphasis`

```yaml
# format machinome-video-draft/0.4 — Revolutions v2 the-same-in-python (the syntax
# study's phrase is "Here, the waterwheel drives the crankshaft.")
    code:
      snippet: mill-class           # model.py lines 366–376
      typing:
        - {from: 0.4, to: 3, throughLine: 376}
      emphasis:
        - line: 376
          phrase: The waterwheel drives the crankshaft.
          words: [waterwheel, drives, crankshaft]
          hold: 0.9
```

The experiment's rule, unchanged in substance, on the stable code panel:

- `line` is an absolute source line inside the snippet's range; `phrase` a passage of
  the shot's narration (written; spoken through the replacements, found exactly once
  in the written narration and exactly once in the cached alignment, as D2); `words`
  a non-empty list of distinct identifiers (`^[A-Za-z_]\w*$`), each found exactly
  once as a whole word in the spoken phrase and exactly once in that line of the
  excerpt as shown (after the common indentation is removed); `hold` finite, `>= 0`.
- Word `i` is lit from its onset (`speechOffset` + the start time of its first
  spoken character, the experiment's `from`) until the phrase's last character ends
  plus `hold` (the experiment's `to`, one instant for all words); onsets must follow
  narration order strictly. The highlights accumulate and clear together, half-open.
- New refusals the stable panel needs: a word not yet typed at its onset (the typing
  cues decide what is on screen, and the experiment's excerpt was always complete);
  a clear instant after the shot's end; two emphasis cues of one shot whose intervals
  (first onset to clear) overlap; `line` outside the snippet. Source-token checks run
  when the episode is loaded, after the excerpt is read; timing checks when word
  timing is resolved (D4).
- `codeAt` returns, with the typed text, the active words and their character ranges
  in the displayed text. The page wraps each range of the highlighted HTML in
  `mark.spoken` after setting it, as the experiment did, and refuses a range whose
  text is not the word. The mark keeps the word's syntax colour and adds a tint of
  `style.accent` behind it and an accent underline, so the look follows the episode's
  palette (the experiment's colours were hand-picked for its dark palette).
- `experiments/dark-source/` is not modified or imported; its tests keep proving the
  experiment. The rule lives in `src/words.mjs`, and the stable tests port the
  experiment's cases (D8, tasks 1.2).

### D7. Format 0.4: fields, closed lists, older formats, frame shape

- New fields, accepted only in 0.4: `reveal`, `subtitle`, `enter`, `leave` on an
  overlay; `title` as an overlay position; `emphasis` in `code`. In 0.2 or 0.3 any of
  them is refused, naming the shot:
  `Text animation needs format machinome-video-draft/0.4: shot judgment`. Before this
  change a 0.3 episode with `reveal` would render with every word shown at once; the
  refusal replaces that. `position: title` in 0.2 or 0.3, refused today as
  `Invalid overlay`, gets the same format message.
- Closed lists in 0.4 (this is the first change of the campaign to touch overlays
  and code, so it closes them, per the `keyframes-and-easing` ratification):
  an overlay accepts `from, to, text, position, reveal, subtitle, enter, leave`;
  `reveal` accepts `timing` plus `phrase` (spoken) or `duration, ease` (even);
  `enter`/`leave` accept `kind, duration, ease`; `code` accepts
  `snippet, typing, emphasis`; a typing cue `from, to, throughLine`; an emphasis cue
  `line, phrase, words, hold`. Anything else is refused, naming the cue and shot:
  `Unknown overlay field: revael (overlay #0 in shot judgment)`,
  `Unknown reveal field: duration (overlay #0 in shot judgment)` for a field of the
  other timing, and likewise `Unknown fade field`, `Unknown code field`,
  `Unknown typing cue field`, `Unknown emphasis field`. 0.2 and 0.3 keep ignoring
  unknown overlay and code fields, so no existing episode can break. No shot field is
  added.
- Frames. 0.2 and 0.3 frames are untouched. In 0.4, an active overlay that declares
  none of the new fields is emitted exactly as today (the authored object), so a 0.4
  episode without text animation keeps the frames the earlier 0.4 cycles pinned. An
  overlay with `reveal` is emitted with its words and separators (split once, in
  Node, so the page never re-splits) and `shown`; a title with `enter` or `leave`
  with `opacity`. `code` gains `emphasis` only when the shot declares it.
- Viewer. Text animation is page-only; `requiredViewerApi` is unchanged, and a 0.4
  episode that only animates text needs Viewer API 21.

### D8. What `preview` proves

On every posed frame (`preview` and `render`), the page reports, per drawn overlay,
the words drawn visible and its box; `pose` refuses a count that differs from the
timeline's and a title box outside the frame.

`preview` adds, per shot:

- **Each reveal** at its start, midpoint and end: for `spoken`, the first word's
  appearance, the last word's, and halfway between; for `even`, `from`,
  `from + duration/2` and `from + duration` (the last output frame before `to` if
  that is later than the cue). The drawn counts must equal the rule's, must not
  decrease across the three, and the last must be all the words; for two or more
  words the start and end captures must differ in pixels. Reported as
  `revealChecks: [{shotId, index, timing, samples: [{time, shown, expected}]}]`.
- **Each title fade**: the entrance's first instant must be pixel-identical to the
  same instant posed with that title removed (opacity 0 reaches the pixels as
  nothing), and the entrance's midpoint must differ from both that capture and the
  capture after the entrance (the title is partly there). The same for an exit's
  midpoint against its start. Reported as `fadeChecks`.
- **Each emphasis cue**: just before its first onset (no marks), at every word's
  onset (the words so far, each mark's text equal to its word), and at its clear
  instant (no marks); re-posing the first onset after the clear reproduces its
  capture exactly. Reported as `emphasisChecks`.
- The existing samples (three per shot, typing midpoints, annotation and highlight
  instants) and the exact pixel-replay check are unchanged, and each new sample is
  also saved as a still for the contact sheet.

These checks prove what is drawn and that it replays; whether a reveal's pace, a
title's size or a fade reads well is the pilot's review.

### D9. Frame cache and provenance

The render identity already hashes the episode (which now carries `e.wordTiming`,
so a new take re-renders exactly the frames whose words move), the served page files,
`timeline.mjs` and `code.mjs`; it adds `src/words.mjs`. The build manifest records
the resolved episode, and so each measured cue's onsets and the SHA-256 of the take
they were read from.

### D10. What is left out, and why

- Burned-in captions: no episode is a Short or asks for them (proposal Non-goals).
- The covering card (D5).
- Fades on `top`, `center` and `lower-third` overlays: the evidence for a fade is a
  title that "arrives"; the other overlays of the drafts appear and cut with their
  beats (the sawmill's alternating CUT / ADVANCE).
- Letter-by-letter reveals and per-word fades: typing already reveals characters,
  and no episode asks for text to type itself outside the code panel.
- Emphasis timed evenly, of numbers or punctuation (`48.0`, `delta=0.01` in the v2
  draft's `test-class` shot), or of whole lines ("Emphasize the class header"): the
  commissioned emphasis is identifiers at measured onsets; these wait for a rendered
  shot that needs them.

## Risks / Trade-offs

- **The syntax study cannot yet be restaged as a stable episode with its approved
  take.** Its approved IPA-pronunciation take was imported by `prepare-audio.mjs`
  under its own file name; the stable cache key for its narration finds no take
  (the only keyed take speaks the older `Masheenome` spelling), because `speech` does
  not forward pronunciation dictionaries. D4 reads exactly the take the film is
  mixed from, so this change will not read the imported one. Restaging it with the
  approved voice needs a separate change to speech (dictionaries), outside this item.
  The consumer verification uses a take the stable cache already holds (tasks 3).
- **Onsets move when narration is regenerated.** By design; a reveal follows the
  words. The refusals (word before `from`, word after the cue's last frame) surface
  when a new take no longer fits the cue.
- **The provider's normalized alignment can differ from the written text** (numbers
  read as words). A phrase that is not in the cached characters is refused with the
  phrase named; choose a phrase spoken as written.
- **`check` now depends on cached speech** for episodes with measured cues, and an
  author must run `speech` first. That order is stated in the message and in
  FORMAT.md; the static checks still run first, so a typo is caught before any
  purchase.
- **Emphasis on the split-layout panel.** The syntax study and the v2 draft show
  source full screen; this change lights words in the existing panel (full-screen
  source is roadmap item 12). A code shot must still type its excerpt; a shot that
  wants the excerpt standing from the first frame types it in a short first cue.
- **Closed lists for overlays and code arrive with this cycle**, after
  `keyframes-and-easing`, `shot-transitions` and `graphic-overlays` opened 0.4. A 0.4
  episode with `reveal` run on a build of the branch before this cycle would render
  without its reveal. No 0.4 episode is released, and the campaign is applied in order
  on one branch, so the window is internal to the branch.
- **Readability of text over the running model** without a plate is a review matter,
  as `top` overlays are today.

## Migration Plan

Additive and opt-in by format 0.4 and the new fields. Every 0.2 and 0.3 episode,
and every 0.4 episode without the new fields, keeps its frames (pinned by test) and
needs no speech for `check`, `preview` or a silent render. Reverting the tool commit
makes an episode that uses the fields refused by its closed lists, never rendered
with its reveals missing.

## Open Questions

- **The entrance spelling** is shared with `graphic-overlays`, which is applied
  first. This design writes `enter`/`leave: {kind: fade, duration, ease}`; the
  implementation adopts whatever `graphic-overlays` ratified, so 0.4 has one spelling.
- **The covering card** (D5): left out for lack of an episode. The orchestrator or the
  pilot may name a shot and add `cover` at ratification; the semantics are written
  above.
- **The even reveal's evidence** is weaker than the spoken one's: it serves text that
  is not spoken as written (`genome`), and no draft names an even reveal. Kept because
  it is the only reveal such text can have, and it shares the machinery.
- **Title and emphasis looks** (sizes, the accent tint) are proposals for the pilot's
  review on the demo stills; they are page styles, not format.

## Ratification (29 September 2026)

Ratified by the orchestrating agent as the campaign's review gate, under the
pilot's delegation, with these resolutions:

- **No covering card** (D5): accepted; no episode asks. The `cover` semantics
  stay written here for the day one does.
- **The even reveal stays** (D3): it is the only reveal text not spoken as
  written can have.
- **Entrance and exit spelling** (D5): the implementation uses the spelling
  `graphic-overlays` ratifies, applied before this change, so 0.4 has one
  spelling; `graphic-overlays` ratified `enter`/`leave: {kind, duration, ease}`,
  so nothing changes here except the refusal wording, which becomes
  `Unknown entrance field: …` / `Unknown exit field: …` instead of
  `Unknown fade field`.
- **Speech for the demo.** The pilot's demo of this feature may run the
  `speech` command for its own short narration (one or two shots), so a
  spoken reveal is demonstrated on a real take; the cost is a few hundred
  characters. No other demo of the campaign generates speech.
- **`check` needing the cache** for measured cues, and `render --silent`
  refusing without it (D4): accepted as the truthful rule.
- 0.4 closed lists: this change closes overlay, `code`, typing and its own
  cue lists (D7), as the campaign note requires of the first cycle to touch
  overlays.
