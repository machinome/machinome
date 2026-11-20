/* Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+ */
import * as THREE from 'three';
import { describe, expect, it, vi } from 'vitest';
const { loadAsync } = vi.hoisted(() => ({
  loadAsync: vi.fn(() => Promise.resolve(new THREE.BoxGeometry())),
}));
vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({
  STLLoader: class { loadAsync = loadAsync; },
}));
import { assertRenderable } from './viewer';
import { WidgetTree } from './tree';
import { MaterialPresentation, DIM_FACTOR } from './presentation';
import { bindingTable } from './bindings';
import { clockedScope } from './run/pose';
import type { Manifest, ManifestNode } from './types';
import posedFixture from '../../../../../tests/fixtures/state-color/posed/manifest.json';
import clockedFixture from '../../../../../tests/fixtures/state-color/clocked/manifest.json';
import runningFixture from '../../../../../tests/fixtures/state-color/running/manifest.json';
import profileFixture from './run/profile-overlap-v13.json';
import followFixture from './run/follow-wrapped-v12.json';
import timeCorpus from './time-drive-corpus.json';
import { loadProgram } from './run/program';
import type { RunDocument } from './run/program';

const ON = '#ffd978', OFF = '#e5dfce';
const choice = (when = 'powered') => ({ when, on: ON, off: OFF });
const leaf = (name: string, color: unknown = null, operations: unknown[] = []): ManifestNode =>
  ({ name, type: 'part', color, operations, model: `${name}.stl` } as ManifestNode);
const document = (color: unknown = choice()): Manifest => ({
  format: 'machinome-export', version: 14,
  animation: { fps: 30, frames: 360 },
  drivers: { powered: { default: 0, range: null, unit: null, scale: null, dtype: null } },
  root: { name: 'root', type: 'assembly', color, operations: [], children: [leaf('glass')] },
} as Manifest);
const mesh = (node: WidgetTree) => node.group.children.find(c => c instanceof THREE.Mesh) as THREE.Mesh;
const hex = (node: WidgetTree) => (mesh(node).material as THREE.MeshStandardMaterial).color.getHexString();
const changed = (id: string) => ({ time: false, drivers: new Set([id]) });

