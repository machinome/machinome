/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import * as THREE from 'three';
import { describe, expect, it, vi } from 'vitest';

const { loadAsync } = vi.hoisted(() => ({
  loadAsync: vi.fn(() => Promise.resolve(new THREE.BoxGeometry())),
}));

vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({
  STLLoader: class { loadAsync = loadAsync; },
}));

// The real evaluator, watched: what a driver change must NOT do is
// re-evaluate an expression that does not name it, and the only way to
// see that is to count the evaluations.
vi.mock('./evaluator', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./evaluator')>();
  return { ...actual, evalExpr: vi.fn(actual.evalExpr) };
});

import { evalExpr } from './evaluator';
import { bindingTable } from './bindings';
import { assemblyPathKey, materialForColor, WidgetTree } from './tree';
import { Manifest, ManifestNode } from './types';
import pascaline from '../../../tests/fixtures/pascaline/viewer.json';

const evaluations = () =>
  (evalExpr as unknown as ReturnType<typeof vi.fn>).mock.calls
    .map((call) => call[0] as string);

const leaf = (overrides: Partial<ManifestNode> = {}): ManifestNode => ({
  name: 'leaf', type: 'part', color: '#cc4444', operations: [],
  model: 'leaf.stl', mtime: 1, ...overrides,
});

const root = (children: ManifestNode[]): ManifestNode => ({
  name: 'root', type: 'assembly', color: null, operations: [], children,
});

// OpenSpec `read-expression-bindings`: a table built the same way
// `assertRenderable` builds one, over a hand-written {name, expression}
// array. `bindingTable` reads only `.bindings` and `.drivers`, so a
// minimal object stands in for a full `Manifest`.
const bindings = (
  entries: { name: string; expression: string }[],
  drivers: Record<string, unknown> = {},
) => bindingTable({ bindings: entries, drivers } as unknown as Manifest, '/m.json');

describe('materialForColor', () => {
  it('uses the development viewer normal material when no color is supplied', () => {
    expect(materialForColor(null)).toBeInstanceOf(THREE.MeshNormalMaterial);
  });

  it('keeps the standard material for an explicit color', () => {
    expect(materialForColor('#cc4444')).toBeInstanceOf(
      THREE.MeshStandardMaterial,
    );
  });
});

