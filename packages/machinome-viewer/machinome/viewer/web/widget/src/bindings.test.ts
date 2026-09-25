/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The document's binding table (OpenSpec `read-expression-bindings`,
// design D1-D7; ADR-044). A table this viewer cannot resolve is refused
// HERE, at construction, before any tree is built -- see viewer.test.ts's
// counterpart (via document.test.ts's `assertRenderable`) for the case
// where the refusal must be reached through the loader instead.

import { describe, expect, it } from 'vitest';
import { bindingTable, EMPTY_BINDINGS } from './bindings';
import { NodeId, valueOf } from './expressions';
import { Manifest, ManifestBinding, ManifestDriver } from './types';

const motor: ManifestDriver = {
  default: 8000, range: [0, 8000], unit: 'ustep', dtype: 'int', scale: 0.0125,
};

const document = (overrides: Partial<Manifest> = {}): Manifest => ({
  format: 'machinome-export',
  version: 4 as unknown as Manifest['version'],
  animation: { fps: 30, frames: 360 },
  root: { name: 'root', type: 'AssemblyNode', color: null, operations: [] },
  ...overrides,
});

describe('bindingTable: shape and validation (D7)', () => {
  it('refuses a bindings value that is not an array', () => {
    const manifest = document({ bindings: 'nope' as unknown as Manifest['bindings'] });
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/bindings/);
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses an entry that is not an object', () => {
    const manifest = document({
      bindings: ['nope' as unknown as ManifestBinding],
    });
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses an entry whose name is not a string', () => {
    const manifest = document({
      bindings: [{ name: 1 as unknown as string, expression: '$t' }],
    });
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses an entry whose expression is not a string', () => {
    const manifest = document({
      bindings: [{ name: '_b0', expression: 1 as unknown as string }],
    });
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses two entries under one name', () => {
    const manifest = document({
      bindings: [
        { name: '_b0', expression: '$t' },
        { name: '_b0', expression: '(2.0 * $t)' },
      ],
    });
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/_b0/);
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses an entry naming itself', () => {
    const manifest = document({
      bindings: [{ name: '_b0', expression: '(_b0 + 1.0)' }],
    });
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/_b0/);
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses an entry naming an entry later in the array', () => {
    const manifest = document({
      bindings: [
        { name: '_b0', expression: '(_b1 + 1.0)' },
        { name: '_b1', expression: '$t' },
      ],
    });
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/_b0/);
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/_b1/);
  });

  it('refuses an entry whose name is also a key of the drivers table', () => {
    const manifest = document({
      drivers: { _b0: motor },
      bindings: [{ name: '_b0', expression: '$t' }],
    });
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/_b0/);
  });

  it('refuses an entry whose expression carries an inline function, reaching the table', () => {
    const manifest = document({
      bindings: [{ name: '_b0', expression: '(x => x + 1)' }],
    });
    expect(() => bindingTable(manifest, '/m.json')).toThrow(/Func/);
  });
});

describe('bindingTable: the closure (D5)', () => {
  const chain = document({
    drivers: { 'x_axis.motor': motor },
    bindings: [
      { name: '_b0', expression: '($t * 2.0)' },
      { name: '_b1', expression: 'floor(_b0)' },
      { name: '_b3', expression: '(_b1 + x_axis.motor)' },
    ],
  });

  it('replaces a binding name with what it transitively reads', () => {
    const table = bindingTable(chain, '/m.json');
    expect(table.closure(new Set(['_b3']))).toEqual(new Set(['$t', 'x_axis.motor']));
  });

  it('leaves a name that is not an entry unchanged, dangling reference included', () => {
    const table = bindingTable(chain, '/m.json');
    expect(table.closure(new Set(['_b99']))).toEqual(new Set(['_b99']));
    expect(table.closure(new Set(['x_axis.motor']))).toEqual(new Set(['x_axis.motor']));
  });

  it('is empty for an empty set', () => {
    const table = bindingTable(chain, '/m.json');
    expect(table.closure(new Set())).toEqual(new Set());
  });
});

describe('bindingTable: the empty table', () => {
  it('gives roots() undefined and the identity closure for a document with no bindings key', () => {
    const table = bindingTable(document(), '/m.json');
    expect(table.roots()).toBeUndefined();
    expect(table.closure(new Set(['x_axis.motor']))).toEqual(new Set(['x_axis.motor']));
  });

  it('EMPTY_BINDINGS behaves the same', () => {
    expect(EMPTY_BINDINGS.roots()).toBeUndefined();
    expect(EMPTY_BINDINGS.closure(new Set(['x_axis.motor'])))
      .toEqual(new Set(['x_axis.motor']));
  });
});

describe('bindingTable: roots()', () => {
  it('maps each name to a node id, interning identical expression text together', () => {
    const manifest = document({
      bindings: [
        { name: '_b0', expression: '($t * 43200.0)' },
        { name: '_b1', expression: '($t * 43200.0)' },
      ],
    });
    const table = bindingTable(manifest, '/m.json');
    const roots = table.roots() as ReadonlyMap<string, NodeId>;

    expect(roots.get('_b0')).toBe(roots.get('_b1'));
    expect(valueOf(roots.get('_b0')!, { time: 0.5 })).toBe(0.5 * 43200.0);
  });
});
