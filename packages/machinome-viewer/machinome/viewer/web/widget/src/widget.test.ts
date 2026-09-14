/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The auto-mount's layout decision (design D8): no DOM is needed to
// decide it, so this runs in the default `node` environment -- no
// `@vitest-environment jsdom` pragma, unlike `inspector.test.ts` and
// `navigator.test.ts`.

import { describe, expect, it } from 'vitest';
import { layoutChoice } from './layout';

describe('layoutChoice (design D8)', () => {
  it('mounts the plain viewer when nothing asks for a layout', () => {
    expect(layoutChoice({}, new URLSearchParams())).toEqual({ layout: 'viewer' });
  });

  it('reads data-solid-layout="inspector" from the container', () => {
    expect(layoutChoice({ solidLayout: 'inspector' }, new URLSearchParams()))
      .toEqual({ layout: 'inspector' });
  });

  it('the query string overrides the attribute toward inspector', () => {
    expect(layoutChoice({ solidLayout: 'viewer' }, new URLSearchParams('layout=inspector')))
      .toEqual({ layout: 'inspector' });
  });

  it('the query string overrides the attribute toward viewer', () => {
    expect(layoutChoice({ solidLayout: 'inspector' }, new URLSearchParams('layout=viewer')))
      .toEqual({ layout: 'viewer' });
  });

  it('reads the initial sidebar state from data-solid-sidebar', () => {
    expect(layoutChoice(
      { solidLayout: 'inspector', solidSidebar: 'open' }, new URLSearchParams(),
    )).toEqual({ layout: 'inspector', sidebar: 'open' });
  });

  it('?sidebar= overrides data-solid-sidebar', () => {
    expect(layoutChoice(
      { solidLayout: 'inspector', solidSidebar: 'open' },
      new URLSearchParams('sidebar=collapsed'),
    )).toEqual({ layout: 'inspector', sidebar: 'collapsed' });
  });

  it('?sidebar= applies with no attribute at all', () => {
    expect(layoutChoice({}, new URLSearchParams('sidebar=open')))
      .toEqual({ layout: 'viewer', sidebar: 'open' });
  });

  it('reports an unrecognised attribute layout value by name', () => {
    expect(layoutChoice({ solidLayout: 'sidebar' }, new URLSearchParams()))
      .toEqual({ layout: { unknown: 'sidebar' } });
  });

  it('reports an unrecognised query-string layout value by name too', () => {
    expect(layoutChoice({ solidLayout: 'inspector' }, new URLSearchParams('layout=bogus')))
      .toEqual({ layout: { unknown: 'bogus' } });
  });
});
