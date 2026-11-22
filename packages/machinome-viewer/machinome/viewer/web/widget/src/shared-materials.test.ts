/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// Parts of one appearance share one material (OpenSpec
// `share-one-material-per-appearance`, design Decision 7).
//
// R1 to R4 count the work the change removes; O1 and O2 hold the order
// of drawing, read as the renderer reads it; P1 and P2 hold every look
// against the shipped owner, kept below as the oracle; L1 to L5 hold
// the materials' lifetime. Every export the change adds is read through
// a module's namespace, so the file loads on the base too.

import * as THREE from 'three';
import { afterEach, describe, expect, it, vi } from 'vitest';

const { loadAsync, overrides } = vi.hoisted(() => {
  const overrides = new Map<string, () => Promise<unknown>>();
  return {
    overrides,
    loadAsync: vi.fn((url: string) => {
      const once = overrides.get(url);
      if (once !== undefined) {
        overrides.delete(url);
        return once();
      }
      return Promise.resolve(new THREE.BoxGeometry());
    }),
  };
});

vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({
  STLLoader: class { loadAsync = loadAsync; },
}));

// A one-shot response a test arranged and did not use must not reach
// another test.
afterEach(() => overrides.clear());

import { WebGLRenderList } from 'three/src/renderers/webgl/WebGLRenderLists.js';
import * as presentation from './presentation';
import * as treeModule from './tree';
import * as flexibleModule from './flexible';
import { WidgetTree } from './tree';
import { bindingTable } from './bindings';
import { clockedScope } from './run/pose';
import type { Manifest, ManifestNode } from './types';

// ---------------------------------------------------------------------
// The oracle: the shipped owner and the three shipped constructors,
// copied verbatim from framework commit e72d1ae7 (`presentation.ts`
// lines 25-26, 51-61, 92-264; `tree.ts` lines 55-64 and 132-139;
// `flexible.ts` lines 431-441), before this change edited them.
// ---------------------------------------------------------------------

/** What happens to the parts a highlight does not name. */
export type OthersMode = 'keep' | 'dim' | 'ghost';

/** What a dimmed part's colour is multiplied by. */
export const DIM_FACTOR = 0.35;

/** The most opacity a ghosted part keeps. */
export const GHOST_OPACITY = 0.15;

/** The grey a hovered part's emissive colour is lifted to.
 *
 * `Color.setHex` reads sRGB and stores linear, so the lift a viewer
 * actually SEES is much smaller than the hex suggests: 0x333333
 * measured about 10/255 on the acceptance model's own materials, which
 * is not the "visible change" the spec asks for. 0x777777 measures
 * about 60/255 there -- unmistakable beside the parts around it, and
 * still a grey rather than a colour of its own. */
export const HOVER_EMISSIVE = 0x777777;

/** The standing highlight, resolved to the meshes it reaches now. */
export interface HighlightState {
  lit: readonly THREE.Mesh[];
  others: readonly THREE.Mesh[];
  color: string;
  mode: OthersMode;
}

interface Base {
  emissive: THREE.Color | null;
  color: THREE.Color | null;
  transparent: boolean;
  opacity: number;
  depthWrite: boolean;
}

type Paintable = THREE.Material & { color?: unknown; emissive?: unknown };

function materialsOf(mesh: THREE.Mesh): THREE.Material[] {
  return Array.isArray(mesh.material) ? mesh.material : [mesh.material];
}

function colourOf(value: unknown): THREE.Color | null {
  return value instanceof THREE.Color ? value : null;
}

/** The ONE writer of a material's `emissive`, `color`, `transparent`,
 * `opacity` and `depthWrite` outside material construction. */
export class MaterialPresentation {
  private readonly bases = new Map<THREE.Material, Base>();
  private hovered = new Set<THREE.Mesh>();
  private highlight: {
    lit: Set<THREE.Mesh>; others: Set<THREE.Mesh>;
    color: THREE.Color; mode: OthersMode;
  } | null = null;

  /** Change the declared model color, then compose the standing overlays
   * from that base. Never read a dimmed/highlighted visible color as base. */
  setBaseColor(mesh: THREE.Mesh, color: string): void {
    for (const material of materialsOf(mesh)) {
      const base = this.bases.get(material) ?? this.record(material);
      base.color?.set(color);
    }
    this.present(new Set([mesh]));
  }

  /** The meshes the hover lift stands on; `[]` lifts nothing. */
  setHover(meshes: readonly THREE.Mesh[]): void {
    const touched = this.touched();
    this.hovered = new Set(meshes);
    this.present(touched);
  }

  /** The standing highlight, or null for none. */
  setHighlight(state: HighlightState | null): void {
    const touched = this.touched();
    this.highlight = state === null ? null : {
      lit: new Set(state.lit),
      others: new Set(state.others),
      color: new THREE.Color(state.color),
      mode: state.mode,
    };
    this.present(touched);
  }

  /** Write every base back and drop every record and overlay: run before
   * meshes or materials are replaced. */
  forget(): void {
    for (const [material, base] of this.bases) {
      this.write(material, base, base);
    }
    this.bases.clear();
    this.hovered = new Set();
    this.highlight = null;
  }

  /** Drop every record and overlay WITHOUT writing: for a disposed
   * mount, whose materials are disposed with its tree. */
  drop(): void {
    this.bases.clear();
    this.hovered = new Set();
    this.highlight = null;
  }

  /** Whether a mesh is drawn as a ghost now (design D5). */
  isGhosted(mesh: THREE.Mesh): boolean {
    const highlight = this.highlight;
    return highlight !== null && highlight.mode === 'ghost'
      && highlight.others.has(mesh) && !highlight.lit.has(mesh);
  }

  /** Every mesh an overlay stands on now. */
  private touched(): Set<THREE.Mesh> {
    const meshes = new Set(this.hovered);
    if (this.highlight !== null) {
      this.highlight.lit.forEach((mesh) => meshes.add(mesh));
      if (this.highlight.mode !== 'keep') {
        this.highlight.others.forEach((mesh) => meshes.add(mesh));
      }
    }
    return meshes;
  }

  /** Present every mesh an overlay stood on before or stands on now. */
  private present(before: Set<THREE.Mesh>): void {
    const meshes = this.touched();
    before.forEach((mesh) => meshes.add(mesh));
    for (const mesh of meshes) {
      const highlight = this.highlight;
      const lit = highlight?.lit.has(mesh) ?? false;
      const other = !lit && highlight !== null && highlight.others.has(mesh);
      const dim = other && highlight!.mode === 'dim';
      const ghost = other && highlight!.mode === 'ghost';
      const hovered = this.hovered.has(mesh);
      for (const material of materialsOf(mesh)) {
        const recorded = this.bases.get(material);
        if (!lit && !hovered && !dim && !ghost) {
          if (recorded !== undefined) {
            this.write(material, recorded, recorded);
            this.bases.delete(material);
          }
          continue;
        }
        const base = recorded ?? this.record(material);
        const emissive = base.emissive === null ? null
          : lit ? highlight!.color
            : hovered ? new THREE.Color(HOVER_EMISSIVE) : base.emissive;
        const color = base.color === null ? null
          : dim ? base.color.clone().multiplyScalar(DIM_FACTOR) : base.color;
        this.write(material, base, {
          emissive,
          color,
          transparent: ghost ? true : base.transparent,
          opacity: ghost ? Math.min(base.opacity, GHOST_OPACITY) : base.opacity,
          depthWrite: ghost ? false : base.depthWrite,
        });
      }
    }
  }

  private record(material: THREE.Material): Base {
    const paintable = material as Paintable;
    const base: Base = {
      emissive: colourOf(paintable.emissive)?.clone() ?? null,
      color: colourOf(paintable.color)?.clone() ?? null,
      transparent: material.transparent,
      opacity: material.opacity,
      depthWrite: material.depthWrite,
    };
    this.bases.set(material, base);
    return base;
  }

