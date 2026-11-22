/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The bench of OpenSpec `draw-only-when-the-picture-changes`, design
// Decision 8: the REAL `mount()` in jsdom, with three.js's
// `WebGLRenderer` replaced by a counting renderer whose `render` does to
// the scene graph what three.js 0.156.1's does before it draws, and whose
// animation loop is kept and driven here frame by frame, with timestamps
// the test chooses. Nothing else of the viewer is replaced: the trees,
// the holder, the drivers, the clocked machine, the run (in thread, as a
// page without a worker runs it), the orbit controls and the pointer
// surface are the ones a page gets.
//
// D, the detector, reads everything a draw reads -- the camera, the
// canvas's size, and for every object of the scene its identity, its
// parent, `visible`, its world matrix, its layers, `renderOrder`,
// `frustumCulled`, a mesh's material and geometry and their versions, a
// light's colour and intensity -- and `expectDrawn()` fails, naming the
// field, when the present reading differs from the one taken at the last
// draw. What D cannot see: a material property written in place without
// its version, a buffer written without its version, state outside
// three.js objects, pixels.
//
// Counts and constants named W1, O1 and M1 to M6 were printed on the
// base (`56de33dd`) before any source change and are written here as
// they printed (evidence.md); they are not regenerated.

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import * as THREE from 'three';
import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';
import type { MockInstance } from 'vitest';
import { mount } from './viewer';
import type { ViewerHandle, ViewerOptions } from './viewer';
import { WidgetTree } from './tree';
import type { Changed } from './tree';
import { FlexibleShape } from './flexible';
import { RunRuntime } from './run/runtime';

// ---------------------------------------------------------------------
// The bench's shared state, reachable from the mocked modules.

type Reading = Array<[string, unknown]>;

const bench = vi.hoisted(() => ({
  now: 0,
  renders: 0,
  sizes: 0,
  width: 800,
  height: 600,
  loop: undefined as ((timestamp: number) => void) | null | undefined,
  loopCalls: [] as unknown[],
  scene: undefined as unknown,
  camera: undefined as unknown,
  canvas: undefined as unknown,
  record: undefined as unknown,
  read: undefined as undefined
    | ((scene: unknown, camera: unknown, canvas: unknown) => unknown),
  observers: [] as Array<{
    callback: (entries: unknown[], observer: unknown) => void;
    self: unknown; connected: boolean;
  }>,
  load: undefined as undefined | ((url: string) => Promise<unknown>),
  documents: new Map<string, string>(),
}));

vi.mock('three', async (importOriginal) => {
  const actual = await importOriginal<typeof import('three')>();
  /** What a page's renderer is to the viewer, minus the GPU: `render`
   * brings the scene's and the camera's world matrices up to date as
   * three.js 0.156.1's does before drawing (`WebGLRenderer.js` 1044,
   * 1048), counts, and records D's reading of what it would draw. */
  class CountingRenderer {
    readonly domElement: HTMLCanvasElement;
    private ratio = 1;
    constructor() {
      const canvas = document.createElement('canvas');
      this.domElement = canvas;
      bench.canvas = canvas;
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
    }
    render(scene: InstanceType<typeof actual.Scene>,
           camera: InstanceType<typeof actual.Camera>): void {
      if (scene.matrixWorldAutoUpdate === true) scene.updateMatrixWorld();
      if (camera.parent === null && camera.matrixWorldAutoUpdate === true) {
        camera.updateMatrixWorld();
      }
      bench.renders += 1;
      bench.scene = scene;
      bench.camera = camera;
      bench.record = bench.read?.(scene, camera, this.domElement);
    }
    setSize(width: number, height: number): void {
      bench.sizes += 1;
      this.domElement.width = Math.floor(width * this.ratio);
      this.domElement.height = Math.floor(height * this.ratio);
    }
    setAnimationLoop(callback: ((timestamp: number) => void) | null): void {
      bench.loopCalls.push(callback);
      bench.loop = callback;
    }
    setPixelRatio(ratio: number): void { this.ratio = ratio; }
    getPixelRatio(): number { return this.ratio; }
    setOpaqueSort(): void { /* the order of drawing is not drawn here */ }
    dispose(): void { /* nothing held */ }
  }
  return { ...actual, WebGLRenderer: CountingRenderer };
});

vi.mock('three/examples/jsm/loaders/STLLoader.js', async () => {
  const actual = await vi.importActual<typeof import('three')>('three');
  return {
    STLLoader: class {
      loadAsync(url: string): Promise<unknown> {
        return bench.load !== undefined ? bench.load(url)
          : Promise.resolve(new actual.BoxGeometry(2, 3, 4));
      }
    },
  };
});

// ---------------------------------------------------------------------
// Documents.

// jsdom gives `import.meta.url` no file scheme, so the fixtures are found
// from this file's directory.
const FIXTURES = resolve(__dirname, '../../../../../tests/fixtures');
const fixture = (path: string): string =>
  readFileSync(resolve(FIXTURES, path), 'utf8');

const FLOAT = (range: [number, number] | null = null, unit: string | null = null) => ({
  default: 0, range, unit, dtype: null, scale: null,
});
const INT = (range: [number, number] | null = null) => ({
  default: 0, range, unit: null, dtype: 'int', scale: null,
});
const leaf = (name: string, operations: unknown[], extra: Record<string, unknown> = {}) => ({
  name, type: 'LeafNode', color: '#8899aa', mtime: 1, operations,
  model: `models/${name}.stl`, ...extra,
});
const assembly = (name: string, children: unknown[], operations: unknown[] = []) => ({
  name, type: 'AssemblyNode', color: null, mtime: 1, operations, children,
});
const SPRING = {
  name: 'spring', type: 'LeafNode', color: '#a0a0a0', mtime: 1, operations: [],
  flexible: {
    tech: 'molejo',
    spec: {
      molejo: '0.1',
      profile: { type: 'circle', radius: 2.0 },
      path: [{ type: 'helix', radius: 14.0, turns: 6.5, height: { param: 'height' } }],
      loop: false,
      tessellation: { path: 48, profile: 8 },
    },
    params: { height: '(46.8 - lift)' },
  },
};
const MARKINGS = [
  { name: 'digits', model: 'models/digits.stl', color: '#FFFFFF', mtime: 1 },
  { name: 'band', model: 'models/band.stl', color: '#C0C0C0', mtime: 1 },
];

/** A hand-written version 2 document: one part on a driver. */
const V2 = {
  format: 'machinome-export', version: 2, animation: { fps: 30, frames: 360 },
  drivers: { x: FLOAT([0, 10], 'mm') }, instructions: {},
  root: assembly('root', [leaf('block', [['t', ['x', '0', '0']]]), leaf('base', [])]),
};

/** A hand-written POSED document (version 14) carrying drivers, an
 * integer driver, instructions, a timeline, a colour choice, markings and
 * a flexible part. */
