/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import * as THREE from 'three';
import { describe, expect, it, vi } from 'vitest';

const { loadAsync } = vi.hoisted(() => ({
  loadAsync: vi.fn(() => Promise.resolve(new THREE.BoxGeometry())),
}));

vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({
  STLLoader: class { loadAsync = loadAsync; },
}));

import { AssemblyNavigation } from './assembly';
import { WidgetTree } from './tree';
import { ManifestNode } from './types';

const leaf = (name: string): ManifestNode => ({
  name, type: 'part', color: null, operations: [], model: `${name}.stl`, mtime: 1,
});

const root = (names: string[]): ManifestNode => ({
  name: 'root', type: 'assembly', color: null, operations: [],
  children: names.map(leaf),
});

describe('AssemblyNavigation', () => {
  it('keeps focus and hidden paths when a reconciled tree retains them', async () => {
    const tree = new WidgetTree(root(['left', 'right']), '/build/');
    await tree.loaded;
    const navigation = new AssemblyNavigation();
    navigation.setRoot(tree, ['left']);
    navigation.setVisible(tree, ['right'], false);

    await tree.reconcile(root(['left', 'right', 'added']), '/build/');
    loadAsync.mockClear();
    navigation.reconcile(tree);

    expect(navigation.root()).toEqual(['left']);
    expect(navigation.isVisible(['right'])).toBe(false);
    expect(tree.children.find((child) => child.name === 'left')!.group.visible).toBe(true);
    expect(tree.children.find((child) => child.name === 'right')!.group.visible).toBe(false);
    expect(loadAsync).not.toHaveBeenCalled();
  });

  it('returns to the document root and discards hidden paths that disappear', async () => {
    const tree = new WidgetTree(root(['left', 'right']), '/build/');
    await tree.loaded;
    const navigation = new AssemblyNavigation();
    navigation.setRoot(tree, ['left']);
    navigation.setVisible(tree, ['right'], false);

    await tree.reconcile(root(['added']), '/build/');
    navigation.reconcile(tree);

    expect(navigation.root()).toBeNull();
    expect(navigation.isVisible(['right'])).toBe(true);
    expect(tree.children[0].group.visible).toBe(true);
  });

  describe('state', () => {
    it('reports the document root as null and no hidden paths, fresh', async () => {
      const tree = new WidgetTree(root(['left', 'right']), '/build/');
      await tree.loaded;
      const navigation = new AssemblyNavigation();

      expect(navigation.state()).toEqual({ root: null, hidden: [] });
    });

    it('reports the focused path after setRoot', async () => {
      const tree = new WidgetTree(root(['left', 'right']), '/build/');
      await tree.loaded;
      const navigation = new AssemblyNavigation();
      navigation.setRoot(tree, ['left']);

      expect(navigation.state().root).toEqual(['left']);
    });

    it('lists a hidden node and not its descendant', async () => {
      const tree = new WidgetTree(
        {
          name: 'root', type: 'assembly', color: null, operations: [],
          children: [
            {
              name: 'parent', type: 'assembly', color: null, operations: [],
              children: [leaf('child')],
            },
          ],
        },
        '/build/',
      );
      await tree.loaded;
      const navigation = new AssemblyNavigation();
      navigation.setVisible(tree, ['parent'], false);

      expect(navigation.state().hidden).toEqual([['parent']]);

      navigation.setVisible(tree, ['parent'], true);
      expect(navigation.state().hidden).toEqual([]);
    });

    it('is a copy: a state already read is unaffected by a later change', async () => {
      const tree = new WidgetTree(root(['left', 'right']), '/build/');
      await tree.loaded;
      const navigation = new AssemblyNavigation();
      navigation.setRoot(tree, ['left']);
      navigation.setVisible(tree, ['right'], false);
      const before = navigation.state();

      navigation.setRoot(tree, ['right']);
      navigation.setVisible(tree, ['right'], true);

      expect(before).toEqual({ root: ['left'], hidden: [['right']] });
      expect(navigation.state()).toEqual({ root: ['right'], hidden: [] });
    });

    it('reports root: null and no hidden path once reconcile drops both', async () => {
      const tree = new WidgetTree(root(['left', 'right']), '/build/');
      await tree.loaded;
      const navigation = new AssemblyNavigation();
      navigation.setRoot(tree, ['left']);
      navigation.setVisible(tree, ['right'], false);

      await tree.reconcile(root(['added']), '/build/');
      navigation.reconcile(tree);

      expect(navigation.state()).toEqual({ root: null, hidden: [] });
    });
  });
});
