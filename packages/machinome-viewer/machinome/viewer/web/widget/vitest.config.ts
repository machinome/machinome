/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The viewer's API version is declared once, in package.json, and
// injected at build time by build.mjs. The suite must be given the same
// value from the same place, so a test can never agree with a bundle
// that was built from a different number.

import { readFileSync } from 'node:fs';
import { defineConfig } from 'vitest/config';

const pkg = JSON.parse(
  readFileSync(new URL('./package.json', import.meta.url), 'utf8'),
);

export default defineConfig({
  define: {
    __VIEWER_API_VERSION__: JSON.stringify(pkg.machinomeViewerApi ?? null),
    __DOCUMENT_VERSIONS__: JSON.stringify(
      pkg.machinomeDocumentVersions ?? null),
    // The suite never builds a worker: `runtime.ts` falls back in-thread
    // when there is no source to make one from, which is the same path a
    // page with a restrictive policy takes.
    __WORKER_SOURCE__: JSON.stringify(''),
  },
});
