# Studio warts

Open findings only, grouped by the project or change that produced them,
in the shape of the framework's `packages/machinome/workflow/warts.md`.
Nothing here is ratified.

# enigma-i, through the framework change `declare-a-models-app` (22 November 2026)

- **The Studio does not rebuild on an edit to a model's app.** A model's
  root may declare its own app (`app = 'app/index.tsx'`), a React
  application in the project's source that the viewer shows in place of its
  panel; `machinome build` bundles it beside `viewer.json`, so the Studio's
  page shows it with no Studio change. But `ModelWatcher.on_any_event`
  (`machinome/studio/watcher.py` 205) skips every path whose suffix is not
  `.py`, so an edit to `app/index.tsx`, a component or its stylesheet
  starts no build, and the Studio's page shows the edited app only at the
  next Python edit. `machinome develop` follows those files itself (the
  framework's design Decision 5a); the Studio would need its watcher to
  admit the app's files, for instance the `inputs` the build's bundle read,
  or the `.tsx`, `.ts`, `.jsx`, `.js` and `.css` files under the declared
  file's directory. Found while designing the framework's OpenSpec change
  `declare-a-models-app` (its design, Decision 9); the watcher is
  unchanged. Untriaged.
