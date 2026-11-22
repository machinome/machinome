/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// A part read from a model file is drawn from its positions alone
// (OpenSpec `draw-rigid-parts-without-stored-normals`, design Decision 9,
// N1 to N6): the REAL tree, each reading handed three.js's REAL
// `STLLoader.parse` of hand-written binary STL bytes, so every geometry
// a part is given arrives with the `normal` attribute the browser's
// parse makes. `computeVertexNormals` and `deleteAttribute` are watched
// on the prototype, recording what they ran on; `parse` records the
// geometries it returns; the holder's `mesh` records every mesh made, so
// a removal can tell whether a mesh already shows its geometry.
//
// Every URL is distinct per test: the admission module is shared by the
// file, and a later load of an open reading's URL would join it.

import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const files = vi.hoisted(() => ({
  bytes: new Map<string, ArrayBuffer>(),
  actual: undefined as unknown as { new (): { parse(data: ArrayBuffer): unknown } },
}));

vi.mock('three/examples/jsm/loaders/STLLoader.js', async (importOriginal) => {
  const actual = await importOriginal<typeof import('three/examples/jsm/loaders/STLLoader.js')>();
  files.actual = actual.STLLoader as unknown as typeof files.actual;
  class WatchedLoader extends actual.STLLoader {
    // Its own, so the test's spy wraps the parse the reading calls.
    parse(data: ArrayBuffer | string): THREE.BufferGeometry {
      return super.parse(data);
    }
    async loadAsync(url: string): Promise<THREE.BufferGeometry> {
      await Promise.resolve();
      const bytes = files.bytes.get(url);
      if (bytes === undefined) throw new Error(`no file at ${url}`);
      return this.parse(bytes.slice(0));
    }
  }
  return { STLLoader: WatchedLoader };
});

import { EMPTY_BINDINGS } from './bindings';
import { GeometryBatch } from './geometry-admission';
import { MaterialPresentation } from './presentation';
import { clockedScope } from './run/pose';
import { liftDecal, WidgetTree } from './tree';
import type { ManifestMarking, ManifestNode } from './types';

// ---------------------------------------------------------------------
// Model files.

type Vertex = readonly [number, number, number];
type Facet = readonly [Vertex, Vertex, Vertex];

function binary(facets: readonly Facet[]): ArrayBuffer {
  const buffer = new ArrayBuffer(84 + 50 * facets.length);
  const view = new DataView(buffer);
  view.setUint32(80, facets.length, true);
  facets.forEach((facet, f) => {
    const at = 84 + 50 * f;
    // The file's own facet normal, deliberately wrong: what is drawn is
    // never what the file says.
    view.setFloat32(at, 0, true); view.setFloat32(at + 4, 0, true); view.setFloat32(at + 8, 1, true);
    facet.forEach((vertex, v) => vertex.forEach((c, k) => {
      view.setFloat32(at + 12 + 12 * v + 4 * k, c, true);
    }));
  });
  return buffer;
}

/** A cube of side `2 * s` about the origin, every triangle wound outward. */
function cube(s = 1): Facet[] {
  const corner = (i: number): Vertex => [i & 4 ? s : -s, i & 2 ? s : -s, i & 1 ? s : -s];
  const quads = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]];
  const facets: Facet[] = [];
  for (const [a, b, c, d] of quads) {
    facets.push([corner(a), corner(b), corner(c)], [corner(a), corner(c), corner(d)]);
  }
  return facets.map(outward);
}

