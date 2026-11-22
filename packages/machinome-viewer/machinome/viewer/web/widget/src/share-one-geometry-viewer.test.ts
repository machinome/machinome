/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// OpenSpec `share-one-geometry-per-model-file`, design Decision 11: the
// REAL `mount()` in jsdom, on a copy of `draw-on-change.test.ts`'s bench
// -- three.js's `WebGLRenderer` replaced by a counting renderer whose
// animation loop is kept and driven here, a stubbed `ResizeObserver` --
// with its STL loader mock removed: three.js's own `STLLoader` and
// `FileLoader` read every model file, over a stubbed `fetch` that answers
// documents at once and holds every model request until the test
// releases it. Each renderer keeps its own loop and the scene it was
// given, and each `Scene` the viewer makes is recorded, so that two
// mounts can be driven and read apart.
//
// The model files are binary STLs of two facets: the first's extent is
// the file's version when the request was sent, the second sits at x =
// the request's serial. Every URL is absolute and distinct in every test.

import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const bench = vi.hoisted(() => ({
  width: 800,
  height: 600,
  renderers: [] as Array<{
    loop: ((timestamp: number) => void) | null;
    renders: number;
    domElement: HTMLCanvasElement;
  }>,
  scenes: [] as unknown[],
  now: 0,
  lastMesh: undefined as object | undefined,
  asks: new WeakMap<object, { url: string; at: number }>(),
  documents: new Map<string, string>(),
}));

vi.mock('three', async (importOriginal) => {
  const actual = await importOriginal<typeof import('three')>();
  /** What a page's renderer is to the viewer, minus the GPU, as the
   * draw-on-change bench's, with its loop and its counts its own. */
  class CountingRenderer {
    readonly domElement: HTMLCanvasElement;
    loop: ((timestamp: number) => void) | null = null;
    renders = 0;
    private ratio = 1;
    constructor() {
      const canvas = document.createElement('canvas');
      this.domElement = canvas;
      canvas.getBoundingClientRect = () => ({
        left: 0, top: 0, x: 0, y: 0, width: bench.width, height: bench.height,
        right: bench.width, bottom: bench.height, toJSON() { return {}; },
      }) as DOMRect;
      Object.defineProperty(canvas, 'clientWidth', { get: () => bench.width });
      Object.defineProperty(canvas, 'clientHeight', { get: () => bench.height });
      const element = canvas as unknown as Record<string, unknown>;
      element.setPointerCapture = () => undefined;
      element.releasePointerCapture = () => undefined;
      element.hasPointerCapture = () => false;
      bench.renderers.push(this);
    }
    render(scene: InstanceType<typeof actual.Scene>,
           camera: InstanceType<typeof actual.Camera>): void {
      if (scene.matrixWorldAutoUpdate === true) scene.updateMatrixWorld();
      if (camera.parent === null && camera.matrixWorldAutoUpdate === true) {
        camera.updateMatrixWorld();
      }
      this.renders += 1;
    }
    setSize(width: number, height: number): void {
      this.domElement.width = Math.floor(width * this.ratio);
      this.domElement.height = Math.floor(height * this.ratio);
    }
    setAnimationLoop(callback: ((timestamp: number) => void) | null): void { this.loop = callback; }
    setPixelRatio(ratio: number): void { this.ratio = ratio; }
    getPixelRatio(): number { return this.ratio; }
    setOpaqueSort(): void { /* the order of drawing is not drawn here */ }
    dispose(): void { /* nothing held */ }
  }
  class RecordedScene extends actual.Scene {
    constructor() { super(); bench.scenes.push(this); }
  }
  return { ...actual, WebGLRenderer: CountingRenderer, Scene: RecordedScene };
});

vi.mock('./geometry-admission', async (importOriginal) => {
  const actual = await importOriginal<Record<string, unknown>>();
  const admit = actual.admitGeometry as (...args: unknown[]) => unknown;
  return {
    ...actual,
    // Named, so that reading it where the module has none gives undefined.
    geometryCensus: actual.geometryCensus,
    admitGeometry: (url: string, ...rest: unknown[]) => {
      if (bench.lastMesh !== undefined) {
        bench.asks.set(bench.lastMesh, { url, at: ++bench.now });
        bench.lastMesh = undefined;
      }
      return admit(url, ...rest);
    },
  };
});

