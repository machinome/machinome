/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// A host that ships against a different viewer needs to say so in a
// sentence rather than render an empty pane, which only works while
// there is exactly one place the number is written. package.json is that
// place, because the next cycle reads it from Python without building or
// running the bundle.

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { API_VERSION } from './version';

const pkg = JSON.parse(
  readFileSync(new URL('../package.json', import.meta.url), 'utf8'),
);

describe('API_VERSION', () => {
  it('is declared in package.json, where a Python caller can read it', () => {
    expect(typeof pkg.solidNodeViewerApi).toBe('number');
    expect(Number.isInteger(pkg.solidNodeViewerApi)).toBe(true);
    expect(pkg.solidNodeViewerApi).toBeGreaterThan(0);
  });

  it('is the number the package declares, not a second copy', () => {
    expect(API_VERSION).toBe(pkg.solidNodeViewerApi);
  });

  // Raised whenever the mount interface or the handle changes
  // incompatibly, AND whenever a capability a host may require is added
  // to it. Rendering `version: 3` documents -- parts whose geometry
  // follows the machine -- was such a capability (5); playing a declared
  // loop at a chosen speed -- `speed` on the options and the handle --
  // was the next (6). Reading a `version: 4` document's `bindings` table
  // (OpenSpec `read-expression-bindings`, design D9) is the one after
  // that (7): a host that mounts a document the framework now publishes
  // at version 4 -- `solid develop`, the shop floor's live viewer, the
  // standalone export page -- needs a number it can check before
  // mounting, and there is no other number to check it by.
  it('declares the read-expression-bindings API as version 7', () => {
    expect(API_VERSION).toBe(7);
  });
});
