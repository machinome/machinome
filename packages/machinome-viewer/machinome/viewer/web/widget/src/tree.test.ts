/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import { readFileSync } from 'node:fs';

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
import { bindingTable, EMPTY_BINDINGS } from './bindings';
import { controlPlan } from './options';
import { clockedScope } from './run/pose';
import {
  assemblyPathKey, liftAlongNormals, liftDecal, MARKING_LIFT, materialForColor,
  WidgetTree,
} from './tree';
import { Manifest, ManifestNode } from './types';
import pascaline from '../../../tests/fixtures/pascaline/viewer.json';
import regulator from '../../../tests/fixtures/regulator/viewer.json';
import markedFixture from '../../../tests/fixtures/marked/manifest.json';

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

  it('is not animated for an ELAPSED clocked document either: the clock '
     + 'is not $t', async () => {
    // OpenSpec `run-the-clock`, design §6 and task 5.6. The acceptance
    // document itself: the bob's pose reads the free name `time` -- a
    // BANK id in seconds -- and nothing in it reads `$t`, which is a
    // 0..1 animation variable and is never seconds (ADR-128 §10). So
    // `animated` is false, `controlPlan` builds no bar, and the clock's
    // transport is the only transport such a document has: there is
    // nothing for a maker to confuse it with.
    const document = regulator as unknown as Manifest;
    const tree = new WidgetTree(document.root, './', null,
                                bindingTable(document, 'regulator'));
    await tree.loaded;

    expect(document.version).toBe(8);
    expect((document as unknown as { clocked: { clock: string } })
      .clocked.clock).toBe('time');
    expect(tree.animated).toBe(false);
    expect(controlPlan('inline', tree.animated).bar).toBe(false);
  });

  it('IS animated where a document reads BOTH, and the two advance '
     + 'different values', async () => {
    // Where a document carries both -- a `$t` operation somewhere
    // alongside a clocked machine with a clock -- the two controls are
    // independent and each says what it advances: the timeline plays
    // `$t` over its frames, the transport advances the machine's
    // seconds, and neither touches the other's value. The pose reads
    // both through ONE scope, so a frame in which both moved
    // re-evaluates once.
    const both = new WidgetTree(root([
      leaf({ name: 'bob',
             operations: [['r', '(12.0 * sin((180.0 * time)))',
                           [0, 0, 1]] as const] }),
      leaf({ name: 'spinner',
             operations: [['r', '($t * 360.0)', [0, 0, 1]] as const] }),
    ]), '/build/');
    await both.loaded;
    expect(both.animated).toBe(true);
    expect(controlPlan('inline', both.animated).bar).toBe(true);

    const matrices = () => both.children.map(
      (child) => child.group.matrix.elements.slice());
    const scope = (time: number, seconds: number) => clockedScope(
      { time: seconds }, time, EMPTY_BINDINGS);

    both.update(scope(0, 0));
    const [bobAtRest, spinnerAtRest] = matrices();
    // The TRANSPORT moved: the bob follows the bank and the spinner does
    // not budge.
    both.update(scope(0, 0.5), { time: false, drivers: new Set(['time']) });
    const [bobMoved, spinnerStill] = matrices();
    expect(bobMoved).not.toEqual(bobAtRest);
    expect(spinnerStill).toEqual(spinnerAtRest);
    // The TIMELINE moved: the spinner follows `$t` and the bob stands.
    both.update(scope(0.25, 0.5), { time: true, drivers: new Set() });
    const [bobStill, spinnerMoved] = matrices();
    expect(spinnerMoved).not.toEqual(spinnerAtRest);
    expect(bobStill).toEqual(bobMoved);
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

// OpenSpec `draw-what-a-part-carries`: what a part CARRIES on its
// surface -- artwork, not a solid -- is drawn inside that part's own
// group (design D2), through the same `loadMesh` a model takes (D1),
// lifted off the nominal surface by the viewer's own rendering constant
// (D3).
describe('WidgetTree draws the markings a part carries', () => {
  const digits = { name: 'digits', model: 'dial.marking-digits.stl',
                   color: '#FFFFFF', mtime: 2 };
  const band = { name: 'band', model: 'dial.marking-band.stl',
                 color: '#C0C0C0', mtime: 3 };

  const marked = (markings = [digits, band]) =>
    root([leaf({ name: 'dial', model: 'dial.stl', markings })]);

  const decalMeshes = (part: WidgetTree): THREE.Mesh[] => {
    const groups = part.group.children
      .filter((child): child is THREE.Group => child instanceof THREE.Group);
    expect(groups.length).toBe(1);
    return groups[0].children
      .filter((child): child is THREE.Mesh => child instanceof THREE.Mesh);
  };

  it('loads one mesh per entry, in document order, through the model path', async () => {
    loadAsync.mockClear();
    const tree = new WidgetTree(marked(), '/build/');
    await tree.loaded;

    expect(loadAsync.mock.calls.map(([url]) => url).sort()).toEqual([
      '/build/dial.marking-band.stl',
      '/build/dial.marking-digits.stl',
      '/build/dial.stl',
    ]);
    expect(tree.children[0].markings.map((one) => one.name))
      .toEqual(['digits', 'band']);
  });

  it('puts the decals in a group of their own inside the part\'s group', async () => {
    const tree = new WidgetTree(marked(), '/build/');
    await tree.loaded;
    const part = tree.children[0];

    // The part's own mesh is a DIRECT child; the decals are not.
    expect(part.group.children
      .filter((child) => child instanceof THREE.Mesh).length).toBe(1);
    expect(decalMeshes(part).length).toBe(2);
    expect(decalMeshes(part)).toEqual(part.markings.map((one) => one.mesh));
  });

  it('gives each decal the colour its own entry declares', async () => {
    const tree = new WidgetTree(marked(), '/build/');
    await tree.loaded;
    const materials = decalMeshes(tree.children[0])
      .map((mesh) => mesh.material as THREE.MeshStandardMaterial);

    expect(materials[0].color.getHexString()).toBe('ffffff');
    expect(materials[1].color.getHexString()).toBe('c0c0c0');
  });

  it('adds nothing at all to a node that carries no markings', async () => {
    const tree = new WidgetTree(root([leaf()]), '/build/');
    await tree.loaded;
    const part = tree.children[0];

    expect(part.markings).toEqual([]);
    expect(part.group.children.filter(
      (child) => child instanceof THREE.Group).length).toBe(0);
    expect(part.group.children.length).toBe(1);
  });

  // Design D3: the bias is TWO things, and both belong to the viewer.
  it('draws a decal over the surface with the material design D3 states', async () => {
    const tree = new WidgetTree(marked([digits]), '/build/');
    await tree.loaded;
    const material = decalMeshes(tree.children[0])[0]
      .material as THREE.MeshStandardMaterial;

    // An open sheet has a back, and a decal must not vanish when the
    // camera crosses its plane.
    expect(material.side).toBe(THREE.DoubleSide);
    expect(material.polygonOffset).toBe(true);
    expect(material.polygonOffsetFactor).toBe(-1);
    expect(material.polygonOffsetUnits).toBe(-1);
    // A decal that did not write depth would show through everything
    // drawn after it.
    expect(material.depthWrite).toBe(true);
  });
});

// Design D3's world-space lift, pinned in BOTH direction and magnitude:
// 0.15 document units along each vertex's own normal. The direction
// argument relies on a property the producer has but the export spec
// does not yet promise -- a decal's triangles wind with their normal
// AWAY from the part -- so the fixture assertion below fails by name if
// a producer ever winds the other way, rather than drawing digits inside
// the roll.
describe('MARKING_LIFT', () => {
  it('is the ratified 0.15 document units', () => {
    expect(MARKING_LIFT).toBe(0.15);
  });

  it('moves each vertex along its own normal, by exactly the lift', () => {
    // One triangle in the z = 0 plane, wound counter-clockwise seen
    // from +z: its normal is +z, the way a `Flat` decal's is its
    // declared plane normal.
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(
      new Float32Array([0, 0, 0, 1, 0, 0, 0, 1, 0]), 3));
    geometry.computeVertexNormals();
    const normal = geometry.getAttribute('normal');
    expect([normal.getX(0), normal.getY(0), normal.getZ(0)]).toEqual([0, 0, 1]);

    liftAlongNormals(geometry);

    // Float32 storage, so the components are pinned to the precision
    // the buffer actually keeps.
    const position = geometry.getAttribute('position');
    [...position.array].forEach((value, index) => {
      expect(value).toBeCloseTo([0, 0, 0.15, 1, 0, 0.15, 0, 1, 0.15][index], 6);
    });
  });

  const fixtureDecal = async () => {
    const { STLLoader: RealSTLLoader } = await vi.importActual<
      typeof import('three/examples/jsm/loaders/STLLoader.js')
    >('three/examples/jsm/loaders/STLLoader.js');
    const bytes = readFileSync(new URL(
      '../../../tests/fixtures/marked/models/markings_project/'
      + 'dial-Dial-9f2c3557d753.marking-digits.stl',
      import.meta.url));
    return new RealSTLLoader().parse(
      bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
  };

  const radii = (geometry: THREE.BufferGeometry) => {
    const position = geometry.getAttribute('position');
    return Array.from({ length: position.count }, (_, index) =>
      Math.hypot(position.getX(index), position.getY(index)));
  };

  it('lifts the fixture\'s wrapped decal OUTWARD, every vertex of it', async () => {
    const geometry = await fixtureDecal();
    const before = radii(geometry);
    // The dial's nominal radius, which the artifact lies exactly on.
    expect(Math.min(...before)).toBeCloseTo(9.45, 5);
    expect(Math.max(...before)).toBeCloseTo(9.45, 5);

    const after = radii(liftDecal(geometry));

    expect(after.filter((value) => value > 9.45).length).toBe(after.length);
    // And by the lift itself, since the wrapped decal's normals are radial.
    expect(Math.min(...after)).toBeGreaterThan(9.45 + 0.9 * MARKING_LIFT);
    expect(Math.max(...after)).toBeLessThan(9.45 + 1.01 * MARKING_LIFT);
  });

  it('welds the sheet before lifting it, so it cannot tear open', async () => {
    // An STL arrives non-indexed, one private copy of each corner per
    // facet. Lifting each copy along its own FACE normal pulls adjacent
    // facets apart and the part shows through the cracks -- measured on
    // this very decal as a 0.031 mm tear along every internal edge,
    // drawn as a grid over the digits. Welding is what makes the sheet
    // move as one.
    const geometry = await fixtureDecal();
    expect(geometry.index).toBeNull();
    const facetCorners = geometry.getAttribute('position').count;

    const lifted = liftDecal(geometry);

    expect(lifted.index).not.toBeNull();
    expect(lifted.getAttribute('position').count).toBeLessThan(facetCorners);
    // Every facet still has its three corners.
    expect(lifted.index!.count).toBe(facetCorners);
  });
});

// Design D2's two filters, and the one line the sub-group costs.
describe('WidgetTree markings under the filters that select direct meshes', () => {
  const digits = { name: 'digits', model: 'dial.marking-digits.stl',
                   color: '#FFFFFF', mtime: 2 };

  const markedRoot = (color: string | null = null) => ({
    ...root([leaf({ name: 'pin', model: 'pin.stl' })]),
    color, model: 'base.stl', mtime: 1, markings: [digits],
  });

  const decals = (part: WidgetTree) => part.group.children
    .find((child): child is THREE.Group => child instanceof THREE.Group)!;

  it('does not draw an ancestor\'s decals while its own surface is not drawn', async () => {
    const tree = new WidgetTree(markedRoot(), '/build/');
    await tree.loaded;

    tree.applyVisibility(['pin'], new Set());

    // The group itself stays visible to preserve the focused node's
    // transform; the ancestor's own surface is not drawn -- and its
    // decals ARE its own surface.
    expect(tree.group.visible).toBe(true);
    expect(tree.group.children.find(
      (child): child is THREE.Mesh => child instanceof THREE.Mesh)!.visible)
      .toBe(false);
    expect(decals(tree).visible).toBe(false);

    tree.applyVisibility(null, new Set());
    expect(decals(tree).visible).toBe(true);
  });

  it('leaves a decal\'s material alone when the part\'s inherited colour moves', async () => {
    const tree = new WidgetTree(markedRoot(null), '/build/');
    await tree.loaded;
    const material = tree.markings[0].mesh.material as THREE.MeshStandardMaterial;

    await tree.reconcile(markedRoot('#336699'), '/build/');

    expect(tree.markings[0].mesh.material).toBe(material);
    expect(material.color.getHexString()).toBe('ffffff');
    expect((material as THREE.Material).side).toBe(THREE.DoubleSide);
  });

  it('leaves a decal\'s geometry alone when the part\'s own model is replaced', async () => {
    const tree = new WidgetTree(markedRoot(), '/build/');
    await tree.loaded;
    const mesh = tree.markings[0].mesh;
    const geometry = mesh.geometry;
    loadAsync.mockClear();

    await tree.reconcile({ ...markedRoot(), model: 'base2.stl' }, '/build/');

    expect(loadAsync.mock.calls.map(([url]) => url)).toEqual(['/build/base2.stl']);
    expect(tree.markings[0].mesh).toBe(mesh);
    expect(tree.markings[0].mesh.geometry).toBe(geometry);
    expect(geometry.getAttribute('position')).toBeDefined();
    expect(decals(tree).children).toEqual([mesh]);
  });
});

// Design D7: a marking is NOT a part, and the assembly readback is the
// first place that has to be true. `assembly()` walks `this.children`,
// which are `WidgetTree`s, so a marking is excluded BY CONSTRUCTION --
// and "by construction" is a property of today's code, which is why it
// is pinned here on the framework's own marked document.
describe('WidgetTree assembly over a marked document', () => {
  const stripped = (node: ManifestNode): ManifestNode => {
    const { markings, ...rest } = node as ManifestNode & { markings?: unknown };
    void markings;
    return { ...rest, children: node.children?.map(stripped) } as ManifestNode;
  };

  it('reads back exactly the snapshot its unmarked twin reads back', async () => {
    const document = markedFixture as unknown as Manifest;
    const marked = new WidgetTree(document.root, '/build/');
    const twin = new WidgetTree(stripped(document.root), '/build/');
    await Promise.all([marked.loaded, twin.loaded]);

    expect(marked.assembly()).toEqual(twin.assembly());
    // And nothing named for a marking is anywhere in it.
    const names: string[] = [];
    const walk = (node: ReturnType<WidgetTree['assembly']>) => {
      names.push(node.name);
      node.children.forEach(walk);
    };
    walk(marked.assembly());
    expect(names).toEqual(['Bench', 'dial', 'plate']);
    expect(marked.children[0].markings.map((one) => one.name)).toEqual(['digits']);
    expect(marked.children[1].markings.map((one) => one.name))
      .toEqual(['badge', 'band']);
  });

  it('hides a marked part\'s decals with it and restores them with it', async () => {
    // The path `setVisible` drives: a hidden part's group is invisible,
    // and there is no path that names a marking, so a decal is hidden
    // with its part and in no other way.
    const document = markedFixture as unknown as Manifest;
    const tree = new WidgetTree(document.root, '/build/');
    await tree.loaded;
    const plate = tree.children[1];

    tree.applyVisibility(null, new Set([assemblyPathKey(['plate'])]));
    expect(plate.group.visible).toBe(false);
    expect(tree.children[0].group.visible).toBe(true);

    tree.applyVisibility(null, new Set());
    expect(plate.group.visible).toBe(true);
    expect(plate.markings.every((one) => one.mesh.visible)).toBe(true);
  });
});

// Design D5: a decal has its OWN currency. The producer's whole currency
// split exists so that editing artwork moves the marking's stamp and
// leaves the part's STL current -- so a targeted update refetches a
// decal without refetching the part it is on, and the mirror.
describe('WidgetTree markings reload on their own currency', () => {
  const digits = { name: 'digits', model: 'dial.marking-digits.stl',
                   color: '#FFFFFF', mtime: 2 };
  const band = { name: 'band', model: 'dial.marking-band.stl',
                 color: '#C0C0C0', mtime: 3 };

  // `null` means the node carries NO `markings` key at all, which a
  // default parameter could not express: an explicit `undefined` takes
  // the default.
  const marked = (markings: unknown[] | null = [digits, band],
                  overrides: Partial<ManifestNode> = {}) => root([{
    ...leaf({ name: 'dial', model: 'dial.stl', ...overrides }),
    ...(markings === null ? {} : { markings }),
  } as ManifestNode]);

  const mounted = async (markings?: unknown[]) => {
    const tree = new WidgetTree(marked(markings), '/build/');
    await tree.loaded;
    loadAsync.mockClear();
    return tree;
  };

  const fetched = () => loadAsync.mock.calls.map(([url]) => url);

  const decalGroup = (part: WidgetTree) => part.group.children
    .find((child): child is THREE.Group => child instanceof THREE.Group);

  it('refetches a marking whose mtime moved, and not the part it is on', async () => {
    const tree = await mounted();
    const partMesh = tree.children[0].group.children.find(
      (child): child is THREE.Mesh => child instanceof THREE.Mesh);

    await tree.reconcile(marked([{ ...digits, mtime: 9 }, band]), '/build/');

    expect(fetched()).toEqual(['/build/dial.marking-digits.stl']);
    expect(tree.children[0].group.children.find(
      (child): child is THREE.Mesh => child instanceof THREE.Mesh)).toBe(partMesh);
    expect(decalGroup(tree.children[0])!.children.length).toBe(2);
  });

  it('refetches a marking whose model path moved, and not the part', async () => {
    const tree = await mounted();

    await tree.reconcile(
      marked([{ ...digits, model: 'dial.marking-digits-2.stl' }, band]), '/build/');

    expect(fetched()).toEqual(['/build/dial.marking-digits-2.stl']);
    expect(tree.children[0].markings[0].model).toBe('dial.marking-digits-2.stl');
  });

  it('refetches a part whose model moved, and none of its markings', async () => {
    const tree = await mounted();
    const meshes = tree.children[0].markings.map((one) => one.mesh);

    await tree.reconcile(marked([digits, band], { mtime: 7 }), '/build/');

    expect(fetched()).toEqual(['/build/dial.stl']);
    expect(tree.children[0].markings.map((one) => one.mesh)).toEqual(meshes);
  });

  it('removes a marking dropped from the list and leaves the rest standing', async () => {
    const tree = await mounted();
    const dropped = tree.children[0].markings[0].mesh;
    const kept = tree.children[0].markings[1].mesh;
    const disposed = vi.spyOn(dropped.geometry, 'dispose');

    await tree.reconcile(marked([band]), '/build/');

    expect(fetched()).toEqual([]);
    expect(disposed).toHaveBeenCalled();
    expect(tree.children[0].markings.map((one) => one.name)).toEqual(['band']);
    expect(decalGroup(tree.children[0])!.children).toEqual([kept]);
  });

  it('drops the group when the whole markings key disappears', async () => {
    const tree = await mounted();

    await tree.reconcile(marked(null), '/build/');

    expect(tree.children[0].markings).toEqual([]);
    expect(decalGroup(tree.children[0])).toBeUndefined();
    expect(tree.children[0].group.children.filter(
      (child) => child instanceof THREE.Mesh).length).toBe(1);
  });

  it('creates the group for a marking added to a node that had none', async () => {
    const tree = await mounted([]);

    await tree.reconcile(marked([digits]), '/build/');

    expect(fetched()).toEqual(['/build/dial.marking-digits.stl']);
    expect(tree.children[0].markings.map((one) => one.name)).toEqual(['digits']);
    expect(decalGroup(tree.children[0])!.children.length).toBe(1);
  });

  it('keeps document order when a marking is inserted before another', async () => {
    const tree = await mounted([band]);

    await tree.reconcile(marked([digits, band]), '/build/');

    expect(tree.children[0].markings.map((one) => one.name))
      .toEqual(['digits', 'band']);
    expect(decalGroup(tree.children[0])!.children)
      .toEqual(tree.children[0].markings.map((one) => one.mesh));
  });

  it('replaces the material of a retained marking whose colour moved, with no refetch', async () => {
    const tree = await mounted();
    const mesh = tree.children[0].markings[0].mesh;
    const previous = mesh.material as THREE.MeshStandardMaterial;
    const disposed = vi.spyOn(previous, 'dispose');

    await tree.reconcile(marked([{ ...digits, color: '#112233' }, band]), '/build/');

    expect(fetched()).toEqual([]);
    expect(tree.children[0].markings[0].mesh).toBe(mesh);
    expect((mesh.material as THREE.MeshStandardMaterial).color.getHexString())
      .toBe('112233');
    expect((mesh.material as THREE.MeshStandardMaterial).polygonOffset).toBe(true);
    expect(disposed).toHaveBeenCalled();
  });

  it('routes artifactChanged to the marking that owns the path, and to it alone', async () => {
    const tree = await mounted();
    const partMesh = tree.children[0].group.children.find(
      (child): child is THREE.Mesh => child instanceof THREE.Mesh);
    const before = tree.children[0].markings[0].mesh;

    await tree.artifactChanged('dial.marking-digits.stl', '/build/');

    expect(fetched()).toEqual(['/build/dial.marking-digits.stl']);
    expect(tree.children[0].markings[0].mesh).not.toBe(before);
    expect(tree.children[0].markings[1].mesh).toBeDefined();
    expect(tree.children[0].group.children.find(
      (child): child is THREE.Mesh => child instanceof THREE.Mesh)).toBe(partMesh);
    expect(decalGroup(tree.children[0])!.children)
      .toEqual(tree.children[0].markings.map((one) => one.mesh));
  });

  it('does not refetch the reconcile that follows a marking\'s artifact update', async () => {
    // The manifest publishes AFTER the artifact, so the reconcile that
    // follows names a new mtime for bytes already on screen. A decal's
    // flag is independent of its node's, because their stamps are.
    const tree = await mounted();

    await tree.artifactChanged('dial.marking-digits.stl', '/build/');
    loadAsync.mockClear();

    await tree.reconcile(marked([{ ...digits, mtime: 99 }, band]), '/build/');
    expect(fetched()).toEqual([]);

    // And the flag is consumed: a later genuine change is still caught.
    await tree.reconcile(marked([{ ...digits, mtime: 100 }, band]), '/build/');
    expect(fetched()).toEqual(['/build/dial.marking-digits.stl']);
  });

  it('leaves the whole previous scene standing when a decal fetch rejects', async () => {
    const tree = await mounted();
    const part = tree.children[0];
    const meshes = part.markings.map((one) => one.mesh);
    const partMesh = part.group.children.find(
      (child): child is THREE.Mesh => child instanceof THREE.Mesh);
    loadAsync.mockRejectedValueOnce(new Error('decal fetch failed'));

    await expect(tree.reconcile(
      marked([{ ...digits, mtime: 9 }, band], { mtime: 7 }), '/build/'))
      .rejects.toThrow('decal fetch failed');

    expect(tree.children[0]).toBe(part);
    expect(part.markings.map((one) => one.mesh)).toEqual(meshes);
    expect(part.group.children.find(
      (child): child is THREE.Mesh => child instanceof THREE.Mesh)).toBe(partMesh);

    // And a later update still succeeds.
    await tree.reconcile(marked([{ ...digits, mtime: 9 }, band]), '/build/');
    expect(part.markings[0].mesh).not.toBe(meshes[0]);
  });
});

// Design D2, the last thing membership in the part's group buys:
// `viewer.ts`'s `rebuildPartControls` (`:673-696`) traverses the
// control's part group and collects every `THREE.Mesh` under it. A decal
// on a touchable dial is therefore pressable and highlights WITH the
// dial -- which is what a maker means when they press the digit they can
// see -- and `artifactChanged`'s handler needs no change beyond what
// `tree.ts` now does, because the traverse is rerun there already.
describe('a decal is part of the surface a control is bound to', () => {
  it('is collected by the traverse rebuildPartControls performs', async () => {
    const tree = new WidgetTree(root([{
      ...leaf({ name: 'dial', model: 'dial.stl' }),
      markings: [{ name: 'digits', model: 'dial.marking-digits.stl',
                   color: '#FFFFFF', mtime: 2 }],
    } as ManifestNode]), '/build/');
    await tree.loaded;

    const meshes: THREE.Mesh[] = [];
    tree.requirePath(['dial']).group.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        meshes.push(object);
      }
    });

    expect(meshes.length).toBe(2);
    expect(meshes).toContain(tree.children[0].markings[0].mesh);
  });
});
