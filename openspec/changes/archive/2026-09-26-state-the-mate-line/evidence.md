# Evidence: state-the-mate-line

Every command ran from the worktree
`/home/asa/devel/machinome/machinome/WTs/state-the-mate-line` with
`PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
No `git` write command was run at any point, and no two test suites ran
at once.

## 0.1 Worktree and base

    python -c "import machinome; print(machinome.__file__)"
    /home/asa/devel/machinome/machinome/WTs/state-the-mate-line/machinome/__init__.py

Branch `state-the-mate-line`, base commit `d791eaa` ("Implement
place-parts-by-mate: frames on parts, revolute mates compiled at
realization (ADR-147)"), planning commit `81d056d` at `HEAD`. The
worktree was clean when this work began.

## 0.2 Full suite at the base (planning commit 81d056d)

    python -m pytest -q -p no:cacheprovider -rs

    3816 passed, 4 skipped, 53 warnings, 2487 subtests passed in 398.13s (0:06:38)

The 4 skips: browser snapshot e2e not enabled, jscad CLI absent, the two
Internal-Cycloidal-Actuator vendor-STEP cases.

## 0.3 Scope

The three scope questions of `proposal.md` were taken at their
recommendations, ratified on 2026-09-26 by the orchestrator's
adversarial review under the review gate the pilot delegated on
2026-09-07, on the pilot's instruction of 2026-09-26 to work the
`place-parts-by-mate` findings with Thor as the validator
(`proposal.md`, "Ratified scope"):

1. Both provisional dispositions of the `place-parts-by-mate` findings
   (the first **Deferred**, the second **Left as is**) are reopened now,
   with Thor as the originating project.
2. A stated line is numbers only, refused by name at class creation
   otherwise.
3. A new ADR-148 (NODE) amends ADR-147, with an *Amended by* line on
   ADR-147, written after implementation confirms the design.

None differs from the recommendation, so the planning artifacts stand
as ratified.

## 0.4 Base documents, captured before any code change

Two mated fixtures whose freedoms state no line, bound to their
declared defaults and published by `tests/test_mates.published`
(`json.dumps(..., indent=2) + '\n'`), captured at `81d056d` with no
framework source edited (`git diff --quiet -- machinome` held):

- `tests.mate_project.arm:MatedElbowMachine` (the existing root over
  `MatedArm`) -> `mated_elbow_machine.json`, 1917 bytes;
- `tests.mate_project.arm:MatedShoulderMachine`, a root over
  `MatedHousing` added to `tests/mate_project/arm.py` for this task (a
  fixture, not implementation), driving the shoulder at 15 and the
  elbow at 25 -> `mated_shoulder_machine.json`, 3434 bytes. Its `art2`
  carries the shoulder's centring pair `-(0, 0, 68)` / `+(0, 0, 68)`
  round the turn, then `r 180 (0, .7071..., .7071...)` and
  `t (0, -68, 123)`: the frame's origin as the joint's anchor, today's
  behaviour.

Each in `evidence/base_documents/` and the same bytes in
`tests/base_documents/` (which the test reads, so archiving the change
cannot break it):

    cmp evidence/base_documents/mated_elbow_machine.json tests/base_documents/mated_elbow_machine.json      -> identical
    cmp evidence/base_documents/mated_shoulder_machine.json tests/base_documents/mated_shoulder_machine.json -> identical

Both declare document version 2.

## 1.1 Planning record

    openspec validate state-the-mate-line --strict
    Change 'state-the-mate-line' is valid

## Section 2: red first (`tests/test_mates.py`)

Fixtures, each beside its hand-placed twin:

- `tests/mate_project/verbatim.py` holds everything a freedom stating no
  line can already express: the moving parts with the design's
  connectors verbatim (`Art2.bore`, `Art56.bore`, `Art4.bore`, each a
  `Link` assembly with one `Plate` leaf placed at `(7, 11, 13)` so a
  world matrix sees a misplaced anchor or axis), the hand-placed twins
  (`HandShoulder`, `HandWrist`, `HandYaw`, their `render()` writing the
  rest placement of tasks section 2 over a child whose class declares
  the hand-written joint), `HandShoulderMachine` (a driver `angle` onto
  the twin's joint), and `ReversedYawByFrame` (the reversed connector
  mated with `Revolute()`, 2.7's guard).
- `tests/mate_project/line.py` holds the mates that state their line:
  `VerbatimShoulder` (`Revolute(axis=(0, 0, 1), at=(0, 0, 0))`),
  `VerbatimShoulderMachine`, `VerbatimWrist` (`axis=(1, 0, 0)`),
  `VerbatimYaw` (`axis=(0, 0, 1)`) and `AnchoredHousing`
  (`MatedHousing`'s on-line bore with `Revolute(at=(0, 0, 0))`).

The split keeps the guards importable at the base: every class of
`line.py` is refused at the base when the module is imported.

**Red** (no framework source edited, `git diff --quiet -- machinome`):

    python -m pytest -q -p no:cacheprovider tests/test_mates.py \
        -k "may_state or stated_line_is or stated_axis_has or StatedLine"
    25 failed, 5 passed, 60 deselected, 17 subtests passed

Per test:

- **2.1** `RefusalTest::test_a_freedom_may_state_its_line` (replaces
  `test_a_freedom_does_not_restate_the_line`): all three subtests red on
  the restatement refusal, e.g. `TypeError: Stated.swing: its freedom
  states axis=(0, 0, 1), and the two frames supply the axis and the
  anchor ... Drop axis.`
- **2.2** `RefusalTest::test_a_stated_line_is_numbers`: all five cases
  (`token`, `formula`, `callable_axis`, `two_components`, `a_bool`) red on
  the ARGUMENT and REASON fragments -- `"freedom's at" not found`,
  `"written in the assembly and read in the moving child's frame" not
  found`, `'two frames supply' unexpectedly found` -- while the class and
  mate names (`Lifted`, `swing`) were already present, the proposer's
  trap: a names-only assertion would have been green.
- **2.3** `RefusalTest::test_a_stated_axis_has_a_direction`: red on
  `"freedom's axis"` and `'an axis of zero length states no line' not
  found in "Flat.swing: its freedom states axis=(0, 0, 0), and the two
  frames supply ..."`; `Flat`, `swing` passed.
