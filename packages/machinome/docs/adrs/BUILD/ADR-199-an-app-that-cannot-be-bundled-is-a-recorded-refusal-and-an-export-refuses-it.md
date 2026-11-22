# ADR-199: An App That Cannot Be Bundled Is a Recorded Refusal, and an Export Refuses It

**Status:** Accepted
**Date:** 2026-11-22
**Change:** [`declare-a-models-app`](../../../openspec/changes/archive/2026-11-22-declare-a-models-app/)
**Related to:**
- [ADR-198: A model's app is declared on its root and bundled by the viewer beside every document](ADR-198-a-model-s-app-is-declared-on-its-root-and-bundled-by-the-viewer-beside-every-document.md): the declaration and the bundle this record refuses
- [ADR-194: Viewers are providers behind one seam, chosen by name](ADR-194-viewers-are-providers-behind-one-seam-chosen-by-name.md): its refusals (an absent viewer by its extra, an operation a viewer lacks by name) are carried, never substituted
- The viewer's own decision log, `packages/machinome-viewer/workflow/adrs/`: the viewer shows a recorded refusal over the drawn model

## Context and Problem Statement

A declared app may fail to bundle: its file does not exist, its file lies
outside the project, the bundling viewer is not installed or does not bundle,
or the viewer refuses the app's sources (an unsupported import, a file read
outside the project, source that does not build, an installed viewer without
its toolchain, missing JavaScript dependencies, no Node.js).

`machinome build`'s requirement says its exit status reflects whether the
model built. In `develop` a build error is a pane over the whole page
(`widget/src/develop.ts`), which would hide the model the failure is about,
and the Studio keeps the previous document and says "Model rebuild failed"
about a model that did build. An export is what a reader receives, and a
reader who meets a refusal cannot fix it. The reviewer ruled on 22 November
2026, under the pilot's standing delegation: a refused app does not fail
`machinome build` (exit 0); the export refuses it; a widget-less export of a
model with an app is refused.

## Considered Options

1. **A build records the refusal in the document and publishes the model;
   an export refuses before writing anything** (chosen)
2. Failing the build: refused, the develop page would cover the model and
   the Studio would keep the previous document
3. Publishing the viewer's automatic panel in the app's place: refused, a
   substitution; the page names why the app is absent instead
4. A widget-less export carrying the bundled app for a host's own viewer:
   not taken, no project asks for it

## Decision Outcome

**A build.** `publish_app` turns each failure into the record
`{'refusal': '<sentence>'}`, logs the sentence once at error level
(`core.app`) and never raises; the document is published as for any model,
`errors.json` is not written, and `machinome build` exits 0 since the model
built. The sentences, each naming the root's class and the declared path:

- `<Class>.app = '<path>' names <absolute path>, which does not exist`
- `<Class>.app = '<path>' names <real path>, which is outside the project at
  <root>; an app's files are the project's own`: judged by the core, on real
  paths, against `project_root(node.src)`, before any viewer is asked; the
  root is also handed to the viewer, which refuses any file the bundle reads
  outside it
- `<Class>.app = '<path>' cannot be bundled: <sentence>` for the seam's
  `ExtraUnavailable` and `ViewerLacks`, the viewer's `ViewerError`, and,
  beyond the design's table, a `ProjectManifestError` met while resolving
  the bundling viewer from a malformed `[tool.machinome] viewer` (departure
  7 of the change's evidence)

A later build that bundles names the script in place of the refusal; the
record and the sentence follow the files, as any other document key does.

**Which refusal watches a directory.** Where the app was refused before the
bundle's inputs were known, `publish_app` also answers the directory to
watch for its repair (ADR-200): the nearest existing directory of the
declared file, for a missing file or a viewer's refusal of the sources; none
for a file outside the project or an absent or incapable viewer, which no
edit of the app's own files repairs (departure 4 of the change's evidence;
the design named "a syntax error, a missing file").

**An export.** A refusal raises `ExportAppRefused(sentence)` before the
output directory is created or modified: the entry and containment checks
and the bundling viewer at the top of `export_node`, the bundling itself into
a temporary directory after the build. `machinome export` reports it as
`Error: <sentence>` and exits 1, as the existing refusals do.

**A widget-less export.** `machinome export --no-widget` of a root declaring
an app is refused before anything is built, by the command after the node
loads and by `export_node` before `clear_keyframe`: `machinome export
--no-widget does not carry a model's app, and <Class> declares app =
'<path>'; export it with its widget`. `--no-widget` still resolves no viewer.

### Consequences

- Good: every page shows the model and names why its app is absent; the
  develop page is not covered and the Studio publishes the build.
- Good: a reader never receives an export whose app is missing.
- Bad: a refused app does not fail `machinome build`; it is seen only in the
  log and on the page.
- Neutral: the same failure is a recorded refusal in a build and an error in
  an export, by design.

## References

- OpenSpec change `declare-a-models-app`: design Decisions 6-8 and its
  "Rulings"; the capabilities `model-app` and `export`; its `evidence.md`
  (departures 4 and 7)
- `machinome/core/app.py` (`checked_entry`, `bundler`, `bundle`,
  `publish_app`, `widgetless_refusal`), `machinome/core/export.py`
  (`ExportAppRefused`), `machinome/manager/export.py`
- `tests/test_model_app.py` (R1-R4, E2, E3, E4)