const POSED = {
  format: 'machinome-export', version: 14, animation: { fps: 30, frames: 360 },
  drivers: {
    x: FLOAT([0, 10], 'mm'), n: INT([0, 10]), lift: FLOAT([0, 12], 'mm'),
    powered: FLOAT([0, 1]),
  },
  instructions: {
    Slide: { targets: { x: 5 }, duration: 0.5 },
    Advance: { targets: { n: 3 }, duration: 1.0 },
  },
  root: assembly('root', [
    leaf('carriage', [['t', ['x', '0', '0']]], { markings: MARKINGS }),
    leaf('wheel', [['r', '(n * 36)', [0, 0, 1]]]),
    leaf('spinner', [['r', '($t * 360)', [0, 0, 1]], ['t', ['0', '20', '0']]]),
    leaf('lamp', [['t', ['0', '-20', '0']]], {
      color: { when: '(powered > 0.5)', on: '#ffd978', off: '#e5dfce' },
    }),
    SPRING,
    assembly('frame', [leaf('left', [['t', ['-30', '0', '0']]]),
                       leaf('right', [['t', ['30', '0', '0']]])]),
  ]),
};

/** A posed document with drivers and an instruction, nothing else. */
const INSTRUCTED = {
  format: 'machinome-export', version: 2, animation: { fps: 30, frames: 360 },
  drivers: { x: FLOAT([0, 10], 'mm') },
  instructions: { Slide: { targets: { x: 5 }, duration: 0.5 } },
  root: assembly('root', [leaf('block', [['t', ['x', '0', '0']]])]),
};

/** One flexible part. */
const FLEXIBLE = {
  format: 'machinome-export', version: 3, animation: { fps: 30, frames: 360 },
  drivers: { lift: FLOAT([0, 12], 'mm') }, instructions: {},
  root: assembly('root', [SPRING, leaf('valve', [['t', ['0', '0', 'lift']]])]),
};

/** Markings on a part. */
const MARKED = {
  format: 'machinome-export', version: 2, animation: { fps: 30, frames: 360 },
  drivers: { angle: FLOAT(null, 'deg') }, instructions: {},
  root: assembly('root', [
    leaf('dial', [['r', 'angle', [0, 0, 1]]], { markings: MARKINGS }),
    leaf('plate', [], { markings: [MARKINGS[1]] }),
  ]),
};

/** A hand-written CLOCKED document whose instructions are drawn, on an
 * integer input, with no clock. */
const CLOCKED = {
  format: 'machinome-export', version: 8, animation: { fps: 30, frames: 360 },
  drivers: { n: INT() }, states: {},
  instructions: {
    Press: { by: { n: 1 }, duration: 0.2 },
    Turn: { by: { n: 3 }, duration: 1.0 },
  },
  bindings: [],
  clocked: {
    identity: 'hand-written-drawn', clock: null, own: '_own',
    commits: [], bounds: [],
    limits: { crossing_tolerance: 1e-12, max_crossings: 1000 },
  },
  root: assembly('root', [
    leaf('wheel', [['r', '(n * 36)', [0, 0, 1]]]),
    leaf('stand', [['t', ['0', '-10', '0']]]),
  ]),
};

const DOCUMENTS: Record<string, string> = {
  'v2.json': JSON.stringify(V2),
  'posed.json': JSON.stringify(POSED),
  'instructed.json': JSON.stringify(INSTRUCTED),
  'flexible.json': JSON.stringify(FLEXIBLE),
  'markings.json': JSON.stringify(MARKED),
  'clocked.json': JSON.stringify(CLOCKED),
  'regulator.json': fixture('regulator/viewer.json'),
  'touched.json': fixture('touched/viewer.json'),
  'spinner.json': fixture('spinner/manifest.json'),
  'marked.json': fixture('marked/manifest.json'),
  'state-color.json': fixture('state-color/posed/manifest.json'),
  'calculator.json': fixture('calculator/viewer.json'),
};

/** Every kind of document a page mounts, each with the options a still
 * page of it has. */
const KINDS: Array<[string, string, ViewerOptions]> = [
  ['a hand-written version 2 document', 'v2.json', {}],
  ['regulator (clocked, clock paused)', 'regulator.json', {}],
  ['touched (running, run paused)', 'touched.json', {}],
  ['state-color/posed (a colour choice)', 'state-color.json', {}],
  ['spinner (timeline, autoplay false)', 'spinner.json', { autoplay: false }],
  ['a posed document with drivers and an instruction', 'instructed.json', {}],
  ['a flexible part', 'flexible.json', {}],
  ['markings', 'markings.json', {}],
  ['the whole posed document', 'posed.json', { autoplay: false }],
  ['marked (fixture)', 'marked.json', {}],
  ['calculator (clocked fixture)', 'calculator.json', {}],
  ['a hand-written clocked document with drawn instructions', 'clocked.json', {}],
];

// ---------------------------------------------------------------------
// D, the detector.

function pictureState(scene: THREE.Scene, camera: THREE.Camera,
                      canvas: HTMLCanvasElement): Reading {
  scene.updateMatrixWorld(true);
  camera.updateMatrixWorld();
  const reading: Reading = [];
  const put = (name: string, value: unknown) => { reading.push([name, value]); };
  const matrix = (name: string, value: THREE.Matrix4) => {
    value.elements.forEach((element, index) => put(`${name}[${index}]`, element));
  };
  matrix('camera.matrixWorld', camera.matrixWorld);
  matrix('camera.projectionMatrix', camera.projectionMatrix);
  put('camera.layers', camera.layers.mask);
  put('canvas.width', canvas.width);
  put('canvas.height', canvas.height);
  put('scene.background', scene.background);
  put('scene.environment', scene.environment);
  put('scene.fog', scene.fog);
  put('scene.overrideMaterial', scene.overrideMaterial);
  let index = 0;
  scene.traverse((object) => {
    const at = `object ${index} (${object.type})`;
    index += 1;
    put(`${at} identity`, object);
    put(`${at} parent`, object.parent);
    put(`${at} visible`, object.visible);
    matrix(`${at} matrixWorld`, object.matrixWorld);
    put(`${at} layers`, object.layers.mask);
    put(`${at} renderOrder`, object.renderOrder);
    put(`${at} frustumCulled`, object.frustumCulled);
    if (object instanceof THREE.Mesh) {
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      materials.forEach((material, i) => {
        put(`${at} material ${i}`, material);
        put(`${at} material ${i} version`, material.version);
      });
      const geometry = object.geometry as THREE.BufferGeometry;
      put(`${at} geometry`, geometry);
      for (const name of Object.keys(geometry.attributes).sort()) {
        const attribute = geometry.attributes[name] as THREE.BufferAttribute;
        put(`${at} attribute ${name}`, attribute);
        put(`${at} attribute ${name} version`, attribute.version);
      }
      put(`${at} index`, geometry.index);
      put(`${at} index version`, geometry.index?.version);
      put(`${at} drawRange.start`, geometry.drawRange.start);
      put(`${at} drawRange.count`, geometry.drawRange.count);
      put(`${at} groups`, geometry.groups.length);
    }
    if (object instanceof THREE.Light) {
      put(`${at} color`, object.color.getHex());
      put(`${at} intensity`, object.intensity);
      if (object instanceof THREE.HemisphereLight) {
        put(`${at} groundColor`, object.groundColor.getHex());
      }
    }
  });
  return reading;
}

