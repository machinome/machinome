## Why

The episode is the film *Cut and Advance* (the Leonardo project, version 2,
30 September 2026), the first film declared in Python. Four of its five
chapters end on `lines.end(plus=…)`, and so does the closing shot of the
fixture tour. Two findings of that film, in `workflow/warts.md` ("Cut and
Advance"):

- **Wart 2, `lines.end()` has no anchor of its own.** `Narration.end()`
  evaluates to `{"spokenEnd": <tail>}`, where the tail is the shortest run of
  the narration's last words that occurs once (`moment`, `stroke`,
  `progress`, `blade`, `description` in the film). The document then says a
  phrase the author never wrote, and a narration whose last words repeat
  earlier ones makes the tail grow until it is unique ("Up. Down. Up." ends on
  "Down. Up"). It works and is fragile in principle; the author meant "when
  the narrator finishes", and the document should say that.
- **Wart 7, the narrator sets the film's length.** With every cut on a phrase
  and the chapter tails as the only slack, a 100-second shot list resolved to
  59 s once the narrator's takes were measured. That is what anchors are for,
  but an author needs to know it before estimating, and needs to see, per
  chapter, how long the take is and how much of the chapter is tail.

What the film does with the result: its `lines.end(plus=…)` cuts are written
in its document as the end of the narration, and resolve to the same frames
as today; `check` shows each chapter's take, length and tail, which is what
the author reads when deciding how long a chapter's ending lingers.

## What Changes

- **A third anchor form, `{"narrationEnd": true}`**, with an optional
  `plus`, accepted wherever `spokenEnd` is (a shot's `until`, a cue's `at` and
  `until`, a `move`'s `until`, a model key's `at`, a picture view key's `at`).
  It resolves to the instant the chapter's narration ends: the chapter's
  start plus its speech offset plus the end of the last spoken letter or digit
  of the chapter's cached take plus `plus`, snapped to the frame grid like
  the other anchors. It needs a cached take like they do (the same refusal
  naming the chapter and the `speech` command). The schema refuses it when
  its value is not `true` or when it carries another field, naming
  `narrationEnd` and the field's path.
- **`Narration.end(plus=0)` evaluates to it.** `lines.end()` keeps its name
  and meaning; the tail helper is removed. Nothing else in the Python API
  changes.
- **`check` prints one line per chapter**, after the summary line it already
  prints: the chapter's id, its take's measured length, the chapter's
  resolved length and its tail (the chapter's length minus its speech offset
  minus the take), for example `  drive: take 5.68 s, chapter 7.20 s, tail
  1.32 s`; a chapter without a cached take says so.
- **The manual says the narrator sets the film's length**: with every cut on
  a phrase, a film is as long as its takes and their tails, so an author
  estimates by speaking the narration, not by counting shots, and reads
  `check`'s per-chapter line.
- Fixtures: the `minimal` and `tour` documents are re-evaluated (their
  `lines.end()` anchors become `narrationEnd`) and resolve to their existing
  pins byte for byte; one invalid fixture, `{"narrationEnd": false}`, refused
  by both runtimes.
- Records: `docs/movie-document.md` ("Anchors") and
  `schema/machinome-movie-0.2.json`; `docs/declaring-a-movie.md`; `README.md`
  where it describes `check`'s output; ADR-001 amended in place with a dated
  section; `CHANGELOG.md` under `Unreleased`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `movie-document`: the `narrationEnd` anchor and its refusal; `check`'s
  per-chapter report of takes and tails.
- `declarative-movie`: what `lines.end()` evaluates to.

## Impact

Changed: `schema/machinome-movie-0.2.json` (the anchor form),
`src/movie.mjs` (static checks, resolution, `describeAnchor`),
`src/schema.mjs` (a `oneOf` whose value carries exactly one branch's
required field is refused with that branch's error, so the refusal names the
field at fault), `bin/videomaker.mjs` (the per-chapter line),
`python/machinome_movie/anchors.py` and `document.py`, the fixture documents
`fixtures/documents/minimal.json` and `tour.json`, a new
`fixtures/invalid/narration-end-not-true.json`, the tests of layers 1, 2, 3,
8 and 9. The resolved pins `fixtures/resolved/*.json` are not rewritten: the
change is proven by their staying equal.

## Non-goals

No other anchor form; no change to `spoken` or `spokenEnd`, or to how
`until` snaps; no per-shot report; no change to the take, the speech command
or YAML episodes' sources. No publication, push or paid request.
