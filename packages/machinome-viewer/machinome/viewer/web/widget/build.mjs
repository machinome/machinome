/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import { build } from 'esbuild';
import { readFile } from 'node:fs/promises';

const pkg = JSON.parse(await readFile('package.json', 'utf8'));

// The banner is the notice every downstream copy of the bundle carries --
// in git, on PyPI, and in each `solid export` directory a maker publishes.
// It names this bundle's own licence and points at its source, which is
// what the AGPL asks of conveyed object code, and it retains the notices of
// the bundled dependencies: MIT's for three.js and jokenizer, Apache-2.0's
// attribution notice for molejo.
const banner = `/*!
 * solid-widget.js - the browser viewer for solid-node models
 * solid-node-viewer ${pkg.version} - viewer API ${pkg.solidNodeViewerApi}
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 * Source: https://github.com/LibreSolid/solid-node-viewer
 *
 * Bundles three.js - Copyright 2010-2023 three.js authors
 *   MIT License - https://github.com/mrdoob/three.js/blob/dev/LICENSE
 * Bundles jokenizer - Copyright (c) 2018 Umut Özel
 *   MIT License - https://github.com/umutozel/jokenizer/blob/master/LICENSE
 * Bundles molejo - Copyright (C) 2026 Luis Henrique Cassis Fagundes
 *   Apache License 2.0 - https://github.com/LibreSolid/molejo/blob/main/LICENSE
 */`;

await build({
  entryPoints: ['src/widget.ts'],
  bundle: true,
  minify: true,
  format: 'iife',
  globalName: 'SolidNodeWidget',
  outfile: 'dist/solid-widget.js',
  define: {
    __VIEWER_API_VERSION__: JSON.stringify(pkg.solidNodeViewerApi),
  },
  banner: { js: banner },
  logLevel: 'info',
});
