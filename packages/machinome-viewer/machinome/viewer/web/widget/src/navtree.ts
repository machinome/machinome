/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// What the navigator shows and does, decided as pure data (design D3),
// following `controls.ts`'s own pattern exactly: nothing here touches the
// DOM, and `navigator.ts` renders exactly what `navigatorRows` returns and
// calls the viewer exactly as `keyAction` and a pointer gesture decide --
// which is what lets every decision below be tested in plain node, where
// there is no document object at all.
//
// The snapshot's `AssemblyNode.color` is the node's own EFFECTIVE,
// inherited colour (`tree.ts`'s `WidgetTree` resolves
// `data.color ?? inheritedColor` once, when the node is built): nothing
// here re-derives inheritance, and a row without children reads it
// through. A row with children shows the one colour its parts all show,
// when they share one, and otherwise its own `node.color` (OpenSpec
// `colour-a-node-by-what-it-holds`): its parts are every node without
// children beneath it, and the node itself when it has a model of its
// own. The snapshot's colour is left as it is.

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
  /** Invisible only because a PROPER ancestor is hidden, or because the
   * shown layer leaves the row out (`outsideLayer`) -- independent of
   * this node's own `hidden` (design D5's fourth and fifth rows). */
  obscured: boolean;
  /** The name of the nearest hidden ancestor, for the accessible name of
   * an obscured row's visibility control; `null` when not obscured. */
  hidingAncestor: string | null;
  /** The label of the shown layer when neither this row's node nor any
   * node below it is on that layer, else `null` (OpenSpec
   * `show-only-a-layer`, design Decision 5). Such a row is `obscured`,
   * and its visibility control keeps the node's own setting. */
  outsideLayer: string | null;
  /** The colour this row shows, or `null`: for a node with children,
   * the one colour all its parts show when they share one; otherwise the
   * node's effective, inherited colour, `node.color` (OpenSpec
   * `colour-a-node-by-what-it-holds`). */
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

  // One post-order pass over the whole snapshot, before the row walk
  // (design Decisions 1 and 5): for every node, the one colour its parts
  // share, or `null` when they share none. A node without children is its
  // own part; a node with children holds its children's parts, and itself
  // when it has a model of its own. Colours are compared as the strings
  // the snapshot reports, and a part with no colour shares with nothing.
  // Every node is visited once, whatever is expanded.
  const shared = new Map<AssemblyNode, string | null>();
  const gather = (node: AssemblyNode): string | null => {
    const children = node.children;
    let colour: string | null | undefined =
      children.length === 0 || node.model ? node.color : undefined;
    for (const child of children) {
      const held = gather(child);
      colour = colour === undefined || colour === held ? held : null;
    }
    const result = colour ?? null;
    shared.set(node, result);
    return result;
  };
  gather(assembly);

  // One post-order pass for the shown layer (design Decision 5): whether
  // the node or any node below it is on it. A node's layers are already
  // effective, so a node's own report covers every ancestor's. Read only
  // while a layer is shown, so a snapshot without `layers` is never asked.
  const shownLayer = navigation.layer ?? null;
  const holdsLayer = new Map<AssemblyNode, boolean>();
  if (shownLayer !== null) {
    const hold = (node: AssemblyNode): boolean => {
      let holds = node.layers.includes(shownLayer.key);
      for (const child of node.children) {
        if (hold(child)) holds = true;
      }
      holdsLayer.set(node, holds);
      return holds;
    };
    hold(assembly);
  }

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
    const partsColour = shared.get(node) ?? null;
    const outsideLayer = shownLayer !== null && holdsLayer.get(node) === false
      ? shownLayer.label : null;

    rows.push({
      node,
      key,
      depth,
      expandable,
      expanded,
      active: local.active === key,
      root: isRoot,
      hidden,
      obscured: hidingAncestor !== null || outsideLayer !== null,
      hidingAncestor,
      outsideLayer,
      color: expandable && partsColour !== null ? partsColour : node.color,
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
  // What obscures the row, hiding ancestor first, then the shown layer.
  const reasons = [
    ...(row.hidingAncestor !== null ? [`hidden with ${row.hidingAncestor}`] : []),
    ...(row.outsideLayer !== null ? [`not on the shown layer ${row.outsideLayer}`] : []),
  ];
  const label = reasons.length > 0
    ? `Visibility for ${row.node.name} (${reasons.join(', ')})`
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
