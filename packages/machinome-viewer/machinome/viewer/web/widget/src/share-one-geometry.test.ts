/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// OpenSpec `share-one-geometry-per-model-file`, design Decision 11: the
// REAL tree with three.js's REAL `STLLoader` and `FileLoader`, so every
// parse is a real parse making a new geometry. The network is a stubbed
// `fetch` that records each request with the file's version when it is
// sent and answers only when the test releases it, with a binary STL
// whose first facet's extent is that version and whose second facet sits
// at x = the request's serial number, so the bytes a part shows name the
// request they came from. The response's `body` is undefined, so
// `FileLoader` reads `arrayBuffer()` directly (the stream path is the
// browser tests').
//
// Every URL is absolute (Node's `Request` refuses a relative one) and
// distinct in every test: the admission module is shared by the file, a
// request left unanswered keeps its reading open, and every later load
// of its URL would join it. Every request is answered and every tree
// disposed before a test ends.
//
// The census is read through the module's namespace, so on the base,
// where it does not exist, only the assertions that read it fail.
// `admitGeometry` is wrapped, never called, to learn the URL each mesh
// asked for and when (for D4).

import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const clock = vi.hoisted(() => ({
  now: 0,
  lastMesh: undefined as object | undefined,
  asks: new WeakMap<object, { url: string; at: number }>(),
}));

vi.mock('./geometry-admission', async (importOriginal) => {
  const actual = await importOriginal<Record<string, unknown>>();
  const admit = actual.admitGeometry as (...args: unknown[]) => unknown;
  return {
    ...actual,
    // Named, so that reading it where the module has none gives undefined.
    geometryCensus: actual.geometryCensus,
    admitGeometry: (url: string, ...rest: unknown[]) => {
      // `loadMesh` reserves its mesh, then asks, synchronously.
      if (clock.lastMesh !== undefined) {
        clock.asks.set(clock.lastMesh, { url, at: ++clock.now });
        clock.lastMesh = undefined;
      }
      return admit(url, ...rest);
    },
  };
});

import * as admission from './geometry-admission';
import { GeometryBatch } from './geometry-admission';
import { EMPTY_BINDINGS } from './bindings';
import { frameBounds } from './camera';
import { MaterialPresentation } from './presentation';
import { clockedScope } from './run/pose';
import { worldBounds } from './screen';
import { assemblyPathKey, WidgetTree } from './tree';
import type { ManifestMarking, ManifestNode } from './types';

// ---------------------------------------------------------------------
// The network.

interface Sent {
  serial: number;
  url: string;
  version: number;
  at: number;
  answeredAt: number | undefined;
  answer(status?: number): void;
}

const net = {
  versions: new Map<string, number>(),
  sent: [] as Sent[],
  bySerial: new Map<number, Sent>(),
  serial: 0,
};

/** A binary STL of two facets: the first's extent is the file's version,
 * the second sits at x = the request's serial. */
function stl(version: number, serial: number): ArrayBuffer {
  const facets = [
    [[0, 0, 0], [version, 0, 0], [0, version, 0]],
    [[serial, 0, 0], [serial, 1, 0], [serial, 0, 1]],
  ];
  const buffer = new ArrayBuffer(84 + 50 * facets.length);
  const view = new DataView(buffer);
  view.setUint32(80, facets.length, true);
  facets.forEach((facet, f) => {
    const at = 84 + 50 * f;
    facet.forEach((vertex, v) => vertex.forEach((c, k) => {
      view.setFloat32(at + 12 + 12 * v + 4 * k, c, true);
    }));
  });
  return buffer;
}

function stubNetwork(): void {
  vi.stubGlobal('fetch', (input: { url: string } | string) => {
    const url = typeof input === 'string' ? input : input.url;
    const version = net.versions.get(url) ?? 1;
    net.serial += 1;
    const serial = net.serial;
    return new Promise((resolve) => {
      const sent: Sent = {
        serial, url, version, at: ++clock.now, answeredAt: undefined,
        answer: (status = 200) => {
          if (sent.answeredAt !== undefined) return;
          sent.answeredAt = ++clock.now;
          resolve({
            status, statusText: status === 200 ? 'OK' : 'Internal Server Error', url,
            body: undefined, headers: new Headers(),
            arrayBuffer: async () => stl(version, serial),
          });
        },
      };
      net.sent.push(sent);
      net.bySerial.set(serial, sent);
    });
  });
}

function resetNet(): void {
  net.sent = [];
  net.bySerial.clear();
  net.versions.clear();
}

const waiting = (): Sent[] => net.sent.filter((sent) => sent.answeredAt === undefined);
const requestsFor = (url: string): Sent[] => net.sent.filter((sent) => sent.url === url);

/** Run what has been released to quiescence: promises only, no clock. */
async function drain(): Promise<void> {
  for (let i = 0; i < 300; i += 1) await Promise.resolve();
}

/** Answer every request, and every request those answers lead to. */
async function serve(status = 200): Promise<void> {
  for (let round = 0; round < 60; round += 1) {
    await drain();
    const open = waiting();
    if (open.length === 0) return;
    open.forEach((sent) => sent.answer(status));
  }
  throw new Error('requests kept coming');
}

// ---------------------------------------------------------------------
// What the test sees of geometries and meshes.

const seen = {
  parsed: new Set<THREE.BufferGeometry>(),
  clones: new Map<THREE.BufferGeometry, THREE.BufferGeometry>(),
  liftTemps: new Set<THREE.BufferGeometry>(),
  disposals: new Map<THREE.BufferGeometry, number>(),
  normals: new Map<THREE.BufferGeometry, number>(),
  meshes: new Set<THREE.Mesh>(),
  released: new Set<THREE.Mesh>(),
  viewerOf: new Map<THREE.Mesh, MaterialPresentation>(),
  parseHook: undefined as (() => void) | undefined,
};

function resetSeen(): void {
  seen.parsed.clear(); seen.clones.clear(); seen.liftTemps.clear();
  seen.disposals.clear(); seen.normals.clear(); seen.meshes.clear();
  seen.released.clear(); seen.viewerOf.clear(); seen.parseHook = undefined;
}