  private write(material: THREE.Material, base: Base, look: Base): void {
    const paintable = material as Paintable;
    const emissive = colourOf(paintable.emissive);
    if (emissive !== null && base.emissive !== null && look.emissive !== null) {
      emissive.copy(look.emissive);
    }
    const color = colourOf(paintable.color);
    if (color !== null && base.color !== null && look.color !== null) {
      color.copy(look.color);
    }
    if (material.transparent !== look.transparent) {
      material.transparent = look.transparent;
      // A change of `transparent` changes which program and which pass
      // draw the material.
      material.needsUpdate = true;
    }
    material.opacity = look.opacity;
    material.depthWrite = look.depthWrite;
  }
}

export function materialForColor(color: string | null): THREE.Material {
  if (color === null) {
    return new THREE.MeshNormalMaterial();
  }
  return new THREE.MeshStandardMaterial({
    color: new THREE.Color(color),
    metalness: 0.1,
    roughness: 0.6,
  });
}

export function markingMaterial(color: string): THREE.Material {
  const material = materialForColor(color) as THREE.MeshStandardMaterial;
  material.side = THREE.DoubleSide;
  material.polygonOffset = true;
  material.polygonOffsetFactor = -1;
  material.polygonOffsetUnits = -1;
  return material;
}

function materialForFlexible(color: string | null): THREE.Material {
  if (color === null) {
    return new THREE.MeshNormalMaterial({ flatShading: true });
  }
  return new THREE.MeshStandardMaterial({
    color: new THREE.Color(color),
    metalness: 0.1,
    roughness: 0.6,
    flatShading: true,
  });
}

// ---------------------------------------------------------------------
// The change's exports, read through the namespaces (absent on the base).
// ---------------------------------------------------------------------

const P = presentation as any;
const kinds = () => ({
  rigid: (treeModule as any).RIGID,
  marking: (treeModule as any).MARKING,
  flexible: (flexibleModule as any).FLEXIBLE,
  emissive: EMISSIVE_KIND,
  glass: GLASS_KIND,
  faint: FAINT_KIND,
});

/** Kinds the test declares: a kind is any `{ name, make }`. One whose
 * plain material has an emissive of its own, one already transparent. */
const EMISSIVE_KIND = {
  name: 'test-emissive',
  make: (color: THREE.Color | string | null) => new THREE.MeshStandardMaterial({
    color: new THREE.Color(color as THREE.Color), emissive: 0x010203,
    metalness: 0.1, roughness: 0.6,
  }),
};
const GLASS_KIND = {
  name: 'test-glass',
  make: (color: THREE.Color | string | null) => new THREE.MeshStandardMaterial({
    color: new THREE.Color(color as THREE.Color), transparent: true, opacity: 0.5,
    metalness: 0.1, roughness: 0.6,
  }),
};

/** Added in review: a part already fainter than a ghost, so that the
 * ghost's opacity is seen to be the smaller of the two. */
const FAINT_KIND = {
  name: 'test-faint',
  make: (color: THREE.Color | string | null) => new THREE.MeshStandardMaterial({
    color: new THREE.Color(color as THREE.Color), transparent: true, opacity: 0.1,
    metalness: 0.1, roughness: 0.6,
  }),
};

function newHolder(): any {
  return new P.MaterialPresentation();
}

// ---------------------------------------------------------------------
// Exact printing: every number by `String`, `-0` written apart.
// ---------------------------------------------------------------------

function num(value: number): string {
  return Object.is(value, -0) ? '-0' : String(value);
}

function exact(value: unknown): string {
  if (typeof value === 'number') return num(value);
  if (value === null || value === undefined || typeof value !== 'object') {
    return typeof value === 'string' ? JSON.stringify(value) : String(value);
  }
  if (Array.isArray(value)) return `[${value.map(exact).join(',')}]`;
  const name = (value as object).constructor?.name ?? 'Object';
  const keys = Object.keys(value as object).sort();
  return `${name}{${keys.map((key) => `${key}:${exact((value as any)[key])}`).join(',')}}`;
}

/** A material compared property by property: its class and every own
 * property, identity and the count of writes left out. */
function props(material: THREE.Material, leaveOut = ['uuid', 'id', 'version', '_listeners']): string {
  const own = material as unknown as Record<string, unknown>;
  const keys = Object.keys(own).filter((key) => !leaveOut.includes(key)).sort();
  return `${material.constructor.name}{${keys.map((key) => `${key}:${exact(own[key])}`).join(',')}}`;
}

/** What R3 snapshots: every own property, `version` included, by name. */
function snapshot(material: THREE.Material): Record<string, string> {
  const own = material as unknown as Record<string, unknown>;
  return Object.fromEntries(Object.keys(own)
    .filter((key) => key !== 'uuid' && key !== '_listeners')
    .sort().map((key) => [key, exact(own[key])]));
}

function components(color: unknown): string {
  return color instanceof THREE.Color
    ? `[${num(color.r)},${num(color.g)},${num(color.b)}]` : 'none';
}

// ---------------------------------------------------------------------
// Documents and trees.
// ---------------------------------------------------------------------

const FLEX_SPEC = {
  molejo: '0.1', profile: { type: 'circle', radius: 1 },
  path: [{ type: 'helix', radius: 4, turns: 2, height: { param: 'height' } }],
  loop: false, tessellation: { path: 24, profile: 8 },
};

const at = (x: number, y = 0, z = 0) => [['t', [String(x), String(y), String(z)]]];

const part = (name: string, color: unknown, x: number,
              extra: Record<string, unknown> = {}): ManifestNode => ({
  name, type: 'part', color, operations: at(x), model: `${name}.stl`, mtime: 1, ...extra,
} as unknown as ManifestNode);

const spring = (name: string, color: unknown, x: number,
                spec: Record<string, unknown> = FLEX_SPEC): ManifestNode => ({
  name, type: 'part', color, operations: at(x, 3),
  flexible: { tech: 'molejo', params: { height: '(20 + powered)' }, spec },
} as unknown as ManifestNode);

const manifest = (children: ManifestNode[]): Manifest => ({
  format: 'machinome-export', version: 14,
  animation: { fps: 30, frames: 360 },
  drivers: { powered: { default: 0, range: null, unit: null, scale: null, dtype: null } },
  root: { name: 'root', type: 'assembly', color: null, operations: [], children },
} as unknown as Manifest);

const changed = (id: string) => ({ time: false, drivers: new Set([id]) });

function meshesIn(object: THREE.Object3D): THREE.Mesh[] {
  const meshes: THREE.Mesh[] = [];
  object.traverse((child) => { if (child instanceof THREE.Mesh) meshes.push(child); });
  return meshes;
}

function meshesUnder(tree: WidgetTree, path: string[]): THREE.Mesh[] {
  return meshesIn(tree.requirePath(path).group);
}

function materialOf(mesh: THREE.Mesh): THREE.Material {
  return mesh.material as THREE.Material;
}

/** Each mesh by the node it draws: a node's own surface by its path, a
 * marking by its path and name. */
function labels(tree: WidgetTree): Map<THREE.Mesh, string> {
  const named = new Map<THREE.Mesh, string>();
  const visit = (node: WidgetTree, path: string[]) => {
    const name = path.length === 0 ? 'root' : path.join('/');
    node.group.children.forEach((child) => {
      if (child instanceof THREE.Mesh) named.set(child, name);
    });
    node.markings.forEach((marking) => named.set(marking.mesh, `${name}#${marking.name}`));
    node.children.forEach((child) => visit(child, [...path, child.name]));
  };
  visit(tree, []);
  return named;
}

const camera = new THREE.PerspectiveCamera(50, 4 / 3, 0.1, 1000);
camera.position.set(20, -30, 40);
camera.lookAt(0, 0, 0);
camera.updateMatrixWorld();

/** The render lists three.js would draw `tree` from, through its own
 * `WebGLRenderList`: `z` as `projectObject` computes it, the opaque list
 * sorted by the viewer's comparator where the module has one. */