bench.read = (scene, camera, canvas) => pictureState(
  scene as THREE.Scene, camera as THREE.Camera, canvas as HTMLCanvasElement);

/** The fields in which two readings differ, by name, under `Object.is`. */
function differences(drawn: Reading, now: Reading): string[] {
  const found: string[] = [];
  const length = Math.max(drawn.length, now.length);
  for (let i = 0; i < length && found.length < 8; i += 1) {
    const a = drawn[i];
    const b = now[i];
    if (a === undefined || b === undefined) {
      found.push(`reading length ${drawn.length} drawn, ${now.length} now`);
      break;
    }
    if (a[0] !== b[0]) {
      found.push(`${b[0]} (drawn: ${a[0]})`);
      break;
    }
    if (!Object.is(a[1], b[1])) found.push(b[0]);
  }
  return found;
}

function present(): Reading {
  return pictureState(bench.scene as THREE.Scene, bench.camera as THREE.Camera,
                      bench.canvas as HTMLCanvasElement);
}

/** The picture last drawn is the present state, field for field. */
function expectDrawn(): void {
  expect(bench.record, 'nothing has been drawn').toBeDefined();
  expect(differences(bench.record as Reading, present())).toEqual([]);
}

// ---------------------------------------------------------------------
// Driving the mount.

let updates: MockInstance;
const opened: ViewerHandle[] = [];
let container: HTMLElement;

/** Whether a change set names anything (`all`, time, or a driver). */
function names(changed: Changed | undefined): boolean {
  if (changed === undefined || changed === 'all') return true;
  return changed.time || changed.drivers.size > 0;
}

function namedUpdates(): number {
  return updates.mock.calls.filter((call) => names(call[1] as Changed | undefined)).length;
}

async function settle(): Promise<void> {
  for (let i = 0; i < 40; i += 1) await Promise.resolve();
}

/** `count` animation frames, `ms` milliseconds apart, each followed by
 * the microtasks it queued (a run's in-thread replies). */
async function frames(count: number, ms = 16): Promise<void> {
  for (let i = 0; i < count; i += 1) {
    bench.now += ms;
    const loop = bench.loop;
    if (typeof loop !== 'function') throw new Error('no animation loop installed');
    loop(bench.now);
    await settle();
  }
}

/** The resize observer's callback, as a browser runs it. */
function observe(): void {
  for (const observer of bench.observers) {
    if (observer.connected) observer.callback([], observer.self);
  }
}

/** Draws and named and unnamed updates during `action`. */
async function counted(action: () => Promise<void> | void): Promise<{
  draws: number; updates: number; named: number;
}> {
  const renders = bench.renders;
  const calls = updates.mock.calls.length;
  const named = namedUpdates();
  await action();
  return { draws: bench.renders - renders, updates: updates.mock.calls.length - calls,
           named: namedUpdates() - named };
}

/** Per frame, for `count` frames: [draws, updates naming something]. */
async function perFrame(count: number, ms = 16,
                        until?: () => boolean): Promise<Array<[number, number]>> {
  const out: Array<[number, number]> = [];
  for (let i = 0; i < count; i += 1) {
    const one = await counted(() => frames(1, ms));
    out.push([one.draws, one.named]);
    if (until?.()) break;
  }
  return out;
}

async function open(name: string, options: ViewerOptions = {}): Promise<ViewerHandle> {
  const viewer = await mount(container, name, options);
  opened.push(viewer);
  return viewer;
}

/** A mounted page brought to rest: its first two frames and the resize
 * observer's first observation. */
async function rested(name: string, options: ViewerOptions = {}): Promise<ViewerHandle> {
  const viewer = await open(name, options);
  await frames(2);
  observe();
  return viewer;
}

/** `count` frames that must draw and update nothing. */
async function expectStill(count = 10): Promise<void> {
  const tail = await counted(() => frames(count));
  expect({ draws: tail.draws, updates: tail.updates }).toEqual({ draws: 0, updates: 0 });
}

function canvas(): HTMLCanvasElement {
  return bench.canvas as HTMLCanvasElement;
}

function pointer(type: string, x: number, y: number, init: PointerEventInit = {}): void {
  canvas().dispatchEvent(new PointerEvent(type, {
    bubbles: true, cancelable: true, composed: true, clientX: x, clientY: y,
    pointerId: 1, pointerType: 'mouse', button: 0, buttons: 1, isPrimary: true, ...init,
  }));
}

function wheel(deltaY = 120): void {
  canvas().dispatchEvent(new WheelEvent('wheel', {
    bubbles: true, cancelable: true, deltaY, clientX: 400, clientY: 300,
  }));
}

/** A point at which a press reaches the named control, as a host reads it. */
function controlPoint(viewer: ViewerHandle, name: string): { x: number; y: number } {
  const control = viewer.controls().find((one) => one.name === name);
  if (control === undefined || control.point === null) {
    throw new Error(`the control ${name} is not reachable on screen`);
  }
  return control.point;
}

/** The materials of the meshes under a path, in traversal order. */
function materialsUnder(path: string[]): THREE.Material[] {
  const scene = bench.scene as THREE.Scene;
  const root = scene.children.find((child) => child instanceof THREE.Group) as THREE.Group;
  let node: THREE.Object3D = root;
  const tree = opened[opened.length - 1].assembly();
  let level = tree;
  for (const name of path) {
    const index = level.children.findIndex((child) => child.name === name);
    level = level.children[index];
    node = node.children.filter((child) => child instanceof THREE.Group)[index];
  }
  const found: THREE.Material[] = [];
  node.traverse((object) => {
    if (object instanceof THREE.Mesh) found.push(object.material as THREE.Material);
  });
  return found;
}

beforeEach(() => {
  bench.now = 1000;
  bench.renders = 0;
  bench.sizes = 0;
  bench.width = 800;
  bench.height = 600;
  bench.loop = undefined;
  bench.loopCalls = [];
  bench.scene = undefined;
  bench.camera = undefined;
  bench.canvas = undefined;
  bench.record = undefined;
  bench.observers = [];
  bench.load = undefined;
  bench.documents = new Map(Object.entries(DOCUMENTS));
  vi.spyOn(performance, 'now').mockImplementation(() => bench.now);
  vi.stubGlobal('fetch', async (url: string) => {
    const text = bench.documents.get(String(url));
    if (text === undefined) return { ok: false, status: 404, json: async () => null };
    return { ok: true, status: 200, json: async () => JSON.parse(text) };
  });
  vi.stubGlobal('ResizeObserver', class {
    private readonly entry: { callback: (entries: unknown[], observer: unknown) => void;
                              self: unknown; connected: boolean };
    constructor(callback: (entries: unknown[], observer: unknown) => void) {
      this.entry = { callback, self: this, connected: false };
      bench.observers.push(this.entry);
    }
    observe(): void { this.entry.connected = true; }
    unobserve(): void { this.entry.connected = false; }
    disconnect(): void { this.entry.connected = false; }
  });
  updates = vi.spyOn(WidgetTree.prototype, 'update');
  container = document.createElement('div');
  Object.defineProperty(container, 'clientWidth', { get: () => bench.width });
  Object.defineProperty(container, 'clientHeight', { get: () => bench.height });
  document.body.append(container);
});

