# ADR-198: A Model's App Is Declared on Its Root and Bundled by the Viewer Beside Every Document

**Status:** Accepted
**Date:** 2026-11-22
**Change:** [`declare-a-models-app`](../../../openspec/changes/archive/2026-11-22-declare-a-models-app/)
**Amends:**
- [ADR-194: Viewers are providers behind one seam, chosen by name](ADR-194-viewers-are-providers-behind-one-seam-chosen-by-name.md): the seam gains the operation `bundle`, a Protocol `Bundler` and its default viewer `web`; the contract version stays 1
**Related to:**
- [ADR-199: An app that cannot be bundled is a recorded refusal, and an export refuses it](ADR-199-an-app-that-cannot-be-bundled-is-a-recorded-refusal-and-an-export-refuses-it.md): what is published when the bundle fails
- [ADR-200: A watching builder republishes an edited app in place, and develop tells open pages when the document is published](ADR-200-a-watching-builder-republishes-an-edited-app-in-place-and-develop-tells-open-pages-when-the-document-is-published.md): how `develop` follows the app
- [ADR-197: A state color is presentation on the existing body](../EXPORT/ADR-197-a-state-color-is-presentation-on-the-existing-body.md): an earlier additive document key that moves no version, as `app` does not
- The viewer's own decision log, `packages/machinome-viewer/workflow/adrs/`, which records how the viewer bundles an app and shows it in place of its panel (OpenSpec change `show-a-models-own-app`)

## Context and Problem Statement

The Enigma I reconstruction (`projects/enigma-i`, root class
`simulation/machine.py:Enigma`, a clocked machine) is operated in the browser
through the panel the viewer builds from its declarations, and a reader
cannot type on it. The pilot asked for the model to carry its own app, a
React application kept beside the model in the project's source, which the
viewer shows in place of that panel: an on-screen keyboard, case and rotor
controls, the picture filling the rest. The direction was ratified with
"yes, go on": declared on the root class beside the drivers and
instructions, a path relative to the declaring file, the source beside the
model, the build bundling it, the tool owning the toolchain and the project
carrying only its `.tsx` and `.css`.

Before this record nothing in the declarations, the build
(`core/builder.py` `_write_viewer_snapshot`) or the export
(`core/export.py` `export_node`) knew of an app, the core reached a viewer
only through the seam's four operations (ADR-194), and the build's sweep
removed every file of the build directory the document did not name.

## Considered Options

1. **A reserved class-body name `app = '<path>'`, relative to the declaring
   file, bundled by the viewer through a new seam operation into the
   directory each document is published in, and named by a top-level `app`
   record** (chosen)
2. A value object, `app = App('app/index.tsx')`: refused, a class for one
   string with no second field the Enigma needs
3. A `[tool.machinome]` key: refused, the pilot placed the app beside the
   drivers and instructions it operates, on the class
4. A JavaScript toolchain in the framework: refused, the viewer owns its
   widget's build tool and React, and the framework imports none
5. A new contract version for the operation: refused, the operation is
   additive, and a viewer that does not declare it is already refused by
   name

## Decision Outcome

