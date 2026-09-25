/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// Full-screen viewing (OpenSpec `go-fullscreen`, design D1-D9). The pure
// decisions -- does this key toggle, where does the button go, is full
// screen available, which background -- are plain functions any test can
// call with hand-built values; the DOM controller below renders exactly
// what they decide and touches nothing else. `viewer.ts` and `inspector.ts`
// import this module for TYPES and for the seam design D1 asks for: a
// module-private root registry, so a mount option is never needed for it.

/** The full-screen root a container goes full screen AS, when it is part
 * of a layout the package composed (design D1). Module-private apart from
 * the register and resolve functions below: `inspector.ts` registers its
 * viewer pane before mounting the viewer, and `viewer.ts` resolves its own
 * container through it. A plain `mount()` container that was never
 * registered resolves to itself. */
const fullscreenRoots = new WeakMap<HTMLElement, HTMLElement>();

export function registerFullscreenRoot(
  container: HTMLElement, root: HTMLElement,
): void {
  fullscreenRoots.set(container, root);
}

export function fullscreenRootFor(container: HTMLElement): HTMLElement {
  return fullscreenRoots.get(container) ?? container;
}

// ---------------------------------------------------------------------
// Pure decisions (design D2, D4, D5, D6). No DOM: a controller and its
// test drive these with hand-built values or with jsdom's own objects,
// which satisfy the same duck-typed shapes.

export type FullscreenPlacement = 'run-transport' | 'animation-bar' | 'corner';

/** Where the button goes, from what the viewer just built (design D2):
 * the running transport, else the inline STYLED animation bar, else the
 * corner. A toggled or externally driven animation bar, a static model, a
 * drivers-only posed model and a clocked machine (whose transport lives in
 * the side rail) all fall through to the corner. */
export function fullscreenPlacement(input: {
  runTransport: boolean;
  inlineAnimationBar: boolean;
}): FullscreenPlacement {
  if (input.runTransport) {
    return 'run-transport';
  }
  if (input.inlineAnimationBar) {
    return 'animation-bar';
  }
  return 'corner';
}

/** Full screen is offered only in continuous render mode, and only where
 * the document itself permits it (design D5): false in an iframe without
 * `allowfullscreen`, and on a browser with no element full screen. Only
 * the unprefixed property is read (0.2, evidence.md). */
export function fullscreenAvailable(
  doc: { fullscreenEnabled?: boolean },
  renderMode: 'continuous' | 'on-demand',
): boolean {
  return renderMode === 'continuous' && doc.fullscreenEnabled === true;
}

interface EditableTarget {
  tagName?: string;
  isContentEditable?: boolean;
}

const EDITABLE_TAGS = new Set(['INPUT', 'TEXTAREA', 'SELECT']);

function isEditableTarget(target: unknown): boolean {
  if (target === null || typeof target !== 'object') {
    return false;
  }
  const element = target as EditableTarget;
  if (typeof element.tagName === 'string' && EDITABLE_TAGS.has(element.tagName)) {
    return true;
  }
  return element.isContentEditable === true;
}

/** The event shape `togglesFullscreen` reads: exactly a `KeyboardEvent`'s
 * own fields, so the real listener passes one unchanged and a test passes
 * a hand-built object. */
export interface FullscreenKeyEvent {
  key: string;
  ctrlKey: boolean;
  altKey: boolean;
  metaKey: boolean;
  repeat: boolean;
  defaultPrevented: boolean;
  target: unknown;
}

export interface FullscreenKeyContext {
  /** The event's target is inside this mount's full-screen root. */
  insideRoot: boolean;
  /** The event's target is the document's `body` or `documentElement`:
   * nothing is focused. */
  bodyTarget: boolean;
  /** This mount is the only live viewer able to go full screen in this
   * document -- the only case a `bodyTarget` key is honest about (design
   * D4). */
  soleViewer: boolean;
}

