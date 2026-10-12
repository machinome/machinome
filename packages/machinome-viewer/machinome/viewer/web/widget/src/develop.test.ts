/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// `mountDevelopment` against a STUBBED `mountInspector` (design D15's
// seam, applied here too: nothing in this file touches three.js) and a
// stubbed `fetch`/`WebSocket`, exactly what `develop.html` calls after
// its own availability check and script injection (design D10).

import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';
import { mountDevelopmentWith } from './develop';
import type { InspectorHandle } from './inspector';
import type { mountInspector } from './inspector';
import type { ViewerHandle } from './viewer';

class FakeWebSocket {
  static instances: FakeWebSocket[] = [];

  url: string;

  onopen: (() => void) | null = null;

  onclose: (() => void) | null = null;

  onmessage: ((event: { data: string }) => void) | null = null;

  onerror: (() => void) | null = null;

  constructor(url: string) {
    this.url = url;
    FakeWebSocket.instances.push(this);
  }
}

function latestSocket(): FakeWebSocket {
  return FakeWebSocket.instances[FakeWebSocket.instances.length - 1];
}

function stubInspector() {
  const manifestChanged = vi.fn(() => Promise.resolve());
  const disposeViewer = vi.fn();
  const viewerHandle = {
    manifestChanged, dispose: disposeViewer,
  } as unknown as ViewerHandle;
  const disposeInspector = vi.fn();
  const handle: InspectorHandle = {
    viewer: viewerHandle,
    navigator: { dispose: vi.fn() } as never,
    sidebarOpen: () => true,
    setSidebar: vi.fn(),
    dispose: disposeInspector,
  };
  const mountInspectorFn = vi.fn(
    async () => handle,
  ) as unknown as typeof mountInspector;
  return {
    handle, mountInspectorFn, manifestChanged, disposeInspector,
  };
}

function stubFetch(
  name: string | null = 'SpinnerProject',
  buildError: { error: string; tstamp: number } = { error: '', tstamp: 0 },
) {
  return vi.fn((url: string) => {
    if (url === '/_build_error') {
      return Promise.resolve({ json: () => Promise.resolve(buildError) });
    }
    return Promise.resolve({ json: () => Promise.resolve({ root: { name } }) });
  });
}

let container: HTMLElement;

beforeEach(() => {
  container = document.createElement('div');
  document.body.append(container);
  document.title = '';
  FakeWebSocket.instances = [];
  (globalThis as unknown as { WebSocket: unknown }).WebSocket = FakeWebSocket;
});

afterEach(() => {
  document.body.replaceChildren();
  document.getElementById('machinome-develop-style')?.remove();
  document.getElementById('machinome-reloader-style')?.remove();
  vi.restoreAllMocks();
});

describe('mounting', () => {
  it('mounts the inspector on /build/viewer.json, inline animation, autoplay, sidebar open', async () => {
    const { mountInspectorFn } = stubInspector();
    globalThis.fetch = stubFetch() as unknown as typeof fetch;

    await mountDevelopmentWith(mountInspectorFn, container);

    expect(mountInspectorFn).toHaveBeenCalledWith(container, '/build/viewer.json', {
      animation: 'inline', autoplay: true, sidebar: 'open',
    });
  });

  it('an explicit sidebar option wins over the open default', async () => {
    const { mountInspectorFn } = stubInspector();
    globalThis.fetch = stubFetch() as unknown as typeof fetch;

    await mountDevelopmentWith(mountInspectorFn, container, { sidebar: 'collapsed' });

    expect(mountInspectorFn).toHaveBeenCalledWith(container, '/build/viewer.json', {
      animation: 'inline', autoplay: true, sidebar: 'collapsed',
    });
  });

  it('a sourceUrl option overrides the default document, and is not forwarded to mountInspector', async () => {
    const { mountInspectorFn } = stubInspector();
    globalThis.fetch = stubFetch() as unknown as typeof fetch;

    await mountDevelopmentWith(mountInspectorFn, container, { sourceUrl: '/build/other.json' });

    expect(mountInspectorFn).toHaveBeenCalledWith(container, '/build/other.json', {
      animation: 'inline', autoplay: true, sidebar: 'open',
    });
  });

  it("titles the document from the model's root name, split on capitals", async () => {
    const { mountInspectorFn } = stubInspector();
    globalThis.fetch = stubFetch('SpinnerProject') as unknown as typeof fetch;

    await mountDevelopmentWith(mountInspectorFn, container);

    expect(document.title).toBe('Spinner Project');
  });

  it('exposes the mounted inspector handle', async () => {
    const { mountInspectorFn, handle } = stubInspector();
    globalThis.fetch = stubFetch() as unknown as typeof fetch;

    const development = await mountDevelopmentWith(mountInspectorFn, container);

    expect(development.inspector).toBe(handle);
  });
});

describe('the reloader', () => {
  it("a reload calls the inspector's viewer.manifestChanged(), never reload()", async () => {
    const { mountInspectorFn, manifestChanged } = stubInspector();
    globalThis.fetch = stubFetch() as unknown as typeof fetch;

    await mountDevelopmentWith(mountInspectorFn, container);
    latestSocket().onmessage?.({ data: 'reload' });
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();

    expect(manifestChanged).toHaveBeenCalledTimes(1);
  });
});

describe('a build error', () => {
  it('shows the error pane with the message, leaving the inspector mounted', async () => {
    const { mountInspectorFn, handle, disposeInspector } = stubInspector();
    let buildError = { error: 'boom: relation refused', tstamp: 1 };
    globalThis.fetch = vi.fn((url: string) => {
      if (url === '/_build_error') {
        return Promise.resolve({ json: () => Promise.resolve(buildError) });
      }
      return Promise.resolve({ json: () => Promise.resolve({ root: { name: 'X' } }) });
    }) as unknown as typeof fetch;

    await mountDevelopmentWith(mountInspectorFn, container);
    latestSocket().onmessage?.({ data: 'reload' });
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();

    const pane = document.querySelector('.machinome-inspector-error');
    expect(pane).not.toBeNull();
    expect(pane?.textContent).toBe('boom: relation refused');
    expect(disposeInspector).not.toHaveBeenCalled();
    expect(handle.viewer.manifestChanged).not.toHaveBeenCalled();

    buildError = { error: '', tstamp: 1 };
    latestSocket().onmessage?.({ data: 'reload' });
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();

    expect(document.querySelector('.machinome-inspector-error')).toBeNull();
  });
});