function drawn(tree: WidgetTree, opaqueSort: unknown = P.drawOrderSort) {
  const scene = new THREE.Scene();
  scene.add(tree.group);
  scene.updateMatrixWorld(true);
  const projScreen = new THREE.Matrix4()
    .multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  const list = new (WebGLRenderList as any)();
  list.init();
  const point = new THREE.Vector3();
  const visit = (object: THREE.Object3D, groupOrder: number) => {
    if (object.visible === false) return;
    if (object.layers.test(camera.layers)) {
      if ((object as THREE.Group).isGroup) {
        groupOrder = object.renderOrder;
      } else if (object instanceof THREE.Mesh) {
        const geometry = object.geometry;
        if (geometry.boundingSphere === null) geometry.computeBoundingSphere();
        point.copy(geometry.boundingSphere!.center)
          .applyMatrix4(object.matrixWorld).applyMatrix4(projScreen);
        const material = object.material as THREE.Material;
        if (material.visible) list.push(object, geometry, material, groupOrder, point.z, null);
      }
    }
    object.children.forEach((child) => visit(child, groupOrder));
  };
  visit(scene, 0);
  list.sort(opaqueSort, null);
  scene.remove(tree.group);
  return { opaque: list.opaque.slice(), transparent: list.transparent.slice() };
}

function changesAlong(items: Array<{ material: THREE.Material }>): number {
  let changes = 0;
  for (let i = 1; i < items.length; i += 1) {
    if (items[i].material !== items[i - 1].material) changes += 1;
  }
  return changes;
}

/** Watch every material disposal, passing through. */
function watchDisposal() {
  const disposed = new Map<THREE.Material, number>();
  const original = THREE.Material.prototype.dispose;
  const spy = vi.spyOn(THREE.Material.prototype, 'dispose')
    .mockImplementation(function (this: THREE.Material) {
      disposed.set(this, (disposed.get(this) ?? 0) + 1);
      original.call(this);
    });
  return { disposed, restore: () => spy.mockRestore() };
}

function deferred() {
  let resolve!: (geometry: THREE.BufferGeometry) => void;
  let reject!: (error: Error) => void;
  const promise = new Promise<THREE.BufferGeometry>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

// ---------------------------------------------------------------------
// The scripted bench: the tree driven as `viewer.ts` drives it.
// ---------------------------------------------------------------------

interface Standing { paths: string[][]; color: string; mode: 'keep' | 'dim' | 'ghost' }

class Bench {
  holder = newHolder();
  tree!: WidgetTree;
  table!: ReturnType<typeof bindingTable>;
  powered = 0;
  standing: Standing | null = null;

  scope(table = this.table) {
    return clockedScope({ powered: this.powered }, 0, table);
  }

  async load(document: Manifest): Promise<void> {
    this.table = bindingTable(document, '/bench.json');
    this.tree = new WidgetTree(document.root, '/build/', null, this.table, undefined, this.holder);
    await this.tree.loaded;
    this.tree.update(this.scope());
  }

  /** `presentHighlight`, as `viewer.ts` resolves the standing request. */
  present(): void {
    const standing = this.standing;
    if (standing === null) { this.holder.setHighlight(null); return; }
    const paths = standing.paths.filter((path) => this.tree.hasPath(path));
    if (paths.length === 0) { this.standing = null; this.holder.setHighlight(null); return; }
    const lit = new Set(paths.flatMap((path) => meshesUnder(this.tree, path)));
    const others = meshesIn(this.tree.group).filter((mesh) => !lit.has(mesh));
    this.standing = { ...standing, paths };
    this.holder.setHighlight({ lit: [...lit], others, color: standing.color, mode: standing.mode });
  }

  highlight(paths: string[][], color: string, mode: Standing['mode']): void {
    this.standing = { paths, color, mode };
    this.present();
  }

  putBack(): void {
    this.standing = null;
    this.holder.setHighlight(null);
  }

  hover(path: string[] | null): void {
    this.holder.setHover(path === null ? [] : meshesUnder(this.tree, path));
  }

  flip(powered: number): void {
    this.powered = powered;
    this.tree.update(this.scope(), changed('powered'));
  }

  /** `manifestChanged`: prepared, admitted, the overlays forgotten before
   * the commit, the highlight re-resolved after. */
  async republish(document: Manifest): Promise<void> {
    const table = bindingTable(document, '/bench.json');
    await this.tree.reconcile(document.root, '/build/', null, table,
      () => this.scope(table), () => this.holder.forget());
    this.table = table;
    this.present();
  }

  /** `artifactChanged`: forgotten first, re-resolved after. */
  async artifact(path: string): Promise<void> {
    this.holder.forget();
    await this.tree.artifactChanged(path, '/build/');
    this.present();
  }

  /** `replaceTree`: the new tree prepared with the same holder, the old
   * forgotten and disposed, the highlight re-resolved on the new one. */
  async reload(document: Manifest): Promise<void> {
    const table = bindingTable(document, '/bench.json');
    const next = new WidgetTree(document.root, '/build/', null, table, undefined, this.holder);
    await next.loaded;
    next.update(this.scope(table));
    this.holder.forget();
    this.tree.dispose();
    this.tree = next;
    this.table = table;
    this.present();
  }

  record(name: string, opaqueSort: unknown = P.drawOrderSort): string {
    const named = labels(this.tree);
    const lists = drawn(this.tree, opaqueSort);
    const name0 = (item: { object: THREE.Object3D }) => named.get(item.object as THREE.Mesh) ?? '?';
    const looks = [...named.entries()]
      .map(([mesh, label]) => {
        const m = mesh.material as any;
        return `  ${label}: ${m.type} color=${components(m.color)} emissive=${components(m.emissive)}`
          + ` transparent=${m.transparent} opacity=${num(m.opacity)} depthWrite=${m.depthWrite}`
          + ` side=${m.side} polygonOffset=${m.polygonOffset} flatShading=${m.flatShading}`;
      })
      .sort();
    return [
      name,
      `  opaque: ${lists.opaque.map(name0).join(' ')}`,
      `  transparent: ${lists.transparent.map(name0).join(' ')}`,
      ...looks,
    ].join('\n');
  }
}

const LAMP = { when: 'powered', on: '#ffd978', off: '#e5dfce' };
const DIGITS = { name: 'digits', model: 'digits.stl', color: '#ffffff' };
const BAND = { name: 'band', model: 'band.stl', color: '#c0c0c0' };

/** O1's document: the choice's part and the colourless part the
 * republish colours first in document order, so a move to the end shows. */
const O1_DOCUMENT = () => manifest([
  part('lamp', LAMP, -9),
  part('bare', null, -6),
  part('body', '#cc4444', -3, {
    markings: [DIGITS, BAND],
    children: [part('knob', '#cc4444', 0, { operations: at(0, 0, 2) })],
  }),
  spring('spring', '#336699', 0),
  part('plain', null, 3),
  part('tail', '#cc4444', 6),
]);

/** The republish: a colourless part coloured, a marking recoloured, one
 * model replaced by its mtime, a node added. */
const O1_REPUBLISHED = () => manifest([
  part('lamp', LAMP, -9),
  part('bare', '#cc4444', -6),
  part('body', '#cc4444', -3, {
    markings: [{ ...DIGITS, color: '#112233' }, BAND],
    children: [part('knob', '#cc4444', 0, { operations: at(0, 0, 2) })],
  }),
  spring('spring', '#336699', 0),
  part('plain', null, 3),
  part('tail', '#cc4444', 6, { mtime: 2 }),
  part('extra', '#ffd978', 9, { children: [part('pin', null, 0, { operations: at(0, 2, 0) })] }),
]);

/** A second republish, under a standing ghost: a part coloured, one put
 * back to no colour, a marking recoloured, a flexible part's spec and a
 * nested model replaced. */
const O1_REPUBLISHED_AGAIN = () => manifest([
  part('lamp', LAMP, -9),
  part('bare', null, -6),
  part('body', '#cc4444', -3, {
    markings: [{ ...DIGITS, color: '#112233' }, { ...BAND, color: '#ffffff' }],
    children: [part('knob', '#cc4444', 0, { operations: at(0, 0, 2), mtime: 2 })],
  }),
  spring('spring', '#336699', 0, { ...FLEX_SPEC, tessellation: { path: 12, profile: 8 } }),
  part('plain', '#336699', 3),
  part('tail', '#cc4444', 6, { mtime: 2 }),
  part('extra', '#ffd978', 9, { children: [part('pin', null, 0, { operations: at(0, 2, 0) })] }),
]);

/** O1's steps, each followed by what the viewer does after it. The
 * first twelve are design Decision 7's; the rest repeat the replacements
 * under a standing ghost and a hover. */
const O1_STEPS: Array<[string, (bench: Bench) => Promise<void> | void]> = [
  ['load', async (bench) => { await bench.load(O1_DOCUMENT()); }],
  ['hover tail', (bench) => bench.hover(['tail'])],
  ['highlight body kept', (bench) => bench.highlight([['body']], '#ffb000', 'keep')],
  ['put back', (bench) => bench.putBack()],
  ['highlight body dimmed', (bench) => bench.highlight([['body']], '#ffb000', 'dim')],
  ['put back', (bench) => bench.putBack()],
  ['highlight body ghosted', (bench) => bench.highlight([['body']], '#00ff00', 'ghost')],
  ['hover plain, ghosted', (bench) => bench.hover(['plain'])],
  ['put back both', (bench) => { bench.putBack(); bench.hover(null); }],
  ['flip the choice', (bench) => bench.flip(1)],
  ['republish', async (bench) => { await bench.republish(O1_REPUBLISHED()); }],
  ['artifactChanged body.stl', async (bench) => { await bench.artifact('body.stl'); }],
  ['reload', async (bench) => { await bench.reload(O1_REPUBLISHED()); }],
  ['highlight knob ghosted, hover tail', (bench) => {
    bench.highlight([['body', 'knob']], '#fff', 'ghost'); bench.hover(['tail']);
  }],
  ['flip the choice back under it', (bench) => bench.flip(0)],
  ['republish under it', async (bench) => { await bench.republish(O1_REPUBLISHED_AGAIN()); }],
  ['artifactChanged lamp.stl under it', async (bench) => { await bench.artifact('lamp.stl'); }],
  ['reload under it', async (bench) => { await bench.reload(O1_REPUBLISHED_AGAIN()); }],
  ['highlight dimmed in its place, hover lamp', (bench) => {
    bench.putBack(); bench.highlight([['spring'], ['body']], '#abc', 'dim'); bench.hover(['lamp']);
  }],
  ['flip the choice under a dim', (bench) => bench.flip(1)],
  ['put back both again', (bench) => { bench.putBack(); bench.hover(null); }],
];

/** Recorded on the base (e72d1ae7), before any source change, and never
 * regenerated: today's order of drawing and today's looks. Since OpenSpec
 * `draw-rigid-parts-without-stored-normals` the rigid parts' looks, its
 * 148 lines of `side=0 polygonOffset=false`, carry `flatShading=true`
 * (design Decision 9); no order line and no other value changed. */
const O1_EXPECTED: string[] = [
  [
    "load",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "hover tail",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "highlight body kept",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "put back",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "highlight body dimmed",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.274238227032548,0.2582686430685311,0.21602229684422222] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.01158666829780323,0.04650391254045119,0.11149137234002374] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.21133956859663927,0.020231900564327443,0.020231900564327443] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "put back",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "highlight body ghosted",
    "  opaque: body body#digits body#band body/knob",
    "  transparent: lamp bare plain tail spring",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
  ],
  [
    "hover plain, ghosted",
    "  opaque: body body#digits body#band body/knob",
    "  transparent: lamp bare plain tail spring",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
  ],
  [
    "put back both",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "flip the choice",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "republish",
    "  opaque: lamp body body#band body/knob spring plain tail extra extra/pin bare body#digits",
    "  transparent: ",
    "  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "artifactChanged body.stl",
    "  opaque: lamp body#band body/knob spring plain tail extra extra/pin bare body#digits body",
    "  transparent: ",
    "  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "reload",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail extra extra/pin",
    "  transparent: ",
    "  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "highlight knob ghosted, hover tail",
    "  opaque: body/knob",
    "  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring",
    "  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
  ],
  [
    "flip the choice back under it",
    "  opaque: body/knob",
    "  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring",
    "  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  plain: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
  ],
  [
    "republish under it",
    "  opaque: body/knob",
    "  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  plain: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
  ],
  [
    "artifactChanged lamp.stl under it",
    "  opaque: body/knob",
    "  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  plain: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
  ],
  [
    "reload under it",
    "  opaque: body/knob",
    "  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  plain: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true",
  ],
  [
    "highlight dimmed in its place, hover lamp",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail extra extra/pin",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.274238227032548,0.2582686430685311,0.21602229684422222] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshStandardMaterial color=[0.01158666829780323,0.04650391254045119,0.11149137234002374] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.21133956859663927,0.020231900564327443,0.020231900564327443] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "flip the choice under a dim",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail extra extra/pin",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshStandardMaterial color=[0.01158666829780323,0.04650391254045119,0.11149137234002374] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.21133956859663927,0.020231900564327443,0.020231900564327443] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
  [
    "put back both again",
    "  opaque: lamp bare body body#digits body#band body/knob spring plain tail extra extra/pin",
    "  transparent: ",
    "  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false",
    "  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  plain: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
    "  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true",
  ],
].map((lines) => lines.join('\n'));

