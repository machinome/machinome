# Implementation evidence

## Authority and scope

Planning commit `121a86c` (proposal, design, delta spec, tasks, ADR-005 as
Proposed), cut on branch `declarative-stage` from `react-stage` at `be98523`,
the commit that wrote the contract (`docs/movie-document.md`,
`schema/machinome-movie-0.2.json`). The orchestrator's brief is the
ratification this cycle ran under; no design point in it was substituted.

Nothing was written in the Leonardo repository, the framework, the viewer,
the studio, the primary checkout or any other worktree. The Leonardo spec was
read; the three source excerpts its film emphasises (lines 413–415, 425–435
and 472–486 of its `models/hydraulic_sawmill/model.py`) were read to check
the token rule against them. Leonardo's model was never imported and its
export never read. Nothing was installed, pushed or published. No Node, no
`src/`, no `test/` was touched, and `fixtures/resolved/` was not written.

## Red / green chronology

All runs: `/home/asa/devel/machinome/.venv/bin/python -m pytest -q` from
`python/` (pytest 9.1.1, Python 3.12.3).

1. **Base.** Before any change: **98 passed** in 9.4 s.
2. **R1.** The five test modules rewritten for 0.2 and the fixture project's
   movies rewritten on `Frame`, `Split`, `Playbill`, `PlaybillSplit` and
   `Tally` (the tests' inputs), package unchanged: 2 collection errors
   (`test_declarations`, `test_evaluation`: `cannot import name 'Action'
   from 'machinome_movie'`), **37 failed, 9 passed** (with
   `--continue-on-collection-errors`): the CLI's pinned `minimal`, every
   registered document and every invalid fixture (the documents and
   fixtures were still 0.1), the schema link, the 0.1 pin, the revision, the
   manual and the changelog.
3. **G1.** After `text.py`, `names.py`, `take.py`, `stage.py`, `movie.py`:
   `test_declarations.py` **71 passed**.
4. **G2.** After `evaluate.py`, `document.py`, the schema link and
   `__init__.py`: `test_evaluation.py` **31 passed**.
5. **R2.** The fixture revision re-pinned to
   `99219d36cd87e0ada0244a6c2e0eb532659cdda5` by the fixtures README's recipe;
   documents, takes and 59 invalid fixtures written: full suite **4 failed,
   178 passed**, the four being the records (0.1 still named in
   `docs/declaring-a-movie.md` and `fixtures/README.md`, the manual's
   examples and link, the changelog).
6. **G3.** After the manual page, the fixtures README and the changelog:
   **182 passed**.
7. Two evaluation tests added after a review of what the tour does not
   exercise (a base set no shot uses; two sets of one kind), and a 60th
   invalid fixture (`token-segment-of-a-dotted-path`) after the mutation
   check below showed the invalid set alone did not tell the two token
   readings apart.
8. **Green.** **185 passed** in 10.6 s: `test_cli` 5, `test_declarations`
   71, `test_evaluation` 33, `test_fixtures` 65, `test_repository` 11.

### Mutation spot-checks

Because the first red of the new tests was a missing import, ten checks were
removed one at a time, the named tests run, and the source restored byte for
byte (sha256 compared) by a scratch script:

| check removed | went red |
|---|---|
| a slot read returns a fresh key | `test_slot_filled_twice` |
| an element placed in two slots | `test_element_placed_in_two_slots` |
| the dot as a token boundary | `test_words_and_tokens_are_bounded`; after step 7 also the invalid fixture `token-segment-of-a-dotted-path` |
| a set's slots are its own body's | the two derived-set tests |
| a completed panel is not typed again (document check) | invalid fixture `typing-a-completed-panel` |
| an action parameter's type | `test_an_action_call_checks_its_parameters_by_name` |
| a token's count in its excerpt (evaluation) | `test_a_token_absent_from_its_excerpt`, `test_a_token_repeated_in_its_excerpt` |
| a project base listed in `stage.sets` | `test_a_derived_sets_base_is_listed_though_no_shot_uses_it` |
| props of one kind agree across a movie | `test_an_elements_props_have_one_kind_in_a_movie` |
| a placed panel is completed | `test_a_placed_panel_is_typed_to_its_end` |

### Determinism

Two command-line evaluations of the fixture `tour` to files outside the
project were byte-identical (20 615 bytes); the suite asserts it for `tour`
in-process and pins both documents (sha256 `minimal.json` 4b197185…,
`tour.json` f97855fd…). Evaluation opened exactly the export's manifest, its
revision and `models/seesaw.py` (the emphasised excerpt's file), asserted by
`test_evaluation_opens_only_the_manifest_revision_and_emphasised_excerpts`.

### Invalid fixtures

Each of the 60 was checked to be refused for its intended reason (the
refusal printed and read, not only its words matched): 3 schema or format,
7 stage block, 8 chapter elements, 4 placements, 12 shot time, joins and
model, 12 cue actions, 12 typing and emphasis, 2 reveals. Every one is a
single mutation of an evaluated fixture document, rooted at the fixture
project's movie from `fixtures/invalid/`, so the parts and tokens they name
are checked against the real fixture export and source through `root`.

## Acceptance against the film's source

The "The Python source" block of the Leonardo spec (version 2) was copied to
a scratch stand-in project: a stand-in model declaring exactly the part paths
the source names, the three excerpts placed at their real line numbers with
the text read from the model, a stand-in export naming those parts, an empty
`stage.tsx` and still, and a `pyproject.toml` listing the movie.

- **As specified**, evaluation refuses:
  `Drive.coupling: cues[3]: emphasize: the token 'waterwheel' is absent from
  the excerpt coupling (../../models/hydraulic_sawmill/model.py, lines 413 to
  415; found 0 times)`. See "Spellings changed" below.
- **With that one spelling changed**, the source evaluates: five chapters,
  twelve shots, on `leonardo` (with `series`) and `leonardo-split` (base
  `leonardo`, slots `left`, `right`, `headline`), the element `jobs` (props
  `jobs: list`, action `light(job: string)`), `stage.modules` `["stage.tsx"]`;
  two command-line evaluations byte-identical (29 798 bytes). The emphasis
  pairs of `pawls`, `holding` and `shaft` (`feed.rocker.turn`,
  `feed.pawl.turn`, `ratchet_angle`, `feed.holding_pawl.turn`,
  `feed.reserve.shift`, `feed.takeup.shift`) each occur once in their
  excerpts under the token rule.
- The refusals the film's acceptance names, each on a mutated copy: a
  misspelled part path (`Mill.feed.pawll`, refused by the framework at the
  line), an unknown camera (`Sawmill.pawlz`, refused by Python at the line),
  an absent phrase (`Drive.wheel: until: the phrase 'In the modle' is
  absent…`), an element in a slot the set lacks (`Drive.coupling: stage is a
  slot of Leonardo, not of LeonardoSplit, whose slots are left, right,
  headline`), an action on an element the shot does not place
  (`Question.hook: cues[1]: show acts on title, which the shot does not
  place`), a token absent (`ratchet`), and a wrong action parameter
  (`Jobs.light: the parameter job is 2, and the action declares it string`).
  A token repeated in its excerpt is refused as the fixture `Block` shows;
  no token of the film's excerpts is repeated.

## Spellings changed from the film's source

Only one, for the orchestrator to carry into
`videos/cut_and_advance/spec.md`:

- Chapter `drive`, shot `coupling`, the emphasis cue:

  ```python
  code.emphasize(("waterwheel drives", "water_drive.waterwheel.spin.drives"),
                 ("crankshaft", "water_drive.crankshaft.spin"), hold=0.6)
  ```

  instead of `code.emphasize("waterwheel", "drives", "crankshaft", hold=0.6)`.
  Reason: under the contract's token rule (a token occurs once in the
  excerpt, identifier-bounded, `[A-Za-z_][\w.]*`), `waterwheel`, `drives` and
  `crankshaft` are never whole tokens of lines 413–415; they are segments of
  `cycle.drives`, `water_drive.waterwheel.spin`,
  `water_drive.waterwheel.spin.drives` and `water_drive.crankshaft.spin`.
  The pairs light the call that says "the waterwheel drives" and the
  crankshaft it drives, each once in the excerpt. The lesson is unchanged;
  what lights is a whole call instead of three words. If the pilot wants a
  word lit inside a dotted path, that is a contract change (see finding 1).

Everything else in the source (sets, slots, props, the `Jobs` element and its
action, titles and pictures as elements, marks on the view, `Style`, empty
slots, the panel and view kept across `pawls` → `holding`) is implemented as
written.

## Contract findings

For the orchestrator. For each, the reading this change took keeps both
runtimes able to agree; the smallest correction to `docs/movie-document.md`
is proposed. The schema was not edited.

1. **What "identifier-bounded" means is ambiguous, and the page's example
   contradicts the stricter reading.** The page says each token occurs once
   "identifier-bounded (`[A-Za-z_][\w.]*`, so `feed.pawl.turn` is one
   token)" and also that "*the driving pawl* may light `feed.pawl`". Read
   with boundaries that exclude the dot, `feed.pawl` never occurs in an
   excerpt that spells `feed.pawl.turn`; read with boundaries that exclude
   only word characters, it occurs as often as `feed.pawl.` does, and
   `waterwheel` occurs twice in the film's coupling excerpt. Reading taken:
   an occurrence is not preceded or followed by `[A-Za-z0-9_.]`, ASCII, and
   the token matches `[A-Za-z_][A-Za-z0-9_.]*`. Correction: state that rule
   in those words and change the example to `feed.pawl.turn`. The invalid
   fixture `token-segment-of-a-dotted-path` pins it for both runtimes.
