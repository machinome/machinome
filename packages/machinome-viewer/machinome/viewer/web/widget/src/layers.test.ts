/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// OpenSpec `show-only-a-layer`, design Decision 11, V1 to V10: the REAL
// `mount()` in jsdom on the bench of `draw-on-change.test.ts` (three.js's
// `WebGLRenderer` replaced by a counting renderer whose animation loop is
// driven here frame by frame), over a hand-written document whose parts
// declare layers:
//
//   case                    no layer, a marking, a large box
//   circuit   [electrical]  an assembly holding
//     wire                  nothing of its own
//     lamp    [mechanical]
//     spring                a flexible part
//   lever     [mechanical]  a small box standing INSIDE the case
//   key       [electrical, mechanical]
//
// The new handle members are read through `layered()` so that this file
// loads, and fails by name, on a viewer that does not have them.

import * as THREE from 'three';
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
  scene: undefined as unknown,
  canvas: undefined as unknown,
  documents: new Map<string, string>(),
}));

vi.mock('three', async (importOriginal) => {
  const actual = await importOriginal<typeof import('three')>();
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
    }
    setSize(width: number, height: number): void {
      this.domElement.width = Math.floor(width * this.ratio);
      this.domElement.height = Math.floor(height * this.ratio);
    }
    setAnimationLoop(callback: ((timestamp: number) => void) | null): void {
      bench.loop = callback;
    }
    setPixelRatio(ratio: number): void { this.ratio = ratio; }
    getPixelRatio(): number { return this.ratio; }
    setOpaqueSort(): void { /* nothing is sorted here */ }
    dispose(): void { /* nothing held */ }
  }
  return { ...actual, WebGLRenderer: CountingRenderer };
});

// The case is a large box with the lever inside it; every other file is
// a small box, placed apart by its own translation.
vi.mock('three/examples/jsm/loaders/STLLoader.js', async () => {
  const actual = await vi.importActual<typeof import('three')>('three');
  return {
    STLLoader: class {
      loadAsync(url: string): Promise<unknown> {
        return Promise.resolve(url.endsWith('models/case.stl')
          ? new actual.BoxGeometry(20, 20, 20)
          : new actual.BoxGeometry(2, 3, 4));
      }
    },
  };
});

// ---------------------------------------------------------------------
// The document.

const ELECTRICAL = { key: 'electrical', label: 'Electrical path' };
const MECHANICAL = { key: 'mechanical', label: 'Rotor stepping' };

