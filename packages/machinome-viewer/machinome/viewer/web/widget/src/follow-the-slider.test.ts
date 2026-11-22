/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The bench of OpenSpec `follow-the-slider-as-it-is-dragged`, design
// Decision 11: the REAL `mount()` in jsdom, as `draw-on-change.test.ts`
// mounts it (copied, so that no existing test file changes): three.js's
// `WebGLRenderer` replaced by a counting renderer whose `render` does to
// the scene graph what three.js 0.156.1's does before it draws, its
// animation loop kept and driven here frame by frame. Two modules pass
// through with a counter: the clocked machine, whose every `move` is
// logged with the frame it was made in (the panel's requests do not go
// through the mount handle, so the handle cannot count them), and
// `clockedControls`, whose `clockedControlLayer` is the first step of a
// rebuild of the panel.
//
// A drag is dispatched on the REAL slider the panel built: `PointerEvent`s
// with a pointer id, the value set as the browser sets it, and `input` and
// `change` dispatched in the order the browsers recorded in design
// Decision 1 dispatch them. The slider is focused at its `pointerdown`, as
// the browsers do. jsdom has no drag of its own: what this proves is the
// rule given an order of events; `tests/test_follow_the_slider.py` holds
// the order and the result in Chromium.
//
// Constants named in RECORDED were printed on the base (`f6119628`,
// planning commit `b1729544`) before any source change and are written
// here as they printed (evidence.md); they are not regenerated.

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
import { formatDisplay } from './controls';
import { bindingTable } from './bindings';
import { loadClocked } from './clocked/document';
import type { ClockedDocument } from './clocked/document';
import type { ClockedMachine, ClockedSnapshot } from './clocked/machine';
import type { Manifest } from './types';

// ---------------------------------------------------------------------
// The bench's shared state, reachable from the mocked modules.

type Reading = Array<[string, unknown]>;

/** One entry of the bench's log, in the order things happened. */
interface Entry {
  kind: 'move' | 'restore' | 'reset' | 'layer';
  /** Which machine of the test, in the order they were built. */
  machine: number;
  id: string;
  request: { by?: number; to?: number };
  /** Made inside an animation frame, and which one. */
  inFrame: boolean;
  frame: number;
  origin?: number;
  refused?: boolean;
  /** The machine's bank after the call, refused or not. */
  after?: Record<string, number>;
  /** Pictures rendered while the request ran. */
  renders?: number;
}

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
  log: [] as unknown[],
  machines: [] as unknown[],
  layers: 0,
  frame: 0,
  inFrame: false,
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

// Every machine the viewer builds, passed through, its `move`, `restore`
// and `reset` logged. `trigger` calls `this.move`, so an instruction's
// request is logged too.
vi.mock('./clocked/machine', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./clocked/machine')>();
  return {
    ...actual,
    clockedMachine: (...args: Parameters<typeof actual.clockedMachine>) => {
      const made = actual.clockedMachine(...args);
      const index = bench.machines.length;
      bench.machines.push(made);
      const move = made.move;
      const restore = made.restore;
      const reset = made.reset;
      const base = (kind: Entry['kind'], id: string,
                    request: Entry['request']): Entry => ({
        kind, machine: index, id, request: { ...request },
        inFrame: bench.inFrame, frame: bench.frame,
      });
      made.move = (id, request) => {
        const entry = base('move', id, request);
        bench.log.push(entry);
        const renders = bench.renders;
        try {
          const answered = move(id, request);
          entry.origin = answered.origin;
          return answered;
        } catch (error) {
          entry.refused = true;
          throw error;
        } finally {
          entry.after = made.state();
          entry.renders = bench.renders - renders;
        }
      };
      made.restore = (state) => {
        bench.log.push(base('restore', '', {}));
        restore(state);
      };
      made.reset = () => {
        bench.log.push(base('reset', '', {}));
        reset();
      };
      return made;
    },
  };
});

// The panel's rebuild, counted at its first step.
vi.mock('./clockedControls', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./clockedControls')>();
  return {
    ...actual,
    clockedControlLayer: (...args: Parameters<typeof actual.clockedControlLayer>) => {
      bench.layers += 1;
      bench.log.push({ kind: 'layer', machine: -1, id: '', request: {},
                       inFrame: bench.inFrame, frame: bench.frame });
      return actual.clockedControlLayer(...args);
    },
  };
});

const { clockedMachine: actualMachine } = await vi.importActual<
  typeof import('./clocked/machine')>('./clocked/machine');

// ---------------------------------------------------------------------
// Documents, hand-written (design Decision 11).

const FLOAT = (range: [number, number] | null, unit: string | null = null,
               extra: Record<string, unknown> = {}) => ({
  default: 0, range, unit, dtype: null, scale: null, ...extra,
});
const INT = (range: [number, number] | null = null) => ({
  default: 0, range, unit: null, dtype: 'int', scale: null,
});
const leaf = (name: string, operations: unknown[]) => ({
  name, type: 'LeafNode', color: '#8899aa', mtime: 1, operations,
  model: `models/${name}.stl`,
});
const assembly = (name: string, children: unknown[]) => ({
  name, type: 'AssemblyNode', color: null, mtime: 1, operations: [], children,
});

/** FOLLOW: a float input on [0, 2] with a `floor` commit writing `count`
 * and a stop at 1.5, a whole-number input, an input whose design units
 * are twice its native ones, and a free input; two instructions; every
 * part posed by translations only, so that a part's world matrix reads a
 * bank value exactly. */
const FOLLOW = {
  format: 'machinome-export', version: 8, animation: { fps: 30, frames: 360 },
  drivers: {
    press: FLOAT([0, 2], 'mm'), wheel: INT([0, 9]),
    scaled: FLOAT([0, 10], null, { scale: 2 }), open: FLOAT([0, 1]),
  },
  states: { count: INT() },
  instructions: {
    Push: { by: { press: 0.5 }, duration: 0.5 },
    Turn: { by: { wheel: 3 }, duration: 1 },
  },
  bindings: [],
  clocked: {
    identity: 'follow-the-slider', clock: null as string | null, own: '_own',
    commits: [{
      sources: ['press', 'count'], targets: ['count'],
      at: { primitive: 'floor', level: 'press' }, law: ['(count + 1)'],
      shapes: { press: 'affine' }, description: '(press, count) commits count',
      stated_by: 'Follow',
    }],
    bounds: [{
      coordinate: 'block.travel', side: 'high', unit: 'mm', value: 'press',
      bound: 1.5, plan: null, shapes: { press: { level: 'affine', jumps: [] } },
      node: 'Block', joint: 'travel', description: "the high bound of 'block.travel'",
    }],
    limits: { crossing_tolerance: 1e-12, max_crossings: 1000 },
  },
  root: assembly('root', [
    leaf('block', [['t', ['press', '0', '0']]]),
    leaf('dial', [['t', ['wheel', '0', '0']]]),
    leaf('counter', [['t', ['count', 'scaled', '0']]]),
    leaf('lid', [['t', ['open', '0', '0']]]),
  ]),
};

/** FOLLOW with a clock declared. */
const FOLLOW_CLOCK = {
  ...FOLLOW,
  clocked: { ...FOLLOW.clocked, identity: 'follow-the-slider-clock', clock: 'time' },
};

/** FOLLOW published as a version 14 document: a republish of version 8
 * keeps the machine whatever its identity (`manifestChanged`, which calls
 * `startMachine` for version 14 only), so a machine REPLACED by a
 * republish needs this one (evidence.md). */
const FOLLOW_14 = { ...FOLLOW, version: 14 };

/** FOLLOW with `Push` declared at no duration (added in review): a
 * gesture on `press` then has a tempo of zero seconds, so a request the
 * viewer would draw starts no drawing and is published at once
 * (`clockedRequest`, `publishJudged`). A press on the track is such a
 * request, and it rebuilds nothing. */
const FOLLOW_INSTANT = {
  ...FOLLOW,
  instructions: { ...FOLLOW.instructions, Push: { by: { press: 0.5 }, duration: 0 } },
  clocked: { ...FOLLOW.clocked, identity: 'follow-the-slider-instant' },
};

/** FINE: a commit at every tenth, at most three crossings a request. */
const FINE = {
  format: 'machinome-export', version: 8, animation: { fps: 30, frames: 360 },
  drivers: { fine: FLOAT([0, 1]) },
  states: { teeth: INT() },
  instructions: {},
  bindings: [],
  clocked: {
    identity: 'follow-the-slider-fine', clock: null, own: '_own',
    commits: [{
      sources: ['fine', 'teeth'], targets: ['teeth'],
      at: { primitive: 'floor', level: '(fine * 10)' }, law: ['(teeth + 1)'],
      shapes: { fine: 'affine' }, description: '(fine, teeth) commits teeth',
      stated_by: 'Fine',
    }],
    bounds: [],
    limits: { crossing_tolerance: 1e-12, max_crossings: 3 },
  },
  root: assembly('root', [leaf('plate', [['t', ['fine', 'teeth', '0']]])]),
};

const DOCUMENTS: Record<string, string> = {
  'follow.json': JSON.stringify(FOLLOW),
  'follow-clock.json': JSON.stringify(FOLLOW_CLOCK),
  'follow-14.json': JSON.stringify(FOLLOW_14),
  'follow-instant.json': JSON.stringify(FOLLOW_INSTANT),
  'fine.json': JSON.stringify(FINE),
};

/** Where each id of a document is posed: [part index, matrix element]. */
const POSES: Record<string, Record<string, [number, number]>> = {
  'follow.json': {
    press: [0, 12], wheel: [1, 12], count: [2, 12], scaled: [2, 13], open: [3, 12],
  },
  'follow-clock.json': {
    press: [0, 12], wheel: [1, 12], count: [2, 12], scaled: [2, 13], open: [3, 12],
  },
  'follow-14.json': {
    press: [0, 12], wheel: [1, 12], count: [2, 12], scaled: [2, 13], open: [3, 12],
  },
  'follow-instant.json': {
    press: [0, 12], wheel: [1, 12], count: [2, 12], scaled: [2, 13], open: [3, 12],
  },
  'fine.json': { fine: [0, 12], teeth: [0, 13] },
};
const SCALES: Record<string, number> = { scaled: 2 };