2. **Word-bounded is undefined.** Reading taken: a spoken part is not
   preceded or followed by `[A-Za-z0-9_]`, ASCII, case-sensitive, so both
   runtimes' regular expressions agree. Correction: say so.
3. **Which runtime checks tokens, and what evaluation reads.** The page
   refuses a token absent from or repeated in its excerpt, which needs the
   excerpt's text; the brief's layer 1 said evaluation reads only the
   manifest and revision. Reading taken: evaluation also opens the source
   files of the excerpts an emphasis lights (only those), and
   `check_document` checks tokens when given the excerpts' text; the invalid
   fixtures give it through `root`. Correction: name the excerpts among what
   evaluation reads, and state that the static checks include tokens.
4. **`stage.sets` lists "every set kind a shot uses", but `base` must be "a
   kind in this table or a shipped kind".** A project set whose derived set
   is used and which no shot uses would leave `base` dangling. Reading taken:
   the table lists every set a shot uses and every project set those derive
   from. Correction: "every set kind a shot uses, and the project sets they
   derive from".
5. **Where an element's prop kinds come from is unstated.** Reading taken:
   from the instances the movie declares (the film's `Jobs` declares none on
   the class); every instance of a kind in one movie gives the same props of
   the same kinds, or evaluation refuses; `null` has no prop kind and is
   refused. Correction: one sentence under the stage block.