const leaf = (name: string, operations: unknown[], extra: Record<string, unknown> = {}) => ({
  name, type: 'LeafNode', color: '#8899aa', mtime: 1, operations,
  model: `models/${name}.stl`, ...extra,
});
const group = (name: string, children: unknown[], extra: Record<string, unknown> = {}) => ({
  name, type: 'AssemblyNode', color: null, mtime: 1, operations: [], children, ...extra,
});
const SPRING = {
  name: 'spring', type: 'LeafNode', color: '#a0a0a0', mtime: 1,
  operations: [['t', ['0', '0', '30']]],
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
const MARKS = [{ name: 'digits', model: 'models/digits.stl', color: '#FFFFFF', mtime: 1 }];

type Doc = Record<string, any>;

function layered(): Doc {
  return {
    format: 'machinome-export', version: 3, animation: { fps: 30, frames: 360 },
    drivers: { lift: { default: 0, range: [0, 12], unit: 'mm', dtype: null, scale: null } },
    instructions: {},
    layers: [ELECTRICAL, MECHANICAL],
    root: group('root', [
      leaf('case', [], { markings: MARKS }),
      group('circuit', [
        leaf('wire', [['t', ['40', '0', '0']]]),
        leaf('lamp', [['t', ['-40', '0', '0']]], { layers: ['mechanical'] }),
        SPRING,
      ], { layers: ['electrical'] }),
      leaf('lever', [], { layers: ['mechanical'] }),
      leaf('key', [['t', ['0', '40', '0']]], { layers: ['electrical', 'mechanical'] }),
    ]),
  };
}

/** The same machine without the case and the lever. */
function withoutCaseAndLever(): Doc {
  const document = layered();
  document.root.children = document.root.children.filter(
    (child: Doc) => child.name !== 'case' && child.name !== 'lever');
  return document;
}

function put(name: string, document: Doc): void {
  bench.documents.set(name, JSON.stringify(document));
}

// ---------------------------------------------------------------------
// The handle's new members, read through the namespace.

interface Layer { readonly key: string; readonly label: string }
interface Layered {
  layers(): readonly Layer[];
  layer(key: string): Layer;
  show(layer: Layer | null): void;
  navigation(): { root: string[] | null; hidden: string[][]; layer?: Layer | null };
}
const layered_ = (viewer: ViewerHandle): Layered => viewer as unknown as Layered;

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

async function rested(name: string, options: ViewerOptions = { autoplay: false }): Promise<ViewerHandle> {
  const viewer = await mount(container, name, options);
  opened.push(viewer);
  await frames(2);
  return viewer;
}

async function counted(action: () => Promise<void> | void): Promise<number> {
  const before = bench.renders;
  await action();
  return bench.renders - before;
}

function rootGroup(): THREE.Group {
  const scene = bench.scene as THREE.Scene;
  return scene.children.find((child) => child instanceof THREE.Group) as THREE.Group;
}

/** The scene group of a node, by path (the nodes of this document have
 * decals only on a leaf, which has no child nodes). */
function groupAt(path: string[], viewer: ViewerHandle): THREE.Group {
  let node = rootGroup();
  let level = viewer.assembly();
  for (const name of path) {
    const index = level.children.findIndex((child) => child.name === name);
    level = level.children[index];
    node = node.children.filter((child) => child instanceof THREE.Group)[index] as THREE.Group;
  }
  return node;
}

function visibleUp(object: THREE.Object3D): boolean {
  for (let one: THREE.Object3D | null = object; one !== null; one = one.parent) {
    if (!one.visible) return false;
  }
  return true;
}

/** Whether any mesh of the node (its own, a flexible one or a decal) or
 * of a node below it is drawn. */
function drawn(path: string[], viewer: ViewerHandle): boolean {
  let any = false;
  groupAt(path, viewer).traverse((object) => {
    if (object instanceof THREE.Mesh && visibleUp(object)) any = true;
  });
  return any;
}

/** Whether the part's own surface (a direct mesh of its group) is drawn. */
function ownDrawn(path: string[], viewer: ViewerHandle): boolean {
  return groupAt(path, viewer).children.some(
    (child) => child instanceof THREE.Mesh && visibleUp(child));
}

/** Whether a decal of the part is drawn. */
function decalDrawn(path: string[], viewer: ViewerHandle): boolean {
  let any = false;
  groupAt(path, viewer).children.forEach((child) => {
    if (child instanceof THREE.Group) {
      child.traverse((object) => {
        if (object instanceof THREE.Mesh && visibleUp(object)) any = true;
      });
    }
  });
  return any;
}

/** Every visibility flag of the scene, in traversal order. */
function flags(): boolean[] {
  const out: boolean[] = [];
  rootGroup().traverse((object) => { out.push(object.visible); });
  return out;
}

const ALL = [['case'], ['circuit', 'wire'], ['circuit', 'lamp'], ['circuit', 'spring'],
             ['lever'], ['key']];

beforeEach(() => {
  bench.now = 1000;
  bench.renders = 0;
  bench.width = 800;
  bench.height = 600;
  bench.loop = undefined;
  bench.scene = undefined;
  bench.canvas = undefined;
  bench.documents = new Map();
  put('layers.json', layered());
  vi.spyOn(performance, 'now').mockImplementation(() => bench.now);
  vi.stubGlobal('fetch', async (url: string) => {
    const text = bench.documents.get(String(url));
    if (text === undefined) return { ok: false, status: 404, json: async () => null };
    return { ok: true, status: 200, json: async () => JSON.parse(text) };
  });
  vi.stubGlobal('ResizeObserver', class {
    observe(): void { /* not resized */ }
    unobserve(): void { /* not resized */ }
    disconnect(): void { /* not resized */ }
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

describe('V1: the document\'s layers are validated', () => {
  const refused: Array<[string, (document: Doc) => void, RegExp]> = [
    ['layers that is not a list', (d) => { d.layers = {}; }, /"layers" is not a list/],
    ['an entry that is not an object', (d) => { d.layers = [ELECTRICAL, 'x']; },
     /index 1 is not an object/],
    ['an entry with no key', (d) => { d.layers = [{ label: 'x' }]; },
     /index 0 declares no key/],
    ['an entry with an empty key', (d) => { d.layers = [{ key: '', label: 'x' }]; },
     /index 0 declares no key/],
    ['an entry with no label', (d) => { d.layers = [ELECTRICAL, { key: 'm' }]; },
     /layer "m" declares no label/],
    ['a key twice', (d) => { d.layers = [ELECTRICAL, ELECTRICAL]; },
     /names the key "electrical" twice/],
    ['a node\'s layers that is not a list', (d) => { d.root.children[1].layers = 'electrical'; },
     /node "root\/circuit".*"layers" is not a list/],
    ['a node\'s layer twice', (d) => { d.root.children[3].layers = ['mechanical', 'mechanical']; },
     /node "root\/key".*"mechanical" twice/],
    ['a node\'s key that is not a string', (d) => { d.root.children[3].layers = [3]; },
     /node "root\/key".*not a string/],
    ['a node naming a layer the list does not hold', (d) => { d.root.children[2].layers = ['optical']; },
     /node "root\/lever" names the layer "optical", which the document's "layers" does not list/],
    ['a node naming a layer where there is no list', (d) => { delete d.layers; },
     /names the layer "electrical", which the document's "layers" does not list/],
  ];

  it.each(refused)('refuses %s by name', async (_name, edit, pattern) => {
    const document = layered();
    edit(document);
    put('bad.json', document);
    await expect(mount(container, 'bad.json', { autoplay: false })).rejects.toThrow(pattern);
  });

  it('mounts a document with no layers as it mounts today', async () => {
    const document = layered();
    delete document.layers;
    document.root.children.forEach((child: Doc) => { delete child.layers; });
    document.root.children[1].children.forEach((child: Doc) => { delete child.layers; });
    put('plain.json', document);
    const viewer = await rested('plain.json');
    ALL.forEach((path) => expect(drawn(path, viewer), path.join('/')).toBe(true));
    expect(flags().every(Boolean)).toBe(true);
  });
});

describe('V2: the handle answers the layers', () => {
  it('answers the list in order, frozen, with the same objects until it differs', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    const list = handle.layers();
    expect(list).toEqual([ELECTRICAL, MECHANICAL]);
    expect(Object.isFrozen(list)).toBe(true);
    list.forEach((one) => expect(Object.isFrozen(one)).toBe(true));
    expect(handle.layers()).toBe(list);

    await viewer.manifestChanged();
    expect(handle.layers(), 'an equal list on a republish').toBe(list);
    expect(handle.layers()[0]).toBe(list[0]);

    const renamed = layered();
    renamed.layers = [{ ...ELECTRICAL, label: 'Wiring' }, MECHANICAL];
    put('layers.json', renamed);
    await viewer.manifestChanged();
    expect(handle.layers()).not.toBe(list);
    expect(handle.layers()[0].label).toBe('Wiring');
  });

  it('answers [] for a document with none', async () => {
    const document = layered();
    delete document.layers;
    document.root.children.forEach((child: Doc) => { delete child.layers; });
    document.root.children[1].children.forEach((child: Doc) => { delete child.layers; });
    put('plain.json', document);
    const viewer = await rested('plain.json');
    expect(layered_(viewer).layers()).toEqual([]);
  });

  it('answers a layer by key, and refuses an unknown key by name', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    expect(handle.layer('electrical')).toBe(handle.layers()[0]);
    expect(() => handle.layer('optical')).toThrow(
      /Unknown layer 'optical': this document declares the layers electrical, mechanical/);
    expect(() => handle.layer('toString')).toThrow(/Unknown layer 'toString'/);
  });

  it('names the absence when the document declares none', async () => {
    const document = layered();
    delete document.layers;
    document.root.children.forEach((child: Doc) => { delete child.layers; });
    document.root.children[1].children.forEach((child: Doc) => { delete child.layers; });
    put('plain.json', document);
    const viewer = await rested('plain.json');
    expect(() => layered_(viewer).layer('x')).toThrow(/Unknown layer 'x': this document declares no layer/);
  });
});

describe('V3: showing a layer shows only the parts on it', () => {
  it('draws the parts on the electrical layer and no other, markings included', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    ALL.forEach((path) => expect(drawn(path, viewer), path.join('/')).toBe(true));
    expect(decalDrawn(['case'], viewer)).toBe(true);

    handle.show(handle.layer('electrical'));
    for (const path of [['circuit', 'wire'], ['circuit', 'lamp'], ['circuit', 'spring'], ['key']]) {
      expect(drawn(path, viewer), path.join('/')).toBe(true);
    }
    expect(ownDrawn(['circuit', 'spring'], viewer)).toBe(true);
    expect(drawn(['case'], viewer)).toBe(false);
    expect(ownDrawn(['case'], viewer)).toBe(false);
    expect(decalDrawn(['case'], viewer)).toBe(false);
    expect(drawn(['lever'], viewer)).toBe(false);
  });

  it('draws the mechanical layer: its own parts, none of the wires', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('mechanical'));
    expect(drawn(['lever'], viewer)).toBe(true);
    expect(drawn(['key'], viewer)).toBe(true);
    expect(drawn(['circuit', 'lamp'], viewer)).toBe(true);
    expect(drawn(['circuit', 'wire'], viewer)).toBe(false);
    expect(drawn(['circuit', 'spring'], viewer)).toBe(false);
    expect(drawn(['case'], viewer)).toBe(false);
  });

  it('draws everything again for null', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    const before = flags();
    handle.show(handle.layer('electrical'));
    handle.show(null);
    expect(flags()).toEqual(before);
    expect(decalDrawn(['case'], viewer)).toBe(true);
  });
});

describe('V3: the two rules of design Decision 4, read flag by flag', () => {
  it('a part\'s own surface and its decals carry the layer term themselves', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('electrical'));
    const flag = groupAt(['case'], viewer).children.find((child) => child instanceof THREE.Group)!;
    // The case is on no layer: its own flags say so, not only its group's.
    expect(flag.visible, 'the decals\' own flag').toBe(false);
    const own = groupAt(['case'], viewer).children.find((child) => child instanceof THREE.Mesh)!;
    expect(own.visible, 'the case\'s own mesh flag').toBe(false);
    handle.show(null);
    expect(flag.visible).toBe(true);
    expect(own.visible).toBe(true);
  });

  it('a part off the layer with a part on it below it draws only the part on it', async () => {
    const document = layered();
    document.layers = [ELECTRICAL];
    document.root.children = [
      group('hub', [leaf('pin', [['t', ['30', '0', '0']]], { layers: ['electrical'] })],
            { model: 'models/hub.stl', color: '#8899aa' }),
      leaf('bar', [['t', ['0', '30', '0']]]),
    ];
    put('hub.json', document);
    const viewer = await rested('hub.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('electrical'));
    expect(ownDrawn(['hub'], viewer), 'the hub\'s own mesh').toBe(false);
    expect(drawn(['hub', 'pin'], viewer)).toBe(true);
    expect(drawn(['bar'], viewer)).toBe(false);
    handle.show(null);
    expect(ownDrawn(['hub'], viewer)).toBe(true);
    expect(drawn(['bar'], viewer)).toBe(true);
  });
});

