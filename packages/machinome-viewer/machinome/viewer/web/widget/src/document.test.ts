/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The schema v2 consumer gate, INVERTED (ADR-056 stage 3b, design D8).
//
// The export delta's manifest contract says a consumer SHALL either
// evaluate driver-referencing expressions or fail loudly on a non-empty
// `drivers` table rather than render a wrong pose. Stage 3a took the
// second branch: this viewer evaluated `$t` and nothing else, so it
// refused every non-empty table. It now takes the first -- a document
// with drivers loads and renders at the pose its table's defaults
// imply, so these tests changed meaning with the capability.
//
// What stays refused is a MALFORMED document: one whose expressions
// name a qualified id its own table does not declare. There is no value
// to bind for it, and rendering it anyway would show a wrong machine
// rather than an error. The producer guarantees this cannot happen
// (every referenced id appears in the table); the gate is what makes a
// broken producer loud instead of silent.

import { describe, expect, it } from 'vitest';
import { assertRenderable, mountRetained } from './viewer';
import { expressionMetrics, prepare, releaseExpressions } from './expressions';
import {
  Manifest, ManifestFlexible, ManifestNode, RawOperation,
} from './types';

const node = (name: string, operations: RawOperation[],
              children?: ManifestNode[]): ManifestNode => ({
  name, type: 'AssemblyNode', color: null, operations, children,
});

// The valve spring of `tests/flexible_project/spring.py`, as the
// producer publishes it: the spec verbatim and one expression per
// parameter.
const SPRING_SPEC = {
  molejo: '0.1',
  profile: { type: 'circle', radius: 2.0 },
  path: [{ type: 'helix', radius: 14.0, turns: 6.5,
           height: { param: 'height' } }],
  loop: false,
  tessellation: { path: 240, profile: 16 },
};

const spring = (overrides: Partial<ManifestFlexible> = {}): ManifestNode => ({
  name: 'spring', type: 'LeafNode', color: null, operations: [],
  flexible: {
    tech: 'molejo', spec: SPRING_SPEC,
    params: { height: '(46.8 - valvetrain.lift)' },
    ...overrides,
  },
});

const lift = {
  default: 0.0, range: [0.0, 12.0], unit: 'mm',
  dtype: 'float', scale: null,
};

const document = (overrides: Partial<Manifest>): Manifest => ({
  format: 'solid-node-export',
  version: 2,
  animation: { fps: 30, frames: 360 },
  root: node('root', []),
  ...overrides,
});

const motor = {
  default: 8000, range: [0, 8000], unit: 'ustep',
  dtype: 'int', scale: 0.0125,
};

