/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// A part's presented look has one owner (OpenSpec `highlight-a-part`,
// design D3, ADR-076), and that owner holds the materials (OpenSpec
// `share-one-material-per-appearance`, design Decisions 1 to 4).
//
// Every mesh a part, a flexible part or a marking draws with is made
// here, and points at the one material of its APPEARANCE -- the kind of
// material and its colour value -- and of the LOOK the overlays standing
// on it call for. Two things depart from the declared look: the hover
// lift of a declared control's part, and a host's highlight. Both are
// OVERLAYS on this owner, which computes a look's values from the
// appearance's plain material and the overlays standing -- never from
// the values a mesh shows now -- and points the mesh at the material of
// that look, made from the plain one on first use. Model-selected colours
// point a mesh at the appearance of its new colour, keeping its place in
// the order of drawing; replacing a mesh's material gives it a new place.
//
// No material is written after it is handed to a mesh: a hover, a
// highlight, a put-back and a chosen colour point meshes at other
// materials and back. A material is disposed when no mesh points at it,
// except the ghosted ones, kept while their appearance has meshes, and
// all of an appearance's materials when its last mesh is released.

import * as THREE from 'three';
import type { AssemblyPath } from './tree';

/** What happens to the parts a highlight does not name. */
export type OthersMode = 'keep' | 'dim' | 'ghost';

export interface HighlightOptions {
  /** `#rgb` or `#rrggbb`; default `DEFAULT_HIGHLIGHT_COLOR`. */
  color?: string;
  /** Default `'keep'`. */
  others?: OthersMode;
}

/** A highlight request, checked and copied (design D6). */
export interface HighlightRequest {
  paths: AssemblyPath[];
  color: string;
  others: OthersMode;
}

/** The highlight's emissive tint when the host names none: an amber
 * that reads against the grey, red and blue parts machines are usually
 * declared in. */
export const DEFAULT_HIGHLIGHT_COLOR = '#ffb000';

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

const HEX_COLOR = /^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i;
const MODES: readonly OthersMode[] = ['keep', 'dim', 'ghost'];

/** Check and copy a highlight request, before anything changes (design
 * D6). Whether each path exists is the tree's question, asked by the
 * viewer next. three.js's own colour parser warns and keeps the old
 * colour on a string it cannot read, which would pass silently, so the
 * colour is checked here. */
export function highlightRequest(paths: readonly AssemblyPath[],
                                 options: HighlightOptions = {}): HighlightRequest {
  if (!Array.isArray(paths) || paths.length === 0) {
    throw new Error('highlight needs at least one assembly path');
  }
  for (const path of paths) {
    if (!Array.isArray(path) || !path.every((name) => typeof name === 'string')) {
      throw new Error(`highlight needs assembly paths, arrays of names, not ${JSON.stringify(path)}`);
    }
  }
  const color = options?.color ?? DEFAULT_HIGHLIGHT_COLOR;
  if (typeof color !== 'string' || !HEX_COLOR.test(color)) {
    throw new Error(`highlight color must be #rgb or #rrggbb, not ${JSON.stringify(color)}`);
  }
  const others = options?.others ?? 'keep';
  if (!MODES.includes(others)) {
    throw new Error(`highlight others must be 'keep', 'dim' or 'ghost', not ${JSON.stringify(others)}`);
  }
  return { paths: paths.map((path) => [...path]), color, others };
}

/** The standing highlight, resolved to the meshes it reaches now. */
export interface HighlightState {
  lit: readonly THREE.Mesh[];
  others: readonly THREE.Mesh[];
  color: string;
  mode: OthersMode;
}

/** A kind of material: how the plain material of an appearance is made
 * from its colour value. The viewer declares three (`RIGID` and
 * `MARKING` in `tree.ts`, `FLEXIBLE` in `flexible.ts`); the holder
 * assumes nothing about any of them. */
export interface MaterialKind {
  readonly name: string;
  make(color: THREE.Color | null): THREE.Material;
}