describe('V4: show refuses what is not a layer, changing nothing', () => {
  it('refuses a string and an unknown key, flags and subscribers untouched', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('electrical'));
    const before = flags();
    const heard = vi.fn();
    viewer.onAssemblyChange(heard);
    const renders = bench.renders;
    expect(() => handle.show('electrical' as unknown as Layer)).toThrow(
      /show\(\) takes a layer from layers\(\) or layer\(key\), or null; it was given the string 'electrical'/);
    expect(() => handle.show({ key: 'optical', label: 'x' })).toThrow(/Unknown layer 'optical'/);
    expect(() => handle.show(undefined as unknown as Layer)).toThrow(/show\(\) takes a layer/);
    expect(flags()).toEqual(before);
    expect(heard).not.toHaveBeenCalled();
    expect(bench.renders).toBe(renders);
    expect(handle.navigation().layer).toEqual(ELECTRICAL);
  });
});

describe('V5: a part off the layer is absent', () => {
  it('has no on-screen position, is not reached, and is not framed', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    expect(viewer.partOnScreen(['case'])).not.toBeNull();
    // The lever stands inside the case: nothing of it can be reached.
    expect(viewer.partOnScreen(['lever'])!.point).toBeNull();

    handle.show(handle.layer('electrical'));
    expect(viewer.partOnScreen(['case'])).toBeNull();
    expect(viewer.partOnScreen(['lever'])).toBeNull();
    expect(viewer.partOnScreen(['circuit', 'wire'])).not.toBeNull();
    expect(viewer.partOnScreen(['key'])).not.toBeNull();

    handle.show(handle.layer('mechanical'));
    expect(viewer.partOnScreen(['case'])).toBeNull();
    // With the case gone, what a press reaches there is the lever.
    expect(viewer.partOnScreen(['lever'])!.point).not.toBeNull();

    handle.show(null);
    expect(viewer.partOnScreen(['case'])).not.toBeNull();
  });

  it('frames what is drawn: the camera of the same machine without the case and the lever', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    viewer.setRoot(['circuit']);
    viewer.setRoot(null);
    const whole = viewer.view();
    handle.show(handle.layer('electrical'));
    viewer.setRoot(['circuit']);
    viewer.setRoot(null);
    const framed = viewer.view();
    expect(framed).not.toEqual(whole);
    // The same machine without the two parts, framed by the same calls.
    put('trimmed.json', withoutCaseAndLever());
    container = document.createElement('div');
    Object.defineProperty(container, 'clientWidth', { get: () => bench.width });
    Object.defineProperty(container, 'clientHeight', { get: () => bench.height });
    document.body.append(container);
    const trimmed = await rested('trimmed.json');
    trimmed.setRoot(['circuit']);
    trimmed.setRoot(null);
    expect(framed).toEqual(trimmed.view());
  });

  it('does not move the camera when a layer is shown', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    const before = viewer.view();
    handle.show(handle.layer('electrical'));
    expect(viewer.view()).toEqual(before);
    handle.show(null);
    expect(viewer.view()).toEqual(before);
  });
});

