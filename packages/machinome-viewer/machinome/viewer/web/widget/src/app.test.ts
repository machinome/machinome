/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The bench of OpenSpec `show-a-models-own-app`, design Decisions 1 to 10
// and Decision 15 (A1 to A9): the REAL `mount()` in jsdom, on the bench of
// `machine-change.test.ts`, showing a model's app.
//
// jsdom loads no script and no stylesheet, so the loader is reached through
// its seam: `app.ts`'s `mountApp` is `mountAppWith` over the page's own way
// of attaching an element, and this file mocks `mountApp` with
// `mountAppWith` over a FAKE attachment, which appends the element exactly
// as the real one does and then plays, in a later task, what a browser
// would do with it: a stylesheet loads or fails; a script runs -- it may
// dispatch `machinome:app` on its own element, carrying a start function --
// and then loads, or fails to load. Everything after the attachment is the
// real loader and the real mount.
//
// A9 needs no app at all, and runs on a base that has no `app.ts`: the mock
// below is consulted only when something imports `./app`.

import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';
import { mount } from './viewer';
import type { ViewerHandle, ViewerOptions } from './viewer';

/** What a fake script does once attached. */
type Behaviour = (element: HTMLScriptElement) => void;

interface Started {
  name: string;
  host: Record<string, unknown>;
}