afterEach(() => {
  opened.splice(0).forEach((viewer) => viewer.dispose());
  document.body.replaceChildren();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

// ---------------------------------------------------------------------
// D0. The detector sees each kind of write.

describe('D0: the detector sees every kind of write a draw reads', () => {
  it('fails naming each field written behind the viewer\'s back, and passes again once undone', async () => {
    await rested('v2.json');
    await frames(1);
    if (bench.record === undefined) await frames(1);
    expectDrawn();
    const scene = bench.scene as THREE.Scene;
    const camera = bench.camera as THREE.PerspectiveCamera;
    const root = scene.children.find((child) => child instanceof THREE.Group) as THREE.Group;
    const group = root.children[0] as THREE.Group;
    let mesh: THREE.Mesh | undefined;
    root.traverse((object) => { if (mesh === undefined && object instanceof THREE.Mesh) mesh = object; });
    const drawn = bench.record as Reading;
    const writes: Array<[string, RegExp, () => () => void]> = [
      ['a group\'s matrix', /matrixWorld/, () => {
        const before = group.matrix.clone();
        group.matrix.elements[12] += 1;
        return () => { group.matrix.copy(before); };
      }],
      ['a mesh\'s visible', /visible/, () => {
        mesh!.visible = false;
        return () => { mesh!.visible = true; };
      }],
      ['a mesh pointed at another material', /material 0$/, () => {
        const before = mesh!.material;
        mesh!.material = new THREE.MeshBasicMaterial();
        return () => { mesh!.material = before; };
      }],
      ['an attribute\'s version', /attribute position version/, () => {
        const position = mesh!.geometry.getAttribute('position') as THREE.BufferAttribute;
        position.needsUpdate = true;
        return () => { position.version -= 1; };
      }],
      ['the camera', /camera\.matrixWorld/, () => {
        const before = camera.position.clone();
        camera.position.x += 1;
        return () => { camera.position.copy(before); };
      }],
      ['the camera\'s projection', /camera\.projectionMatrix/, () => {
        const before = camera.fov;
        camera.fov = before + 5;
        camera.updateProjectionMatrix();
        return () => { camera.fov = before; camera.updateProjectionMatrix(); };
      }],
      ['the canvas\'s size', /canvas\.width/, () => {
        const before = canvas().width;
        canvas().width = before + 1;
        return () => { canvas().width = before; };
      }],
    ];
    for (const [what, field, write] of writes) {
      const undo = write();
      const found = differences(drawn, present());
      expect(found.length, `${what} was not seen`).toBeGreaterThan(0);
      expect(found.some((name) => field.test(name)), `${what}: ${found.join(', ')}`).toBe(true);
      undo();
      expect(differences(drawn, present()), `${what} undone`).toEqual([]);
    }
  });
});

// ---------------------------------------------------------------------
// I1, I2, S0. A still page.

describe('I1: a still page draws and updates nothing', () => {
  it.each(KINDS)('%s: thirty still frames draw nothing and update nothing', async (_kind, name, options) => {
    await rested(name, options);
    const still = await counted(() => frames(30));
    expect({ draws: still.draws, updates: still.updates }).toEqual({ draws: 0, updates: 0 });
  });
});

describe('I2: a zero-sized container is still too', () => {
  it('thirty frames of a container with no size draw nothing', async () => {
    bench.width = 0;
    bench.height = 0;
    await rested('v2.json');
    const still = await counted(() => frames(30));
    expect(still.draws).toBe(0);
  });
});

describe('S0: the first frame after a mount is drawn', () => {
  it.each(KINDS)('%s: the first frame draws once, and D matches', async (_kind, name, options) => {
    await open(name, options);
    const first = await counted(() => frames(1));
    expect(first.draws).toBe(1);
    expectDrawn();
  });
});

// ---------------------------------------------------------------------
// S1 to S8. Each source drawn within one frame, and not after.

/** One frame after a change: drawn once, D matches, then ten frames draw
 * nothing. */
async function expectShownOnce(): Promise<void> {
  const next = await counted(() => frames(1));
  expect(next.draws, 'the frame after the change').toBe(1);
  expectDrawn();
  await expectStill(10);
}

function cameraNumbers(): number[] {
  const camera = bench.camera as THREE.Camera;
  camera.updateMatrixWorld();
  return [...camera.matrixWorld.elements, ...camera.projectionMatrix.elements];
}

describe('S1 to S8: each source of a changed picture is drawn within one frame, and not after', () => {
  it('S1: a wheel event on the canvas', async () => {
    await rested('v2.json');
    const before = cameraNumbers();
    wheel(120);
    await expectShownOnce();
    expect(cameraNumbers()).not.toEqual(before);
  });

  it('S2: a pointer drag on the canvas turns the model', async () => {
    await rested('v2.json');
    const before = cameraNumbers();
    pointer('pointerdown', 400, 300);
    pointer('pointermove', 460, 330);
    pointer('pointerup', 460, 330, { buttons: 0 });
    await expectShownOnce();
    expect(cameraNumbers()).not.toEqual(before);
  });

  it('S3: a resize is drawn inside the observer\'s callback, then nothing', async () => {
    await rested('v2.json');
    await frames(1);
    bench.width = 640;
    bench.height = 480;
    const inside = await counted(() => { observe(); });
    expect(inside.draws, 'draws inside the observer\'s callback').toBe(1);
    expectDrawn();
    expect(canvas().width).toBe(640);
    await expectStill(10);
    // Added in review: an observation at an unchanged size is drawn too.
    // Every `setSize` is followed by a draw, because a browser may clear
    // the canvas whenever its size is set; headless Chromium does not at
    // an equal size, so only this count holds the rule.
    const again = await counted(() => { observe(); });
    expect(again.draws, 'draws at an unchanged size').toBe(1);
    expectDrawn();
    await expectStill(10);
  });

  it('S4: a hover on a touchable part, and its end by moving away', async () => {
    const viewer = await rested('touched.json');
    await frames(1);
    const control = viewer.controls().find((one) => one.point !== null)!;
    const plain = materialsUnder(control.part);
    const at = controlPoint(viewer, control.name);
    pointer('pointermove', at.x, at.y, { buttons: 0 });
    await expectShownOnce();
    expect(materialsUnder(control.part)).not.toEqual(plain);
    expect(canvas().style.cursor).toBe('pointer');
    pointer('pointermove', 1, 1, { buttons: 0 });
    await expectShownOnce();
    expect(materialsUnder(control.part)).toEqual(plain);
  });

  it('S5: a hover ended by the window\'s blur', async () => {
    const viewer = await rested('touched.json');
    await frames(1);
    const control = viewer.controls().find((one) => one.point !== null)!;
    const plain = materialsUnder(control.part);
    const at = controlPoint(viewer, control.name);
    pointer('pointermove', at.x, at.y, { buttons: 0 });
    await frames(1);
    expect(materialsUnder(control.part)).not.toEqual(plain);
    await frames(1);
    window.dispatchEvent(new Event('blur'));
    await expectShownOnce();
    expect(materialsUnder(control.part)).toEqual(plain);
  });

  it('S6: reload() shows the new tree', async () => {
    const viewer = await rested('v2.json');
    await frames(1);
    const shown = (bench.scene as THREE.Scene).children.find((child) => child instanceof THREE.Group);
    await viewer.reload();
    await expectShownOnce();
    const now = (bench.scene as THREE.Scene).children.find((child) => child instanceof THREE.Group);
    expect(now).not.toBe(shown);
  });

  it('S7: a restored graphics context draws the next frame', async () => {
    await rested('v2.json');
    await frames(1);
    canvas().dispatchEvent(new Event('webglcontextrestored'));
    await expectShownOnce();
  });

  it('S8: a page shown again draws the next frame', async () => {
    await rested('v2.json');
    await frames(1);
    expect(document.hidden).toBe(false);
    document.dispatchEvent(new Event('visibilitychange'));
    await expectShownOnce();
  });
});

// ---------------------------------------------------------------------
// S9. Every call that draws still draws before it returns.

type Call = [string, string, ViewerOptions, (viewer: ViewerHandle) => Promise<void> | void];

const CALLS: Call[] = [
  ['setView', 'posed.json', { autoplay: false }, (viewer) => {
    viewer.setView({ camera: [120, -80, 90], target: [0, 0, 0] });
  }],
  ['setView with a new up', 'posed.json', { autoplay: false }, (viewer) => {
    viewer.setView({ camera: [120, -80, 90], target: [0, 0, 0], up: [0, 1, 0], fov: 30 });
  }],
  ['setDriver', 'posed.json', { autoplay: false }, (viewer) => { viewer.setDriver('x', 3); }],
  ['setTime', 'posed.json', { autoplay: false }, (viewer) => { viewer.setTime(0.25); }],
  ['setVisible off', 'posed.json', { autoplay: false }, (viewer) => { viewer.setVisible(['wheel'], false); }],
  ['setRoot', 'posed.json', { autoplay: false }, (viewer) => { viewer.setRoot(['frame']); }],
  ['highlight', 'posed.json', { autoplay: false }, (viewer) => {
    viewer.highlight([['wheel']], { others: 'dim' });
  }],
  ['artifactChanged', 'posed.json', { autoplay: false }, async (viewer) => {
    await viewer.artifactChanged('models/wheel.stl');
  }],
  ['manifestChanged', 'posed.json', { autoplay: false }, async (viewer) => {
    const moved = structuredClone(POSED);
    (moved.root.children[1] as { operations: unknown[] }).operations =
      [['r', '(n * 36)', [0, 0, 1]], ['t', ['0', '0', '7']]];
    (moved.root.children[0] as { color: string }).color = '#22aa22';
    bench.documents.set('posed.json', JSON.stringify(moved));
    await viewer.manifestChanged();
  }],
  ['machine().move', 'clocked.json', {}, (viewer) => { viewer.machine()!.move('n', { by: 2 }); }],
  ['machine().restore', 'clocked.json', {}, (viewer) => {
    const machine = viewer.machine()!;
    const rest = machine.snapshot();
    machine.move('n', { by: 4 });
    machine.restore(rest);
  }],
  ['machine().reset', 'clocked.json', {}, (viewer) => {
    const machine = viewer.machine()!;
    machine.move('n', { by: 4 });
    machine.reset();
  }],
];

describe('S9: every call that draws still draws before it returns, and nothing after', () => {
  it.each(CALLS)('%s', async (_name, document, options, call) => {
    const viewer = await rested(document, options);
    await frames(1);
    const inside = await counted(() => call(viewer));
    expect(inside.draws, 'draws inside the call').toBeGreaterThan(0);
    expectDrawn();
    await expectStill(10);
  });

  it('highlight\'s put-back', async () => {
    const viewer = await rested('posed.json', { autoplay: false });
    const restore = viewer.highlight([['wheel']], { others: 'ghost' });
    await frames(1);
    const inside = await counted(() => { restore(); });
    expect(inside.draws, 'draws inside the put-back').toBeGreaterThan(0);
    expectDrawn();
    await expectStill(10);
  });

  it('setVisible on again, and setRoot back', async () => {
    const viewer = await rested('posed.json', { autoplay: false });
    viewer.setVisible(['wheel'], false);
    viewer.setRoot(['frame']);
    await frames(1);
    for (const call of [() => viewer.setVisible(['wheel'], true), () => viewer.setRoot(null)]) {
      const inside = await counted(call);
      expect(inside.draws).toBeGreaterThan(0);
      expectDrawn();
    }
    await expectStill(10);
  });
});

// ---------------------------------------------------------------------
// S10. Two changes before one frame cost one draw.

describe('S10: two changes before one frame cost one draw', () => {
  it('a wheel event and a hover before one frame: one draw, showing both', async () => {
    const viewer = await rested('touched.json');
    await frames(1);
    const control = viewer.controls().find((one) => one.point !== null)!;
    const plain = materialsUnder(control.part);
    const before = cameraNumbers();
    const at = controlPoint(viewer, control.name);
    pointer('pointermove', at.x, at.y, { buttons: 0 });
    wheel(-40);
    const next = await counted(() => frames(1));
    expect(next.draws).toBe(1);
    expectDrawn();
    expect(cameraNumbers()).not.toEqual(before);
    await expectStill(10);
    void plain;
  });
});

// ---------------------------------------------------------------------
// S11. A republish drawn while its new program starts.

describe('S11: a republish applied while its new program starts is drawn by the next frame', () => {
  it('the frame between the application and the call\'s own draw is drawn, and nothing after', async () => {
    const viewer = await rested('touched.json');
    await frames(1);
    const original = RunRuntime.start.bind(RunRuntime);
    let release!: () => void;
    let held = false;
    const spy = vi.spyOn(RunRuntime, 'start').mockImplementation((document, options) => {
      const real = original(document, options);
      const ready = real.ready;
      const gate = new Promise<void>((resolve) => { release = resolve; });
      held = true;
      Object.defineProperty(real, 'ready', { value: gate.then(() => ready) });
      return real;
    });
    // A republish that moves a part and publishes another mechanism, so
    // the run restarts and the call awaits the new program's start.
    const moved = JSON.parse(DOCUMENTS['touched.json']);
    moved.program.identity = `${moved.program.identity}-republished`;
    moved.root.children[0].operations = [['t', ['0', '0', '9.0']], ['r', '120', [1, 1, 1]]];
    bench.documents.set('touched.json', JSON.stringify(moved));
    const renders = bench.renders;
    let returned = false;
    const call = viewer.manifestChanged().then(() => { returned = true; });
    await settle();
    expect(held, 'the new program\'s start was not reached').toBe(true);
    expect(spy).toHaveBeenCalledTimes(1);
    expect(returned).toBe(false);
    expect(bench.renders, 'the call drew before its program started').toBe(renders);
    const between = await counted(() => frames(1));
    expect(between.draws, 'the frame while the new program starts').toBe(1);
    expectDrawn();
    release();
    await call;
    expect(returned).toBe(true);
    expect(bench.renders).toBeGreaterThan(renders + 1);
    expectDrawn();
    await expectStill(10);
  });
});

// ---------------------------------------------------------------------
// The constants recorded on the base (`56de33dd`), before any source
// change, from the lines this file prints as `RECORDED <name> <json>`
// (evidence.md, "Constants recorded on the base"). Never regenerated.

const RECORDED: Record<string, unknown> = {
  'W1.clock':
    {"first":0.016,"second":0.036000000000000004},
  'W1.press':
    {"landedOnFrame":14,"originFrames":13},
  'W1.ramp':
    {"landedOnFrame":32,"elapsedMs":512,"value":5},
  'M1':
    [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1]],
  'M2':
    [[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2]],
  'M3':
    [[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1]],
  'M4':
    [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1]],
  'M5':
    [[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1]],
  'M6':
    [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]],
  // Recorded on the base (56de33dd) in review, on a clean checkout.
  'M7':
    [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]],
  'O1':
    [["setTime",1],["setView",1],["setDriver",1],["setDriver (colour)",1],["setVisible off",1],["setVisible on",1],["highlight",1],["put-back",1],["observer",0],["webglcontextrestored",0],["visibilitychange",0],["machine().move",1],["machine().move again",1],["machine().restore",1],["machine().reset",1],["setTime",1],["observer",0]],
};

