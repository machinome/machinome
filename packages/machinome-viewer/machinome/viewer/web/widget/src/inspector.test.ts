/**
 * @vitest-environment jsdom
 */
/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The layout against STUB `mount` and `mountNavigator` (design D15):
// `mount()` builds a THREE.WebGLRenderer, which jsdom cannot give a
// context for, so this test never calls the real one. It calls the
// internal `mountInspectorWith(mountFn, mountNavigatorFn, ...)` seam
// directly, which is exactly what the exported `mountInspector` does
// with the real collaborators (proved against the real bundle in
// `tests/test_widget_e2e.py`, increment 2).

import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';
import {
  InspectorHandle, mountInspectorWith,
} from './inspector';
import type { NavigatorHandle, NavigatorOptions } from './navigator';
import type { ViewerHandle, ViewerOptions } from './viewer';

let container: HTMLElement;
const handles: InspectorHandle[] = [];

beforeEach(() => {
  container = document.createElement('div');
  document.body.append(container);
});

afterEach(() => {
  handles.splice(0).forEach((handle) => handle.dispose());
  document.body.replaceChildren();
  document.getElementById('solid-node-inspector-style')?.remove();
  document.getElementById('solid-node-navigator-style')?.remove();
  vi.restoreAllMocks();
});

interface MountCall {
  target: HTMLElement | string;
  sourceUrl: string;
  options: ViewerOptions;
}

interface NavigatorMountCall {
  target: HTMLElement | string;
  viewer: ViewerHandle;
  options: NavigatorOptions | undefined;
}

/** A record of every call, and the order disposal happens in -- the
 * whole surface `inspector.ts` uses from each collaborator. */
function stubs(order: string[] = []) {
  const mountCalls: MountCall[] = [];
  const navigatorCalls: NavigatorMountCall[] = [];
  let mountResult: 'resolve' | 'reject' = 'resolve';
  let mountError: Error = new Error('mount refused');

  const viewerHandle = {
    dispose: () => order.push('viewer'),
    apiVersion: 11,
  } as unknown as ViewerHandle;

  const navigatorHandle = {
    dispose: () => order.push('navigator'),
  } as unknown as NavigatorHandle;

  const mountFn = vi.fn(async (
    target: HTMLElement | string, sourceUrl: string, options: ViewerOptions = {},
  ): Promise<ViewerHandle> => {
    mountCalls.push({ target, sourceUrl, options });
    if (mountResult === 'reject') {
      throw mountError;
    }
    return viewerHandle;
  });

  const mountNavigatorFn = vi.fn((
    target: HTMLElement | string, viewer: ViewerHandle, options?: NavigatorOptions,
  ): NavigatorHandle => {
    navigatorCalls.push({ target, viewer, options });
    return navigatorHandle;
  });

  return {
    mountFn, mountNavigatorFn, mountCalls, navigatorCalls, viewerHandle, navigatorHandle,
    rejectWith(error: Error) { mountResult = 'reject'; mountError = error; },
  };
}

async function mount(
  options?: Parameters<typeof mountInspectorWith>[4],
  target: HTMLElement | string = container,
  order: string[] = [],
) {
  const collaborators = stubs(order);
  const handle = await mountInspectorWith(
    collaborators.mountFn, collaborators.mountNavigatorFn, target, 'viewer.json', options,
  );
  handles.push(handle);
  return { handle, order, ...collaborators };
}