const bench = vi.hoisted(() => ({
  now: 0,
  width: 800,
  height: 600,
  loop: undefined as ((timestamp: number) => void) | null | undefined,
  observers: [] as Array<{
    callback: (entries: unknown[], observer: unknown) => void;
    self: unknown; targets: Set<unknown>;
  }>,
  documents: new Map<string, string>(),
  /** By the `src` a script element was given. */
  scripts: new Map<string, (element: HTMLScriptElement) => void>(),
  /** By the `href` a stylesheet link was given: 'load' unless said. */
  sheets: new Map<string, 'load' | 'error' | 'pending'>(),
  /** Every element attached, in order, by its URL. */
  attached: [] as string[],
  started: [] as Array<{ name: string; host: Record<string, unknown> }>,
  disposals: [] as Array<Record<string, unknown>>,
  pending: [] as Array<() => void>,
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

// The seam (design Decision 15): `mountApp` over a fake attachment.
vi.mock('./app', async (importOriginal) => {
  const actual = await importOriginal<Record<string, unknown>>();
  const mountAppWith = actual.mountAppWith as (
    attach: (element: HTMLElement, parent: HTMLElement) => void,
    request: unknown) => unknown;
  const attach = (element: HTMLElement, parent: HTMLElement): void => {
    parent.append(element);
    if (element instanceof HTMLLinkElement) {
      const href = element.getAttribute('href') ?? '';
      bench.attached.push(href);
      const outcome = bench.sheets.get(href) ?? 'load';
      if (outcome === 'pending') return;
      queueMicrotask(() => element.dispatchEvent(new Event(outcome)));
      return;
    }
    if (element instanceof HTMLScriptElement) {
      const src = element.getAttribute('src') ?? '';
      bench.attached.push(src);
      const behaviour = bench.scripts.get(src);
      queueMicrotask(() => {
        if (behaviour === undefined) {
          element.dispatchEvent(new Event('error'));
          return;
        }
        behaviour(element);
      });
    }
  };
  return {
    ...actual,
    mountApp: (request: unknown) => mountAppWith(attach, request),
  };
});

// ---------------------------------------------------------------------
// Fake scripts.

/** Dispatch `machinome:app` on the script, as a bundle does from
 * `document.currentScript`. */
function send(element: HTMLScriptElement, detail: unknown): void {
  element.dispatchEvent(new CustomEvent('machinome:app', { detail }));
}

/** A script that starts an app named `name`: it fills `host.element` with
 * a bar of its own and a place for the picture, adopts the viewport there,
 * and returns a disposer recording what it could still read. */
function anApp(name: string, onStart?: (host: Record<string, unknown>) => void): Behaviour {
  return (element) => {
    send(element, {
      contract: 1,
      start: (host: Record<string, unknown>) => {
        bench.started.push({ name, host });
        const root = host.element as HTMLElement;
        root.innerHTML = `<div class="fake-app" data-name="${name}">`
          + '<div class="fake-picture"></div><button class="fake-key">Q</button></div>';
        root.querySelector('.fake-picture')!.append(host.viewport as HTMLElement);
        onStart?.(host);
        return () => {
          const viewer = host.viewer as ViewerHandle;
          bench.disposals.push({
            name,
            machine: viewer.machine() !== null,
            elementConnected: root.isConnected,
            canvasConnected: (host.viewport as HTMLElement)
              .querySelector('canvas')?.isConnected ?? false,
          });
          root.replaceChildren();
        };
      },
    });
    element.dispatchEvent(new Event('load'));
  };
}

const SCRIPTS: Record<string, Behaviour> = {
  './app.js': anApp('app'),
  './other.js': anApp('other'),
  './third.js': anApp('third'),
  './silent.js': (element) => { element.dispatchEvent(new Event('load')); },
  './contract-2.js': (element) => {
    send(element, { contract: 2, start: () => () => undefined });
    element.dispatchEvent(new Event('load'));
  },
  './throws.js': (element) => {
    send(element, {
      contract: 1,
      start: () => { throw new Error('the keyboard has no keys'); },
    });
    element.dispatchEvent(new Event('load'));
  },
  './refuses.js': anApp('refuses', (host) => {
    (host.refuse as (reason: string) => void)(
      'it places no <Viewport/>, so the model would not be seen');
  }),
  './pending.js': (element) => {
    bench.pending.push(() => anApp('pending')(element));
  },
};

// ---------------------------------------------------------------------
// Documents.

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

/** A clocked machine one of whose parts also turns with `$t`, so that
 * without an app it gets BOTH the clocked panel and the animation bar. */
const CLOCKED = {
  format: 'machinome-export', version: 8, animation: { fps: 30, frames: 360 },
  drivers: { press: FLOAT([0, 2], 'mm'), wheel: INT([0, 9]) },
  states: { count: INT() },
  instructions: { Push: { by: { press: 0.5 }, duration: 0.5 } },
  bindings: [],
  clocked: {
    identity: 'model-app', clock: null, own: '_own',
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
    leaf('fan', [['r', '($t * 360)', [0, 0, 1]]]),
  ]),
};

const withApp = (app: unknown) => ({ ...CLOCKED, app });

const DOCUMENTS: Record<string, unknown> = {
  'plain.json': CLOCKED,
  'app.json': withApp({ script: 'app.js', stylesheet: 'app.css' }),
  'refusal.json': withApp({ refusal: 'Enigma.app names app/index.tsx, which does not exist' }),
  'sheet-fails.json': withApp({ script: 'app.js', stylesheet: 'missing.css' }),
  'script-fails.json': withApp({ script: 'missing.js' }),
  'silent.json': withApp({ script: 'silent.js' }),
  'contract-2.json': withApp({ script: 'contract-2.js' }),
  'throws.json': withApp({ script: 'throws.js' }),
  'refuses.json': withApp({ script: 'refuses.js' }),
};

// ---------------------------------------------------------------------
// Driving the mount.

const opened: ViewerHandle[] = [];
let container: HTMLElement;

async function settle(): Promise<void> {
  for (let i = 0; i < 40; i += 1) await Promise.resolve();
}

async function frames(count: number, ms = 16): Promise<void> {
  for (let i = 0; i < count; i += 1) {
    bench.now += ms;
    const loop = bench.loop;
    if (typeof loop !== 'function') throw new Error('no animation loop installed');
    loop(bench.now);
    await settle();
  }
}

async function open(name: string, options: ViewerOptions = {}): Promise<ViewerHandle> {
  const viewer = await mount(container, name, options);
  opened.push(viewer);
  await frames(2);
  return viewer;
}

function publish(name: string, document: unknown): void {
  bench.documents.set(name, JSON.stringify(document));
}

const panel = (): Element | null => container.querySelector('.clocked-controls');
const bar = (): Element | null => container.querySelector('.animation-controls');
const canvas = (): HTMLCanvasElement => container.querySelector('canvas')!;
const viewport = (): HTMLElement | null => container.querySelector('.machinome-viewport');
const appElement = (): HTMLElement | null => container.querySelector('.machinome-app');
const notice = (): HTMLElement | null => container.querySelector('.machinome-app-refusal');
const sheets = (): HTMLLinkElement[] => [...document.head.querySelectorAll<HTMLLinkElement>(
  'link[rel="stylesheet"]')];

/** The targets the viewer's own observer watches. */
function observed(): Set<unknown> {
  const watching = bench.observers.filter((one) => one.targets.size > 0);
  expect(watching, 'one observer watches').toHaveLength(1);
  return watching[0].targets;
}

beforeEach(() => {
  bench.now = 1000;
  bench.width = 800;
  bench.height = 600;
  bench.loop = undefined;
  bench.observers = [];
  bench.documents = new Map(Object.entries(DOCUMENTS)
    .map(([name, document]) => [name, JSON.stringify(document)]));
  bench.scripts = new Map(Object.entries(SCRIPTS));
  bench.sheets = new Map([['./missing.css', 'error']]);
  bench.attached = [];
  bench.started = [];
  bench.disposals = [];
  bench.pending = [];
  vi.spyOn(performance, 'now').mockImplementation(() => bench.now);
  vi.stubGlobal('fetch', async (url: string) => {
    const text = bench.documents.get(String(url));
    if (text === undefined) return { ok: false, status: 404, json: async () => null };
    return { ok: true, status: 200, json: async () => JSON.parse(text) };
  });
  vi.stubGlobal('ResizeObserver', class {
    private readonly entry: { callback: (entries: unknown[], observer: unknown) => void;
                              self: unknown; targets: Set<unknown> };
    constructor(callback: (entries: unknown[], observer: unknown) => void) {
      this.entry = { callback, self: this, targets: new Set() };
      bench.observers.push(this.entry);
    }
    observe(target: unknown): void { this.entry.targets.add(target); }
    unobserve(target: unknown): void { this.entry.targets.delete(target); }
    disconnect(): void { this.entry.targets.clear(); }
  });
  container = document.createElement('div');
  Object.defineProperty(container, 'clientWidth', { get: () => bench.width });
  Object.defineProperty(container, 'clientHeight', { get: () => bench.height });
  document.body.append(container);
});

afterEach(() => {
  opened.splice(0).forEach((viewer) => viewer.dispose());
  document.body.replaceChildren();
  document.head.replaceChildren();
  Object.defineProperty(document, 'fullscreenEnabled', { value: false, configurable: true });
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

// ---------------------------------------------------------------------
// A1 to A9.

describe('A1: a document with an app shows the app in place of the panel', () => {
  it('A1: no clocked panel and no animation bar are built, and the app fills the container', async () => {
    const viewer = await open('app.json');
    expect(bench.started.map((one) => one.name)).toEqual(['app']);
    expect(panel()).toBeNull();
    expect(bar()).toBeNull();
    const element = appElement();
    expect(element).not.toBeNull();
    expect(element!.parentElement).toBe(container);
    expect(element!.style.position).toBe('absolute');
    expect([element!.style.width, element!.style.height]).toEqual(['100%', '100%']);
    expect(element!.querySelector('.fake-app')).not.toBeNull();
    // The host is the contract's, and the handle is the mount's own.
    const { host } = bench.started[0];
    expect(host.contract).toBe(1);
    expect(host.element).toBe(element);
    expect(host.viewer).toBe(viewer);
    expect(typeof host.refuse).toBe('function');
    // The stylesheet is in the page, loaded before the script ran.
    expect(bench.attached).toEqual(['./app.css', './app.js']);
    expect(sheets().map((link) => link.getAttribute('href'))).toEqual(['./app.css']);
    // The script element is gone once the app started.
    expect(document.head.querySelector('script')).toBeNull();
    // The animation still plays with no bar: `$t` advances.
    expect(viewer.machine()).not.toBeNull();
  });
});

describe('A2: the picture is the viewport the app placed', () => {
  it('A2: the canvas is in the viewport, the observer watches the viewport, and the renderer takes its size', async () => {
    await open('app.json');
    const place = viewport();
    expect(place).not.toBeNull();
    expect(canvas().parentElement).toBe(place);
    expect(canvas().style.position).toBe('absolute');
    expect(place!.parentElement!.classList.contains('fake-picture')).toBe(true);
    const targets = observed();
    expect(targets.has(place)).toBe(true);
    expect(targets.has(container)).toBe(false);
    Object.defineProperty(place, 'clientWidth', { get: () => 320, configurable: true });
    Object.defineProperty(place, 'clientHeight', { get: () => 200, configurable: true });
    for (const observer of bench.observers) {
      if (observer.targets.size > 0) observer.callback([], observer.self);
    }
    expect([canvas().width, canvas().height]).toEqual([320, 200]);
  });
});

describe('A3: the full-screen control stands in the picture\'s corner', () => {
  it('A3: the corner control is inside the viewport', async () => {
    Object.defineProperty(document, 'fullscreenEnabled', { value: true, configurable: true });
    await open('app.json');
    const button = container.querySelector('.machinome-fullscreen');
    expect(button).not.toBeNull();
    expect(button!.parentElement).toBe(viewport());
  });
});

const SENTENCE = "This model's app is not shown: ";

describe('A4: an app that cannot be shown is refused in its place', () => {
  const cases: Array<[string, string, string]> = [
    ['the document records a refusal', 'refusal.json',
      'Enigma.app names app/index.tsx, which does not exist'],
    ['the stylesheet fails to load', 'sheet-fails.json',
      'missing.css could not be loaded (HTTP 404)'],
    ['the script fails to load', 'script-fails.json',
      'missing.js could not be loaded (HTTP 404)'],
    ['the script starts no app', 'silent.json',
      'silent.js is not an app this viewer can start (it sent no machinome:app event)'],
    ['the script speaks another contract', 'contract-2.json',
      'contract-2.js is not an app this viewer can start (it sent contract 2)'],
    ['the start throws', 'throws.json',
      'it failed as it started: the keyboard has no keys'],
    ['the app refuses as it starts', 'refuses.json',
      'it places no <Viewport/>, so the model would not be seen'],
  ];
  it.each(cases)('A4: %s', async (_label, name, reason) => {
    const errors = vi.spyOn(console, 'error').mockImplementation(() => undefined);
    const viewer = await open(name);
    const shown = notice();
    expect(shown, 'a notice is shown').not.toBeNull();
    expect(shown!.getAttribute('role')).toBe('alert');
    expect(shown!.textContent).toBe(SENTENCE + reason);
    expect(errors.mock.calls.map((call) => call[0])).toContain(SENTENCE + reason);
    expect(panel(), 'no panel in the app\'s place').toBeNull();
    expect(bar()).toBeNull();
    // The model fills the area: the viewport is the container's own child.
    expect(viewport()!.parentElement).toBe(container);
    expect(canvas().parentElement).toBe(viewport());
    expect(appElement(), 'no app element stands').toBeNull();
    // The machine is still whole.
    expect(viewer.machine()).not.toBeNull();
  });

  it('A4: an app that refuses after it started is taken away, then named', async () => {
    const errors = vi.spyOn(console, 'error').mockImplementation(() => undefined);
    await open('app.json');
    const { host } = bench.started[0];
    (host.refuse as (reason: string) => void)('it failed as it rendered: no window');
    await settle();
    expect(bench.disposals.map((one) => one.name)).toEqual(['app']);
    expect(notice()!.textContent).toBe(`${SENTENCE}it failed as it rendered: no window`);
    expect(errors.mock.calls.map((call) => call[0]))
      .toContain(`${SENTENCE}it failed as it rendered: no window`);
    expect(viewport()!.parentElement).toBe(container);
    expect(panel()).toBeNull();
    // A second refusal changes nothing.
    (host.refuse as (reason: string) => void)('again');
    await settle();
    expect(notice()!.textContent).toBe(`${SENTENCE}it failed as it rendered: no window`);
    expect(bench.disposals).toHaveLength(1);
  });
});

describe('A5: a malformed app record refuses the document by name', () => {
  const records: Array<[string, unknown]> = [
    ['both a script and a refusal', { script: 'app.js', refusal: 'no' }],
    ['neither', {}],
    ['a string', 'app.js'],
    ['a parent segment', { script: '../app.js' }],
    ['a rooted path', { script: '/app.js' }],
    ['a scheme', { script: 'https://example.org/app.js' }],
    ['a stylesheet that is not a string', { script: 'app.js', stylesheet: 3 }],
    ['an empty refusal', { refusal: '' }],
    ['a stylesheet beside a refusal', { refusal: 'no', stylesheet: 'app.css' }],
    ['an unknown key', { script: 'app.js', contract: 2 }],
  ];
  it.each(records)('A5: %s', async (_label, record) => {
    publish('malformed.json', withApp(record));
    await expect(mount(container, 'malformed.json')).rejects.toThrow(/the document's `app` record/);
    expect(bench.attached).toEqual([]);
  });
});

describe('A6: a host that suppresses the chrome gets no app', () => {
  it('A6: driverControls none fetches nothing of the app and builds no viewport', async () => {
    const viewer = await open('app.json', { driverControls: 'none' });
    expect(bench.attached).toEqual([]);
    expect(bench.started).toEqual([]);
    expect(appElement()).toBeNull();
    expect(viewport()).toBeNull();
    expect(panel()).toBeNull();
    expect(canvas().parentElement).toBe(container);
    expect(viewer.machine()).not.toBeNull();
  });

  it('A6: under driverControls none the record is still validated with the document', async () => {
    publish('malformed.json', withApp({ script: '../app.js' }));
    await expect(mount(container, 'malformed.json', { driverControls: 'none' }))
      .rejects.toThrow(/the document's `app` record/);
    expect(bench.attached).toEqual([]);
  });
});

describe('A7: a republish keeps or replaces the app in place', () => {
  it('A7: the same record keeps the app; another replaces it; none restores the panel; one again takes it away', async () => {
    publish('live.json', withApp({ script: 'app.js', stylesheet: 'app.css' }));
    const viewer = await open('live.json');
    const shown = canvas();
    expect(bench.started.map((one) => one.name)).toEqual(['app']);

    await viewer.manifestChanged();
    expect(bench.started.map((one) => one.name), 'kept').toEqual(['app']);
    expect(bench.disposals).toEqual([]);

    publish('live.json', withApp({ script: 'other.js' }));
    await viewer.manifestChanged();
    expect(bench.disposals.map((one) => one.name)).toEqual(['app']);
    expect(bench.started.map((one) => one.name)).toEqual(['app', 'other']);
    expect(sheets(), 'the old stylesheet is gone').toEqual([]);
    expect(appElement()!.querySelector('.fake-app')!.getAttribute('data-name')).toBe('other');
    expect(canvas(), 'the same canvas').toBe(shown);
    expect(canvas().parentElement).toBe(viewport());
    expect(panel()).toBeNull();

    publish('live.json', CLOCKED);
    await viewer.manifestChanged();
    expect(bench.disposals.map((one) => one.name)).toEqual(['app', 'other']);
    expect(appElement()).toBeNull();
    expect(panel(), 'the panel is built as for a document that never had an app').not.toBeNull();
    expect(bar()).not.toBeNull();
    expect(canvas()).toBe(shown);

    publish('live.json', withApp({ script: 'third.js' }));
    await viewer.manifestChanged();
    expect(panel()).toBeNull();
    expect(bar()).toBeNull();
    expect(bench.started.map((one) => one.name)).toEqual(['app', 'other', 'third']);

    // reload() reconciles the same way.
    publish('live.json', withApp({ refusal: 'the app does not build' }));
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    await viewer.reload();
    expect(bench.disposals.map((one) => one.name)).toEqual(['app', 'other', 'third']);
    expect(notice()!.textContent).toBe(`${SENTENCE}the app does not build`);
    expect(panel()).toBeNull();
  });
});

describe('A8: disposing the viewer disposes its app first', () => {
  it('A8: the disposer runs while the handle answers, and the stylesheet is removed', async () => {
    const viewer = await open('app.json');
    opened.splice(0);
    expect(sheets()).toHaveLength(1);
    viewer.dispose();
    expect(bench.disposals).toEqual([{
      name: 'app', machine: true, elementConnected: true, canvasConnected: true,
    }]);
    expect(sheets()).toEqual([]);
    expect(container.children).toHaveLength(0);
  });

  it('A8: a script still loading when the viewer is disposed never starts', async () => {
    publish('live.json', withApp({ script: 'app.js' }));
    const viewer = await open('live.json');
    opened.splice(0);
    publish('live.json', withApp({ script: 'pending.js' }));
    const changed = viewer.manifestChanged();
    await settle();
    expect(bench.pending).toHaveLength(1);
    viewer.dispose();
    await changed;
    bench.pending[0]();
    await settle();
    expect(bench.started.map((one) => one.name)).toEqual(['app']);
    expect(container.children).toHaveLength(0);
  });
});

describe('A9: a document without an app is mounted as before', () => {
  it('A9: the canvas is the container\'s child, no viewport, the observer watches the container, the panel and bar are built', async () => {
    await open('plain.json');
    expect(canvas().parentElement).toBe(container);
    expect(viewport()).toBeNull();
    expect(appElement()).toBeNull();
    expect(observed().has(container)).toBe(true);
    expect(panel()).not.toBeNull();
    expect(bar()).not.toBeNull();
    expect(bench.attached).toEqual([]);
  });
});