describe('V6: one draw per show, nothing while still', () => {
  it('draws once inside show and not at all over the still frames after', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    await frames(1);
    for (const layer of [handle.layer('electrical'), null, handle.layer('mechanical')]) {
      expect(await counted(() => handle.show(layer))).toBe(1);
      expect(await counted(() => frames(10))).toBe(0);
    }
  });
});

describe('V7: the layer composes with focus and hiding', () => {
  it('hiding, then showing a layer, keeps the part hidden and listed', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    viewer.setVisible(['key'], false);
    handle.show(handle.layer('electrical'));
    expect(drawn(['key'], viewer)).toBe(false);
    expect(handle.navigation().hidden).toEqual([['key']]);
    handle.show(null);
    expect(drawn(['key'], viewer)).toBe(false);
    expect(handle.navigation().hidden).toEqual([['key']]);
    expect(drawn(['case'], viewer)).toBe(true);
  });

  it('showing a part the layer leaves out draws nothing; the whole machine then draws it', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    viewer.setVisible(['case'], false);
    handle.show(handle.layer('electrical'));
    viewer.setVisible(['case'], true);
    expect(drawn(['case'], viewer)).toBe(false);
    expect(handle.navigation().hidden).toEqual([]);
    handle.show(null);
    expect(drawn(['case'], viewer)).toBe(true);
  });

  it('a focus under a layer draws only that subtree\'s parts on it, and the layer survives', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    viewer.setVisible(['key'], false);
    handle.show(handle.layer('electrical'));
    viewer.setRoot(['circuit']);
    expect(drawn(['circuit', 'wire'], viewer)).toBe(true);
    expect(drawn(['circuit', 'lamp'], viewer)).toBe(true);
    expect(drawn(['circuit', 'spring'], viewer)).toBe(true);
    expect(drawn(['key'], viewer)).toBe(false);
    expect(drawn(['case'], viewer)).toBe(false);
    expect(handle.navigation()).toEqual({
      root: ['circuit'], hidden: [['key']], layer: ELECTRICAL,
    });
    viewer.setRoot(null);
    expect(handle.navigation().layer).toEqual(ELECTRICAL);
    viewer.setVisible(['key'], true);
    expect(handle.navigation().layer).toEqual(ELECTRICAL);
    expect(drawn(['key'], viewer)).toBe(true);
  });

  it('showing a layer leaves the focus and the hidden paths as they were', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    viewer.setRoot(['circuit']);
    viewer.setVisible(['circuit', 'wire'], false);
    handle.show(handle.layer('mechanical'));
    expect(handle.navigation()).toEqual({
      root: ['circuit'], hidden: [['circuit', 'wire']], layer: MECHANICAL,
    });
    handle.show(null);
    expect(handle.navigation()).toEqual({
      root: ['circuit'], hidden: [['circuit', 'wire']], layer: null,
    });
  });

  it('reports the layer as a copy that show takes back', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('mechanical'));
    const read = handle.navigation().layer!;
    handle.show(handle.layer('electrical'));
    expect(read).toEqual(MECHANICAL);
    handle.show(read);
    expect(handle.navigation().layer).toEqual(MECHANICAL);
    expect(handle.navigation().layer).not.toBe(handle.layer('mechanical'));
  });
});

