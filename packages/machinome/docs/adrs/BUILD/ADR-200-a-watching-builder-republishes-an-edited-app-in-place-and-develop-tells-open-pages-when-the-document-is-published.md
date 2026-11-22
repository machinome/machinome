# ADR-200: A Watching Builder Republishes an Edited App in Place, and `develop` Tells Open Pages When the Document Is Published

**Status:** Accepted
**Date:** 2026-11-22
**Change:** [`declare-a-models-app`](../../../openspec/changes/archive/2026-11-22-declare-a-models-app/)
**Related to:**
- [ADR-198: A model's app is declared on its root and bundled by the viewer beside every document](ADR-198-a-model-s-app-is-declared-on-its-root-and-bundled-by-the-viewer-beside-every-document.md): the publication this record repeats in place
- [ADR-199: An app that cannot be bundled is a recorded refusal, and an export refuses it](ADR-199-an-app-that-cannot-be-bundled-is-a-recorded-refusal-and-an-export-refuses-it.md): the directory watched after a refusal
- [ADR-194: Viewers are providers behind one seam, chosen by name](ADR-194-viewers-are-providers-behind-one-seam-chosen-by-name.md): the web viewer serves in the develop process, in a session whose `reload()` tells every open page that a build was published

## Context and Problem Statement

`machinome develop` runs each build in a fresh builder process that watches
the loaded model's source files and exits on a change; the loop then calls
the session's `reload()` and starts the next builder. Restarting the builder
for an app edit would make the next one load the whole model and compile its
document again before it could bundle (for the Enigma, 3,347 parts), although
an app edit changes no Python and no part.

It was also observed on the bench (the change's
`evidence/develop-reload-observation.md`) that an open page learns of a build
only through `reload` on its socket, which it received about 0.1 s after an
edit, when the builder respawned, and before the next builder published:
the page read the document still on disk and showed every edit one edit
late. An app edit riding that path would too. The reviewer's blocking
finding asked that the open page be shown to display the edited app with the
picture standing.

## Considered Options

1. **The watching builder republishes an app edit in place, and `develop`
   watches the build directory and calls `reload()` each time `viewer.json`
   is replaced** (chosen)
2. An app edit exiting the builder with `SOURCE_CHANGED`: refused, the next
   builder loads the model and renders nothing new for minutes on a large
   model; the loaded root, the snapshot and the build lock are already in
   the watching builder
3. A reload sent by the builder process: refused, it has no session
4. The page polling the document: refused, a second channel beside the
   socket every page already keeps open

## Decision Outcome

**The app's sources.** After `publish_app` the builder schedules the
returned `inputs` (the project files the bundle read, as real paths) on its
observer as files, and keeps them as app sources apart from the model's
`_watched_sources`; where the app was refused before its inputs were known
it watches the directory ADR-199 names recursively, admitting `.tsx`, `.ts`,
`.jsx`, `.js` and `.css` events only, and ignoring other files there. Each
publication unschedules the previous app watches and schedules the new ones.
`on_modified` resolves `file_changed` for a model source, as before, and a
second future, `app_changed`, for an app source.

**What was published.** The builder keeps the snapshot dictionary and the
bytes it last published, both when it writes `viewer.json` and when it finds
the document already equal.

**The republish.** `wait_for_change` waits for either future. After an app
event it waits 0.1 s (`APP_SETTLE`), so one save writing several files is
one republication and a model source saved in the same burst makes it a
model change, which returns `SOURCE_CHANGED` as before (departure 5 of the
change's evidence; the design asked for the burst rule and left the means
open). Otherwise, under the project build lock, it reads `viewer.json`: if
the bytes are not the ones it last published (another producer published
since) it logs `the published document changed since this builder published
it; reloading the model to publish the app` and returns `SOURCE_CHANGED`;
where it has published nothing it logs that and does the same. Otherwise it
bundles again with the loaded root, replaces the held snapshot's `app`
record (keeping the key's place), encodes it, writes `viewer.json`
atomically and sweeps when the bytes differ, re-schedules the new inputs,
issues the build-ready callback when the publication changed, logs `The app
was republished`, and waits again. Nothing is loaded and no part is
rendered.

**The page is told.** When it serves through a session, `develop` starts
`watch_publication(build_dir, session)` before the first builder: a
`watchdog` observer on the build directory, created if absent, not
recursive, calling `session.reload()` once for each rename onto
`viewer.json` there. `atomic_write` replaces the document that way, after
the files it names are in place, so the page that is told reads the
document it is told of. The observer is stopped with the session. The
respawn `reload` is kept. The same notification makes a Python edit's
publication reach the page when it is published rather than at the next
edit; that is a consequence of the one mechanism.

**Known limits, not covered by this record:**

- An app file is watched by its own path. An editor that saves by writing a
  new file and renaming it over the old one may leave that watch on the
  replaced file, so later edits of it may stop being followed until the
  model is rebuilt. Not verified; the model's own sources are watched the
  same way.
- The publication watch sees only the rename `atomic_write` makes onto
  `viewer.json`. A document written in place by another writer is not
  announced (departure 14 of the change's evidence), and neither is
  `errors.json`, so a build error is still announced before it is written
  (`workflow/warts.md`).

### Consequences

- Good: an app edit reaches the open page in place, the picture standing, no
  builder started and no mesh fetched again (the change's X2: 0.39-0.49 s on
  the bench, from the edit to the page showing it).
- Good: a Python edit reaches the open page when it is published (X2:
  1.12-1.17 s), where it came one edit late before.
- Good: a document another producer published is never overwritten by an
  app republish; the rebuild that follows is said, not silent.
- Bad: the watching builder holds the published snapshot in memory; for the
  Enigma's document about 24.6 MB of JSON as a dictionary.
- Neutral: the Studio rebuilds only on Python events, so an app edit reaches
  its page at its next build; recorded in the Studio's `workflow/warts.md`,
  not changed here.

## References

- OpenSpec change `declare-a-models-app`: design Decision 5 (5a and 5b) and
  the review recorded in its proposal; the capabilities `model-app` and
  `cli` ("Develop command"); `evidence/develop-reload-observation.md` and its
  probe; its `evidence.md` (departures 5 and 14, X2's times)
- `machinome/core/builder.py` (`wait_for_change`, `_republish_app`,
  `_follow_app`, `on_modified`, `APP_SETTLE`, `REPLACED_SINCE_PUBLISHED`),
  `machinome/manager/develop.py` (`watch_publication`)
- `tests/test_model_app.py` (W1-W5, W1 through a symbolically linked project,
  X2), `tests/test_manager_develop.py`