function instrument(): void {
  const parse = STLLoader.prototype.parse;
  vi.spyOn(STLLoader.prototype, 'parse').mockImplementation(function (this: STLLoader, data) {
    const geometry = parse.call(this, data);
    seen.parsed.add(geometry);
    seen.parseHook?.();
    return geometry;
  });
  const clone = THREE.BufferGeometry.prototype.clone;
  vi.spyOn(THREE.BufferGeometry.prototype, 'clone').mockImplementation(function (this: THREE.BufferGeometry) {
    const copy = clone.call(this);
    seen.clones.set(copy, this);
    return copy;
  });
  const deleteAttribute = THREE.BufferGeometry.prototype.deleteAttribute;
  vi.spyOn(THREE.BufferGeometry.prototype, 'deleteAttribute').mockImplementation(
    function (this: THREE.BufferGeometry, name: string) {
      // `liftDecal` deletes its temporary clone's normals before welding.
      if (name === 'normal') seen.liftTemps.add(this);
      return deleteAttribute.call(this, name);
    });
  const dispose = THREE.BufferGeometry.prototype.dispose;
  vi.spyOn(THREE.BufferGeometry.prototype, 'dispose').mockImplementation(function (this: THREE.BufferGeometry) {
    seen.disposals.set(this, (seen.disposals.get(this) ?? 0) + 1);
    return dispose.call(this);
  });
  const normals = THREE.BufferGeometry.prototype.computeVertexNormals;
  vi.spyOn(THREE.BufferGeometry.prototype, 'computeVertexNormals').mockImplementation(
    function (this: THREE.BufferGeometry) {
      seen.normals.set(this, (seen.normals.get(this) ?? 0) + 1);
      return normals.call(this);
    });
  const mesh = MaterialPresentation.prototype.mesh;
  vi.spyOn(MaterialPresentation.prototype, 'mesh').mockImplementation(
    function (this: MaterialPresentation, ...args: Parameters<MaterialPresentation['mesh']>) {
      const made = mesh.apply(this, args);
      seen.meshes.add(made);
      seen.viewerOf.set(made, this);
      clock.lastMesh = made;
      return made;
    });
  const release = MaterialPresentation.prototype.release;
  vi.spyOn(MaterialPresentation.prototype, 'release').mockImplementation(
    function (this: MaterialPresentation, released: THREE.Mesh) {
      seen.released.add(released);
      return release.call(this, released);
    });
}

const disposals = (geometry: THREE.BufferGeometry): number => seen.disposals.get(geometry) ?? 0;
const versionOf = (geometry: THREE.BufferGeometry): number => geometry.getAttribute('position').getX(1);
const serialOf = (geometry: THREE.BufferGeometry): number => geometry.getAttribute('position').getX(3);
const urlOf = (geometry: THREE.BufferGeometry): string | undefined =>
  net.bySerial.get(serialOf(geometry))?.url;

/** The per-viewer copies a reading made: clones of a parse (or of a
 * copy), not `liftDecal`'s temporary clone. */
function copies(): Set<THREE.BufferGeometry> {
  const found = new Set<THREE.BufferGeometry>();
  let grew = true;
  while (grew) {
    grew = false;
    for (const [copy, source] of seen.clones) {
      if (found.has(copy) || seen.liftTemps.has(copy)) continue;
      if (seen.parsed.has(source) || found.has(source)) { found.add(copy); grew = true; }
    }
  }
  return found;
}
const fromFile = (geometry: THREE.BufferGeometry): boolean =>
  seen.parsed.has(geometry) || copies().has(geometry);
const parsesOf = (prefix: string): THREE.BufferGeometry[] =>
  [...seen.parsed].filter((geometry) => urlOf(geometry)?.startsWith(prefix));
const liveMeshes = (): THREE.Mesh[] => [...seen.meshes].filter((mesh) => !seen.released.has(mesh));

// ---------------------------------------------------------------------
// The census, if the module has one.

interface CensusRow { url: string; viewer: object; holders: number; value: unknown }
function census(): CensusRow[] | undefined {
  const read = (admission as unknown as Record<string, unknown>).geometryCensus;
  return typeof read === 'function' ? (read as () => CensusRow[])() : undefined;
}
const rows = (prefix: string): CensusRow[] =>
  (census() ?? []).filter((row) => row.url.startsWith(prefix));
const holdersOf = (geometry: THREE.BufferGeometry): number | undefined =>
  census()?.find((row) => row.value === geometry)?.holders;

// ---------------------------------------------------------------------
// Documents and trees.

const part = (name: string, model: string, extra: Partial<ManifestNode> = {}): ManifestNode => ({
  name, type: 'leaf', color: '#888888', operations: [], model, mtime: 1, ...extra,
});
const asm = (name: string, children: ManifestNode[]): ManifestNode => ({
  name, type: 'assembly', color: null, operations: [], children,
});
const mark = (name: string, model: string, extra: Partial<ManifestMarking> = {}): ManifestMarking => ({
  name, model, color: '#ffffff', mtime: 1, ...extra,
});
const base = (name: string): string => `http://share.test/${name}/`;

const trees: WidgetTree[] = [];
function track(tree: WidgetTree): WidgetTree {
  trees.push(tree);
  tree.loaded.catch(() => undefined);
  return tree;
}
const quiet = <T>(promise: Promise<T>): Promise<T> => { promise.catch(() => undefined); return promise; };
const ownMesh = (tree: WidgetTree): THREE.Mesh =>
  tree.group.children.find((child): child is THREE.Mesh => child instanceof THREE.Mesh)!;
function meshesUnder(tree: WidgetTree): THREE.Mesh[] {
  const found: THREE.Mesh[] = [];
  tree.group.traverse((object) => { if (object instanceof THREE.Mesh) found.push(object); });
  return found;
}

beforeEach(() => {
  stubNetwork();
  instrument();
});

afterEach(async () => {
  trees.splice(0).forEach((tree) => tree.dispose());
  await serve(500);
  await drain();
  resetNet();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  resetSeen();
});

// ---------------------------------------------------------------------
// S1 to S13.