// ---------------------------------------------------------------------
// Red on the base, by count.
// ---------------------------------------------------------------------

describe('one material per appearance (R)', () => {
  it('R1: twelve meshes of five appearances are drawn with five material objects', async () => {
    const tree = new WidgetTree(manifest([
      part('a', '#ff0000', 0),
      part('b', '#FF0000', 1),
      part('c', '#f00', 2),
      part('d', 'red', 3),
      part('e', '#0000ff', 4),
      part('f', '#0000ff', 5),
      part('g', null, 6, { markings: [
        { name: 'one', model: 'one.stl', color: '#ffffff' },
        { name: 'two', model: 'two.stl', color: '#ffffff' },
      ] }),
      part('h', null, 7),
      spring('s1', '#336699', 8),
      spring('s2', '#336699', 9),
    ]).root, '/build/');
    await tree.loaded;
    const meshes = meshesIn(tree.group);
    expect(meshes).toHaveLength(12);
    expect(new Set(meshes.map(materialOf)).size).toBe(5);
    tree.dispose();
  });

  it('R2: three red then three blue parts change material once along the drawn order', async () => {
    const tree = new WidgetTree(manifest([
      part('r1', '#ff0000', 0), part('r2', '#ff0000', 1), part('r3', '#ff0000', 2),
      part('b1', '#0000ff', 3), part('b2', '#0000ff', 4), part('b3', '#0000ff', 5),
    ]).root, '/build/');
    await tree.loaded;
    const { opaque } = drawn(tree);
    expect(opaque).toHaveLength(6);
    expect(changesAlong(opaque)).toBe(1);
    tree.dispose();
  });

  it('R3: no material is written after it is first handed to a mesh', async () => {
    const bench = new Bench();
    const seen = new Map<THREE.Material, Record<string, string>>();
    const look = (step: string) => {
      for (const mesh of meshesIn(bench.tree.group)) {
        const material = materialOf(mesh);
        if (!seen.has(material)) seen.set(material, snapshot(material));
      }
      for (const [material, before] of seen) {
        expect(snapshot(material), `a material written at "${step}"`).toEqual(before);
      }
    };
    for (const [name, step] of O1_STEPS) {
      await step(bench);
      look(name);
    }
    bench.tree.dispose();
  });

  it('R4: a reload into a new tree with the same holder makes no material', async () => {
    const watch = watchDisposal();
    try {
      const holder = newHolder();
      const document = O1_DOCUMENT();
      const table = bindingTable(document, '/r4.json');
      const old = new WidgetTree(document.root, '/build/', null, table, undefined, holder);
      await old.loaded;
      old.update(clockedScope({ powered: 0 }, 0, table));
      const before = new Set(meshesIn(old.group).map(materialOf));
      const next = new WidgetTree(document.root, '/build/', null, table, undefined, holder);
      await next.loaded;
      next.update(clockedScope({ powered: 0 }, 0, table));
      holder.forget();
      old.dispose();
      const meshes = meshesIn(next.group);
      const shared = meshes.filter((mesh) => before.has(materialOf(mesh)));
      expect(shared.length).toBe(meshes.length);
      expect(meshes.filter((mesh) => watch.disposed.has(materialOf(mesh)))).toEqual([]);
      next.dispose();
    } finally {
      watch.restore();
    }
  });
});