describe('WidgetTree targeted updates', () => {
  it('uses model path and mtime together as geometry identity', async () => {
    const tree = new WidgetTree(root([leaf()]), '/build/');
    await tree.loaded;
    loadAsync.mockClear();

    await tree.reconcile(root([leaf()]), '/build/');
    expect(loadAsync).not.toHaveBeenCalled();

    await tree.reconcile(root([leaf({ mtime: 2 })]), '/build/');
    await tree.reconcile(root([leaf({ model: 'other.stl', mtime: 2 })]), '/build/');
    expect(loadAsync.mock.calls.map(([url]) => url)).toEqual([
      '/build/leaf.stl', '/build/other.stl',
    ]);
  });

  it('replaces only the named artifact and leaves an unknown path alone', async () => {
    const tree = new WidgetTree(root([leaf(), leaf({ name: 'other', model: 'other.stl' })]), '/build/');
    await tree.loaded;
    const otherGroup = tree.children[1].group;
    loadAsync.mockClear();

    await tree.artifactChanged('leaf.stl', '/build/');
    await tree.artifactChanged('missing.stl', '/build/');

    expect(loadAsync.mock.calls.map(([url]) => url)).toEqual(['/build/leaf.stl']);
    expect(tree.children[1].group).toBe(otherGroup);
  });

  it('keeps the old tree when fetching a changed document mesh fails', async () => {
    const tree = new WidgetTree(root([leaf()]), '/build/');
    await tree.loaded;
    const previous = tree.children[0].group;
    loadAsync.mockRejectedValueOnce(new Error('network down'));

    await expect(tree.reconcile(root([leaf({ mtime: 2 })]), '/build/'))
      .rejects.toThrow('network down');
    expect(tree.children[0].group).toBe(previous);
  });

  it('does not partially update siblings when one replacement fails', async () => {
    const tree = new WidgetTree(root([
      leaf(), leaf({ name: 'other', model: 'other.stl' }),
    ]), '/build/');
    await tree.loaded;
    const first = tree.children[0].group;
    const second = tree.children[1].group;
    loadAsync.mockResolvedValueOnce(new THREE.BoxGeometry());
    loadAsync.mockRejectedValueOnce(new Error('second failed'));

    await expect(tree.reconcile(root([
      leaf({ mtime: 2 }), leaf({ name: 'other', model: 'other.stl', mtime: 2 }),
    ]), '/build/')).rejects.toThrow('second failed');
    expect(tree.children[0].group).toBe(first);
    expect(tree.children[1].group).toBe(second);
  });

  it('does not refetch a manifest reconcile that follows an artifact update for the same artifact', async () => {
    const tree = new WidgetTree(root([leaf()]), '/build/');
    await tree.loaded;
    loadAsync.mockClear();

    await tree.artifactChanged('leaf.stl', '/build/');
    expect(loadAsync).toHaveBeenCalledTimes(1);
    loadAsync.mockClear();

    await tree.reconcile(root([leaf({ mtime: 2 })]), '/build/');
    expect(loadAsync).not.toHaveBeenCalled();
  });

  it('reconciles structure and operations without refetching unchanged geometry', async () => {
    const tree = new WidgetTree(root([leaf()]), '/build/');
    await tree.loaded;
    const retained = tree.children[0].group;
    loadAsync.mockClear();

    await tree.reconcile(root([
      leaf({ operations: [['t', ['1', '0', '0']] as const] }),
      leaf({ name: 'added', model: 'added.stl' }),
    ]), '/build/');

    expect(tree.children[0].group).toBe(retained);
    expect(tree.children[0].operations).toEqual([['t', ['1', '0', '0']]]);
    expect(loadAsync.mock.calls.map(([url]) => url)).toEqual(['/build/added.stl']);
  });
});

describe('WidgetTree assembly navigation', () => {
  it('exposes stable paths and effective inherited colours', async () => {
    const tree = new WidgetTree({
      name: 'root', type: 'assembly', color: '#336699', operations: [],
      children: [
        {
          name: 'arm', type: 'assembly', color: null, operations: [],
          children: [leaf({ name: 'pin', color: null })],
        },
      ],
    }, '/build/');
    await tree.loaded;

    expect(tree.assembly()).toEqual({
      name: 'root', path: [], color: '#336699', model: false,
      children: [{
        name: 'arm', path: ['arm'], color: '#336699', model: false,
        children: [{
          name: 'pin', path: ['arm', 'pin'], color: '#336699', model: true,
          children: [],
        }],
      }],
    });
  });

  it('validates node paths and filters the rendered tree by focus and visibility', async () => {
    const tree = new WidgetTree(root([
      leaf({ name: 'left', model: 'left.stl' }),
      leaf({ name: 'right', model: 'right.stl' }),
    ]), '/build/');
    await tree.loaded;

    expect(tree.hasPath(['left'])).toBe(true);
    expect(tree.hasPath(['missing'])).toBe(false);
    expect(() => tree.requirePath(['missing'])).toThrow('Unknown assembly path: missing');

    tree.applyVisibility(['left'], new Set());
    expect(tree.group.visible).toBe(true);
    expect(tree.children[0].group.visible).toBe(true);
    expect(tree.children[1].group.visible).toBe(false);

    tree.applyVisibility(null, new Set([assemblyPathKey(['left'])]));
    expect(tree.children[0].group.visible).toBe(false);
    expect(tree.children[1].group.visible).toBe(true);
  });

  it('hides geometry owned by focus ancestors while retaining their transforms', async () => {
    const tree = new WidgetTree({
      ...root([
        leaf({ name: 'left', model: 'left.stl' }),
        leaf({ name: 'right', model: 'right.stl' }),
      ]),
      model: 'root.stl',
      mtime: 1,
    }, '/build/');
    await tree.loaded;

    tree.applyVisibility(['left'], new Set());

    const rootMesh = tree.group.children.find(
      (child): child is THREE.Mesh => child instanceof THREE.Mesh,
    );
    const leftMesh = tree.children[0].group.children.find(
      (child): child is THREE.Mesh => child instanceof THREE.Mesh,
    );
    expect(tree.group.visible).toBe(true);
    expect(rootMesh?.visible).toBe(false);
    expect(leftMesh?.visible).toBe(true);
    expect(tree.children[1].group.visible).toBe(false);
  });

  it('keeps a shown child occluded while its ancestor remains hidden', async () => {
    const tree = new WidgetTree(root([{
      name: 'arm', type: 'assembly', color: null, operations: [],
      children: [leaf({ name: 'pin' })],
    }]), '/build/');
    await tree.loaded;

    tree.applyVisibility(null, new Set([assemblyPathKey(['arm'])]));
    expect(tree.children[0].group.visible).toBe(false);
    expect(tree.children[0].children[0].group.visible).toBe(true);
  });
});

