# Machinome 0.9.0: the release day

Status: working record, written 13 October 2026 by the OpenSpec change
`release-0-9-0` (bench `v0.9-release`). Not ratified; the change's archive
is the authority for what was released. Every step under "The pilot's
steps" is the pilot's: no agent tags, pushes or uploads.

## Where the release stands

The bench `v0.9-release` holds the set at 0.8.1, with the mechanics helpers
numbered with it, the release's tests and the upgrading page's 0.9 part, in
the commit "Prepare 0.9.0: the mechanics helpers numbered with the set",
which reaches `main` with the release. When the pilot names
the day, the orchestrator briefs a fresh agent with the date; it bumps the
set with `make bump VERSION=0.9.0`, dates the records, runs the tests,
`make docs` and `make check`, and leaves one commit, "Release 0.9.0". The
orchestrator reviews it, fast-forwards `main` to it and runs `make dist` in
the primary checkout, which keeps the archives in `dist/v0.9.0` beside the
earlier releases' folders; then it archives the change and records the
progress. Nothing is tagged, pushed or uploaded by then.

## The pilot's steps

1. **Read the folder.** `ls dist/v0.9.0` in the primary checkout: 36
   archives, the sdist and the wheel of each of the eighteen packages at
   0.9.0, each checked with `twine check --strict` by `make dist`.
2. **Tag the release commit**, the commit "Release 0.9.0" the archives were
   built from: `git tag -a v0.9.0 <commit> -m "Machinome 0.9.0"`.
3. **Push `main` and the tag**: `git push origin main v0.9.0`. GitHub
   Actions runs the tests on the tag, checks that the tag names the set's
   version, builds the archives again with `make dist` and creates the
   GitHub release `0.9.0` with them attached. The other local tags
   (`v0.8.1`, `viewer-v0.7.0` to `viewer-v0.8.1`, `mechanics-v0.1.0`) are a
   separate choice.
4. **Upload**: `make upload` in the primary checkout uploads
   `dist/v0.9.0/*` with twine, in one go. Fifteen of the eighteen projects
   are new on PyPI (`machinome-movie`, `machinome-skills`,
   `machinome-studio`, `machinome-engine-brep`, `machinome-engine-mesh`,
   the nine `machinome-node-*` and `machinome-viewer-openscad`), so the
   token must be one that may create projects, not one scoped to
   `machinome`. The packages pin each other `~=0.9.0` both ways, so no
   order helps: `machinome[viewer]` and every other extra resolves once all
   are up. If the upload stops part way, `twine upload --skip-existing
   dist/v0.9.0/*` completes it.
5. **Read the Docs.** The project `machinome` reads its configuration at
   `packages/machinome/.readthedocs.yaml` (Admin, Settings, the path of the
   configuration file); build `latest` and activate `v0.9.0`. The build
   installs `docs/requirements.txt` and builds the viewer's bundle with Node
   22, as the file says. The projects `machinome-mechanics` and
   `machinome-viewer` there: retire, or point at the manual's sections.
6. **Context7**: refresh from `context7.json`.
7. **The original repositories on GitHub** (the mechanics helpers', the
   viewer's, the videomaker's, the skills', the studio's and the FreeCAD
   adapter's): a note pointing to `machinome/machinome`, archive, or leave.
8. **0.8.1**, if wanted: its archives are in `dist/0.8.1-2026-10-10/`,
   never uploaded. Uploading them is independent of 0.9.0; PyPI shows the
   highest version as the latest whatever the order.