// ---------------------------------------------------------------------
// The order of drawing.
// ---------------------------------------------------------------------

describe('the order of drawing (O)', () => {
  it('O1: a scripted sequence draws in the order and with the looks recorded on the base', async () => {
    const bench = new Bench();
    const records: string[] = [];
    for (const [name, step] of O1_STEPS) {
      await step(bench);
      records.push(bench.record(name));
    }
    bench.tree.dispose();
    expect(records.length).toBe(O1_STEPS.length);
    for (let i = 0; i < records.length; i += 1) {
      expect(records[i], `O1 step ${i}`).toBe(O1_EXPECTED[i]);
    }
  });

  // Added in review. A fault planted there survived O1: a recolour into
  // the appearance a mesh already has kept its place. The shipped code
  // makes a new material at that point whatever the colour, so the mesh
  // moves after everything made since it was reserved. Passes on the base.
  it('O3: a part a republish both colours and re-models is drawn after the sibling re-modelled beside it', async () => {
    const bench = new Bench();
    await bench.load(manifest([part('first', null, -3), part('second', '#0000ff', 3)]));
    expect(bench.record('load').split('\n')[1]).toBe('  opaque: first second');
    // Both replacements are reserved while the update prepares, first's
    // before second's; the commit then replaces first's material again,
    // because the part had no colour, and that is the later event.
    await bench.republish(manifest([
      part('first', '#ff0000', -3, { mtime: 2 }), part('second', '#0000ff', 3, { mtime: 2 })]));
    expect(bench.record('republish').split('\n')[1]).toBe('  opaque: second first');
    bench.tree.dispose();
  });

  it("O2: the comparator sorts as three.js's own sort does where materials number the places", () => {
    const random = seeded(0x0202);
    const holder = newHolder();
    const placed: THREE.Mesh[] = [];
    for (let i = 0; i < 40; i += 1) {
      // A colour of its own per mesh: each its own material, made in the
      // order of the places.
      const color = new THREE.Color().setRGB(i / 64, 0.5, 0.25);
      placed.push(holder.mesh(new THREE.BufferGeometry(), kinds().rigid, color));
    }
    const shared = new THREE.MeshBasicMaterial();
    const unplaced = Array.from({ length: 12 }, (_unused, i) => new THREE.Mesh(
      new THREE.BufferGeometry(), i % 3 === 0 ? shared : new THREE.MeshBasicMaterial()));
    for (const mesh of [...placed, ...unplaced]) {
      expect(P.placeOf(mesh) === undefined).toBe(unplaced.includes(mesh));
    }
    for (let trial = 0; trial < 200; trial += 1) {
      const pick = <T>(values: readonly T[]) => values[Math.floor(random() * values.length)];
      const objects = [...placed, ...unplaced].filter(() => random() < 0.7);
      // three.js reads the render order from the object.
      objects.forEach((object) => { object.renderOrder = pick([0, 0, 0, 2, -2]); });
      const list = new (WebGLRenderList as any)();
      list.init();
      objects.forEach((object) => list.push(object, object.geometry, object.material,
        pick([0, 0, 0, 1, -1]), pick([0.25, 0.5, 0.5, 0.75, -0.5]), null));
      const ours = [...list.opaque].sort(P.drawOrderSort);
      list.sort(undefined, null);
      expect(ours.map((item: { object: THREE.Object3D }) => item.object.id))
        .toEqual(list.opaque.map((item: { object: THREE.Object3D }) => item.object.id));
      // Among items of one group and one render order, the unplaced come last.
      for (let i = 1; i < ours.length; i += 1) {
        const [a, b] = [ours[i - 1], ours[i]];
        if (a.groupOrder === b.groupOrder && a.renderOrder === b.renderOrder) {
          expect(P.placeOf(a.object) === undefined && P.placeOf(b.object) !== undefined).toBe(false);
        }
      }
    }
    [...placed, ...unplaced].forEach((mesh) => { mesh.renderOrder = 0; });
    placed.forEach((mesh) => holder.release(mesh));
    holder.dispose();
  });
});

// ---------------------------------------------------------------------
// The look against the shipped owner.
// ---------------------------------------------------------------------

function seeded(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

type KindName = 'rigid' | 'marking' | 'flexible' | 'emissive' | 'glass' | 'faint';

/** The shipped construction of each kind, for the oracle's meshes. */
function shipped(kind: KindName, color: string | null): THREE.Material {
  switch (kind) {
    // The rigid kind's material is the flexible pair since OpenSpec
    // `draw-rigid-parts-without-stored-normals` (design Decisions 3 and
    // 9); a marking's is still built on the smooth `materialForColor`.
    case 'rigid': return materialForFlexible(color);
    case 'marking': return markingMaterial(color as string);
    case 'flexible': return materialForFlexible(color);
    case 'emissive': return EMISSIVE_KIND.make(color);
    case 'glass': return GLASS_KIND.make(color);
    case 'faint': return FAINT_KIND.make(color);
  }
}

interface Slot {
  kind: KindName;
  color: string | null;
  oracle: THREE.Mesh;
  held: THREE.Mesh;
  live: boolean;
}

/** One set of meshes driven by the oracle, one by the holder. */
class Pair {
  oracle = new MaterialPresentation();
  holder = newHolder();
  slots: Slot[] = [];
  warnings = { oracle: 0, holder: 0 };

  /** Run `oracle` then `holder`, counting what each warns. */
  quietly<O, H>(oracle: () => O, holder: () => H): [O, H] {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => undefined);
    try {
      const first = oracle();
      this.warnings.oracle += warn.mock.calls.length;
      warn.mockClear();
      const second = holder();
      this.warnings.holder += warn.mock.calls.length;
      return [first, second];
    } finally {
      warn.mockRestore();
    }
  }

  add(kind: KindName, color: string | null): Slot {
    const [oracle, held] = this.quietly(
      () => new THREE.Mesh(new THREE.BufferGeometry(), shipped(kind, color)),
      () => this.holder.mesh(new THREE.BufferGeometry(), kinds()[kind], color) as THREE.Mesh);
    const slot: Slot = { kind, color, oracle, held, live: true };
    this.slots.push(slot);
    return slot;
  }

  live(): Slot[] { return this.slots.filter((slot) => slot.live); }

  hover(slots: Slot[]): void {
    this.oracle.setHover(slots.map((slot) => slot.oracle));
    this.holder.setHover(slots.map((slot) => slot.held));
  }

  highlight(lit: Slot[], others: Slot[], color: string, mode: OthersMode): void {
    const live = (slots: Slot[]) => slots.filter((slot) => slot.live);
    this.oracle.setHighlight({ lit: live(lit).map((s) => s.oracle),
      others: live(others).map((s) => s.oracle), color, mode });
    this.holder.setHighlight({ lit: live(lit).map((s) => s.held),
      others: live(others).map((s) => s.held), color, mode });
  }

  putBack(): void {
    this.oracle.setHighlight(null);
    this.holder.setHighlight(null);
  }

  rebase(slot: Slot, color: string): void {
    this.quietly(() => this.oracle.setBaseColor(slot.oracle, color),
      () => this.holder.setBaseColor(slot.held, color));
    slot.color = color;
  }

  forget(): void {
    this.oracle.forget();
    this.holder.forget();
  }

  /** The shipped replacement of a mesh's material, emulated in the
   * oracle; the holder's `recolor`. Run after `forget`, as every caller
   * does. */
  recolor(slot: Slot, color: string | null): void {
    const previous = materialOf(slot.oracle);
    this.quietly(() => { slot.oracle.material = shipped(slot.kind, color); },
      () => this.holder.recolor(slot.held, color));
    previous.dispose();
    slot.color = color;
  }

  /** A mesh replaced by a new one of the same node. */
  replace(slot: Slot): Slot {
    materialOf(slot.oracle).dispose();
    slot.oracle.geometry.dispose();
    const [oracle, held] = this.quietly(
      () => new THREE.Mesh(new THREE.BufferGeometry(), shipped(slot.kind, slot.color)),
      () => this.holder.mesh(new THREE.BufferGeometry(), kinds()[slot.kind], slot.color) as THREE.Mesh);
    const next: Slot = { kind: slot.kind, color: slot.color, oracle, held, live: true };
    this.holder.release(slot.held);
    slot.live = false;
    this.slots.push(next);
    return next;
  }

  release(slot: Slot): void {
    materialOf(slot.oracle).dispose();
    this.holder.release(slot.held);
    slot.live = false;
  }

  /** Every live mesh: the two materials property by property, and
   * whether each is ghosted. */
  check(step: string): void {
    for (const slot of this.live()) {
      expect(props(materialOf(slot.held)), `${step}: ${slot.kind} ${slot.color}`)
        .toBe(props(materialOf(slot.oracle)));
      expect(this.holder.isGhosted(slot.held), `${step}: ghosted`)
        .toBe(this.oracle.isGhosted(slot.oracle));
    }
  }
}

