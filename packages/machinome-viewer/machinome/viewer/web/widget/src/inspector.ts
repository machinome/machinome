/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The inspector layout: a collapsible assembly sidebar composed beside
// the viewer inside one host element (design D1-D7, ADR-051). It is
// framework-free plain DOM, exactly as the navigator it hosts is.
//
// `mount()` cannot run in jsdom -- it builds a THREE.WebGLRenderer, which
// jsdom gives no WebGL context for -- so this module takes `mount` and
// `mountNavigator` through an internal seam, `mountInspectorWith`, that
// its own test stubs (design D15). `mountInspector` is the only thing
// `widget.ts` sees; the seam is not re-exported from there.

import { registerFullscreenRoot } from './fullscreen';
import { mountNavigator, NavigatorHandle, NavigatorOptions } from './navigator';
import { mount, ViewerHandle, ViewerOptions } from './viewer';

export interface InspectorOptions extends ViewerOptions {
  /** Whether the assembly sidebar starts open; default 'collapsed'. */
  sidebar?: 'collapsed' | 'open';
  /** The navigator's own options, passed through untouched. */
  navigator?: NavigatorOptions;
  /** Inject the layout's stylesheet; default 'inject'. Also the default
   * for `navigator.styles` (design D4). */
  styles?: 'inject' | 'none';
}

export interface InspectorHandle {
  /** The mounted viewer. The whole ViewerHandle, not a copy of part of
   * it (design D2). */
  viewer: ViewerHandle;
  /** The mounted navigator. */
  navigator: NavigatorHandle;
  /** Whether the sidebar is open right now. */
  sidebarOpen(): boolean;
  /** Open or close the sidebar, as the toggle does. */
  setSidebar(open: boolean): void;
  /** Dispose navigator then viewer, and empty the target. Idempotent. */
  dispose(): void;
}

const STYLE_ID = 'machinome-inspector-style';

// The class contract and the custom-property defaults (design D6, D13's
// pattern). The rail and its toggle are always in the DOM (design D5);
// collapsing removes only the sidebar from layout, via `hidden`
// (design D6) -- the stylesheet reinforces the UA `display: none` that
// attribute already gets, so a host stylesheet loaded before this one
// cannot accidentally re-show it.
const INSPECTOR_STYLESHEET = `
.machinome-inspector {
  --machinome-inspector-sidebar-width: 260px;
  --machinome-inspector-rail-width: 32px;
  --machinome-inspector-bg: transparent;
  --machinome-inspector-fg: inherit;
  --machinome-inspector-border: rgba(128, 128, 128, 0.35);
  --machinome-inspector-toggle-bg: rgba(128, 128, 128, 0.12);
  --machinome-inspector-toggle-hover-bg: rgba(128, 128, 128, 0.24);
  --machinome-inspector-focus-ring: currentColor;
  background: var(--machinome-inspector-bg);
  color: var(--machinome-inspector-fg);
  display: flex;
  height: 100%;
  width: 100%;
}
.machinome-inspector-rail {
  border-right: 1px solid var(--machinome-inspector-border);
  display: flex;
  flex: 0 0 var(--machinome-inspector-rail-width);
  flex-direction: column;
  align-items: center;
  padding-top: 4px;
}
.machinome-inspector-toggle {
  background: var(--machinome-inspector-toggle-bg);
  border: 1px solid var(--machinome-inspector-border);
  border-radius: 4px;
  color: inherit;
  cursor: pointer;
  font: inherit;
  padding: 4px 2px;
  writing-mode: vertical-rl;
}
.machinome-inspector-toggle:hover {
  background: var(--machinome-inspector-toggle-hover-bg);
}
.machinome-inspector-toggle:focus-visible {
  outline: 2px solid var(--machinome-inspector-focus-ring);
  outline-offset: 1px;
}
.machinome-inspector-sidebar {
  border-right: 1px solid var(--machinome-inspector-border);
  flex: 0 0 var(--machinome-inspector-sidebar-width);
  min-width: 0;
  overflow: auto;
}
.machinome-inspector-sidebar[hidden] {
  display: none;
}
.machinome-inspector-viewer {
  flex: 1 1 auto;
  min-width: 0;
  position: relative;
}
.machinome-inspector :is(
  .driver-descend, .run-descend, .clocked-descend,
  .driver-descend-separator, .run-descend-separator,
  .clocked-descend-separator
),
.machinome-inspector .clocked-reset {
  display: none;
}
`;

function injectStylesheet(doc: Document): void {
  if (doc.getElementById(STYLE_ID)) {
    return;
  }
  const style = doc.createElement('style');
  style.id = STYLE_ID;
  style.textContent = INSPECTOR_STYLESHEET;
  doc.head.append(style);
}