/** Print what was measured, then require the constant recorded on the
 * base. */
function expectRecorded(name: string, measured: unknown): void {
  console.log(`RECORDED ${name} ${JSON.stringify(measured)}`);
  expect(RECORDED[name], `no constant recorded for ${name}`).toBeDefined();
  expect(measured).toEqual(RECORDED[name]);
}

function busy(): boolean {
  return container.querySelector('[aria-busy="true"]') !== null;
}

function matrixOf(path: number[]): number[] {
  const scene = bench.scene as THREE.Scene;
  let node = scene.children.find((child) => child instanceof THREE.Group) as THREE.Object3D;
  for (const index of path) {
    node = node.children.filter((child) => child instanceof THREE.Group)[index];
  }
  node.updateWorldMatrix(true, false);
  return [...node.matrixWorld.elements];
}

// ---------------------------------------------------------------------
// W1. Still frames lose and double no time.

describe('W1: still frames take no time from a motion and add none to it', () => {
  it('the clock\'s first played frame after sixty still frames advances by that frame only', async () => {
    const viewer = await rested('regulator.json');
    await frames(60, 16);
    const machine = viewer.machine()!;
    machine.setClockPlaying(true);
    await frames(1, 16);
    const first = machine.state().time;
    await frames(1, 20);
    const second = machine.state().time;
    machine.setClockPlaying(false);
    expectRecorded('W1.clock', { first, second });
  });

  it('a drawn press after sixty still frames stands at its origin first and lands when its duration has passed', async () => {
    const viewer = await rested('clocked.json');
    await frames(60, 16);
    const origin = matrixOf([0]);
    viewer.machine()!.trigger('Press');
    const poses: Array<{ busy: boolean; atOrigin: boolean }> = [];
    for (let i = 0; i < 40 && (i === 0 || poses[i - 1].busy); i += 1) {
      await frames(1, 16);
      poses.push({ busy: busy(), atOrigin: matrixOf([0]).every((v, j) => Object.is(v, origin[j])) });
    }
    expect(poses[0].atOrigin, 'the first frame of the drawing').toBe(true);
    expectRecorded('W1.press', {
      landedOnFrame: poses.findIndex((one) => !one.busy) + 1,
      originFrames: poses.filter((one) => one.atOrigin).length,
    });
  });

  it('a ramp across still frames lands on the frame the clock reaches its end', async () => {
    const viewer = await rested('instructed.json');
    await frames(60, 16);
    const triggered = bench.now;
    const handle = viewer.trigger('Slide');
    let landedAt: number | null = null;
    void handle.done.then(() => { landedAt = bench.now; });
    let frame = 0;
    while (landedAt === null && frame < 100) {
      await frames(1, 16);
      frame += 1;
    }
    expectRecorded('W1.ramp', { landedOnFrame: frame, elapsedMs: (landedAt ?? 0) - triggered,
                                value: viewer.driver('x') });
  });
});