describe('assertRenderable', () => {
  it('accepts a version 1 document, which carries no table at all', () => {
    expect(() =>
      assertRenderable(document({ version: 1, drivers: undefined }), '/m.json'),
    ).not.toThrow();
  });

  it('accepts a version 2 document with an empty driver table', () => {
    expect(() =>
      assertRenderable(document({ drivers: {} }), '/m.json'),
    ).not.toThrow();
  });

  it('leaves a $t document alone: animation time is not a driver', () => {
    const manifest = document({
      drivers: {},
      root: node('root', [['r', '(360.0 * $t)', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('accepts a non-empty table whose ids its expressions declare', () => {
    // Stage 3a refused exactly this document. It now renders.
    const manifest = document({
      drivers: { 'x_axis.motor': motor },
      root: node('root', [], [
        node('x_axis', [], [
          node('carriage', [['t', ['(x_axis.motor * 0.0125)', '0', '0']]]),
        ]),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('refuses an expression naming an id the table does not declare', () => {
    const manifest = document({
      drivers: { 'x_axis.motor': motor },
      root: node('root', [], [
        node('z_axis', [['r', '(z_axis.motor * 0.1125)', [0, 0, 1]]]),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/z_axis\.motor/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses a driver expression under an empty table too', () => {
    const manifest = document({
      drivers: {},
      root: node('root', [['t', ['(x_axis.motor * 0.0125)', '0', '0']]]),
    });

    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/x_axis\.motor/);
  });

  it('names the undeclared id even beside a legal one', () => {
    const manifest = document({
      drivers: { 'x_axis.motor': motor },
      root: node('root', [['t', [
        '((x_axis.motor * 0.0125) + (y_axis.motor * 0.0125))', '0', '0',
      ]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/y_axis\.motor/);
  });
});

// Schema v3 (the flexible node shape). The producer emits the LOWEST
// version its content needs, so this viewer accepts the whole range it
// can render and refuses anything outside it -- the same posture it
// takes toward a `tech` it cannot evaluate, and for the same reason:
// a schema this build cannot read is not a document to guess at.
describe('assertRenderable on a flexible document', () => {
  it('accepts a version 3 document carrying a flexible node', () => {
    const manifest = document({
      version: 3,
      drivers: { 'valvetrain.lift': lift },
      root: node('engine', [], [node('valvetrain', [], [spring()])]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('refuses a technology it cannot evaluate, naming node and tech', () => {
    const manifest = document({
      version: 3,
      drivers: { 'valvetrain.lift': lift },
      root: node('engine', [], [spring({ tech: 'wibble' })]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/spring/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/wibble/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/molejo/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  // A `tech` this viewer evaluates, carrying a spec its bundled evaluator
  // cannot read -- what a document written for an older molejo is. The
  // document is refused whole, like an unevaluable technology, rather
  // than loading a tree that throws on a later frame.
  it('refuses a spec its evaluator cannot read, naming node and reason', () => {
    const manifest = document({
      version: 3,
      drivers: { 'valvetrain.lift': lift },
      root: node('engine', [], [
        spring({ spec: { ...SPRING_SPEC, molejo: 1 } }),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/spring/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/spec\.molejo/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses a version it does not render, naming it and the ones it does', () => {
    // OpenSpec `read-expression-bindings`: version 4 is now RENDERED (see
    // the `assertRenderable on a document carrying bindings` suite
    // below), so the version this test names moves to 5, the next one
    // still refused.
    const manifest = document({
      version: 5 as unknown as Manifest['version'],
      root: node('root', []),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/\b5\b/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/1, 2, 3, 4/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('holds a `params` expression to the same drivers table', () => {
    // `params` is an expression like any other, so an id its own table
    // does not declare is the same malformed document as an operation's
    // -- there is no value to bind, and evaluating it anyway would show
    // a wrong SHAPE instead of a wrong pose.
    const manifest = document({
      version: 3,
      drivers: {},
      root: node('engine', [], [spring()]),
    });

    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/valvetrain\.lift/);
  });

  it('leaves a `$t` parameter alone: animation time is not a driver', () => {
    const manifest = document({
      version: 3,
      drivers: {},
      root: node('engine', [], [
        spring({ params: { height: '(46.8 - (12.0 * $t))' } }),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });
});

// OpenSpec `read-expression-bindings` (design D7). Version 4's `bindings`
// table is validated at load, beside every refusal already here: a
// malformed table is refused naming the entry, a dangling reference is
// refused naming it (whether reached from an operation, a flexible
// `params` entry, or another binding's own expression), and a name that
// IS a binding is never reported as an undeclared driver -- the
// grasshopper document's exact shape, an empty `drivers` table whose
// every operation names an entry.
describe('assertRenderable on a document carrying bindings', () => {
  it('accepts a version 4 document carrying a table', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      bindings: [{ name: '_b0', expression: '(360.0 * $t)' }],
      root: node('root', [['r', '_b0', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('is a binding name, not an undeclared driver -- the grasshopper document\'s own shape', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      drivers: {},
      bindings: [
        { name: '_b0', expression: '($t * 43200.0)' },
        { name: '_b1', expression: 'floor(_b0)' },
      ],
      root: node('escapement', [['r', '_b1', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('refuses an operation naming an entry the table does not carry', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      bindings: [{ name: '_b0', expression: '$t' }],
      root: node('root', [['r', '_b99', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/_b99/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('reaches assertRenderable, rather than raising bare, for a malformed table', () => {
    // The 1.1 shape-and-validation cases, reached through the loader
    // this time: `bindingTable` throws, and `assertRenderable` -- which
    // calls it before walking a single expression -- does not catch or
    // reword it.
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      bindings: [
        { name: '_b0', expression: '$t' },
        { name: '_b0', expression: '(2.0 * $t)' },
      ],
      root: node('root', []),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/_b0/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses an undeclared driver id named from an ENTRY\'s own expression', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      drivers: { 'x_axis.motor': motor },
      bindings: [{ name: '_b0', expression: '(y_axis.motor * 2.0)' }],
      root: node('root', [['r', '_b0', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/y_axis\.motor/);
  });

  it('refuses a flexible leaf\'s `params` naming a dangling entry', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      drivers: {},
      bindings: [{ name: '_b0', expression: '$t' }],
      root: node('engine', [], [spring({ params: { height: '_b99' } })]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/_b99/);
  });

  it('resolves a chain of entries reached from an operation', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      drivers: { 'x_axis.motor': motor },
      bindings: [
        { name: '_b0', expression: '($t * 2.0)' },
        { name: '_b1', expression: '(_b0 + x_axis.motor)' },
      ],
      root: node('root', [['r', '_b1', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });
});

// D10: an expression form the shared evaluation cannot support -- an
// inline function, which nothing the producer emits carries -- is
// refused when the document is LOADED, beside the refusals above.
// `assertRenderable` already walks every operation's and every
// flexible node's `params` expression through `freeVariables` before
// anything is rendered, so once that walk reads the shared DAG this
// refusal happens here, with no change to viewer.ts.
describe('assertRenderable refuses an inline function (D10)', () => {
  it('names the form and quotes the expression, for an operation', () => {
    const expression = '(x => x + 1)';
    const manifest = document({
      root: node('root', [['r', expression, [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/Func/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/x => x \+ 1/);
  });

  it('names the form and quotes the expression, for a flexible `params` entry', () => {
    const manifest = document({
      version: 3,
      drivers: {},
      root: node('engine', [], [
        spring({ params: { height: '(x => x + 1)' } }),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/Func/);
  });

  it('truncates a very long refused expression rather than quoting it whole', () => {
    const expression = `(x => ${'1 + '.repeat(100)}1)`;
    const manifest = document({
      root: node('root', [['r', expression, [0, 0, 1]]]),
    });

    let message = '';
    try {
      assertRenderable(manifest, '/m.json');
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message.length).toBeLessThan(expression.length);
  });
});

// A refused mount must leave no hold on the shared table (D8): the
// spec's "disposing of the last viewer on the page leaves none of it"
// has to hold for a page whose viewer refused a document too, or a
// `solid develop` session that republishes a broken document and then
// a good one leaks a hold forever -- no handle, no dispose(), and
// nothing ever brings the mount count back to zero. `mountRetained`
// (viewer.ts) is the fix: it retains the shared table ONLY once its
// `action` -- `mount()`'s initial document load, `loadDocument` ->
// `assertRenderable`, exactly the D10 refusal surface -- has already
// succeeded. `mount()` itself needs a DOM/WebGL environment this
// package's suite does not set up, so this exercises the extracted,
// directly-testable piece that carries the actual fix.
describe('mountRetained holds the shared table only for a mount that succeeded (D8)', () => {
  it('a refused action never retains, so one later successful mount/dispose cycle alone empties the table', async () => {
    const refusal = new Error('refused: undeclared driver');

    await expect(mountRetained(async () => {
      throw refusal;
    })).rejects.toThrow(refusal);

    // If the refused attempt above HAD retained (the bug), this single
    // balanced retain/release from a genuinely successful mount would
    // leave the earlier, dangling hold still standing, and the table
    // would NOT come back to empty.
    await mountRetained(async () => {
      prepare('(9100001 + 1)');
    });
    releaseExpressions();

    expect(expressionMetrics().nodes).toBe(0);
  });

  it('retains once the action succeeds, so its own dispose (a matching release) does empty the table', async () => {
    await mountRetained(async () => {
      prepare('(9200002 + 2)');
    });
    expect(expressionMetrics().nodes).toBeGreaterThan(0);

    releaseExpressions(); // the handle's dispose(), in the real mount()

    expect(expressionMetrics().nodes).toBe(0);
  });
});
