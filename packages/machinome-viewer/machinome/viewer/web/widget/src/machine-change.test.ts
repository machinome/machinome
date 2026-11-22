/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The bench of OpenSpec `show-a-models-own-app`, design Decision 6 and
// Decision 15 (M1 to M8): the REAL `mount()` in jsdom, on the bench of
// `follow-the-slider.test.ts` (copied, so that no existing test file
// changes): three.js's `WebGLRenderer` replaced by a counting renderer, its
// animation loop kept and driven here frame by frame, `ResizeObserver` and
// `fetch` stubbed, the documents hand-written.
//
// What is proved is the clocked machine's change notification on the mount
// handle: `onMachineChange(listener)` is called once after every accepted
// operation that changes the committed bank or starts or ends a drawn
// transition, whoever made it, and never for a refused request; and
// `machine().drawing()` answers whether a transition is drawn now. The two
// members are read through the handle's NAMESPACE, so this file loads on a
// base that has neither of them, and each test fails there naming the
// missing member.

import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';
import { mount } from './viewer';
import type { ViewerHandle, ViewerOptions } from './viewer';

const bench = vi.hoisted(() => ({
  now: 0,
  renders: 0,
  width: 800,
  height: 600,
  loop: undefined as ((timestamp: number) => void) | null | undefined,
  observers: [] as Array<{
    callback: (entries: unknown[], observer: unknown) => void;
    self: unknown; connected: boolean;
  }>,
  documents: new Map<string, string>(),
}));

vi.mock('three', async (importOriginal) => {
  const actual = await importOriginal<typeof import('three')>();
  class CountingRenderer {
    readonly domElement: HTMLCanvasElement;
    constructor() {
      const canvas = document.createElement('canvas');
      this.domElement = canvas;
      canvas.getBoundingClientRect = () => ({
        left: 0, top: 0, x: 0, y: 0, width: bench.width, height: bench.height,
        right: bench.width, bottom: bench.height, toJSON() { return {}; },
      }) as DOMRect;
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
    }
    setSize(width: number, height: number): void {
      this.domElement.width = Math.floor(width);
      this.domElement.height = Math.floor(height);
    }
    setAnimationLoop(callback: ((timestamp: number) => void) | null): void {
      bench.loop = callback;
    }
    setPixelRatio(): void { /* one pixel a pixel */ }
    getPixelRatio(): number { return 1; }
    setOpaqueSort(): void { /* the order of drawing is not drawn here */ }
    dispose(): void { /* nothing held */ }
  }
  return { ...actual, WebGLRenderer: CountingRenderer };
});

vi.mock('three/examples/jsm/loaders/STLLoader.js', async () => {
  const actual = await vi.importActual<typeof import('three')>('three');
  return {
    STLLoader: class {
      loadAsync(): Promise<unknown> {
        return Promise.resolve(new actual.BoxGeometry(2, 3, 4));
      }
    },
  };
});

// ---------------------------------------------------------------------
// Documents, hand-written (the shapes of `follow-the-slider.test.ts`).