/** Whether `f` (or `F`) toggles full screen for this mount (design D4). */
export function togglesFullscreen(
  event: FullscreenKeyEvent,
  context: FullscreenKeyContext,
): boolean {
  if (event.key !== 'f' && event.key !== 'F') {
    return false;
  }
  if (event.ctrlKey || event.altKey || event.metaKey) {
    return false;
  }
  if (event.repeat || event.defaultPrevented) {
    return false;
  }
  if (isEditableTarget(event.target)) {
    return false;
  }
  return context.insideRoot || (context.bodyTarget && context.soleViewer);
}

function isTransparent(color: string | null | undefined): boolean {
  if (!color) {
    return true;
  }
  const value = color.trim().toLowerCase();
  if (value === '' || value === 'transparent') {
    return true;
  }
  const match = value.match(/^rgba\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+\s*,\s*([\d.]+)\s*\)$/);
  if (match) {
    return Number(match[1]) === 0;
  }
  return false;
}

/** The background painted behind the root while it is full screen (design
 * D6): the first opaque colour walking from the root up to `<html>`, else
 * white -- the browser's own default canvas. Pure: the controller walks
 * the DOM and hands this the computed colours in order. */
export function fullscreenBackground(
  colors: readonly (string | null | undefined)[],
): string {
  for (const color of colors) {
    if (!isTransparent(color)) {
      return color as string;
    }
  }
  return 'white';
}

// ---------------------------------------------------------------------
// The DOM controller (design D1, D3, D9). One per mount, created whether
// or not full screen is available: an unavailable mount's controller
// creates no button and installs no listener, so every call site treats
// `place`/`dispose` uniformly.

export interface FullscreenBars {
  /** The `.run-transport` bar just built, or `undefined` when the mount
   * has none. */
  runTransport?: HTMLElement | undefined;
  /** The `.animation-controls` bar just built, but ONLY when it is the
   * inline, styled bar (design D2) -- a toggled or externally driven bar
   * is not "permanent" and does not count. */
  animationBar?: HTMLElement | undefined;
}

export interface FullscreenController {
  /** Re-decide and move the button, from the bars this rebuild just
   * built. Idempotent: safe to call after every chrome rebuild, whether
   * or not it changed anything relevant (design D2). */
  place(bars: FullscreenBars): void;
  /** Remove listeners, leave full screen if this root holds it, and
   * remove the button. Idempotent. */
  dispose(): void;
}

const documentControllers = new WeakMap<Document, Set<object>>();

function registerController(doc: Document, token: object): void {
  let set = documentControllers.get(doc);
  if (!set) {
    set = new Set();
    documentControllers.set(doc, set);
  }
  set.add(token);
}

function unregisterController(doc: Document, token: object): void {
  documentControllers.get(doc)?.delete(token);
}

function isSoleController(doc: Document, token: object): boolean {
  const set = documentControllers.get(doc);
  return set !== undefined && set.size === 1 && set.has(token);
}

const BAR_BUTTON_STYLE =
  'background:none;border:none;color:inherit;cursor:pointer;'
  + 'padding:2px 4px;line-height:1;display:inline-flex;'
  + 'align-items:center;justify-content:center;flex:0 0 auto;';

const CORNER_BUTTON_STYLE =
  'position:absolute;right:8px;bottom:8px;width:36px;height:36px;'
  + 'display:flex;align-items:center;justify-content:center;'
  + 'background:rgba(30,33,38,0.65);color:#fff;border:none;'
  + 'border-radius:4px;cursor:pointer;padding:0;z-index:2;';

// Drawn by the package itself, never a font glyph (design D3): the run
// transport already avoids transport glyphs for the same reason -- a
// minimal font renders them as empty boxes. "Enter" is four brackets
// standing at the box's own corners, arms pointing inward; "exit" is the
// same four brackets pulled in toward the centre, arms pointing outward.
const ENTER_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" '
  + 'aria-hidden="true" focusable="false"><path d="M4 9V4h5M15 4h5v5'
  + 'M20 15v5h-5M9 20H4v-5" fill="none" stroke="currentColor" '
  + 'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

const EXIT_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" '
  + 'aria-hidden="true" focusable="false"><path d="M9 4V9H4M15 4V9H20'
  + 'M15 20V15H20M9 20V15H4" fill="none" stroke="currentColor" '
  + 'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