/** Resolves the mount target, exactly as `viewer.ts`'s `resolveContainer`
 * and `navigator.ts`'s `resolveTarget` do -- duplicated rather than
 * imported, for the same reason `navigator.ts` gives (design D2): so
 * this module's own test drags no renderer with it. */
function resolveTarget(target: HTMLElement | string): HTMLElement {
  if (typeof target !== 'string') {
    return target;
  }
  const element = document.querySelector<HTMLElement>(target);
  if (!element) {
    throw new Error(`machinome-viewer: no element matches "${target}"`);
  }
  return element;
}

let nextSidebarId = 0;

/** The seam design D15 asks for: `mount` and `mountNavigator` arrive as
 * parameters rather than module-level imports called directly, so a
 * jsdom test can stub both and the real wiring -- one line, below --
 * stays the only thing exercising three.js. */
export async function mountInspectorWith(
  mountFn: typeof mount,
  mountNavigatorFn: typeof mountNavigator,
  target: HTMLElement | string,
  sourceUrl: string,
  options: InspectorOptions = {},
): Promise<InspectorHandle> {
  const container = resolveTarget(target);
  const { sidebar, navigator: navigatorOptions, styles, ...viewerOptions } = options;
  const stylesMode = styles ?? 'inject';
  const label = navigatorOptions?.label ?? 'Assembly';

  // Built in the target's own document, as the navigator is, so a layout
  // mounted inside an iframe belongs to that iframe.
  const doc = container.ownerDocument;
  if (stylesMode === 'inject') {
    injectStylesheet(doc);
  }

  const root = doc.createElement('div');
  root.className = 'machinome-inspector';

  const rail = doc.createElement('div');
  rail.className = 'machinome-inspector-rail';

  const sidebarId = `machinome-inspector-sidebar-${(nextSidebarId += 1)}`;
  const sidebarEl = doc.createElement('div');
  sidebarEl.className = 'machinome-inspector-sidebar';
  sidebarEl.id = sidebarId;

  const toggle = doc.createElement('button');
  toggle.type = 'button';
  toggle.className = 'machinome-inspector-toggle';
  toggle.setAttribute('aria-controls', sidebarId);
  toggle.textContent = label;

  const viewerPane = doc.createElement('div');
  viewerPane.className = 'machinome-inspector-viewer';

  rail.append(toggle);
  root.append(rail, sidebarEl, viewerPane);
  container.append(root);

  let open = sidebar === 'open';

  function applySidebarState(): void {
    toggle.setAttribute('aria-expanded', String(open));
    sidebarEl.hidden = !open;
  }
  applySidebarState();

  function setSidebar(next: boolean): void {
    open = next;
    applySidebarState();
  }

  toggle.addEventListener('click', () => setSidebar(!open));

  // Registered BEFORE the viewer mounts (OpenSpec `go-fullscreen`, design
  // D1): the viewer's own full-screen controller resolves its root through
  // this registry while it builds, so the whole composed layout -- rail,
  // sidebar and viewer pane together -- goes full screen as one, not only
  // the pane.
  registerFullscreenRoot(viewerPane, root);

  let viewer: ViewerHandle;
  try {
    // The layout builds its skeleton synchronously above, then `await`s
    // the viewer on its own pane (design D1): a navigator cannot exist
    // before a viewer handle does, so there is no honest synchronous
    // version of this call.
    viewer = await mountFn(viewerPane, sourceUrl, viewerOptions);
  } catch (error) {
    // The viewer refused the document: leave nothing behind rather than
    // presenting a sidebar around a viewer that does not exist
    // (design D1), and rethrow the ORIGINAL error unchanged.
    container.replaceChildren();
    throw error;
  }

  const navigator = mountNavigatorFn(sidebarEl, viewer, {
    ...navigatorOptions,
    styles: navigatorOptions?.styles ?? stylesMode,
  });

  let disposed = false;

  return {
    viewer,
    navigator,
    sidebarOpen(): boolean {
      return open;
    },
    setSidebar,
    dispose(): void {
      if (disposed) {
        return;
      }
      disposed = true;
      // Navigator first, then the viewer, then the target -- the
      // navigator cancels its subscription before the viewer's own
      // teardown has anything left to notify (design D2).
      navigator.dispose();
      viewer.dispose();
      container.replaceChildren();
    },
  };
}

export function mountInspector(
  target: HTMLElement | string,
  sourceUrl: string,
  options?: InspectorOptions,
): Promise<InspectorHandle> {
  return mountInspectorWith(mount, mountNavigator, target, sourceUrl, options);
}