// ---------------------------------------------------------------------
// M1 to M6. During motion, every frame as on the base.

describe('M1 to M6: while something moves every frame draws and updates as on the base, and nothing after', () => {
  it('M1: a ramp of an integer driver slow enough that some frames move no value', async () => {
    const viewer = await rested('posed.json', { autoplay: false });
    const handle = viewer.trigger('Advance');
    let landed = false;
    void handle.done.then(() => { landed = true; });
    const counts = await perFrame(200, 16, () => landed);
    expect(landed).toBe(true);
    expectRecorded('M1', counts);
    await expectStill(10);
  });

  // Added in review. A fault planted there, the frame a motion stops in
  // drawn only if something else called for it, passed M1 to M6: in each
  // of them the last frame moves something, which is drawn anyway. A
  // ramp to the value its driver already has moves nothing on any frame,
  // the one it lands on included.
  it('M7: a ramp that moves nothing is drawn on every frame, the one it lands on included', async () => {
    const viewer = await rested('posed.json', { autoplay: false });
    const first = viewer.trigger('Advance');
    let landed = false;
    void first.done.then(() => { landed = true; });
    await perFrame(200, 16, () => landed);
    expect(landed).toBe(true);
    const second = viewer.trigger('Advance');
    landed = false;
    void second.done.then(() => { landed = true; });
    const counts = await perFrame(200, 16, () => landed);
    expect(landed).toBe(true);
    expect(counts.every(([, named]) => named === 0), 'no frame moves a driver').toBe(true);
    expectRecorded('M7', counts);
    await expectStill(10);
  });

  it('M2: the timeline played on spinner, and paused', async () => {
    await rested('spinner.json', { autoplay: false });
    const play = container.querySelector<HTMLButtonElement>('.animation-controls button')!;
    play.click();
    const counts = await perFrame(20);
    play.click();
    expectRecorded('M2', counts);
    await expectStill(10);
  });

  it('M3: the clock played on regulator, and paused', async () => {
    const viewer = await rested('regulator.json');
    viewer.machine()!.setClockPlaying(true);
    const counts = await perFrame(20);
    viewer.machine()!.setClockPlaying(false);
    expectRecorded('M3', counts);
    await expectStill(10);
  });

  it('M4: a drawn press of an instruction on an integer input', async () => {
    const viewer = await rested('clocked.json');
    viewer.machine()!.trigger('Turn');
    expect(busy()).toBe(true);
    const counts = await perFrame(200, 16, () => !busy());
    expect(busy()).toBe(false);
    expectRecorded('M4', counts);
    await expectStill(10);
  });

  it('M5: a run started on touched, and paused', async () => {
    const viewer = await rested('touched.json');
    const run = viewer.run()!;
    run.start();
    run.trigger('Add one').catch(() => undefined);
    const counts = await perFrame(30);
    run.pause();
    await settle();
    expectRecorded('M5', counts);
    await expectStill(10);
  });

  it('M6: a press held on a part of touched without moving, and let go', async () => {
    const viewer = await rested('touched.json');
    await frames(1);
    const control = viewer.controls().find((one) => one.point !== null)!;
    const at = controlPoint(viewer, control.name);
    pointer('pointerdown', at.x, at.y);
    const held = await perFrame(10);
    canvas().dispatchEvent(new PointerEvent('pointercancel', { bubbles: true, pointerId: 1 }));
    const after = await perFrame(1);
    expect(viewer.run()!.running()).toBe(false);
    expectRecorded('M6', [...held, ...after]);
    await expectStill(10);
  });
});

