/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The owners of the scene count (OpenSpec
// `draw-only-when-the-picture-changes`, design Decisions 2 and 8, U1 to
// U7): the mount's picture revision, carried by the holder, is raised by
// the tree's four writers and by the holder's one assignment of a
// mesh's material, and by nothing else; and the camera is compared by
// value under `Object.is`.
//
// Everything this change adds is read through its module's namespace --
// `presentation.picture` off the holder, and `picture.ts` by a dynamic
// import inside the tests -- so this file loads on the base, where each
// test fails at the absent member or module.
//
// What these cannot see: a writer outside these methods, and whether the
// loop reads the revision (the mount's bench, `draw-on-change.test.ts`,
// S4 to S6).

import * as THREE from 'three';
import { afterEach, describe, expect, it, vi } from 'vitest';

const { loadAsync } = vi.hoisted(() => ({
  loadAsync: vi.fn(() => Promise.resolve(new THREE.BoxGeometry())),
}));

vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({
  STLLoader: class { loadAsync = loadAsync; },
}));

import { EMPTY_BINDINGS } from './bindings';
import type { EvalScope } from './evaluator';
import { FlexibleShape } from './flexible';
import { MaterialPresentation } from './presentation';
import { RIGID, WidgetTree } from './tree';
import type { ManifestNode } from './types';

/** The holder's revision, read through the holder as the viewer reads it. */
function revision(holder: MaterialPresentation): number {
  return (holder as unknown as { picture: { value(): number } }).picture.value();
}

/** `picture.ts`, which the base does not have. A variable specifier, so
 * the transform does not resolve it before the test runs. */
const PICTURE = './picture';
async function pictureModule(): Promise<{
  cameraReading(camera: THREE.Camera): number[];
  sameReading(a: readonly number[], b: readonly number[]): boolean;
  PictureRevision: new () => { value(): number; raise(): void };
}> {
  return await import(/* @vite-ignore */ PICTURE);
}

