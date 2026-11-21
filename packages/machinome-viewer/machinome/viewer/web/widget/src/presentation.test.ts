/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// A part's presented look has one owner (OpenSpec `highlight-a-part`,
// design D3, ADR-076). three.js materials are plain objects, so every
// departure and every restore is tested here without WebGL. The owner
// makes the meshes (OpenSpec `share-one-material-per-appearance`, design
// Decision 7, E1); a base the viewer's own kinds cannot make is made by a
// kind declared here, since the look's formulas are relative to it.

import * as THREE from 'three';
import { describe, expect, it } from 'vitest';
import {
  DEFAULT_HIGHLIGHT_COLOR, DIM_FACTOR, GHOST_OPACITY, HOVER_EMISSIVE,
  highlightRequest, MaterialKind, MaterialPresentation,
} from './presentation';
import { RIGID } from './tree';

function coloured(owner: MaterialPresentation, hex: number,
                  kind: MaterialKind = RIGID): THREE.Mesh {
  return owner.mesh(new THREE.BufferGeometry(), kind, new THREE.Color(hex));
}

function colourless(owner: MaterialPresentation): THREE.Mesh {
  return owner.mesh(new THREE.BufferGeometry(), RIGID, null);
}

/** A kind whose plain material has an emissive of its own. */
function glowing(emissive: number): MaterialKind {
  return {
    name: `glowing ${emissive}`,
    make: (color) => new THREE.MeshStandardMaterial({ color: color ?? undefined, emissive }),
  };
}

/** A kind whose plain material is already transparent at opacity 0.5. */
const GLASS: MaterialKind = {
  name: 'glass',
  make: (color) => new THREE.MeshStandardMaterial({
    color: color ?? undefined, transparent: true, opacity: 0.5,
  }),
};

function standard(mesh: THREE.Mesh): THREE.MeshStandardMaterial {
  return mesh.material as THREE.MeshStandardMaterial;
}

/** Everything the owner may write, as plain numbers. */
function look(mesh: THREE.Mesh) {
  const material = mesh.material as THREE.Material & {
    color?: THREE.Color; emissive?: THREE.Color;
  };
  return {
    color: material.color?.getHex() ?? null,
    emissive: material.emissive?.getHex() ?? null,
    transparent: material.transparent,
    opacity: material.opacity,
    depthWrite: material.depthWrite,
  };
}

const TINT = new THREE.Color(DEFAULT_HIGHLIGHT_COLOR).getHex();