// ---------------------------------------------------------------------
// D, the detector (copied from `draw-on-change.test.ts`).

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

/** `count` animation frames, `ms` milliseconds apart. */
async function frames(count: number, ms = 16): Promise<void> {
  for (let i = 0; i < count; i += 1) {
    bench.now += ms;
    const loop = bench.loop;
    if (typeof loop !== 'function') throw new Error('no animation loop installed');
    bench.frame += 1;
    bench.inFrame = true;
    try { loop(bench.now); } finally { bench.inFrame = false; }
    await settle();
  }
}

function observe(): void {
  for (const observer of bench.observers) {
    if (observer.connected) observer.callback([], observer.self);
  }
}

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

async function expectStill(count = 10): Promise<void> {
  const tail = await counted(() => frames(count));
  expect({ draws: tail.draws, updates: tail.updates }).toEqual({ draws: 0, updates: 0 });
}

const log = (): Entry[] => bench.log as Entry[];
const requests = (): Entry[] => log().filter((one) => one.kind === 'move');
/** The requests made since `mark`, as `[id, request]`. */
const askedSince = (mark: number, id?: string): Array<[string, Entry['request']]> =>
  requests().slice(mark).filter((one) => id === undefined || one.id === id)
    .map((one) => [one.id, one.request]);

function panel(): HTMLElement | null {
  return container.querySelector<HTMLElement>('.clocked-controls');
}
function slider(id: string): HTMLInputElement {
  const found = container.querySelector<HTMLInputElement>(`.clocked-slider[data-input="${id}"]`);
  if (found === null) throw new Error(`no slider for ${id}`);
  return found;
}
function field(id: string): HTMLInputElement {
  return container.querySelector<HTMLInputElement>(`.clocked-value[data-input="${id}"]`)!;
}
function outcomeLine(id: string): HTMLElement {
  return container.querySelector<HTMLElement>(`.clocked-outcome[data-input="${id}"]`)!;
}
function readout(id: string): HTMLElement {
  return container.querySelector<HTMLElement>(`.clocked-readout-value[data-readout="${id}"]`)!;
}

/** A pointer event of pointer 1 (the mouse), unless `init` says other. */
function pointerOn(target: EventTarget, type: string, init: PointerEventInit = {}): void {
  const moving = type === 'pointermove';
  const up = type === 'pointerup' || type === 'pointercancel'
    || type === 'lostpointercapture';
  target.dispatchEvent(new PointerEvent(type, {
    bubbles: true, cancelable: true, composed: true, pointerId: 1,
    pointerType: 'mouse', button: moving ? -1 : 0, buttons: up ? 0 : 1,
    isPrimary: true, ...init,
  }));
}

/** A press on a slider, focused as the browsers focus it. */
function pressOn(target: HTMLInputElement, init: PointerEventInit = {}): void {
  pointerOn(target, 'pointerdown', init);
  target.focus();
}

/** The browser moving the thumb: its value set, and `input`. */
function valueTo(target: HTMLInputElement, value: number): void {
  target.value = String(value);
  target.dispatchEvent(new Event('input', { bubbles: true }));
}

/** A step of a dragged thumb: a `pointermove`, then the value. */
function dragTo(target: HTMLInputElement, value: number, init: PointerEventInit = {}): void {
  pointerOn(target, 'pointermove', init);
  valueTo(target, value);
}

function change(target: HTMLInputElement): void {
  target.dispatchEvent(new Event('change', { bubbles: true }));
}

/** A release in one task: `pointerup`, then the release's `change`. */
function letGo(target: HTMLInputElement, init: PointerEventInit = {}): void {
  pointerOn(target, 'pointerup', init);
  change(target);
}

/** The part groups of the shown tree, in document order. */
function parts(): THREE.Object3D[] {
  const scene = bench.scene as THREE.Scene;
  const root = scene.children.find((child) => child instanceof THREE.Group) as THREE.Group;
  return root.children.filter((child) => child instanceof THREE.Group);
}

/** The value `id` is posed at, read from its part's world matrix. */
function modelValue(document: string, id: string): number {
  const [part, element] = POSES[document][id];
  const group = parts()[part];
  group.updateWorldMatrix(true, false);
  return group.matrixWorld.elements[element];
}

/** Every write of an element's text, in order. */
function writesOf(element: Element): { texts(): string[] } {
  const texts: string[] = [];
  const take = (records: MutationRecord[]) => {
    for (const record of records) {
      if (record.type !== 'childList') continue;
      texts.push([...record.addedNodes].map((node) => node.textContent ?? '').join(''));
    }
  };
  const observer = new MutationObserver(take);
  observer.observe(element, { childList: true, characterData: true, subtree: true });
  return { texts: () => { take(observer.takeRecords()); return [...texts]; } };
}

/** `document` as the machine `start` was taken over: G1's republishes
 * change a document's identity and nothing else. */
function sameMachine(document: object, start: ClockedSnapshot): object {
  const copy = JSON.parse(JSON.stringify(document)) as { clocked: { identity: string } };
  copy.clocked.identity = start.identity;
  return copy;
}

function freshMachine(document: object): ClockedMachine {
  return actualMachine(loadClocked(document as unknown as ClockedDocument, 'x.json',
    bindingTable(document as unknown as Manifest, 'x.json')));
}

/** A fresh machine of `document`, restored to `start`, replaying
 * `asked`; its bank. */
function replayed(document: object, start: ClockedSnapshot,
                  asked: ReadonlyArray<[string, Entry['request']]>): Record<string, number> {
  const fresh = freshMachine(sameMachine(document, start));
  fresh.restore(start);
  for (const [id, request] of asked) {
    try { fresh.move(id, request); } catch { /* refused: the bank stands */ }
  }
  return fresh.state();
}

/** Frames until two in a row draw nothing (a drawing draws every frame
 * it runs, ADR-080), each checked by D. */
async function untilRest(limit = 400): Promise<void> {
  let quiet = 0;
  for (let i = 0; i < limit; i += 1) {
    const one = await counted(() => frames(1));
    if (one.draws > 0) expectDrawn();
    quiet = one.draws === 0 ? quiet + 1 : 0;
    if (quiet >= 2) return;
  }
  throw new Error('the page did not come to rest');
}

/** The field's reading of `id` per frame, until the page rests. */
async function pathUntilRest(id: string, limit = 400): Promise<number[]> {
  const path: number[] = [];
  let quiet = 0;
  for (let i = 0; i < limit; i += 1) {
    const one = await counted(() => frames(1));
    if (one.draws > 0) path.push(Number(field(id).value));
    quiet = one.draws === 0 ? quiet + 1 : 0;
    if (quiet >= 2) return path;
  }
  throw new Error('the page did not come to rest');
}

// ---------------------------------------------------------------------
// What the base showed, printed as `RECORDED <name> <json>` before any
// source change (evidence.md). Never regenerated.

const RECORDED: Record<string, unknown> = {
  'R6.click':
    {"asked":[["press",{"to":1.2}]],"path":[0,0.016,0.032,0.048,0.064,0.08,0.096,0.112,0.128,0.144,0.16,0.176,0.192,0.208,0.224,0.24,0.256,0.272,0.288,0.304,0.32,0.336,0.352,0.368,0.384,0.4,0.416,0.432,0.448,0.464,0.48,0.496,0.512,0.528,0.544,0.56,0.576,0.592,0.608,0.624,0.64,0.656,0.672,0.688,0.704,0.72,0.736,0.752,0.768,0.784,0.8,0.816,0.832,0.848,0.864,0.88,0.896,0.912,0.928,0.944,0.96,0.976,0.992,1.008,1.024,1.04,1.056,1.072,1.088,1.104,1.12,1.136,1.152,1.168,1.184,1.2]},
  'R17':
    {"during":["time","time","time"],"playingAfterFrames":true,"atChange":[["press",{"to":1.2}]],"layers":true,"replaced":true,"playing":false,"path":[0,0.016,0.032,0.048,0.064,0.08,0.096,0.112,0.128,0.144,0.16,0.176,0.192,0.208,0.224,0.24,0.256,0.272,0.288,0.304,0.32,0.336,0.352,0.368,0.384,0.4,0.416,0.432,0.448,0.464,0.48,0.496,0.512,0.528,0.544,0.56,0.576,0.592,0.608,0.624,0.64,0.656,0.672,0.688,0.704,0.72,0.736,0.752,0.768,0.784,0.8,0.816,0.832,0.848,0.864,0.88,0.896,0.912,0.928,0.944,0.96,0.976,0.992,1.008,1.024,1.04,1.056,1.072,1.088,1.104,1.12,1.136,1.152,1.168,1.184,1.2]},
  'R18':
    {"key":{"asked":[["press",{"to":1}]],"rebuilt":1,"replaced":true,"path":[0,0.016,0.032,0.048,0.064,0.08,0.096,0.112,0.128,0.144,0.16,0.176,0.192,0.208,0.224,0.24,0.256,0.272,0.288,0.304,0.32,0.336,0.352,0.368,0.384,0.4,0.416,0.432,0.448,0.464,0.48,0.496,0.512,0.528,0.544,0.56,0.576,0.592,0.608,0.624,0.64,0.656,0.672,0.688,0.704,0.72,0.736,0.752,0.768,0.784,0.8,0.816,0.832,0.848,0.864,0.88,0.896,0.912,0.928,0.944,0.96,0.976,0.992,1],"bank":{"press":1,"wheel":0,"scaled":0,"open":0,"count":1}},"input with no press":{"asked":[],"rebuilt":0,"replaced":false,"path":[],"bank":{"press":1,"wheel":0,"scaled":0,"open":0,"count":1}},"typed value":{"asked":[["wheel",{"to":4}]],"rebuilt":1,"replaced":true,"path":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4],"bank":{"press":1,"wheel":4,"scaled":0,"open":0,"count":1}},"nudge":{"asked":[["wheel",{"by":-1}]],"rebuilt":1,"replaced":true,"path":[4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,3],"bank":{"press":1,"wheel":3,"scaled":0,"open":0,"count":1}}},
  'O1':
    {"sliders":0,"measured":[["move press",1],["move wheel",1],["move past the stop",1],["restore",1],["reset",1]],"loop":false},
};

