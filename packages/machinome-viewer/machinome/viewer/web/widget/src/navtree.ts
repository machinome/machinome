/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// What the navigator shows and does, decided as pure data (design D3),
// following `controls.ts`'s own pattern exactly: nothing here touches the
// DOM, and `navigator.ts` renders exactly what `navigatorRows` returns and
// calls the viewer exactly as `keyAction` and a pointer gesture decide --
// which is what lets every decision below be tested in plain node, where
// there is no document object at all.
//
// `AssemblyNode.color` already carries the EFFECTIVE, inherited colour
// (`tree.ts`'s `WidgetTree` resolves `data.color ?? inheritedColor` once,
// when the node is built): nothing here re-derives inheritance, it only
// reads `node.color` through.

import type { AssemblyNavigationState } from './assembly';
import { assemblyPathKey, type AssemblyNode, type AssemblyPath } from './tree';

/** The navigator's own state: which rows are expanded and which row
 * holds keyboard focus (design D8). The viewer has no opinion about
 * either, so this is the only state the navigator itself keeps. */
export interface NavigatorLocal {
  expanded: Set<string>;
  active: string | null;
}

/** One presented row: a node plus everything about how it is shown right
 * now, decided once per render so `navigator.ts` renders and nothing
 * else (design D3, D5). */
export interface NavigatorRow {
  node: AssemblyNode;
  /** `assemblyPathKey(node.path)` -- the same key the viewer hides by. */
  key: string;
  depth: number;
  expandable: boolean;
  expanded: boolean;
  /** The roving-tabindex row: the tree's one tab stop. */
  active: boolean;
  /** The focused viewer root (design D4: compared against
   * `navigation.root`, `null` meaning the document root). */
  root: boolean;
  /** Explicitly hidden, by this node's own key. */
  hidden: boolean;
  /** Invisible only because a PROPER ancestor is hidden -- independent
   * of this node's own `hidden` (design D5's fourth and fifth rows). */
  obscured: boolean;
  /** The name of the nearest hidden ancestor, for the accessible name of
   * an obscured row's visibility control; `null` when not obscured. */
  hidingAncestor: string | null;
  /** The node's effective, inherited colour, or `null`. */
  color: string | null;
}

/** What a gesture, decided here, asks the navigator to do. `move` and
 * `expand`/`collapse` are entirely local (design D8); `focus` and
 * `visibility` are calls into the viewer handle (design D10). */
export type NavigatorAction =
  | { type: 'move'; key: string }
  | { type: 'expand'; key: string }
  | { type: 'collapse'; key: string }
  | { type: 'focus'; path: AssemblyPath | null }
  | { type: 'visibility'; path: AssemblyPath; visible: boolean };

/** The document root's own key -- `assemblyPathKey([])` -- named once
 * because both `navigatorRows` and `reconcileLocal` compare against it. */
const DOCUMENT_ROOT_KEY = assemblyPathKey([]);

/** Every row the navigator currently presents: the root, and every node
 * under an expanded parent, depth-first (design D3). `root`, `hidden`
 * and `obscured` are decided from `navigation` alone, in the same walk. */
export function navigatorRows(
  assembly: AssemblyNode,
  navigation: AssemblyNavigationState,
  local: NavigatorLocal,
): NavigatorRow[] {
  const hiddenKeys = new Set(navigation.hidden.map((path) => assemblyPathKey(path)));
  const rootKey = navigation.root === null ? null : assemblyPathKey(navigation.root);
  const rows: NavigatorRow[] = [];

  const visit = (
    node: AssemblyNode,
    depth: number,
    hidingAncestor: string | null,
  ): void => {
    const key = assemblyPathKey(node.path);
    const expandable = node.children.length > 0;
    const expanded = expandable && local.expanded.has(key);
    const hidden = hiddenKeys.has(key);
    const isRoot = navigation.root === null ? depth === 0 : key === rootKey;

    rows.push({
      node,
      key,
      depth,
      expandable,
      expanded,
      active: local.active === key,
      root: isRoot,
      hidden,
      obscured: hidingAncestor !== null,
      hidingAncestor,
      color: node.color,
    });

    if (expanded) {
      // A hidden node becomes the "hiding ancestor" its own children
      // are obscured by; a node that is only itself obscured does not
      // become one -- obscured is about a PROPER ancestor (design D3).
      const childHidingAncestor = hidden ? node.name : hidingAncestor;
      node.children.forEach((child) => visit(child, depth + 1, childHidingAncestor));
    }
  };

  visit(assembly, 0, null);
  return rows;
}

/** What a checkbox reports for one row (design D5): checked state, which
 * fill the chip paints, and the visibility control's accessible name --
 * naming the hiding ancestor only when the row is obscured. */