describe('MaterialPresentation', () => {
  it("tints the highlighted meshes' emissive and restores it exactly", () => {
    const owner = new MaterialPresentation();
    const hub = coloured(owner, 0xcc4444, glowing(0x010203));
    const blade = coloured(owner, 0x4477cc);
    const before = [look(hub), look(blade)];
    owner.setHighlight({ lit: [hub], others: [blade], color: '#00ff00', mode: 'keep' });
    expect(standard(hub).emissive.getHex()).toBe(0x00ff00);
    expect(look(blade)).toEqual(before[1]);
    owner.setHighlight(null);
    expect([look(hub), look(blade)]).toEqual(before);
  });

  it("dims the others' colour and leaves the highlighted ones", () => {
    const owner = new MaterialPresentation();
    const hub = coloured(owner, 0xcc4444);
    const blade = coloured(owner, 0x4477cc);
    const base = standard(blade).color.clone();
    owner.setHighlight({ lit: [hub], others: [blade], color: DEFAULT_HIGHLIGHT_COLOR, mode: 'dim' });
    expect(standard(blade).color.r).toBeCloseTo(base.r * DIM_FACTOR);
    expect(standard(blade).color.g).toBeCloseTo(base.g * DIM_FACTOR);
    expect(standard(blade).color.b).toBeCloseTo(base.b * DIM_FACTOR);
    expect(standard(hub).color.getHex()).toBe(0xcc4444);
    expect(standard(hub).emissive.getHex()).toBe(TINT);
    // Applied again, the dim is computed from the base, not compounded.
    owner.setHighlight({ lit: [hub], others: [blade], color: DEFAULT_HIGHLIGHT_COLOR, mode: 'dim' });
    expect(standard(blade).color.r).toBeCloseTo(base.r * DIM_FACTOR);
    owner.setHighlight(null);
    expect(standard(blade).color.getHex()).toBe(0x4477cc);
  });

  it('ghosts the others, including a normal material, and restores transparent, opacity and depthWrite exactly', () => {
    const owner = new MaterialPresentation();
    const hub = coloured(owner, 0xcc4444);
    const blade = coloured(owner, 0x4477cc);
    const glass = coloured(owner, 0x888888, GLASS);
    const plain = colourless(owner);
    const before = [blade, glass, plain].map(look);
    const plains = [blade, glass, plain].map(mesh => mesh.material as THREE.Material);
    const versions = plains.map(material => material.version);
    owner.setHighlight({ lit: [hub], others: [blade, glass, plain], color: '#fff', mode: 'ghost' });
    for (const mesh of [blade, glass, plain]) {
      const material = mesh.material as THREE.Material;
      expect(material.transparent).toBe(true);
      expect(material.depthWrite).toBe(false);
      expect(material.opacity).toBeCloseTo(GHOST_OPACITY);
    }
    // Transparent variants where `transparent` changed, made with it, and
    // the plain materials never written.
    expect(blade.material).not.toBe(plains[0]);
    expect(plain.material).not.toBe(plains[2]);
    expect((glass.material as THREE.Material).transparent).toBe(plains[1].transparent);
    expect(plains.map(material => material.version)).toEqual(versions);
    expect(owner.isGhosted(blade)).toBe(true);
    owner.setHighlight(null);
    expect([blade, glass, plain].map(look)).toEqual(before);
    [blade, glass, plain].forEach((mesh, i) => expect(mesh.material).toBe(plains[i]));
    expect(plains.map(material => material.version)).toEqual(versions);
  });

  it('leaves a normal material untinted and undimmed without throwing', () => {
    const owner = new MaterialPresentation();
    const plain = colourless(owner);
    const other = colourless(owner);
    const before = [look(plain), look(other)];
    owner.setHighlight({ lit: [plain], others: [other], color: '#ff0000', mode: 'dim' });
    owner.setHover([plain, other]);
    expect([look(plain), look(other)]).toEqual(before);
    owner.setHover([]);
    owner.setHighlight(null);
    expect([look(plain), look(other)]).toEqual(before);
  });

  // The four events -- hover, highlight, unhover, restore -- in every
  // order that keeps each pair's own order. The defect ADR-076 names is
  // the second: two writers that each copy what they found.
  const orders: [string, string[]][] = [
    ['hover, highlight, unhover, restore', ['hover', 'highlight', 'unhover', 'restore']],
    ['hover, highlight, restore, unhover', ['hover', 'highlight', 'restore', 'unhover']],
    ['highlight, hover, unhover, restore', ['highlight', 'hover', 'unhover', 'restore']],
    ['highlight, hover, restore, unhover', ['highlight', 'hover', 'restore', 'unhover']],
    ['hover, unhover, highlight, restore', ['hover', 'unhover', 'highlight', 'restore']],
    ['highlight, restore, hover, unhover', ['highlight', 'restore', 'hover', 'unhover']],
  ];
  it.each(orders)('%s leaves the base exactly', (_name, events) => {
    const owner = new MaterialPresentation();
    const dial = coloured(owner, 0x336699, glowing(0x050505));
    const lid = coloured(owner, 0x999999);
    const before = [look(dial), look(lid)];
    for (const event of events) {
      if (event === 'hover') owner.setHover([dial]);
      if (event === 'unhover') owner.setHover([]);
      if (event === 'highlight') {
        owner.setHighlight({ lit: [dial], others: [lid], color: '#00ff00', mode: 'ghost' });
      }
      if (event === 'restore') owner.setHighlight(null);
    }
    expect([look(dial), look(lid)]).toEqual(before);
  });

  it('shows the highlight over a hover and the hover grey once the highlight goes', () => {
    const owner = new MaterialPresentation();
    const dial = coloured(owner, 0x336699);
    owner.setHover([dial]);
    expect(standard(dial).emissive.getHex()).toBe(HOVER_EMISSIVE);
    owner.setHighlight({ lit: [dial], others: [], color: '#00ff00', mode: 'keep' });
    expect(standard(dial).emissive.getHex()).toBe(0x00ff00);
    owner.setHighlight(null);
    expect(standard(dial).emissive.getHex()).toBe(HOVER_EMISSIVE);
    owner.setHover([]);
    expect(standard(dial).emissive.getHex()).toBe(0x000000);
  });

  it('forget writes every base back and a re-applied highlight reaches new meshes', () => {
    const owner = new MaterialPresentation();
    const hub = coloured(owner, 0xcc4444);
    const blade = coloured(owner, 0x4477cc);
    const before = [look(hub), look(blade)];
    owner.setHover([blade]);
    owner.setHighlight({ lit: [hub], others: [blade], color: '#00ff00', mode: 'dim' });
    owner.forget();
    expect([look(hub), look(blade)]).toEqual(before);
    expect(owner.isGhosted(blade)).toBe(false);
    // A stale hover restore after forgetting touches nothing.
    owner.setHover([]);
    expect([look(hub), look(blade)]).toEqual(before);
    const newHub = coloured(owner, 0xcc4444);
    owner.setHighlight({ lit: [newHub], others: [blade], color: '#00ff00', mode: 'keep' });
    expect(standard(newHub).emissive.getHex()).toBe(0x00ff00);
    expect(look(hub)).toEqual(before[0]);
  });

  it('never writes a material no overlay touched', () => {
    const owner = new MaterialPresentation();
    const untouched = coloured(owner, 0x123456);
    const material = standard(untouched);
    const version = material.version;
    owner.setHighlight({ lit: [coloured(owner, 0xffffff)], others: [], color: '#abc', mode: 'ghost' });
    owner.setHighlight(null);
    owner.forget();
    expect(material.version).toBe(version);
    expect(look(untouched).color).toBe(0x123456);
  });

  it('reports ghosted meshes and only those', () => {
    const owner = new MaterialPresentation();
    const hub = coloured(owner, 0xcc4444);
    const blade = coloured(owner, 0x4477cc);
    expect(owner.isGhosted(blade)).toBe(false);
    owner.setHighlight({ lit: [hub], others: [blade], color: '#00ff00', mode: 'dim' });
    expect(owner.isGhosted(blade)).toBe(false);
    owner.setHighlight({ lit: [hub], others: [blade], color: '#00ff00', mode: 'ghost' });
    expect(owner.isGhosted(blade)).toBe(true);
    expect(owner.isGhosted(hub)).toBe(false);
    owner.setHighlight(null);
    expect(owner.isGhosted(blade)).toBe(false);
  });
});

