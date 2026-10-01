# Shared fixtures

Fixtures both the Python suite and the JavaScript suite run, so the two
sides of the movie document cannot drift from each other. A fixture is added
once and paid for twice: a document one side does not handle fails that
side's suite.

- `documents/<name>.json` — valid `machinome-movie/0.2` documents. The Python
  suite asserts that evaluating the fixture movie of the same name (declared
  under that name in the fixture project's `[tool.machinome.movies]`, at
  `python/tests/fixtures/project/videos/<name>/movie.py`) yields exactly this
  document, written for this file (`root` points back at the movie; files are
  written with two-space indentation and a final newline). The Node suite
  asserts that it validates against `schema/machinome-movie-0.2.json`, passes
  the static checks, resolves against its takes to exactly
  `resolved/<name>.json`, twice identically, with every anchor on the frame
  grid. `minimal` is one shot on the shipped `frame`; `tour` uses the fixture
  project's own sets (`playbill`, `playbill-split`, drawn by
  `videos/tour/stage.tsx`) and element (`tally`), the shipped `frame` and
  `split`, and every shipped element and action the validation film uses;
  `count` films the clocked counter's take `Turns` (`model.timeMode`
  `take`, the `take` block of the framework's recorded requests and banks)
  in three shots on `frame` and `split`, with a typed source panel, an
  emphasis and a highlight. The Node suite refuses `count` until it reads
  take documents (the `pose-a-take` change), and it has no resolved pin
  until then. A
  document written by hand on the Node side is named `node-<name>.json` and
  has no fixture movie; the Python suite asserts instead that
  `check_document` accepts it.
- `takes/<name>/<chapter-id>.json` — the speech double: one per chapter whose
  anchors need a take (a chapter without spoken anchors may have one too). Its
  shape is the part of the speech cache record the resolver reads:

  ```json
  {"duration": 4.54,
   "alignment": {"characters": ["W", "a", …],
                 "character_start_times_seconds": [0, 0.06, …],
                 "character_end_times_seconds": [0.06, 0.12, …]}}
  ```

  `characters` spell the chapter's spoken narration (after
  `audio.replacements`) one code point each, times in seconds from the take's
  start, non-decreasing; `duration` is the take's length. The fixtures here
  give every character 0.06 s (`test/project-fixture.mjs`, `evenAlignment`)
  and a duration of the characters plus 0.1 s. The Node pipeline test
  installs a take as the speech command caches it: a silent WAV of
  `duration` at `_build/audio/<chapter-id>-<key16>.wav` beside a record with
  its checksum. A registered document whose anchors need a take this
  directory lacks fails the Node suite naming the file to add.
- `resolved/<name>.json` — the resolved document the Node resolver produces
  from `documents/<name>.json` with `takes/<name>/` (see "Resolution" in
  `docs/movie-document.md`). Pinned by the Node suite, reviewed by hand when
  written; the Python suite does not read it.
- `invalid/<name>.json` — `{"name", "document", "must_mention": [...]}`: a
  document that must be refused, with the substrings the refusal names.
  Both suites iterate every file here. Each is refusable without a take:
  format, schema, the stage block (modules, shipped sets and their slots,
  bases, kinds the tool ships), a chapter's elements (kinds, fields, cameras,
  layers, excerpts, stills, a project element's props), a shot's set and
  placements, fades, a literal `until`, phrases in the written narration,
  marks, model keys, joins and easings (a reframe whose shots share no
  view), a cue's actions (placed elements,
  actions a kind has, their fields and parameters, spans with an `until`,
  entrances), typing and completion, emphasis anchors and spoken words, a
  spoken reveal, duplicate ids, a take document's `take` block and its
  model time; and, read through the document's `root`, the parts it names
  checked against its export, the tokens it emphasises checked against its
  excerpts, and a take's identity and inputs checked against its export and
  its banks against the replay of its steps. Each is one mutation of an
  evaluated fixture document, rooted at the fixture project's movie from
  this directory.
- `scripts/pin-resolved.mjs NAME...` writes `resolved/<name>.json` from the
  document and its takes, for a person to review before committing; never
  regenerate a pin to make a failing test pass.

