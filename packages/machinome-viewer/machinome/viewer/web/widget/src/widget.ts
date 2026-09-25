/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The published entry point deliberately keeps the auto-mount contract. Hosts
// that need an imperative viewer import viewer.ts instead, whose module load is
// side-effect free.

import { mount, ViewerOptions } from './viewer';
import { mountInspector } from './inspector';
import { layoutChoice } from './layout';
import { API_VERSION } from './version';

export { mount } from './viewer';
export { API_VERSION } from './version';
export { mountNavigator } from './navigator';
export type { NavigatorHandle, NavigatorOptions } from './navigator';
export { mountInspector } from './inspector';
export type { InspectorHandle, InspectorOptions } from './inspector';
export { mountDevelopment } from './develop';
export type { DevelopmentHandle, DevelopmentOptions } from './develop';
export const apiVersion = API_VERSION;

function autoMount(): void {
  const params = new URLSearchParams(window.location.search);
  const options: ViewerOptions = { animation: 'inline' };
  const time = Number(params.get('t'));
  if (params.has('t') && !Number.isNaN(time)) {
    options.time = time;
  }
  if (params.get('autoplay') === '0') {
    options.autoplay = false;
  }
  document.querySelectorAll<HTMLElement>('[data-machinome-widget]').forEach(
    (element) => {
      const sourceUrl = element.dataset.machinomeWidget;
      if (!sourceUrl) {
        return;
      }
      // The layout a container asks for (design D8): no attribute and no
      // query string mounts the plain viewer, unchanged from every page
      // written before this capability existed.
      const choice = layoutChoice(element.dataset, params);
      if (typeof choice.layout === 'object') {
        element.textContent = `machinome-viewer: unknown layout "${choice.layout.unknown}"`;
        return;
      }
      const mounted = choice.layout === 'inspector'
        ? mountInspector(element, sourceUrl, { ...options, sidebar: choice.sidebar })
        : mount(element, sourceUrl, options);
      mounted.catch((error) => {
        element.textContent = `machinome-viewer: ${error.message}`;
        console.error(error);
      });
    },
  );
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoMount);
  } else {
    autoMount();
  }
}
