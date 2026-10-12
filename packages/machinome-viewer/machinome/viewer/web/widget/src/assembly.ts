/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {
  AssemblyNode,
  AssemblyPath,
  assemblyPathKey,
  WidgetTree,
} from './tree';

/** The navigation state a host reads: the focused root, or `null` for
 * the published document root -- the same `null` `setRoot` accepts, so a
 * reported root is always a value it can be handed back -- and the
 * explicitly hidden paths, each root-relative (design D1-D3). Both
 * fields are copies: a caller holds a value, not a window into the
 * widget. */
export interface AssemblyNavigationState {
  root: string[] | null;
  hidden: string[][];
}

export class AssemblyNavigation {
  private focusedPath: string[] | null = null;
  private hiddenPaths = new Map<string, string[]>();

  root(): string[] | null {
    return this.focusedPath === null ? null : [...this.focusedPath];
  }

  /** The whole inspection state, as a copy (design D1). */
  state(): AssemblyNavigationState {
    return {
      root: this.root(),
      hidden: [...this.hiddenPaths.values()].map((path) => [...path]),
    };
  }

  isVisible(path: AssemblyPath): boolean {
    return !this.hiddenPaths.has(assemblyPathKey(path));
  }

  setRoot(tree: WidgetTree, path: AssemblyPath | null): void {
    if (path !== null) {
      tree.requirePath(path);
    }
    this.focusedPath = path === null ? null : [...path];
    this.apply(tree);
  }

  setVisible(tree: WidgetTree, path: AssemblyPath, visible: boolean): void {
    tree.requirePath(path);
    const key = assemblyPathKey(path);
    if (visible) {
      this.hiddenPaths.delete(key);
    } else {
      this.hiddenPaths.set(key, [...path]);
    }
    this.apply(tree);
  }

  reconcile(tree: WidgetTree): boolean {
    let rootChanged = false;
    if (this.focusedPath !== null && !tree.hasPath(this.focusedPath)) {
      this.focusedPath = null;
      rootChanged = true;
    }
    for (const [key, path] of this.hiddenPaths) {
      if (!tree.hasPath(path)) {
        this.hiddenPaths.delete(key);
      }
    }
    this.apply(tree);
    return rootChanged;
  }

  private apply(tree: WidgetTree): void {
    tree.applyVisibility(this.focusedPath, new Set(this.hiddenPaths.keys()));
  }
}

/** What a subscribed listener receives: the fresh assembly and navigation
 * snapshots, equal to what `assembly()` and `navigation()` return at that
 * moment (design D4) -- so a listener never has to call back into the
 * handle to redraw. */
export interface AssemblyChange {
  assembly: AssemblyNode;
  navigation: AssemblyNavigationState;
}

export type AssemblyListener = (change: AssemblyChange) => void;

/** Subscribe, notify, dispose -- mirroring `onDriverChange`
 * (`drivers.ts:214-217`, `:310-314`, `:286-292`), but defensive where
 * that channel is not (design D6): a listener cancelled or added while a
 * notification is being delivered is not called for that notification,
 * and a listener that throws does not stop the others or escape
 * `notify`. `viewer.ts` decides *when* to call `notify`; this class
 * decides nothing. */
export class AssemblyChangeNotifier {
  private listeners = new Set<AssemblyListener>();

  subscribe(listener: AssemblyListener): () => void {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  }

  notify(change: AssemblyChange): void {
    for (const listener of [...this.listeners]) {
      if (!this.listeners.has(listener)) {
        // Cancelled by an earlier listener in this same dispatch.
        continue;
      }
      try {
        listener(change);
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('assembly change listener threw', error);
      }
    }
  }

  dispose(): void {
    this.listeners.clear();
  }
}
