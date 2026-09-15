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
  // Publishing the navigation state and a change subscription (OpenSpec
  // `observe-assembly-navigation`) is the one after that (9): a
  // navigator -- this package's own, in the next cycle, or a host's own
  // built on the same channel -- needs `navigation()` and
  // `onAssemblyChange()` to exist before it can be mounted at all, which
  // is exactly the capability a host may require this number exists to
  // answer.
  // Mounting the assembly navigator itself (OpenSpec `mount-the-navigator`,
  // ADR-050) is the one after that (10): `SolidNodeWidget.mountNavigator`
  // is a capability a host may require -- rather than build its own tree
  // over the state version 9 published -- and this is the number that
  // tells it whether the bundle carries one.
  // Mounting the composed inspector layout (OpenSpec
  // `ship-the-inspector-layout`, ADR-051) is the one after that (11):
  // `SolidNodeWidget.mountInspector` -- the sidebar, the navigator and
  // the viewer composed into one host element -- and
  // `mountDevelopment`, the development page's own mount built on it,
  // are capabilities a host may require rather than lay the parts out
  // itself; 10 was the bundle that carried a navigator with nowhere to
  // put it.
  // Binding a pick to a declared control (OpenSpec
  // `drive-the-run-by-touch`) is the one after that (12): a host that
  // means to present a machine a maker DRIVES BY TOUCHING IT -- the
  // shop floor, a gallery page -- needs to know the bundle it is about
  // to mount reads a document's `controls` table and binds a press and
  // a turn to it, and that `controls()` and `partControls` exist. 11
  // is the bundle that would show the same document with no affordance
  // at all, and no number would say so: the document versions this
  // build reads do NOT move, because `controls` is additive within
  // version 5 (solid-node ADR-112).
  // Drawing the markings a document's parts carry (OpenSpec
  // `draw-what-a-part-carries`) is the one after that (14): a studio
  // that means to show a readable Curta -- a machine whose ANSWER is
  // printed on its parts -- wants to know, before it mounts, whether
  // this bundle draws the digits or silently shows a blank drum. 13 is
  // SKIPPED deliberately: the in-flight cycle `slide-and-turn-parts`
  // claims it, and taking 14 here means the two numbers cannot collide
  // whatever order they integrate in (design D9). The document versions
  // this build reads do NOT move: `markings` is additive and gated on
  // no document version -- the framework's own marked fixture declares
  // version 2 -- which is the posture the `controls` table already set.
  // Executing a version 6 document -- a compiled program one of whose
  // laws READS THE COORDINATE IT DRIVES -- is the one after that (15).
  // This one is NOT additive, which is why the document list moves with
  // it: a bundle at 14 refuses the Curta's own clearing interface BY
  // NAME and renders nothing at all, so a host that means to present
  // such a machine has to be able to ask before it mounts. The
  // precedent is exact -- `run-in-the-worker` raised the API to 8 when
  // `documentVersions` grew to include 5 -- and the contrast is exact
  // too: `controls` and `markings` left the list alone because a
  // document carrying neither renders identically. 13 stays SKIPPED:
  // the in-flight cycle `slide-and-turn-parts` claims it, and taking 14
  // and then 15 here means the numbers cannot collide whatever order
  // they integrate in.
  it('declares the self-read API as version 15', () => {
    expect(API_VERSION).toBe(15);
  });
});

describe('DOCUMENT_VERSIONS', () => {
  it('is declared in package.json, where a Python caller can read it', () => {
    expect(Array.isArray(pkg.solidNodeDocumentVersions)).toBe(true);
    expect(pkg.solidNodeDocumentVersions).toEqual([1, 2, 3, 4, 5, 6]);
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