describe('version-14 model colors', () => {
  it('loads a posed choice without inventing a missing running program', () => {
    const loaded = assertRenderable(document(), '/lamp.json');
    expect(loaded.program).toBeNull(); expect(loaded.machine).toBeNull();
  });
  it.each([
    { when: 'powered', on: '#fff', off: OFF },
    { when: 'powered', on: ON, off: 'yellow' },
    { when: 'powered', on: ON },
    { when: 'powered', on: ON, off: OFF, extra: 1 },
    { when: 1, on: ON, off: OFF }, [],
  ].map(color => [color]))('refuses malformed choices before rendering: %j', color => {
    expect(() => assertRenderable(document(color), '/lamp.json')).toThrow(/color/i);
  });
  it.each([
    ['posed', posedFixture, false, false],
    ['clocked', clockedFixture, true, false],
    ['running', runningFixture, false, true],
  ])('selects the standard-produced %s runtime by payload', (_name, raw, clocked, running) => {
    const loaded = assertRenderable(raw as Manifest, '/standard.json');
    expect(loaded.machine !== null).toBe(clocked);
    expect(loaded.program !== null).toBe(running);
  });
  it('refuses both execution payloads together in version fourteen', () => {
    expect(() => assertRenderable({ ...clockedFixture, program: runningFixture.program } as Manifest, '/both.json')).toThrow(/both/i);
  });
  it('admits existing profile, Follow and time-drive payloads in version fourteen', () => {
    for (const source of [profileFixture, followFixture, timeCorpus.machines[0].document]) {
      const body = { ...source, version: 14 } as unknown as RunDocument;
      expect(() => loadProgram(body, '/v14.json')).not.toThrow();
    }
    const missing = structuredClone(profileFixture) as Record<string, any>;
    delete missing.program.profiles;
    expect(() => loadProgram(missing as RunDocument, '/v13.json')).toThrow(/no finite profile/i);
  });
  it('refuses old-version choices and undeclared binding inputs', () => {
    expect(() => assertRenderable({ ...document(), version: 2 }, '/lamp.json')).toThrow(/color.*14/i);
    const body = document(choice('_shared'));
    body.bindings = [{ name: '_shared', expression: 'missing.powered' }];
    expect(() => assertRenderable(body, '/lamp.json')).toThrow(/missing.powered/);
  });
  it('resolves finite zero/nonzero, inheritance, overrides and fixed markings without replacing anything', async () => {
    const body = document(choice('_shared'));
    body.bindings = [{ name: '_shared', expression: '(powered * 2)' }];
    body.root.children!.push(leaf('fixed', '#112233'));
    body.root.children![0].markings = [{ name: 'label', model: 'label.stl', color: '#445566' }];
    const table = bindingTable(body, '/lamp.json');
    const tree = new WidgetTree(body.root, '/', null, table);
    await tree.loaded;
    const glass = tree.children[0], fixed = tree.children[1];
    const original = mesh(glass), geometry = original.geometry, material = original.material;
    const count = loadAsync.mock.calls.length;
    for (const powered of [1, 0, -2, 0]) {
      tree.update(clockedScope({ powered }, 0, table), changed('powered'));
      expect(hex(glass)).toBe((powered ? ON : OFF).slice(1));
      expect(tree.assembly().children[0].color).toBe(powered ? ON : OFF);
      expect(hex(fixed)).toBe('112233');
      expect((glass.markings[0].mesh.material as THREE.MeshStandardMaterial).color.getHexString()).toBe('445566');
      expect(mesh(glass)).toBe(original); expect(original.material).toBe(material);
      expect(original.geometry).toBe(geometry);
    }
    expect(loadAsync.mock.calls.length).toBe(count);
    tree.dispose();
  });
  it.each(['sqrt(2 - powered)', '(1 / (3 - powered))', '(-1 / (3 - powered))',
    '((powered > 2) ? powered.missing : 0)'])('prepares colors and transforms atomically and recovers scope after %s', async invalid => {
    const body = document(null);
    body.bindings = [{ name: '_shared', expression: '(powered * 10)' }];
    body.root.children = [
      leaf('earlier', choice('(_shared + independent)'), [['t', ['(_shared + independent)', '0', '0']]]),
      leaf('later', choice(invalid)),
    ];
    const table = bindingTable(body, '/lamp.json');
    const tree = new WidgetTree(body.root, '/', null, table); await tree.loaded;
    const scope = (powered: number, independent = 0) => clockedScope({ powered, independent }, 0, table);
    tree.update(scope(0));
    const before = tree.children.map(n => [...n.group.matrix.elements]);
    expect(() => tree.update(scope(3), changed('powered'))).toThrow(/later.*color/i);
    expect(tree.children.map(n => [...n.group.matrix.elements])).toEqual(before);
    expect(hex(tree.children[0])).toBe(OFF.slice(1));
    tree.update(scope(0)); expect(hex(tree.children[0])).toBe(OFF.slice(1));
    expect(() => tree.update(scope(3), changed('powered'))).toThrow();
    tree.update(scope(0, 4), changed('independent'));
    expect(tree.children[0].group.matrix.elements[12]).toBe(4);
    expect(hex(tree.children[0])).toBe(ON.slice(1));
    tree.update(scope(1, 4), changed('powered'));
    expect(tree.children[0].group.matrix.elements[12]).toBe(14);
    tree.dispose();
  });
  it('rebases every overlay from the current declared color, preserving material identity', () => {
    for (const mode of ['keep', 'dim', 'ghost'] as const) for (const hoverFirst of [false, true]) {
      const target = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshStandardMaterial({ color: OFF }));
      const other = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshStandardMaterial({ color: OFF }));
      const owner = new MaterialPresentation();
      const material = target.material;
      owner.setHover([target, other]);
      owner.setHighlight({ lit: [target], others: [other], color: '#00ff00', mode });
      owner.setBaseColor(target, ON); owner.setBaseColor(other, ON);
      expect(target.material).toBe(material);
      if (mode === 'dim') expect(other.material.color.r).toBeCloseTo(new THREE.Color(ON).r * DIM_FACTOR);
      if (hoverFirst) { owner.setHover([]); owner.setHighlight(null); }
      else { owner.setHighlight(null); owner.setHover([]); }
      expect(target.material.color.getHexString()).toBe(ON.slice(1));
      expect(other.material.color.getHexString()).toBe(ON.slice(1));
      expect(target.material.emissive.getHex()).toBe(0);
      target.geometry.dispose(); target.material.dispose(); other.geometry.dispose(); other.material.dispose();
    }
  });
  it('refuses an invalid republished color before clearing overlays or changing the standing tree', async () => {
    const body = document();
    const table = bindingTable(body, '/lamp.json');
    const owner = new MaterialPresentation();
    const tree = new WidgetTree(body.root, '/', null, table, undefined, owner);
    await tree.loaded;
    const scope = () => clockedScope({ powered: 1 }, 0, table);
    tree.update(scope());
    const glass = mesh(tree.children[0]);
    owner.setHighlight({ lit: [glass], others: [], color: '#00ff00', mode: 'keep' });
    const incoming = document(choice('sqrt(-powered)'));
    const beforeCommit = vi.fn(() => owner.forget());
    await expect(tree.reconcile(incoming.root, '/', null, table, scope, beforeCommit)).rejects.toThrow(/color/i);
    expect(beforeCommit).not.toHaveBeenCalled();
    expect(tree.assembly().children[0].color).toBe(ON);
    expect((glass.material as THREE.MeshStandardMaterial).emissive.getHexString()).toBe('00ff00');
    owner.setHighlight(null); expect(hex(tree.children[0])).toBe(ON.slice(1));
    tree.dispose();
  });
  // OpenSpec `draw-a-press-from-its-first-frame` (design D1, D8 T6): a
  // drawn request's final pose is judged and not shown, colours included.
  it('judges a chosen color without showing it, and refuses an invalid one as an update would', async () => {
    const lamp = document();
    const lampTable = bindingTable(lamp, '/lamp.json');
    const lit = new WidgetTree(lamp.root, '/', null, lampTable); await lit.loaded;
    lit.update(clockedScope({ powered: 0 }, 0, lampTable));
    const glass = mesh(lit.children[0]), material = glass.material;
    expect(hex(lit.children[0])).toBe(OFF.slice(1));
    lit.admit(clockedScope({ powered: 1 }, 0, lampTable), changed('powered'));
    expect(hex(lit.children[0])).toBe(OFF.slice(1));
    expect(glass.material).toBe(material);
    expect(lit.assembly().children[0].color).toBe(OFF);
    lit.dispose();

    const body = document(null);
    body.bindings = [{ name: '_shared', expression: '(powered * 10)' }];
    body.root.children = [
      leaf('earlier', choice('(_shared + independent)'), [['t', ['(_shared + independent)', '0', '0']]]),
      leaf('later', choice('sqrt(2 - powered)')),
    ];
    const table = bindingTable(body, '/lamp.json');
    const tree = new WidgetTree(body.root, '/', null, table); await tree.loaded;
    const scope = (powered: number, independent = 0) => clockedScope({ powered, independent }, 0, table);
    tree.update(scope(0));
    const before = tree.children.map(n => [...n.group.matrix.elements]);
    const colors = tree.children.map(hex);
    expect(() => tree.admit(scope(3), changed('powered'))).toThrow(/later.*color/i);
    expect(tree.children.map(n => [...n.group.matrix.elements])).toEqual(before);
    expect(tree.children.map(hex)).toEqual(colors);
    tree.dispose();
  });
  it('keeps an inherited flexible color through geometry evaluation and reconciliation', async () => {
    const body = document();
    body.root.children = [{ name: 'spring', type: 'part', color: null, operations: [], flexible: {
      tech: 'molejo', params: { height: '(20 + powered)' }, spec: {
        molejo: '0.1', profile: { type: 'circle', radius: 1 },
        path: [{ type: 'helix', radius: 4, turns: 2, height: { param: 'height' } }],
        loop: false, tessellation: { path: 24, profile: 8 },
      },
    } }];
    const table = bindingTable(body, '/lamp.json');
    const tree = new WidgetTree(body.root, '/', null, table); await tree.loaded;
    const scope = (powered: number) => clockedScope({ powered }, 0, table);
    tree.update(scope(0));
    const spring = mesh(tree.children[0]), material = spring.material, geometry = spring.geometry;
    tree.update(scope(1), changed('powered'));
    expect(hex(tree.children[0])).toBe(ON.slice(1));
    expect(spring.material).toBe(material); expect(spring.geometry).toBe(geometry);
    await tree.reconcile(body.root, '/', null, table);
    tree.update(scope(1)); expect(hex(tree.children[0])).toBe(ON.slice(1));
    expect(spring.material).toBe(material); expect(spring.geometry).toBe(geometry);
    tree.dispose();
  });
});
