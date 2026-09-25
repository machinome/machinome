/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The pure decisions (design D2, D4-D6) and the DOM controller built over
// them (design D1, D3, D9). jsdom gives no real Fullscreen API, so every
// controller test stubs `Element.requestFullscreen` and
// `Document.exitFullscreen` and fires `fullscreenchange` itself -- exactly
// the seam `tests/test_widget_e2e.py` then proves against a real browser.

import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';
import {
  createFullscreenController, fullscreenAvailable, fullscreenBackground,
  fullscreenPlacement, fullscreenRootFor, registerFullscreenRoot,
  togglesFullscreen,
} from './fullscreen';

describe('fullscreenPlacement', () => {
  it('chooses the run transport first', () => {
    expect(fullscreenPlacement({ runTransport: true, inlineAnimationBar: true }))
      .toBe('run-transport');
  });

  it('falls back to the inline animation bar', () => {
    expect(fullscreenPlacement({ runTransport: false, inlineAnimationBar: true }))
      .toBe('animation-bar');
  });

  it('falls back to the corner when neither is drawn', () => {
    expect(fullscreenPlacement({ runTransport: false, inlineAnimationBar: false }))
      .toBe('corner');
  });
});

describe('fullscreenAvailable', () => {
  it('is true only in continuous mode on a document that permits it', () => {
    expect(fullscreenAvailable({ fullscreenEnabled: true }, 'continuous')).toBe(true);
  });

  it('is false in on-demand mode even where the document permits it', () => {
    expect(fullscreenAvailable({ fullscreenEnabled: true }, 'on-demand')).toBe(false);
  });

  it('is false where the document does not permit it, such as an iframe without allowfullscreen', () => {
    expect(fullscreenAvailable({ fullscreenEnabled: false }, 'continuous')).toBe(false);
  });

  it('is false where fullscreenEnabled is undefined', () => {
    expect(fullscreenAvailable({}, 'continuous')).toBe(false);
  });
});

describe('fullscreenBackground', () => {
  it('picks the first opaque colour', () => {
    expect(fullscreenBackground(['transparent', 'rgba(0, 0, 0, 0)', 'rgb(10, 20, 30)', 'white']))
      .toBe('rgb(10, 20, 30)');
  });

  it('defaults to white when every colour is transparent or absent', () => {
    expect(fullscreenBackground(['transparent', '', null, undefined, 'rgba(0, 0, 0, 0)']))
      .toBe('white');
  });

  it('defaults to white given no colours at all', () => {
    expect(fullscreenBackground([])).toBe('white');
  });
});

function key(overrides: Partial<{
  key: string; ctrlKey: boolean; altKey: boolean; metaKey: boolean;
  repeat: boolean; defaultPrevented: boolean; target: unknown;
}> = {}) {
  return {
    key: 'f', ctrlKey: false, altKey: false, metaKey: false,
    repeat: false, defaultPrevented: false, target: null,
    ...overrides,
  };
}

const insideRoot = { insideRoot: true, bodyTarget: false, soleViewer: false };
const bodyAlone = { insideRoot: false, bodyTarget: true, soleViewer: true };
const bodyNotSole = { insideRoot: false, bodyTarget: true, soleViewer: false };
const neither = { insideRoot: false, bodyTarget: false, soleViewer: false };

