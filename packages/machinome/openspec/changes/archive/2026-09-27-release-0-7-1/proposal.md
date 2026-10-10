## Why

Machinome 0.7.0 was uploaded to PyPI on 26 September 2026. Since the
tagged 0.7.0 commit, `main` has taken thirty-three commits that the
manual still describes as unreleased: the status page has a "Since
0.7.0" section and the changelog an *Unreleased* section. They hold
frames and mates, the way a part is placed by its connectors and freed
in one sentence (ADR-147, ADR-148, ADR-150 to ADR-155; from a robot
arm's elbow, then two handed arms, a gripper, a quadruped's bought parts
and a calculator's dials), the `machinome vet` command (ADR-149), and
three corrections found while the calculator moved onto mates. On
27 September 2026 the pilot decided to release them as **Machinome
0.7.1**, with the viewer renumbered 0.7.1 beside it, and to leave the
distributions ready for upload. Every record still says 0.7.0.

## What Changes

- **The version is 0.7.1.** `pyproject.toml`, `machinome/__init__.py`,
  `machinome/vet/universe.toml`, `setup.cfg` and `docs/conf.py`'s
  `release` move together, as `setup.cfg`'s bumpversion table names
  them. `docs/conf.py`'s release facts state 27 September 2026 and the
  matching viewer 0.7.1; viewer API 27 and document versions 1 to 13 are
  unchanged, because nothing in 0.7.1 changes the published document.
- **The changelog's *Unreleased* section becomes *Machinome 0.7.1*,**
  dated, rewritten as a story for readers: frames and mates first, in
  the order a maker meets them, then `machinome vet`, then the
  corrections. Three items on `main` have no bullet at all today and
  gain one: `machinome vet` (ADR-149), the source-qualified identity of
  an imported part's wrapper (ADR-155) and the stable recovery of a
  mate's rest rotation. No *Unreleased* section remains.
- **`HISTORY.rst` gains the 0.7.1 section** above 0.7.0, with the ADR
  numbers and the originating machines, in the shape of the 0.7.0
  section.
- **The status page describes 0.7.1 as released:** its "Since 0.7.0"
  section goes, "What 0.7 is" names frames, mates and vet, and no page
  says unreleased. The release note under `docs/releases/` gains a
  0.7.1 section, since the release has a one-page story.
- **The status page's first sentence renders its facts.** The 0.7.0
  manual on Read the Docs says "Machinome |release| was released on
  |release_date|", literally: a substitution inside a bold sentence is
  not resolved. The sentence loses its bold and a test refuses the
  shape on every page.
- **The vet fixtures are committed.** The suite and CI have been red
  on eleven `test_vet_*` tests since `vet-the-project` landed:
  `.gitignore` ignores `parts/`, so the three fixture packages
  `tests/vet_projects/{pure_project,star_import,init_on_path}/sim/parts/`
  were never committed. They are restored from the bench that still held
  them and the rule gains a negation for the fixtures.
- **`context7.json`** states 0.7.1, the viewer 0.7.1, and gains a rule
  for frames and mates and one for `machinome vet`.
- **Tests pin the release facts** by the version `pyproject.toml`
  states rather than by a literal, so the next release moves one file
  and the tests follow: the four version files agree, the changelog's
  top entry is that version with its date and names the mate and the
  vet command, `HISTORY.rst`'s top entry is that version, and the
  status page describes no unreleased work. The three tests that today
  require the mate, or the precision change, to sit *above* the 0.7.0
  section are repointed to the 0.7.1 section.
- **No source, document or viewer change.** The document format is
  unchanged; a 0.7.0 viewer reads a 0.7.1 export.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: "Explicit frame direction precision is documented
  narrowly" no longer requires the precision change under *Unreleased*
  but in the 0.7.1 section that ships it; "Profile contact is documented
  as a current-source, pointwise capability" stops describing profile
  contact as current-source, since 0.7.0 shipped it; a new requirement,
  "The 0.7.1 release is recorded", states where the release facts live
  and that they agree.
- `framework-identity`: "Version 0.7 records the rename lineage" says
  the *first* Machinome release is 0.7.0, not the *next*, and that later
  0.7.x releases keep that material and add their own entries.

## Impact

`pyproject.toml`, `setup.cfg`, `machinome/__init__.py`,
`machinome/vet/universe.toml`, `docs/conf.py`, `docs/project/changelog.rst`,
`docs/project/status.rst`, `docs/releases/release-0.7.rst`, `HISTORY.rst`,
`context7.json`; `tests/test_machinome_identity.py`, `tests/test_mates.py`,
`tests/test_frame_precision_docs.py` and a new `tests/test_release_records.py`.
The viewer's own renumbering is its own change in its own repository
(`release-0-7-1` there); the studio's contract skill already describes
every 0.7.1 capability. Tagging, pushing, uploading and the Read the Docs
builds remain the pilot's.

Standalone cycle on framework `main` base `fabfc3d`, branch and worktree
`release-0-7-1` at `machinome/WTs/release-0-7-1`, integration target
framework `main`.