6. **A derived set's props.** The example gives `leonardo-split` `props: {}`
   while the chrome it inherits reads `series`, which lives on `leonardo`.
   Reading taken: a set's props are its own body's; the base's props reach
   the chrome through the base's own entry, which finding 4 guarantees is in
   the table. Correction: say that the stage hands a base's chrome the
   base's props.
7. **A spoken reveal's phrase must occur once in the narration.** The page
   says it defaults to the title's text and matches it word for word, not
   that it is a phrase of the narration once; the renderer cannot place it
   otherwise. Reading taken: refused when absent or ambiguous, as any
   phrase. Correction: add "and occurs once in the chapter's narration".
8. **The schema does not require `props` on a project set**, which the page
   says a project entry has. Python always writes it; the Node side should
   not depend on it until the schema requires it (an `if module then
   required props` clause). Not a blocking error; no schema edit made.
9. **`draw` on a leave.** The page says `enter` and `leave` take `fade` or
   `draw`, `draw` on a ring or an arrow only. Python writes `draw` only on
   entrances and the check accepts it on either, per the letter. If a drawn
   exit is not meant, the page should say "`draw` only on the entrance of a
   ring or an arrow".

## Not claimed

- The Node side: loading 0.2, the resolved documents for `minimal` and
  `tour` (`fixtures/resolved/` still holds the 0.1 pins; the orchestrator
  pins the new ones after the merge), the stage runtime, the placeholder
  `stage.tsx`'s components. Until the `react-stage` change lands, the Node
  suite reads the 0.1 schema and fixtures this change removes and fails on
  them; the Node suite was not run.
- The film itself, its speech, preview and render: the campaign's film step.
- Slow layers (5 to 8) do not exist for Python and were not run.