describe('V8: the assembly reports each node\'s effective layers', () => {
  it('lists a node\'s own layers and every ancestor\'s, in the document\'s order', async () => {
    const viewer = await rested('layers.json');
    const find = (path: string[]) => {
      let node = viewer.assembly() as any;
      for (const name of path) node = node.children.find((child: any) => child.name === name);
      return node;
    };
    expect(find(['circuit']).layers).toEqual(['electrical']);
    expect(find(['circuit', 'wire']).layers).toEqual(['electrical']);
    expect(find(['circuit', 'lamp']).layers).toEqual(['electrical', 'mechanical']);
    expect(find(['circuit', 'spring']).layers).toEqual(['electrical']);
    expect(find(['lever']).layers).toEqual(['mechanical']);
    expect(find(['key']).layers).toEqual(['electrical', 'mechanical']);
    expect(find(['case']).layers).toEqual([]);
    expect(find([]).layers).toEqual([]);
  });
});

describe('V9: every accepted show is announced once', () => {
  it('notifies per call, a redundant one included, with the layer in the navigation', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    const heard: Array<Layer | null | undefined> = [];
    viewer.onAssemblyChange((change) => { heard.push((change.navigation as any).layer); });
    handle.show(handle.layer('electrical'));
    handle.show(handle.layer('electrical'));
    handle.show(null);
    expect(heard).toEqual([ELECTRICAL, ELECTRICAL, null]);
  });
});

