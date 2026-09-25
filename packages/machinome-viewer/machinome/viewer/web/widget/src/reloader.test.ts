/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// Ported from `app/src/reloader.test.ts` (design D12): every case held
// identical in intent, jest -> vitest (`jest.useFakeTimers` ->
// `vi.useFakeTimers`, `jest.fn` -> `vi.fn`). One case is new -- the
// injected stylesheet, which the React shell's `App.css` carried instead.

import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';

// Stand-in for the browser WebSocket: exposes the on* handlers Reloader
// assigns so tests can fire them directly, without a live server.
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

const latestSocket = () => FakeWebSocket.instances[FakeWebSocket.instances.length - 1];

import { Reloader } from './reloader';

const BANNER_SELECTOR = '.reload-offline-banner';

beforeEach(() => {
  vi.useFakeTimers();
  FakeWebSocket.instances = [];
  (globalThis as unknown as { WebSocket: unknown }).WebSocket = FakeWebSocket;
  document.body.innerHTML = '';
  document.getElementById('machinome-reloader-style')?.remove();
  globalThis.fetch = vi.fn(() => Promise.resolve({
    json: () => Promise.resolve({}),
  })) as unknown as typeof fetch;
});

afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe('Reloader offline banner', () => {
  it('does not show a banner while the initial connection is still pending', () => {
    new Reloader(() => {}, () => {});

    expect(document.querySelector(BANNER_SELECTOR)).toBeNull();
  });

  it('does not flash a banner when the initial connection succeeds immediately', () => {
    new Reloader(() => {}, () => {});

    latestSocket().onopen?.();

    expect(document.querySelector(BANNER_SELECTOR)).toBeNull();
  });

  it('does not show the banner on the very first failed connection attempt (grace period)', () => {
    new Reloader(() => {}, () => {});

    latestSocket().onclose?.();

    expect(document.querySelector(BANNER_SELECTOR)).toBeNull();
  });

  it('shows the banner after a couple of failed initial-connect retries', () => {
    new Reloader(() => {}, () => {});

    // First failed attempt: still within grace, no banner yet.
    latestSocket().onclose?.();
    expect(document.querySelector(BANNER_SELECTOR)).toBeNull();

    // Retry fires ~2s later.
    vi.advanceTimersByTime(2000);
    expect(FakeWebSocket.instances).toHaveLength(2);

    // Second consecutive failure: grace exhausted, banner must appear.
    latestSocket().onclose?.();
    const banner = document.querySelector(BANNER_SELECTOR);
    expect(banner).not.toBeNull();
    expect(banner?.id).toBe('machinome-offline-banner');
    expect(banner?.textContent).toBe('machinome develop is not running — model may be stale');
  });

  it('shows the banner immediately once a previously-live connection drops', () => {
    new Reloader(() => {}, () => {});

    latestSocket().onopen?.();
    expect(document.querySelector(BANNER_SELECTOR)).toBeNull();

    latestSocket().onclose?.();

    const banner = document.querySelector(BANNER_SELECTOR);
    expect(banner).not.toBeNull();
    expect(banner?.id).toBe('machinome-offline-banner');
    expect(banner?.textContent).toBe('machinome develop is not running — model may be stale');
  });

  it('retries the dropped connection roughly every 2 seconds, indefinitely', () => {
    new Reloader(() => {}, () => {});

    latestSocket().onopen?.();
    latestSocket().onclose?.();
    expect(FakeWebSocket.instances).toHaveLength(1);

    vi.advanceTimersByTime(1999);
    expect(FakeWebSocket.instances).toHaveLength(1);

    vi.advanceTimersByTime(1);
    expect(FakeWebSocket.instances).toHaveLength(2);

    latestSocket().onclose?.();
    vi.advanceTimersByTime(2000);
    expect(FakeWebSocket.instances).toHaveLength(3);
  });

  it('on reconnect after a drop, triggers the full reload path and then clears the banner', async () => {
    const reload = vi.fn(() => Promise.resolve());
    new Reloader(() => {}, reload);

    latestSocket().onopen?.();
    latestSocket().onclose?.();
    expect(document.querySelector(BANNER_SELECTOR)).not.toBeNull();

    vi.advanceTimersByTime(2000);
    // Reconnect succeeds: same full-reload path a file-change "reload"
    // message would trigger (fetch /_build_error, then reload()).
    latestSocket().onopen?.();

    // Flush the microtask queue the async reconnect handler schedules.
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();

    expect(globalThis.fetch).toHaveBeenCalledWith('/_build_error');
    expect(reload).toHaveBeenCalled();
    expect(document.querySelector(BANNER_SELECTOR)).toBeNull();
  });

  it('does not re-trigger the reload path on a first-ever successful connect', () => {
    const reload = vi.fn(() => Promise.resolve());
    new Reloader(() => {}, reload);

    latestSocket().onopen?.();

    expect(reload).not.toHaveBeenCalled();
  });
});

describe('the injected stylesheet', () => {
  it('injects exactly one identifiable stylesheet, once, however many Reloaders are made', () => {
    new Reloader(() => {}, () => {});
    new Reloader(() => {}, () => {});

    expect(document.querySelectorAll('#machinome-reloader-style').length).toBe(1);
  });
});