import * as admission from './geometry-admission';
import { MaterialPresentation } from './presentation';
import { mount } from './viewer';
import type { ViewerHandle } from './viewer';

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
  vi.stubGlobal('fetch', async (input: { url: string } | string) => {
    const url = typeof input === 'string' ? input : input.url;
    const text = bench.documents.get(url);
    if (typeof input === 'string') {
      if (text === undefined) return { ok: false, status: 404, json: async () => null };
      return { ok: true, status: 200, json: async () => JSON.parse(text) };
    }
    const version = net.versions.get(url) ?? 1;
    net.serial += 1;
    const serial = net.serial;
    return new Promise((resolve) => {
      const sent: Sent = {
        serial, url, version, at: ++bench.now, answeredAt: undefined,
        answer: (status = 200) => {
          if (sent.answeredAt !== undefined) return;
          sent.answeredAt = ++bench.now;
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

const waiting = (): Sent[] => net.sent.filter((sent) => sent.answeredAt === undefined);

async function drain(): Promise<void> {
  for (let i = 0; i < 400; i += 1) await Promise.resolve();
}

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
  meshes: new Set<THREE.Mesh>(),
  released: new Set<THREE.Mesh>(),
  viewerOf: new Map<THREE.Mesh, MaterialPresentation>(),
};

function resetSeen(): void {
  seen.parsed.clear(); seen.clones.clear(); seen.liftTemps.clear(); seen.disposals.clear();
  seen.meshes.clear(); seen.released.clear(); seen.viewerOf.clear();
}

function instrument(): void {
  const parse = STLLoader.prototype.parse;
  vi.spyOn(STLLoader.prototype, 'parse').mockImplementation(function (this: STLLoader, data) {
    const geometry = parse.call(this, data);
    seen.parsed.add(geometry);
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
      if (name === 'normal') seen.liftTemps.add(this);
      return deleteAttribute.call(this, name);
    });
  const dispose = THREE.BufferGeometry.prototype.dispose;
  vi.spyOn(THREE.BufferGeometry.prototype, 'dispose').mockImplementation(function (this: THREE.BufferGeometry) {
    seen.disposals.set(this, (seen.disposals.get(this) ?? 0) + 1);
    return dispose.call(this);
  });
  const mesh = MaterialPresentation.prototype.mesh;
  vi.spyOn(MaterialPresentation.prototype, 'mesh').mockImplementation(
    function (this: MaterialPresentation, ...args: Parameters<MaterialPresentation['mesh']>) {
      const made = mesh.apply(this, args);
      seen.meshes.add(made);
      seen.viewerOf.set(made, this);
      bench.lastMesh = made;
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
const serialOf = (geometry: THREE.BufferGeometry): number => geometry.getAttribute('position').getX(3);
const urlOf = (geometry: THREE.BufferGeometry): string | undefined =>
  net.bySerial.get(serialOf(geometry))?.url;

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
const liveMeshes = (): THREE.Mesh[] => [...seen.meshes].filter((mesh) => !seen.released.has(mesh));

interface CensusRow { url: string; viewer: object; holders: number; value: unknown }
function census(): CensusRow[] | undefined {
  const read = (admission as unknown as Record<string, unknown>).geometryCensus;
  return typeof read === 'function' ? (read as () => CensusRow[])() : undefined;
}
const rows = (prefix: string): CensusRow[] =>
  (census() ?? []).filter((row) => row.url.startsWith(prefix));

// ---------------------------------------------------------------------
// Documents and mounts.

const leaf = (name: string, model: string, extra: Record<string, unknown> = {}) => ({
  name, type: 'LeafNode', color: '#8899aa', mtime: 1, operations: [],
  model: `models/${model}`, ...extra,
});
const documentOf = (children: unknown[]) => ({
  format: 'machinome-export', version: 2, animation: { fps: 30, frames: 360 },
  drivers: {}, instructions: {},
  root: { name: 'root', type: 'AssemblyNode', color: null, mtime: 1, operations: [], children },
});
const base = (name: string): string => `http://view.test/${name}/`;
const OPTIONS = { partControls: 'none', driverControls: 'none' } as const;

interface Mounted {
  handle: ViewerHandle | undefined;
  mounting: Promise<ViewerHandle>;
  scene: THREE.Scene;
  renderer: (typeof bench.renderers)[number];
  state: 'pending' | 'live' | 'disposed' | 'failed';
}

const mounts: Mounted[] = [];

/** Mount without waiting: the scene and renderer the mount made are
 * read before its first await. */
function start(url: string): Mounted {
  const container = document.createElement('div');
  Object.defineProperty(container, 'clientWidth', { get: () => bench.width });
  Object.defineProperty(container, 'clientHeight', { get: () => bench.height });
  document.body.append(container);
  const scenes = bench.scenes.length;
  const renderers = bench.renderers.length;
  const mounting = mount(container, url, OPTIONS);
  expect(bench.scenes.length, 'the mount made its scene at once').toBe(scenes + 1);
  const entry: Mounted = {
    handle: undefined, mounting, scene: bench.scenes[scenes] as THREE.Scene,
    renderer: bench.renderers[renderers], state: 'pending',
  };
  mounts.push(entry);
  mounting.then((handle) => {
    entry.handle = handle;
    if (entry.state === 'disposed') handle.dispose();
    else entry.state = 'live';
  }, () => { entry.state = 'failed'; });
  return entry;
}

async function frames(entry: Mounted, count = 2): Promise<void> {
  for (let i = 0; i < count; i += 1) {
    bench.now += 16;
    entry.renderer.loop?.(bench.now * 16);
    await drain();
  }
}

function dispose(entry: Mounted): void {
  if (entry.state === 'live') entry.handle!.dispose();
  entry.state = 'disposed';
}

/** The meshes of a scene drawn from model files. */
function fileMeshes(scene: THREE.Scene): THREE.Mesh[] {
  const found: THREE.Mesh[] = [];
  scene.traverse((object) => {
    if (object instanceof THREE.Mesh && fromFile(object.geometry)) found.push(object);
  });
  return found;
}

const quiet = <T>(promise: Promise<T>): Promise<T> => { promise.catch(() => undefined); return promise; };

beforeEach(() => {
  bench.width = 800;
  bench.height = 600;
  bench.renderers = [];
  bench.scenes = [];
  bench.documents = new Map();
  bench.lastMesh = undefined;
  vi.spyOn(performance, 'now').mockImplementation(() => bench.now);
  stubNetwork();
  instrument();
  vi.stubGlobal('ResizeObserver', class {
    observe(): void { /* never fires */ }
    unobserve(): void { /* nothing to stop */ }
    disconnect(): void { /* nothing to stop */ }
  });
});

afterEach(async () => {
  mounts.forEach(dispose);
  await serve(500);
  await Promise.allSettled(mounts.map((entry) => entry.mounting));
  mounts.forEach(dispose);
  mounts.splice(0);
  await drain();
  document.body.replaceChildren();
  net.sent = [];
  net.bySerial.clear();
  net.versions.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  resetSeen();
});

async function served(url: string): Promise<Mounted> {
  const entry = start(url);
  await serve();
  await entry.mounting;
  await frames(entry);
  return entry;
}

// ---------------------------------------------------------------------
// V1 to V4.

describe('share-one-geometry-per-model-file: the real viewer', () => {
  it('V1: reload() reads every file again, keeps the old tree drawn until the new one is installed, then frees it', async () => {
    const at = base('v1');
    bench.documents.set(`${at}doc.json`, JSON.stringify(documentOf([
      leaf('a', 'f.stl'), leaf('b', 'f.stl'), leaf('c', 'g.stl'),
    ])));
    const viewer = await served(`${at}doc.json`);
    const old = fileMeshes(viewer.scene);
    expect(old).toHaveLength(3);
    const oldGeometries = [...new Set(old.map((mesh) => mesh.geometry))];
    const parsedBefore = new Set(seen.parsed);
    const reloading = quiet(viewer.handle!.reload());
    await drain();
    expect(waiting().map((sent) => sent.url).sort()).toEqual([`${at}models/f.stl`, `${at}models/g.stl`]);
    expect(fileMeshes(viewer.scene)).toEqual(old);
    oldGeometries.forEach((geometry) => expect(disposals(geometry)).toBe(0));
    await serve();
    await reloading;
    // The stated reason on the base: a parse per part (3).
    expect([...seen.parsed].filter((g) => !parsedBefore.has(g))).toHaveLength(2);
    const now = fileMeshes(viewer.scene);
    expect(now).toHaveLength(3);
    expect(now[0].geometry).toBe(now[1].geometry);
    now.forEach((mesh) => expect(oldGeometries.includes(mesh.geometry)).toBe(false));
    oldGeometries.forEach((geometry) => expect(disposals(geometry)).toBe(1));
    const shown = [...new Set(now.map((mesh) => mesh.geometry))];
    expect(rows(at).map((row) => [row.value, row.holders]).sort((x, y) =>
      (x[0] as THREE.BufferGeometry).id - (y[0] as THREE.BufferGeometry).id))
      .toEqual(shown.map((geometry) => [geometry, now.filter((m) => m.geometry === geometry).length]));
  });

  it('V2: two viewers of one document hold geometry of their own; disposing one leaves the other drawn', async () => {
    const at = base('v2');
    bench.documents.set(`${at}doc.json`, JSON.stringify(documentOf([
      leaf('a', 'f.stl'), leaf('b', 'f.stl'), leaf('c', 'g.stl'),
    ])));
    const one = start(`${at}doc.json`);
    const two = start(`${at}doc.json`);
    await serve();
    await Promise.all([one.mounting, two.mounting]);
    await frames(one);
    await frames(two);
    // The stated reason on the base: a parse per part of each viewer (6).
    expect([...seen.parsed]).toHaveLength(2);
    expect([...copies()]).toHaveLength(2);
    const [m1, m2] = [fileMeshes(one.scene), fileMeshes(two.scene)];
    expect(m1[0].geometry).toBe(m1[1].geometry);
    expect(m2[0].geometry).toBe(m2[1].geometry);
    m1.forEach((mesh) => expect(m2.some((other) => other.geometry === mesh.geometry)).toBe(false));
    dispose(one);
    await drain();
    m1.forEach((mesh) => expect(disposals(mesh.geometry)).toBe(1));
    m2.forEach((mesh) => expect(disposals(mesh.geometry)).toBe(0));
    expect(fileMeshes(two.scene)).toEqual(m2);
    expect(rows(at).map((row) => row.value).sort()).toEqual(
      [...new Set(m2.map((mesh) => mesh.geometry))].sort());
    dispose(two);
    await drain();
    m2.forEach((mesh) => expect(disposals(mesh.geometry)).toBe(1));
    expect(census()).toBeDefined();
    expect(rows(at)).toEqual([]);
  });

  it('V3: manifestChanged() adding a part naming a file on screen reads the file again and leaves the parts on screen as they are', async () => {
    const at = base('v3');
    const url = `${at}doc.json`;
    bench.documents.set(url, JSON.stringify(documentOf([leaf('a', 'f.stl')])));
    const viewer = await served(url);
    const [a] = fileMeshes(viewer.scene);
    const shown = a.geometry;
    const parsedBefore = new Set(seen.parsed);
    bench.documents.set(url, JSON.stringify(documentOf([leaf('a', 'f.stl'), leaf('b', 'f.stl')])));
    const changing = quiet(viewer.handle!.manifestChanged());
    await drain();
    expect(waiting().map((sent) => sent.url)).toEqual([`${at}models/f.stl`]);
    await serve();
    await changing;
    expect([...seen.parsed].filter((g) => !parsedBefore.has(g))).toHaveLength(1);
    const now = fileMeshes(viewer.scene);
    expect(now).toHaveLength(2);
    expect(now[0]).toBe(a);
    expect(a.geometry).toBe(shown);
    expect(disposals(shown)).toBe(0);
    expect(now[1].geometry).not.toBe(shown);
  });

  it('V4: artifactChanged() of a shared path reads it once and replaces every part naming it in one application, then draws', async () => {
    const at = base('v4');
    bench.documents.set(`${at}doc.json`, JSON.stringify(documentOf([
      leaf('a', 'f.stl'), leaf('b', 'f.stl'), leaf('c', 'g.stl'),
    ])));
    const viewer = await served(`${at}doc.json`);
    const old = fileMeshes(viewer.scene);
    const parsedBefore = new Set(seen.parsed);
    net.versions.set(`${at}models/f.stl`, 2);
    const changing = quiet(viewer.handle!.artifactChanged('models/f.stl'));
    await drain();
    expect(waiting().map((sent) => sent.url)).toEqual([`${at}models/f.stl`]);
    expect(fileMeshes(viewer.scene)).toEqual(old);
    const draws = viewer.renderer.renders;
    await serve();
    await changing;
    // The stated reason on the base: a parse per part naming it (2).
    expect([...seen.parsed].filter((g) => !parsedBefore.has(g))).toHaveLength(1);
    const now = fileMeshes(viewer.scene);
    expect(now).toHaveLength(3);
    expect(now[0]).not.toBe(old[0]);
    expect(now[1]).not.toBe(old[1]);
    expect(now[2]).toBe(old[2]);
    expect(now[0].geometry).toBe(now[1].geometry);
    expect(now[0].geometry.getAttribute('position').getX(1)).toBe(2);
    expect(disposals(old[0].geometry)).toBe(1);
    expect(viewer.renderer.renders).toBeGreaterThan(draws);
    expect(rows(`${at}models/f.stl`).map((row) => [row.value, row.holders])).toEqual([[now[0].geometry, 2]]);
  });
});

// ---------------------------------------------------------------------
// G2, generated, on the viewer.

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

const FILES = ['f0.stl', 'f1.stl', 'f2.stl'];

function detect(label: string, at: string, scenes: THREE.Scene[]): void {
  const live = liveMeshes();
  const copied = copies();
  const isRead = (geometry: THREE.BufferGeometry) => seen.parsed.has(geometry) || copied.has(geometry);
  // D1, over the meshes of each live viewer's scene and every live mesh.
  for (const scene of scenes) {
    scene.traverse((object) => {
      if (!(object instanceof THREE.Mesh)) return;
      expect(seen.released.has(object), `${label}: D1 a released mesh is on screen`).toBe(false);
      expect(disposals(object.geometry), `${label}: D1 a mesh on screen shows a disposed geometry`).toBe(0);
    });
  }
  for (const mesh of live) {
    expect(disposals(mesh.geometry), `${label}: D1 a live mesh shows a disposed geometry`).toBe(0);
  }
  for (const [geometry, count] of seen.disposals) {
    expect(count, `${label}: geometry ${geometry.id} disposed more than once`).toBeLessThanOrEqual(1);
  }
  // D2.
  const alive = [...seen.parsed, ...copied].filter((geometry) => disposals(geometry) === 0)
    .map((geometry) => geometry.id).sort((x, y) => x - y);
  const shown = [...new Set(live.map((mesh) => mesh.geometry).filter(isRead))]
    .map((geometry) => geometry.id).sort((x, y) => x - y);
  expect(alive, `${label}: D2`).toEqual(shown);
  // D3.
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
  // D4.
  for (const mesh of live) {
    if (!isRead(mesh.geometry)) continue;
    const asked = bench.asks.get(mesh);
    const request = net.bySerial.get(serialOf(mesh.geometry));
    expect(asked, `${label}: D4 a mesh that never asked`).toBeDefined();
    expect(request?.url, `${label}: D4 another file's geometry`).toBe(asked!.url);
    expect(request!.answeredAt! > asked!.at, `${label}: D4 a reading closed before it asked`).toBe(true);
  }
}

function generatedDocument(next: () => number, pick: <T>(items: readonly T[]) => T): unknown {
  const children: unknown[] = [];
  let budget = 1 + Math.floor(next() * 6);
  let index = 0;
  while (budget > 0) {
    const markings = budget > 1 && next() < 0.25
      ? [{ name: `m${index}`, model: `models/${pick(FILES)}`, color: '#ffffff', mtime: 1 + Math.floor(next() * 3) }]
      : undefined;
    budget -= 1 + (markings?.length ?? 0);
    children.push(leaf(`p${index}`, pick(FILES), {
      mtime: 1 + Math.floor(next() * 3), ...(markings ? { markings } : {}),
    }));
    index += 1;
  }
  return documentOf(children);
}

async function generatedViewerSequence(seed: number, steps: number,
                                       tally: Map<string, number>): Promise<void> {
  const next = random(seed);
  const pick = <T>(items: readonly T[]): T => items[Math.floor(next() * items.length)];
  const at = base(`g2-${seed}`);
  const urls = [`${at}a.json`, `${at}b.json`];
  urls.forEach((url) => bench.documents.set(url, JSON.stringify(generatedDocument(next, pick))));
  const mine: Array<{ url: string; mounted: Mounted }> = [];
  const standing = (url: string) => mine.some((entry) => entry.url === url
    && (entry.mounted.state === 'pending' || entry.mounted.state === 'live'));
  for (let step = 0; step < steps; step += 1) {
    const roll = next();
    const live = mine.filter((entry) => entry.mounted.state === 'live');
    let done = 'nothing';
    const free = urls.filter((url) => !standing(url));
    if ((roll < 0.15 || live.length === 0) && free.length > 0) {
      const url = pick(free);
      mine.push({ url, mounted: start(url) });
      done = 'mount';
    } else if (roll < 0.25 && live.length > 0) {
      quiet(pick(live).mounted.handle!.reload());
      done = 'reload';
    } else if (roll < 0.4 && live.length > 0) {
      const entry = pick(live);
      bench.documents.set(entry.url, JSON.stringify(generatedDocument(next, pick)));
      quiet(entry.mounted.handle!.manifestChanged());
      done = 'manifestChanged';
    } else if (roll < 0.5 && live.length > 0) {
      quiet(pick(live).mounted.handle!.artifactChanged(`models/${pick(FILES)}`));
      done = 'artifactChanged';
    } else if (roll < 0.58) {
      const file = `${at}models/${pick(FILES)}`;
      net.versions.set(file, (net.versions.get(file) ?? 1) + 1);
      done = 'rewrite';
    } else if (roll < 0.92 && waiting().length > 0) {
      const status = next() < 0.12 ? 500 : 200;
      pick(waiting()).answer(status);
      done = `answer ${status}`;
    } else if (live.length > 0) {
      dispose(pick(live).mounted);
      done = 'dispose';
    }
    tally.set(done, (tally.get(done) ?? 0) + 1);
    await drain();
    for (const entry of mine) if (entry.mounted.state === 'live') await frames(entry.mounted, 1);
    detect(`seed ${seed} step ${step} (${done})`, at,
      mine.filter((entry) => entry.mounted.state === 'live').map((entry) => entry.mounted.scene));
  }
  // D5.
  for (let round = 0; round < 10; round += 1) {
    mine.forEach((entry) => dispose(entry.mounted));
    await serve();
    await Promise.allSettled(mine.map((entry) => entry.mounted.mounting));
    await drain();
  }
  mine.forEach((entry) => dispose(entry.mounted));
  await drain();
  const read = [...seen.parsed, ...copies()].filter((geometry) => urlOf(geometry)?.startsWith(at));
  tally.set('requests', (tally.get('requests') ?? 0) + net.sent.length);
  tally.set('parses', (tally.get('parses') ?? 0) + seen.parsed.size);
  tally.set('copies', (tally.get('copies') ?? 0) + copies().size);
  tally.set('mounted', (tally.get('mounted') ?? 0)
    + mine.filter((entry) => entry.mounted.handle !== undefined).length);
  expect(read.map(disposals).filter((count) => count !== 1), `seed ${seed}: D5 freed once`).toEqual([]);
  expect(census(), `seed ${seed}: D5 the census`).toBeDefined();
  expect(rows(at), `seed ${seed}: D5 the census is empty`).toEqual([]);
}

describe('G2: generated sequences on the viewer', () => {
  it('40 seeded sequences of 25 steps on two mounts keep D1 to D5', async () => {
    const started = Date.now();
    const tally = new Map<string, number>();
    // G2_FROM and G2_TO replay a printed seed alone.
    for (let seed = Number(process.env.G2_FROM ?? 1); seed <= Number(process.env.G2_TO ?? 40); seed += 1) {
      try {
        await generatedViewerSequence(seed, 25, tally);
      } catch (error) {
        console.error(`G2 failed at seed ${seed}`);
        throw error;
      } finally {
        mounts.forEach(dispose);
        await serve(500);
        await Promise.allSettled(mounts.map((entry) => entry.mounting));
        mounts.forEach(dispose);
        mounts.splice(0);
        net.sent = [];
        net.bySerial.clear();
        net.versions.clear();
        resetSeen();
      }
    }
    console.info(`G2: 40 sequences of 25 steps in ${Date.now() - started} ms`,
                 JSON.stringify(Object.fromEntries([...tally].sort())));
  }, 600_000);
});
