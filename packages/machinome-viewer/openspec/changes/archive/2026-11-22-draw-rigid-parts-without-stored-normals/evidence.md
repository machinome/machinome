# Evidence: draw-rigid-parts-without-stored-normals

Recorded by the applier, 22 November 2026, in the worktree
`machinome/WTs/draw-rigid-parts-without-stored-normals` (branch of the same
name, planning commit `1fb2f49e` above base
`6aee67ef9dc5453ea6ff731f3f692b0f7473fdf0`). Tasks 1.2 to 5.2, 6.1 and 7.1.
Task 6.2 (the Enigma page and the comparison of pictures with the base) and
7.2 are the reviewer's and are not recorded here.

Every run below was made one at a time: the widget's files with the bench's
`node_modules/.bin/vitest`, the browser tests with the bench's `.venv`
Python from `packages/machinome-viewer`, in the suite's Chromium (Playwright,
`--use-angle=swiftshader --enable-unsafe-swiftshader`).

## The two bundles

| Bundle | SHA256 |
|---|---|
| Built from the base source (task 2.3) | `0ecadb1e8523bc46d9c289e17367a185d41261096be5fa86df200c7807c4caad` |
| Built from the implementation (task 4.3, and again after 4.4) | `3ee8073f3a676d6657098eaab58be824763a8e5c281682187a9d9e79d7d7f6e8` |

Both were built by `npm run build` in the widget directory. The rebuild
after the mutations of 4.4 gave the implementation's SHA256 again. Copies
were left for the reviewer outside the worktree, as `bundle14-base.js` and
`bundle14-change.js` in the session's scratch directory.

## 2.2: the widget tests on the base source

`src/rigid-part-normals.test.ts` on the base source: 5 failed, 1 passed.
Each red test failed at the clause the design gives it, never at an
import, a fixture or a setup step:

```
× N1  AssertionError: mount: a's attributes: expected [ 'normal', 'position' ] to deeply equal [ 'position' ]
× N2  AssertionError: mount: a's attributes: expected [ 'normal', 'position' ] to deeply equal [ 'position' ]
× N3  AssertionError: plain: part 0's flatShading: expected false to be true
× N4  AssertionError: the part's attributes: expected [ 'normal', 'position' ] to deeply equal [ 'position' ]
× N5  AssertionError: the rigid flag: expected false to be true
✓ N6
```

N4 failed only at its last clause (the part's attributes): every decal
assertion before it (indexed, `normal` and `position`, arrays equal to
`liftDecal` of a fresh parse with its normals computed, the material
smooth, double-sided, offset -1/-1) passed on the base. N5's counts (two
appearances of the kinds `rigid` and `flexible`, two materials) and its
flexible flag passed; it failed at the rigid flag. N1 and N2 stop at their
first clause, the attribute; that their other clauses also bite on the base
is shown by the mutations (MU3 turns N1 red at the computation clause,
MU2 at the flag).

The file was edited once after this run (N2's second-viewer checks
reordered after MU11, below) and run on the base source again (the base
`tree.ts` and `flexible.ts` copied back, confirmed equal to `HEAD` by
`git diff --quiet`, then the implementation restored and confirmed
byte-equal): the same five failures with the same messages, N6 green.

## 2.3: the browser tests on the base bundle, and what was recorded

`tests/test_rigid_part_normals.py` alone, with the base bundle in
`dist/`: 1 failed, 5 passed.

```
FAILED R1  AssertionError: 6 != 3          (R1 mount {'created': 6, 'deleted': 0, 'bytes': 434016})
passed R2, R3 coloured, R3 inside out, R3 colourless, R3 marked
```

R1's document is the cube (12 facets), the sphere (3,968) and the cylinder
(2,048): 18,084 vertices, so positions alone are 217,008 bytes in three
buffers. The base created six buffers of 434,016 bytes: two a geometry,
twice the bytes, the stated reason.

Recorded on the base bundle, written into the test, and not recorded again:

- **R2**: the marked fixture created 13 buffers of 49,788 bytes at mount
  and its unmarked twin 4 of 36,864, each in a page of its own, at the
  bench view of `test_widget_e2e.py`: the markings add **12,924 bytes**.