describe('togglesFullscreen', () => {
  it('toggles on lower or upper case f inside the root', () => {
    expect(togglesFullscreen(key({ key: 'f' }), insideRoot)).toBe(true);
    expect(togglesFullscreen(key({ key: 'F' }), insideRoot)).toBe(true);
  });

  it('does not toggle on any other key', () => {
    expect(togglesFullscreen(key({ key: 'g' }), insideRoot)).toBe(false);
  });

  it('does not toggle with Ctrl, Alt or Meta held', () => {
    expect(togglesFullscreen(key({ ctrlKey: true }), insideRoot)).toBe(false);
    expect(togglesFullscreen(key({ altKey: true }), insideRoot)).toBe(false);
    expect(togglesFullscreen(key({ metaKey: true }), insideRoot)).toBe(false);
  });

  it('does not toggle on key repeat', () => {
    expect(togglesFullscreen(key({ repeat: true }), insideRoot)).toBe(false);
  });

  it('does not toggle once another handler consumed the key', () => {
    expect(togglesFullscreen(key({ defaultPrevented: true }), insideRoot)).toBe(false);
  });

  it('does not toggle while typing into an input, textarea, select or contenteditable element', () => {
    expect(togglesFullscreen(key({ target: { tagName: 'INPUT' } }), insideRoot)).toBe(false);
    expect(togglesFullscreen(key({ target: { tagName: 'TEXTAREA' } }), insideRoot)).toBe(false);
    expect(togglesFullscreen(key({ target: { tagName: 'SELECT' } }), insideRoot)).toBe(false);
    expect(togglesFullscreen(
      key({ target: { tagName: 'DIV', isContentEditable: true } }), insideRoot,
    )).toBe(false);
  });

  it('toggles when the target is inside the root', () => {
    expect(togglesFullscreen(key(), insideRoot)).toBe(true);
  });

  it('toggles on a body/html target only when this is the sole viewer', () => {
    expect(togglesFullscreen(key(), bodyAlone)).toBe(true);
    expect(togglesFullscreen(key(), bodyNotSole)).toBe(false);
  });

  it('does not toggle when the target is neither inside the root nor body/html', () => {
    expect(togglesFullscreen(key(), neither)).toBe(false);
  });
});

describe('the root registry', () => {
  it('resolves an unregistered container to itself', () => {
    const container = document.createElement('div');
    expect(fullscreenRootFor(container)).toBe(container);
  });

  it('resolves a registered container to its registered root', () => {
    const container = document.createElement('div');
    const root = document.createElement('div');
    registerFullscreenRoot(container, root);
    expect(fullscreenRootFor(container)).toBe(root);
  });
});

// The controller. jsdom has no real Fullscreen API: `fullscreenEnabled`
// is not `true` by default, `Element.requestFullscreen` and
// `Document.exitFullscreen` do not exist, and nothing sets
// `document.fullscreenElement` on its own -- so every test below that
// wants "available" stubs all three, and drives entry/exit itself by
// writing `fullscreenElement` and dispatching `fullscreenchange`, exactly
// as a real browser's own effect on the document would.

let container: HTMLElement;

beforeEach(() => {
  container = document.createElement('div');
  document.body.append(container);
});

afterEach(() => {
  document.body.replaceChildren();
  Object.defineProperty(document, 'fullscreenEnabled', {
    value: false, configurable: true,
  });
  Object.defineProperty(document, 'fullscreenElement', {
    value: null, configurable: true,
  });
  vi.restoreAllMocks();
});

function stubFullscreenApi(): { enter: () => void; exit: () => void } {
  Object.defineProperty(document, 'fullscreenEnabled', {
    value: true, configurable: true,
  });
  let current: HTMLElement | null = null;
  Object.defineProperty(document, 'fullscreenElement', {
    get: () => current, configurable: true,
  });
  HTMLElement.prototype.requestFullscreen = vi.fn(function requestFullscreen(
    this: HTMLElement,
  ) {
    current = this;
    document.dispatchEvent(new Event('fullscreenchange'));
    return Promise.resolve();
  });
  document.exitFullscreen = vi.fn(() => {
    current = null;
    document.dispatchEvent(new Event('fullscreenchange'));
    return Promise.resolve();
  });
  return {
    enter: () => { current = container; document.dispatchEvent(new Event('fullscreenchange')); },
    exit: () => { current = null; document.dispatchEvent(new Event('fullscreenchange')); },
  };
}