**The declaration.** `app` is a reserved class-body name on a node class.
Where a class body assigns it, `NodeMeta` checks its form beside `controls`
(`node/declarative.py` `_validate_app`): a non-empty string, a relative
POSIX path (no leading `/`, no drive, no `\`), ending in `.tsx`, `.ts`,
`.jsx` or `.js`; any other value raises `TypeError` naming the class, the
attribute and the form. Existence and containment are not judged there. At
publication `machinome/core/app.py` `declared_app(root)` finds the class of
the root's method resolution order whose own body assigned `app`, and joins
the value to the real directory of that class's module file, so an
inherited app stays relative to the file that declared it. Only the
published root is read; a child's declaration contributes nothing.

**The seam.** `machinome.viewer.OPERATIONS` gains `bundle`,
`DEFAULTS['bundle'] = 'web'`, and the Protocol `Bundler` states
`bundle_app(entry, root, output_dir)`: bundle the app whose entry is `entry`,
every file it reads inside the project's `root`, into `output_dir`, answering
`{'script', 'stylesheet' or None, 'inputs': [paths]}` or raising
`ViewerError` with the sentence and writing nothing. `CONTRACT` stays 1. The
viewer that bundles is chosen as every operation's viewer is: the command's
`--viewer` (`develop`'s, handed to the builder as `Builder.viewer`;
`export`'s), else the project's `[tool.machinome] viewer`, else the default.
The web viewer offers the operation; the OpenSCAD viewer does not, and is
refused by `ViewerLacks`. What needs the bundle is named in that refusal as
`the build` for a build and `machinome export` for an export (departure 3 of
the change's evidence).

**A build.** `Builder._write_viewer_snapshot`, before its retry loop, calls
`publish_app(root, build_dir, 'the build', viewer, origin)` once when the
root declares an app; the record is passed to `document_body(..., app=)`,
which writes it as the body's last key, before the producer's `root` and
`pieces`. The record is `{'script': 'app-<h>.js', 'stylesheet':
'app-<h>.css'}`, the stylesheet key absent when the app imports none, the
files written by the viewer at the build directory's top level beside
`viewer.json` and named by their content. The sweep spares the files the
record names and removes an earlier app's, by the rule that removes a
renamed part's mesh. An unchanged app gives a byte-identical document, which
is not republished. A root with no app resolves no viewer and writes no
`app` key, so its document is byte-identical to the one published before
this record (pinned by the change's test P4). The capture staging passes no
record. The document's version does not move.

**An export.** When the root declares an app and the widget is exported,
`export_node` checks the entry's existence and containment and resolves the
bundling viewer at its top, beside the embedding viewer and before
`clear_keyframe` and the build; after `build_stls` it bundles into a fresh
temporary directory, then, after the output directory exists, copies the
files beside `manifest.json` with `_copy_artifact` and writes the record as
the manifest's `app` (departure 6 of the change's evidence: the design
resolved the bundling viewer with the embedding one and bundled after the
build; the checks moved to the top as well). Refusals: ADR-199.

**The refusal sentences** of the seam and the viewer are carried after
`<Class>.app = '<path>' cannot be bundled: ` (departure 2 of the change's
evidence; the design gave only the tail).

**The limit.** In this release an app is bundled only where the viewer's
JavaScript dependencies are installed, a source checkout; elsewhere the
viewer's refusal is the app's recorded refusal (ADR-199).

### Consequences

- Good: one line on the root class gives a model its app in every document
  the framework publishes for the browser, `machinome build`'s, so
  `develop`'s and the Studio's, and the export's.
- Good: a model without an app is unchanged in every byte and asks no viewer.
- Good: the core still names no viewer's technology; the toolchain is the
  viewer's.
- Bad: every publication of a model with an app runs Node: measured at about
  0.17-0.19 s on the change's fixture (`machinome build` median 1.20 s
  without the app, 1.39 s with it).
- Neutral: `app` is now a reserved name on a node class; no project used it.

## References

- OpenSpec change `declare-a-models-app`: proposal, design (Decisions 1-4, 7,
  8 and 11), the capability `model-app` and the modified capabilities
  `viewer-seam`, `export` and `user-documentation`; its `evidence.md`
  (departures 2, 3 and 6, the timings of task 4.4)
- `machinome/node/declarative.py` (`_validate_app`, `APP_SUFFIXES`),
  `machinome/core/app.py`, `machinome/viewer/__init__.py` (`OPERATIONS`,
  `DEFAULTS`, `Bundler`), `machinome/core/serializer.py` (`document_body`),
  `machinome/core/builder.py`, `machinome/core/export.py`
- `tests/test_model_app.py` (D1-D2, P1-P4, E1, X1), `tests/test_viewer_seam.py`
  (S1), the fixture `tests/app_project/`
