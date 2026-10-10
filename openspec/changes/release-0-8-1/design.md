## Context

0.8.0 was released through the change `release-0-8-0` (archived
`2026-10-05-release-0-8-0`), which made `tests/test_release_records.py`
derive the release note's page and section from `pyproject.toml`'s
version, and since `viewer-extra-floors-at-the-matching-viewer` the same
test holds the `viewer` and `web-snapshot` extras' floor to
`docs/conf.py`'s `viewer_version`. `skills/write-the-manual/SKILL.md`
("Work after a release", "A release pass") is the procedure: the
`Unreleased` section, written one bullet per cycle, becomes the version
section.

## Goals / Non-Goals

**Goals:**
- Every reader-facing record states 0.8.1, released 10 October 2026,
  with the matching viewer 0.8.1, API 29, document versions 1 to 13.
- A 0.8.0 project learns, on the upgrading page, the few changes it may
  have to follow.
- The distributions built from the tagged commit are the ones the pilot
  uploads.

**Non-Goals:**
- No source change, no document version, no viewer API move.
- No rewrite of the changelog bullets: each was written and checked by
  the cycle that landed it.
- The push, the upload, Read the Docs and Context7.

## Decisions

1. **A patch number, 0.8.1.** Every change since 0.8.0 is a correction, a
   speed-up or a sharper refusal; nothing is added to the public
   vocabulary, no document version and no viewer API moves. The few
   behaviour changes a project may meet (a refused early read of
   `children`, a renamed one-member production binding, a third
   `ClockedSnapshot` argument, a `ValueError` for an undeclared leaf
   source) correct what was wrong or silent; the upgrading page states
   each. Alternative rejected: 0.9.0, which the roadmap reserves for
   dynamics.

2. **The viewer is numbered with the framework, 0.8.1.** The extras'
   floor equals `viewer_version`, held by a test, and the two packages are
   numbered together since 0.7. The viewer has no shipped change since
   0.8.0, so its 0.8.1 is 0.8.0 renumbered, as viewer 0.7.1 was 0.7.0
   renumbered. Alternative rejected: keeping the floor at 0.8.0, which
   would break the numbering rule and the test that holds it.

3. **The release note gains a section, not a page,** as 0.7.1 did: the
   test reads a patch's note as the last section of its line's page.

4. **The bullets stay; an opening and an order are added.** The
   twenty-two bullets were written as each cycle landed. The section gains
   the opening every release section has and groups the bullets as a
   maker meets them: speed of the exact checks, builds and caching,
   refusals and test reports, corrections, installation.

## Risks / Trade-offs

- [The floor requires viewer 0.8.1 on PyPI] → `pip install
  "machinome[viewer]==0.8.1"` fails until the viewer is uploaded, and so
  does the documentation CI job that installs from PyPI. The handoff says
  to upload the viewer first.
- [A fresh checkout's suite] → CI runs on a clean clone, where a local
  green has masked failures before; the evidence records a run on a
  fresh clone with a fresh environment.
