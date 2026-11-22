## Context

Three producers serialize a document for the browser through one function, `document_body` (`core/serializer.py` 883-940): the build's `viewer.json` (`core/builder.py` `_write_viewer_snapshot_with_inventory` 662-725), the export's `manifest.json` (`core/export.py` 206-210), and the web viewer's capture staging (`packages/machinome-viewer/machinome/viewer/web/stage.py` 96), which passes no instructions and bakes one instant. The build publishes into the build directory and then sweeps every file the published tree does not name, collecting only the tree's `model` and `markings` references (`builder.py` 772-860, `collect` 782-794). The export resolves the viewer that embeds before anything is written (`export.py` 155, `manager/export.py` 61-75), writes the models after `os.makedirs` (221) and copies the viewer's two files last (242, 303-307); `--no-widget` resolves no viewer (`cli` spec, "Export command").

The core reaches a viewer only through its seam (`machinome/viewer/__init__.py`, ADR-194): `CONTRACT = 1`, `OPERATIONS = ('present', 'capture', 'serve', 'embed')` (51), `DEFAULTS` (55), Protocols, `resolve(operation, needed_by, explicit, origin)` choosing by the flag, the project's `[tool.machinome] viewer`, else the operation's default, and refusing an absent viewer by its extra, an operation a viewer lacks by name, and never substituting.

`machinome develop` runs each build in a fresh builder process (`manager/develop.py` 154-188) that watches the loaded model's source files (`builder.py` 423-429, `on_modified` 889-913) and exits on a change; the loop then tells the open pages to reload and starts the next builder. The Studio runs `machinome build` (`packages/machinome-studio/machinome/studio/preparation.py` 300) into the build directory it serves whole (`app.py` 859-867).

A declaration with a path relative to its declaring file has a precedent in the movie package: `module_path` checks the form, `declaring_class` finds the class whose body wrote the attribute, `module_directory` is that class's file's directory (`machinome-movie/machinome/movie/names.py` 82-89, 151-167). A reserved, form-checked class-body name has one in the core: `controls` (`node/declarative.py` 1078-1079, 1105-1144).

The Enigma declares `viewer = "web"` under `[tool.machinome]` (`projects/enigma-i/pyproject.toml` 8-10), exports with the widget, and its public page copies every file of the export and mounts the inspector over `model/manifest.json` (`tools/machine/build_page.py` 49-54, `tools/machine/page/index.html` 389).

## Goals / Non-Goals

**Goals:**

- One line on the root class says the model has an app; the path means the same thing wherever the project lies.
- Every document a maker or a reader opens in a browser — the build's, so `develop`'s and the Studio's, and the export's — carries the bundled app, and every failure to bundle it is named where the model is shown.
- `develop` follows an edit to the app without re-rendering parts.
- No document of a model without an app changes in any byte, and no viewer is asked for it.

**Non-Goals:**

- Apps per sub-assembly, types generated from the model, any JavaScript toolchain in the framework, a toolchain in an installed viewer, an app in a widget-less export, a type check of an app.

## Decisions

### 1. The declaration

