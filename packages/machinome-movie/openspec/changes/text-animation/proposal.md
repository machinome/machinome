## Why

Words on screen in a Videomaker film appear all at once and vanish all at once.
Three Leonardo episodes ask for more, and one of them had to leave the supported
format to get it:

- The syntax study (`projects/Leonardo/videos/machinome-syntax-study`) commissioned
  source-word emphasis: in line 376 of the sawmill's `model.py`, `waterwheel`,
  `drives` and `crankshaft` light up as the narrator says "Here, the waterwheel
  drives the crankshaft", accumulate, hold briefly and clear. It exists only in the
  disposable renderer `experiments/dark-source/` (`emphasis.mjs`), which proved the
  rule: an exact spoken phrase, unambiguous, each word's onset read from the cached
  narration's character timestamps, never estimated from reading speed. The
  *Revolutions* draft (`machinome-revolutions-v2`) asks for the same emphasis in its
  shot `the-same-in-python` ("Highlight exactly waterwheel, drives, crankshaft ...
  at their measured spoken onsets ... No estimated timings").
- *Revolutions* (`machinome-revolutions`) shot `judgment` shows the overlay
  "Propose. Inspect. Correct." from 1.933 s, all three words at once, while the
  narrator says the same three words one by one. Each word wants to appear as it is
  spoken. Its shot `genome` shows "Pause. Inspect. Test." against the spoken "Pause
  it. Look inside. Test a connection."; there the words are not spoken as written, so
  measured timing is impossible and an even reveal is the only reveal.
- *Revolutions* opens with its title, "REVOLUTIONS", arriving after the first
  sentence over the moving wheel ("Title arrives after the first sentence"), and
  names the sawmill with a title and a line beneath it ("Leonardo's hydraulic
  sawmill" / "Digital reconstruction of a later museum interpretation", shot
  `river`). Today both are spelled as a `top` caption and a `lower-third`, and both
  pop on and off.

This is roadmap item 8 (text animation), whose origin is the syntax study.

## What Changes

- In format `machinome-video-draft/0.4` (introduced by `keyframes-and-easing`), an
  overlay may declare `reveal`: its words appear one by one, either as the shot's
  narration speaks them (`timing: spoken`, onsets from the cached speech, matched
  as the experiment matches an exact phrase) or evenly across a span with an easing
  name from the campaign vocabulary (`timing: even`). Words that have not appeared
  keep their place, so a line never reflows.
- Measured timing is read only from the speech cache that `speech` writes. `check`,
  `preview` and `render` (including `render --silent`) read that cache and never
  generate or purchase speech; an episode whose measured words have no cached speech
  is refused with "run the speech command first". A frame stays a pure function of
  its video time, the episode and the speech cache.
- A new overlay position, `title`: a large centred title with an optional
  `subtitle`, drawn over the model, which keeps running beneath it. A title may fade
  in (`enter`) and out (`leave`) with a duration and an easing name.
- A code shot may declare `code.emphasis`: words of one source line light up at
  their measured onsets in the narration, accumulate, hold and clear together. This
  promotes the experiment's rule into the format; `experiments/dark-source/` stays
  untouched.
- In 0.4 the overlay list, the `code` field and its typing cues become closed
  field lists (the first change of the campaign to touch them), so a misspelled
  `reveal` or `emphasis` is refused, never ignored. 0.2 and 0.3 episodes carrying
  any of the new fields are refused and asked to change their format; 0.2 and 0.3
  frames are unchanged.
- `preview` samples every reveal at its start, midpoint and end, every title fade,
  and every emphasis word, and proves in the page and in pixels that what is drawn
  follows the rule.

## Capabilities

### New Capabilities

- `text-animation`: words that appear as they are spoken or evenly, titles that
  fade in and out over the model, and source words lit as they are spoken.

### Modified Capabilities

None in baseline. Overlays without the new fields keep their meaning; the typing
behaviour of code shots is unchanged.

## Impact

`src/words.mjs` (new: phrase matching, onsets, reveal counts, emphasis ranges),
`src/speech.mjs` (a cache-only reader shared with `speech`; `speech` reports
word-timing refusals after caching), `src/episode.mjs` (0.4 overlay and code
validation, closed lists, refusals in older formats), `src/timeline.mjs` (reveal
and fade state in 0.4 overlay frames), `src/code.mjs` (emphasis ranges),
`src/film.js` and `src/film.html` (words in place, the title, fades, marked source
words), `src/render.mjs` (preview proofs, per-frame checks, frame identity),
`bin/videomaker.mjs` (resolving word timing before `check`, `preview` and
`render`), tests, `docs/FORMAT.md`, `README.md`. It uses `ease` from
`src/easing.mjs` (`keyframes-and-easing`) and adds no Viewer API requirement. The
consuming demo episodes are authored untracked in the Leonardo project; whether
*Revolutions* or its draft adopts any of this is the pilot's decision.

## Non-goals

- Burned-in captions. The roadmap mentions them for vertical Shorts; no episode is a
  Short, every Leonardo README records "no burned subtitles", and the film page's
  test that it has no caption element stays.
- A title card that covers the model. No episode asks for the model to be hidden
  behind a title: *Revolutions* sets its titles over the moving wheel and the
  sawmill, and two of its directions refuse cards ("No authorship card", "without
  interrupting the argument with a legal card"). See design D5.
- Fades on overlays other than titles, letter-by-letter reveals, per-word colours,
  emphasis of numbers, punctuation or whole lines (the v2 draft's `48.0` and
  "class header"), emphasis timed evenly, full-screen source (roadmap item 12).
- Entrances for annotations and graphic shapes (`graphic-overlays`), transitions
  (`shot-transitions`), stills (`stills-and-clips`).
- Any change to speech generation, pronunciation dictionaries or the mix. No
  publication.
