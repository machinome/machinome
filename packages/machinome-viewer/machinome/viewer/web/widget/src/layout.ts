/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The auto-mount's layout decision (design D8), extracted from
// `widget.ts` so it is testable with no DOM at all: `data-solid-layout`
// / `data-solid-sidebar` on the container, `?layout=` / `?sidebar=` on
// the page, the query string winning over the attribute in both
// directions, and an unrecognised layout value reported by name rather
// than mounting something the page did not ask for. Not re-exported
// from `widget.ts`: it decides nothing a host calls directly.

/** The subset of `HTMLElement.dataset` this decision reads. */
export interface LayoutDataset {
  solidLayout?: string;
  solidSidebar?: string;
}

export interface LayoutChoice {
  /** `{ unknown: value }` when the container or the query string named a
   * layout this page does not recognise, refused by name rather than
   * silently ignored. */
  layout: 'viewer' | 'inspector' | { unknown: string };
  /** Present only when the attribute or the query string named one of
   * the two recognised values; absent otherwise, so a mount call can
   * default it itself. */
  sidebar?: 'open' | 'collapsed';
}

export function layoutChoice(dataset: LayoutDataset, search: URLSearchParams): LayoutChoice {
  // A container with no selection at all mounts exactly what it mounts
  // today (design D8): the plain viewer.
  const layoutValue = search.get('layout') ?? dataset.solidLayout ?? 'viewer';
  const sidebarValue = search.get('sidebar') ?? dataset.solidSidebar;

  const choice: LayoutChoice = {
    layout: layoutValue === 'viewer' || layoutValue === 'inspector'
      ? layoutValue
      : { unknown: layoutValue },
  };
  if (sidebarValue === 'open' || sidebarValue === 'collapsed') {
    choice.sidebar = sidebarValue;
  }
  return choice;
}