// ---------------------------------------------------------------------
// O1. On demand is unchanged.

describe('O1: an on-demand viewer draws exactly where its calls draw', () => {
  it('a posed and a clocked document: the base\'s draws per call, no loop, nothing on a resize or an event', async () => {
    const measured: Array<[string, number]> = [];
    const step = async (name: string, action: () => Promise<void> | void) => {
      measured.push([name, (await counted(action)).draws]);
    };
    const ON_DEMAND: ViewerOptions = { renderMode: 'on-demand', animation: 'external',
                                       autoplay: false, driverControls: 'none',
                                       partControls: 'none' };
    const posed = await open('state-color.json', ON_DEMAND);
    await step('setTime', () => posed.setTime(0.5));
    await step('setView', () => posed.setView({ camera: [80, -60, 50], target: [0, 0, 0] }));
    await step('setDriver', () => posed.setDriver('independent', 2));
    await step('setDriver (colour)', () => posed.setDriver('powered', 1));
    await step('setVisible off', () => posed.setVisible(['glass'], false));
    await step('setVisible on', () => posed.setVisible(['glass'], true));
    let restore: () => void = () => undefined;
    await step('highlight', () => { restore = posed.highlight([['glass']], { others: 'dim' }); });
    await step('put-back', () => restore());
    bench.width = 500;
    await step('observer', () => observe());
    await step('webglcontextrestored', () => { canvas().dispatchEvent(new Event('webglcontextrestored')); });
    await step('visibilitychange', () => { document.dispatchEvent(new Event('visibilitychange')); });
    posed.dispose();
    const clocked = await open('regulator.json', ON_DEMAND);
    const machine = clocked.machine()!;
    await step('machine().move', () => { machine.move('time', { by: 0.25 }); });
    const snapshot = machine.snapshot();
    await step('machine().move again', () => { machine.move('time', { by: 0.5 }); });
    await step('machine().restore', () => { machine.restore(snapshot); });
    await step('machine().reset', () => { machine.reset(); });
    await step('setTime', () => clocked.setTime(0.5));
    bench.width = 420;
    await step('observer', () => observe());
    expect(bench.loopCalls.some((one) => typeof one === 'function'),
           'an on-demand viewer was given an animation loop').toBe(false);
    expectRecorded('O1', measured);
  });
});

// ---------------------------------------------------------------------
// G1. Generated sequences of host and maker actions.

/** mulberry32: a small seeded generator, so a failing sequence is
 * reproduced from its seed. */