function expectRecorded(name: string, measured: unknown): void {
  console.log(`RECORDED ${name} ${JSON.stringify(measured)}`);
  expect(RECORDED[name], `no constant recorded for ${name}`).toBeDefined();
  expect(measured).toEqual(RECORDED[name]);
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
  bench.log = [];
  bench.machines = [];
  bench.layers = 0;
  bench.frame = 0;
  bench.inFrame = false;
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
  delete (document as unknown as Record<string, unknown>).hidden;
  opened.splice(0).forEach((viewer) => viewer.dispose());
  document.body.replaceChildren();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

// ---------------------------------------------------------------------
// R1 to R20.

const R1_STEPS = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4];

describe('R1 to R4: a dragged thumb is followed, one request a frame', () => {
  it('R1: a thumb drag is followed: one request a frame for its position, posed and drawn in that frame', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    const held = panel();
    pressOn(s);
    for (const position of R1_STEPS) {
      const mark = requests().length;
      dragTo(s, position);
      expect(askedSince(mark), `a request inside the input's task, at ${position}`).toEqual([]);
      const one = await counted(() => frames(1));
      expect(askedSince(mark), `the frame after the thumb reached ${position}`)
        .toEqual([['press', { to: position }]]);
      const bank = viewer.machine()!.state();
      expect(bank.press).toBe(position);
      expect(bank.count).toBe(position >= 1 ? 1 : 0);
      expect(modelValue('follow.json', 'press')).toBe(position);
      expect(modelValue('follow.json', 'count')).toBe(bank.count);
      expect(field('press').value).toBe(formatDisplay(position));
      expect(readout('count').textContent).toBe(String(bank.count));
      expect(s.valueAsNumber, 'the thumb holds what the pointer set').toBe(position);
      expect(panel(), 'the panel was replaced').toBe(held);
      expect(slider('press'), 'the slider was replaced').toBe(s);
      expect(one.draws, 'that frame drew once').toBe(1);
      expectDrawn();
    }
  });

  it('R2: the release asks nothing more, keeps the element and its focus, and adds no window listener before a press', async () => {
    const added = vi.spyOn(window, 'addEventListener');
    const removed = vi.spyOn(window, 'removeEventListener');
    const viewer = await rested('follow.json');
    const POINTER = ['pointermove', 'pointerup', 'pointercancel'];
    const pointerCalls = (spy: MockInstance) => spy.mock.calls
      .filter((call) => POINTER.includes(String(call[0])));
    expect(pointerCalls(added), 'the mount added a pointer listener to the window').toEqual([]);
    const s = slider('press');
    const addedBefore = added.mock.calls.length;
    pressOn(s);
    for (const position of R1_STEPS) {
      dragTo(s, position);
      await frames(1);
    }
    const mark = requests().length;
    letGo(s);
    expect(askedSince(mark), 'the release made a request').toEqual([]);
    expect(slider('press'), 'the slider was replaced at the release').toBe(s);
    expect(document.activeElement, 'the slider lost the focus').toBe(s);
    expect(outcomeLine('press').textContent).toBe('moved 1.4 mm');
    expect(s.valueAsNumber, 'the thumb').toBe(viewer.machine()!.state().press);
    await expectStill(10);
    expect(askedSince(mark)).toEqual([]);
    // Every listener the press added to the window has been removed.
    const pressAdded = added.mock.calls.slice(addedBefore)
      .filter((call) => POINTER.includes(String(call[0])));
    for (const call of pressAdded) {
      const match = removed.mock.calls.some((one) => one[0] === call[0] && one[1] === call[1]
        && JSON.stringify(one[2] ?? false) === JSON.stringify(call[2] ?? false));
      expect(match, `the window still holds the press's ${String(call[0])} listener`).toBe(true);
    }
  });

  it('R3: several positions before one frame make one request, for the latest; a thumb held still asks and draws nothing', async () => {
    await rested('follow.json');
    const s = slider('press');
    pressOn(s);
    const mark = requests().length;
    dragTo(s, 0.3);
    dragTo(s, 0.5);
    dragTo(s, 0.7);
    await frames(1);
    expect(askedSince(mark)).toEqual([['press', { to: 0.7 }]]);
    dragTo(s, 0.7);
    await frames(1);
    expect(askedSince(mark), 'the same position was asked again').toEqual([['press', { to: 0.7 }]]);
    const still = await counted(() => frames(10));
    expect({ draws: still.draws, updates: still.updates }).toEqual({ draws: 0, updates: 0 });
    expect(askedSince(mark)).toEqual([['press', { to: 0.7 }]]);
  });

  it('R4: the last position is asked at the release, rendered by the next frame and not in the release', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    pressOn(s);
    const mark = requests().length;
    const renders = bench.renders;
    dragTo(s, 0.9);
    pointerOn(s, 'pointerup');
    expect(askedSince(mark), 'the release did not ask the last position').toEqual([['press', { to: 0.9 }]]);
    expect(bench.renders - renders, 'rendered in the release').toBe(0);
    expect(viewer.machine()!.state().press).toBe(0.9);
    const next = await counted(() => frames(1));
    expect(next.draws).toBe(1);
    expectDrawn();
    await expectStill(10);
    expect(askedSince(mark)).toEqual([['press', { to: 0.9 }]]);
  });
});

describe('R5: a press ends without a change, and the window losing focus ends nothing', () => {
  const ENDINGS: Array<[string, (s: HTMLInputElement) => void]> = [
    ['pointercancel', (s) => { pointerOn(s, 'pointercancel'); }],
    ['lostpointercapture', (s) => { pointerOn(s, 'lostpointercapture'); }],
    ['pointerup let go elsewhere', () => { pointerOn(document.body, 'pointerup'); }],
  ];
  it.each(ENDINGS)('%s asks the pending position once, places the thumb at the bank, and later inputs ask nothing', async (_name, end) => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    pressOn(s);
    const mark = requests().length;
    dragTo(s, 1.8);
    end(s);
    expect(askedSince(mark), 'the pending position').toEqual([['press', { to: 1.8 }]]);
    expect(viewer.machine()!.state().press).toBe(1.5);
    expect(s.valueAsNumber, 'the thumb stands where the machine stands').toBe(1.5);
    await frames(2);
    valueTo(s, 1.1);
    await frames(2);
    dragTo(s, 0.4);
    await frames(2);
    expect(askedSince(mark), 'an input after the end of the press asked').toEqual([['press', { to: 1.8 }]]);
  });

  const NOT_ENDINGS: Array<[string, (s: HTMLInputElement) => void]> = [
    ['the window\'s blur', () => { window.dispatchEvent(new Event('blur')); }],
    ['a hidden page', () => {
      Object.defineProperty(document, 'hidden', { configurable: true, get: () => true });
      document.dispatchEvent(new Event('visibilitychange'));
    }],
    ['a blur on another element', () => {
      field('wheel').dispatchEvent(new FocusEvent('blur'));
    }],
  ];
  it.each(NOT_ENDINGS)('%s ends nothing: the next position is followed in its frame', async (_name, happen) => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    pressOn(s);
    dragTo(s, 0.4);
    await frames(1);
    const mark = requests().length;
    happen(s);
    await frames(1);
    expect(askedSince(mark), 'something was asked by what ends nothing').toEqual([]);
    dragTo(s, 0.8);
    expect(askedSince(mark)).toEqual([]);
    await frames(1);
    expect(askedSince(mark)).toEqual([['press', { to: 0.8 }]]);
    expect(viewer.machine()!.state().press).toBe(0.8);
    delete (document as unknown as Record<string, unknown>).hidden;
  });
});

