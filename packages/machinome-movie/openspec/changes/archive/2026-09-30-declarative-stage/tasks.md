## 0. Preconditions

- [x] 0.1 The base run of the Python suite is recorded in `evidence.md`
  before any change (98 passed).
- [x] 0.2 The contract, the schema, the campaign plan, the direction note,
  the manual page, ADR-002, the baseline spec, the previous cycle and the
  film's specification are read; readings and findings are recorded in
  design.md and `evidence.md`.

## 1. Red tests, innermost first (record each failure in evidence.md)

- [x] 1.1 Layer 1, declarations: project sets (kind, slots, props, module,
  base, refusals), project elements (actions, parameter types, props,
  refusals), shipped elements and their actions, emphasis words and anchors,
  placements (empty slots, unknown slot, element in two slots), typing and
  completion across a chapter.
- [x] 1.2 Layer 1, evaluation: the 0.2 shape of the tour and minimal movies,
  the stage block, token checks against the excerpt, module existence inside
  the project, props kinds consistent across instances, twice byte-identical,
  only the manifest, revision and emphasised excerpts opened.
- [x] 1.3 Layer 2: the fixture documents equal their movies' evaluation;
  every invalid fixture is refused naming its `must_mention`; a document
  written by hand on the Node side is accepted by `check_document`.
- [x] 1.4 Layer 9: the package ships the 0.2 schema; no reference to 0.1 in
  the package, the manual page or the fixtures; the manual's examples are the
  fixture project's code and name no project; the fixture revision is
  reproducible.

## 2. Implementation

- [x] 2.1 Sets and slots: `Set`, `Slot`, `Frame`, `Split`, kinds, props,
  modules (D1).
- [x] 2.2 Elements and actions: `Element`, `Action`, project actions, `View`
  with its marks, the source panel, `Title`, `Picture`, `Reveal`, `Style`
  (D2, D3).
- [x] 2.3 Chapters, shots and cues in the 0.2 shape; emphasis phrase checks;
  typing and completion (D4 phrase part, D5, D6).
- [x] 2.4 Evaluation to 0.2: the stage block, modules, token checks, the top
  level (D4 token part, D7, D8).
- [x] 2.5 `check_document` for 0.2 and the package's schema link (D9, D10).
- [x] 2.6 The fixture project's movies and `stage.tsx`; the revision re-pinned;
  documents, takes, invalid fixtures and `fixtures/manifest.json` written;
  the 0.1 documents and their takes deleted (D10).

## 3. Records

- [x] 3.1 ADR-005 under `docs/adrs/SOURCE/`, listed in the index; Accepted at
  archive.
- [x] 3.2 `docs/declaring-a-movie.md` rewritten for the stage shape;
  `python/README.md`; `fixtures/README.md` for 0.2 documents.
- [x] 3.3 `docs/architecture-overview.md` "Movies declared in Python";
  `AGENTS.md` the Python part of the status bullet.
- [x] 3.4 `CHANGELOG.md` bullet under `Unreleased`.
- [x] 3.5 Findings for `workflow/warts.md` under a dated heading.
- [x] 3.6 Sync the baseline spec and archive the change; `evidence.md` carries
  the red and green runs, the contract findings and the spellings changed.

## 4. Human review (not claimed by automation)

- [ ] 4.1 The film itself: produced in the Leonardo repository by the
  campaign's film step once this change and `react-stage` are merged, and
  inspected by the pilot.

Implementation note (30 September 2026): the film's source was checked on a
scratch stand-in project, its model and export standing in for the Leonardo
project's, with one spelling changed (`evidence.md`); 4.1 remains open.