// ADR-056 stage 3b: which operations recompute is decided by the FREE
// VARIABLES of their parsed expressions (design D2), not by whether the
// raw string contains `$t`. A driver change must re-evaluate exactly the
// operations that name that driver, and nothing else -- that bound is
// what makes per-driver interactivity cheap on a large tree.
describe('WidgetTree driver-aware updates', () => {
  const STATIC = '90';
  const X_TERM = '(x_axis.motor * 0.0125)';
  const Y_TERM = '(y_axis.motor * 0.0125)';
  const SPIN = '(360.0 * $t)';
  const MIXED = '((5.0 * cos((360.0 * $t))) + ((x_axis.motor * 0.0125) * 0.1))';

  const machine = (): ManifestNode => root([
    leaf({ name: 'frame', operations: [['r', STATIC, [0, 0, 1]] as const] }),
    leaf({ name: 'x', operations: [['t', [X_TERM, '0', '0']] as const] }),
    leaf({ name: 'y', operations: [['t', [Y_TERM, '0', '0']] as const] }),
    leaf({ name: 'spin', operations: [['r', SPIN, [0, 0, 1]] as const] }),
    leaf({ name: 'cover', operations: [['t', [MIXED, '0', '0']] as const] }),
  ]);

  const scope = (time: number, x: number, y: number) => ({
    time, drivers: { x_axis: { motor: x }, y_axis: { motor: y } },
  });

  const mounted = async () => {
    const tree = new WidgetTree(machine(), '/build/');
    await tree.loaded;
    tree.update(scope(0, 8000, 2000));
    (evalExpr as unknown as ReturnType<typeof vi.fn>).mockClear();
    return tree;
  };

  it('re-evaluates only the operations naming a changed driver', async () => {
    const tree = await mounted();

    tree.update(scope(0, 1600, 2000),
                { time: false, drivers: new Set(['x_axis.motor']) });

    expect(evaluations()).toContain(X_TERM);
    expect(evaluations()).toContain(MIXED);
    expect(evaluations()).not.toContain(Y_TERM);
    expect(evaluations()).not.toContain(SPIN);
    expect(evaluations()).not.toContain(STATIC);
  });

  it('moves the carriage to the pose the new driver value implies', async () => {
    const tree = await mounted();

    tree.update(scope(0, 1600, 2000),
                { time: false, drivers: new Set(['x_axis.motor']) });

    expect(tree.children[1].group.matrix.elements[12]).toBeCloseTo(20);
    expect(tree.children[2].group.matrix.elements[12]).toBeCloseTo(25);
  });

  it('keeps animating $t operations from the time transport', async () => {
    const tree = await mounted();

    tree.update(scope(0.25, 8000, 2000),
                { time: true, drivers: new Set() });

    expect(evaluations()).toContain(SPIN);
    expect(evaluations()).toContain(MIXED);
    expect(evaluations()).not.toContain(X_TERM);
    expect(evaluations()).not.toContain(STATIC);
  });

  it('recomputes everything when nothing is named as changed', async () => {
    const tree = await mounted();

    tree.update(scope(0.25, 1600, 2000));

    expect(evaluations()).toContain(STATIC);
    expect(evaluations()).toContain(X_TERM);
    expect(evaluations()).toContain(Y_TERM);
  });

  it('reads `animated` off the parsed tree, not a substring', async () => {
    const timeDriven = new WidgetTree(machine(), '/build/');
    const driverOnly = new WidgetTree(root([
      leaf({ name: 'x', operations: [['t', [X_TERM, '0', '0']] as const] }),
    ]), '/build/');
    await Promise.all([timeDriven.loaded, driverOnly.loaded]);

    // A driver-driven document has no timeline to scrub: `animated` is
    // about the `$t` transport, and `x_axis.motor` is not it.
    expect(timeDriven.animated).toBe(true);
    expect(driverOnly.animated).toBe(false);
  });

  it('is not animated for a document a committed bank poses', async () => {
    // A version 5 document has no `$t`: its poses name bank
    // coordinates, so `animated` is false and the animation bar is not
    // built at all. Pinned on the acceptance document itself, so a
    // change that made both the timeline and the transport appear
    // beside each other would be loud here (OpenSpec
    // `drive-the-run-on-screen`, task 2.2).
    const document = pascaline as unknown as Manifest;
    const tree = new WidgetTree(document.root, './', null,
                               bindingTable(document, 'pascaline'));
    await tree.loaded;

    expect(document.version).toBe(5);
    expect(tree.animated).toBe(false);
  });

  it('forgets a node\'s free variables when its operations are replaced', async () => {
    const tree = await mounted();

    await tree.reconcile(root([
      leaf({ name: 'frame', operations: [['t', [X_TERM, '0', '0']] as const] }),
    ]), '/build/');
    (evalExpr as unknown as ReturnType<typeof vi.fn>).mockClear();

    tree.update(scope(0, 1600, 2000),
                { time: false, drivers: new Set(['x_axis.motor']) });

    expect(evaluations()).toContain(X_TERM);
  });
});