/** The comparator's view of three.js's render item. */
export interface RenderItem {
  id: number;
  object: THREE.Object3D;
  material: THREE.Material;
  groupOrder: number;
  renderOrder: number;
  z: number;
}

type Paintable = THREE.Material & { color?: unknown; emissive?: unknown };

function colourOf(value: unknown): THREE.Color | null {
  return value instanceof THREE.Color ? value : null;
}

function number(value: number): string {
  return Object.is(value, -0) ? '-0' : String(value);
}

/** Three components under `Object.is`: equal values share a key, values
 * that differ do not, `-0` written apart. */
function colourKey(color: THREE.Color | null): string {
  return color === null ? 'none'
    : `${number(color.r)},${number(color.g)},${number(color.b)}`;
}

/** The values a look writes, as `present` wrote them (ADR-076). */
interface Values {
  emissive: THREE.Color | null;
  color: THREE.Color | null;
  transparent: boolean;
  opacity: number;
  depthWrite: boolean;
}

function valuesKey(values: Values): string {
  return `${colourKey(values.emissive)}|${colourKey(values.color)}|${values.transparent}`
    + `|${number(values.opacity)}|${values.depthWrite}`;
}

/** One appearance: its plain material, never written after it is made,
 * the variants made from it for the looks met so far, and how many
 * meshes it has. */
interface Appearance {
  kind: MaterialKind;
  key: string;
  plain: THREE.Material;
  /** The plain material's values, read once when it is made. */
  base: Values;
  baseKey: string;
  /** Variants by the values they carry: two looks with equal values
   * share one. */
  variants: Map<string, THREE.Material>;
  users: number;
}

interface Held {
  kind: MaterialKind;
  color: THREE.Color | null;
  appearance: Appearance;
  material: THREE.Material;
}

/** A mesh's place in the order of drawing, on the mesh itself, because
 * the comparator reads it at every comparison of every frame. */
const PLACE = Symbol('machinome place in the order of drawing');

/** The holder that made each mesh, so its disposal releases it there. */
const holders = new WeakMap<THREE.Mesh, MaterialPresentation>();

/** The place a mesh was given, or `undefined` for an object no holder
 * made. Read by `drawOrderSort` and by the tests. */
export function placeOf(object: THREE.Object3D): number | undefined {
  return (object as unknown as { [PLACE]?: number })[PLACE];
}

/** three.js's opaque sort (`painterSortStable`, three.js 0.156.1) with
 * the place where it reads `material.id`, so the opaque parts are drawn
 * in the order the shipped per-part materials were made in (design
 * Decision 3). An object with no place is drawn after every placed one,
 * by three.js's own keys among themselves. */
export function drawOrderSort(a: RenderItem, b: RenderItem): number {
  if (a.groupOrder !== b.groupOrder) return a.groupOrder - b.groupOrder;
  if (a.renderOrder !== b.renderOrder) return a.renderOrder - b.renderOrder;
  const p = placeOf(a.object), q = placeOf(b.object);
  if (p !== q) {
    if (p === undefined) return 1;
    if (q === undefined) return -1;
    return p - q;
  }
  if (p === undefined && a.material.id !== b.material.id) return a.material.id - b.material.id;
  if (a.z !== b.z) return a.z - b.z;
  return a.id - b.id;
}

/** Release a mesh's material where it was made: the counts fall, and a
 * material no mesh needs any more is disposed. A mesh no holder made has
 * its own materials disposed. */
export function releaseMaterial(mesh: THREE.Mesh): void {
  const holder = holders.get(mesh);
  if (holder !== undefined) {
    holder.release(mesh);
    return;
  }
  const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
  materials.forEach((material) => material.dispose());
}

/** What the holder holds, for the tests. */
export interface HolderCounts {
  meshes: number;
  materials: number;
  appearances: Array<{
    kind: string;
    color: string;
    users: number;
    /** Variants held other than the kept ghosted ones. */
    variants: number;
    /** Variants kept while the appearance has meshes. */
    kept: number;
  }>;
}