`app` is a reserved class-body name on a node class. Where a class body assigns it, `NodeMeta` checks its form as it checks `controls` (beside `declarative.py` 1078-1079): a non-empty string, a relative POSIX path (no leading `/`, no drive, no `\`), ending in `.tsx`, `.ts`, `.jsx` or `.js`; otherwise `TypeError` naming the class, the attribute and the form (`Enigma.app is 42. On a node class `app` names the model's app: a TypeScript or JavaScript file relative to this file, such as 'app/index.tsx'; the name is reserved`). Existence and containment are not checked here: a class is imported in places that publish nothing.

At publication, `machinome/core/app.py` `declared_app(root)` reads `type(root)`'s attribute; when present, `declaring_class(type(root), 'app')` (the class whose own body assigned it, so an inherited app is relative to its own file) and that class's module file give the entry's absolute path. Only the published root is read: a child whose class also declares an app contributes nothing, which the manual says. A class that is the root of one declared model and a child in another is therefore an app in the first and not in the second.

Alternatives rejected: a call such as `app = App('app/index.tsx')` (a value object for one string with no second field the Enigma needs); a `[tool.machinome]` key (the pilot placed it beside the drivers and instructions it operates, on the class).

### 2. The seam's operation `bundle`

`OPERATIONS` gains `'bundle'`; `DEFAULTS['bundle'] = 'web'`; a Protocol:

```python
class Bundler(Protocol):
    """`bundle`: a model's app, bundled beside its document."""

    def bundle_app(self, entry: str, root: str, output_dir: str) -> dict:
        """Bundle the app whose entry file is `entry`, every file it reads
        inside the project's `root`, into `output_dir`; return
        `{'script': name, 'stylesheet': name or None, 'inputs': [path, ...]}`,
        the names relative to `output_dir` and the inputs the project files
        read, or raise `ViewerError` with the sentence, writing nothing."""
```

`CONTRACT` stays 1: the operation is additive, an older web provider that does not declare it is refused by `require` with `ViewerLacks` ("the build needs a viewer that can bundle, and the web viewer cannot; the viewers that can: …"), and the two providers release together as one set. The OpenSCAD viewer does not offer it.

### 3. Which viewer bundles

The same rule as every operation (ADR-194): the command's `--viewer` (`develop`'s, passed to the builder as `Builder.viewer`; `export`'s), else the project's `[tool.machinome] viewer`, else `DEFAULTS['bundle']`. `machinome build` has no flag, so the project's or the default. A project declaring `viewer = "openscad"` with an app is therefore refused by name naming the key (`ViewerLacks(..., declared=True)`); such a project already cannot `develop` without `--viewer web`. No project has that combination today.

### 4. Publication in a build

`Builder._write_viewer_snapshot` (643-660), before its retry loop: when `declared_app(self.node)` is not None, `publish_app(node, self.build_dir, needed_by, self.viewer, origin)` returns the record:

- `{'script': 'app-<h>.js', 'stylesheet': 'app-<h>.css'}` (the stylesheet key absent when the app imports none), after the provider wrote those files into the build directory, or
- `{'refusal': '<sentence>'}`.

The record is passed to `document_body(..., app=record)`, which writes it as the body's last key. The build directory's files sit at its top level, beside `viewer.json`, not in a subdirectory, so no declared model's directory name (`_build/<model>/`) can collide with them. The sweep's `collect` adds the record's `script` and `stylesheet` to `referenced`, so a published app is kept and a previous one, no longer named, is removed with the same rule that removes a renamed part's mesh. Because the provider names files by their content (companion design Decision 11) and leaves a file that already holds the same bytes untouched, an unchanged app gives a byte-identical document, which `_write_viewer_snapshot_with_inventory`'s comparison (714) does not republish.

A root with no app: `publish_app` is not called, no viewer is resolved, `document_body` writes no `app` key, the document is byte-identical to today's. The capture staging calls `document_body` without `app` and publishes none (`stage.py` 96 is unchanged).

Bundling runs inside the project build lock, as every publication step does. Its cost (a Node start, esbuild, React) is paid per publication of a model that declares an app and is measured in tasks 4.4.

### 5. `develop` follows the app, and the open page shows it

**How an open page learns of a build today, read and observed** (`evidence/develop-reload-observation.md`, `machinome develop` on a scratch copy of `tests/flat_project/` on port 8028, the page driven in headless Chromium). The page learns of a build only through `reload` on its socket: `reloader.ts`'s `onmessage` calls `checkBuild`, which fetches `/_build_error` and, with no new error, calls the handle's `manifestChanged()` through `develop.ts`'s callback (109-113). The server sends `reload` when a socket opens and when the session's `reload()` is called; `develop.py` calls it at the top of its loop, after a builder process has exited and before the next starts (158-170), and a watching builder exits only when a source changes after it has published (`builder.py` 514-518, 636-641). Observed: after each Python edit the page received `reload` 0.1 s later and fetched the document still on disk; the new document was published 1 s after that, and nothing told the page; each edit appeared only at the next edit. The page does not watch the document itself. This stands in the way of point (f), so it is fixed here for the path the app needs (Decision 5b).

**5a. An app edit is republished by the builder that holds the model.** Restarting the builder for an app edit would make the next builder load the whole model and compile its document again before it can bundle; an app edit changes no Python and no part. So the watching builder rebundles in place:

- After `publish_app` it schedules the returned `inputs` on its observer and keeps them as **app sources**, apart from `_watched_sources` (the model's); where the app was refused before Node produced its inputs (a syntax error, a missing file), it watches the entry's directory recursively, admitting `.tsx`, `.ts`, `.jsx`, `.js` and `.css` events only. `on_modified` (889-913) tells the two kinds apart: a model source resolves `file_changed` as today; an app source resolves a second future, `app_changed`.
- The builder keeps what it last published: the snapshot dictionary and its bytes, set in `_write_viewer_snapshot_with_inventory` both when it writes and when it finds the document already equal (714-725).
- `wait_for_change` (636-641) waits for either future. On `file_changed` it returns `SOURCE_CHANGED` as today; a model source and an app source in one burst is a model change. On `app_changed`, under the project build lock, it reads `viewer.json`; if the bytes are not the ones it last published (another producer, such as a concurrent `machinome build`, published since) it logs `the published document changed since this builder published it; reloading the model to publish the app` and returns `SOURCE_CHANGED`, which is the existing full rebuild and is said, not silent. Otherwise it calls `publish_app` with the loaded root, replaces the snapshot's `app` record, encodes it, writes `viewer.json` atomically when the bytes differ, sweeps with the snapshot (so the previous app's files go), re-schedules the new inputs, issues the build-ready callback when the publication changed (`_notify_callback`, under `one-shot-build-and-notification`), and waits again. Where the builder has nothing published (its model failed), an app event is treated as a model change and returns `SOURCE_CHANGED`, logged.
- Its cost is one bundling and one encoding of the held document; no import, no assembly, no serialization walk, no part. Measured on the bench for the Enigma's published document (24,599,557 bytes): `json.loads` 0.29 s, `json.dumps` 0.24 s; the bundling is measured in tasks 4.4. No recorded figure for the Enigma's model load was found in `packages/machinome-viewer/workflow/evidence/enigma-*.md`; this design does not need one, since an app edit never pays it.

Alternative rejected: exiting with `SOURCE_CHANGED` for an app edit (the first version of this design). The code gives no reason to keep it: the loaded root, the snapshot and the build lock are all in the watching builder already.

**5b. The page is told when the document is published.** `develop.py`, when it serves through a session, watches the build directory (non-recursively, with the `watchdog` observer the builder already uses) and calls `session.reload()` once each time `viewer.json` is replaced there; `atomic_write` (214-226) replaces it by a rename inside that directory, after the files it names are in place, so the page that is told reads the document and finds its app. The `reload` sent when a builder is respawned is kept as it is. The page then does what it does on every `reload` (`/_build_error`, then `manifestChanged()`), and the viewer reconciles the app in place (companion design Decision 9): the root is unchanged, so no part's geometry is fetched again and the picture stands while the old app is replaced by the new one. The same notification serves a Python edit's publication, which the page then shows when it is published instead of at the next edit; that is a consequence of the one mechanism, not a separate change. A build error (`errors.json`) is not watched: an app's refusal is in the document, not there; the error path's own timing is left as the warts entry says.

Alternatives rejected: a reload sent by the builder process (it has no session; the develop process does); the page polling the document (a second channel beside the socket every page already keeps open).

### 6. Refusals: recorded in the document, not substituted

`publish_app` turns each of these into the record's `refusal`, a sentence naming the model's root class and the declared path, and logs it once at error level:

| Case | Sentence (after `<Class>.app = '<path>'`) |
| --- | --- |
| the entry does not exist | `names <absolute path>, which does not exist` |
| its real path is outside the project root (`project_root(node.src)`) | `names <absolute path>, which is outside the project at <root>; an app's files are the project's own` |
| the bundling viewer is not installed | the seam's `ExtraUnavailable` sentence (`… pip install "machinome[viewer]"`) |
| it is installed and does not bundle | the seam's `ViewerLacks` sentence |
| the viewer refuses to bundle | the viewer's `ViewerError` sentence (an unsupported import, a file outside the project, source that does not build, a viewer without its toolchain, missing JavaScript dependencies, no Node.js) |

The document is still published and the model stays visible on every page, which names the refusal over it (companion design Decision 8). `errors.json` is not written for an app's refusal: in `develop` the page shows a build error as a pane over the whole page (`packages/machinome-viewer/machinome/viewer/web/widget/src/develop.ts` 36-52), which would hide the model the refusal is about. `machinome build` exits 0, since its status "SHALL reflect whether the model built" (`one-shot-build-and-notification`) and the model did; the log line and the page say what did not. Whether a refused app should fail `machinome build` is listed under Open Questions.

Alternative rejected: failing the build. The develop page would cover the model; the Studio would keep the previous document and say "Model rebuild failed" about a model that built.

### 7. The files stay inside the project

The entry's real path must lie inside the project root; this is checked by the core before any viewer is asked (Decision 6), and the root is handed to the viewer, which refuses any file the bundle reads outside it (companion design Decision 11). The project root is the one `project_root(node.src)` finds, the same the export uses for its source record (`export.py` 157).

### 8. An export

`export_node` (114): when the root declares an app and `widget` is true, it resolves the bundling viewer with the embedding one (`resolve('bundle', 'machinome export', viewer, origin)`), and, after `build_stls` and before `os.makedirs(output_dir)` (221), bundles into a fresh temporary directory. A refusal raises `ExportAppRefused(sentence)`, which `manager/export.py` reports as `Error: <sentence>` and exit 1, with no output directory created or modified, as the existing refusals do. Otherwise the files are copied atomically beside `manifest.json` with the models (`_copy_artifact`, 91-112) and the record is the manifest's `app`. The export page and any page over the export (the Enigma's) load them through the base the models use.