// OpenSpec `read-expression-bindings` (design D5, D6; ADR-044). The free
// set each node already computes is closed over the document's table, so
// `animated` and the re-evaluation bounding both follow what a binding
// TRANSITIVELY reads rather than what its own text mentions -- the exact
// failure the grasshopper clock's document showed: not one of its
// operation expressions contains `$t` as text, yet the machine moves.
describe('WidgetTree bindings: the timeline follows a binding (D6)', () => {
  const timeChain = bindings([
    { name: '_b0', expression: '($t * 43200.0)' },
    { name: '_b1', expression: 'floor(_b0)' },
  ]);

  it('is animated through a binding, though no operation text contains $t', async () => {
    const tree = new WidgetTree(root([
      leaf({ name: 'escapement', operations: [['r', '_b1', [0, 0, 1]] as const] }),
    ]), '/build/', null, timeChain);
    await tree.loaded;

    expect(tree.animated).toBe(true);
  });

  it('moves the operation when time changes, through the binding', async () => {
    const tree = new WidgetTree(root([
      leaf({ name: 'escapement', operations: [['r', '_b1', [0, 0, 1]] as const] }),
    ]), '/build/', null, timeChain);
    await tree.loaded;
    const scope = (time: number) => ({ time, bindings: timeChain.roots() });
    tree.update(scope(0));
    const before = tree.children[0].group.matrix.elements.slice();

    tree.update(scope(0.5), { time: true, drivers: new Set() });

    expect(tree.children[0].group.matrix.elements).not.toEqual(before);
  });

  it('without a table, an operation that is only a binding name is neither animated nor moved', async () => {
    // The negative case: `bindings` defaulting to `EMPTY_BINDINGS`
    // resolves nothing, so a document that NAMES bindings but is
    // mounted without its table stands still rather than crashing --
    // it does not read `$t` at all under the empty closure.
    const tree = new WidgetTree(root([
      leaf({ name: 'escapement', operations: [['r', '_b1', [0, 0, 1]] as const] }),
    ]), '/build/');
    await tree.loaded;

    expect(tree.animated).toBe(false);
  });
});