describe('R6 to R9: a jump is drawn, and the positions after it wait for it', () => {
  it('R6: a track press is drawn from the press, the thumb held at the press point, and its release asks nothing', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    const renders = bench.renders;
    const mark = requests().length;
    pressOn(s);
    valueTo(s, 1.2);
    expect(askedSince(mark), 'the track press made no request at its input').toEqual([['press', { to: 1.2 }]]);
    expect(viewer.machine()!.state().press).toBe(1.2);
    expect(modelValue('follow.json', 'press'), 'the model jumped').toBe(0);
    expect(field('press').value).toBe('0');
    expect(bench.renders - renders, 'the press rendered').toBe(0);
    const risen: number[] = [];
    for (let i = 0; i < 20; i += 1) {
      await frames(1);
      risen.push(Number(field('press').value));
      expect(s.valueAsNumber, 'the thumb left the press point while held').toBe(1.2);
    }
    expect(risen).toEqual([...risen].sort((a, b) => a - b));
    expect(risen[risen.length - 1]).toBeGreaterThan(0);
    expect(risen[risen.length - 1]).toBeLessThan(1.2);
    letGo(s);
    expect(askedSince(mark), 'the release asked').toEqual([['press', { to: 1.2 }]]);
    const rest = await pathUntilRest('press');
    expect(rest).toEqual([...rest].sort((a, b) => a - b));
    expect(field('press').value).toBe('1.2');
    expect(s.valueAsNumber).toBe(1.2);
    expect(slider('press')).toBe(s);
    expect(askedSince(mark)).toEqual([['press', { to: 1.2 }]]);
  });

  it('R6: a click on the track (every event in one task) is one request, drawn from where the input stood', async () => {
    await rested('follow.json');
    const s = slider('press');
    const mark = requests().length;
    pressOn(s);
    valueTo(s, 1.2);
    letGo(s);
    const asked = askedSince(mark);
    const element = slider('press');
    const thumb = element.valueAsNumber;
    const path = await pathUntilRest('press');
    expect(asked, 'the request count').toEqual([['press', { to: 1.2 }]]);
    expectRecorded('R6.click', { asked, path });
    expect(thumb, 'the thumb right after the click').toBe(1.2);
    expect(element === s, 'the slider was replaced').toBe(true);
  });

  it('R7: the positions after a drawn jump wait for it, the latest asked in the frame it lands', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    const mark = requests().length;
    pressOn(s);
    valueTo(s, 0.4);
    expect(askedSince(mark)).toEqual([['press', { to: 0.4 }]]);
    await frames(2);
    dragTo(s, 0.5);
    await frames(1);
    dragTo(s, 0.6);
    let landed = -1;
    for (let i = 0; i < 60; i += 1) {
      const before = Number(field('press').value);
      await frames(1);
      const made = askedSince(mark);
      if (made.length > 1) {
        expect(made).toEqual([['press', { to: 0.4 }], ['press', { to: 0.6 }]]);
        expect(before, 'the jump had not been drawn to its end').toBeLessThan(0.4);
        landed = i;
        break;
      }
    }
    expect(landed, 'the positions after the jump were never asked').toBeGreaterThan(10);
    expect(viewer.machine()!.state().press).toBe(0.6);
    expect(field('press').value).toBe('0.6');
    dragTo(s, 0.8);
    await frames(1);
    expect(askedSince(mark)).toEqual([['press', { to: 0.4 }], ['press', { to: 0.6 }],
                                      ['press', { to: 0.8 }]]);
  });

  it('R8: released during the jump, the drawing goes on and the frame it lands in asks the latest position', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    const mark = requests().length;
    pressOn(s);
    valueTo(s, 0.4);
    await frames(2);
    dragTo(s, 0.5);
    dragTo(s, 0.6);
    letGo(s);
    expect(askedSince(mark), 'the release did not wait for the jump').toEqual([['press', { to: 0.4 }]]);
    await frames(1);
    expect(Number(field('press').value)).toBeLessThan(0.4);
    await untilRest();
    expect(askedSince(mark)).toEqual([['press', { to: 0.4 }], ['press', { to: 0.6 }]]);
    expect(viewer.machine()!.state().press).toBe(0.6);
    expect(s.valueAsNumber).toBe(0.6);
    await expectStill(10);
    expect(askedSince(mark)).toEqual([['press', { to: 0.4 }], ['press', { to: 0.6 }]]);
  });

  it('R8: a host request during the jump lands it, asks the latest position, then acts', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    const mark = requests().length;
    pressOn(s);
    valueTo(s, 0.4);
    await frames(2);
    dragTo(s, 0.6);
    letGo(s);
    await frames(1);
    viewer.machine()!.move('wheel', { to: 3 });
    expect(askedSince(mark)).toEqual([['press', { to: 0.4 }], ['press', { to: 0.6 }],
                                      ['wheel', { to: 3 }]]);
    expect(field('press').value).toBe('0.6');
    expect(viewer.machine()!.state().press).toBe(0.6);
  });

  it('R9: the first position of a pinned thumb is drawn, and the positions after it wait for it', async () => {
    const viewer = await rested('follow.json');
    viewer.machine()!.move('open', { to: 1.4 });
    await frames(1);
    const s = slider('open');
    expect(s.valueAsNumber, 'the thumb is pinned at the end').toBe(1);
    const mark = requests().length;
    const renders = bench.renders;
    pressOn(s);
    dragTo(s, 0.9);
    expect(askedSince(mark), 'the pinned thumb\'s first position').toEqual([['open', { to: 0.9 }]]);
    expect(viewer.machine()!.state().open).toBe(0.9);
    expect(modelValue('follow.json', 'open'), 'the model jumped').toBe(1.4);
    expect(field('open').value).toBe('1.4');
    expect(bench.renders - renders).toBe(0);
    dragTo(s, 0.8);
    let asked = -1;
    for (let i = 0; i < 40; i += 1) {
      await frames(1);
      if (askedSince(mark).length > 1) { asked = i; break; }
    }
    expect(asked, 'the position after the jump did not wait for it').toBeGreaterThan(5);
    expect(askedSince(mark)).toEqual([['open', { to: 0.9 }], ['open', { to: 0.8 }]]);
  });
});

describe('R10 to R14: stops, refusals, commits, whole numbers and scales', () => {
  it('R10: a stop holds the model and the reading at it while the thumb stays under the pointer, reported once', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    const held = panel();
    const line = writesOf(outcomeLine('press'));
    const STOPPED = 'moved 1.5 mm, held by block.travel (high 1.5)';
    pressOn(s);
    for (const position of [1.2, 1.6, 1.8, 1.9]) {
      dragTo(s, position);
      await frames(1);
      if (position > 1.5) {
        expect(viewer.machine()!.state().press).toBe(1.5);
        expect(modelValue('follow.json', 'press')).toBe(1.5);
        expect(field('press').value).toBe('1.5');
        expect(s.valueAsNumber).toBe(position);
        expect(outcomeLine('press').textContent).toBe(STOPPED);
      }
    }
    expect(line.texts().filter((text) => text === STOPPED), 'the stop\'s report').toEqual([STOPPED]);
    expect(panel(), 'the panel was replaced').toBe(held);
    letGo(s);
    expect(s.valueAsNumber, 'the thumb at the release').toBe(1.5);
    expect(outcomeLine('press').textContent).toBe(STOPPED);
  });

  it('R11: a refused position leaves the last admitted one, is reported once, and a drag is admitted step by step where one request is refused', async () => {
    const viewer = await rested('fine.json');
    const start = viewer.machine()!.snapshot();
    const s = slider('fine');
    const line = writesOf(outcomeLine('fine'));
    pressOn(s);
    for (const position of [0.1, 0.2]) { dragTo(s, position); await frames(1); }
    for (const position of [0.75, 0.8]) {
      dragTo(s, position);
      await frames(1);
      expect(viewer.machine()!.state().fine).toBe(0.2);
      expect(modelValue('fine.json', 'fine')).toBe(0.2);
      expect(field('fine').value).toBe('0.2');
      expect(outcomeLine('fine').textContent).toMatch(/^refused: /);
    }
    const refusals = line.texts().filter((text) => text.startsWith('refused'));
    expect(refusals.length, `the refusal was written ${refusals.length} times`).toBe(1);
    for (const position of [0.3, 0.4, 0.55]) { dragTo(s, position); await frames(1); }
    letGo(s);
    const bank = viewer.machine()!.state();
    expect(bank).toEqual({ fine: 0.55, teeth: 5 });
    expect(outcomeLine('fine').textContent).toBe('moved 0.55');
    const once = freshMachine(FINE);
    once.restore(start);
    expect(() => once.move('fine', { to: 0.55 }), 'one request of 0.55').toThrow(/would cross/);
  });

  it('R12: back and forth across a commit fires it at each crossing; the bank is the bank of the requests', async () => {
    const viewer = await rested('follow.json');
    const start = viewer.machine()!.snapshot();
    const s = slider('press');
    const mark = requests().length;
    pressOn(s);
    for (const position of [0.7, 1.3, 0.7, 1.3]) { dragTo(s, position); await frames(1); }
    letGo(s);
    const bank = viewer.machine()!.state();
    expect(bank.count).toBe(2);
    const once = freshMachine(FOLLOW);
    once.restore(start);
    once.move('press', { to: 1.3 });
    expect(once.state().count).toBe(1);
    expect(bank).toEqual(replayed(FOLLOW, start, askedSince(mark)));
    expect(askedSince(mark).length).toBe(4);
  });

  it('R13: a whole-number input is asked whole numbers and posed whole at every frame', async () => {
    const viewer = await rested('follow.json');
    viewer.machine()!.move('wheel', { to: 1 });
    await frames(1);
    const s = slider('wheel');
    const mark = requests().length;
    pressOn(s);
    for (const position of [2, 3, 4]) {
      dragTo(s, position);
      await frames(1);
      const bank = viewer.machine()!.state();
      expect(bank.wheel).toBe(position);
      expect(modelValue('follow.json', 'wheel')).toBe(position);
      expect(field('wheel').value).toBe(String(position));
    }
    const asked = askedSince(mark);
    expect(asked).toEqual([['wheel', { to: 2 }], ['wheel', { to: 3 }], ['wheel', { to: 4 }]]);
    for (const [, request] of asked) expect(Number.isInteger(request.to)).toBe(true);
  });

  it('R14: a scaled input is asked in design units and holds the native value', async () => {
    const viewer = await rested('follow.json');
    const s = slider('scaled');
    const mark = requests().length;
    pressOn(s);
    dragTo(s, 4);
    await frames(1);
    expect(askedSince(mark)).toEqual([['scaled', { to: 4 }]]);
    expect(viewer.machine()!.state().scaled).toBe(2);
    expect(modelValue('follow.json', 'scaled')).toBe(2);
    expect(field('scaled').value).toBe('4');
    letGo(s);
    expect(s.valueAsNumber).toBe(4);
    expect(outcomeLine('scaled').textContent).toBe('moved 4');
  });
});