With `--no-widget`, a root declaring an app is refused before anything is built: `machinome export --no-widget does not carry a model's app, and <Class> declares app = '<path>'; export it with its widget`. `--no-widget` still resolves no viewer. Carrying an app into a widget-less export for a host's own copy of the viewer has no project asking for it yet; it is listed under Open Questions.

The export refuses where the build records because an export is what a reader receives, and a reader who meets a refusal cannot fix it.

### 9. The Studio

Nothing in the Studio changes for an app to be shown there: it runs `machinome build`, which now bundles into the build directory, serves every file of that directory, and mounts the viewer with its panel presented. Two things are owed in its own package and are not made here: its `ModelWatcher` rebuilds only on `.py` events (`packages/machinome-studio/machinome/studio/watcher.py` 205), so an edit to an app's file reaches the Studio's page at the next Python edit; and its API shop skill must state the `app` declaration (tasks 6.3), as the public contract changed.

### 10. Tests, red first

The fixture `tests/app_project/` (inside the suite's project, `tests/pyproject.toml`): `calculator_app.py` declaring `class CalculatorApp(Calculator): app = 'app/index.tsx'` over the existing clocked `tests/clocked_project/calculator.py:Calculator`, and `app/index.tsx`, `app/Readout.tsx`, `app/app.css` (two buttons playing `Set four` and `Stroke`, disabled while a transition is drawn, the four window digits, a `<Viewport/>`); `outside.py` declaring `app = '../../outside-app.tsx'` with that file created by the test outside `tests/` in a temporary copy; `missing.py` naming a file that does not exist; `broken.py` naming `app/broken.tsx`. In `tests/test_model_app.py`:

- D1 a class body `app = 42`, `app = '/abs/x.tsx'`, `app = 'x.py'` each raise the form's `TypeError` naming the class (red: accepted today).
- D2 `declared_app` of `CalculatorApp` is `tests/app_project/app/index.tsx`; of a subclass in another file, the same path; of `Calculator`, None.
- P1 a build of `CalculatorApp` publishes `viewer.json` with `app.script` and `app.stylesheet` naming files beside it; P2 a second build does not republish (document bytes and the script's mtime unchanged); P3 an edit to `app/Readout.tsx` gives a new script name and the old file is swept; P4 a build of `Calculator` is byte-identical to the document published before this change (pinned bytes, as the bindings and markings requirements pin them) and asks no viewer (the seam's `resolve` patched to fail).
- R1-R4 `missing.py`, `outside.py`, the viewer patched absent (`ExtraUnavailable`), `broken.py`: each publishes the document with `app.refusal` carrying the table's sentence, logs one error, writes no `errors.json`, and `machinome build` exits 0.
- W1 a watching builder of `CalculatorApp`, after publishing, on an edit to `app/Readout.tsx`, republishes `viewer.json` naming a new script, sweeps the old one, does not return (it is still watching), and loads nothing (`load_node` patched to count: no call); an edit to an unrelated `.tsx` beside the project changes nothing; W2 after `broken.py`'s refusal, a repair of `app/broken.tsx` republishes with a script in place of the refusal, in the same builder; W3 when `viewer.json` was replaced by another writer after the builder published, an app edit returns `SOURCE_CHANGED` with the logged sentence; W4 an edit to the model's Python with the app still returns `SOURCE_CHANGED` as today; W5 `develop`'s publication watch calls a fake session's `reload()` once per replacement of `viewer.json` and not for any other file of the build directory.
- E1 `export_node` of `CalculatorApp` writes the script and stylesheet beside `manifest.json` and names them; E2 `broken.py`'s export raises `ExportAppRefused` and creates no output directory; E3 `machinome export --no-widget` of `CalculatorApp` exits 1 with the sentence and writes nothing; E4 `--no-widget` of `Calculator` is unchanged.
- S1 (in `tests/test_viewer_seam.py`) `OPERATIONS` holds `bundle`, `DEFAULTS['bundle']` is `web`, the web provider offers it and the OpenSCAD one does not, `require('openscad', 'bundle', …)` is refused naming `web`.
- X1, the end-to-end proof: export `CalculatorApp` with its widget into a temporary directory, serve it statically, open `index.html` in headless Chromium (launched with the arguments of `machinome.viewer.web.capture.Capture.launch`, `capture.py` 328-334), and check that the app's buttons are drawn and no clocked panel is, that clicking `Stroke` disables the buttons until the drawing lands and the digits then read the committed bank, and that the model's canvas has drawn pixels. Skips, saying why, without Chromium or without the viewer's JavaScript dependencies.
- X2, the open development page shows the edited app, the picture standing: run `machinome develop` on a temporary copy of the suite's project selecting `app_project.calculator_app:CalculatorApp`, on a port the test binds free (never 9010), open its page in headless Chromium, wait for the app, then edit the text `app/Readout.tsx` draws; check, within a bounded wait, that the page shows the new text without a page load (a marker set on `window` survives), that the canvas is the same element with drawn pixels, that no model file was requested again after the edit, and that the develop log shows one builder `START` before the edit and none after it. Then edit the model's Python once and check the page shows that edit when it is published, not at a following edit. Same skips as X1, and skips where OpenSCAD or CadQuery, whichever the fixture's parts need, is absent.

P1-P3, R1-R4, W1-W3, W5, E1-E3, S1, X1 and X2 are red on the base (nothing reads `app`, no publication is watched; X2's Python half is red on the base by the observation above); P4, W4 and E4 are green on the base and stay green.

### 11. The manual and the changelog

Under the workspace's `skills/write-the-manual/SKILL.md`: the new how-to `docs/howto/give-a-model-its-app.rst` (`.. needs:: viewer`), shared with the companion change (the declaration, the files beside the model, what `develop`, the export and the Studio do, the refusals and where they appear, the limit of this release; the companion writes the helper's part); `docs/reference/api.rst` (the reserved `app` declaration); `docs/reference/cli.rst` (`export --no-widget` and an app; `build` and an app's refusal); `docs/howto/share-an-export.rst` (an export carries its app's files); the index's toctree. The `HISTORY.rst` bullet under "Unreleased" is written in this cycle.

## Risks / Trade-offs

- [Every publication of a model with an app runs Node] → measured (tasks 4.4); the content name makes an unchanged app publish nothing new.
- [A refused app does not fail `machinome build`] → logged at error level and shown on every page; ruled by the reviewer (see "Rulings").
- [An in-place republish could overwrite a document another producer published since] → the builder compares the bytes on disk with its own under the build lock and falls back to the full rebuild, saying so (Decision 5a).
- [The publication watch also makes a Python edit's page current] → the one mechanism serves both; the respawn `reload` is kept, so nothing a page received before is withheld.
- [An app file outside the model's import closure is not part of the model's currency] → deliberate: an app's edit changes no part; it changes the document through the bundle's name.
- [The bundling viewer follows the project's `viewer` key] → consistent with every operation; the corner case (an OpenSCAD project with an app) is refused by name.

## Decision record

After the implementation confirms them, ADRs under `docs/adrs/BUILD/` (next free numbers after ADR-197): a model's app is declared on its root class and bundled by the viewer through the seam's `bundle` operation, beside every document the framework publishes for the browser (Decisions 1-5, 8); an app that cannot be bundled is a recorded refusal, not a build failure (Decision 6); a watching builder republishes an edited app in place, and `develop` tells the open pages when the document is published (Decision 5). ADR-194 gains a dated pointer naming the operation. None is written before the implementation.

## Rulings (reviewer, 22 November 2026, under the pilot's standing delegation)

- A refused app does not fail `machinome build`: it exits 0 (Decision 6). The export refuses it (Decision 8).
- A widget-less export of a model with an app is refused (Decision 8).
- The reserved class-body name is `app` (Decision 1).
- No type check of an app's sources in this change.

## Open Questions

- For the pilot: an app bundle combines the project's own code with the viewer's helper, which carries the set's grant, GPL-2.0-or-later OR CERN-OHL-S-2.0+ (companion design Decision 7). Should the helper carry a permissive grant instead? Kept as designed until the pilot answers; it does not block.

## Found while proposing, out of scope

- The development page is told of a build before the build publishes, so it shows each edit one edit late (observed, `evidence/develop-reload-observation.md`). Decision 5b fixes it for a published document, the app's path included; recorded in `workflow/warts.md` (tasks 6.4) with the observation and with what remains: a build error's `errors.json` is still announced before it is written.