/** Every appearance P1 starts from: every kind, with and without colour
 * where the kind admits none, each colour in several spellings. */
const APPEARANCES: Array<{ kind: KindName; spellings: Array<string | null> }> = [
  { kind: 'rigid', spellings: ['#ff0000', '#FF0000', '#f00', 'red'] },
  { kind: 'rigid', spellings: [null] },
  { kind: 'rigid', spellings: ['#336699'] },
  { kind: 'marking', spellings: ['#ffffff', '#FFFFFF', '#fff'] },
  { kind: 'flexible', spellings: ['#336699', '#336699'] },
  { kind: 'flexible', spellings: [null] },
  { kind: 'emissive', spellings: ['#4477cc', '#4477CC'] },
  { kind: 'glass', spellings: ['#888888'] },
];
const HIGHLIGHT_COLORS = ['#ffb000', '#00ff00', '#fff', '#FFFFFF', '#abc'];
const MODES: OthersMode[] = ['keep', 'dim', 'ghost'];
const REBASE_COLORS = ['#ff0000', '#f00', 'red', '#336699', 'not a colour'];
const RECOLORS: Array<string | null> = ['#ff0000', '#336699', '#ffffff', '#4477cc', null];

describe('the look against the shipped owner (P)', () => {
  it('P1: 200 generated sequences of 40 steps look exactly as the shipped owner draws them', () => {
    const random = seeded(0x5eed);
    const pick = <T>(values: readonly T[]) => values[Math.floor(random() * values.length)];
    const subset = (slots: Slot[]) => slots.filter(() => random() < 0.4);
    const covered = new Set<number>();
    let steps = 0;
    for (let sequence = 0; sequence < 200; sequence += 1) {
      const pair = new Pair();
      // Five appearances, two meshes each, the five drawn without
      // repetition from the eight.
      const order = APPEARANCES.map((_a, i) => i).sort(() => random() - 0.5).slice(0, 5);
      for (const index of order) {
        covered.add(index);
        const appearance = APPEARANCES[index];
        pair.add(appearance.kind, pick(appearance.spellings));
        pair.add(appearance.kind, pick(appearance.spellings));
      }
      let standing: { lit: Slot[]; others: Slot[]; color: string; mode: OthersMode } | null = null;
      const resolve = () => {
        if (standing === null) pair.putBack();
        else pair.highlight(standing.lit, standing.others, standing.color, standing.mode);
      };
      pair.check(`sequence ${sequence} start`);
      for (let step = 0; step < 40; step += 1) {
        const live = pair.live();
        if (live.length === 0) break;
        const action = pick(['hover', 'hover', 'highlight', 'highlight', 'putBack',
          'rebase', 'rebase', 'recolor', 'replace', 'forget', 'release'] as const);
        let label: string = action;
        if (action === 'hover') {
          pair.hover(subset(live));
        } else if (action === 'highlight') {
          const lit = subset(live);
          if (lit.length === 0) lit.push(pick(live));
          const others = random() < 0.5 ? subset(live) : live.filter((slot) => !lit.includes(slot));
          standing = { lit, others, color: pick(HIGHLIGHT_COLORS), mode: pick(MODES) };
          label = `highlight ${standing.mode} ${standing.color}`;
          resolve();
        } else if (action === 'putBack') {
          standing = null;
          pair.putBack();
        } else if (action === 'rebase') {
          const candidates = live.filter((slot) =>
            (slot.kind === 'rigid' || slot.kind === 'flexible') && slot.color !== null);
          if (candidates.length === 0) continue;
          const color = pick(REBASE_COLORS);
          label = `rebase ${color}`;
          pair.rebase(pick(candidates), color);
        } else if (action === 'recolor') {
          const slot = pick(live);
          const choices = RECOLORS.filter((color) =>
            color !== null || slot.kind === 'rigid' || slot.kind === 'flexible');
          const color = pick(choices);
          label = `recolor ${slot.kind} ${color}`;
          pair.forget();
          pair.recolor(slot, color);
          resolve();
        } else if (action === 'replace') {
          const slot = pick(live);
          pair.forget();
          const next = pair.replace(slot);
          if (standing !== null) {
            const swap = (slots: Slot[]) => slots.map((one) => (one === slot ? next : one));
            standing = { ...standing, lit: swap(standing.lit), others: swap(standing.others) };
          }
          resolve();
        } else if (action === 'forget') {
          standing = null;
          pair.forget();
        } else {
          const touched = live.filter((slot) => standing !== null
            && (standing.lit.includes(slot) || standing.others.includes(slot)));
          pair.release(pick(touched.length > 0 ? touched : live));
        }
        steps += 1;
        pair.check(`sequence ${sequence} step ${step} (${label})`);
      }
      expect(pair.warnings.holder).toBe(pair.warnings.oracle);
      pair.live().forEach((slot) => pair.holder.release(slot.held));
      pair.holder.dispose();
    }
    expect(covered.size).toBe(APPEARANCES.length);
    expect(steps).toBeGreaterThan(7000);
  }, 60_000);

  describe('P2: the special cases, by name', () => {
    it('a normal material stays on its plain material hovered, lit or dimmed, and ghosts', () => {
      const pair = new Pair();
      const [plain, other, third] = [pair.add('rigid', null), pair.add('rigid', null),
        pair.add('flexible', null)];
      const base = materialOf(plain.held);
      pair.hover([plain, other, third]);
      pair.check('hovered');
      expect(materialOf(plain.held)).toBe(base);
      pair.highlight([plain], [other, third], '#ff0000', 'dim');
      pair.check('lit and dimmed');
      expect(materialOf(plain.held)).toBe(base);
      expect(materialOf(other.held)).toBe(base);
      pair.highlight([plain], [other, third], '#ff0000', 'ghost');
      pair.check('ghosted and hovered');
      // A normal material ghosted shares one variant, hovered or not.
      pair.hover([]);
      pair.check('ghosted');
      const ghost = materialOf(other.held);
      expect(ghost).not.toBe(base);
      pair.hover([other]);
      expect(materialOf(other.held)).toBe(ghost);
      pair.putBack(); pair.hover([]);
      pair.check('put back');
      expect(materialOf(other.held)).toBe(base);
    });

    it('lit and hovered shows the highlight; lit and among the others is lit', () => {
      const pair = new Pair();
      const [dial, lid] = [pair.add('rigid', '#336699'), pair.add('rigid', '#336699')];
      pair.hover([dial]);
      pair.highlight([dial], [dial, lid], '#00ff00', 'dim');
      pair.check('lit, hovered and among the others');
      expect((materialOf(dial.held) as THREE.MeshStandardMaterial).emissive.getHex()).toBe(0x00ff00);
    });

    it('dimmed and hovered, and ghosted and hovered, carry the hover grey', () => {
      const pair = new Pair();
      const [hub, blade, fan] = [pair.add('rigid', '#cc4444'), pair.add('rigid', '#4477cc'),
        pair.add('emissive', '#4477cc')];
      pair.hover([blade, fan]);
      for (const mode of MODES) {
        pair.highlight([hub], [blade, fan], '#ffb000', mode);
        pair.check(`${mode} and hovered`);
      }
    });

    it('a variant is made with its transparent; the plain material is never written', () => {
      const pair = new Pair();
      const [blade, glass, plain] = [pair.add('rigid', '#4477cc'), pair.add('glass', '#888888'),
        pair.add('rigid', null)];
      const lit = pair.add('rigid', '#cc4444');
      const bases = [blade, glass, plain].map((slot) => materialOf(slot.held));
      const versions = bases.map((material) => material.version);
      pair.highlight([lit], [blade, glass, plain], '#fff', 'ghost');
      pair.check('ghosted');
      expect(bases.map((material) => material.version)).toEqual(versions);
      expect([blade, glass, plain].map((slot) => materialOf(slot.held).transparent))
        .toEqual([true, true, true]);
      pair.putBack();
      pair.check('put back');
      expect([blade, glass, plain].map((slot) => materialOf(slot.held))).toEqual(bases);
      expect(bases.map((material) => material.version)).toEqual(versions);
    });

    it('a standing highlight re-resolved onto new meshes points them at their looks', () => {
      const pair = new Pair();
      const [hub, blade] = [pair.add('rigid', '#cc4444'), pair.add('rigid', '#4477cc')];
      pair.highlight([hub], [blade], '#00ff00', 'dim');
      pair.forget();
      const next = pair.replace(hub);
      pair.highlight([next], [blade], '#00ff00', 'dim');
      pair.check('re-resolved');
    });

    it('the lamp: a colour chosen under a highlight is the new base, in both orders of put-back', () => {
      for (const mode of MODES) for (const hoverFirst of [false, true]) {
        const pair = new Pair();
        const [target, other] = [pair.add('rigid', '#e5dfce'), pair.add('flexible', '#e5dfce')];
        pair.hover([target, other]);
        pair.highlight([target], [other], '#00ff00', mode);
        pair.rebase(target, '#ffd978');
        pair.rebase(other, '#ffd978');
        pair.check(`${mode}: rebased under it`);
        if (hoverFirst) { pair.hover([]); pair.check(`${mode}: unhovered`); pair.putBack(); }
        else { pair.putBack(); pair.check(`${mode}: put back`); pair.hover([]); }
        pair.check(`${mode}: both gone`);
        expect((materialOf(target.held) as THREE.MeshStandardMaterial).color.getHexString())
          .toBe('ffd978');
        expect(materialOf(target.held)).toBe(materialOf(pair.add('rigid', '#ffd978').held));
      }
    });

    it('a colour chosen under a dim is dimmed from its own plain colour', () => {
      const pair = new Pair();
      const [hub, blade] = [pair.add('rigid', '#cc4444'), pair.add('rigid', '#4477cc')];
      pair.highlight([hub], [blade], '#ffb000', 'dim');
      pair.rebase(blade, '#336699');
      pair.check('rebased under a dim');
      pair.rebase(blade, '#4477cc');
      pair.check('rebased back under a dim');
    });

    it('a marking ghosted keeps its two sides and its polygon offset', () => {
      const pair = new Pair();
      const [part0, digits] = [pair.add('rigid', '#cc4444'), pair.add('marking', '#ffffff')];
      for (const mode of MODES) {
        pair.highlight([part0], [digits], '#ffb000', mode);
        pair.check(`marking ${mode}`);
        const material = materialOf(digits.held);
        expect([material.side, material.polygonOffset, material.polygonOffsetFactor,
          material.polygonOffsetUnits]).toEqual([THREE.DoubleSide, true, -1, -1]);
      }
    });

    it('a rebase onto an unreadable colour keeps the colour it had', () => {
      const pair = new Pair();
      const lamp = pair.add('rigid', '#ff0000');
      pair.rebase(lamp, 'not a colour');
      pair.check('rebased onto nothing readable');
      const color = (materialOf(lamp.held) as THREE.MeshStandardMaterial).color;
      expect([color.r, color.g, color.b]).toEqual([1, 0, 0]);
      expect(pair.warnings.holder).toBe(pair.warnings.oracle);
      const fresh = pair.add('rigid', 'not a colour');
      pair.check('made from nothing readable');
      const white = (materialOf(fresh.held) as THREE.MeshStandardMaterial).color;
      expect([white.r, white.g, white.b]).toEqual([1, 1, 1]);
    });

    it('four spellings of one colour are one appearance and one material', () => {
      const pair = new Pair();
      const slots = ['#f00', '#ff0000', '#FF0000', 'red'].map((color) => pair.add('rigid', color));
      pair.check('four spellings');
      expect(new Set(slots.map((slot) => materialOf(slot.held))).size).toBe(1);
    });

    // Added in review. Two faults planted there survived every case above:
    // an appearance keyed by its colour rounded to eight bits, and a ghost
    // that took the ghost opacity whatever the plain one was.
    it('two colours less than one part in 255 apart are two appearances', () => {
      const pair = new Pair();
      const [half, hex] = [pair.add('rigid', 'rgb(50%, 0%, 0%)'), pair.add('rigid', '#800000')];
      pair.check('made');
      const [a, b] = [half, hex].map((slot) => materialOf(slot.held) as THREE.MeshStandardMaterial);
      expect(a.color.getHexString()).toBe(b.color.getHexString());
      expect(a.color.r).not.toBe(b.color.r);
      expect(a).not.toBe(b);
      pair.highlight([half], [hex], '#ffb000', 'dim');
      pair.check('lit and dimmed');
    });

    it('a part fainter than a ghost keeps its own opacity when ghosted', () => {
      const pair = new Pair();
      const [hub, faint] = [pair.add('rigid', '#cc4444'), pair.add('faint', '#888888')];
      pair.highlight([hub], [faint], '#ffb000', 'ghost');
      pair.check('ghosted');
      expect(materialOf(faint.held).opacity).toBe(0.1);
      expect(pair.holder.isGhosted(faint.held)).toBe(true);
      pair.putBack();
      pair.check('put back');
      expect(materialOf(faint.held).opacity).toBe(0.1);
    });
  });
});

