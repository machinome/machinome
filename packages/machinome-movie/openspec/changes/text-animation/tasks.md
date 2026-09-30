## 0. Preconditions

- [ ] 0.1 Confirm the existing 29 September ratification under the pilot's
  delegation still covers the two reveal timings and their rules (D1–D3),
  cache-only measured timing and the
  refusal of a silent render without speech (D4), the title as an overlay position
  over the running model with fades, and the covering card left out (D5), the
  promoted emphasis rule and its new refusals (D6), the 0.4 closed lists (D7).
- [ ] 0.2 Applied on branch `film-motion` after `keyframes-and-easing`,
  `shot-transitions` and `graphic-overlays` (campaign order). Record the base commit
  in `evidence.md`. `src/easing.mjs` exists with `ease`; `graphic-overlays`
  ratified `enter`/`leave: {kind: fade, duration, ease?}` for titles.
- [ ] 0.3 Reuse suitable Leonardo speech takes where they fit. The ratified
  allowance also permits the `speech` command for one or two short narration
  shots in this feature's demo, so its spoken reveal can be checked against a
  real take. `check`, `preview` and `render`, including silent render, remain
  cache-only and never purchase speech. No other campaign demo generates speech.

## 1. Red tests (written before any implementation; record each failure)

- [ ] 1.1 `test/words.test.mjs` (new, Node only; fails to load before 2.1).
  - Word split: `"Propose. Inspect. Correct."` gives three words and two separators;
    a `|-` text keeps its newline as a separator; joining words and separators gives
    the text back exactly.
  - Spoken onsets from a fixture alignment (characters of `"Intro. Propose. Inspect.
    Correct. Outro."`, start `i/10`, end `(i+1)/10`, offset 0.2): each onset equals
    `0.2 + index/10` of the word's first letter; phrase given explicitly with the
    displayed text in capitals; a replacement `Machinome → machine-ohm` times
    "Machinome" at `machine-ohm`'s first letter; a leading quote is skipped to the
    first letter.
  - Refusals, each naming the word or phrase: phrase absent from the written
    narration; present twice; spoken form absent from the alignment (a normalized
    alignment that reads "48.0" as words); present twice; displayed and phrase words
    differ (`Inspect.` against `it.`); different counts; a punctuation-only word
    (`·`); a replacement spanning two words; alignment arrays of unequal length,
    non-finite, negative or decreasing times; equal onsets for two words; a word
    spoken more than a frame before `from`; one spoken less than a frame before
    `from` appears at `from`; a word that appears on no global output frame before
    `to`, including fractional shot and cue starts that are not multiples of `1/fps`.
  - Even counts: three words over 2.4 s `linear` show 1, 1, 2, 2, 3, 3 at
    `0, 0.79, 0.81, 1.59, 1.61, 2.4` s after `from` (away from the exact thresholds,
    where floating point decides the frame); `in` delays the second word past its
    linear instant; after the span every word shows; `ease` clamps so a local time
    past `to` (a transition's continued cue) shows every word.
  - Fade opacity: `enter` gives exactly 0 at `from` and 1 at `from + duration`,
    `ease(name, u)` between; `leave` gives 1 at `to − duration` and stays 0 past `to`.
- [ ] 1.2 `test/words.test.mjs`, emphasis: port the three cases of
  `experiments/dark-source/emphasis.test.mjs` to the stable function with the same
  fixture (literal source-token offsets; onset `index/10 + offset`; cumulative active
  words at each onset; nothing at the clear instant; half-open at the first onset;
  refusals for a wrong line, a misspelled word, an unspoken phrase, the ambiguous
  phrase `the`, an invalid alignment). Add: a non-identifier word (`48.0`),
  duplicate words, words out of spoken order, `line` outside the snippet, a word not
  yet typed at its onset, a clear instant past the shot's end, two overlapping cues.
  Pin source text containing `<`, `&` and quotes through emphasis rendering so
  marks preserve the characters and HTML escaping. The experiment's own tests
  stay unchanged and green.
- [ ] 1.3 `test/text-animation.test.mjs` (new, Node only).
  - A 0.4 fixture with a spoken reveal (resolved from a fixture alignment), an even
    reveal, a title with `subtitle`, `enter` and `leave`, and a code shot with
    `emphasis` validates; `frameAt` gives the expected `shown`, `opacity` and
    emphasis ranges at chosen instants; a spoken reveal whose timing was not resolved
    throws `Word timing is not resolved`.
  - Refusals, each naming the shot: every new field and `position: title` in a 0.3
    and in a 0.2 episode (`Text animation needs format machinome-video-draft/0.4`);
    in 0.4 unknown overlay, reveal (including a field of the other timing),
    entrance, exit, code, typing cue and emphasis fields; `subtitle`, `enter` or `leave` on a
    non-title; `kind` other than `fade`; non-positive durations; fades longer than the
    cue together; overlapping titles; an even span past `to`; an easing name outside
    the vocabulary.
  - The same unknown overlay and code fields in a 0.3 episode are still accepted.
  - 0.2 and 0.3 frames unchanged: the existing pins stay green, plus a 0.3 fixture
    with active `top`, `lower-third` and `center` overlays and a typing code shot,
    pinned literally on the base commit; a 0.4 copy without the new fields gives the
    frames the earlier 0.4 cycles pinned.
  - `requiredViewerApi` of a 0.4 episode that only animates text is
    `{api: 21, reasons: []}`.
- [ ] 1.4 `test/speech.test.mjs`: the cache-only reader returns the cached alignment
  and SHA-256 with `ELEVENLABS_API_KEY` unset and `globalThis.fetch` replaced by a
  function that throws; a missing take is refused with `Word timing needs cached
  speech for shot hook; run the speech command first`; a checksum mismatch is refused;
  `speech` (cached, no generation) refuses a phrase absent from the take after
  writing captions, leaving the take in place.
- [ ] 1.5 `test/render.test.mjs` (real browser, viewer double, one browser at a time).
  A 0.4 episode whose `_build/audio` holds a fixture take under the key `speech`
  computes (arbitrary bytes, a matching record and fixture alignment):
  - `preview` passes with exact pixel replay; `revealChecks` for the spoken reveal
    report 1, 2 and 3 words drawn at its start, midpoint and end, and the even reveal
    the counts of its rule; start and end captures differ.
  - `fadeChecks`: the title's first entrance frame is pixel-identical to the same
    instant posed without it; its entrance midpoint differs from both that capture
    and the full title at the same model and video instant. Use a moving model in
    the fixture; assert the title absent/full/composed captures isolate title
    opacity from model motion at each checked instant, including exit start and
    midpoint.
  - `emphasisChecks`: no mark before the first onset, marks equal to the words at each
    onset, none at the clear instant, exact replay.
  - A page that draws a different word count (the timeline's count altered through
    `pose`'s override) is refused; a title long enough to leave the frame is refused
    with `Title leaves the frame`.
  - With the take removed, `preview` and a silent `render` refuse with
    `run the speech command first`; the same episode without measured cues previews
    and renders silently with no take.

## 2. Implementation

- [ ] 2.1 `src/words.mjs`: word split; spoken-phrase matching with replacements and
  folding (D2); onsets; even counts (D3); fade opacity (D5); emphasis resolution (D6,
  the experiment's rule plus the stable refusals); `resolveWordTiming(e, read)`
  producing `e.wordTiming` (D4). Uses `ease` from `src/easing.mjs`.
- [ ] 2.2 `src/speech.mjs`: one function computing a shot's cache key and paths, used
  by `speech` and by the new cache-only reader; `speech` resolves word timing after
  caching and refuses mismatches with the audio kept.
- [ ] 2.3 `src/episode.mjs`: 0.4 overlay, reveal, fade, title, `code`, typing-cue and
  emphasis validation with closed lists and the D7 messages; the format refusal in 0.2
  and 0.3; the static phrase checks; after `loadSourceCode` in `loadEpisode`, the
  emphasis source-token checks.
- [ ] 2.4 `src/timeline.mjs` and `src/code.mjs`: 0.4 overlay frames with words,
  `shown` and `opacity` only where declared; `codeAt` returns `emphasis` ranges only
  where declared; 0.2/0.3 frames untouched.
- [ ] 2.5 `src/film.html`, `src/film.js`: words drawn in place with hidden ones
  invisible; the `title` position with its subtitle; opacity; `mark.spoken` over the
  highlighted source, refusing a range whose text is not its word while preserving
  source characters and HTML escaping; `setFrame` returns per overlay the visible
  word count and box.
- [ ] 2.6 `src/render.mjs`: per-frame word-count and title-in-frame refusals; the
  preview samples and `revealChecks`, `fadeChecks`, `emphasisChecks` (D8); the frame
  identity adds `words.mjs` (D9).
- [ ] 2.7 `bin/videomaker.mjs`: resolve word timing before `check`, `preview`,
  `render` (silent included) and after generation in `build`; never for `speech`'s
  own validation.
- [ ] 2.8 `docs/FORMAT.md`: in "Format 0.4", the overlay and code closed lists and
  the new fields' format refusal; a section "Text animation" with "Words that appear
  as they are spoken" (D1–D2, the judgment example, the refusals, "run speech
  first"), "Words at an even pace" (D3), "Titles" (D5, the two *Revolutions*
  examples, the model beneath, fades), "Source words lit as they are spoken" (D6);
  "Timing and rendering semantics": positions include `title` in 0.4; "Actual Python
  beside the animation": emphasis beside typing; "Optional subtitles": still no
  burned captions. `README.md`: "Produce an episode" (`speech` before `check` for
  measured timing; `render --silent` reads cached speech for it), `preview`'s new
  checks.
- [ ] 2.9 `npm test` green; record the red runs of 1.1–1.5, the pins green before and
  after, and the green run in `evidence.md`.

## 3. Consumer verification (implementation evidence)

- [ ] 3.1 In the Leonardo project, untracked (never committed there, never here),
  make one concise format-0.4 episode at `videos/demo-text-animation/`, initially
  two shots of about eight seconds each, adjusting durations to the measured
  narration. Across those two shots, show a large title with subtitle fading
  over the moving model, an even reveal such as "Pause. Inspect. Test.",
  "Propose. Inspect. Correct." appearing at its measured spoken onsets, and
  the source emphasis of 3.2. This is a feature demonstration;
  it need not reconstruct the unrelated *Revolutions* `river`, `judgment`,
  `corrections` and `now` shots or their neighbouring cache keys.
- [ ] 3.2 In a code shot, show an export-pinned `model.py` excerpt including
  line 415, such as 405–415, and give `code.emphasis` the words `waterwheel`,
  `drives`, `crankshaft` on the actual matching phrase in that shot's narration
  and cached take. The short demo may say "The waterwheel drives the
  crankshaft."; the earlier cached study says "Here, the waterwheel drives the
  crankshaft." The current export revision has
  `water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)` at line 415;
  confirm the selected revision again before rendering and complete typing
  before those words are spoken. Prefer a fitting existing cached take, but do
  not force the original script or its neighbouring shots to preserve one. The
  ratified allowance permits `speech` for this demo's one or two short shots;
  record the exact selected phrase, cache keys, take hashes, onsets and source
  revision in evidence.
- [ ] 3.3 `check` passes after the takes are in place and refuses (with "run the
  speech command first") before; the resolved onsets of every measured cue, the take
  hashes and the even-reveal instants are recorded in `evidence.md`. `preview` passes
  with its reveal, fade and emphasis checks and exact replay.
- [ ] 3.4 With one viewer bundle, the root-owned
  `videos/demo-legacy-02` episode (format 0.2, current 1460-second export pinned
  to revision `28b43bc`), `demo-feed-mechanism` (0.3) and the earlier campaign
  demos pass `check` without reading speech. The orchestrating agent compares
  this 0.2 fixture's preview still hashes on detached pre-overlay `6417f97`
  and after this cycle, recording their byte identity. Record separately that
  the unchanged historic `videos/hydraulic-sawmill` refuses because it expects
  296 model seconds, and `videos/machinome-revolutions` refuses because its
  source revision is not pinned; neither original is a rendering compatibility
  fixture.
- [ ] 3.5 The orchestrating agent renders the short demo with its cached
  narration (`--width 960 --fps 30`) and records its hash; confirm on decoded
  frames that "Propose. Inspect. Correct." appears at the measured frames and
  the line-415 identifiers light at their measured onsets. A silent quick
  render may be used first, but the film review includes the narrated result.

## 4. Delegated film review and archive gate

- [ ] 4.1 After implementation tests pass, the orchestrating agent performs an
  adversarial review against the plan and rendered pixels. Inspect the spoken
  reveal against the actual voice, the even reveal's pace, title size and fades,
  and source emphasis on a light palette. Record the findings and fixes; do not
  claim pilot review from automated counts, opacity and replay checks.
- [ ] 4.2 The orchestrating agent inspects the feature demonstration video from
  Leonardo `videos/demo-text-animation/` with vision,
  records its path, hash and review findings, then syncs and archives this change.
  A covering title card, adoption by *Revolutions* and pronunciation-dictionary
  support remain separate pilot decisions or changes. Publication and pushing
  remain outside this campaign.