describe('WidgetTree bindings: driver dependence follows the table (D6)', () => {
  const scaled = (x: number, y: number) => ({
    time: 0, drivers: { x_axis: { motor: x }, y_axis: { motor: y } },
  });

  it('re-evaluates when the driver reached through a binding changes, and not another', async () => {
    const single = bindings(
      [{ name: '_b0', expression: '(x_axis.motor * 0.1)' }],
      { 'x_axis.motor': {} },
    );
    const tree = new WidgetTree(root([
      leaf({ name: 'moved', operations: [['t', ['_b0', '0', '0']] as const] }),
    ]), '/build/', null, single);
    await tree.loaded;
    const scope = (x: number, y: number) => ({ ...scaled(x, y), bindings: single.roots() });
    tree.update(scope(8000, 2000));
    (evalExpr as unknown as ReturnType<typeof vi.fn>).mockClear();

    tree.update(scope(1600, 2000), { time: false, drivers: new Set(['x_axis.motor']) });
    expect(evaluations()).toContain('_b0');

    (evalExpr as unknown as ReturnType<typeof vi.fn>).mockClear();
    tree.update(scope(1600, 500), { time: false, drivers: new Set(['y_axis.motor']) });
    expect(evaluations()).not.toContain('_b0');
  });

  it('carries dependence through a chain of two entries', async () => {
    const chain = bindings([
      { name: '_b0', expression: '(x_axis.motor * 2.0)' },
      { name: '_b1', expression: '(_b0 + 1.0)' },
    ], { 'x_axis.motor': {} });
    const tree = new WidgetTree(root([
      leaf({ name: 'moved', operations: [['t', ['_b1', '0', '0']] as const] }),
    ]), '/build/', null, chain);
    await tree.loaded;
    const scope = (x: number) => ({ time: 0, drivers: { x_axis: { motor: x } }, bindings: chain.roots() });
    tree.update(scope(0));
    (evalExpr as unknown as ReturnType<typeof vi.fn>).mockClear();

    tree.update(scope(3), { time: false, drivers: new Set(['x_axis.motor']) });

    expect(evaluations()).toContain('_b1');
    expect(tree.children[0].group.matrix.elements[12]).toBeCloseTo(7);
  });
});

// D11's proof, at the tree level: a document whose operations reference
// a bindings table poses exactly as the same machine with every
// reference written out in full.
describe('WidgetTree bindings: a bound document poses as the flat one it names (D11)', () => {
  it('matches a flat document element for element', async () => {
    const chain = bindings([
      { name: '_b0', expression: '($t * 43200.0)' },
      { name: '_b1', expression: '(_b0 + x_axis.motor)' },
    ], { 'x_axis.motor': {} });

    const bound = new WidgetTree(root([
      leaf({ name: 'spin', operations: [['r', '_b1', [0, 0, 1]] as const] }),
    ]), '/build/', null, chain);
    const flat = new WidgetTree(root([
      leaf({
        name: 'spin',
        operations: [['r', '(($t * 43200.0) + x_axis.motor)', [0, 0, 1]] as const],
      }),
    ]), '/build/');
    await Promise.all([bound.loaded, flat.loaded]);

    const time = 0.3333;
    const motor = 8000;
    bound.update({ time, drivers: { x_axis: { motor } }, bindings: chain.roots() });
    flat.update({ time, drivers: { x_axis: { motor } } });

    expect(bound.children[0].group.matrix.elements)
      .toEqual(flat.children[0].group.matrix.elements);
  });
});