const FLOAT = (range: [number, number] | null, unit: string | null = null) => ({
  default: 0, range, unit, dtype: null, scale: null,
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

/** A float input on [0, 2] committing `count` at each whole number, a
 * whole-number input, and two drawn instructions. */
const CLOCKED = {
  format: 'machinome-export', version: 8, animation: { fps: 30, frames: 360 },
  drivers: { press: FLOAT([0, 2], 'mm'), wheel: INT([0, 9]) },
  states: { count: INT() },
  instructions: {
    Push: { by: { press: 0.5 }, duration: 0.5 },
    Turn: { by: { wheel: 3 }, duration: 1 },
  },
  bindings: [],
  clocked: {
    identity: 'machine-change', clock: null as string | null, own: '_own',
    commits: [{
      sources: ['press', 'count'], targets: ['count'],
      at: { primitive: 'floor', level: 'press' }, law: ['(count + 1)'],
      shapes: { press: 'affine' }, description: '(press, count) commits count',
      stated_by: 'Follow',
    }],
    bounds: [],
    limits: { crossing_tolerance: 1e-12, max_crossings: 1000 },
  },
  root: assembly('root', [
    leaf('block', [['t', ['press', '0', '0']]]),
    leaf('dial', [['t', ['wheel', 'count', '0']]]),
  ]),
};

/** The same machine declaring a clock. */
const CLOCKED_CLOCK = {
  ...CLOCKED,
  clocked: { ...CLOCKED.clocked, identity: 'machine-change-clock', clock: 'time' },
};

/** The same machine published at version 14, so that a republish whose
 * identity differs REPLACES the machine (`manifestChanged` rebuilds it for
 * version 14 only). */
const CLOCKED_14 = { ...CLOCKED, version: 14 };
const CLOCKED_14_REBUILT = {
  ...CLOCKED_14,
  clocked: { ...CLOCKED.clocked, identity: 'machine-change-rebuilt' },
};

/** A posed document: drivers and an instruction, no machine. */
const POSED = {
  format: 'machinome-export', version: 2, animation: { fps: 30, frames: 360 },
  drivers: { lift: { default: 0, range: [0, 10], unit: 'mm' } },
  instructions: { Raise: { targets: { lift: 5 }, duration: 0.2 } },
  root: assembly('root', [leaf('block', [['t', ['0', '0', 'lift']]])]),
};

const DOCUMENTS: Record<string, string> = {
  'clocked.json': JSON.stringify(CLOCKED),
  'clocked-clock.json': JSON.stringify(CLOCKED_CLOCK),
  'clocked-14.json': JSON.stringify(CLOCKED_14),
  'posed.json': JSON.stringify(POSED),
};

// ---------------------------------------------------------------------
// Driving the mount.

const opened: ViewerHandle[] = [];
let container: HTMLElement;

async function settle(): Promise<void> {
  for (let i = 0; i < 40; i += 1) await Promise.resolve();
}

/** `count` animation frames, `ms` milliseconds apart. */
async function frames(count: number, ms = 16): Promise<void> {
  for (let i = 0; i < count; i += 1) {
    bench.now += ms;
    const loop = bench.loop;
    if (typeof loop !== 'function') throw new Error('no animation loop installed');
    loop(bench.now);
    await settle();
  }
}

async function rested(name: string, options: ViewerOptions = {}): Promise<ViewerHandle> {
  const viewer = await mount(container, name, options);
  opened.push(viewer);
  await frames(2);
  return viewer;
}

/** `onMachineChange`, read through the handle's namespace: on a base that
 * has no such member this throws naming it, rather than failing to load. */
function subscribe(viewer: ViewerHandle, listener: () => void): () => void {
  const member = (viewer as unknown as Record<string, unknown>).onMachineChange;
  if (typeof member !== 'function') {
    throw new Error('the handle has no onMachineChange member');
  }
  return (member as (listener: () => void) => () => void).call(viewer, listener);
}

/** `machine().drawing()`, read the same way. */
function drawing(viewer: ViewerHandle): boolean {
  const handle = viewer.machine();
  if (handle === null) throw new Error('the document carries no machine');
  const member = (handle as unknown as Record<string, unknown>).drawing;
  if (typeof member !== 'function') {
    throw new Error('the machine handle has no drawing member');
  }
  return (member as () => boolean).call(handle);
}

/** What a listener read at each notification: the committed bank and
 * whether a transition was drawn. */
interface Heard { bank: Record<string, number>; drawing: boolean; identity: string }

function listen(viewer: ViewerHandle): Heard[] {
  const heard: Heard[] = [];
  subscribe(viewer, () => {
    const machine = viewer.machine()!;
    heard.push({ bank: machine.state(), drawing: drawing(viewer),
                 identity: machine.identity() });
  });
  return heard;
}

/** Frames until no drawing runs, then two more; throws if one never ends. */
async function untilLanded(viewer: ViewerHandle, limit = 400): Promise<void> {
  for (let i = 0; i < limit; i += 1) {
    if (!drawing(viewer)) {
      await frames(2);
      return;
    }
    await frames(1);
  }
  throw new Error('the drawing never landed');
}

beforeEach(() => {
  bench.now = 1000;
  bench.renders = 0;
  bench.width = 800;
  bench.height = 600;
  bench.loop = undefined;
  bench.observers = [];
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
// M1 to M8.

describe('M1: a request on the handle or the panel notifies once, after the bank changed', () => {
  it('M1: a host move notifies once, reading the bank the move committed', async () => {
    const viewer = await rested('clocked.json');
    const heard = listen(viewer);
    viewer.machine()!.move('press', { to: 1.2 });
    expect(heard).toHaveLength(1);
    expect(heard[0].bank).toEqual({ press: 1.2, wheel: 0, count: 1 });
    expect(heard[0].drawing).toBe(false);
    // Nothing more arrives while nothing moves.
    await frames(5);
    expect(heard).toHaveLength(1);
    // restore and reset are accepted operations that change the bank.
    const start = viewer.machine()!.snapshot();
    viewer.machine()!.move('wheel', { to: 4 });
    viewer.machine()!.restore(start);
    viewer.machine()!.reset();
    expect(heard.map((one) => one.bank)).toEqual([
      { press: 1.2, wheel: 0, count: 1 },
      { press: 1.2, wheel: 4, count: 1 },
      { press: 1.2, wheel: 0, count: 1 },
      { press: 0, wheel: 0, count: 0 },
    ]);
  });

  it('M1: a gesture on the panel notifies at the request and at the landing', async () => {
    const viewer = await rested('clocked.json');
    const heard = listen(viewer);
    const plus = container.querySelector<HTMLButtonElement>(
      '.clocked-plus[data-input="wheel"]');
    expect(plus, 'the panel has a nudge for wheel').not.toBeNull();
    plus!.click();
    expect(heard.map((one) => one.drawing)).toEqual([true]);
    expect(heard[0].bank.wheel).toBe(1);
    await untilLanded(viewer);
    expect(heard.map((one) => one.drawing)).toEqual([true, false]);
  });
});

describe('M2: a drawn instruction notifies at the request and at its last frame', () => {
  it('M2: trigger notifies with drawing() true and the bank at its end, then with drawing() false', async () => {
    const viewer = await rested('clocked.json');
    const heard = listen(viewer);
    expect(drawing(viewer)).toBe(false);
    viewer.machine()!.trigger('Push');
    expect(heard).toHaveLength(1);
    expect(heard[0]).toMatchObject({ drawing: true, bank: { press: 0.5 } });
    expect(drawing(viewer)).toBe(true);
    await frames(3);
    expect(heard, 'the frames between notify nothing').toHaveLength(1);
    await untilLanded(viewer);
    expect(heard).toHaveLength(2);
    expect(heard[1]).toMatchObject({ drawing: false, bank: { press: 0.5 } });
    await frames(5);
    expect(heard).toHaveLength(2);
  });

  it('M2: a later gesture that lands a running drawing notifies once, for itself', async () => {
    const viewer = await rested('clocked.json');
    viewer.machine()!.trigger('Push');
    await frames(3);
    const heard = listen(viewer);
    viewer.machine()!.trigger('Turn');
    expect(heard).toHaveLength(1);
    expect(heard[0]).toMatchObject({ drawing: true, bank: { press: 0.5, wheel: 3 } });
    // A host move lands the drawing and moves: one notification for both.
    viewer.machine()!.move('press', { to: 1.4 });
    expect(heard).toHaveLength(2);
    expect(heard[1]).toMatchObject({ drawing: false, bank: { press: 1.4, wheel: 3 } });
  });
});

describe('M3: a refused request notifies nobody', () => {
  it('M3: a refused move and a refused instruction notify nothing and leave the bank', async () => {
    const viewer = await rested('clocked.json');
    const heard = listen(viewer);
    const before = viewer.machine()!.state();
    expect(() => viewer.machine()!.move('handle', { by: 1 })).toThrow();
    expect(() => viewer.machine()!.trigger('Nope')).toThrow();
    expect(heard).toEqual([]);
    expect(viewer.machine()!.state()).toEqual(before);
    await frames(5);
    expect(heard).toEqual([]);
  });
});

describe('M4: the clock notifies once per played frame', () => {
  it('M4: a playing clock notifies once for each frame it advanced in', async () => {
    const viewer = await rested('clocked-clock.json');
    const heard = listen(viewer);
    viewer.machine()!.setClockPlaying(true);
    expect(heard, 'starting the transport moves nothing').toHaveLength(0);
    await frames(5);
    expect(heard).toHaveLength(5);
    const times = heard.map((one) => one.bank.time);
    expect([...times].sort((a, b) => a - b)).toEqual(times);
    expect(new Set(times).size).toBe(5);
    viewer.machine()!.setClockPlaying(false);
    await frames(5);
    expect(heard).toHaveLength(5);
  });
});

describe('M5: the subscription belongs to the mount and survives a republish', () => {
  it('M5: a republish that rebuilds the machine notifies, and the listener hears the new machine', async () => {
    const viewer = await rested('clocked-14.json');
    const heard = listen(viewer);
    viewer.machine()!.move('press', { to: 1.2 });
    expect(heard).toHaveLength(1);
    expect(heard[0].identity).toBe('machine-change');
    bench.documents.set('clocked-14.json', JSON.stringify(CLOCKED_14_REBUILT));
    await viewer.manifestChanged();
    expect(heard).toHaveLength(2);
    expect(heard[1].identity).toBe('machine-change-rebuilt');
    // Rebuilt at its initial bank.
    expect(heard[1].bank).toEqual({ press: 0, wheel: 0, count: 0 });
    viewer.machine()!.move('wheel', { to: 2 });
    expect(heard).toHaveLength(3);
    expect(heard[2]).toMatchObject({ identity: 'machine-change-rebuilt',
                                     bank: { wheel: 2 } });
  });

  it('M5: a republish that keeps the machine notifies too, and so does a reload', async () => {
    const viewer = await rested('clocked.json');
    const heard = listen(viewer);
    await viewer.manifestChanged();
    expect(heard).toHaveLength(1);
    await viewer.reload();
    expect(heard).toHaveLength(2);
  });
});

describe('M6: a throwing listener does not stop the others', () => {
  it('M6: the next listener is still notified, and a cancelled one is not', async () => {
    const viewer = await rested('clocked.json');
    const errors = vi.spyOn(console, 'error').mockImplementation(() => undefined);
    subscribe(viewer, () => { throw new Error('a listener failed'); });
    let second = 0;
    let third = 0;
    subscribe(viewer, () => { second += 1; });
    const cancel = subscribe(viewer, () => { third += 1; });
    viewer.machine()!.move('press', { to: 0.4 });
    expect(second).toBe(1);
    expect(third).toBe(1);
    expect(errors).toHaveBeenCalled();
    cancel();
    viewer.machine()!.move('press', { to: 0.6 });
    expect(second).toBe(2);
    expect(third).toBe(1);
  });
});

describe('M7: disposing the viewer notifies nobody', () => {
  it('M7: dispose() drops every listener and notifies none of them', async () => {
    const viewer = await rested('clocked.json');
    viewer.machine()!.trigger('Push');
    let heard = 0;
    subscribe(viewer, () => { heard += 1; });
    viewer.dispose();
    expect(heard).toBe(0);
  });
});

describe('M8: a document with no clocked machine never notifies', () => {
  it('M8: a posed document driven and played notifies nothing', async () => {
    const viewer = await rested('posed.json');
    let heard = 0;
    subscribe(viewer, () => { heard += 1; });
    expect(viewer.machine()).toBeNull();
    viewer.setDriver('lift', 3);
    const ramp = viewer.trigger('Raise');
    await frames(30);
    await ramp.done;
    await viewer.manifestChanged();
    await viewer.reload();
    expect(heard).toBe(0);
  });
});