- **2.4** `StatedLineTest::test_the_joint_turns_about_the_stated_line`,
  **2.5** `test_an_anchor_at_the_childs_origin_drops_the_centring_pair`,
  **2.6** `test_thors_across_and_reversed_shapes_reproduce_their_twins`,
  **2.7** `test_a_stated_axis_keeps_the_sign_a_reversed_frame_would_flip`,
  and **2.9**'s `StatedLineDocumentTest::test_a_stated_line_needs_no_newer_consumer`:
  red on `TypeError: VerbatimShoulder.shoulder: its freedom states
  axis=(0, 0, 1) and at=(0, 0, 0), and the two frames supply ...` raised
  importing `line.py` -- the only failure a stated line can have at the
  base. Because that red says nothing about the geometry, each was also
  shown to discriminate by mutation after the implementation (below).
- **2.8** `test_a_freedom_stating_no_line_takes_the_frames` and **2.9**'s
  `test_a_mate_that_states_no_line_is_unchanged_in_every_byte`: green at
  the base, as the tasks name them (guards of today's behaviour); shown
  to discriminate by mutation below.

**Implementation** (tasks 3.1, 3.2): in `machinome/motion/mates.py`,
`_check_freedom` loses the restatement refusal and calls the new
`_check_stated(where, argument, value)` for a stated `axis`
(`is not None`) and a written `at` (`anchor_written`, identity with the
sentinel); `_check_stated` refuses a token or formula (duck-typed on
`dimension`, as the range check already does), a callable, a string or
non-sequence, a sequence not of three, and a component that is a `bool`,
a token or not an `int`/`float`, each naming the class, the mate and
the argument and saying the line is written in the assembly and read in
the moving child's frame; then an axis whose length is below `1e-9`
(the joint's threshold). `_install` builds
`Revolute(axis=freedom.axis if freedom.axis is not None else frame.z,
at=freedom.at if freedom.anchor_written else frame.at, range, unit)`,
the stated values passed straight through. `_placement` and
`apply_mates` are untouched.

One test defect, not code: 2.6's leaf walk first read `node.children`,
which a rendered assembly does not populate (it is set by
`as_scad`/`materialize`), so it compared only the root; it now walks
`declared_children` and asserts the leaf set is exactly
`['/<child>/plate']` for mated and twin alike.

**Green:** `10 passed, 60 deselected, 59 subtests passed`. Measured at
30 degrees, verbatim shoulder: plate world matrix deviation from the
twin `0.0`.

**Mutation runs** (each applied to `_install`, the section-2 tests run,
the file restored from a copy and compared with `cmp`):

- stated axis ignored (`axis=frame.z`): 2.4 red, 2.7 red, 2.9's
  document test red, and 2.6 red for every binding except unbound, for
  all three shapes (15 subtests);
- stated anchor ignored (`at=frame.at`): 2.4 red (the centring pair
  appears), 2.5 red, 2.9's document test red, 2.6 red for the shoulder at
  every binding;
- a left-out anchor taken as written (`at=freedom.at` always): 2.5 red,
  2.8 red for `elbow`, `shoulder` and `yaw`, and both byte-identity
  documents red (`mated_elbow_machine.json`,
  `mated_shoulder_machine.json`).

Unbound, every mutation leaves 2.6 green: the frames alone place the
rest, which is the design (decision 4).

## 3.3 Docstrings and messages

`mates.py`: the module docstring (the freedom states its line or the
frame supplies it; the frames fix the rest and the zero, ADR-148; item 2
of the compile list), `_check_freedom`, `_install`, and the new
`_check_stated`. `joints.py`: `_DefaultAnchor` (one purpose: left out
takes the frame's origin, written is the child's origin), `Revolute`
(the moving frame supplies the axis by default; a freedom may state it
in numbers), `axisless_refusal` ("where the moving frame supplies it";
the fragments `axis` and `mate` kept). `frames.py`: `Frame` ("`z` is the
line a revolute mate turns about unless the mate's freedom states one").

Probes outside the suite (a scratch project with a `[tool.machinome]`
manifest): a stated axis spelled as a list, `axis=[0, 0, 1]`, is
accepted and turns the part; a whole-argument token, `at=lift`, is
refused ("is a parameter token or a formula, which would resolve against
the moving child's parameters of the same name"), a reason added after
the probe showed the first draft said only "not a sequence of three
numbers".

## 3.4 Full suite after the implementation

First run (`full-1`, implementation, tests and the manual section and
changelog bullet in place; ADR, architecture, note and warts not yet
edited):

    python -m pytest -q -p no:cacheprovider -rs
    3826 passed, 4 skipped, 53 warnings, 2536 subtests passed in 396.80s (0:06:36)

3816 at the base, minus the replaced
`test_a_freedom_does_not_restate_the_line`, plus eleven new tests:
`RefusalTest` 3 (2.1, 2.2, 2.3), `StatedLineTest` 5 (2.4 to 2.8),
`StatedLineDocumentTest` 2 (2.9), `ManualTest` 1 (4.1). The 4 skips are
the base's. No existing test was edited but the replaced one.

Final run (`full-2`), with every section 0 to 4 edit in place (the
refined token reason and the corrected manual clause included):

    python -m pytest -q -p no:cacheprovider -rs
    3826 passed, 4 skipped, 53 warnings, 2536 subtests passed in 402.24s (0:06:42)

## 4.1 The manual

Under `skills/write-the-manual`:

- **Red first:** `ManualTest::test_the_joints_page_states_a_line_across_a_connector`
  ran red on the unedited page, `IndexError: list index out of range`
  (the *Frames and mates* section had one code block).
- **Written**, folded into `docs/concepts/joints.rst`, *Frames and
  mates*: a frame's `z` is the line "by default"; the joint bullet says
  "unless the freedom states its own line"; a new passage and a second
  complete example on the public contract -- a robot arm's shoulder
  whose connector's `z` stands across the joint line, the freedom
  stating `axis=(0, 0, 1), at=(0, 0, 0)` -- saying the frames fix the
  rest and the zero and the freedom the line, each of `axis` and `at`
  defaults to the frame's, `at=(0, 0, 0)` written is the part's origin,
  nothing checks a stated line against the frames, and a stated line is
  numbers and why; the freedom paragraph and the refusal list updated
  (the list loses "states an `axis` or `at`" and gains the non-numeric
  and zero-length line). The test EXECUTES the example and checks the
  installed joint's line `(0, 0, 1)` through `(0, 0, 0)`, the bound turn,
  the rest `180` and `(0, -68, 123)`, and that the prose states
  `(0, -68, 123)`. No project is named (skill rule 3).
- **Build:** `python -m sphinx -E -b html -n -W --keep-going docs <out>`
  reports the same 5 warnings the parent change recorded at its base
  (`api.rst:23/35/76`, two `Sim` docstrings); none on a page or docstring
  this change touched. The built `concepts/joints.html` was read; one
  clause of the first draft was wrong -- it said the shoulder's line runs
  through the link's origin "rather than the connector's", but the
  connector's origin `(0, 0, 68)` is on the same line -- and was
  corrected. `reference/api.html` renders the new `Frame` docstring.
  `tests/test_docs_structure.py` and `tests/test_profile_documentation.py`
  pass.

## 4.2 Changelog

`docs/project/changelog.rst`, *Unreleased*: a second bullet, "A mate's
freedom may state its own line", in the moving part's own frame, the
frames still fixing the rest, each default the frame's (ADR-148). The
status page's *Since |release|* paragraph already covers frames and
mates as unreleased and needed no change.

## 4.3 Record for the studio

The studio's `shop-skills/machinome-api/SKILL.md` (the framework's
complete public contract, in the separate `machinome-studio`
repository) must gain the stated line: as a mate's freedom,
`Revolute(axis=(x, y, z), at=(x, y, z), range=..., unit=...)`, three
numbers each, read in the moving child's own frame, each left out
taking the moving frame's `z` or origin; `at=(0, 0, 0)` written is the
child's origin; the frames still fix the rest placement and the zero;
refused at class creation: a stated line that is a token, formula,
callable or not three numbers, and a zero-length axis. The refusal of a
stated line it may still list goes. That is a separate change in that
repository, made by someone else; nothing of it is made here.

## 4.4 ADR and architecture

`docs/adrs/NODE/ADR-148-a-mates-freedom-may-state-its-own-line.md`,
**Accepted**, written after `full-1` confirmed the design; ADR-147 gains
an *Amended by* line; `docs/adrs/README.md` indexes ADR-148 under NODE
and marks ADR-147 "amended by 148". `docs/architecture.md`: the
Kinematics mate paragraph (the freedom's stated line, `_check_stated`;
the installed joint's axis and anchor, stated else the frame's
DECLARED, read in the child's frame, the frames fixing rest and zero),
its ADR citation, and the Map rows *Node model* and *Motion* gain 148.

## 4.5 The working note

`workflow/ongoing/mates-and-sketches.md`: §5 records the cut into
`state-the-mate-line`; §5.1's "`z` is the line a revolute turns about"
becomes "BY DEFAULT" and §5.2's freedom paragraph gains the stated line
in the moving child's own frame, both marked *(corrected 2026-09-26,
state-the-mate-line)*; §6's first candidate records the follow-up cut.

## 4.6 Warts

`workflow/warts.md`, the `place-parts-by-mate` findings: the first two
bullets gain **Reopened and fixed, 2026-09-26, by `state-the-mate-line`
(ADR-148)**, pending Thor's follow-up (tasks §6).

Not done here (the orchestrator's, after review): 5.1 (spec sync,
archive, commit) and section 6 (Thor, in Thor's own repository).

## Where the implementation departs from, or clarifies, `design.md`

None contradicts a ratified behaviour.

1. **A whole-argument token or formula** (`at=lift`, not only
   `at=(0, 0, lift)`) gets its own reason, "a parameter token or a
   formula", rather than "not a sequence of three numbers"; the spec's
   list names tokens, formulas and callables, and a probe showed the
   first draft's wording for the whole-argument case said less.
2. **A sequence spelled as a list** (`axis=[0, 0, 1]`) is accepted, as
   "a sequence of three real numbers" (design decision 5) reads; it is
   passed to the joint unchanged.
3. **Fixtures:** the twins and verbatim connectors live in
   `tests/mate_project/verbatim.py`, the line-stating mates in
   `tests/mate_project/line.py`, so the no-line guards import at the
   base; the 0.4 root over `MatedHousing` is
   `tests/mate_project/arm.py:MatedShoulderMachine`.
4. **2.9's twin-root comparison** also runs 2.6's comparison rules on
   the published operations (the driver token `angle` compared as a
   token, numbers within `1e-9`), and requires every mated node entry's
   field set to be one the twin document publishes.

## 5.1 Sync and archive (the orchestrator, after review)

The reviewer re-ran the full suite from a clean shell (`3826 passed, 4
skipped, 2536 subtests`, the applier's counts), built the manual with
`-n -W` (the same five pre-existing warnings, none on a touched page),
validated the change `--strict`, and probed outside the suite: the
verbatim shoulder at 47, the wrist at -63 and the reversed yaw at 30
against hand-derived world matrices (deviation `4.4e-16`, `0`, `0`) and
against their twins (`0`); the sentinel identity of a written `at`; and
the refusals of a `Driver` component, a whole-argument token, a numpy
integer axis, a string, a `1e-10` axis and a `None` component, each
naming the mate and the argument (`evidence/review_probes.py`).

`openspec archive` refused the `mates` delta: its MODIFIED block for "An
assembly mates a child's frame onto another frame" does not carry the
baseline scenario "A freedom does not restate the line", and the CLI
treats any scenario missing from a modified block as an accidental drop,
with no way to state a deliberate one. The drop is deliberate and
ratified -- the behaviour inverted, and the delta replaces the scenario
by "A freedom states the line across its attachment frame", "A freedom
may state its anchor alone", "A stated line is numbers" and "A stated
axis has a direction". The two ratified MODIFIED blocks (`mates`,
`joints`) were therefore applied to `openspec/specs/` verbatim by a
script that does what the CLI does minus that refusal
(`evidence/sync_modified.py`), the result checked with
`openspec validate --specs --strict` and by a search for the old
wording, and the change archived with `--skip-specs`.