describe('share-one-geometry-per-model-file: the real tree', () => {
  it('S1: a mount past the budget reads each file once, into one geometry that holds no normals', async () => {
    const at = base('s1');
    const files = [0, 1, 2, 3, 4, 5, 6].map((i) => `f${i}.stl`);
    const models = [...files, ...files, files[0]];
    const tree = track(new WidgetTree(asm('root', models.map((model, i) => part(`p${i}`, model))), at));
    // Four readings were sent while the tree was built; the first file's
    // second and third parts asked after its reading was sent.
    expect(net.sent.map((sent) => sent.url)).toEqual(files.slice(0, 4).map((file) => at + file));
    await serve();
    await tree.loaded;
    for (const file of files) expect(requestsFor(at + file), file).toHaveLength(1);
    // The stated reason on the base: a parse per part (15).
    expect(parsesOf(at)).toHaveLength(7);
    const shown = files.map((file) => tree.children
      .filter((_, i) => models[i] === file).map((child) => ownMesh(child).geometry));
    shown.forEach((geometries, i) => expect(new Set(geometries).size, files[i]).toBe(1));
    expect(new Set(shown.flat()).size).toBe(7);
    for (const [geometry] of shown) {
      // No normal is computed or held for a part read from a file
      // (OpenSpec `draw-rigid-parts-without-stored-normals`).
      expect(seen.normals.get(geometry)).toBeUndefined();
      expect(geometry.getAttribute('normal')).toBeUndefined();
      expect(disposals(geometry)).toBe(0);
    }
    shown.forEach((geometries) => expect(holdersOf(geometries[0])).toBe(geometries.length));
  });

  it('S2: the parts of one geometry are replaced and removed and cleaned up twice, and it is disposed once, with the last', async () => {
    const at = base('s2');
    const doc = (bMtime: number, withC: boolean) => asm('root', [
      part('a', 'f.stl'), part('b', 'f.stl', { mtime: bMtime }), ...(withC ? [part('c', 'f.stl')] : []),
    ]);
    const batch = new GeometryBatch();
    const tree = track(new WidgetTree(doc(1, true), at, null, EMPTY_BINDINGS, batch, new MaterialPresentation()));
    await serve();
    await tree.loaded;
    const shown = () => tree.children.map((child) => ownMesh(child).geometry);
    const [g] = shown();
    // The stated reason on the base: three distinct geometries.
    expect(new Set(shown()).size).toBe(1);
    expect(holdersOf(g)).toBe(3);

    const removed = quiet(tree.reconcile(doc(1, false), at));
    await serve();
    await removed;
    expect(shown()).toEqual([g, g]);
    expect(disposals(g)).toBe(0);
    expect(holdersOf(g)).toBe(2);

    const moved = quiet(tree.reconcile(doc(2, false), at));
    await serve();
    await moved;
    const [a, b] = shown();
    expect(a).toBe(g);
    expect(b).not.toBe(g);
    expect([disposals(a), disposals(b)]).toEqual([0, 0]);
    expect([holdersOf(a), holdersOf(b)]).toEqual([1, 1]);

    // The owners' cleanups run inside each `dispose()` before its
    // traversal, then the traversal, then a second `dispose()` and the
    // mount batch's own cancellation: every mesh is cleaned up more than
    // once.
    tree.dispose();
    tree.dispose();
    batch.cancel();
    await drain();
    expect([disposals(a), disposals(b)]).toEqual([1, 1]);
    expect(rows(at)).toEqual([]);
  });

  it('S3: a part and its marking on one file, and two markings on one file, read each file once', async () => {
    const at = base('s3');
    const tree = track(new WidgetTree(asm('root', [
      part('p', 'm.stl', { markings: [mark('mark', 'm.stl')] }),
      part('q', 'q.stl', { markings: [mark('x', 'k.stl', { color: '#ff0000' }), mark('y', 'k.stl', { color: '#00ff00' })] }),
    ]), at));
    await serve();
    await tree.loaded;
    expect(requestsFor(`${at}m.stl`)).toHaveLength(1);
    expect(requestsFor(`${at}k.stl`)).toHaveLength(1);
    // The stated reason on the base: two parses of each.
    expect(parsesOf(`${at}m.stl`)).toHaveLength(1);
    expect(parsesOf(`${at}k.stl`)).toHaveLength(1);
    const [p, q] = tree.children;
    const partGeometry = ownMesh(p).geometry;
    const decals = [...p.markings, ...q.markings].map((record) => record.mesh.geometry);
    expect(new Set([partGeometry, ...decals]).size).toBe(4);
    for (const decal of decals) {
      expect(fromFile(decal)).toBe(false);
      expect(decal.index).not.toBeNull();
      expect(disposals(decal)).toBe(0);
    }
    // Lifted off the surface it was read from, along the facet's normal.
    expect(partGeometry.getAttribute('position').getZ(0)).toBe(0);
    expect(decals[0].getAttribute('position').getZ(0)).toBeCloseTo(0.15, 6);
    expect(disposals(partGeometry)).toBe(0);
    expect(holdersOf(partGeometry)).toBe(1);
    expect(rows(`${at}k.stl`)).toEqual([]);
    const [k] = parsesOf(`${at}k.stl`);
    expect(disposals(k)).toBe(1);
  });

  it('S4: two artifact notices for one path while the first request is held: one reading, held by the parts that show it', async () => {
    const at = base('s4');
    const tree = track(new WidgetTree(asm('root', [
      part('a', 'f.stl'), part('b', 'f.stl'), part('c', 'g.stl'),
    ]), at));
    await serve();
    await tree.loaded;
    const mounted = ownMesh(tree.children[0]).geometry;
    const before = net.sent.length;
    const parsedBefore = new Set(seen.parsed);
    net.versions.set(`${at}f.stl`, 2);
    const first = quiet(tree.artifactChanged('f.stl', at));
    await drain();
    net.versions.set(`${at}f.stl`, 3);
    const second = quiet(tree.artifactChanged('f.stl', at));
    await drain();
    expect(net.sent.slice(before).map((sent) => [sent.url, sent.version])).toEqual([[`${at}f.stl`, 2]]);
    await serve();
    await Promise.all([first, second]);
    const shown = tree.children.slice(0, 2).map((child) => ownMesh(child).geometry);
    // The bytes the parts end on are the first request's, as on the base.
    expect(shown.map(versionOf)).toEqual([2, 2]);
    // The stated reason on the base: a parse per part of each batch (4).
    expect([...seen.parsed].filter((g) => !parsedBefore.has(g))).toHaveLength(1);
    expect(shown[0]).toBe(shown[1]);
    expect(disposals(shown[0])).toBe(0);
    expect(disposals(mounted)).toBe(1);
    expect(rows(`${at}f.stl`).map((row) => [row.value, row.holders])).toEqual([[shown[0], 2]]);
  });

  it.each(['a', 'b'])('S5: a republish adds a part naming a path an artifact update is reading; removing %s leaves the other drawn', async (removed) => {
    const at = base(`s5-${removed}`);
    const tree = track(new WidgetTree(asm('root', [part('a', 'f.stl')]), at));
    await serve();
    await tree.loaded;
    const before = net.sent.length;
    const parsedBefore = new Set(seen.parsed);
    net.versions.set(`${at}f.stl`, 2);
    const changed = quiet(tree.artifactChanged('f.stl', at));
    await drain();
    const reconciled = quiet(tree.reconcile(asm('root', [part('a', 'f.stl'), part('b', 'f.stl')]), at));
    await drain();
    expect(net.sent.slice(before).map((sent) => sent.url)).toEqual([`${at}f.stl`]);
    await serve();
    await Promise.all([changed, reconciled]);
    // The stated reason on the base: a parse per part (2).
    expect([...seen.parsed].filter((g) => !parsedBefore.has(g))).toHaveLength(1);
    const [a, b] = tree.children.map((child) => ownMesh(child).geometry);
    expect(a).toBe(b);
    expect(holdersOf(a)).toBe(2);
    const kept = removed === 'a' ? 'b' : 'a';
    const removal = quiet(tree.reconcile(asm('root', [part(kept, 'f.stl')]), at));
    await serve();
    await removal;
    expect(tree.children.map((child) => child.name)).toEqual([kept]);
    expect(ownMesh(tree.children[0]).geometry).toBe(a);
    expect(disposals(a)).toBe(0);
    expect(holdersOf(a)).toBe(1);
  });

  it('S6: a new tree built while a request for one of its files is held joins it and reads every other file again', async () => {
    const at = base('s6');
    const doc = asm('root', [part('a', 'f.stl'), part('b', 'f.stl'), part('c', 'g.stl'), part('d', 'g.stl')]);
    const viewer = new MaterialPresentation();
    const old = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, undefined, viewer));
    await serve();
    await old.loaded;
    const oldG = ownMesh(old.children[2]).geometry;
    const parsedBefore = new Set(seen.parsed);
    net.versions.set(`${at}f.stl`, 2);
    const changed = quiet(old.artifactChanged('f.stl', at));
    await drain();
    const before = net.sent.length;
    const next = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, undefined, viewer));
    await drain();
    expect(net.sent.slice(before).map((sent) => sent.url)).toEqual([`${at}g.stl`]);
    await serve();
    await changed;
    await next.loaded;
    // The stated reason on the base: a parse per part (6).
    expect([...seen.parsed].filter((g) => !parsedBefore.has(g))).toHaveLength(2);
    const [nf, nb, ng, nd] = next.children.map((child) => ownMesh(child).geometry);
    expect(nb).toBe(nf);
    expect(nd).toBe(ng);
    expect(ng).not.toBe(oldG);
    expect(nf).toBe(ownMesh(old.children[0]).geometry);
    old.dispose();
    await drain();
    for (const mesh of meshesUnder(next)) expect(disposals(mesh.geometry)).toBe(0);
    expect(disposals(oldG)).toBe(1);
    expect(rows(at).map((row) => [row.url, row.value, row.holders])
      .sort((x, y) => String(x[0]).localeCompare(String(y[0])))).toEqual(
      [[`${at}f.stl`, nf, 2], [`${at}g.stl`, ng, 2]]);
  });

  it('S7: one republish\'s later load joins its own reading in flight', async () => {
    const at = base('s7');
    const tree = track(new WidgetTree(asm('root', [part('a', 'f.stl'), asm('s', [part('x', 'g.stl')])]), at));
    await serve();
    await tree.loaded;
    const before = net.sent.length;
    const parsedBefore = new Set(seen.parsed);
    const reconciled = quiet(tree.reconcile(asm('root', [
      part('a', 'f.stl', { mtime: 2 }), asm('s', [part('x', 'g.stl'), part('y', 'f.stl')]),
    ]), at));
    await drain();
    expect(net.sent.slice(before).map((sent) => sent.url)).toEqual([`${at}f.stl`]);
    await serve();
    await reconciled;
    expect(net.sent.slice(before)).toHaveLength(1);
    // The stated reason on the base: two parses of the one response.
    expect([...seen.parsed].filter((g) => !parsedBefore.has(g))).toHaveLength(1);
    const a = ownMesh(tree.children[0]).geometry;
    const y = ownMesh(tree.children[1].children[1]).geometry;
    expect(y).toBe(a);
    expect(holdersOf(a)).toBe(2);
  });

  it('S8: two viewers in one batch read once, hold one geometry each, and free only their own', async () => {
    const at = base('s8');
    const doc = asm('root', [part('a', 'f.stl'), part('b', 'f.stl')]);
    const batch = new GeometryBatch();
    const one = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, batch, new MaterialPresentation()));
    const two = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, batch, new MaterialPresentation()));
    await serve();
    await Promise.all([one.loaded, two.loaded]);
    expect(requestsFor(`${at}f.stl`)).toHaveLength(1);
    // The stated reason on the base: four parses.
    expect(parsesOf(at)).toHaveLength(1);
    const g1 = one.children.map((child) => ownMesh(child).geometry);
    const g2 = two.children.map((child) => ownMesh(child).geometry);
    expect(g1[0]).toBe(g1[1]);
    expect(g2[0]).toBe(g2[1]);
    expect(g1[0]).not.toBe(g2[0]);
    expect([...copies()]).toHaveLength(1);
    expect(seen.parsed.has(g1[0]) || seen.parsed.has(g2[0])).toBe(true);
    one.dispose();
    await drain();
    expect([disposals(g1[0]), disposals(g2[0])]).toEqual([1, 0]);
    expect(rows(at).map((row) => [row.value, row.holders])).toEqual([[g2[0], 2]]);
    two.dispose();
    await drain();
    expect([disposals(g1[0]), disposals(g2[0])]).toEqual([1, 1]);
    expect(rows(at)).toEqual([]);
  });

  it('S9: a tree disposed while every part waits on one request: its parse is freed on arrival, never attached', async () => {
    const at = base('s9');
    const tree = track(new WidgetTree(asm('root', [part('a', 'f.stl'), part('b', 'f.stl'), part('c', 'f.stl')]), at));
    await drain();
    expect(requestsFor(`${at}f.stl`)).toHaveLength(1);
    const loaded = Promise.allSettled([tree.loaded]);
    tree.dispose();
    await serve();
    await loaded;
    const parsed = parsesOf(at);
    // The stated reason on the base: a parse per part (3).
    expect(parsed).toHaveLength(1);
    expect(disposals(parsed[0])).toBe(1);
    expect(meshesUnder(tree)).toEqual([]);
    expect(liveMeshes().filter((mesh) => mesh.geometry === parsed[0])).toEqual([]);
    expect(census()).toBeDefined();
    expect(rows(at)).toEqual([]);
  });

  it.each([0, 1, 2, 3, 4, 5, 6])('S10: of two trees of one viewer sharing a reading, the first disposed %i microtasks after the response', async (steps) => {
    const at = base(`s10-${steps}`);
    const viewer = new MaterialPresentation();
    const doc = asm('root', [part('a', 'f.stl')]);
    // Built together, each with a batch of its own as `replaceTree` builds
    // a tree: one batch would let the first tree's failure cancel the
    // second's owner, on the base as here.
    const one = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, new GeometryBatch(), viewer));
    const two = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, new GeometryBatch(), viewer));
    await drain();
    expect(requestsFor(`${at}f.stl`)).toHaveLength(1);
    // "After the response": counted from the parse of its bytes.
    let parsed!: () => void;
    const arrived = new Promise<void>((resolve) => { parsed = resolve; });
    seen.parseHook = () => parsed();
    waiting()[0].answer();
    await arrived;
    for (let i = 0; i < steps; i += 1) await Promise.resolve();
    one.dispose();
    await Promise.allSettled([one.loaded]);
    await two.loaded;
    await drain();
    // The stated reason on the base: two parses, distinct geometries.
    expect(parsesOf(at)).toHaveLength(1);
    const shown = ownMesh(two.children[0]).geometry;
    expect(disposals(shown)).toBe(0);
    expect(rows(at).map((row) => [row.value, row.holders])).toEqual([[shown, 1]]);
  });

  it('S11: a shared file answered 500 at a mount and in a republish fails every load of it and keeps the last good model', async () => {
    const at = base('s11');
    // At a mount.
    const failed = track(new WidgetTree(asm('root', [part('a', 'bad.stl'), part('b', 'bad.stl')]), at));
    const children = failed.children.map((child) => Promise.allSettled([child.loaded]));
    await drain();
    expect(requestsFor(`${at}bad.stl`)).toHaveLength(1);
    waiting()[0].answer(500);
    await drain();
    const outcomes = (await Promise.all(children)).map(([row]) => row);
    expect(outcomes.map((row) => row.status)).toEqual(['rejected', 'rejected']);
    const reasons = outcomes.map((row) => (row as PromiseRejectedResult).reason as Error);
    expect(reasons[0].constructor.name).toBe('HttpError');
    expect(reasons[0].message).toContain('responded with 500');
    expect(reasons[1]).toBe(reasons[0]);
    await expect(failed.loaded).rejects.toBe(reasons[0]);
    expect(meshesUnder(failed)).toEqual([]);
    expect(parsesOf(`${at}bad.stl`)).toEqual([]);
    expect(rows(`${at}bad.stl`)).toEqual([]);

    // In a republish.
    const tree = track(new WidgetTree(asm('root', [part('a', 'f.stl'), part('b', 'f.stl')]), at));
    await serve();
    await tree.loaded;
    const meshes = tree.children.map(ownMesh);
    const standing = meshes.map((mesh) => mesh.geometry);
    const republish = quiet(tree.reconcile(asm('root', [
      part('a', 'f.stl', { mtime: 2 }), part('b', 'f.stl', { mtime: 2 }),
    ]), at));
    await drain();
    expect(waiting().map((sent) => sent.url)).toEqual([`${at}f.stl`]);
    waiting()[0].answer(500);
    const error = await republish.then(() => undefined, (reason) => reason as Error);
    expect(error?.constructor.name).toBe('HttpError');
    await drain();
    expect(tree.children.map(ownMesh)).toEqual(meshes);
    expect(tree.children.map((child) => ownMesh(child).geometry)).toEqual(standing);
    standing.forEach((geometry) => expect(disposals(geometry)).toBe(0));
    for (const mesh of liveMeshes()) expect(meshes.includes(mesh), 'a reserved mesh survived').toBe(true);
    if (census() !== undefined) {
      expect(rows(`${at}f.stl`).map((row) => [row.value, row.holders])).toEqual([[standing[0], 2]]);
    }
  });

  it('S12: nothing writes a shared geometry: every operation that reads one leaves its versions and arrays as the mount left them', async () => {
    const at = base('s12');
    const viewer = new MaterialPresentation();
    const doc = (overrides: { bColor?: string; aX?: string; cMarks?: ManifestMarking[] } = {}) => asm('root', [
      part('a', 'f.stl', { operations: [['t', [overrides.aX ?? '0', '0', '0']]] }),
      part('b', 'f.stl', { color: overrides.bColor ?? '#888888', markings: [mark('m', 'f.stl')] }),
      part('c', 'g.stl', { markings: overrides.cMarks }),
    ]);
    const tree = track(new WidgetTree(doc(), at, null, EMPTY_BINDINGS, undefined, viewer));
    await serve();
    await tree.loaded;
    const scope = clockedScope({}, 0, EMPTY_BINDINGS);
    tree.update(scope);
    const mountedShown = tree.children.slice(0, 2).map((child) => ownMesh(child).geometry);
    const geometries = [...new Set(mountedShown)];

    // What three.js's own parse of the same bytes and the reading's one
    // preparation, the removal of its normals (OpenSpec
    // `draw-rigid-parts-without-stored-normals`), give: the mount, its
    // decal lift included, wrote nothing else.
    const reading = (geometry: THREE.BufferGeometry) => Object.keys(geometry.attributes).sort().map((name) => {
      const attribute = geometry.getAttribute(name) as THREE.BufferAttribute;
      return [name, attribute.version, Array.from(attribute.array as Float32Array)];
    });
    for (const geometry of geometries) {
      const fresh = new STLLoader().parse(stl(versionOf(geometry), serialOf(geometry)));
      seen.parsed.delete(fresh);
      fresh.deleteAttribute('normal');
      expect(reading(geometry)).toEqual(reading(fresh));
    }
    const after = geometries.map(reading);

    const meshes = () => tree.children.map(ownMesh);
    const [ma, mb, mc] = meshes();
    for (const mode of ['keep', 'dim', 'ghost'] as const) {
      viewer.setHighlight({ lit: [ma], others: [mb, mc], color: '#ffb000', mode });
    }
    viewer.setHover([mb]);
    viewer.setHover([]);
    viewer.setHighlight(null);
    const recolored = quiet(tree.reconcile(doc({ bColor: '#123456' }), at, null, EMPTY_BINDINGS, () => scope));
    await serve();
    await recolored;
    tree.applyVisibility(null, new Set([assemblyPathKey(['b'])]));
    tree.applyVisibility(null, new Set());
    tree.applyVisibility(['a'], new Set());
    tree.applyVisibility(null, new Set());
    tree.group.updateMatrixWorld(true);
    expect(worldBounds(meshes()).isEmpty()).toBe(false);
    // `visibleBounds` is the viewer's own and private; this is what it
    // does to a geometry, then the camera fit it feeds.
    const visible = new THREE.Box3();
    tree.group.traverse((object) => {
      if (object instanceof THREE.Mesh && object.visible) {
        if (object.geometry.boundingBox === null) object.geometry.computeBoundingBox();
        visible.union(object.geometry.boundingBox!.clone().applyMatrix4(object.matrixWorld));
      }
    });
    expect(frameBounds(visible, 50)).not.toBeNull();
    const ray = new THREE.Raycaster(new THREE.Vector3(0.2, 0.2, 10), new THREE.Vector3(0, 0, -1));
    expect(ray.intersectObject(tree.group, true).length).toBeGreaterThan(0);
    const marked = quiet(tree.reconcile(doc({ bColor: '#123456', cMarks: [mark('n', 'f.stl')] }), at,
      null, EMPTY_BINDINGS, () => scope));
    await serve();
    await marked;
    const changed = quiet(tree.artifactChanged('g.stl', at));
    await serve();
    await changed;
    const posed = quiet(tree.reconcile(doc({ bColor: '#123456', aX: '5', cMarks: [mark('n', 'f.stl')] }), at,
      null, EMPTY_BINDINGS, () => scope));
    await serve();
    await posed;
    tree.group.updateMatrixWorld(true);
    ray.intersectObject(tree.group, true);
    expect(meshes().slice(0, 2).map((mesh) => mesh.geometry)).toEqual(mountedShown);
    expect(geometries.map(reading)).toEqual(after);
  });

  it('S13: once every tree is disposed and every request answered, nothing is held and every geometry read was freed once', async () => {
    const at = base('s13');
    const doc = asm('root', [
      part('a', 'f.stl', { markings: [mark('m', 'f.stl')] }), part('b', 'f.stl'),
      asm('s', [part('c', 'g.stl'), part('d', 'h.stl')]),
    ]);
    const batch = new GeometryBatch();
    const one = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, batch, new MaterialPresentation()));
    const two = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, batch, new MaterialPresentation()));
    await serve();
    await Promise.all([one.loaded, two.loaded]);
    net.versions.set(`${at}f.stl`, 2);
    const changed = quiet(one.artifactChanged('f.stl', at));
    const republished = quiet(two.reconcile(asm('root', [
      part('a', 'f.stl', { markings: [mark('m', 'f.stl', { mtime: 2 })] }), part('e', 'g.stl'),
      asm('s', [part('c', 'g.stl', { mtime: 2 })]),
    ]), at));
    await serve();
    await Promise.all([changed, republished]);
    const failing = quiet(one.reconcile(asm('root', [part('a', 'h.stl'), part('b', 'f.stl')]), at));
    await drain();
    waiting().forEach((sent) => sent.answer(500));
    await failing.catch(() => undefined);
    const third = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, undefined, new MaterialPresentation()));
    await drain();
    third.dispose();
    one.dispose();
    two.dispose();
    await serve();
    await drain();
    const read = [...seen.parsed, ...copies()].filter((geometry) => urlOf(geometry)?.startsWith(at));
    expect(read.length).toBeGreaterThan(0);
    expect(read.map(disposals).filter((count) => count !== 1)).toEqual([]);
    expect(liveMeshes().filter((mesh) => fromFile(mesh.geometry))).toEqual([]);
    expect(census()).toBeDefined();
    expect(rows(at)).toEqual([]);
  });
});

