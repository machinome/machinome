/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import { build } from 'esbuild';
import { readFile } from 'node:fs/promises';

const pkg = JSON.parse(await readFile('package.json', 'utf8'));

// The banner is the notice every downstream copy of the bundle carries --
// in git, on PyPI, and in each `machinome export` directory a maker publishes.
// It names this bundle's own licence and points at its source, which is
// what the AGPL asks of conveyed object code, and it retains the notices of
// the bundled dependencies: MIT's for three.js and jokenizer, Apache-2.0's
// attribution notice for molejo.
const banner = `/*!
 * machinome-viewer.js - the browser viewer for machinome models
 * machinome-viewer ${pkg.version} - viewer API ${pkg.machinomeViewerApi}
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 * Source: https://github.com/machinome/machinome-viewer
 *
 * Bundles three.js - Copyright 2010-2023 three.js authors
 *   MIT License - https://github.com/mrdoob/three.js/blob/dev/LICENSE
 * Bundles jokenizer - Copyright (c) 2018 Umut Özel
 *   MIT License - https://github.com/umutozel/jokenizer/blob/master/LICENSE
 * Bundles molejo - Copyright (C) 2026 Luis Henrique Cassis Fagundes
 *   Apache License 2.0 - https://github.com/LibreSolid/molejo/blob/main/LICENSE
 */`;

// The worker is bundled FIRST, to a string, and injected into the main
// pass as `__WORKER_SOURCE__` (OpenSpec `run-in-the-worker`, design D3).
// `runtime.ts` makes the worker from a blob URL of that string, so there
// is still exactly ONE published artifact -- `dist/machinome-viewer.js`,
// whose name is a compatibility contract -- and `machinome export`, the
// development server's `/_viewer/bundle.js` and the capture page go on
// copying one file.
const worker = await build({
  entryPoints: ['src/run/worker.ts'],
  bundle: true,
  minify: true,
  format: 'iife',
  write: false,
  logLevel: 'info',
});

await build({
  entryPoints: ['src/widget.ts'],
  bundle: true,
  minify: true,
  format: 'iife',
  globalName: 'MachinomeViewer',
  outfile: 'dist/machinome-viewer.js',
  define: {
    __VIEWER_API_VERSION__: JSON.stringify(pkg.machinomeViewerApi),
    __DOCUMENT_VERSIONS__: JSON.stringify(pkg.machinomeDocumentVersions),
    __WORKER_SOURCE__: JSON.stringify(worker.outputFiles[0].text),
  },
  banner: { js: banner },
  logLevel: 'info',
});