/** The ONE owner of the viewer's materials: it makes them, points each
 * mesh at the one its appearance and its overlays call for, and
 * releases them. One per viewer. */
export class MaterialPresentation {
  private readonly held = new Map<THREE.Mesh, Held>();
  private readonly appearances = new Map<MaterialKind, Map<string, Appearance>>();
  private readonly pointers = new Map<THREE.Material, number>();
  /** The appearance each held material was made for. */
  private readonly owners = new Map<THREE.Material, Appearance>();
  private places = 0;
  private hovered = new Set<THREE.Mesh>();
  private highlight: {
    lit: Set<THREE.Mesh>; others: Set<THREE.Mesh>;
    color: THREE.Color; mode: OthersMode;
  } | null = null;

  /** Make a mesh of `kind` in `color`: its place, its appearance and its
   * material, the plain one, since no overlay stands on a new mesh. */
  mesh(geometry: THREE.BufferGeometry, kind: MaterialKind,
       color: string | THREE.Color | null): THREE.Mesh {
    const value = color === null ? null : new THREE.Color(color);
    const appearance = this.acquire(kind, value);
    const mesh = new THREE.Mesh(geometry, appearance.plain);
    this.place(mesh);
    holders.set(mesh, this);
    this.held.set(mesh, { kind, color: value, appearance, material: appearance.plain });
    this.count(appearance.plain, 1);
    return mesh;
  }

  /** Replace a mesh's material, as the shipped code did at its three
   * replacing sites: the mesh takes the appearance of `color` and a new
   * place, and its look is presented there. */
  recolor(mesh: THREE.Mesh, color: string | THREE.Color | null): void {
    const held = this.held.get(mesh);
    if (held === undefined) return;
    this.move(mesh, held, color === null ? null : new THREE.Color(color));
    this.place(mesh);
  }

  /** Change the declared model color, then compose the standing overlays
   * from that base: the mesh's present colour value, then `set`, as the
   * shipped owner rebased its recorded colour. Keeps the place. */
  setBaseColor(mesh: THREE.Mesh, color: string): void {
    const held = this.held.get(mesh);
    if (held === undefined) return;
    if (held.color === null) {
      this.present(new Set([mesh]));
      return;
    }
    this.move(mesh, held, held.color.clone().set(color));
  }

