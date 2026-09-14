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

import { AssemblyChange, AssemblyChangeNotifier, AssemblyNavigation } from './assembly';
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

const change = (): AssemblyChange => ({
  assembly: { name: 'root', path: [], color: null, model: false, children: [] },
  navigation: { root: null, hidden: [] },
});

describe('AssemblyChangeNotifier', () => {
  it('calls every subscribed listener with the exact change notified', () => {
    const notifier = new AssemblyChangeNotifier();
    const first: AssemblyChange[] = [];
    const second: AssemblyChange[] = [];
    notifier.subscribe((c) => first.push(c));
    notifier.subscribe((c) => second.push(c));
    const sent = change();

    notifier.notify(sent);

    expect(first).toEqual([sent]);
    expect(second).toEqual([sent]);
  });

  it('subscribing returns a cancel function that stops that listener', () => {
    const notifier = new AssemblyChangeNotifier();
    const received: AssemblyChange[] = [];
    const cancel = notifier.subscribe((c) => received.push(c));

    cancel();
    notifier.notify(change());

    expect(received).toEqual([]);
  });

  it('cancelling twice is safe', () => {
    const notifier = new AssemblyChangeNotifier();
    const cancel = notifier.subscribe(() => {});

    expect(() => { cancel(); cancel(); }).not.toThrow();
  });

  it('a listener cancelled during a notification does not receive it', () => {
    const notifier = new AssemblyChangeNotifier();
    const received: AssemblyChange[] = [];
    let cancelSecond: () => void;
    notifier.subscribe(() => { cancelSecond(); });
    cancelSecond = notifier.subscribe((c) => received.push(c));

    notifier.notify(change());

    expect(received).toEqual([]);
  });

  it('a listener added during a notification does not receive that one, but hears the next', () => {
    const notifier = new AssemblyChangeNotifier();
    const received: AssemblyChange[] = [];
    notifier.subscribe(() => {
      notifier.subscribe((c) => received.push(c));
    });

    const firstChange = change();
    notifier.notify(firstChange);
    expect(received).toEqual([]);

    const secondChange = change();
    notifier.notify(secondChange);
    expect(received).toEqual([secondChange]);
  });

  it('a throwing listener does not stop the others or escape notify', () => {
    const notifier = new AssemblyChangeNotifier();
    const received: AssemblyChange[] = [];
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    notifier.subscribe(() => { throw new Error('boom'); });
    notifier.subscribe((c) => received.push(c));
    const sent = change();

    expect(() => notifier.notify(sent)).not.toThrow();

    expect(received).toEqual([sent]);
    expect(consoleError).toHaveBeenCalled();
    consoleError.mockRestore();
  });

  it('dispose drops every listener; a later notify calls nobody', () => {
    const notifier = new AssemblyChangeNotifier();
    const received: AssemblyChange[] = [];
    const cancel = notifier.subscribe((c) => received.push(c));

    notifier.dispose();
    notifier.notify(change());

    expect(received).toEqual([]);
    expect(() => cancel()).not.toThrow();
  });
});