- **R3, the coloured cube** (`#c08040`, faces +x, -y, +z, indices 0, 1, 2):
  order from the brightest **[2, 0, 1]** in every look; gaps **[52, 55]**
  plain, kept among the others and hidden and shown; **[17, 14]** lit (in
  each of the three modes); **[37, 32.24]** dimmed among the others;
  **[8.08, 7.96]** ghosted among the others; spreads **[0, 0, 0]** but
  **[0, 1, 0]** dimmed and **[0, 1, 1]** ghosted among the others. Face
  means plain: (122, 81, 40), (94, 63, 31), (147, 98, 50).
- **R3, the inside-out cube** (faces -x, +y, -z, whose inner sides it
  shows): order **[2, 0, 1]**, gaps **[52, 55]**, spreads **[0, 0, 0]**;
  the same means as the outward cube's faces facing the same way.
- **R3, the colourless cube**: strongest channel **[2, 2, 1]** (blue, blue,
  green) and spreads **[0, 0, 0]** in every look. Means plain: (203, 81,
  219), (25, 93, 195), (128, 241, 185); ghosted among the others (247, 229,
  250), (221, 231, 246), (236, 253, 245).
- **R3, the marked bench**: **1,309** pixels changed by more than 24 in a
  channel against the unmarked twin, of which **1,165 (0.89)** are neutral
  (channels within 20) and at least 60 in their darkest channel. The floor
  was chosen from the base's distribution of the changed pixels' darkest
  channel (5th percentile 73, 10th 78, median 155); a share of 0.89 at 60,
  0.80 at 80, 0.76 at 100.

### How R3 samples and judges

- The host is 321 by 241. The view is set by `setView` with camera, target,
  `up` (0, 0, 1) and `fov` 35, so the test projects points itself: the
  cube's (side 40 mm) camera is at (95, -70, 60) looking at the origin,
  which shows the +x, -y and +z faces. The marked bench uses
  `test_widget_e2e.py`'s `BENCH_VIEW`.
- A face is sampled at a 5 by 5 grid of points over the middle 60 per cent
  of it, projected with three.js's perspective camera arithmetic, written
  in the test (`project`). Its brightness is the sum of its three channel
  means; its spread is the widest range of one channel over the 25 samples.
- The looks: plain; lit with the others kept, dimmed and ghosted; among the
  others (a small second part lit) kept, dimmed and ghosted; hidden and
  shown again. Each is made, the view set (a draw, the mount being
  `on-demand`), the host photographed, then put back.
- Judged, for the coloured and the inside-out cube: no face's brightest
  channel mean below 24 (black); every face's spread at most its recorded
  spread and one step; the order from the brightest the recorded one; every
  gap at least half the recorded gap. For the colourless cube: no face
  black, the spread as above, each face's strongest channel the recorded
  one, and every pair of faces apart by more than 8 in some channel
  (three colours). For the marked bench: at least half the recorded count
  of changed pixels, and the share of them showing a marking's colour no
  less than the recorded share less 0.05.

Before recording, the margins were tried on the bundle the proposer built
from a prototype of the design (`p14-bundle-change.js` in the session's
scratch directory, not part of the change): every measured value equal to
the base's but the colourless cube's third face, spread 1 where the base
had 0 (its red mean 127.5 for 128). Nothing was recorded from it.

## 3.2: the implementation

`tsc --noEmit`: no output, exit 0. `src/rigid-part-normals.test.ts`: 6
passed.

## 4.1 and 4.2: the existing widget tests

Each changed file run alone and green: `src/tree.test.ts` 71 passed,
`src/share-one-geometry.test.ts` 55 passed, `src/shared-materials.test.ts`
25 passed. In `shared-materials.test.ts`, `side=0 polygonOffset=false
flatShading=false` occurred 148 times before the edit, all inside
`O1_EXPECTED`, and 0 times after; `flatShading=true` went from 21 to 169
lines and the 42 marking lines (`side=2 polygonOffset=true
flatShading=false`) are untouched. No other line of the file changed but
the comment above `O1_EXPECTED` and the oracle's `case 'rigid'` with its
comment.