describe('R15 and R16: other authorities over the pose', () => {
  it('R15: a drawing running at the press goes on, writes the field and not the held thumb, and the first position lands it', async () => {
    const viewer = await rested('follow.json');
    viewer.machine()!.trigger('Push');
    await frames(3);
    const s = slider('press');
    pressOn(s);
    s.value = '0.3';
    const fields: number[] = [];
    for (let i = 0; i < 3; i += 1) {
      await frames(1);
      fields.push(Number(field('press').value));
      expect(s.valueAsNumber, 'the drawing wrote the held thumb').toBe(0.3);
    }
    expect(fields).toEqual([...fields].sort((a, b) => a - b));
    expect(fields[0]).toBeGreaterThan(0);
    expect(fields[2]).toBeLessThan(0.5);
    const mark = requests().length;
    dragTo(s, 0.3);
    await frames(1);
    const made = requests().slice(mark);
    expect(made.map((one) => [one.id, one.request])).toEqual([['press', { to: 0.3 }]]);
    expect(made[0].origin, 'the request was not made from the drawing\'s end').toBe(0.5);
    expect(viewer.machine()!.state().press).toBe(0.3);
    expect(field('press').value).toBe('0.3');
  });

  type Door = [string, string, boolean, (viewer: ViewerHandle, snapshot: ClockedSnapshot) => Promise<void> | void];
  const DOORS: Door[] = [
    ['the host\'s move', 'follow.json', true, (viewer) => { viewer.machine()!.move('wheel', { to: 3 }); }],
    ['the host\'s restore', 'follow.json', true, (viewer, snapshot) => { viewer.machine()!.restore(snapshot); }],
    ['the host\'s reset', 'follow.json', true, (viewer) => { viewer.machine()!.reset(); }],
    ['the host\'s trigger', 'follow.json', true, (viewer) => { viewer.machine()!.trigger('Turn'); }],
    ['the host\'s setClockPlaying(true)', 'follow-clock.json', true, (viewer) => { viewer.machine()!.setClockPlaying(true); }],
    ['an instruction pressed', 'follow.json', true, () => {
      container.querySelector<HTMLButtonElement>('.clocked-instruction[data-instruction="Turn"]')!.click();
    }],
    ['a typed value', 'follow.json', true, () => {
      const box = field('wheel');
      box.value = '3';
      box.dispatchEvent(new Event('change', { bubbles: true }));
    }],
    ['a nudge', 'follow.json', true, () => {
      container.querySelector<HTMLButtonElement>('.clocked-plus[data-input="wheel"]')!.click();
    }],
    ['the panel\'s Reset', 'follow.json', true, () => {
      container.querySelector<HTMLButtonElement>('.clocked-reset')!.click();
    }],
    ['setRoot and back', 'follow.json', true, (viewer) => { viewer.setRoot(['block']); viewer.setRoot(null); }],
    ['reload()', 'follow.json', true, async (viewer) => { await viewer.reload(); }],
    ['manifestChanged() with the same machine', 'follow.json', true, async (viewer) => { await viewer.manifestChanged(); }],
    ['manifestChanged() with the same machine (version 14)', 'follow-14.json', true, async (viewer) => { await viewer.manifestChanged(); }],
    ['manifestChanged() with another machine (version 14)', 'follow-14.json', false, async (viewer) => {
      const document = JSON.parse(bench.documents.get('follow-14.json')!) as typeof FOLLOW;
      document.clocked.identity = 'another-machine';
      bench.documents.set('follow-14.json', JSON.stringify(document));
      await viewer.manifestChanged();
      expect(bench.machines.length, 'the republish did not replace the machine').toBe(2);
    }],
    ['dispose()', 'follow.json', false, (viewer) => { viewer.dispose(); }],
  ];
  it.each(DOORS)('R16: %s ends the press first', async (name, document, asks, door) => {
    const viewer = await rested(document);
    const snapshot = viewer.machine()!.snapshot();
    const s = slider('press');
    pressOn(s);
    dragTo(s, 0.7);
    const mark = log().length;
    await door(viewer, snapshot);
    const after = log().slice(mark);
    const at = after.findIndex((one) => one.kind === 'move' && one.id === 'press'
      && one.request.to === 0.7);
    if (asks) {
      expect(at, `${name}: the pending position was never asked`).toBeGreaterThanOrEqual(0);
      expect(after[at].machine, 'asked of another machine').toBe(0);
      expect(after.slice(0, at).filter((one) => one.kind !== 'move' || one.id !== 'time')
        .map((one) => one.kind), 'something acted before the pending position was asked').toEqual([]);
    } else {
      expect(at, `${name}: the pending position was asked of a machine`).toBe(-1);
    }
    // The slider the pointer held asks nothing afterwards. (A disposed
    // viewer's elements are gone with it; nothing is dispatched there.)
    if (name === 'dispose()') return;
    const later = log().length;
    valueTo(s, 1.1);
    change(s);
    dragTo(s, 0.3);
    pointerOn(s, 'pointerup');
    await frames(2);
    expect(log().slice(later).filter((one) => one.kind === 'move' && one.id === 'press')
      .map((one) => one.request), 'the old slider asked').toEqual([]);
  });
});

describe('R17 to R20: what is not a drag', () => {
  it('R17: no press begins while the clock plays; a change is one drawn request, as on the base', async () => {
    const viewer = await rested('follow-clock.json');
    viewer.machine()!.setClockPlaying(true);
    await frames(2);
    const mark = requests().length;
    const s = slider('press');
    pressOn(s);
    dragTo(s, 0.6);
    dragTo(s, 0.9);
    await frames(1);
    const s2 = slider('press');
    dragTo(s2, 1.1);
    await frames(2);
    const during = requests().slice(mark).map((one) => one.id);
    const playingAfterFrames = viewer.machine()!.clockPlaying();
    const s3 = slider('press');
    const before = requests().length;
    const layers = bench.layers;
    valueTo(s3, 1.2);
    change(s3);
    const atChange = askedSince(before);
    const replaced = slider('press') !== s3;
    const path = await pathUntilRest('press');
    expectRecorded('R17', {
      during, playingAfterFrames, atChange, layers: bench.layers - layers > 0,
      replaced, playing: viewer.machine()!.clockPlaying(), path,
    });
  });

  it('R17: with the clock paused, a drag on the same document is followed', async () => {
    const viewer = await rested('follow-clock.json');
    const s = slider('press');
    pressOn(s);
    const mark = requests().length;
    for (const position of [0.3, 0.6]) {
      dragTo(s, position);
      await frames(1);
      expect(askedSince(mark).slice(-1)).toEqual([['press', { to: position }]]);
      expect(viewer.machine()!.state().press).toBe(position);
    }
  });

  it('R18: a key, an input with no press, a typed value and a nudge are as on the base', async () => {
    const viewer = await rested('follow.json');
    const measured: Record<string, unknown> = {};
    const gesture = async (name: string, id: string, act: () => void) => {
      const mark = requests().length;
      const layers = bench.layers;
      const held = panel();
      act();
      const asked = askedSince(mark);
      const rebuilt = bench.layers - layers;
      const replaced = panel() !== held;
      const path = await pathUntilRest(id);
      measured[name] = { asked, rebuilt, replaced, path, bank: viewer.machine()!.state() };
    };
    await gesture('key', 'press', () => {
      const s = slider('press');
      s.focus();
      s.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
      valueTo(s, 1);
      change(s);
    });
    await gesture('input with no press', 'press', () => { valueTo(slider('press'), 1.6); });
    await gesture('typed value', 'wheel', () => {
      const box = field('wheel');
      box.value = '4';
      box.dispatchEvent(new Event('change', { bubbles: true }));
    });
    await gesture('nudge', 'wheel', () => {
      container.querySelector<HTMLButtonElement>('.clocked-minus[data-input="wheel"]')!.click();
    });
    expectRecorded('R18', measured);
  });

  it('R18: a change one frame after a release is one drawn request again', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    pressOn(s);
    dragTo(s, 0.5);
    await frames(1);
    const mark = requests().length;
    letGo(s);
    expect(askedSince(mark), 'the release\'s own change was a request').toEqual([]);
    await frames(1);
    valueTo(s, 1.0);
    change(s);
    expect(askedSince(mark)).toEqual([['press', { to: 1 }]]);
    expect(viewer.machine()!.state().press).toBe(1);
    expect(field('press').value, 'the change was not drawn').toBe('0.5');
  });

  it('R19: a followed frame costs one draw, one named update, no render inside the request and no rebuild', async () => {
    await rested('follow.json');
    const s = slider('press');
    const held = panel();
    pressOn(s);
    for (const position of R1_STEPS) {
      dragTo(s, position);
      const layers = bench.layers;
      const mark = requests().length;
      const one = await counted(() => frames(1));
      const made = requests().slice(mark);
      expect({ draws: one.draws, named: one.named }, `the frame at ${position}`)
        .toEqual({ draws: 1, named: 1 });
      expect(made.map((entry) => entry.renders)).toEqual([0]);
      expect(bench.layers - layers, 'the panel was rebuilt').toBe(0);
      expect(panel()).toBe(held);
    }
  });

  it('R20: a second pointer is ignored, another slider takes the press over, and a right button is no press', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    pressOn(s);
    const mark = requests().length;
    dragTo(s, 0.4);
    pointerOn(s, 'pointerdown', { pointerId: 2, pointerType: 'touch' });
    await frames(1);
    expect(askedSince(mark)).toEqual([['press', { to: 0.4 }]]);
    pointerOn(s, 'pointerup', { pointerId: 2, pointerType: 'touch' });
    dragTo(s, 0.6);
    await frames(1);
    expect(askedSince(mark), 'the second pointer ended the press').toEqual([['press', { to: 0.4 }], ['press', { to: 0.6 }]]);
    dragTo(s, 0.8);
    const w = slider('wheel');
    pressOn(w);
    expect(askedSince(mark), 'the other slider did not end the press')
      .toEqual([['press', { to: 0.4 }], ['press', { to: 0.6 }], ['press', { to: 0.8 }]]);
    dragTo(w, 5);
    await frames(1);
    expect(askedSince(mark, 'wheel')).toEqual([['wheel', { to: 5 }]]);
    dragTo(s, 1.2);
    await frames(1);
    expect(askedSince(mark, 'press').length, 'the first slider is still followed').toBe(3);
    letGo(w);
    const o = slider('open');
    const before = requests().length;
    pressOn(o, { button: 2, buttons: 2 });
    dragTo(o, 0.5, { buttons: 2 });
    await frames(2);
    expect(askedSince(before), 'a right button pressed').toEqual([]);
    expect(viewer.machine()!.state().open).toBe(0);
  });

  it('O1: an on-demand mount presents no slider, and its handle draws per call as on the base', async () => {
    const ON_DEMAND: ViewerOptions = { renderMode: 'on-demand', animation: 'external',
                                       autoplay: false, driverControls: 'none',
                                       partControls: 'none' };
    const viewer = await open('follow.json', ON_DEMAND);
    const sliders = container.querySelectorAll('.clocked-slider').length;
    const machine = viewer.machine()!;
    const measured: Array<[string, number]> = [];
    const step = async (name: string, action: () => void) => {
      measured.push([name, (await counted(action)).draws]);
    };
    const snapshot = machine.snapshot();
    await step('move press', () => { machine.move('press', { to: 0.7 }); });
    await step('move wheel', () => { machine.move('wheel', { by: 2 }); });
    await step('move past the stop', () => { machine.move('press', { to: 1.9 }); });
    await step('restore', () => { machine.restore(snapshot); });
    await step('reset', () => { machine.reset(); });
    expectRecorded('O1', { sliders, measured,
                           loop: bench.loopCalls.some((one) => typeof one === 'function') });
  });
});

// ---------------------------------------------------------------------
// Added in review (evidence.md, "The reviewer's record").

