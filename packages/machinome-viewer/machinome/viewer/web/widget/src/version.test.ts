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
import { API_VERSION, DOCUMENT_VERSIONS } from './version';
import { RENDERED_VERSIONS } from './viewer';

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
  // Executing a published program (OpenSpec `run-in-the-worker`) is the
  // one after that (8): the document's `program` object, the run it
  // describes, and the `run()` operation on the handle. A host that
  // mounts a document the framework now publishes at version 5 -- `solid
  // develop`, the shop floor's live viewer, the standalone export page
  // -- needs a number it can check before mounting.
  it('declares the run-in-the-worker API as version 8', () => {
    expect(API_VERSION).toBe(8);
  });
});

describe('DOCUMENT_VERSIONS', () => {
  it('is declared in package.json, where a Python caller can read it', () => {
    expect(Array.isArray(pkg.solidNodeDocumentVersions)).toBe(true);
    expect(pkg.solidNodeDocumentVersions).toEqual([1, 2, 3, 4, 5]);
  });

  it('is the list the package declares, not a second copy', () => {
    expect([...DOCUMENT_VERSIONS]).toEqual(pkg.solidNodeDocumentVersions);
  });

  it('is exactly what the loader refuses by', () => {
    // The number the viewer REPORTS and the versions it REFUSES by
    // cannot be allowed to drift apart: a framework decides whether to
    // warn on a build and whether to refuse `solid snapshot --renderer
    // web` from this list, and the loader turns a document away by that
    // one.
    expect([...DOCUMENT_VERSIONS]).toEqual([...RENDERED_VERSIONS]);
  });
});
