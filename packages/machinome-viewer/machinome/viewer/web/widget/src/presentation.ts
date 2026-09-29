/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// A part's presented look has one owner (OpenSpec `highlight-a-part`,
// design D3, ADR-076).
//
// Every mesh owns its material, built with the look the document
// declares. Two things depart from that look: the hover lift of a
// declared control's part, and a host's highlight. Two writers that each
// copy what they found and write it back corrupt each other when their
// lifetimes interleave, so neither writes a material: both are OVERLAYS
// on this owner, which records a material's BASE values the first time
// any overlay touches it, computes the presented values from the base
// and the overlays standing -- never from the current values -- and
// writes the base back and forgets the record when the last overlay
// leaves.

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