describe('highlightRequest', () => {
  it('refuses no path', () => {
    expect(() => highlightRequest([])).toThrow('highlight needs at least one assembly path');
    expect(() => highlightRequest(undefined as never))
      .toThrow('highlight needs at least one assembly path');
    expect(() => highlightRequest(['Hub'] as never)).toThrow(/assembly path/);
  });

  it('refuses a colour that is not #rgb or #rrggbb', () => {
    for (const color of ['red', '#ff00', '#ff00001', 'ff0000', '#gg0000', 12]) {
      expect(() => highlightRequest([['Hub']], { color: color as string }))
        .toThrow(new RegExp(`highlight color .*${String(color)}`));
    }
    expect(highlightRequest([['Hub']], { color: '#AbC' }).color).toBe('#AbC');
  });

  it('refuses an unknown treatment of the others', () => {
    expect(() => highlightRequest([['Hub']], { others: 'hide' as never }))
      .toThrow(/highlight others .*hide/);
  });

  it('defaults to #ffb000 and keep', () => {
    const paths = [['Hub'], ['b0']];
    const request = highlightRequest(paths);
    expect(request).toEqual({ paths: [['Hub'], ['b0']], color: '#ffb000', others: 'keep' });
    paths[0].push('changed');
    expect(request.paths[0]).toEqual(['Hub']);
    expect(DEFAULT_HIGHLIGHT_COLOR).toBe('#ffb000');
  });
});