describe('V1 to V3: added in review', () => {
  it('V1: the panel\'s Reset during a drag resets the bank the hand left, and nothing is asked after it', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    pressOn(s);
    dragTo(s, 0.7);
    const mark = log().length;
    container.querySelector<HTMLButtonElement>('.clocked-reset')!.click();
    expect(log().slice(mark).filter((one) => one.kind !== 'layer')
      .map((one) => [one.kind, one.id, one.request.to ?? null]))
      .toEqual([['move', 'press', 0.7], ['reset', '', null]]);
    expect(viewer.machine()!.state().press).toBe(0);
    expect(modelValue('follow.json', 'press')).toBe(0);
    expect(field('press').value).toBe('0');
    await frames(2);
    expect(viewer.machine()!.state().press).toBe(0);
  });

  it('V2: a click on the track that starts no drawing leaves the panel as the base\'s rebuilt panel read', async () => {
    const viewer = await rested('follow-instant.json');
    const s = slider('press');
    const mark = requests().length;
    pressOn(s);
    valueTo(s, 1.2);
    letGo(s);
    expect(askedSince(mark)).toEqual([['press', { to: 1.2 }]]);
    const bank = viewer.machine()!.state();
    expect({ press: bank.press, count: bank.count }).toEqual({ press: 1.2, count: 1 });
    expect(modelValue('follow-instant.json', 'press')).toBe(1.2);
    expect(modelValue('follow-instant.json', 'count')).toBe(1);
    expect(field('press').value, 'the field of the pressed input').toBe('1.2');
    expect(readout('count').textContent, 'the readout the request\'s commit wrote').toBe('1');
    expect(slider('press').valueAsNumber).toBe(1.2);
    await frames(1);
    expectDrawn();
    await expectStill(5);
    expect(askedSince(mark)).toEqual([['press', { to: 1.2 }]]);
  });

  it('V2: a press on the track that starts no drawing writes the panel in place, and the next position is followed', async () => {
    const viewer = await rested('follow-instant.json');
    const s = slider('press');
    const held = panel();
    const mark = requests().length;
    pressOn(s);
    valueTo(s, 1.2);
    expect(askedSince(mark)).toEqual([['press', { to: 1.2 }]]);
    expect(viewer.machine()!.state().count).toBe(1);
    expect(modelValue('follow-instant.json', 'press')).toBe(1.2);
    expect(modelValue('follow-instant.json', 'count')).toBe(1);
    expect(field('press').value, 'the field of the pressed input').toBe('1.2');
    expect(readout('count').textContent, 'the readout the request\'s commit wrote').toBe('1');
    expect(outcomeLine('press').textContent).toBe('moved 1.2 mm');
    expect(panel(), 'the panel was replaced').toBe(held);
    expect(slider('press'), 'the slider was replaced').toBe(s);
    expect(s.valueAsNumber, 'the thumb left the press point').toBe(1.2);
    dragTo(s, 1.3);
    await frames(1);
    expect(askedSince(mark)).toEqual([['press', { to: 1.2 }], ['press', { to: 1.3 }]]);
    expect(field('press').value).toBe('1.3');
    expectDrawn();
    letGo(s);
    await expectStill(5);
    expect(askedSince(mark)).toEqual([['press', { to: 1.2 }], ['press', { to: 1.3 }]]);
  });

  it('V3: the speed of the clock moves nothing and replaces nothing, so it ends no press', async () => {
    const viewer = await rested('follow-clock.json');
    const s = slider('press');
    const held = panel();
    pressOn(s);
    dragTo(s, 0.4);
    await frames(1);
    const mark = requests().length;
    const speed = container.querySelector<HTMLSelectElement>('.clocked-speed')!;
    const other = [...speed.options].find((one) => one.value !== speed.value)!;
    speed.value = other.value;
    speed.dispatchEvent(new Event('change', { bubbles: true }));
    await frames(1);
    expect(askedSince(mark), 'the speed control asked').toEqual([]);
    expect(panel(), 'the panel was replaced').toBe(held);
    dragTo(s, 0.8);
    await frames(1);
    expect(askedSince(mark), 'the drag was not followed after the speed changed')
      .toEqual([['press', { to: 0.8 }]]);
    expect(viewer.machine()!.state().press).toBe(0.8);
    letGo(s);
    await expectStill(5);
    expect(askedSince(mark)).toEqual([['press', { to: 0.8 }]]);
  });
});

describe('V4 to V9: what the planted faults of the review left standing', () => {
  const POINTER = ['pointermove', 'pointerup', 'pointercancel'];
  /** The pointer listeners added to the window since the marks and not
   * removed since. */
  function windowHolds(added: MockInstance, removed: MockInstance,
                       from: [number, number]): string[] {
    const left = added.mock.calls.slice(from[0])
      .filter((call) => POINTER.includes(String(call[0])))
      .map((call) => [call[0], call[1], JSON.stringify(call[2] ?? false)]);
    for (const call of removed.mock.calls.slice(from[1])) {
      const at = left.findIndex((one) => one[0] === call[0] && one[1] === call[1]
        && one[2] === JSON.stringify(call[2] ?? false));
      if (at >= 0) left.splice(at, 1);
    }
    return left.map((one) => String(one[0]));
  }

  it('V4: a drag begun while a drawing runs reports its travel from the bank that drawing ends at', async () => {
    const viewer = await rested('follow.json');
    viewer.machine()!.trigger('Push');
    await frames(3);
    expect(viewer.machine()!.state().press).toBe(0.5);
    const s = slider('press');
    pressOn(s);
    dragTo(s, 0.3);
    await frames(1);
    expect(viewer.machine()!.state().press).toBe(0.3);
    expect(outcomeLine('press').textContent).toBe('moved -0.2 mm');
  });

  it('V5: a thumb is pinned by what the model shows, not by a bank a running drawing has yet to reach', async () => {
    const viewer = await rested('follow.json');
    viewer.machine()!.move('wheel', { to: 8 });
    await frames(1);
    viewer.machine()!.trigger('Turn');
    await frames(3);
    expect(viewer.machine()!.state().wheel, 'the bank is outside the slider').toBe(11);
    const s = slider('wheel');
    expect(s.valueAsNumber, 'the thumb is where the drawing shows the input').toBe(8);
    const mark = requests().length;
    pressOn(s);
    dragTo(s, 7);
    expect(askedSince(mark), 'the first position was drawn as a jump').toEqual([]);
    await frames(1);
    expect(askedSince(mark)).toEqual([['wheel', { to: 7 }]]);
    expect(viewer.machine()!.state().wheel).toBe(7);
    expect(modelValue('follow.json', 'wheel')).toBe(7);
    expect(field('wheel').value).toBe('7');
  });

  it('V6: between a republish replacing the machine and the panel being rebuilt, the old panel asks nothing and holds nothing on the window', async () => {
    const added = vi.spyOn(window, 'addEventListener');
    const removed = vi.spyOn(window, 'removeEventListener');
    const viewer = await rested('follow-14.json');
    const s = slider('press');
    const from: [number, number] = [added.mock.calls.length, removed.mock.calls.length];
    pressOn(s);
    dragTo(s, 0.7);
    expect(windowHolds(added, removed, from).sort()).toEqual([...POINTER].sort());
    const served = JSON.parse(bench.documents.get('follow-14.json')!) as typeof FOLLOW;
    served.clocked.identity = 'another-machine';
    bench.documents.set('follow-14.json', JSON.stringify(served));
    const mark = log().length;
    const done = viewer.manifestChanged();
    let replaced = false;
    for (let i = 0; i < 400 && !replaced; i += 1) {
      await Promise.resolve();
      replaced = bench.machines.length === 2;
    }
    expect(replaced, 'the republish never replaced the machine').toBe(true);
    expect(s.isConnected && slider('press') === s,
           'the panel was rebuilt already: this is not the interval the test is about').toBe(true);
    expect(windowHolds(added, removed, from), 'the dropped press left listeners on the window').toEqual([]);
    dragTo(s, 0.9);
    letGo(s);
    const again: [number, number] = [added.mock.calls.length, removed.mock.calls.length];
    pressOn(s);
    expect(added.mock.calls.slice(again[0]).filter((call) => POINTER.includes(String(call[0]))),
           'a press began on a panel built for the machine that is gone').toEqual([]);
    valueTo(s, 1.1);
    dragTo(s, 1.3);
    letGo(s);
    s.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft', bubbles: true }));
    valueTo(s, 1.2);
    change(s);
    await done;
    await frames(2);
    expect(log().slice(mark).filter((one) => one.kind === 'move')
      .map((one) => [one.machine, one.id, one.request]),
           'a request reached a machine from the old panel').toEqual([]);
    expect(slider('press'), 'the panel was not rebuilt for the new machine').not.toBe(s);
  });

  it('V7: a key pressed in the task of a release is a request: its change is not taken for the release\'s', async () => {
    await rested('follow.json');
    const s = slider('press');
    pressOn(s);
    dragTo(s, 0.4);
    await frames(1);
    letGo(s);
    const mark = requests().length;
    s.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
    valueTo(s, 0.6);
    change(s);
    expect(askedSince(mark)).toEqual([['press', { to: 0.6 }]]);
  });

  it('V8: another pointer\'s movement and lost capture leave the press as it is', async () => {
    const viewer = await rested('follow.json');
    const s = slider('press');
    const mark = requests().length;
    pressOn(s);
    pointerOn(document.body, 'pointermove', { pointerId: 2, pointerType: 'touch' });
    valueTo(s, 1.2);
    expect(askedSince(mark), 'another pointer\'s movement made the track press a drag')
      .toEqual([['press', { to: 1.2 }]]);
    await untilRest();
    pointerOn(s, 'lostpointercapture', { pointerId: 2, pointerType: 'touch' });
    dragTo(s, 1.3);
    await frames(1);
    expect(askedSince(mark), 'another pointer\'s lost capture ended the press')
      .toEqual([['press', { to: 1.2 }], ['press', { to: 1.3 }]]);
    expect(viewer.machine()!.state().press).toBe(1.3);
  });

  it('V9: dispose() during a drag takes the press\'s listeners off the window, and nothing is asked afterwards', async () => {
    const added = vi.spyOn(window, 'addEventListener');
    const removed = vi.spyOn(window, 'removeEventListener');
    const viewer = await rested('follow.json');
    const s = slider('press');
    const from: [number, number] = [added.mock.calls.length, removed.mock.calls.length];
    pressOn(s);
    dragTo(s, 0.7);
    const mark = log().length;
    viewer.dispose();
    expect(windowHolds(added, removed, from), 'the disposed viewer left listeners on the window').toEqual([]);
    pointerOn(document.body, 'pointermove');
    pointerOn(document.body, 'pointerup');
    expect(log().slice(mark)).toEqual([]);
  });
});

