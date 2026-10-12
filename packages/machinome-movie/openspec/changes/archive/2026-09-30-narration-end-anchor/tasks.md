## 0. Preconditions

- [x] 0.1 Base: branch `narration-end-anchor` from `fix-warts` at `e30b05f`.
  Run both suites once before any change and record their summary lines in
  `evidence.md`.
- [ ] 0.2 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: the form (D1), the instant and its departure from the
  ruling's wording (D2), where it is accepted (D3), the schema refusal (D4),
  the Python side (D5), `check`'s line (D6), the manual (D7).

## 1. Python declarations (layer 1, red first)

- [x] 1.1 Red: `lines.end()` and `lines.end(plus=0.8)` evaluate to
  `{"narrationEnd": true}` and `{"narrationEnd": true, "plus": 0.8}`; a
  narration whose last words repeat earlier ("Up. Down. Up.") still ends on
  `narrationEnd`; the evaluation tests of the tour and minimal movies expect
  it. Record the failures.
- [x] 1.2 `anchors.py`: `Anchor.document()` for `end`, `Anchor.check` without
  the tail, `Narration.tail()` removed; `document.py`: the static phrase check
  skips `narrationEnd`.

## 2. Shared fixtures (layer 2, red first)

- [x] 2.1 Red: add `fixtures/invalid/narration-end-not-true.json` (the tour's
  `question` `until` as `{"narrationEnd": false}`, must mention
  `shot question` and `until.narrationEnd`); both suites fail on it (the
  schema has no such form, and the Node refusal does not name the field).
  Record the failures.
- [x] 2.2 The schema's `narrationEnd` branch of `time`; `src/schema.mjs`'s
  `oneOf` refusal by the one titled branch whose required fields are present
  (D4).
- [x] 2.3 Re-evaluate `fixtures/documents/minimal.json` and `tour.json` by
  the recipe of `fixtures/README.md`; diff the resolved documents before and
  after against `fixtures/resolved/` (they must be equal; a difference is a
  finding, never a re-pin), and record the literal last-character reading's
  difference for D2.

## 3. Resolution (layer 3, red first)

- [x] 3.1 Red: in `test/movie-document.test.mjs`, a `narrationEnd` until
  resolves to the chapter start plus offset plus the end of the take's last
  letter or digit plus `plus`, on the grid, and equals the `spokenEnd` of the
  last word; it is refused without a take naming the chapter and `speech`; a
  take with no letter or digit is refused naming `narrationEnd`;
  `describeAnchor` prints `narrationEnd plus 0.8` in an `until` refusal; the
  extra-field form is refused naming `phrase` and `narrationEnd anchor`.
  Record the failures.
- [x] 3.2 `src/movie.mjs`: the static phrase check, `instant`, and
  `describeAnchor`.

## 4. The report (layer 8, red first)

- [x] 4.1 Red: the pipeline test that runs `check` on the tour asserts the
  three per-chapter lines (`opening`, `balance`, `tip`: take, chapter and
  tail in seconds). Record the failure.
- [x] 4.2 `chapterTakeLines` in `src/chapters.mjs`; `bin/videomaker.mjs`
  prints it after the summary line at `check`.

## 5. Manual and records (layer 9)

- [x] 5.1 Red: `python/tests/test_repository.py` pins the manual's paragraph
  (the narrator sets the film's length; `check`'s per-chapter line) and the
  `narrationEnd` of `lines.end()`. Record the failure.
- [x] 5.2 `docs/declaring-a-movie.md`, `docs/movie-document.md` ("Anchors"
  and the refusals), `README.md` (`check`'s output), ADR-001 amended in place,
  `CHANGELOG.md` under `Unreleased`, the architecture overview if its
  structure moved.
- [x] 5.3 Both suites on the final content, with their summary lines in
  `evidence.md`; the Node files this change touches run cold once.
- [x] 5.4 Sync the baseline specs and archive the change with the CLI;
  `evidence.md` in the archived change.

## 6. Human review (not claimed by automation)

- [ ] 6.1 The orchestrator keeps D2 or rules the literal last character.
- [ ] 6.2 *Cut and Advance* re-evaluated in its own repository and its
  resolved cuts compared (the project's, not this change's).

Implementation note (30 September 2026): 0.2 is left open: the planning
commit was made for the orchestrator's review before implementation, and
that review is not claimed here. Order as run: the schema branch (2.2) was
added before the invalid fixture (2.1) because the Python evaluation tests
of 1.1 cannot pass without it; the Python side's red on the fixture is
therefore shown against the base schema (`evidence.md`). The pure tests
always run; of the slow files only `test/pipeline/movie-pipeline.test.mjs`
was changed, and it ran cold; the other slow files ran fresh on the final
content because their keys changed (the edits reach them), not from the
memo. The architecture overview's structure did not move and it is
unchanged. 0.2, 6.1 and 6.2 remain open.