function generator(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

interface Generated {
  viewer: ViewerHandle;
  name: string;
  random: () => number;
  pick<T>(items: readonly T[]): T;
  restoreHighlight: (() => void) | null;
  grown: number;
  rest: unknown;
}

type AssemblyEntry = { path: string[]; model: boolean };

function paths(viewer: ViewerHandle): AssemblyEntry[] {
  const found: AssemblyEntry[] = [];
  const visit = (node: { path: string[]; model: boolean; children: unknown[] }) => {
    if (node.path.length > 0) found.push({ path: node.path, model: node.model });
    (node.children as typeof node[]).forEach(visit);
  };
  visit(viewer.assembly() as unknown as { path: string[]; model: boolean; children: unknown[] });
  return found;
}

function served(g: Generated): Record<string, unknown> {
  return JSON.parse(bench.documents.get(g.name)!) as Record<string, unknown>;
}

type DocNode = { name: string; color?: unknown; operations: unknown[]; model?: string;
                 children?: DocNode[]; markings?: Array<{ model: string }> };

function nodesOf(root: DocNode): DocNode[] {
  const all: DocNode[] = [];
  const visit = (node: DocNode) => { all.push(node); (node.children ?? []).forEach(visit); };
  visit(root);
  return all.slice(1);
}

function hex(random: () => number): string {
  return `#${Math.floor(random() * 0xffffff).toString(16).padStart(6, '0')}`;
}

/** Frames until no ramp and no drawing is left, each frame checked by D.
 * A drawing is waited for by its declared duration, not by its button's
 * `aria-busy`: a panel rebuilt for another focus shows no instruction
 * button to carry it. */
async function untilStill(_g: Generated, limit = 200): Promise<void> {
  for (let i = 0; i < limit; i += 1) {
    if (rampsDone && !busy() && bench.now >= drawingUntil) return;
    await frames(1, 16);
    expectDrawn();
  }
  throw new Error('a motion did not land');
}

let rampsDone = true;
let drawingUntil = 0;

const COMMON: Array<[string, (g: Generated) => Promise<void> | void]> = [
  ['setView', (g) => {
    const r = () => (g.random() - 0.5) * 400;
    const view: { camera: [number, number, number]; target: [number, number, number];
                  up?: [number, number, number] } = {
      camera: [r() + 60, r() + 60, r() + 60], target: [r() / 20, r() / 20, r() / 20],
    };
    if (g.random() < 0.3) view.up = g.pick([[0, 0, 1], [0, 1, 0], [1, 0, 0]] as Array<[number, number, number]>);
    g.viewer.setView(view);
  }],
  ['wheel', (g) => { wheel(g.random() < 0.5 ? -120 : 120); }],
  ['drag', (g) => {
    const x = 50 + g.random() * 700, y = 50 + g.random() * 500;
    pointer('pointerdown', x, y);
    pointer('pointermove', x + (g.random() - 0.5) * 80, y + (g.random() - 0.5) * 80);
    pointer('pointerup', x, y, { buttons: 0 });
  }],
  ['resize', (g) => {
    if (g.random() < 0.05) { bench.width = 0; bench.height = 0; } else {
      bench.width = 200 + Math.floor(g.random() * 800);
      bench.height = 150 + Math.floor(g.random() * 600);
    }
    observe();
  }],
  ['highlight', (g) => {
    if (g.restoreHighlight !== null) { g.restoreHighlight(); g.restoreHighlight = null; return; }
    const path = g.pick(paths(g.viewer)).path;
    g.restoreHighlight = g.viewer.highlight([path], {
      others: g.pick(['keep', 'dim', 'ghost'] as const), color: hex(g.random),
    });
  }],
  ['setVisible', (g) => {
    const path = g.pick(paths(g.viewer)).path;
    g.viewer.setVisible(path, g.random() < 0.5);
  }],
  ['setRoot', (g) => {
    g.viewer.setRoot(g.random() < 0.4 ? null : g.pick(paths(g.viewer)).path);
  }],
  ['setTime', (g) => { g.viewer.setTime(g.random()); }],
  ['blur', () => { window.dispatchEvent(new Event('blur')); }],
  ['reload', async (g) => { await g.viewer.reload(); }],
  ['manifestChanged', async (g) => {
    const document = served(g);
    const nodes = nodesOf(document.root as DocNode);
    const kind = g.pick(['recolour', 'move', 'grow', 'shrink']);
    if (kind === 'recolour') {
      const coloured = nodes.filter((node) => typeof node.color === 'string');
      if (coloured.length > 0) g.pick(coloured).color = hex(g.random);
    } else if (kind === 'move') {
      const node = g.pick(nodes);
      node.operations = [...node.operations,
        ['t', [String(Math.round((g.random() - 0.5) * 20)), '0', '0']]];
    } else if (kind === 'grow') {
      g.grown += 1;
      const root = document.root as DocNode;
      root.children = [...(root.children ?? []), leaf(`grown${g.grown}`,
        [['t', ['0', '0', String(g.grown * 5)]]], { color: hex(g.random) }) as DocNode];
    } else {
      const root = document.root as DocNode;
      const index = (root.children ?? []).findIndex((child) => child.name.startsWith('grown'));
      if (index >= 0) root.children!.splice(index, 1);
    }
    bench.documents.set(g.name, JSON.stringify(document));
    await g.viewer.manifestChanged();
  }],
  ['artifactChanged', async (g) => {
    const models = nodesOf(served(g).root as DocNode).flatMap((node) => [
      ...(node.model ? [node.model] : []), ...(node.markings ?? []).map((one) => one.model)]);
    await g.viewer.artifactChanged(g.pick(models));
  }],
  ['webglcontextrestored', () => { canvas().dispatchEvent(new Event('webglcontextrestored')); }],
  ['visibilitychange', () => { document.dispatchEvent(new Event('visibilitychange')); }],
];

const POSED_STEPS: Array<[string, (g: Generated) => Promise<void> | void]> = [
  ['setDriver', (g) => {
    const id = g.pick(['x', 'n', 'lift', 'powered']);
    g.viewer.setDriver(id, id === 'n' ? Math.floor(g.random() * 10) : g.random() * (id === 'powered' ? 1 : 10));
  }],
  ['trigger', async (g) => {
    const handle = g.viewer.trigger(g.pick(['Slide', 'Advance']));
    rampsDone = false;
    void handle.done.then(() => { rampsDone = true; });
    await untilStill(g);
  }],
];

const MACHINE_STEPS = (input: string, integer: boolean): Array<[string, (g: Generated) => Promise<void> | void]> => [
  ['machine().move', (g) => {
    const by = integer ? 1 + Math.floor(g.random() * 3) : g.random();
    g.viewer.machine()!.move(input, { by });
  }],
  ['machine().restore', (g) => { g.viewer.machine()!.restore(g.rest as never); }],
  ['machine().reset', (g) => { g.viewer.machine()!.reset(); }],
];

const DOCUMENT_STEPS: Record<string, Array<[string, (g: Generated) => Promise<void> | void]>> = {
  'posed.json': POSED_STEPS,
  'regulator.json': [
    ...MACHINE_STEPS('time', false),
    ['clock played', (g) => { g.viewer.machine()!.setClockPlaying(true); }],
    ['clock paused', (g) => { g.viewer.machine()!.setClockPlaying(false); }],
  ],
  'clocked.json': [
    ...MACHINE_STEPS('n', true),
    ['machine().trigger', async (g) => {
      const name = g.pick(['Press', 'Turn']);
      g.viewer.machine()!.trigger(name);
      // Its first frame is the next one, at most 40 ms away.
      drawingUntil = Math.max(drawingUntil,
        bench.now + CLOCKED.instructions[name as 'Press' | 'Turn'].duration * 1000 + 100);
      if (g.random() < 0.7) await untilStill(g);
    }],
  ],
  'touched.json': [
    ['hover', (g) => {
      const reachable = g.viewer.controls().filter((one) => one.point !== null);
      if (reachable.length === 0) return;
      const at = g.pick(reachable).point!;
      pointer('pointermove', at.x, at.y, { buttons: 0 });
    }],
    ['hover end', () => { pointer('pointermove', 1, 1, { buttons: 0 }); }],
    ['run started', (g) => { g.viewer.run()!.start(); }],
    ['run paused', (g) => { g.viewer.run()!.pause(); }],
    ['run trigger', (g) => {
      // A second command on an input another one owns is refused by the
      // run, which is the run's answer and not this bench's concern.
      g.viewer.run()!.trigger(g.pick(['Add one', 'Add ten', 'Add hundred']))
        .catch(() => undefined);
    }],
  ],
};

const GENERATED_DOCUMENTS = ['posed.json', 'regulator.json', 'clocked.json', 'touched.json'];

async function generatedSequence(seed: number): Promise<string[]> {
  const name = GENERATED_DOCUMENTS[seed % GENERATED_DOCUMENTS.length];
  bench.documents = new Map(Object.entries(DOCUMENTS));
  bench.width = 800;
  bench.height = 600;
  rampsDone = true;
  drawingUntil = 0;
  const random = generator(seed);
  const viewer = await rested(name, name === 'posed.json' ? { autoplay: false } : {});
  const g: Generated = {
    viewer, name, random, pick: (items) => items[Math.floor(random() * items.length)],
    restoreHighlight: null, grown: 0, rest: viewer.machine()?.snapshot(),
  };
  const vocabulary = [...COMMON, ...DOCUMENT_STEPS[name]];
  const log: string[] = [];
  for (let step = 0; step < 30; step += 1) {
    const [label, action] = g.pick(vocabulary);
    log.push(label);
    await action(g);
    const count = 1 + Math.floor(random() * 3);
    for (let i = 0; i < count; i += 1) {
      await frames(1, 1 + Math.floor(random() * 40));
      try { expectDrawn(); } catch (error) {
        throw new Error(`seed ${seed} (${name}) after ${log.join(', ')}: ${String(error)}`);
      }
    }
  }
  // Every motion stopped, as a maker leaves the page.
  const machine = viewer.machine();
  if (machine !== null && machine.clock() !== null) machine.setClockPlaying(false);
  viewer.run()?.pause();
  await settle();
  await untilStill(g);
  await frames(1);
  expectDrawn();
  const tail = await counted(() => frames(20));
  expect({ draws: tail.draws, updates: tail.updates },
         `seed ${seed} (${name}), idle tail after ${log.join(', ')}`)
    .toEqual({ draws: 0, updates: 0 });
  opened.splice(0).forEach((one) => one.dispose());
  container.replaceChildren();
  return log;
}

describe('G1: generated sequences of host and maker actions', () => {
  it('200 seeded sequences of 30 steps: D matches after every frame, and twenty still frames after each draw and update nothing', async () => {
    const failures: string[] = [];
    for (let seed = 1; seed <= 200; seed += 1) {
      try {
        await generatedSequence(seed);
      } catch (error) {
        failures.push(String(error).slice(0, 600));
        opened.splice(0).forEach((one) => one.dispose());
        container.replaceChildren();
      }
    }
    const tails = failures.filter((one) => one.includes('idle tail')).length;
    console.log(`G1: ${failures.length} of 200 sequences failed, ${tails} of them at the idle tail`);
    expect(failures.length, failures.slice(0, 5).join('\n\n')).toBe(0);
  }, 600_000);
});