function backgroundChain(root: HTMLElement, doc: Document): string[] {
  const view = doc.defaultView;
  if (!view) {
    return [];
  }
  const colors: string[] = [];
  let node: HTMLElement | null = root;
  while (node) {
    colors.push(view.getComputedStyle(node).backgroundColor);
    if (node === doc.documentElement) {
      break;
    }
    node = node.parentElement;
  }
  return colors;
}

/** Build the full-screen controller for one mount (design D1, D3-D9).
 * `root` is this mount's full-screen root (`fullscreenRootFor(container)`);
 * `container` is the viewer's own element, where the corner button is
 * anchored regardless of what the root is (design D2). Returns an inert
 * controller, with no button and no listener installed, where
 * `fullscreenAvailable` is false (design D5). */
export function createFullscreenController(
  root: HTMLElement,
  container: HTMLElement,
  renderMode: 'continuous' | 'on-demand',
): FullscreenController {
  const doc = container.ownerDocument;
  if (!fullscreenAvailable(doc, renderMode)) {
    return { place() {}, dispose() {} };
  }

  const token = {};
  let disposed = false;
  let previousBackground: string | null = null;

  const button = doc.createElement('button');
  button.type = 'button';
  button.className = 'machinome-fullscreen';
  button.style.cssText = CORNER_BUTTON_STYLE;

  function updateState(): void {
    const active = doc.fullscreenElement === root;
    button.innerHTML = active ? EXIT_ICON : ENTER_ICON;
    button.setAttribute('aria-label', active ? 'Exit full screen' : 'Full screen');
    button.title = active ? 'Exit full screen (f)' : 'Full screen (f)';
  }
  updateState();

  function applyBackground(): void {
    previousBackground = root.style.backgroundColor;
    root.style.backgroundColor = fullscreenBackground(backgroundChain(root, doc));
  }

  function restoreBackground(): void {
    root.style.backgroundColor = previousBackground ?? '';
    previousBackground = null;
  }

  function toggle(): void {
    if (doc.fullscreenElement === root) {
      doc.exitFullscreen().catch(() => undefined);
    } else {
      root.requestFullscreen().catch(() => undefined);
    }
  }

  function onFullscreenChange(): void {
    if (doc.fullscreenElement === root) {
      applyBackground();
    } else if (previousBackground !== null) {
      restoreBackground();
    }
    updateState();
  }

  function onKeydown(event: KeyboardEvent): void {
    const target = event.target;
    const insideRoot = target instanceof Node && root.contains(target);
    const bodyTarget = target === doc.body || target === doc.documentElement;
    const soleViewer = isSoleController(doc, token);
    if (!togglesFullscreen(event, { insideRoot, bodyTarget, soleViewer })) {
      return;
    }
    event.preventDefault();
    toggle();
  }

  button.addEventListener('click', toggle);
  doc.addEventListener('fullscreenchange', onFullscreenChange);
  doc.addEventListener('keydown', onKeydown);
  registerController(doc, token);

  return {
    place(bars: FullscreenBars): void {
      if (disposed) {
        return;
      }
      const placement = fullscreenPlacement({
        runTransport: bars.runTransport !== undefined,
        inlineAnimationBar: bars.animationBar !== undefined,
      });
      if (placement === 'run-transport') {
        button.style.cssText = BAR_BUTTON_STYLE;
        bars.runTransport!.append(button);
      } else if (placement === 'animation-bar') {
        button.style.cssText = BAR_BUTTON_STYLE;
        bars.animationBar!.append(button);
      } else {
        button.style.cssText = CORNER_BUTTON_STYLE;
        container.append(button);
      }
    },
    dispose(): void {
      if (disposed) {
        return;
      }
      disposed = true;
      unregisterController(doc, token);
      doc.removeEventListener('fullscreenchange', onFullscreenChange);
      doc.removeEventListener('keydown', onKeydown);
      if (doc.fullscreenElement === root) {
        doc.exitFullscreen().catch(() => undefined);
      }
      button.remove();
    },
  };
}