// ---------------------------------------------------------------------
// G1. Generated sequences.

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

interface Drag {
  id: string;
  slider: HTMLInputElement;
  /** The test's pointer is down on it. */
  held: boolean;
  first: 'drawn' | 'followed';
  start: ClockedSnapshot;
  startDisplay: number;
  document: object;
  logFrom: number;
  dispatched: number[];
  /** The drag's requests end at this index of the log; its own
   * requests after it, if a door made one, are the door's. */
  endedAt: number | null;
  dropped: boolean;
}

interface Generated {
  viewer: ViewerHandle;
  name: string;
  random: () => number;
  pick<T>(items: readonly T[]): T;
  drag: Drag | null;
  steps: string[];
}

const RANGES: Record<string, [number, number, boolean]> = {
  press: [0, 2, false], wheel: [0, 9, true], scaled: [0, 10, false], open: [0, 1, false],
  fine: [0, 1, false],
};

function served(g: Generated): Record<string, unknown> {
  return JSON.parse(bench.documents.get(g.name)!) as Record<string, unknown>;
}

function inputsShown(): string[] {
  return [...container.querySelectorAll<HTMLElement>('.clocked-slider')]
    .map((one) => one.dataset.input!);
}

function position(g: Generated, id: string): number {
  const [min, max, whole] = RANGES[id];
  const last = g.drag?.dispatched[g.drag.dispatched.length - 1];
  const roll = g.random();
  let value: number;
  if (roll < 0.15 && last !== undefined) value = last;
  else if (roll < 0.3) value = g.random() < 0.5 ? min : max;
  else if (roll < 0.45 && id === 'press') value = 1.5 + g.random() * 0.5;
  else value = min + g.random() * (max - min);
  return whole ? Math.round(value) : Math.round(value * 1000) / 1000;
}

/** A1: what the panel shows is what the model shows. */
function expectPanelIsModel(g: Generated, where: string, heldExempt: boolean): void {
  const poses = POSES[g.name];
  const machine = g.viewer.machine();
  if (machine === null) return;
  const drivers = machine.drivers();
  for (const row of container.querySelectorAll<HTMLElement>('.clocked-input')) {
    const id = row.dataset.input!;
    if (poses[id] === undefined) continue;
    const display = modelValue(g.name, id) * (SCALES[id] ?? 1);
    const box = row.querySelector<HTMLInputElement>('.clocked-value')!;
    if (document.activeElement !== box) {
      expect(box.value, `${where}: the field of ${id}`).toBe(formatDisplay(display));
    }
    const thumb = row.querySelector<HTMLInputElement>('.clocked-slider');
    if (thumb === null) continue;
    if (heldExempt && g.drag !== null && g.drag.slider === thumb) continue;
    const [min, max] = drivers[id].range as [number, number];
    expect(thumb.valueAsNumber, `${where}: the thumb of ${id}`)
      .toBe(Math.min(Math.max(display, min), max));
  }
  for (const value of container.querySelectorAll<HTMLElement>('.clocked-readout-value')) {
    const id = value.dataset.readout!;
    if (poses[id] === undefined) continue;
    expect(value.textContent, `${where}: the readout of ${id}`).toBe(String(modelValue(g.name, id)));
  }
}

/** A2: at rest, the model is the machine's bank. */
function expectModelIsBank(g: Generated, where: string): void {
  const bank = g.viewer.machine()!.state();
  for (const id of Object.keys(POSES[g.name])) {
    expect(modelValue(g.name, id), `${where}: the model of ${id} at rest`).toBe(bank[id]);
  }
}

/** What G1 exercised, printed so that a vacuous run shows. */
const exercised = { drags: 0, asked: 0, jumps: 0, dropped: 0, refused: 0, monotone: 0 };

/** A3: the requests of one drag. */
function expectDragAsked(g: Generated, drag: Drag, ownRequest: boolean, where: string): void {
  const upTo = drag.endedAt ?? log().length;
  let entries = log().slice(drag.logFrom, upTo)
    .filter((one) => one.kind === 'move' && one.id === drag.id);
  if (ownRequest) entries = entries.slice(0, -1);
  const asked = entries.map((one) => one.request.to as number);
  exercised.drags += 1;
  exercised.asked += asked.length;
  if (drag.first === 'drawn' && entries.some((one) => !one.inFrame)) exercised.jumps += 1;
  if (drag.dropped) exercised.dropped += 1;
  exercised.refused += entries.filter((one) => one.refused).length;
  // Every asked position is one the sequence dispatched, in order.
  let at = 0;
  for (const value of asked) {
    while (at < drag.dispatched.length && drag.dispatched[at] !== value) at += 1;
    expect(at < drag.dispatched.length,
           `${where}: asked ${value}, not dispatched in order (${drag.dispatched.join(', ')} / ${asked.join(', ')})`).toBe(true);
    at += 1;
  }
  for (let i = 1; i < asked.length; i += 1) {
    expect(asked[i] !== asked[i - 1], `${where}: ${asked[i]} asked twice in succession`).toBe(true);
  }
  const perFrame = new Map<number, number>();
  let outside = 0;
  for (const one of entries) {
    if (one.inFrame) perFrame.set(one.frame, (perFrame.get(one.frame) ?? 0) + 1);
    else outside += 1;
  }
  for (const [frame, count] of perFrame) {
    expect(count, `${where}: ${count} requests in frame ${frame}`).toBeLessThanOrEqual(1);
  }
  expect(outside, `${where}: requests outside a frame`)
    .toBeLessThanOrEqual(drag.first === 'drawn' ? 2 : 1);
  if (!drag.dropped && drag.dispatched.length > 0) {
    expect(asked[asked.length - 1], `${where}: the last position`)
      .toBe(drag.dispatched[drag.dispatched.length - 1]);
  }
  if (entries.length === 0) return;
  const bank = entries[entries.length - 1].after!;
  const replay = replayed(drag.document, drag.start, entries.map((one) => [one.id, one.request]));
  expect(bank, `${where}: the bank is not the replay of the drag's requests`).toEqual(replay);
  if (g.name === 'fine.json') return;
  const path = [drag.startDisplay, ...asked];
  const rising = path.every((value, i) => i === 0 || value >= path[i - 1]);
  const falling = path.every((value, i) => i === 0 || value <= path[i - 1]);
  const pastStop = drag.id === 'press' && path.some((value) => value > 1.5);
  if ((rising || falling) && !pastStop) {
    const once = freshMachine(sameMachine(drag.document, drag.start));
    once.restore(drag.start);
    once.move(drag.id, { to: asked[asked.length - 1] });
    exercised.monotone += 1;
    expect(bank, `${where}: a monotone drag differs from one request`).toEqual(once.state());
  }
}

/** The end of a drag, seen from the test: to rest unless the clock
 * plays, then A2 and A3. */
async function finished(g: Generated, ownRequest = false, waitForRest = true): Promise<void> {
  const drag = g.drag;
  if (drag === null) return;
  const where = `seed ${g.steps[0]} after ${g.steps.slice(1).join(', ')}`;
  const playing = g.viewer.machine()?.clock() !== null && g.viewer.machine()?.clockPlaying();
  if (waitForRest && !playing) {
    await untilRestChecked(g, where, true);
  }
  if (drag.endedAt === null) drag.endedAt = log().length;
  expectDragAsked(g, drag, ownRequest, where);
  if (g.drag === drag) g.drag = null;
  if (waitForRest && !playing) {
    expectPanelIsModel(g, `${where} (at rest)`, false);
    expectModelIsBank(g, where);
  }
}

async function untilRestChecked(g: Generated, where: string, exempt: boolean): Promise<void> {
  let quiet = 0;
  for (let i = 0; i < 400; i += 1) {
    const one = await counted(() => frames(1));
    expectDrawn();
    expectPanelIsModel(g, where, exempt);
    quiet = one.draws === 0 ? quiet + 1 : 0;
    if (quiet >= 2) return;
  }
  throw new Error(`${where}: the page did not come to rest`);
}

function beginDrag(g: Generated, id: string, target: HTMLInputElement,
                   first: Drag['first']): Drag | null {
  const machine = g.viewer.machine()!;
  if (machine.clock() !== null && machine.clockPlaying()) return null;
  const start = machine.snapshot();
  // A thumb pinned at an end, as the model shows it, is a jump too.
  const [min, max] = RANGES[id];
  const shown = modelValue(g.name, id) * (SCALES[id] ?? 1);
  const drawnFirst = first === 'drawn' || shown < min || shown > max;
  return {
    id, slider: target, held: true, first: drawnFirst ? 'drawn' : 'followed', start,
    startDisplay: start.bank[id] * (SCALES[id] ?? 1),
    document: served(g), logFrom: log().length, dispatched: [], endedAt: null,
    dropped: false,
  };
}

/** Dispatch one position on the held slider, recording what the slider
 * took. */
function dispatchPosition(g: Generated, withMove: boolean): void {
  const drag = g.drag!;
  if (withMove) pointerOn(drag.slider, 'pointermove');
  drag.slider.value = String(position(g, drag.id));
  drag.dispatched.push(drag.slider.valueAsNumber);
  drag.slider.dispatchEvent(new Event('input', { bubbles: true }));
}

type Action = [string, (g: Generated) => Promise<void> | void];

/** Doors: each ends a held drag first. `own` names the input the door's
 * own request moves, if any. */