// ---------------------------------------------------------------------
// Lifetime.
// ---------------------------------------------------------------------

describe('lifetime (L)', () => {
  it('L1: nothing is disposed under a mesh, and no other part changes', async () => {
    const watch = watchDisposal();
    try {
      const holder = newHolder();
      const reds = (extra: Record<string, Record<string, unknown>> = {}, names = ['a1', 'a2', 'a3']) =>
        manifest([
          ...names.map((name, i) => part(name, '#ff0000', i, extra[name] ?? {})),
          part('b', '#0000ff', 5),
        ]);
      const tree = new WidgetTree(reds().root, '/build/', null, undefined, undefined, holder);
      await tree.loaded;
      tree.update(clockedScope({}, 0, bindingTable(reds(), '/l1.json')));
      const step = async (name: string, run: () => Promise<void> | void) => {
        const before = new Map(meshesIn(tree.group).map((mesh) => [mesh, props(materialOf(mesh))]));
        await run();
        for (const mesh of meshesIn(tree.group)) {
          expect(watch.disposed.has(materialOf(mesh)), `${name}: a live mesh on a disposed material`)
            .toBe(false);
          if (before.has(mesh)) {
            expect(props(materialOf(mesh)), `${name}: another part changed`).toBe(before.get(mesh));
          }
        }
      };

      await step('a failed load of a part sharing an appearance with a live one', async () => {
        overrides.set('/build/a1.stl', () => Promise.reject(new Error('fetch failed')));
        const failed = new WidgetTree(reds().root, '/build/', null, undefined, undefined, holder);
        await expect(failed.loaded).rejects.toThrow('fetch failed');
        failed.dispose();
      });
      await step('a republish removing one of two parts of one colour', async () => {
        await tree.reconcile(reds({}, ['a1', 'a2']).root, '/build/', null, undefined,
          undefined, () => holder.forget());
      });
      await step('a republish replacing the model of one of two parts of one colour', async () => {
        await tree.reconcile(reds({ a2: { mtime: 2 } }, ['a1', 'a2']).root, '/build/', null,
          undefined, undefined, () => holder.forget());
      });
      const others = () => meshesIn(tree.group).filter((mesh) => mesh !== meshesUnder(tree, ['a1'])[0]);
      holder.setHighlight({ lit: meshesUnder(tree, ['a1']), others: others(),
        color: '#00ff00', mode: 'dim' });
      await step('a failed reconcile with a highlight standing', async () => {
        overrides.set('/build/a2.stl', () => Promise.reject(new Error('replacement failed')));
        await expect(tree.reconcile(reds({ a2: { mtime: 3 } }, ['a1', 'a2']).root, '/build/',
          null, undefined, undefined, () => holder.forget())).rejects.toThrow('replacement failed');
      });
      await step('a failed artifactChanged with a highlight standing', async () => {
        overrides.set('/build/a1.stl', () => Promise.reject(new Error('artifact failed')));
        await expect(tree.artifactChanged('a1.stl', '/build/')).rejects.toThrow('artifact failed');
      });
      holder.setHighlight(null);
      await step('a tree disposed during loading', async () => {
        const pending = ['a1', 'a2', 'b'].map((name) => {
          const one = deferred();
          overrides.set(`/build/${name}.stl`, () => one.promise);
          return one;
        });
        const loading = new WidgetTree(reds({}, ['a1', 'a2']).root, '/build/', null, undefined,
          undefined, holder);
        loading.dispose();
        pending.forEach((one) => one.resolve(new THREE.BoxGeometry()));
        await expect(loading.loaded).rejects.toBeDefined();
      });
      holder.setHover([...meshesUnder(tree, ['a1']), ...meshesUnder(tree, ['a2'])]);
      await step('a mesh released under a hover', async () => {
        await tree.reconcile(reds({}, ['a1']).root, '/build/');
      });
      holder.setHover([]);
      tree.dispose();
    } finally {
      watch.restore();
    }
  });

  it('L2: nothing outlives the trees; every material made is disposed exactly once', async () => {
    const watch = watchDisposal();
    try {
      const bench = new Bench();
      const seen = new Set<THREE.Material>();
      for (const [, step] of O1_STEPS) {
        await step(bench);
        meshesIn(bench.tree.group).forEach((mesh) => seen.add(materialOf(mesh)));
      }
      const waiting = deferred();
      overrides.set('/build/lamp.stl', () => waiting.promise);
      const pending = new WidgetTree(O1_DOCUMENT().root, '/build/', null,
        bindingTable(O1_DOCUMENT(), '/l2.json'), undefined, bench.holder);
      meshesIn(pending.group).forEach((mesh) => seen.add(materialOf(mesh)));
      bench.holder.drop();
      pending.dispose();
      bench.tree.dispose();
      waiting.resolve(new THREE.BoxGeometry());
      await expect(pending.loaded).rejects.toBeDefined();
      const counts = bench.holder.counts();
      expect(counts.meshes).toBe(0);
      expect(counts.appearances).toEqual([]);
      expect(counts.materials).toBe(0);
      for (const material of seen) {
        expect(watch.disposed.get(material), 'a material not disposed exactly once').toBe(1);
      }
      for (const [, times] of watch.disposed) expect(times).toBe(1);
      bench.holder.dispose();
    } finally {
      watch.restore();
    }
  });

  it('L3: the holder holds at most a plain and two ghosted materials per appearance after put-back', async () => {
    const watch = watchDisposal();
    try {
      const holder = newHolder();
      const palette = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#00ffff'];
      const document = (colors: string[]) => manifest(Array.from({ length: 50 },
        (_unused, i) => part(`p${i}`, colors[i % colors.length], i)));
      const tree = new WidgetTree(document(palette).root, '/build/', null, undefined, undefined, holder);
      await tree.loaded;
      const seen = new Set<THREE.Material>();
      const look = () => meshesIn(tree.group).forEach((mesh) => seen.add(materialOf(mesh)));
      const bounded = (when: string) => {
        const counts = holder.counts();
        for (const appearance of counts.appearances) {
          expect(appearance.users, when).toBeGreaterThan(0);
          expect(appearance.variants, `${when}: a lit, hovered or dimmed variant held`).toBe(0);
          expect(appearance.kept, when).toBeLessThanOrEqual(2);
        }
        const live = [...seen].filter((material) => !watch.disposed.has(material));
        expect(live.length, `${when}: a material held beyond the count`).toBe(counts.materials);
      };
      for (const mesh of meshesIn(tree.group)) {
        holder.setHover([mesh]);
        look();
      }
      holder.setHover([]);
      bounded('after a hover across fifty parts');
      const colors = ['#100000', '#200000', '#300000', '#400000', '#500000',
        '#600000', '#700000', '#800000', '#900000', '#a00000'];
      for (const color of colors) for (const mode of MODES) {
        const lit = meshesUnder(tree, ['p0']);
        holder.setHover(meshesUnder(tree, ['p1']));
        holder.setHighlight({ lit, others: meshesIn(tree.group).filter((m) => !lit.includes(m)),
          color, mode });
        look();
        holder.setHighlight(null);
        holder.setHover([]);
        bounded(`after a ${mode} highlight in ${color}`);
      }
      await tree.reconcile(document(['#123456', '#234567', '#345678', '#456789', '#56789a']).root,
        '/build/', null, undefined, undefined, () => holder.forget());
      look();
      bounded('after a republish changing every colour');
      expect(holder.counts().appearances.length).toBe(5);
      tree.dispose();
      holder.dispose();
    } finally {
      watch.restore();
    }
  });

  it('L4: a second ghost hands out the materials of the first and makes none', async () => {
    const holder = newHolder();
    // The lit part has no colour, so its lit look is its plain material:
    // a lit variant, released at the put-back by design, is L3's.
    const tree = new WidgetTree(manifest([
      part('hub', null, 0), part('a', '#4477cc', 1), part('b', '#4477cc', 2),
      part('c', null, 3), part('d', '#cc4444', 5), spring('s', '#336699', 4),
    ]).root, '/build/', null, bindingTable(manifest([]), '/l4.json'), undefined, holder);
    await tree.loaded;
    const seen = new Set<THREE.Material>();
    const look = () => meshesIn(tree.group).forEach((mesh) => seen.add(materialOf(mesh)));
    const ghost = () => {
      const lit = meshesUnder(tree, ['hub']);
      holder.setHighlight({ lit, others: meshesIn(tree.group).filter((m) => !lit.includes(m)),
        color: '#ffb000', mode: 'ghost' });
      return meshesIn(tree.group).map(materialOf);
    };
    look();
    const first = ghost();
    look();
    const made = seen.size;
    holder.setHighlight(null);
    look();
    const second = ghost();
    look();
    expect(second).toEqual(first);
    second.forEach((material, i) => expect(material).toBe(first[i]));
    expect(seen.size).toBe(made);
    holder.setHighlight(null);
    tree.dispose();
  });

  it('L5: two holders share no material, and disposing one disposes none of the other', async () => {
    const watch = watchDisposal();
    try {
      const document = O1_DOCUMENT();
      const table = bindingTable(document, '/l5.json');
      const one = new WidgetTree(document.root, '/build/', null, table, undefined, newHolder());
      const two = new WidgetTree(document.root, '/build/', null, table, undefined, newHolder());
      await Promise.all([one.loaded, two.loaded]);
      const theirs = new Set(meshesIn(two.group).map(materialOf));
      expect(meshesIn(one.group).filter((mesh) => theirs.has(materialOf(mesh)))).toEqual([]);
      one.dispose();
      expect([...theirs].filter((material) => watch.disposed.has(material))).toEqual([]);
      two.dispose();
    } finally {
      watch.restore();
    }
  });
});
