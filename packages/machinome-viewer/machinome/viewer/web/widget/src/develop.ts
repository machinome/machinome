/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The development page's own mount, built on the inspector (design D10).
// `develop.html` does two things no bundle code can do -- check whether
// the bundle exists at all, and inject the script tag that loads it --
// and then calls this. Everything else that page needs is here, where
// vitest can reach it.

import { InspectorHandle, InspectorOptions, mountInspector } from './inspector';
import { Reloader } from './reloader';

export interface DevelopmentOptions extends InspectorOptions {
  /** The document; default '/build/viewer.json'. */
  sourceUrl?: string;
}

export interface DevelopmentHandle {
  inspector: InspectorHandle;
  dispose(): void;
}

const DEFAULT_SOURCE_URL = '/build/viewer.json';
const STYLE_ID = 'machinome-develop-style';
const ERROR_CLASS = 'machinome-inspector-error';

// design D11: the build error is a pane OVER a viewer that stays
// mounted, not a replacement for it -- `position: fixed` covers the
// whole page regardless of where the inspector's own target sits, which
// is exactly right for a page whose whole body is the development app.
const DEVELOP_STYLESHEET = `
.${ERROR_CLASS} {
  position: fixed;
  inset: 0;
  margin: 0;
  padding: 1rem;
  overflow: auto;
  white-space: pre-wrap;
  background: rgba(20, 20, 20, 0.92);
  color: #fff;
  font: 13px ui-monospace, SFMono-Regular, Menlo, monospace;
  z-index: 10000;
}
`;

function injectStylesheet(doc: Document): void {
  if (doc.getElementById(STYLE_ID)) {
    return;
  }
  const style = doc.createElement('style');
  style.id = STYLE_ID;
  style.textContent = DEVELOP_STYLESHEET;
  doc.head.append(style);
}

/** `root.name`, split into words the way a maker wrote it: a capital
 * starts a new word. Ported from `app/src/viewerShell.ts:89-93`, byte
 * for byte. */
function titleFromName(name: string): string {
  return name.replace(/([A-Z])/g, ' $1').trim();
}

/** The seam design D15's pattern extends to (`mountInspector` itself
 * calls the real `mount()`, which needs WebGL): `mountDevelopmentWith`
 * takes it as a parameter so this module's own test stubs it, and
 * `mountDevelopment` is the one line wiring the real one. */
export async function mountDevelopmentWith(
  mountInspectorFn: typeof mountInspector,
  target: HTMLElement | string,
  options: DevelopmentOptions = {},
): Promise<DevelopmentHandle> {
  const { sourceUrl, ...inspectorOptions } = options;
  const url = sourceUrl ?? DEFAULT_SOURCE_URL;

  const inspector = await mountInspectorFn(target, url, {
    animation: 'inline', autoplay: true, sidebar: 'open', ...inspectorOptions,
  });

  const doc = typeof target === 'string' ? document : target.ownerDocument;
  injectStylesheet(doc);

  let errorPane: HTMLElement | null = null;
  function showError(message: string): void {
    if (message) {
      if (!errorPane) {
        errorPane = doc.createElement('pre');
        errorPane.className = ERROR_CLASS;
        doc.body.append(errorPane);
      }
      errorPane.textContent = message;
    } else if (errorPane) {
      errorPane.remove();
      errorPane = null;
    }
  }

  // Refetches the document, exactly as `viewerShell.ts:89-93` did: a
  // republished snapshot names the tab, and the server sends
  // `Cache-Control: no-store` for it. Cosmetic, so a refused fetch here
  // must not fail the mount that already succeeded.
  try {
    const response = await fetch(url);
    const document_ = await response.json() as { root: { name: string } };
    doc.title = titleFromName(document_.root.name);
  } catch {
    // Title is cosmetic; leave whatever the page already had.
  }

  // The partial update, unchanged (design D12): every reload ends in
  // the handle's own `manifestChanged()`, never a page load and never
  // `inspector.viewer.reload()` (which would refetch every artifact).
  const reloader = new Reloader(showError, () => {
    inspector.viewer.manifestChanged().catch((error) => showError(String(error)));
  });

  let disposed = false;

  return {
    inspector,
    dispose(): void {
      if (disposed) {
        return;
      }
      disposed = true;
      if (errorPane) {
        errorPane.remove();
        errorPane = null;
      }
      reloader.reloadTrigger?.close();
      inspector.dispose();
    },
  };
}

export function mountDevelopment(
  target: HTMLElement | string,
  options?: DevelopmentOptions,
): Promise<DevelopmentHandle> {
  return mountDevelopmentWith(mountInspector, target, options);
}