describe('mounting', () => {
  it('builds one root under the target: a rail with the toggle, a sidebar, a viewer pane', async () => {
    const { mountCalls } = await mount();

    expect(container.children.length).toBe(1);
    const root = container.querySelector('.solid-inspector')!;
    expect(root).not.toBeNull();
    expect(root.parentElement).toBe(container);

    const rail = root.querySelector('.solid-inspector-rail');
    expect(rail).not.toBeNull();
    const toggle = rail!.querySelector('.solid-inspector-toggle');
    expect(toggle).not.toBeNull();

    const sidebar = root.querySelector('.solid-inspector-sidebar');
    expect(sidebar).not.toBeNull();

    const viewerPane = root.querySelector('.solid-inspector-viewer');
    expect(viewerPane).not.toBeNull();

    // mount() was called with the VIEWER PANE, never the target itself
    // (design D5) -- the whole reason the viewer gets a pane of its own.
    expect(mountCalls).toHaveLength(1);
    expect(mountCalls[0].target).toBe(viewerPane);
    expect(mountCalls[0].sourceUrl).toBe('viewer.json');
  });

  it('gives the toggle aria-expanded, aria-controls naming the sidebar, and the accessible name Assembly', async () => {
    await mount();

    const toggle = container.querySelector<HTMLButtonElement>('.solid-inspector-toggle')!;
    const sidebar = container.querySelector<HTMLElement>('.solid-inspector-sidebar')!;
    expect(toggle.getAttribute('aria-expanded')).toBe('false');
    expect(toggle.getAttribute('aria-controls')).toBe(sidebar.id);
    expect(sidebar.id).not.toBe('');
    expect(toggle.textContent).toBe('Assembly');
    expect(sidebar.hidden).toBe(true);
  });

  it('defaults the sidebar to collapsed, and sidebar: "open" starts it open', async () => {
    const collapsed = await mount();
    const collapsedToggle = container.querySelector<HTMLButtonElement>('.solid-inspector-toggle')!;
    expect(collapsedToggle.getAttribute('aria-expanded')).toBe('false');
    expect(container.querySelector<HTMLElement>('.solid-inspector-sidebar')!.hidden).toBe(true);
    collapsed.handle.dispose();
    container.replaceChildren();

    const { handle } = await mount({ sidebar: 'open' });
    const toggle = container.querySelector<HTMLButtonElement>('.solid-inspector-toggle')!;
    expect(toggle.getAttribute('aria-expanded')).toBe('true');
    expect(container.querySelector<HTMLElement>('.solid-inspector-sidebar')!.hidden).toBe(false);
    handle.dispose();
  });

  it('mounts the navigator into the sidebar, passing options.navigator through untouched', async () => {
    const navigatorOptions: NavigatorOptions = { label: 'Parts', fullAssembly: false };
    const { navigatorCalls, viewerHandle } = await mount({ navigator: navigatorOptions });

    expect(navigatorCalls).toHaveLength(1);
    expect(navigatorCalls[0].target).toBe(container.querySelector('.solid-inspector-sidebar'));
    expect(navigatorCalls[0].viewer).toBe(viewerHandle);
    // Passed through untouched, plus styles defaulted from the layout's
    // own (design D4) -- asserted separately below.
    expect(navigatorCalls[0].options).toMatchObject(navigatorOptions);
  });

  it("defaults the navigator's own styles to the layout's (design D4)", async () => {
    const { navigatorCalls } = await mount({ styles: 'none' });
    expect(navigatorCalls[0].options?.styles).toBe('none');
  });

  it("an explicit navigator.styles wins over the layout's own", async () => {
    const { navigatorCalls } = await mount({ styles: 'none', navigator: { styles: 'inject' } });
    expect(navigatorCalls[0].options?.styles).toBe('inject');
  });
});

describe('the toggle', () => {
  it('opens and closes the sidebar on click, keeping focus on the toggle throughout', async () => {
    await mount();
    const toggle = container.querySelector<HTMLButtonElement>('.solid-inspector-toggle')!;
    const sidebar = container.querySelector<HTMLElement>('.solid-inspector-sidebar')!;

    toggle.focus();
    toggle.click();
    expect(toggle.getAttribute('aria-expanded')).toBe('true');
    expect(sidebar.hidden).toBe(false);
    expect(document.activeElement).toBe(toggle);

    toggle.click();
    expect(toggle.getAttribute('aria-expanded')).toBe('false');
    expect(sidebar.hidden).toBe(true);
    expect(document.activeElement).toBe(toggle);
  });

  // A real, focusable `<button type="button">` is keyboard-operable by
  // construction -- Enter and Space fire the same 'click' event a
  // pointer does, a browser default action jsdom does not simulate
  // (confirmed empirically; there is no synthetic click from a
  // KeyboardEvent here). What this test can prove in jsdom is that the
  // toggle answers a dispatched 'click' precisely as it does a
  // programmatic one, with no side channel (no tabIndex trick, no
  // separate keydown handler to disagree with the native one); the
  // Playwright suite (`tests/test_widget_e2e.py`, increment 2) proves a
  // real click reaches it in Chromium.
  it('answers a dispatched click event the same way (the keyboard\'s eventual effect)', async () => {
    await mount();
    const toggle = container.querySelector<HTMLButtonElement>('.solid-inspector-toggle')!;
    toggle.focus();
    toggle.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    expect(toggle.getAttribute('aria-expanded')).toBe('true');
    expect(document.activeElement).toBe(toggle);
  });

  it('is the same element across both states -- never destroyed by toggling', async () => {
    await mount();
    const toggle = container.querySelector<HTMLButtonElement>('.solid-inspector-toggle')!;
    toggle.click();
    expect(container.querySelector('.solid-inspector-toggle')).toBe(toggle);
    toggle.click();
    expect(container.querySelector('.solid-inspector-toggle')).toBe(toggle);
  });

  it('writes nothing to storage and rewrites no URL across a toggle', async () => {
    localStorage.clear();
    sessionStorage.clear();
    const before = window.location.href;
    await mount();
    const toggle = container.querySelector<HTMLButtonElement>('.solid-inspector-toggle')!;
    toggle.click();
    toggle.click();
    expect(localStorage.length).toBe(0);
    expect(sessionStorage.length).toBe(0);
    expect(window.location.href).toBe(before);
  });
});