  /** Forget a mesh: its counts fall, a material no mesh needs is
   * disposed, and no overlay stands on it any more. A mesh released
   * already, or never held, changes nothing. */
  release(mesh: THREE.Mesh): void {
    const held = this.held.get(mesh);
    if (held === undefined) return;
    this.held.delete(mesh);
    this.hovered.delete(mesh);
    this.highlight?.lit.delete(mesh);
    this.highlight?.others.delete(mesh);
    this.count(held.material, -1);
    this.settle(held.material);
    this.leave(held.appearance);
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

  /** Point every mesh an overlay stands on back at its plain material
   * and drop every overlay: run before meshes or materials are replaced. */
  forget(): void {
    const touched = this.touched();
    this.hovered = new Set();
    this.highlight = null;
    this.present(touched);
  }

  /** Drop every overlay WITHOUT pointing anything back: for a disposed
   * mount, whose meshes are released next with its trees. */
  drop(): void {
    this.hovered = new Set();
    this.highlight = null;
  }

  /** Whether a mesh is drawn as a ghost now (design D5). */
  isGhosted(mesh: THREE.Mesh): boolean {
    const highlight = this.highlight;
    return highlight !== null && highlight.mode === 'ghost'
      && highlight.others.has(mesh) && !highlight.lit.has(mesh);
  }

  /** Dispose every material still held and forget everything: for a
   * disposed mount, after its trees. */
  dispose(): void {
    for (const byColour of this.appearances.values()) {
      for (const appearance of byColour.values()) {
        appearance.plain.dispose();
        appearance.variants.forEach((variant) => variant.dispose());
      }
    }
    this.appearances.clear();
    this.pointers.clear();
    this.owners.clear();
    this.held.clear();
    this.hovered = new Set();
    this.highlight = null;
  }

  /** What is held now, for the tests. */
  counts(): HolderCounts {
    const appearances: HolderCounts['appearances'] = [];
    let materials = 0;
    for (const byColour of this.appearances.values()) {
      for (const appearance of byColour.values()) {
        let kept = 0;
        appearance.variants.forEach((variant) => {
          if (this.keeps(appearance, variant)) kept += 1;
        });
        appearances.push({
          kind: appearance.kind.name, color: appearance.key, users: appearance.users,
          variants: appearance.variants.size - kept, kept,
        });
        materials += 1 + appearance.variants.size;
      }
    }
    return { meshes: this.held.size, materials, appearances };
  }

  private place(mesh: THREE.Mesh): void {
    this.places += 1;
    (mesh as unknown as { [PLACE]: number })[PLACE] = this.places;
  }

  /** The appearance of `kind` in `value`, made on first use; one more
   * mesh is counted as its user. */
  private acquire(kind: MaterialKind, value: THREE.Color | null): Appearance {
    let byColour = this.appearances.get(kind);
    if (byColour === undefined) {
      byColour = new Map();
      this.appearances.set(kind, byColour);
    }
    const key = colourKey(value);
    let appearance = byColour.get(key);
    if (appearance === undefined) {
      const plain = kind.make(value);
      const paintable = plain as Paintable;
      const base: Values = {
        emissive: colourOf(paintable.emissive)?.clone() ?? null,
        color: colourOf(paintable.color)?.clone() ?? null,
        transparent: plain.transparent,
        opacity: plain.opacity,
        depthWrite: plain.depthWrite,
      };
      appearance = {
        kind, key, plain, base, baseKey: valuesKey(base),
        variants: new Map(), users: 0,
      };
      byColour.set(key, appearance);
      this.owners.set(plain, appearance);
    }
    appearance.users += 1;
    return appearance;
  }

  /** One mesh fewer: an appearance without meshes is disposed whole. */
  private leave(appearance: Appearance): void {
    appearance.users -= 1;
    if (appearance.users > 0) return;
    this.appearances.get(appearance.kind)?.delete(appearance.key);
    // Every pointer is a user, so none is left at these.
    this.owners.delete(appearance.plain);
    appearance.plain.dispose();
    appearance.variants.forEach((variant) => {
      this.owners.delete(variant);
      variant.dispose();
    });
    appearance.variants.clear();
  }

  /** Move a held mesh to the appearance of `value` and present its look
   * there, in one step. */
  private move(mesh: THREE.Mesh, held: Held, value: THREE.Color | null): void {
    const previous = held.appearance;
    held.appearance = this.acquire(held.kind, value);
    held.color = value;
    this.point(mesh, held, this.materialFor(held.appearance, this.lookOf(mesh), new Map()));
    this.leave(previous);
  }

  private count(material: THREE.Material, delta: number): void {
    const pointers = (this.pointers.get(material) ?? 0) + delta;
    if (pointers === 0) this.pointers.delete(material);
    else this.pointers.set(material, pointers);
  }

  /** Whether a variant is kept with no mesh pointing at it: one whose
   * `transparent` differs from its plain material's, so a second ghost
   * finds its program compiled (design Decision 4). */
  private keeps(appearance: Appearance, variant: THREE.Material): boolean {
    return variant.transparent !== appearance.plain.transparent;
  }

  /** Dispose a variant no mesh points at, unless it is kept. A plain
   * material goes with its appearance, in `leave`. */
  private settle(material: THREE.Material): void {
    if (this.pointers.has(material)) return;
    const appearance = this.owners.get(material);
    if (appearance === undefined || material === appearance.plain) return;
    if (this.keeps(appearance, material)) return;
    for (const [key, variant] of appearance.variants) {
      if (variant === material) {
        appearance.variants.delete(key);
        break;
      }
    }
    this.owners.delete(material);
    material.dispose();
  }

  /** Point a held mesh at `material`, the counts moving in the same
   * step, and settle the material it leaves. */
  private point(mesh: THREE.Mesh, held: Held, material: THREE.Material): void {
    const previous = held.material;
    if (previous === material) return;
    this.count(material, 1);
    mesh.material = material;
    held.material = material;
    this.count(previous, -1);
    this.settle(previous);
  }

  /** Lit, dimmed and ghosted decided exactly as the shipped `present`
   * decided them; hovered when in the hover set. */
  private lookOf(mesh: THREE.Mesh) {
    const highlight = this.highlight;
    const lit = highlight?.lit.has(mesh) ?? false;
    const other = !lit && highlight !== null && highlight.others.has(mesh);
    return {
      lit,
      dim: other && highlight!.mode === 'dim',
      ghost: other && highlight!.mode === 'ghost',
      hovered: this.hovered.has(mesh),
    };
  }

  /** The material of a look of an appearance: the plain one when the
   * look's values are the plain values, else the variant carrying them,
   * made from the plain material on first use. Computed once per
   * appearance and look within one presentation. */
  private materialFor(appearance: Appearance,
                      look: { lit: boolean; dim: boolean; ghost: boolean; hovered: boolean },
                      memo: Map<Appearance, Map<string, THREE.Material>>): THREE.Material {
    if (!look.lit && !look.hovered && !look.dim && !look.ghost) return appearance.plain;
    const lookKey = `${look.lit}|${look.hovered}|${look.dim}|${look.ghost}`;
    let known = memo.get(appearance);
    const found = known?.get(lookKey);
    if (found !== undefined) return found;
    const highlight = this.highlight;
    const base = appearance.base;
    // The values the shipped owner wrote (ADR-076), from the plain
    // material's own values, never from the material a mesh points at.
    const values: Values = {
      emissive: base.emissive === null ? null
        : look.lit ? highlight!.color
          : look.hovered ? new THREE.Color(HOVER_EMISSIVE) : base.emissive,
      color: base.color === null ? null
        : look.dim ? base.color.clone().multiplyScalar(DIM_FACTOR) : base.color,
      transparent: look.ghost ? true : base.transparent,
      opacity: look.ghost ? Math.min(base.opacity, GHOST_OPACITY) : base.opacity,
      depthWrite: look.ghost ? false : base.depthWrite,
    };
    const key = valuesKey(values);
    let material: THREE.Material;
    if (key === appearance.baseKey) {
      material = appearance.plain;
    } else {
      let variant = appearance.variants.get(key);
      if (variant === undefined) {
        // Every value is set before any mesh points at it; `clone`
        // carries every other property of the plain material.
        variant = appearance.plain.clone();
        const paintable = variant as Paintable;
        const emissive = colourOf(paintable.emissive);
        if (emissive !== null && values.emissive !== null) emissive.copy(values.emissive);
        const color = colourOf(paintable.color);
        if (color !== null && values.color !== null) color.copy(values.color);
        variant.transparent = values.transparent;
        variant.opacity = values.opacity;
        variant.depthWrite = values.depthWrite;
        appearance.variants.set(key, variant);
        this.owners.set(variant, appearance);
      }
      material = variant;
    }
    if (known === undefined) {
      known = new Map();
      memo.set(appearance, known);
    }
    known.set(lookKey, material);
    return material;
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

  /** Point every mesh an overlay stood on before or stands on now at
   * the material of its look. */
  private present(before: Set<THREE.Mesh>): void {
    const meshes = this.touched();
    before.forEach((mesh) => meshes.add(mesh));
    const memo = new Map<Appearance, Map<string, THREE.Material>>();
    for (const mesh of meshes) {
      const held = this.held.get(mesh);
      if (held === undefined) continue;
      this.point(mesh, held, this.materialFor(held.appearance, this.lookOf(mesh), memo));
    }
  }
}