`manifest.json` indexes the valid documents, `{"documents": [<name>, ...]}`,
so a new fixture is registered once and missed by neither side.

## The fixture project

`python/tests/fixtures/project/` is a tiny machinome project: a seesaw model
(`models/seesaw.py`, a declared 20 s loop through which the beam tips), its
posed export (`export/seesaw/`, which the framework's command writes from the
project directory, `machinome export seesaw -o export/seesaw --fps 30
--frames 600 --no-widget`, and which the viewer layer poses), a clocked
counter (`models/counter.py` and `models/digits.svg`, copied from the
framework tutorial's chapter 9 with the pieces it imports, Apache-2.0 as
the project's `NOTICE` says) and its clocked export (`export/counter/`,
`machinome export counter -o export/counter --no-widget`), a still
(`media/plate.png`), the takes the fixture movies film (`videos/takes.py`:
the seesaw's loop `Playground` and the counter's take `Turns`) and the
movies, with the tour's template (`videos/tour/stage.tsx` and
`stage.css`). The still is drawn by `scripts/draw-fixture-still.mjs`, 864 by
576 pixels of flat shapes with no text, the size at which the tour's plate,
over its stage at 1280 by 720, draws it whole at its own size; a pure test
asserts that the committed file is that drawing. The `source-revision.txt`
of each export (`export/seesaw/`, `export/counter/`) is the commit of the
project made this way, so that source pinned to it can be checked:

1. copy every file of the project except `export/`, `_build/` and
   `__pycache__/` into an empty directory;
2. `git init`, `git add -A`, and `git commit -m "Fixture project"` with
   author and committer `Videomaker fixture <fixture@videomaker.invalid>`,
   both dated `2026-09-30T00:00:00+00:00`, and no global or system Git
   configuration.

The Python suite makes that commit and asserts its hash, and the Node suite
refuses a fixture movie whose copy does not commit to it. Changing any file
of the project changes the hash, so the revision and every document pinned
to it are re-pinned together, by one command:

```sh
node scripts/pin-fixture-project.mjs --python <python>
```

It makes the commit by the recipe, writes its hash to the
`source-revision.txt` of every export, evaluates every document `manifest.json`
registers whose movie the project declares into `documents/` (with
`PYTHONPATH` set to this repository's `python/`; `<python>`, by default
`python3`, needs the package's dependencies) and prints what changed. It
does not write `resolved/`: run `scripts/pin-resolved.mjs` for the documents
it names and review the pins before committing. A document written by hand
is not evaluated; the command prints the revision it pins.

## Refusal words

The substrings are locations, vocabulary and field names, chosen to be stable
across languages, never a runtime's type names, quoting or number
formatting. Both runtimes name:

- the chapter and the shot by id, and a field by its path inside the shot:
  `until`, `places.<slot>`, `model.from`, `model.keys[2].at`,
  `model.keys[0].seconds`, `transition.kind`, `cues[1]`, `cues[1].at`,
  `cues[0].actions[0]`, `words[1].token`, `reveal.phrase`, `enter.kind`;
- a chapter's element as `elements.<key>`, and the stage block's entries as
  `stage.modules`, `stage.sets.<kind>` and `stage.elements.<kind>`;
- the phrase, mark, camera, layer, excerpt, still, slot, element, action,
  parameter, prop or token as written, and the vocabulary word of the rule:
  `absent`, `ambiguous`, `at or before its start`, `first shot`,
  `last shot`, `shot id`, `does not declare`, `does not place`,
  `two slots`, `ships`, `base`, `missing`, `complete`, `already`,
  `outside the excerpt`, `word for word`, `outside the take`, `no view
  element in both` (a reframe whose two shots share no view), and the kinds
  `string`, `number`, `boolean`, `list`, `object`;
- for a take document, its fields by their path: `model.timeMode`,
  `take.steps[0]` with the step's id (`step-1`) and its field (`input`),
  `take.banks.<mark>` with the mark and the first id that differs from the
  replay, `take.identity` beside the export's `clocked.identity`;
- for a schema refusal, the field's name (an unknown `narration` on a shot is
  refused naming `narration`).