// ---------------------------------------------------------------------
// R1 to R4, added in review (evidence.md, "The reviewer's record").

interface Counted { id: number; disposed: number }
interface CountedShare { readonly value: Counted | undefined; release(): void }
/** A reading of a counted value, asked of the module itself. */
function countedKind(): { kind: unknown; made: Counted[]; reads: () => number } {
  const made: Counted[] = [];
  let reads = 0;
  const make = (): Counted => { const value = { id: made.length, disposed: 0 }; made.push(value); return value; };
  const kind = {
    read: async () => { reads += 1; return make(); },
    copy: () => make(),
    dispose: (value: Counted) => { value.disposed += 1; },
  };
  return { kind, made, reads: () => reads };
}
const admit = (url: string, viewer: object, kind: unknown): Promise<CountedShare> =>
  (admission.admitGeometry as unknown as (...args: unknown[]) => Promise<CountedShare>)(
    url, new admission.GeometryOwner(), viewer, kind);

describe('R1 to R4: added in review', () => {
  it('R1: a share let go twice counts once, and a freed geometry is out of its shares\' reach', async () => {
    const { kind, made } = countedKind();
    const viewer = {};
    const url = `${base('r1')}x`;
    const [first, second] = await Promise.all([admit(url, viewer, kind), admit(url, viewer, kind)]);
    await drain();
    expect(first.value).toBe(made[0]);
    expect(second.value).toBe(made[0]);
    first.release();
    first.release();
    expect(rows(url).map((row) => row.holders), 'the second release counted').toEqual([1]);
    expect(made[0].disposed).toBe(0);
    expect(second.value).toBe(made[0]);
    second.release();
    expect(made[0].disposed).toBe(1);
    expect(rows(url)).toEqual([]);
    expect([first.value, second.value], 'a freed geometry is still reachable through its shares')
      .toEqual([undefined, undefined]);
    second.release();
    first.release();
    expect(made.map((value) => value.disposed)).toEqual([1]);
  });

  it('R2: a reading is closed when its request settles: a load asking the moment a share arrives reads again', async () => {
    const { kind, made, reads } = countedKind();
    const viewer = {};
    const url = `${base('r2')}x`;
    let later: Promise<CountedShare> | undefined;
    const first = await admit(url, viewer, kind).then((share) => {
      later = admit(url, viewer, kind);
      return share;
    });
    const second = await later!;
    expect(reads(), 'the load joined a reading whose request had settled').toBe(2);
    expect(second.value).not.toBe(first.value);
    first.release();
    second.release();
    await drain();
    expect(made.map((value) => value.disposed)).toEqual([1, 1]);
    expect(rows(url)).toEqual([]);
  });

  it('R3: a second viewer mounting past the budget joins the first viewer\'s queued readings and holds copies of its own', async () => {
    const at = base('r3');
    const files = ['f0.stl', 'f1.stl', 'f2.stl', 'f3.stl', 'f4.stl', 'f5.stl'];
    const doc = asm('root', files.map((file, index) => part(`p${index}`, file)));
    const one = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, new GeometryBatch(), new MaterialPresentation()));
    const two = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, new GeometryBatch(), new MaterialPresentation()));
    await serve();
    await Promise.all([one.loaded, two.loaded]);
    for (const file of files) expect(requestsFor(`${at}${file}`), file).toHaveLength(1);
    expect(parsesOf(at), 'a file was parsed for each viewer').toHaveLength(files.length);
    const shown = (tree: WidgetTree) => tree.children.map((child) => ownMesh(child).geometry);
    const [g1, g2] = [shown(one), shown(two)];
    g1.forEach((geometry, index) => {
      expect(geometry, files[index]).not.toBe(g2[index]);
      expect(seen.parsed.has(geometry) !== seen.parsed.has(g2[index]), `${files[index]}: one parse and one copy`).toBe(true);
      expect(versionOf(geometry)).toBe(versionOf(g2[index]));
    });
    one.dispose();
    await drain();
    expect(g1.map(disposals)).toEqual(files.map(() => 1));
    expect(g2.map(disposals)).toEqual(files.map(() => 0));
    two.dispose();
    await drain();
    expect(rows(at)).toEqual([]);
  });

  const STEPS = Array.from({ length: 31 }, (_, index) => index);
  it.each(STEPS)('R4: a marking whose tree is disposed %i microtasks after its file arrives rejects with the cancellation and leaves nothing', async (steps) => {
    const at = base(`r4-${steps}`);
    const doc = { ...asm('root', []), markings: [mark('m', 'g.stl')] } as ManifestNode;
    const tree = track(new WidgetTree(doc, at));
    await drain();
    const settled = Promise.allSettled([tree.loaded]);
    waiting().forEach((sent) => sent.answer());
    for (let i = 0; i < steps; i += 1) await Promise.resolve();
    tree.dispose();
    await serve();
    await drain();
    const [row] = await settled;
    if (row.status === 'rejected') {
      expect((row.reason as Error).message).toBe('Geometry load owner was disposed');
    }
    expect(rows(at)).toEqual([]);
    expect(parsesOf(at).map(disposals)).toEqual([1]);
  });
});