The 21 files of 4.2, run singly and unmodified, all green:
`share-one-geometry-viewer` 5, `color` 22, `assembly` 14, `clockedControls`
21, `document` 65, `expression-reuse` 9, `draw-on-change` 62,
`expression-lifetime` 11, `flexible` 32, `flat-pass` 41, `flat-pass-parity`
52, `inspector` 22, `navigator` 26, `presentation` 18, `geometry-admission`
15, `follow-the-slider` 55, `navtree` 40, `picture-revision` 22,
`parent-adversarial-geometry` 12, `flexible-rebuild` 18, `partSurface` 36.

## 4.3: the browser tests on the implementation's bundle

- `tests/test_share_one_geometry.py` alone, B1's counts changed: 3 passed.
  `B1 mount {'created': 2, 'deleted': 0, 'bytes': 288}`, `B1
  artifactChanged {'created': 3, 'deleted': 1, 'bytes': 432}`, `B1 dispose
  {'created': 3, 'deleted': 3, 'bytes': 432}`.
- `tests/test_rigid_part_normals.py` alone, nothing re-recorded: 6 passed.
  `R1 mount {'created': 3, 'deleted': 0, 'bytes': 217008}`; R2 11 buffers
  of 31,356 bytes against 2 of 18,432, 12,924 added; R3 every value as on
  the base but the colourless cube's third face (red mean 127.52, spread 1,
  within 0 and one step); the marked bench 1,309 changed, 1,165 coloured.

## 4.4: the mutations

Each applied alone to the implementation by a scratch script making exact
replacements, run, then the three files it may touch (`tree.ts`,
`presentation.ts`, `flexible.ts`) restored from saved copies and confirmed
byte-equal (`filecmp`, shallow off) before the next.

| | Mutation as applied | Widget tests red (the design's in bold) |
|---|---|---|
| MU1 | the reading's `deleteAttribute` line removed | **N1**, **N2** (attributes), N4 (the part's attributes) |
| MU2 | `material.flatShading = true` removed from `RIGID` | **N1**, N2 (flag), **N3** (flag), N5 (rigid flag) |
| MU3 | `computeVertexNormals()` then `deleteAttribute` in the guarded step | **N1** ("a normal computed for a"), N2 (same) |
| MU4 | `flatShading: true` in both of `materialForColor`'s constructors | **N4** ("own's flatShading"); `shared-materials`: **P1**, O1, P2 "a marking ghosted keeps its two sides and its polygon offset" |
| MU5 | `welded.computeVertexNormals()` removed from `liftDecal` | **N4** ("own's attributes: [ 'position' ]") |
| MU6 | no removal in the reading; `copy` removes it | **N1** (attributes), N2, N4 |
| MU7 | no removal in the reading; `loadMesh` removes it from `share.value` after `mesh.geometry = share.value` | **N1**, at "the reading's removals: [ 'normal', 'normal' ]" (two parts each removed it, after their mesh held it) |
| MU8 | `variant.flatShading = false` after `appearance.plain.clone()` in `presentation.ts` | **N3** ("coloured hovered: part 0's flatShading") |
| MU9 | `RIGID` made `FLEXIBLE` | **N5** (one appearance, not two) |
| MU10 | the removal outside the `try` | **`tree.test.ts`, the rewritten preparation test** ("dispose to be called 1 times, but got 0 times"); `rigid-part-normals` green |
| MU11 | the reading hands a clone without normals, keeping its parse (in `userData`) for `copy` to clone | **N2** ("second viewer: a's attributes: [ 'normal', 'position' ]"), N1 (shown geometries are not the parses) |

Every mutation turned its named tests red. The reds beyond the design's are
listed in the table.

Then each of four bundles built and the browser tests run alone:

| | Bundle SHA256 | Red | Green |
|---|---|---|---|
| MU1 | `ac8dd92a0c3b2667e83a575819636c8c1d762f0fd55214ee977bc4c1429f956e` | **R1** (6 != 3); `test_share_one_geometry.py` **B1** (4 != 2) | R2, every R3, B2, B3 |
| MU2 | `2cd62b6bf511f116bbda70ed6bf81c16b3883235af22db83ca5ea99e10461ef7` | **R3**: the coloured cube black in every look but ghosted (means 0, 0, 0; ghosted 217, 217, 217 on every face), the colourless black (strongest [0, 0, 0]), the inside-out black | R1, R2, R3 marked |
| MU5 | `e72b205b2bdbaac106db01adf1ca93011374de5806e7c1019f6f5f2e734d4094` | **R2** (8,292 != 12,924); **R3 marked** (1,337 changed, 88 coloured, a share of 0.066) | R1, R3 coloured, inside out, colourless |
| MU8 | `a522e018c7d4c797e95987334cbf7c567e1b3dabd6503e9f412b4d8b13b11582` | **R3**: the coloured cube black when lit (all three modes) and dimmed, 217 grey on every face ghosted; the colourless ghosted 217 grey | R1, R2, R3 plain looks, inside out, marked |