describe('V10: a republish', () => {
  it('keeps a shown layer the new document still declares, over its new membership', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('electrical'));
    const heard = vi.fn();
    viewer.onAssemblyChange(heard);
    const next = layered();
    next.root.children[2].layers = ['electrical', 'mechanical'];
    put('layers.json', next);
    await viewer.manifestChanged();
    expect(handle.navigation().layer).toEqual(ELECTRICAL);
    expect(drawn(['lever'], viewer)).toBe(true);
    expect(drawn(['case'], viewer)).toBe(false);
    expect(heard).toHaveBeenCalledTimes(1);
  });

  it('shows the whole machine, notifying once, when the layer is gone', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('electrical'));
    const heard: Array<Layer | null | undefined> = [];
    viewer.onAssemblyChange((change) => { heard.push((change.navigation as any).layer); });
    const next = layered();
    next.layers = [MECHANICAL];
    next.root.children[1].layers = ['mechanical'];
    next.root.children[3].layers = ['mechanical'];
    put('layers.json', next);
    await viewer.manifestChanged();
    expect(handle.navigation().layer).toBeNull();
    ALL.forEach((path) => expect(drawn(path, viewer), path.join('/')).toBe(true));
    expect(heard).toEqual([null]);
  });
});

describe('V11: a republish moves the layers it inherits and the label it shows', () => {
  const find = (viewer: ViewerHandle, path: string[]) => {
    let node = viewer.assembly() as any;
    for (const name of path) node = node.children.find((child: any) => child.name === name);
    return node;
  };

  it('an existing child follows an ancestor that gains a layer', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('mechanical'));
    expect(drawn(['case'], viewer)).toBe(false);
    expect(drawn(['circuit', 'wire'], viewer)).toBe(false);
    const gain = layered();
    gain.root.children[1].layers = ['electrical', 'mechanical'];
    put('layers.json', gain);
    await viewer.manifestChanged();
    expect(find(viewer, ['circuit', 'wire']).layers).toEqual(['electrical', 'mechanical']);
    expect(drawn(['circuit', 'wire'], viewer)).toBe(true);
    expect(drawn(['circuit', 'spring'], viewer)).toBe(true);
  });

  it('an existing child follows an ancestor that loses a layer', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('electrical'));
    expect(drawn(['circuit', 'wire'], viewer)).toBe(true);
    const next = layered();
    next.root.children[1].layers = ['mechanical'];
    put('layers.json', next);
    await viewer.manifestChanged();
    expect(find(viewer, ['circuit', 'wire']).layers).toEqual(['mechanical']);
    expect(drawn(['circuit', 'wire'], viewer)).toBe(false);
    expect(drawn(['circuit', 'spring'], viewer)).toBe(false);
    expect(drawn(['circuit', 'lamp'], viewer)).toBe(false);
  });

  it('a new child inherits its ancestor\'s layers', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('electrical'));
    const next = layered();
    next.root.children[1].children.push(leaf('fuse', [['t', ['0', '0', '-40']]]));
    put('layers.json', next);
    await viewer.manifestChanged();
    expect(find(viewer, ['circuit', 'fuse']).layers).toEqual(['electrical']);
    expect(drawn(['circuit', 'fuse'], viewer)).toBe(true);
  });

  it('a shown layer\'s new label replaces the old one and the layer stays shown', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('electrical'));
    const next = layered();
    next.layers = [{ ...ELECTRICAL, label: 'Wiring' }, MECHANICAL];
    put('layers.json', next);
    await viewer.manifestChanged();
    expect(handle.navigation().layer).toEqual({ key: 'electrical', label: 'Wiring' });
    expect(drawn(['circuit', 'wire'], viewer)).toBe(true);
    expect(drawn(['case'], viewer)).toBe(false);
  });

  it('an artifact change keeps the shown layer', async () => {
    const viewer = await rested('layers.json');
    const handle = layered_(viewer);
    handle.show(handle.layer('electrical'));
    await viewer.artifactChanged('models/wire.stl');
    await frames(2);
    expect(handle.navigation().layer).toEqual(ELECTRICAL);
    expect(drawn(['circuit', 'wire'], viewer)).toBe(true);
    expect(drawn(['case'], viewer)).toBe(false);
  });
});
