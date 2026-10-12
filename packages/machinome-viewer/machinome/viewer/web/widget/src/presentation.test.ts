/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// A part's presented look has one owner (OpenSpec `highlight-a-part`,
// design D3, ADR-076). three.js materials are plain objects, so every
// departure and every restore is tested here without WebGL.

import * as THREE from 'three';
import { describe, expect, it } from 'vitest';
import {
  DEFAULT_HIGHLIGHT_COLOR, DIM_FACTOR, GHOST_OPACITY, HOVER_EMISSIVE,
  highlightRequest, MaterialPresentation,
} from './presentation';

function coloured(hex: number): THREE.Mesh {
  return new THREE.Mesh(new THREE.BufferGeometry(),
    new THREE.MeshStandardMaterial({ color: hex, emissive: 0x000000 }));
}

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
    const hub = coloured(0xcc4444);
    const blade = coloured(0x4477cc);
    standard(hub).emissive.setHex(0x010203);
    const before = [look(hub), look(blade)];
    const owner = new MaterialPresentation();
    owner.setHighlight({ lit: [hub], others: [blade], color: '#00ff00', mode: 'keep' });
    expect(standard(hub).emissive.getHex()).toBe(0x00ff00);
    expect(look(blade)).toEqual(before[1]);
    owner.setHighlight(null);
    expect([look(hub), look(blade)]).toEqual(before);
  });

  it("dims the others' colour and leaves the highlighted ones", () => {
    const hub = coloured(0xcc4444);
    const blade = coloured(0x4477cc);
    const base = standard(blade).color.clone();
    const owner = new MaterialPresentation();
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
    const hub = coloured(0xcc4444);
    const blade = coloured(0x4477cc);
    const glass = coloured(0x888888);
    standard(glass).transparent = true;
    standard(glass).opacity = 0.5;
    const plain = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshNormalMaterial());
    const before = [blade, glass, plain].map(look);
    const versions = [blade, glass, plain].map(mesh =>
      (mesh.material as THREE.Material).version);
    const owner = new MaterialPresentation();
    owner.setHighlight({ lit: [hub], others: [blade, glass, plain], color: '#fff', mode: 'ghost' });
    for (const mesh of [blade, glass, plain]) {
      const material = mesh.material as THREE.Material;
      expect(material.transparent).toBe(true);
      expect(material.depthWrite).toBe(false);
      expect(material.opacity).toBeCloseTo(GHOST_OPACITY);
    }
    // Recompiled where `transparent` changed, and only there.
    expect((blade.material as THREE.Material).version).toBeGreaterThan(versions[0]);
    expect((plain.material as THREE.Material).version).toBeGreaterThan(versions[2]);
    expect((glass.material as THREE.Material).version).toBe(versions[1]);
    expect(owner.isGhosted(blade)).toBe(true);
    owner.setHighlight(null);
    expect([blade, glass, plain].map(look)).toEqual(before);
    expect((blade.material as THREE.Material).version).toBeGreaterThan(versions[0] + 1);
  });

  it('leaves a normal material untinted and undimmed without throwing', () => {
    const plain = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshNormalMaterial());
    const other = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshNormalMaterial());
    const before = [look(plain), look(other)];
    const owner = new MaterialPresentation();
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
    const dial = coloured(0x336699);
    const lid = coloured(0x999999);
    standard(dial).emissive.setHex(0x050505);
    const before = [look(dial), look(lid)];
    const owner = new MaterialPresentation();
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
    const dial = coloured(0x336699);
    const owner = new MaterialPresentation();
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
    const hub = coloured(0xcc4444);
    const blade = coloured(0x4477cc);
    const before = [look(hub), look(blade)];
    const owner = new MaterialPresentation();
    owner.setHover([blade]);
    owner.setHighlight({ lit: [hub], others: [blade], color: '#00ff00', mode: 'dim' });
    owner.forget();
    expect([look(hub), look(blade)]).toEqual(before);
    expect(owner.isGhosted(blade)).toBe(false);
    // A stale hover restore after forgetting touches nothing.
    owner.setHover([]);
    expect([look(hub), look(blade)]).toEqual(before);
    const newHub = coloured(0xcc4444);
    owner.setHighlight({ lit: [newHub], others: [blade], color: '#00ff00', mode: 'keep' });
    expect(standard(newHub).emissive.getHex()).toBe(0x00ff00);
    expect(look(hub)).toEqual(before[0]);
  });

  it('never writes a material no overlay touched', () => {
    const untouched = coloured(0x123456);
    const material = standard(untouched);
    const version = material.version;
    const owner = new MaterialPresentation();
    owner.setHighlight({ lit: [coloured(0xffffff)], others: [], color: '#abc', mode: 'ghost' });
    owner.setHighlight(null);
    owner.forget();
    expect(material.version).toBe(version);
    expect(look(untouched).color).toBe(0x123456);
  });

  it('reports ghosted meshes and only those', () => {
    const hub = coloured(0xcc4444);
    const blade = coloured(0x4477cc);
    const owner = new MaterialPresentation();
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