The bundle rebuilt from the restored implementation had SHA256
`3ee8073f…f6e8` again.

## 5.1 and 5.2: the gate

- Whole widget suite (`vitest run`, once): 78 files, 77 passed and 1
  skipped; 2,121 tests, 2,119 passed and 2 skipped, none failed (66.3 s).
  The skips are the suite's own, on unset environment variables:
  `src/run/profile-contact.test.ts` (one test, `it.skipIf(!process.env.
  CURTA_PROFILE_V13_DOCUMENT)`) and `src/run/profile-installed-benchmark.
  test.ts` (its one test, `it.skipIf(!process.env.
  CURTA_INSTALLED_PROFILE_DOCUMENT)`).
- `tsc --noEmit`: no output, exit 0.
- Python suite, with the bundle of 4.3 (`3ee8073f…f6e8`), once: **1
  failed, 303 passed, 3 skipped** (328.9 s). The skips: two in
  `test_curta_drawing.py` (375, 469), "the Curta's own builds are not at
  …/WTs/projects/Calculators/Curta-Type-I-3x/_build"; one in
  `test_follow_the_slider.py` (380), "Playwright's firefox is not installed
  at the revision it expects". The failure is a finding, below; task 5.2 is
  not ticked.

### Finding: an existing browser test does not hold

`tests/test_widget_e2e.py::OnDemandClockedTest::test_a_clocked_machine_mounts_on_demand_and_poses_by_restore`
fails on the implementation's bundle, every time (run alone twice, the
same numbers), and passes on the base bundle:

```
restore alone: 13775 pixels from the origin, 782 from the setView frame
>       self.assertLess(refit * 20, moved, 'restore alone left a stale frame')
E       AssertionError: 15640 not less than 13775 : restore alone left a stale frame
tests/test_widget_e2e.py:2165
```

On the base bundle, alone: `restore alone: 6198 pixels from the origin, 44
from the setView frame`, passed.

The test counts the pixels whose grey level differs at all (`convert('L')`,
any non-zero difference) between three frames of the calculator fixture:
the origin, the pose a `restore` draws by itself, and the same pose after
`setView(viewer.view())`, which re-fits the near and far planes. It asks
that the second pair differ on fewer than a twentieth of the pixels the
first pair does. Measured by a scratch copy of its steps, the largest
channel difference of each pair (RGB, not grey):

| Pair | Base: pixels (by 1 / 2-3 / >3, max) | Implementation |
|---|---|---|
| origin, restore alone | 7,998 (175 / 991 / 6,832, 121) | 15,588 (7,764 / 992 / 6,832, 121) |
| restore alone, after `setView` | 91 (71 / 6 / 14, 41) | 835 (812 / 9 / 14, 41) |
| origin, after `setView` | 8,000 (178 / 987 / 6,835, 121) | 15,852 (8,029 / 988 / 6,835, 121) |

Every pixel the change adds differs by one step: the pixels by more than
one step are the base's to within three. So the facets' derivative normal
moves the lit colour by a step at thousands of pixels when the pose moves,
and at about 740 when only the near and far planes are re-fitted, which a
stored normal did not; this is the "within one step" the design states,
but the test's ratio counts one-step pixels as it counts a stale frame. The
design (Decision 9, "Existing Python tests that change") did not list this
test, and named `test_widget_e2e.py` among those whose margins are tens of
steps. The test was not changed: whether it should count one-step pixels,
or this change should not make them, is the reviewer's and the pilot's.
The design's claim that a frame's picture depends on "the geometry and the
view, not on the order of arrival" still holds; what this shows in addition,
is that, in SwiftShader, the derivative normal's rounding depends on the
projection's near and far planes, which a stored normal's did not.

## Deviations from the design, and what it left open