describe('the handle', () => {
  it('sidebarOpen() follows the toggle', async () => {
    const { handle } = await mount();
    expect(handle.sidebarOpen()).toBe(false);
    container.querySelector<HTMLButtonElement>('.solid-inspector-toggle')!.click();
    expect(handle.sidebarOpen()).toBe(true);
  });

  it('setSidebar() does exactly what the toggle does', async () => {
    const { handle } = await mount();
    const toggle = container.querySelector<HTMLButtonElement>('.solid-inspector-toggle')!;
    const sidebar = container.querySelector<HTMLElement>('.solid-inspector-sidebar')!;

    handle.setSidebar(true);
    expect(toggle.getAttribute('aria-expanded')).toBe('true');
    expect(sidebar.hidden).toBe(false);
    expect(handle.sidebarOpen()).toBe(true);

    handle.setSidebar(false);
    expect(toggle.getAttribute('aria-expanded')).toBe('false');
    expect(sidebar.hidden).toBe(true);
    expect(handle.sidebarOpen()).toBe(false);
  });

  it('exposes the stub viewer handle and navigator handle as fields', async () => {
    const { handle, viewerHandle, navigatorHandle } = await mount();
    expect(handle.viewer).toBe(viewerHandle);
    expect(handle.navigator).toBe(navigatorHandle);
  });
});

describe('disposal', () => {
  it('disposes the navigator before the viewer, then empties the target', async () => {
    const order: string[] = [];
    const { handle } = await mount(undefined, container, order);
    handle.dispose();
    expect(order).toEqual(['navigator', 'viewer']);
    expect(container.children.length).toBe(0);
  });

  it('is harmless a second time', async () => {
    const { handle } = await mount();
    handle.dispose();
    expect(() => handle.dispose()).not.toThrow();
    expect(container.children.length).toBe(0);
  });
});

describe('the stylesheet', () => {
  it('injects exactly one identifiable stylesheet across two mounts', async () => {
    await mount();
    const second = document.createElement('div');
    document.body.append(second);
    await mount(undefined, second);

    expect(document.querySelectorAll('#solid-node-inspector-style').length).toBe(1);
  });

  it('injects neither the layout\'s nor the navigator\'s stylesheet under styles: "none"', async () => {
    await mount({ styles: 'none' });
    expect(document.getElementById('solid-node-inspector-style')).toBeNull();
    // The navigator itself is stubbed here, so its own stylesheet is not
    // injected by this test; the layout's default-for-navigator wiring
    // is asserted separately above ("defaults the navigator's own
    // styles to the layout's").
    expect(container.querySelector('.solid-inspector')).not.toBeNull();
  });

  it('passes className to the viewer pane\'s mount options, not the layout root', async () => {
    const { mountCalls } = await mount({ className: 'my-canvas' });
    expect(mountCalls[0].options.className).toBe('my-canvas');
    expect(container.querySelector('.solid-inspector')!.className.split(' '))
      .not.toContain('my-canvas');
  });
});

describe('a refused mount', () => {
  it('leaves the target empty and rethrows the original error', async () => {
    const order: string[] = [];
    const collaborators = stubs(order);
    const refusal = new Error('solid-widget: undeclared driver id "x"');
    collaborators.rejectWith(refusal);

    await expect(mountInspectorWith(
      collaborators.mountFn, collaborators.mountNavigatorFn, container, 'viewer.json', undefined,
    )).rejects.toBe(refusal);

    expect(container.children.length).toBe(0);
    expect(collaborators.navigatorCalls).toHaveLength(0);
  });
});

describe('a selector naming no element', () => {
  it('is refused with a message naming it', async () => {
    const collaborators = stubs();
    await expect(mountInspectorWith(
      collaborators.mountFn, collaborators.mountNavigatorFn, '#does-not-exist', 'viewer.json',
    )).rejects.toThrow('solid-widget: no element matches "#does-not-exist"');
  });
});