// ---------------------------------------------------------------------
// G1, generated, on trees.

function random(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6D2B79F5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

interface Held {
  tree: WidgetTree;
  doc: ManifestNode;
  viewer: MaterialPresentation;
  state: 'pending' | 'live' | 'disposed';
  busy: boolean;
}

const FILES = ['f0.stl', 'f1.stl', 'f2.stl'];

function weight(doc: ManifestNode): number {
  return (doc.model ? 1 : 0) + (doc.markings ?? []).length
    + (doc.children ?? []).reduce((sum, child) => sum + weight(child), 0);
}

function leaves(doc: ManifestNode): ManifestNode[] {
  return doc.model ? [doc] : (doc.children ?? []).flatMap(leaves);
}

function generatedDoc(next: () => number, pick: <T>(items: readonly T[]) => T, names: () => string): ManifestNode {
  const top: ManifestNode[] = [];
  const sub: ManifestNode[] = [];
  let budget = 1 + Math.floor(next() * 8);
  while (budget > 0) {
    const markings = budget > 1 && next() < 0.3
      ? Array.from({ length: Math.min(budget - 1, 1 + Math.floor(next() * 2)) },
                   () => mark(names(), pick(FILES)))
      : undefined;
    budget -= 1 + (markings?.length ?? 0);
    (next() < 0.3 ? sub : top).push(part(names(), pick(FILES), markings ? { markings } : {}));
  }
  return asm('root', sub.length > 0 ? [...top, asm('sub', sub)] : top);
}

function mutated(doc: ManifestNode, next: () => number, pick: <T>(items: readonly T[]) => T,
                 names: () => string): ManifestNode {
  const copy = JSON.parse(JSON.stringify(doc)) as ManifestNode;
  const parts = leaves(copy);
  const markings = parts.flatMap((p) => (p.markings ?? []).map((m) => ({ p, m })));
  const choice = next();
  if (choice < 0.15 && weight(copy) < 8) {
    const holder = (copy.children ?? []).find((child) => child.name === 'sub' && !child.model);
    (holder && next() < 0.5 ? holder : copy).children!.push(part(names(), pick(FILES)));
  } else if (choice < 0.3 && parts.length > 1) {
    const victim = pick(parts);
    const strip = (node: ManifestNode) => {
      node.children = (node.children ?? []).filter((child) => child !== victim);
      node.children.forEach(strip);
    };
    strip(copy);
  } else if (choice < 0.4 && weight(copy) < 8) {
    const p = pick(parts);
    p.markings = [...(p.markings ?? []), mark(names(), pick(FILES))];
  } else if (choice < 0.5 && markings.length > 0) {
    const { p, m } = pick(markings);
    p.markings = p.markings!.filter((one) => one !== m);
  } else if (choice < 0.7) {
    if (markings.length > 0 && next() < 0.4) {
      const { m } = pick(markings);
      m.mtime = (m.mtime ?? 0) + 1;
    } else {
      const p = pick(parts);
      p.mtime = (p.mtime ?? 0) + 1;
    }
  } else if (markings.length > 0 && next() < 0.4) {
    const { m } = pick(markings);
    m.model = pick(FILES.filter((file) => file !== m.model));
  } else {
    const p = pick(parts);
    p.model = pick(FILES.filter((file) => file !== p.model));
  }
  return copy;
}

/** D1 to D4 at quiescence, over what is read from files under `at`. */
function detect(label: string, at: string, groups: THREE.Object3D[]): void {
  const live = liveMeshes();
  const copied = copies();
  const isRead = (geometry: THREE.BufferGeometry) => seen.parsed.has(geometry) || copied.has(geometry);
  // D1: every mesh under a live or pending tree's group is live and shows
  // a geometry not disposed, and so does every live mesh (a prepared
  // replacement, the placeholder of a load still waiting).
  for (const group of groups) {
    group.traverse((object) => {
      if (!(object instanceof THREE.Mesh)) return;
      expect(seen.released.has(object), `${label}: D1 a released mesh is in a live tree`).toBe(false);
      expect(disposals(object.geometry), `${label}: D1 a mesh in a live tree shows a disposed geometry`).toBe(0);
    });
  }
  for (const mesh of live) {
    expect(disposals(mesh.geometry), `${label}: D1 a live mesh shows a disposed geometry`).toBe(0);
  }
  for (const [geometry, count] of seen.disposals) {
    expect(count, `${label}: geometry ${geometry.id} disposed more than once`).toBeLessThanOrEqual(1);
  }
  // D2: the geometries read from files and not disposed are exactly those
  // live meshes show.
  const alive = [...seen.parsed, ...copied].filter((geometry) => disposals(geometry) === 0)
    .map((geometry) => geometry.id).sort((x, y) => x - y);
  const shown = [...new Set(live.map((mesh) => mesh.geometry).filter(isRead))]
    .map((geometry) => geometry.id).sort((x, y) => x - y);
  expect(alive, `${label}: D2`).toEqual(shown);
  // D3: each holding's count is the live meshes that show its geometry.
  const table = census();
  expect(table, `${label}: D3 the census`).toBeDefined();
  const counted = new Map<number, number>();
  for (const mesh of live) {
    if (isRead(mesh.geometry)) counted.set(mesh.geometry.id, (counted.get(mesh.geometry.id) ?? 0) + 1);
  }
  const mine = table!.filter((row) => row.url.startsWith(at));
  const listed = new Map(mine.map((row) => [(row.value as THREE.BufferGeometry).id, row.holders]));
  expect(listed.size, `${label}: D3 one holding a geometry`).toBe(mine.length);
  const sorted = (map: Map<number, number>) => [...map].sort((x, y) => x[0] - y[0]);
  expect(sorted(listed), `${label}: D3`).toEqual(sorted(counted));
  // D4: a live mesh shows bytes of the file it asked for, from a reading
  // still open when it asked.
  for (const mesh of live) {
    if (!isRead(mesh.geometry)) continue;
    const asked = clock.asks.get(mesh);
    const request = net.bySerial.get(serialOf(mesh.geometry));
    expect(asked, `${label}: D4 a mesh that never asked`).toBeDefined();
    expect(request?.url, `${label}: D4 another file's geometry`).toBe(asked!.url);
    expect(request!.answeredAt! > asked!.at, `${label}: D4 a reading closed before it asked`).toBe(true);
  }
}

async function generatedSequence(seed: number, steps: number,
                                 tally: Map<string, number>): Promise<void> {
  const next = random(seed);
  const pick = <T>(items: readonly T[]): T => items[Math.floor(next() * items.length)];
  let named = 0;
  const names = () => `n${named++}`;
  const at = base(`g1-${seed}`);
  const viewers = [new MaterialPresentation(), new MaterialPresentation()];
  const held: Held[] = [];
  const mount = (doc: ManifestNode, viewer: MaterialPresentation, replaces?: Held) => {
    const tree = new WidgetTree(doc, at, null, EMPTY_BINDINGS, undefined, viewer);
    trees.push(tree);
    const entry: Held = { tree, doc, viewer, state: 'pending', busy: false };
    held.push(entry);
    tree.loaded.then(() => {
      if (entry.state === 'disposed') return;
      entry.state = 'live';
      // As `replaceTree`: the old tree goes once the new one is loaded.
      if (replaces !== undefined && replaces.state !== 'disposed') {
        replaces.state = 'disposed';
        replaces.tree.dispose();
      }
    }, () => {
      entry.state = 'disposed';
      tree.dispose();
    });
  };
  const standing = () => held.filter((entry) => entry.state !== 'disposed');
  const live = () => held.filter((entry) => entry.state === 'live');
  for (let step = 0; step < steps; step += 1) {
    const roll = next();
    let done = 'nothing';
    if ((roll < 0.12 || standing().length === 0) && standing().length < 4) {
      mount(generatedDoc(next, pick, names), pick(viewers));
      done = 'mount';
    } else if (roll < 0.2 && live().length > 0) {
      const old = pick(live());
      mount(old.doc, old.viewer, old);
      done = 'reload';
    } else if (roll < 0.38 && live().some((entry) => !entry.busy)) {
      const entry = pick(live().filter((one) => !one.busy));
      const doc = mutated(entry.doc, next, pick, names);
      entry.busy = true;
      entry.tree.reconcile(doc, at).then(() => { entry.doc = doc; }, () => undefined)
        .finally(() => { entry.busy = false; });
      done = 'republish';
    } else if (roll < 0.48 && live().length > 0) {
      quiet(pick(live()).tree.artifactChanged(pick(FILES), at));
      done = 'artifact';
    } else if (roll < 0.56) {
      const file = at + pick(FILES);
      net.versions.set(file, (net.versions.get(file) ?? 1) + 1);
      done = 'rewrite';
    } else if (roll < 0.9 && waiting().length > 0) {
      const sent = pick(waiting());
      const status = next() < 0.12 ? 500 : 200;
      sent.answer(status);
      done = `answer ${status}`;
    } else if (standing().length > 0) {
      const entry = pick(standing());
      entry.state = 'disposed';
      entry.tree.dispose();
      done = 'dispose';
    }
    await drain();
    tally.set(done, (tally.get(done) ?? 0) + 1);
    detect(`seed ${seed} step ${step} (${done})`, at, standing().map((entry) => entry.tree.group));
  }
  // D5: once every tree is disposed and every request answered.
  held.forEach((entry) => { entry.state = 'disposed'; entry.tree.dispose(); });
  await serve();
  await drain();
  const read = [...seen.parsed, ...copies()].filter((geometry) => urlOf(geometry)?.startsWith(at));
  tally.set('requests', (tally.get('requests') ?? 0) + net.sent.length);
  tally.set('parses', (tally.get('parses') ?? 0) + seen.parsed.size);
  tally.set('copies', (tally.get('copies') ?? 0) + copies().size);
  tally.set('meshes', (tally.get('meshes') ?? 0) + seen.meshes.size);
  expect(read.map(disposals).filter((count) => count !== 1), `seed ${seed}: D5 freed once`).toEqual([]);
  expect(census(), `seed ${seed}: D5 the census`).toBeDefined();
  expect(rows(at), `seed ${seed}: D5 the census is empty`).toEqual([]);
}

describe('G1: generated sequences on trees', () => {
  it('300 seeded sequences of 40 steps keep D1 to D5', async () => {
    const started = Date.now();
    const tally = new Map<string, number>();
    // G1_FROM and G1_TO replay a printed seed alone.
    for (let seed = Number(process.env.G1_FROM ?? 1); seed <= Number(process.env.G1_TO ?? 300); seed += 1) {
      try {
        await generatedSequence(seed, 40, tally);
      } catch (error) {
        console.error(`G1 failed at seed ${seed}`);
        throw error;
      } finally {
        trees.splice(0).forEach((tree) => tree.dispose());
        await serve();
        resetNet();
        resetSeen();
      }
    }
    console.info(`G1: 300 sequences of 40 steps in ${Date.now() - started} ms`,
                 JSON.stringify(Object.fromEntries([...tally].sort())));
  }, 600_000);
});