/** A wedge: a triangular prism, wound outward. */
function wedge(): Facet[] {
  const p: Vertex[] = [[-1, -1, -1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [-1, 1, 1]];
  const faces = [[0, 2, 1], [3, 4, 5], [0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]];
  const facets: Facet[] = [];
  for (const face of faces) {
    for (let i = 1; i + 1 < face.length; i += 1) facets.push([p[face[0]], p[face[i]], p[face[i + 1]]]);
  }
  return facets.map(outward);
}

/** An open sheet bent over a ridge: a decal's artwork, lying on z = 1. */
function sheet(): Facet[] {
  const z = (x: number): number => 1.0 + 0.2 * (1 - Math.abs(x));
  const xs = [-0.8, -0.4, 0, 0.4, 0.8];
  const facets: Facet[] = [];
  for (let i = 0; i + 1 < xs.length; i += 1) {
    const [x0, x1] = [xs[i], xs[i + 1]];
    const a: Vertex = [x0, -0.5, z(x0)], b: Vertex = [x1, -0.5, z(x1)];
    const c: Vertex = [x1, 0.5, z(x1)], d: Vertex = [x0, 0.5, z(x0)];
    facets.push([a, b, c], [a, c, d]);
  }
  return facets;
}

function outward([a, b, c]: Facet): Facet {
  const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
  const v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
  const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
  const centre = [0, 1, 2].map((k) => (a[k] + b[k] + c[k]) / 3);
  return n[0] * centre[0] + n[1] * centre[1] + n[2] * centre[2] >= 0 ? [a, b, c] : [a, c, b];
}

const CUBE = binary(cube());
const WEDGE = binary(wedge());
const SHEET = binary(sheet());

/** Serve `name` under `at`. */
function serveFile(at: string, name: string, bytes: ArrayBuffer): void {
  files.bytes.set(at + name, bytes);
}

/** three.js's own parse of `bytes`, outside every watch. */
function freshParse(bytes: ArrayBuffer): THREE.BufferGeometry {
  return new files.actual().parse(bytes.slice(0)) as THREE.BufferGeometry;
}

// ---------------------------------------------------------------------
// What the test sees.

interface Removal { geometry: THREE.BufferGeometry; name: string; shown: boolean }

const seen = {
  parsed: [] as THREE.BufferGeometry[],
  normals: [] as THREE.BufferGeometry[],
  removals: [] as Removal[],
  meshes: [] as THREE.Mesh[],
};

function instrument(): void {
  const parse = STLLoader.prototype.parse;
  vi.spyOn(STLLoader.prototype, 'parse').mockImplementation(function (this: STLLoader, data) {
    const geometry = parse.call(this, data);
    seen.parsed.push(geometry);
    return geometry;
  });
  const normals = THREE.BufferGeometry.prototype.computeVertexNormals;
  vi.spyOn(THREE.BufferGeometry.prototype, 'computeVertexNormals').mockImplementation(
    function (this: THREE.BufferGeometry) {
      seen.normals.push(this);
      return normals.call(this);
    });
  const deleteAttribute = THREE.BufferGeometry.prototype.deleteAttribute;
  vi.spyOn(THREE.BufferGeometry.prototype, 'deleteAttribute').mockImplementation(
    function (this: THREE.BufferGeometry, name: string) {
      seen.removals.push({
        geometry: this, name, shown: seen.meshes.some((mesh) => mesh.geometry === this),
      });
      return deleteAttribute.call(this, name);
    });
  const mesh = MaterialPresentation.prototype.mesh;
  vi.spyOn(MaterialPresentation.prototype, 'mesh').mockImplementation(
    function (this: MaterialPresentation, ...args: Parameters<MaterialPresentation['mesh']>) {
      const made = mesh.apply(this, args);
      seen.meshes.push(made);
      return made;
    });
}

// ---------------------------------------------------------------------
// Documents and trees.

const part = (name: string, model: string, color: string | null, x: number,
              extra: Partial<ManifestNode> = {}): ManifestNode => ({
  name, type: 'leaf', color, operations: [['t', [String(x), '0', '0']]], model, mtime: 1, ...extra,
});
const asm = (children: ManifestNode[]): ManifestNode => ({
  name: 'root', type: 'assembly', color: null, operations: [], children,
});
const mark = (name: string, model: string, color: string): ManifestMarking => ({
  name, model, color, mtime: 1,
});

const trees: WidgetTree[] = [];
function track(tree: WidgetTree): WidgetTree {
  trees.push(tree);
  tree.loaded.catch(() => undefined);
  return tree;
}
const ownMesh = (tree: WidgetTree): THREE.Mesh =>
  tree.group.children.find((child): child is THREE.Mesh => child instanceof THREE.Mesh)!;
const partMeshes = (tree: WidgetTree): THREE.Mesh[] => tree.children.map(ownMesh);
const attributes = (geometry: THREE.BufferGeometry): string[] => Object.keys(geometry.attributes).sort();
const materialsOf = (mesh: THREE.Mesh): THREE.Material[] =>
  Array.isArray(mesh.material) ? mesh.material : [mesh.material];

/** Every file part of `tree`: positions alone, no normal computed for
 * its geometry, and a flat, front-sided material of the rigid pair. */
function expectPositionsAlone(tree: WidgetTree, label: string): void {
  for (const child of tree.children) {
    const mesh = ownMesh(child);
    expect(attributes(mesh.geometry), `${label}: ${child.name}'s attributes`).toEqual(['position']);
    expect(seen.normals.includes(mesh.geometry), `${label}: a normal computed for ${child.name}`).toBe(false);
  }
  for (const geometry of seen.normals) {
    expect(seen.parsed.includes(geometry), `${label}: a normal computed for a parse`).toBe(false);
  }
  for (const child of tree.children) expectFlat(ownMesh(child), `${label}: ${child.name}`);
}

function expectFlat(mesh: THREE.Mesh, label: string): void {
  for (const material of materialsOf(mesh)) {
    expect(material, `${label}'s material`).toSatisfy((m: THREE.Material) =>
      m instanceof THREE.MeshStandardMaterial || m instanceof THREE.MeshNormalMaterial);
    expect((material as THREE.MeshStandardMaterial).flatShading, `${label}'s flatShading`).toBe(true);
    expect(material.side, `${label}'s side`).toBe(THREE.FrontSide);
  }
}

beforeEach(() => instrument());

afterEach(() => {
  trees.splice(0).forEach((tree) => tree.dispose());
  vi.restoreAllMocks();
  files.bytes.clear();
  seen.parsed = []; seen.normals = []; seen.removals = []; seen.meshes = [];
});

// ---------------------------------------------------------------------
// N1 to N6.

describe('draw-rigid-parts-without-stored-normals: the real tree', () => {
  it('N1: a mount\'s file parts hold positions alone, their normals removed once a reading before any mesh shows them, on flat materials', async () => {
    const at = 'http://normals.test/n1/';
    serveFile(at, 'cube.stl', CUBE);
    serveFile(at, 'wedge.stl', WEDGE);
    const tree = track(new WidgetTree(asm([
      part('a', 'cube.stl', '#c08040', 0), part('b', 'wedge.stl', '#4080c0', 3),
      part('c', 'cube.stl', null, 6), part('d', 'wedge.stl', '#40c080', 9),
    ]), at, null, EMPTY_BINDINGS, new GeometryBatch(), new MaterialPresentation()));
    await tree.loaded;
    expectPositionsAlone(tree, 'mount');
    // One reading a file, each the geometry its parse returned.
    expect(seen.parsed).toHaveLength(2);
    const shown = partMeshes(tree).map((mesh) => mesh.geometry);
    expect(new Set(shown)).toEqual(new Set(seen.parsed));
    for (const geometry of seen.parsed) {
      const removals = seen.removals.filter((removal) => removal.geometry === geometry);
      expect(removals.map((removal) => removal.name), 'the reading\'s removals').toEqual(['normal']);
      expect(removals[0].shown, 'a mesh showed the geometry when its normals were removed').toBe(false);
    }
    const [a, , c] = partMeshes(tree);
    expect(a.material).toBeInstanceOf(THREE.MeshStandardMaterial);
    expect(c.material).toBeInstanceOf(THREE.MeshNormalMaterial);
  });

  it('N2: a reload, a reconcile, an artifact update and a second viewer\'s copy hold positions alone, on flat materials', async () => {
    const at = 'http://normals.test/n2/';
    serveFile(at, 'cube.stl', CUBE);
    serveFile(at, 'wedge.stl', WEDGE);
    const doc = asm([
      part('a', 'cube.stl', '#c08040', 0), part('b', 'wedge.stl', '#4080c0', 3),
      part('c', 'cube.stl', null, 6), part('d', 'wedge.stl', '#40c080', 9),
    ]);
    const holder = new MaterialPresentation();
    const first = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, undefined, holder));
    await first.loaded;
    expectPositionsAlone(first, 'mount');

    // The path `reload()` takes: a new tree with the same holder, then
    // the old one disposed.
    const parsesBefore = seen.parsed.length;
    const tree = track(new WidgetTree(doc, at, null, EMPTY_BINDINGS, undefined, holder));
    await tree.loaded;
    first.dispose();
    expect(seen.parsed.length).toBeGreaterThan(parsesBefore);
    expectPositionsAlone(tree, 'reload');

    // A reconcile: a's mtime moved, a part added naming a file on screen,
    // the colourless part given a colour and another part none (the
    // replacement of `setColor`).
    await tree.reconcile(asm([
      part('a', 'cube.stl', '#c08040', 0, { mtime: 2 }), part('b', 'wedge.stl', null, 3),
      part('c', 'cube.stl', '#2060a0', 6), part('d', 'wedge.stl', '#40c080', 9),
      part('e', 'wedge.stl', '#a02060', 12),
    ]), at);
    expect(tree.children.map((child) => child.name)).toEqual(['a', 'b', 'c', 'd', 'e']);
    expect(ownMesh(tree.children[1]).material).toBeInstanceOf(THREE.MeshNormalMaterial);
    expect(ownMesh(tree.children[2]).material).toBeInstanceOf(THREE.MeshStandardMaterial);
    expectPositionsAlone(tree, 'reconcile');

    // An artifact update of one file.
    const shownBefore = ownMesh(tree.children[1]).geometry;
    await tree.artifactChanged('wedge.stl', at);
    expect(ownMesh(tree.children[1]).geometry).not.toBe(shownBefore);
    expectPositionsAlone(tree, 'artifactChanged');

    // A second viewer in the same batch: its geometry is the reading's
    // copy, not the first viewer's object.
    const both = 'http://normals.test/n2-second/';
    serveFile(both, 'cube.stl', CUBE);
    serveFile(both, 'wedge.stl', WEDGE);
    const batch = new GeometryBatch();
    const one = track(new WidgetTree(doc, both, null, EMPTY_BINDINGS, batch, new MaterialPresentation()));
    const two = track(new WidgetTree(doc, both, null, EMPTY_BINDINGS, batch, new MaterialPresentation()));
    await Promise.all([one.loaded, two.loaded]);
    expectPositionsAlone(one, 'first viewer');
    expectPositionsAlone(two, 'second viewer');
    const firsts = partMeshes(one).map((mesh) => mesh.geometry);
    const seconds = partMeshes(two).map((mesh) => mesh.geometry);
    firsts.forEach((geometry, i) => {
      expect(seconds[i]).not.toBe(geometry);
      expect(seen.parsed.includes(geometry), 'the first viewer holds the parse').toBe(true);
      expect(seen.parsed.includes(seconds[i]), 'the second viewer holds a copy').toBe(false);
    });
  });

  it('N3: in every look a coloured and a colourless part point only at flat, front-sided materials, and back at their plain ones', async () => {
    const at = 'http://normals.test/n3/';
    serveFile(at, 'cube.stl', CUBE);
    const holder = new MaterialPresentation();
    const tree = track(new WidgetTree(asm([
      part('coloured', 'cube.stl', '#c08040', 0), part('colourless', 'cube.stl', null, 3),
      part('other', 'cube.stl', '#4080c0', 6),
    ]), at, null, EMPTY_BINDINGS, undefined, holder));
    await tree.loaded;
    const meshes = partMeshes(tree);
    const plain = meshes.map((mesh) => mesh.material);
    const [coloured, colourless, other] = meshes;
    const looks: Array<[string, () => void]> = [['plain', () => undefined]];
    for (const target of [coloured, colourless]) {
      const rest = meshes.filter((mesh) => mesh !== target);
      const name = target === coloured ? 'coloured' : 'colourless';
      looks.push([`${name} hovered`, () => holder.setHover([target])]);
      for (const mode of ['keep', 'dim', 'ghost'] as const) {
        looks.push([`${name} lit, others ${mode}`, () => holder.setHighlight({
          lit: [target], others: rest, color: '#ffb000', mode })]);
        looks.push([`${name} among the others ${mode}`, () => holder.setHighlight({
          lit: [other === target ? coloured : other], others: meshes.filter((mesh) => mesh !== other),
          color: '#00ff00', mode })]);
        looks.push([`${name} among the others ${mode}, hovered`, () => holder.setHover([target])]);
        looks.push(['put back', () => { holder.setHighlight(null); holder.setHover([]); }]);
      }
    }
    for (const [label, apply] of looks) {
      apply();
      meshes.forEach((mesh, i) => expectFlat(mesh, `${label}: part ${i}`));
      if (label === 'put back') meshes.forEach((mesh, i) => expect(mesh.material).toBe(plain[i]));
    }
    // The looks reached variants at all.
    holder.setHighlight({ lit: [colourless], others: [coloured, other], color: '#ffb000', mode: 'ghost' });
    expect(coloured.material).not.toBe(plain[0]);
    expectFlat(coloured, 'ghosted');
    holder.setHighlight({ lit: [coloured], others: [colourless, other], color: '#ffb000', mode: 'dim' });
    expect(coloured.material).not.toBe(plain[0]);
    expectFlat(coloured, 'lit');
    holder.setHighlight(null);
    meshes.forEach((mesh, i) => expect(mesh.material).toBe(plain[i]));
  });

  it('N4: a marking keeps its welded, smoothed and lifted decal and its material, its part holding positions alone', async () => {
    const at = 'http://normals.test/n4/';
    serveFile(at, 'cube.stl', CUBE);
    serveFile(at, 'sheet.stl', SHEET);
    const tree = track(new WidgetTree(asm([
      part('p', 'cube.stl', '#888888', 0, {
        markings: [mark('own', 'cube.stl', '#ffffff'), mark('art', 'sheet.stl', '#c0c0c0')],
      }),
    ]), at));
    await tree.loaded;
    const node = tree.children[0];
    const sources = { own: CUBE, art: SHEET } as Record<string, ArrayBuffer>;
    expect(node.markings.map((record) => record.name)).toEqual(['own', 'art']);
    for (const record of node.markings) {
      const geometry = record.mesh.geometry;
      expect(geometry.index, `${record.name} indexed`).not.toBeNull();
      expect(attributes(geometry), `${record.name}'s attributes`).toEqual(['normal', 'position']);
      // The base's path: a fresh parse with its normals computed, lifted.
      const fresh = freshParse(sources[record.name]);
      fresh.computeVertexNormals();
      const reference = liftDecal(fresh);
      expect(Array.from(geometry.index!.array), `${record.name}'s index`)
        .toEqual(Array.from(reference.index!.array));
      for (const name of ['position', 'normal']) {
        expect(Array.from(geometry.getAttribute(name).array), `${record.name}'s ${name}`)
          .toEqual(Array.from(reference.getAttribute(name).array));
      }
      const material = record.mesh.material as THREE.MeshStandardMaterial;
      expect(material).toBeInstanceOf(THREE.MeshStandardMaterial);
      expect(material.flatShading, `${record.name}'s flatShading`).toBe(false);
      expect(material.side).toBe(THREE.DoubleSide);
      expect(material.polygonOffset).toBe(true);
      expect(material.polygonOffsetFactor).toBe(-1);
      expect(material.polygonOffsetUnits).toBe(-1);
    }
    expect(attributes(ownMesh(node).geometry), 'the part\'s attributes').toEqual(['position']);
  });

  it('N5: a rigid and a flexible part of one colour are two appearances of two kinds, both flat', async () => {
    const at = 'http://normals.test/n5/';
    serveFile(at, 'cube.stl', CUBE);
    const holder = new MaterialPresentation();
    const spring: ManifestNode = {
      name: 'spring', type: 'part', color: '#336699', operations: [],
      flexible: {
        tech: 'molejo', params: { height: '20' },
        spec: {
          molejo: '0.1', profile: { type: 'circle', radius: 1 },
          path: [{ type: 'helix', radius: 4, turns: 2, height: { param: 'height' } }],
          loop: false, tessellation: { path: 24, profile: 8 },
        },
      },
    } as unknown as ManifestNode;
    const tree = track(new WidgetTree(asm([part('rigid', 'cube.stl', '#336699', 0), spring]),
      at, null, EMPTY_BINDINGS, undefined, holder));
    await tree.loaded;
    const counts = holder.counts();
    expect(counts.materials).toBe(2);
    expect(counts.appearances.map(({ kind, users }) => [kind, users]).sort())
      .toEqual([['flexible', 1], ['rigid', 1]]);
    const flexible = tree.children[1].group.children
      .find((child): child is THREE.Mesh => child instanceof THREE.Mesh)!;
    const rigid = ownMesh(tree.children[0]);
    expect(flexible.material).not.toBe(rigid.material);
    expect((flexible.material as THREE.MeshStandardMaterial).flatShading, 'the flexible flag').toBe(true);
    expect((rigid.material as THREE.MeshStandardMaterial).flatShading, 'the rigid flag').toBe(true);
  });

  it('N6: a ray through the tree reaches what it reaches through twins holding today\'s normals', async () => {
    const at = 'http://normals.test/n6/';
    serveFile(at, 'cube.stl', CUBE);
    serveFile(at, 'wedge.stl', WEDGE);
    const tree = track(new WidgetTree(asm([
      part('a', 'cube.stl', '#c08040', 0), part('b', 'wedge.stl', '#4080c0', 3),
      part('c', 'cube.stl', null, 6, { operations: [['r', '30', [1, 1, 0]], ['t', ['6', '0', '0']]] }),
    ]), at));
    await tree.loaded;
    tree.update(clockedScope({}, 0, EMPTY_BINDINGS));
    tree.group.updateMatrixWorld(true);
    const meshes = partMeshes(tree);
    const twins = new THREE.Group();
    const partOf = new Map<THREE.Object3D, THREE.Mesh>();
    for (const mesh of meshes) {
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', (mesh.geometry.getAttribute('position') as THREE.BufferAttribute).clone());
      geometry.computeVertexNormals();
      const twin = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial());
      twin.matrixAutoUpdate = false;
      twin.matrix.copy(mesh.matrixWorld);
      twins.add(twin);
      partOf.set(twin, mesh);
    }
    twins.updateMatrixWorld(true);
    const ray = new THREE.Raycaster();
    for (const mesh of meshes) {
      let own = 0;
      const box = new THREE.Box3().setFromObject(mesh);
      for (const u of [0.2, 0.5, 0.8]) {
        for (const v of [0.2, 0.5, 0.8]) {
          const x = box.min.x + u * (box.max.x - box.min.x);
          const y = box.min.y + v * (box.max.y - box.min.y);
          for (const direction of [new THREE.Vector3(0, 0, -1), new THREE.Vector3(0.3, 0.2, -1).normalize()]) {
            ray.set(new THREE.Vector3(x, y, 0).addScaledVector(direction, -20), direction);
            const through = ray.intersectObject(tree.group, true).map((hit) => ({
              object: hit.object, distance: hit.distance, point: hit.point.toArray(),
              faceIndex: hit.faceIndex, normal: hit.face!.normal.toArray(),
            }));
            const twinned = ray.intersectObject(twins, true).map((hit) => ({
              object: partOf.get(hit.object), distance: hit.distance, point: hit.point.toArray(),
              faceIndex: hit.faceIndex, normal: hit.face!.normal.toArray(),
            }));
            expect(through).toEqual(twinned);
            own += through.filter((hit) => hit.object === mesh).length;
          }
        }
      }
      // Nine rays a direction aimed across the part; most reach it.
      expect(own).toBeGreaterThanOrEqual(9);
    }
  });
});
