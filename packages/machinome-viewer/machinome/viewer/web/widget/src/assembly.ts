/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import {
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