- **The mocked loader (N1 to N6).** `STLLoader` is mocked as a subclass of
  the real one whose own `parse` calls the real parse and whose `loadAsync`
  parses bytes registered for the URL; the spy on `parse` is on that
  subclass's prototype. The references of N4 parse with the real class,
  outside every watch.
- **N1's "before the first mesh held it".** The `deleteAttribute` spy
  records whether any mesh made by `MaterialPresentation.prototype.mesh`
  already shows the geometry. Under MU7 N1 went red at the clause just
  before it (a parse had two removals, one by each part) rather than at
  that one; both are true of MU7.
- **N2's order.** The second viewer's checks were first written with the
  identity checks before the attributes; under MU11 N2 then went red at
  "the first viewer holds the parse", not at the copy's normals. They were
  reordered so that both viewers' attributes are checked first, and MU11
  was run again (red at the second viewer's attributes), as was the base.
- **N3** also hovers each part while it stands among the others, and checks
  every part of the tree in every look, not only the two named.
- **N6** casts nine rays a direction (a 3 by 3 grid over each part's box)
  in two directions, straight down and oblique, through three parts, one
  rotated, and compares object, distance, point, face index and face
  normal with twins built from a copy of each part's positions with
  `computeVertexNormals`. The wedge does not fill its box, so it asks
  that at least nine of a part's eighteen rays reach it.
- **R3's shape** (left to the applier): as described above. It adds a
  "hidden and shown" look, from the requirement's scenario "Every look
  keeps the shading"; it judges the colourless cube in every look, not
  only plain; it asks that the three colourless faces differ (a constant,
  8, not a recorded number). The page hides the full-screen button as
  `test_widget_e2e.py`'s marked harness does, so no overlay reaches a
  sample.
- **R2** mounts each document in a page of its own, so that each count is
  one canvas's from its first context.
- **The mutations' spellings**, where the design names an effect: MU4 sets
  the flag in both of `materialForColor`'s constructors; MU5 removes only
  `liftDecal`'s `computeVertexNormals` (its `deleteAttribute` stays, which
  after the change is the same input to the weld); MU9 makes `RIGID` the
  `FLEXIBLE` kind; MU11 is written in `tree.ts` alone (no change to
  `geometry-admission.ts`), the reading returning a stripped clone and
  keeping the parse for `copy`.
- **The rewritten preparation test** in `tree.test.ts` keeps its error
  text, "normal preparation failed", which still names what the step
  prepares.
- **The `flexible.ts` comments.** Both now say a rigid part is shaded flat
  too; the second also names the two kinds, since the materials' values
  are now the same as the rigid kind's and only the kind keeps them apart.
- **The CHANGELOG bullet** was written while the Python suite of 5.2 was
  running. Two tests of that suite read the CHANGELOG
  (`test_documentation.py`, `test_version.py`); either text satisfies them,
  and both files were run alone again afterwards: 16 passed.
- No sentence of the proposal, the design, the delta or the tasks was found
  that still disagrees with the design's "Corrected in review" (searched
  for stored pictures, `base.json`, R4, skips and recordings). No fact the
  design states about three.js 0.156.1 that this work relied on was found
  false: `STLLoader` sets `position` and `normal` and no index (binary
  257-258, ASCII 360-361); `deleteAttribute` is `delete
  this.attributes[name]`; `WebGLGeometries.update` uploads every attribute
  a geometry has; `MeshStandardMaterial.copy` (114) and
  `MeshNormalMaterial.copy` (53) copy `flatShading`; `flatShading` defines
  `FLAT_SHADED`, under which `normal_fragment_begin` takes the derivative
  normal. The counts B1 gives (2, then 1 and 1) are the design's.

## The reviewer's record (tasks 5.2, 6.2, 7.2, 7.3)

Recorded by the reviewing agent on 22 November 2026, after the applying
agent stopped on the finding above with task 5.2 open.

### The finding the applying agent stopped on

`tests/test_widget_e2e.py`, `OnDemandClockedTest`,
`test_a_clocked_machine_mounts_on_demand_and_poses_by_restore`, failed on
the implementation and passed on the base. It compares the frame `restore`
draws by itself with the frame after a `setView` of the same view, which
differ only by the re-fit of the near and far planes, and it counted every
pixel whose grey level differed at all. With a normal taken from the
derivatives of the position, a re-fit moves the rounding of that
arithmetic by one step at several hundred pixels, where with a stored
normal it moved it at a few dozen: the applying agent's table above. No
pixel that differs by more than three steps is new.