describe('createFullscreenController, unavailable', () => {
  it('creates no button and installs no key listener', () => {
    const controller = createFullscreenController(container, container, 'continuous');
    controller.place({});
    expect(container.querySelector('.machinome-fullscreen')).toBeNull();

    const event = new KeyboardEvent('keydown', { key: 'f', bubbles: true });
    const prevented = vi.spyOn(event, 'preventDefault');
    document.dispatchEvent(event);
    expect(prevented).not.toHaveBeenCalled();
    expect(() => controller.dispose()).not.toThrow();
  });

  it('is unavailable in on-demand render mode even where the document permits full screen', () => {
    stubFullscreenApi();
    const controller = createFullscreenController(container, container, 'on-demand');
    controller.place({});
    expect(container.querySelector('.machinome-fullscreen')).toBeNull();
    controller.dispose();
  });
});

describe('createFullscreenController, available', () => {
  it('places a button carrying the stable class', () => {
    stubFullscreenApi();
    const controller = createFullscreenController(container, container, 'continuous');
    controller.place({});
    const button = container.querySelector('.machinome-fullscreen');
    expect(button).not.toBeNull();
    expect(button?.tagName).toBe('BUTTON');
    controller.dispose();
  });

  it('places the button on the run transport, else the animation bar, else the corner', () => {
    stubFullscreenApi();
    const controller = createFullscreenController(container, container, 'continuous');
    const runTransport = document.createElement('div');
    const animationBar = document.createElement('div');
    container.append(runTransport, animationBar);

    controller.place({ runTransport, animationBar });
    expect(runTransport.querySelector('.machinome-fullscreen')).not.toBeNull();

    controller.place({ animationBar });
    expect(animationBar.querySelector('.machinome-fullscreen')).not.toBeNull();

    controller.place({});
    expect(container.querySelector(':scope > .machinome-fullscreen')).not.toBeNull();
    controller.dispose();
  });

  it('swaps the accessible name and title on fullscreenchange', () => {
    const api = stubFullscreenApi();
    const controller = createFullscreenController(container, container, 'continuous');
    controller.place({});
    const button = container.querySelector<HTMLButtonElement>('.machinome-fullscreen')!;
    expect(button.getAttribute('aria-label')).toBe('Full screen');
    expect(button.title).toBe('Full screen (f)');

    api.enter();
    expect(button.getAttribute('aria-label')).toBe('Exit full screen');
    expect(button.title).toBe('Exit full screen (f)');

    api.exit();
    expect(button.getAttribute('aria-label')).toBe('Full screen');
    expect(button.title).toBe('Full screen (f)');
    controller.dispose();
  });

  it('requests full screen on the root when f is pressed with nothing focused, and exits on f again', () => {
    stubFullscreenApi();
    const controller = createFullscreenController(container, container, 'continuous');
    controller.place({});

    const enterEvent = new KeyboardEvent('keydown', { key: 'f', bubbles: true });
    document.body.dispatchEvent(enterEvent);
    expect(document.fullscreenElement).toBe(container);

    const exitEvent = new KeyboardEvent('keydown', { key: 'f', bubbles: true });
    document.body.dispatchEvent(exitEvent);
    expect(document.fullscreenElement).toBeNull();
    controller.dispose();
  });

  it('never prevents Escape', () => {
    stubFullscreenApi();
    const controller = createFullscreenController(container, container, 'continuous');
    controller.place({});
    const escape = new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true });
    document.body.dispatchEvent(escape);
    expect(escape.defaultPrevented).toBe(false);
    controller.dispose();
  });

  it('does nothing on f pressed with nothing focused when two controllers share the document', () => {
    stubFullscreenApi();
    const other = document.createElement('div');
    document.body.append(other);
    const a = createFullscreenController(container, container, 'continuous');
    const b = createFullscreenController(other, other, 'continuous');
    a.place({});
    b.place({});

    document.body.dispatchEvent(new KeyboardEvent('keydown', { key: 'f', bubbles: true }));
    expect(document.fullscreenElement).toBeNull();

    a.dispose();
    b.dispose();
  });

  it('exits full screen on dispose when this root holds it', () => {
    stubFullscreenApi();
    const controller = createFullscreenController(container, container, 'continuous');
    controller.place({});
    container.requestFullscreen();
    expect(document.fullscreenElement).toBe(container);

    controller.dispose();
    expect(document.exitFullscreen).toHaveBeenCalled();
  });
});
