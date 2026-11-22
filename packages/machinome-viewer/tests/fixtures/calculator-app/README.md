<!--
  machinome-viewer - the browser viewer for machinome models
  Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
  SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
-->

# The calculator's app, as a fixture

The sources of a model's own app (OpenSpec `show-a-models-own-app`), and
nothing else. The model is `tests/fixtures/calculator/`, the framework's
clocked `Calculator` published as a version 8 build, reused verbatim: a
test copies that build to a temporary directory, bundles `app/index.tsx`
into the copy with the web viewer's `bundle_app`, and writes the record it
returns into the copy's `viewer.json` as `app`.

- `app/index.tsx`: the app. A default-exported component placing the
  picture with `<Viewport/>` above a bar holding two buttons, which play
  the declared instructions `Set four` and `Stroke` through `usePlay` and
  are both disabled while `useMachine().drawing` is true, and the four
  window digits `w3.digit` to `w0.digit` from `useMachine().bank`.
- `app/Readout.tsx`: one window, its label (`Window`) and its digit; the
  development page's test edits the label.
- `app/app.css`: the app's stylesheet, every selector under
  `.calculator-app`.
- `app/broken.tsx`: an app that does not build (an element never closed).
- `app/imports-three.tsx`: an app importing `three`, which an app may not.

The project carries no `package.json`: the viewer bundles an app with its
own toolchain and its own React.