interface Deferred<T> {
  promise: Promise<T>;
  resolve(value: T): void;
  reject(error: Error): void;
}
function deferred<T>(): Deferred<T> {
  let resolve!: (value: T) => void;
  let reject!: (error: Error) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

const SPRING_SPEC = {
  molejo: '0.1',
  profile: { type: 'circle', radius: 2.0 },
  path: [{ type: 'helix', radius: 14.0, turns: 6.5, height: { param: 'height' } }],
  loop: false,
  tessellation: { path: 48, profile: 8 },
};

const node = (name: string, operations: ManifestNode['operations'],
              extra: Partial<ManifestNode> = {}): ManifestNode => ({
  name, type: 'LeafNode', color: '#cc4444', operations, ...extra,
});

/** Two placed parts, one reading `x` and one `y`, and a flexible part
 * reading `lift`; nothing reads `z`. */
function document(models = false): ManifestNode {
  return {
    name: 'root', type: 'AssemblyNode', color: null, operations: [], children: [
      node('a', [['t', ['x', '0', '0']]], models ? { model: 'a.stl', mtime: 1 } : {}),
      node('b', [['r', '(y * 2)', [0, 0, 1]]], models ? { model: 'b.stl', mtime: 1 } : {}),
      node('spring', [], {
        flexible: { tech: 'molejo', spec: SPRING_SPEC, params: { height: '(46.8 - lift)' } },
      }),
    ],
  };
}

const scope = (x = 0, y = 0, lift = 0, z = 0): EvalScope => ({
  time: 0, drivers: { x, y, lift, z },
});
const moved = (...ids: string[]) => ({ time: false, drivers: new Set(ids) });

async function built(models = false): Promise<{ tree: WidgetTree; holder: MaterialPresentation }> {
  const holder = new MaterialPresentation();
  const tree = new WidgetTree(document(models), '/', null, EMPTY_BINDINGS, undefined, holder);
  await tree.loaded;
  tree.update(scope());
  return { tree, holder };
}

afterEach(() => {
  vi.restoreAllMocks();
  loadAsync.mockReset();
  loadAsync.mockImplementation(() => Promise.resolve(new THREE.BoxGeometry()));
});

describe('U1: update raises the revision when its change set reaches a node', () => {
  it('raises it for a transform the change set reaches', async () => {
    const { tree, holder } = await built();
    const before = revision(holder);
    tree.update(scope(3), moved('x'));
    expect(revision(holder)).not.toBe(before);
  });

  it('raises it for a flexible part the change set reaches', async () => {
    const { tree, holder } = await built();
    const before = revision(holder);
    tree.update(scope(0, 0, 4), moved('lift'));
    expect(revision(holder)).not.toBe(before);
  });

  it('raises it for an update of everything', async () => {
    const { tree, holder } = await built();
    const before = revision(holder);
    tree.update(scope(1, 1, 1));
    expect(revision(holder)).not.toBe(before);
  });

  it('does not raise it when the change set reaches no node', async () => {
    const { tree, holder } = await built();
    const before = revision(holder);
    tree.update(scope(), moved());
    tree.update(scope(0, 0, 0, 7), moved('z'));
    tree.update(scope(), { time: true, drivers: new Set() });
    expect(revision(holder)).toBe(before);
  });

  it('raises it before its first write, so an update that wrote and then threw is still drawn', async () => {
    const { tree, holder } = await built();
    const before = revision(holder);
    const group = tree.children[0].group;
    const matrix = group.matrix.clone();
    vi.spyOn(FlexibleShape.prototype, 'evaluate').mockImplementation(() => {
      throw new Error('refused after a transform was written');
    });
    expect(() => tree.update(scope(5, 0, 2), moved('x', 'lift'))).toThrow(/refused after/);
    expect(group.matrix.equals(matrix), 'the transform was written').toBe(false);
    expect(revision(holder)).not.toBe(before);
  });

  it('does not raise it for an update refused before it wrote anything', async () => {
    const { tree, holder } = await built();
    const before = revision(holder);
    expect(() => tree.update(scope(Number.POSITIVE_INFINITY), moved('x'))).toThrow();
    expect(revision(holder)).toBe(before);
  });
});

describe('U2: admit never raises it', () => {
  it('judging a pose writes nothing and raises nothing', async () => {
    const { tree, holder } = await built();
    const before = revision(holder);
    tree.admit(scope(4, 2, 3), moved('x', 'y', 'lift'));
    tree.admit(scope(4, 2, 3));
    expect(revision(holder)).toBe(before);
  });
});

describe('U3: applyVisibility raises it', () => {
  it('raises it each time visibility is applied', async () => {
    const { tree, holder } = await built();
    const before = revision(holder);
    tree.applyVisibility(null, new Set(['["a"]']));
    const once = revision(holder);
    expect(once).not.toBe(before);
    tree.applyVisibility(['b'], new Set());
    expect(revision(holder)).not.toBe(once);
  });
});

describe('U4: artifactChanged raises it when it applies, not while its loads are pending, not when they fail', () => {
  it('raises it once the replacement is applied, and not before', async () => {
    const { tree, holder } = await built(true);
    const before = revision(holder);
    const load = deferred<THREE.BufferGeometry>();
    loadAsync.mockImplementationOnce(() => load.promise);
    const changing = tree.artifactChanged('a.stl', '/');
    await Promise.resolve();
    expect(revision(holder), 'while the load is pending').toBe(before);
    load.resolve(new THREE.BoxGeometry(5, 5, 5));
    await changing;
    expect(revision(holder)).not.toBe(before);
  });

  it('does not raise it when its load fails', async () => {
    const { tree, holder } = await built(true);
    const before = revision(holder);
    loadAsync.mockImplementationOnce(() => Promise.reject(new Error('network down')));
    await expect(tree.artifactChanged('a.stl', '/')).rejects.toThrow(/network down/);
    expect(revision(holder)).toBe(before);
  });
});

describe('U5: reconcile raises it when it applies, not before, and a refused one does not', () => {
  it('raises it when the republished tree is applied, and not before', async () => {
    const { tree, holder } = await built(true);
    const before = revision(holder);
    const next = document(true);
    next.children![0].operations = [['t', ['x', '0', '3']]];
    next.children![1] = { ...next.children![1], model: 'b2.stl' };
    const load = deferred<THREE.BufferGeometry>();
    loadAsync.mockImplementationOnce(() => load.promise);
    let atCommit: number | undefined;
    const reconciling = tree.reconcile(next, '/', null, EMPTY_BINDINGS, () => scope(),
                                       () => { atCommit = revision(holder); });
    await Promise.resolve();
    expect(revision(holder), 'while the load is pending').toBe(before);
    load.resolve(new THREE.BoxGeometry(5, 5, 5));
    await reconciling;
    expect(atCommit, 'before the application').toBe(before);
    expect(revision(holder)).not.toBe(before);
  });

  // Added in review. The mount hands `reconcile` a candidate scope, so the
  // update that follows the application raises the revision too, and
  // removing the application's own raise turned no test red. A caller
  // that hands no scope gets no update: the application's raise is all
  // there is.
  it('raises it for an application no update follows', async () => {
    const { tree, holder } = await built(true);
    const before = revision(holder);
    const next = document(true);
    next.children![1] = { ...next.children![1], model: 'b4.stl' };
    await tree.reconcile(next, '/', null, EMPTY_BINDINGS);
    expect(revision(holder)).not.toBe(before);
  });

  it('does not raise it for a republish its admission refuses', async () => {
    const { tree, holder } = await built(true);
    const before = revision(holder);
    const next = document(true);
    next.children![0].operations = [['t', ['(x / 0)', '0', '0']]];
    await expect(tree.reconcile(next, '/', null, EMPTY_BINDINGS, () => scope(1)))
      .rejects.toThrow();
    expect(revision(holder)).toBe(before);
  });

  it('does not raise it for a republish whose load fails', async () => {
    const { tree, holder } = await built(true);
    const before = revision(holder);
    const next = document(true);
    next.children![1] = { ...next.children![1], model: 'b3.stl' };
    loadAsync.mockImplementationOnce(() => Promise.reject(new Error('network down')));
    await expect(tree.reconcile(next, '/', null, EMPTY_BINDINGS, () => scope()))
      .rejects.toThrow(/network down/);
    expect(revision(holder)).toBe(before);
  });
});

describe('U6: the holder raises it on every pointer change, and on nothing else', () => {
  const meshes = (holder: MaterialPresentation) => {
    const geometry = new THREE.BoxGeometry();
    return {
      one: holder.mesh(geometry, RIGID, '#ff0000'),
      two: holder.mesh(geometry, RIGID, '#ff0000'),
      normal: holder.mesh(geometry, RIGID, null),
    };
  };

  it('making a mesh raises nothing: no mesh is pointed elsewhere', () => {
    const holder = new MaterialPresentation();
    const before = revision(holder);
    meshes(holder);
    expect(revision(holder)).toBe(before);
  });

  it('a hover, a highlight, its put-back, a chosen colour, a recolour and a forget each raise it', () => {
    const holder = new MaterialPresentation();
    const { one, two } = meshes(holder);
    const steps: Array<[string, () => void]> = [
      ['hover', () => holder.setHover([one])],
      ['hover moved', () => holder.setHover([two])],
      ['hover ended', () => holder.setHover([])],
      ['highlight', () => holder.setHighlight({ lit: [one], others: [two], color: '#00ff00', mode: 'dim' })],
      ['put-back', () => holder.setHighlight(null)],
      ['setBaseColor to another colour', () => holder.setBaseColor(one, '#0000ff')],
      ['recolor', () => holder.recolor(two, '#123456')],
      ['forget with an overlay standing', () => { holder.setHover([one]); holder.forget(); }],
    ];
    for (const [name, step] of steps) {
      const before = revision(holder);
      step();
      expect(revision(holder), name).not.toBe(before);
    }
  });

  it('a call that points nothing elsewhere raises nothing', () => {
    const holder = new MaterialPresentation();
    const { one, normal } = meshes(holder);
    holder.setHover([one]);
    const hovered = revision(holder);
    holder.setHover([one]);
    expect(revision(holder), 'the same hover again').toBe(hovered);
    holder.setHover([]);
    const plain = revision(holder);
    holder.setHighlight({ lit: [normal], others: [], color: '#00ff00', mode: 'keep' });
    expect(revision(holder), 'a normal material under a lit highlight').toBe(plain);
    holder.setHighlight(null);
    expect(revision(holder), 'its put-back').toBe(plain);
    holder.setBaseColor(one, '#ff0000');
    expect(revision(holder), 'setBaseColor to the same colour').toBe(plain);
    holder.forget();
    expect(revision(holder), 'a forget with nothing standing').toBe(plain);
  });

  it('the revision is the holder\'s own unless one is given', async () => {
    const { PictureRevision } = await pictureModule();
    const shared = new PictureRevision();
    const holder = new (MaterialPresentation as unknown as new (revision: unknown) => MaterialPresentation)(shared);
    expect((holder as unknown as { picture: unknown }).picture).toBe(shared);
    const before = shared.value();
    holder.setHover([holder.mesh(new THREE.BoxGeometry(), RIGID, '#ff0000')]);
    expect(shared.value()).not.toBe(before);
    expect(revision(new MaterialPresentation())).toBe(revision(new MaterialPresentation()));
  });

  // Added in review. A fault planted there, every holder sharing one
  // revision, passed the case above: two viewers on a page would then
  // each draw whenever the other changed.
  it('two holders made without a revision do not share one', () => {
    const [first, second] = [new MaterialPresentation(), new MaterialPresentation()];
    const before = revision(second);
    first.setHover([first.mesh(new THREE.BoxGeometry(), RIGID, '#ff0000')]);
    expect(revision(first)).not.toBe(before);
    expect(revision(second)).toBe(before);
  });
});

describe('U7: the camera compared by value', () => {
  const numbers = () => Array.from({ length: 32 }, (_, i) => i * 0.5 - 3);

  it('equal numbers are equal, NaN is equal to NaN, -0 differs from 0', async () => {
    const { sameReading } = await pictureModule();
    expect(sameReading(numbers(), numbers())).toBe(true);
    const nan = numbers();
    nan[5] = Number.NaN;
    expect(sameReading(nan, [...nan])).toBe(true);
    const zero = numbers();
    zero[6] = 0;
    const negative = [...zero];
    negative[6] = -0;
    expect(sameReading(zero, negative)).toBe(false);
  });

  it('any one of the 32 numbers different makes them different', async () => {
    const { sameReading } = await pictureModule();
    for (let i = 0; i < 32; i += 1) {
      const other = numbers();
      other[i] += 1e-12;
      expect(sameReading(numbers(), other), `number ${i}`).toBe(false);
    }
  });

  it('a camera reads as its world matrix, then its projection matrix, brought up to date', async () => {
    const { cameraReading, sameReading } = await pictureModule();
    const camera = new THREE.PerspectiveCamera(40, 1.5, 0.1, 1000);
    camera.position.set(10, -20, 30);
    camera.lookAt(0, 0, 0);
    const reading = cameraReading(camera);
    expect(reading).toHaveLength(32);
    expect(reading.slice(0, 16)).toEqual(camera.matrixWorld.elements);
    expect(reading.slice(16)).toEqual(camera.projectionMatrix.elements);
    expect(sameReading(reading, cameraReading(camera))).toBe(true);
    camera.position.x += 1;
    expect(sameReading(reading, cameraReading(camera))).toBe(false);
    const aspect = new THREE.PerspectiveCamera(40, Number.NaN, 0.1, 1000);
    expect(sameReading(cameraReading(aspect), cameraReading(aspect)),
           'a NaN aspect equals itself').toBe(true);
  });
});
