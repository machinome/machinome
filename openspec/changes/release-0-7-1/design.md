## Context

The 0.7.0 release was folded three times on 23 September 2026 by editing
the same block of files this change edits: `docs/conf.py`'s release
facts, the changelog, `HISTORY.rst`, the release note, the status page,
`context7.json` and the documentation tests (`b5c8c9d`, `42e5b92`).
`skills/write-the-manual/SKILL.md` ("Release facts are stated once",
"Work after a release", "A release pass") is the procedure; the
*Unreleased* section and the status page's "Since |release|" paragraph
are exactly the shape it prescribes for work after a release, and a
release turns them into the version section and drops the caveat.

Since 0.7.0 the changelog's *Unreleased* section was written one bullet
per cycle, as each cycle's proposal required. Three cycles wrote no
bullet: `vet-the-project` (a new command), `external-wrapper-cache-identity`
and `stable-mate-rotation-conversion` (two corrections a reader may
meet as a rebuild or a changed pose readout).

## Goals / Non-Goals

**Goals:**
- Every reader-facing record states 0.7.1, released 27 September 2026,
  with the viewer 0.7.1, API 27, document versions 1 to 13.
- The changelog tells a maker what 0.7.1 gives, in families, in one
  reading, with nothing 0.7.1 ships left out.
- The tests refuse the state being fixed: a version file left behind, a
  changelog whose top entry is not the released version, a status page
  that says unreleased.

**Non-Goals:**
- No source change, no document version, no viewer API move.
- No new manual page: the release is folded into the pages that own the
  subjects (`concepts/joints.rst` and `reference/cli.rst` already teach
  frames, mates and vet).
- Tags, pushes, uploads, Read the Docs and Context7 submissions.

## Decisions

1. **A patch number, 0.7.1.** Frames and mates compile to the rest
   placement, joint and coordinate a 0.7.0 document already carries; a
   0.7.0 viewer reads a 0.7.1 export and the API stays 27. Nothing is
   removed or renamed. The framework is pre-1.0 and 0.7 is one line;
   a minor bump would announce a document or contract change that did
   not happen. Alternative rejected: 0.8.0, which the roadmap reserves
   for production information.

2. **The release note is a section of `releases/release-0.7.rst`, not a
   new page.** The 0.7 note is the one-page story of the 0.7 line, and
   the changelog's toctree lists it; a second page for a patch would
   split one story and add a toctree entry the structure test would then
   have to know. The section is dated and states what 0.7.1 adds.

3. **Release facts come from `pyproject.toml` in the new test.** The
   0.7.0 tests pinned the literal `'0.7.0'` in five places, each of
   which this change must now edit. `tests/test_release_records.py`
   reads the version once from `pyproject.toml` and holds every other
   file to it, and holds the changelog's top entry and `HISTORY.rst`'s
   top entry to that version. The existing `test_machinome_identity`
   literal stays, since it is the 0.7 identity contract, and moves to
   0.7.1.

4. **`bumpversion` is not run.** Its `commit = True` and `tag = True`
   would commit and tag from inside the cycle. The four files it names
   are edited by hand to the same result, and `setup.cfg`'s
   `current_version` with them, so the next `bumpversion` starts from
   0.7.1.

5. **The changelog is rewritten, not appended.** Rule 10 of the manual
   skill: a release section is a story in families. The nine *Unreleased*
   bullets were written one per cycle and in landing order (the last
   cycle first); the 0.7.1 section orders them as a maker meets them:
   a frame, a mate, its freedom (own line, prismatic, per instance,
   none), what it may carry (bounds, constraints, controls; an existing
   joint), reading it back, precision; then `machinome vet`; then the
   corrections. ADR numbers are kept in the bullets as the 0.7.0 section
   keeps them.

6. **The `user-documentation` requirement on profile contact is
   corrected in passing.** It still says profile contact is
   current-source and unreleased; 0.7.0 shipped it. Leaving a false
   requirement beside a new one about release records would make the
   spec contradict itself.

## Risks / Trade-offs

- [The upload slips past 27 September] → the date lives in `docs/conf.py`
  (`release_date`), the changelog head, `HISTORY.rst`, the release note
  section and `context7.json`; the workspace checklist names them.
- [A test elsewhere splits the changelog at `Machinome 0.7.0` and reads
  what is above it as unreleased] → `test_profile_documentation`,
  `test_mates` and `test_frame_precision_docs` are the three; each is
  repointed or already tolerant, and the full suite runs before commit 2.
- [The three unlisted cycles are misdescribed from their proposals] →
  each bullet is checked against the archived change's `tasks.md` and
  the code it names before it is written.