export type ChipFill = 'color' | 'neutral' | 'none';

export interface ChipState {
  checked: boolean;
  fill: ChipFill;
  label: string;
}

export function chipState(row: NavigatorRow): ChipState {
  const checked = !row.hidden;
  const fill: ChipFill = !checked ? 'none' : (row.color !== null ? 'color' : 'neutral');
  const label = row.obscured
    ? `Visibility for ${row.node.name} (hidden with ${row.hidingAncestor})`
    : `Visibility for ${row.node.name}`;
  return { checked, fill, label };
}

/** One keypress's effect, decided against the presented `rows` and the
 * currently active row's key (design D3). `key` is `KeyboardEvent.key`,
 * kept as a bare string so this stays pure. Returns `null` for a key the
 * contract does not bind, or one with nothing to do (the ends of the
 * list, a leaf's Right, a collapsed root's Left) -- `navigator.ts` only
 * suppresses the browser default when this returns an action. */
export function keyAction(
  rows: readonly NavigatorRow[],
  activeKey: string,
  key: string,
): NavigatorAction | null {
  const index = rows.findIndex((row) => row.key === activeKey);
  if (index === -1) {
    return null;
  }
  const row = rows[index];

  switch (key) {
    case 'ArrowDown':
      return index < rows.length - 1 ? { type: 'move', key: rows[index + 1].key } : null;

    case 'ArrowUp':
      return index > 0 ? { type: 'move', key: rows[index - 1].key } : null;

    case 'ArrowRight':
      if (!row.expandable) {
        return null;
      }
      if (!row.expanded) {
        return { type: 'expand', key: row.key };
      }
      // Expanded: the next row in the depth-first walk is its first
      // child, by construction.
      return rows[index + 1] ? { type: 'move', key: rows[index + 1].key } : null;

    case 'ArrowLeft':
      if (row.expandable && row.expanded) {
        return { type: 'collapse', key: row.key };
      }
      if (row.depth === 0) {
        // The root row, collapsed or a leaf: no parent to move to.
        return null;
      }
      for (let i = index - 1; i >= 0; i -= 1) {
        if (rows[i].depth === row.depth - 1) {
          return { type: 'move', key: rows[i].key };
        }
      }
      return null;

    case 'Enter':
      // The document root is `null` to the focus API (design D4), the
      // same conversion the breadcrumb already makes.
      return { type: 'focus', path: row.node.path.length === 0 ? null : row.node.path };

    case ' ':
      // Passing the row's own `hidden` AS the next `visible` argument
      // is the toggle: a hidden row's own hidden is `true`, and showing
      // it means calling `setVisible(path, true)` (the studio's
      // `setVisible(node, hidden.has(key))`, `main.tsx:401`).
      return { type: 'visibility', path: row.node.path, visible: row.hidden };

    default:
      return null;
  }
}

/** Reconciles the navigator's own state across a render (design D9):
 * keeps expansion and the active row for paths that survive, expands
 * only the document root on the very first render, and reveals the
 * focused root's ancestors when the root itself has just moved (compared
 * against `previousRoot`, the root the navigator last rendered -- so a
 * maker who collapses an ancestor of a root that has NOT moved is not
 * fought by the next redundant notification). `previous === null` means
 * "first render"; `previousRoot` is meaningless then and ignored. */
export function reconcileLocal(
  assembly: AssemblyNode,
  navigation: AssemblyNavigationState,
  previous: NavigatorLocal | null,
  previousRoot: AssemblyPath | null,
): NavigatorLocal {
  const known = new Set<string>();
  const collect = (node: AssemblyNode): void => {
    known.add(assemblyPathKey(node.path));
    node.children.forEach(collect);
  };
  collect(assembly);

  const expanded = new Set<string>();
  if (previous === null) {
    // "Expand the root, and nothing else" (design D9).
    expanded.add(DOCUMENT_ROOT_KEY);
  } else {
    for (const key of previous.expanded) {
      if (known.has(key)) {
        expanded.add(key);
      }
    }
    const rootKey = navigation.root === null ? DOCUMENT_ROOT_KEY : assemblyPathKey(navigation.root);
    const previousRootKey = previousRoot === null ? DOCUMENT_ROOT_KEY : assemblyPathKey(previousRoot);
    if (rootKey !== previousRootKey && navigation.root !== null) {
      // Reveal every proper ancestor of the new root -- not the root's
      // own row, which reveals its CHILDREN, not itself.
      for (let i = 0; i < navigation.root.length; i += 1) {
        expanded.add(assemblyPathKey(navigation.root.slice(0, i)));
      }
    }
  }

  const active = previous?.active !== undefined && previous.active !== null
    && known.has(previous.active)
    ? previous.active
    : DOCUMENT_ROOT_KEY;

  return { expanded, active };
}