// D6: "a reconcile carrying a table that differs from the one the node
// holds invalidates that node's free set ... whether or not its
// operations changed." An operation whose whole expression stays `_b3`
// across a republish is exactly the case a reconcile driven by CHANGED
// OPERATIONS would miss.
describe('WidgetTree bindings: a republish that changes only the table (D6)', () => {
  const machine = () => root([
    leaf({ name: 'moved', operations: [['t', ['_b3', '0', '0']] as const] }),
  ]);
  const overTime = () => bindings([{ name: '_b3', expression: '($t * 2.0)' }]);
  const overDriver = () => bindings(
    [{ name: '_b3', expression: '(x_axis.motor * 2.0)' }], { 'x_axis.motor': {} },
  );

  it('follows the table from $t to a driver, though "_b3" never changed', async () => {
    const timeTable = overTime();
    const tree = new WidgetTree(machine(), '/build/', null, timeTable);
    await tree.loaded;
    tree.update({ time: 0, drivers: { x_axis: { motor: 0 } }, bindings: timeTable.roots() });
    expect(tree.animated).toBe(true);

    const driverTable = overDriver();
    await tree.reconcile(machine(), '/build/', null, driverTable);

    expect(tree.animated).toBe(false);

    // A setTime-equivalent update no longer moves it.
    const before = tree.children[0].group.matrix.elements.slice();
    tree.update(
      { time: 0.9, drivers: { x_axis: { motor: 0 } }, bindings: driverTable.roots() },
      { time: true, drivers: new Set() },
    );
    expect(tree.children[0].group.matrix.elements).toEqual(before);

    // A driveTo-equivalent update on the driver it now reads does.
    tree.update(
      { time: 0.9, drivers: { x_axis: { motor: 5 } }, bindings: driverTable.roots() },
      { time: false, drivers: new Set(['x_axis.motor']) },
    );
    expect(tree.children[0].group.matrix.elements[12]).toBeCloseTo(10);
  });

  it('the mirror: follows the table from a driver to $t', async () => {
    const driverTable = overDriver();
    const tree = new WidgetTree(machine(), '/build/', null, driverTable);
    await tree.loaded;
    tree.update({ time: 0, drivers: { x_axis: { motor: 0 } }, bindings: driverTable.roots() });
    expect(tree.animated).toBe(false);

    const timeTable = overTime();
    await tree.reconcile(machine(), '/build/', null, timeTable);

    expect(tree.animated).toBe(true);
    tree.update(
      { time: 0.25, drivers: {}, bindings: timeTable.roots() },
      { time: true, drivers: new Set() },
    );
    expect(tree.children[0].group.matrix.elements[12]).toBeCloseTo(0.5);
  });

  it('a republish carrying an equal table invalidates nothing', async () => {
    const first = overTime();
    const tree = new WidgetTree(machine(), '/build/', null, first);
    await tree.loaded;
    tree.update({ time: 0, drivers: {}, bindings: first.roots() });
    expect(tree.animated).toBe(true);

    // A SEPARATE BindingTable instance, but the same name naming the
    // same expression text -- interning gives it the same node id, so
    // `bindingRootsEqual` reports no difference.
    const same = overTime();
    await tree.reconcile(machine(), '/build/', null, same);

    expect(tree.animated).toBe(true);
    tree.update(
      { time: 0.4, drivers: {}, bindings: same.roots() },
      { time: true, drivers: new Set() },
    );
    expect(tree.children[0].group.matrix.elements[12]).toBeCloseTo(0.8);
  });
});