function doors(g: Generated): Array<[string, string | null, (g: Generated) => Promise<void> | void]> {
  const clocked = g.name === 'follow-clock.json';
  const ids = Object.keys(RANGES).filter((id) => POSES[g.name][id] !== undefined
    && !(['count', 'teeth'].includes(id)));
  const id = g.pick(ids);
  const list: Array<[string, string | null, (g: Generated) => Promise<void> | void]> = [
    [`host move ${id}`, id, (h) => {
      try { h.viewer.machine()!.move(id, { to: position(h, id) }); } catch { /* refused */ }
    }],
    ['host restore', null, (h) => { h.viewer.machine()!.restore(h.viewer.machine()!.snapshot()); }],
    ['host reset', null, (h) => { h.viewer.machine()!.reset(); }],
    ['setRoot', null, (h) => {
      h.viewer.setRoot(h.random() < 0.5 ? null : [h.name === 'fine.json' ? 'plate' : 'block']);
      h.viewer.setRoot(null);
    }],
    ['reload', null, async (h) => { await h.viewer.reload(); }],
    ['manifestChanged (same)', null, async (h) => { await h.viewer.manifestChanged(); }],
    ['manifestChanged (another)', null, async (h) => {
      const document = served(h) as { clocked: { identity: string } };
      document.clocked.identity = `${document.clocked.identity}+`;
      bench.documents.set(h.name, JSON.stringify(document));
      await h.viewer.manifestChanged();
    }],
  ];
  if (container.querySelector(`.clocked-value[data-input="${id}"]`) !== null) {
    list.push([`typed ${id}`, id, (h) => {
      const box = field(id);
      box.value = String(position(h, id));
      box.dispatchEvent(new Event('change', { bubbles: true }));
    }]);
    list.push([`nudge ${id}`, id, (h) => {
      container.querySelector<HTMLButtonElement>(
        `.clocked-${h.random() < 0.5 ? 'plus' : 'minus'}[data-input="${id}"]`)!.click();
    }]);
  }
  if (g.name !== 'fine.json') {
    const name = g.pick(['Push', 'Turn']);
    const moves = name === 'Push' ? 'press' : 'wheel';
    list.push([`host trigger ${name}`, moves, (h) => { h.viewer.machine()!.trigger(name); }]);
    if (container.querySelector(`.clocked-instruction[data-instruction="${name}"]`) !== null) {
      list.push([`button ${name}`, moves, () => {
        container.querySelector<HTMLButtonElement>(`.clocked-instruction[data-instruction="${name}"]`)!.click();
      }]);
    }
  }
  if (container.querySelector('.clocked-reset') !== null) {
    list.push(['panel reset', null, () => {
      container.querySelector<HTMLButtonElement>('.clocked-reset')!.click();
    }]);
  }
  if (clocked) {
    list.push(['clock played', null, (h) => { h.viewer.machine()!.setClockPlaying(true); }]);
    list.push(['clock paused', null, (h) => { h.viewer.machine()!.setClockPlaying(false); }]);
  }
  return list;
}

async function generatedStep(g: Generated): Promise<void> {
  const drag = g.drag;
  const ends: Action[] = [];
  const holding: Action[] = [];
  const free: Action[] = [];
  const shown = inputsShown();
  // Pressing a slider: on its thumb, on its track, or on a pinned thumb.
  if (shown.length > 0) {
    const id = g.pick(shown);
    const target = slider(id);
    const press = (kind: 'thumb' | 'track' | 'pinned'): Action => [`press ${kind} ${id}`, async (h) => {
      if (kind === 'pinned') {
        const [, max] = RANGES[id];
        try { h.viewer.machine()!.move(id, { to: max + 1 }); } catch { /* refused */ }
      }
      const pressed = kind === 'pinned' ? slider(id) : target;
      const previous = h.drag;
      pointerOn(pressed, 'pointerdown');
      pressed.focus();
      if (previous !== null) {
        previous.endedAt = log().length;
        await finished(h, false, false);
      }
      const started = beginDrag(h, id, pressed, kind === 'thumb' ? 'followed' : 'drawn');
      h.drag = started;
      if (started === null) return;
      if (kind === 'track') dispatchPosition(h, false);
      if (kind === 'pinned') dispatchPosition(h, true);
    }];
    if (drag === null || g.random() < 0.15) {
      free.push(press('thumb'), press('track'));
      if (g.name !== 'fine.json' && id !== 'press') free.push(press('pinned'));
    }
  }
  if (drag !== null && drag.held) {
    holding.push(['position', (h) => { dispatchPosition(h, true); }]);
    holding.push(['positions', (h) => {
      const count = 2 + Math.floor(h.random() * 2);
      for (let i = 0; i < count; i += 1) dispatchPosition(h, true);
    }]);
    holding.push(['held still', async () => { await frames(3); }]);
    holding.push(['window blur', () => { window.dispatchEvent(new Event('blur')); }]);
    holding.push(['hidden and shown', async () => {
      Object.defineProperty(document, 'hidden', { configurable: true, get: () => true });
      document.dispatchEvent(new Event('visibilitychange'));
      await frames(1);
      delete (document as unknown as Record<string, unknown>).hidden;
      document.dispatchEvent(new Event('visibilitychange'));
    }]);
    const speedControl = container.querySelector<HTMLSelectElement>('.clocked-speed');
    if (speedControl !== null) {
      holding.push(['speed changed', (h) => {
        const others = [...speedControl.options].filter((one) => one.value !== speedControl.value);
        speedControl.value = h.pick(others).value;
        speedControl.dispatchEvent(new Event('change', { bubbles: true }));
      }]);
    }
    holding.push(['second pointer', (h) => {
      pointerOn(h.drag!.slider, 'pointerdown', { pointerId: 7, pointerType: 'touch' });
      pointerOn(h.drag!.slider, 'pointerup', { pointerId: 7, pointerType: 'touch' });
      pointerOn(h.drag!.slider, 'lostpointercapture', { pointerId: 7, pointerType: 'touch' });
    }]);
    ends.push(['release', async (h) => { h.drag!.held = false; letGo(h.drag!.slider); await finished(h); }]);
    ends.push(['release elsewhere', async (h) => {
      h.drag!.held = false;
      pointerOn(document.body, 'pointerup');
      if (h.random() < 0.5) change(h.drag!.slider);
      await finished(h);
    }]);
    ends.push(['pointercancel', async (h) => {
      h.drag!.held = false; pointerOn(h.drag!.slider, 'pointercancel'); await finished(h);
    }]);
    ends.push(['lostpointercapture', async (h) => {
      h.drag!.held = false; pointerOn(h.drag!.slider, 'lostpointercapture'); await finished(h);
    }]);
    ends.push(['key', async (h) => {
      const target = h.drag!.slider;
      h.drag!.held = false;
      target.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft', bubbles: true }));
      h.drag!.endedAt = log().length;
      await finished(h, false, false);
      target.value = String(position(h, target.dataset.input!));
      target.dispatchEvent(new Event('input', { bubbles: true }));
      change(target);
    }]);
  }
  for (const [name, own, act] of doors(g)) {
    free.push([name, async (h) => {
      const held = h.drag;
      const built = bench.machines.length;
      await act(h);
      // A republish that REPLACED the machine drops the press; a reload
      // asks it first (design Decision 5).
      if (held !== null && name.startsWith('manifestChanged')
          && bench.machines.length > built) held.dropped = true;
      if (held !== null) {
        held.held = false;
        await finished(h, own === held.id, false);
      }
    }]);
  }
  if (drag === null) {
    free.push(['key on a slider', (h) => {
      if (shown.length === 0) return;
      const target = slider(h.pick(shown));
      target.focus();
      target.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
      target.value = String(position(h, target.dataset.input!));
      target.dispatchEvent(new Event('input', { bubbles: true }));
      change(target);
    }]);
    free.push(['input with no press', (h) => {
      if (shown.length === 0) return;
      const target = slider(h.pick(shown));
      const mark = requests().length;
      const was = target.value;
      valueTo(target, position(h, target.dataset.input!));
      expect(requests().length, 'an input with no press asked').toBe(mark);
      // A script's value is not the machine's, today as before: put the
      // thumb back, so A1 reads only what the viewer wrote.
      target.value = was;
    }]);
  }
  const vocabulary = drag !== null && drag.held
    ? [...holding, ...holding, ...holding, ...ends, ...free] : free;
  const [label, action] = g.pick(vocabulary);
  g.steps.push(label);
  await action(g);
}

async function generatedSequence(seed: number): Promise<void> {
  const names = ['follow.json', 'follow-clock.json', 'fine.json', 'follow-14.json',
                 'follow-instant.json'];
  const name = names[seed % names.length];
  bench.documents = new Map(Object.entries(DOCUMENTS));
  bench.log = [];
  bench.machines = [];
  const random = generator(seed);
  const viewer = await rested(name);
  const g: Generated = {
    viewer, name, random, pick: (items) => items[Math.floor(random() * items.length)],
    drag: null, steps: [String(seed)],
  };
  for (let step = 0; step < 40; step += 1) {
    await generatedStep(g);
    const where = `seed ${seed} (${name}) after ${g.steps.slice(1).join(', ')}`;
    expectPanelIsModel(g, where, true);
    const count = Math.floor(random() * 4);
    for (let i = 0; i < count; i += 1) {
      await frames(1, 1 + Math.floor(random() * 30));
      expectDrawn();
      expectPanelIsModel(g, where, true);
    }
  }
  if (g.drag !== null) {
    g.drag.held = false;
    letGo(g.drag.slider);
  }
  const machine = viewer.machine()!;
  if (machine.clock() !== null) machine.setClockPlaying(false);
  await finished(g);
  await untilRestChecked(g, `seed ${seed} at the end`, false);
  expectModelIsBank(g, `seed ${seed} at the end`);
  opened.splice(0).forEach((one) => one.dispose());
  container.replaceChildren();
}

describe('G1: generated sequences of drags, doors and gestures', () => {
  it('200 seeded sequences of 40 steps: the panel is the model, the model is the bank at rest, and every drag asked what its hand did', async () => {
    const failures: string[] = [];
    for (let seed = 1; seed <= 200; seed += 1) {
      try {
        await generatedSequence(seed);
      } catch (error) {
        failures.push(String(error).slice(0, 900));
        opened.splice(0).forEach((one) => one.dispose());
        container.replaceChildren();
        delete (document as unknown as Record<string, unknown>).hidden;
      }
    }
    console.log(`G1: ${failures.length} of 200 sequences failed; exercised ${JSON.stringify(exercised)}`);
    expect(failures.length, failures.slice(0, 4).join('\n\n')).toBe(0);
  }, 900_000);
});
