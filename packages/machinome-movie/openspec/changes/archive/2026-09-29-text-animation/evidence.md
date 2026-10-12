# Text-animation implementation evidence

## Scope and base

The 29 September 2026 pilot-delegated ratification in `design.md` still covers
D1–D7. Implementation started on `film-motion` at
`ff85c4baf78cfcc62ceb36b6bb4cbdc56528af28`, after archived
`keyframes-and-easing`, `shot-transitions` and `graphic-overlays`. Planning-only
commit `b11287c6feda90049146ff3e0165ab5bd6559e38` arrived while this
implementation was in progress. `src/easing.mjs` and the graphic-overlay fade
spelling were present. No source, tests or documentation were committed here by
the implementation agent. The root owns sync, archive, commits, consumer media
and film review.

The Leonardo feature demo uses two 8-second shots in
`videos/demo-text-animation/`. The root used the ratified exception to generate
two short ElevenLabs v3/PCM takes through the standard `speech` command; no key
was exposed. `check`, `preview`, `render` and silent build read only these
cached takes. The source excerpt is export-pinned at line 415 of revision
`28b43bce` (the complete revision is in the project production record).

## Red and green tests

- `test/words.test.mjs` first failed to load (`ERR_MODULE_NOT_FOUND` for
  `src/words.mjs`). Its first implementation run exposed fixture timing and
  punctuation-only ordering errors; those were fixed. Later adversarial tests
  first failed for an exact one-frame-early onset, decreasing alignment end
  times, a replacement in an emphasis phrase, an astral source character
  before a token, and a fractional global onset; each now passes. The test
  covers the two reveal rules, fade ends, source offsets, late typing, cue
  overlap and effective render-fps refusal. A genuine lower-fps missing word
  is refused; two words arriving together on one frame are allowed.
- `test/speech.test.mjs` first failed for the absent `readSpeechTake` export.
  It now checks cache-only reading with no API key and a throwing network stub,
  missing and corrupt cache refusals, and a measured phrase mismatch after
  captions are written while the cached take is preserved.
- `test/text-animation.test.mjs` first failed all three initial validation and
  frame cases (`Invalid overlay` and missing format refusal). It now pins the
  literal 0.3 three-overlay/typed-Python frame; 0.4 plain frame shape; 0.4
  measured/even/title frames; format refusals; closed overlay, reveal, fade,
  code, typing and emphasis fields; title-only fields and overlap; and API 21
  for a text-only episode.
- `test/render.test.mjs` now exercises a moving-model browser double with
  measured/even reveals, same-instant title full/absent/composed captures,
  safely escaped `<`, `&` and quote source characters, source emphasis and
  exact replay. It checks the page's computed visible spans, wrong-count pose
  override, title overflow, and missing-cache preview/silent-render refusals.
  This browser test was added after the first implementation of the page,
  not before it; do not count its existence as a red-first run. Its refusal
  checks were extended in response to the root's review. The root accepted
  this explicit process exception under delegated review; final browser
  coverage passes, but the original red-first sequence is not backdated.
- Final implementation-wide `npm test`: **98/98 pass, 0 fail** (59.5 seconds).
  `git diff --check` passed. No pixel tolerance was widened.

## Cached speech and consumer preview

| Shot | Spoken request | Cache key | Take SHA-256 | Duration |
| --- | --- | --- | --- | --- |
| `judgment` | `Propose. Inspect. Correct.` | `0708d55748c01ff3a86e1d78a83c022e530a27798a39803843c3ce2015627650` | `f0b00e5e3acdcef08295d27034f5c0cd81e3741d74c6cc4ea007f3cb920fcc91` | 3.28 s |
| `source` | `The waterwheel drives the crankshaft.` | `72b6eea39321423a2b15a1215df86c712c05aa2eeb7d2abca830240c06b4cfb5` | `fbb90324145522ded0dde83554039c2063c5ac38141cdfa2c85d66f1c28373d8` | 2.24 s |

Before speech, the real demo's `check` refused with `Word timing needs cached
speech for shot judgment; run the speech command first`. After the root's
standard speech generation, `check` passed. Measured onsets in shot-local
seconds: `judgment` overlay `[3, 4, 5.63]`; `source` identifiers
`waterwheel 2.133`, `drives 2.72`, `crankshaft 3.347`, common clear `5.14`.
The even reveal shows 1, 2 and 3 words at local `0.4`, `1.3` and `2.2`.

An initial real Leonardo preview passed at width 960 after fixing global-time
subtraction at the first source onset. It saved 23 stills (including all
reveal/title/emphasis proof samples), reported 37 poses, two reveal checks,
five title-fade comparisons and one emphasis check with five samples, all
green. The root subsequently changed only the demo's `whole` camera for
title readability; the root's fresh preview and narrated render replace that
initial visual evidence. The source, audio requests and timing above did not
change.

## Compatibility and root gate

The root-owned current-export format-0.2 `demo-legacy-02` passes preview at
width 960. Its three numbered PNG hashes are exactly the three values in
`videos/demo-legacy-02/_build/legacy-6417f97.json` from detached
`6417f97`—**3/3 byte-identical**. The new literal Node 0.3 frame pin and
earlier 0.2/0.3 pins remain green. An attempt to preview 0.3
`demo-feed-mechanism` with the default beside-manifest Viewer API 27 bundle
correctly refused its API 28 cues; the root will run the pinned API 28 bundle
for the remaining legacy PNG comparison. The unchanged historic
`hydraulic-sawmill` and `machinome-revolutions` drafts remain invalid for
their pre-existing duration and source-revision pins and are not compatibility
consumers.

The root subsequently completed the camera-adjusted preview, narrated
960×540@30 video, decoded-frame vision review, adversarial review and remaining
32/32 API-28 legacy PNG comparisons. All pass; `root-review.md` contains the
video hash, exact before/after onset frame numbers, visual findings and closure
decision. The earlier API-27 attempt above is retained as provenance, not the
final compatibility result.