The test's subject is a stale frame, which differs by tens of steps over
thousands of pixels. Its `changed()` now leaves out a pixel that differs
by one grey step, with a comment naming this change; nothing else in the
test moved. Run alone after the edit: on the implementation's bundle
`restore alone: 2844 pixels from the origin, 9 from the setView frame`,
on the base bundle `2741` and `9`; passed on both. Its other assertions,
that the same bank and view draw the same frame exactly, passed on the
implementation before the edit and still do.

This is a property of the change and not of that test alone: a one-step
rounding now moves from frame to frame. It is stated in the decision
record and told to the pilot.

### What the review read, and what it changed

The diff of `src/tree.ts` and `src/flexible.ts` was read against design
Decisions 1, 3, 4 and 10. No source line was changed in review. One
existing test was changed in review, the one above.

### Faults planted in review

Eight, each applied alone to the committed `tree.ts`, with five test files
run (`rigid-part-normals`, `tree`, `shared-materials`,
`share-one-geometry`, `share-one-geometry-viewer`) and the source restored
and checked by digest; the verdict first seen green on a replacement that
changes nothing and red on a reading that keeps its normals (7 tests).

| Fault | Red |
|---|---|
| A part with no colour is left with the smooth material | N1, N2, N3, and `shared-materials` O1, P1 and two more |
| A coloured part is left with the smooth material | N1, N2, N3, N5, and fourteen of `shared-materials` |
| A further viewer's copy is given normals | N2 |
| A marking's material is made flat | N4, and `shared-materials` O1, P1 and "a marking ghosted" |
| A reading whose preparation throws is handed out all the same | `tree` (the reading's preparation rejects) |
| A marking's decal loses its normals once it is lifted | N4 |
| The attribute removed a microtask after the reading returns | `tree` (the reading's preparation rejects): the guard no longer covers the removal. The removal itself still comes before any part or copy, so N1 holds, rightly |
| A coloured file's colour attribute removed with the normals | N1 |

None stood. No test was added in review.

### Gates on what is committed

- `tsc --noEmit`: no output, exit 0.
- The whole widget suite, once: **78 files, 77 passed and 1 skipped; 2121
  tests, 2119 passed and 2 skipped; no failure.**
- The bundle built from the committed source: SHA256
  `3ee8073f3a676d6657098eaab58be824763a8e5c281682187a9d9e79d7d7f6e8`, the
  applying agent's.
- The viewer's Python suite on that bundle, once, with the edited test:
  **304 passed, 3 skipped, no failure** (5 min 30 s); the skips are the two
  Curta builds that are not on this machine and the Firefox leg of another
  change's test.

### The comparison with the base, on the proposal's cases (task 6.2)

The base bundle (`0ecadb1e…`) and the implementation's (`3ee8073f…`), as
the applying agent left them, each serving the same hand-written model
files and the suite's marked fixture to the suite's Chromium (SwiftShader,
a 321 by 241 host, `on-demand`), by the proposer's script with only the two
bundles' paths changed: 103 pictures, 7,968,183 pixels.

| Document | Pictures | Pixels differing | By more than one step | Largest |
|---|---|---|---|---|
| A 40 mm cube, eight views and each highlight mode | 11 | 28 | 0 | 1 |
| The cube with no colour | 8 | 7,094 | 0 | 1 |
| The cube wound inside out | 8 | 66 | 0 | 1 |
| A sphere of 64 by 32 segments, eight views and highlights | 11 | 51 | 0 | 1 |
| The sphere with no colour | 8 | 252 | 0 | 1 |
| The sphere from 3,000 mm | 4 | 0 | 0 | 0 |
| A cylinder of 512 sides | 8 | 107 | 0 | 1 |
| Four parts on three files, every highlight mode | 7 | 908 | 0 | 1 |
| The marked fixture, six views and highlights | 12 | 7,574 | 0 | 1 |
| A plate seen 5 to 0.1 degrees above its plane | 7 | 81 | 80, all at 0.2 degrees | 14 |
| The plate with no colour, 0.5 to 0.2 degrees | 3 | 80 | 80, at 0.2 degrees | 64 |
| The cube with a zero-area triangle on an edge of each facet | 8 | 60 | 32 | 40 |
| The same with no colour | 8 | 7,124 | 32 | 63 |

The figures are the proposal's, pixel for pixel: 77 pictures within one
step, and 224 pixels by more in the two cases it named.

### The Enigma I page (task 6.2)

`projects/enigma-i` at `081f4e6`, its built page served on this machine
only, by the method of `workflow/evidence/enigma-page-memory-2026-11-22.md`:
a probe build of this bench's source beside one of framework `main` at
`6aee67ef`, each with molejo's `main`. One run of each for the memory,
draw calls counted and not executed; four loads of each for the time;
two runs of each for the pictures, really drawn in software.

| One open copy | Base | This change |
|---|---|---|
| All browser processes, settled | 3,034 MiB | 2,489 MiB |
| The tab | 1,578 | 1,311 |
| Its typed arrays | 1,039.1 | 770.7 |
| The graphics process | 1,334 | 1,057 |
| Meshes, and geometries | 3,347 on 1,472 | the same |
| The 993 geometries of the parts read from files | 536.7 MiB, positions and normals | 268.4 MiB, positions |
| WebGL buffers alive | 2,997 of 1,029.9 MiB | 2,004 of 761.5 MiB |
| Draw calls asked in the same two frames | 6,694 | 6,694 |
| Peak while the page loads | 3,265 MiB | 2,612 MiB |
| `reload()`: the peak with both models held | 4,581 MiB | 3,579 MiB |
| After the reload, settled | 3,057 MiB; 2,997 buffers alive, 2,997 deleted | 2,513 MiB; 2,004 alive, 2,004 deleted |
| After `dispose()` | no buffer alive | no buffer alive |
| From the click to a ready page, four loads | 10.5 to 12.4 s | 10.1 to 10.7 s |

**Pictures against the base**, sixteen states, thirty-four pictures (on
screen and forced), 605,864 pixels a picture outside the panel's rail. On
both builds what is on screen equals a forced draw in every state.

| State | Pixels that differ | By more than one step |
|---|---|---|
| The mount; after `reload()`; the highlight put back; parts shown again | 508 | 0 |
| The case at 0.4, before and after the reload | 258 | 0 |
| The flap at 60 degrees; a wheel three teeth on | 283 | 1, by 11 |
| A key pressed | 285 | 1, by 11 |
| A key pressed after the reload | 259 | 0 |
| Seen from behind | 203 | 0 |
| The keyboard highlighted, the others kept | 489 | 0 |
| The electrical branch highlighted, the others dimmed | 534 | 1, by 2 |
| The scrambler highlighted, the others ghosted | 364 | 5, by 2 |
| The enclosure hidden | 329 | 0 |
| The enclosure and the electrical branch hidden | 516 | 1, by 2 |

The pixel that differs by 11 is the same one in its three states, at
(460, 473) of the canvas: on the silhouette of a small brass pin a few
pixels wide beside the keyboard, where a facet of a curved part is seen
edge-on. It reads (108, 91, 64) on the base and (97, 83, 60) here. The
pixels that differ by 2 are single pixels in a dimmed, a ghosted and a
hidden state.

**The design's expectations.** One open copy near 2,489 MiB: 2,489. Typed
arrays and buffers each about 268.4 MiB less: 268.4 and 268.4. 2,004
buffers on the same 1,472 geometries: yes. Pictures in the evidence's nine
states about the evidence's counts: the same counts. Under each highlight
mode and with parts hidden, "the same kind": one step, and one to five
pixels by two. The load shorter: 10.1 to 10.7 s for 10.5 to 12.4, which
overlap at their ends; not claimed.

**Not measured.** The time of a frame of a drawn instruction, which the
task names: the script of a frame does not run the shader, and a frame
drawn in software says nothing of a graphics card, so no figure is given
for it. Any graphics card. Another browser.

### The decision record (task 7.2) and the archive (task 7.3)

The measurement confirms the design. ADR-083, its line in
`workflow/adrs/README.md` and the dated pointers in ADR-082 and ADR-056
were written by the reviewing agent, the applying agent having stopped.
The pilot was told, before the implementation was reviewed, of the two
cases in which a few pixels differ by more than a step, and is told with
the result of the rounding that moves with the frame and of the test that
changed for it. Integration into `main`, pushing and publication are the
pilot's.
