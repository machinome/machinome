/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// A model's own app, loaded, started, refused and disposed (OpenSpec
// `show-a-models-own-app`, design Decisions 2, 8, 9 and 10). No React and
// no other user-interface framework is imported here or anywhere in the
// viewer's bundle: the contract between the viewer and an app is a classic
// script, an event and a function.
//
// 1. The stylesheet, when the record names one, is attached to the
//    document's head and awaited.
// 2. The script is attached with its `src`; as it runs it dispatches
//    `machinome:app` on ITS OWN element (`document.currentScript`),
//    carrying `{ contract: 1, start }`, which is taken from the event
//    synchronously. No global name is claimed, so two viewers on one page
//    may show two apps.
// 3. On the script's `load`, `start(host)` is called with the element the
//    app fills, the picture's element, the mount's handle and a way to
//    refuse; it returns the disposer kept here. The script element is then
//    removed; the stylesheet stays until the app is disposed.
//
// Whatever goes wrong is REFUSED by name in the app's place: the picture
// fills the viewer's area, a notice over it says why, and the same
// sentence goes to the console. Nothing is substituted for the app.
//
// The element attachment is the seam (`mountAppWith`, as `inspector.ts`'s
// `mountInspectorWith`): jsdom loads no script, so `app.test.ts` attaches
// through a fake that plays what a browser would.

import type { ManifestApp } from './types';
import type { ViewerHandle } from './viewer';

/** The event an app's script dispatches on its own element. */
export const APP_EVENT = 'machinome:app';

/** The one contract this viewer knows. */
export const APP_CONTRACT = 1;

/** What `start` is given (design Decision 2). */
export interface AppHost {
  contract: 1;
  /** A fresh element filling the viewer's area: the app renders into it. */
  element: HTMLElement;
  /** The picture: the canvas and its corner control. The app places it. */
  viewport: HTMLElement;
  /** The mount's handle, whole. */
  viewer: ViewerHandle;
  /** The app's way to say it cannot go on; the first sentence wins. */
  refuse(reason: string): void;
}

/** How an element is put into the document: in a page, appended, which
 * starts its load. */
export type Attach = (element: HTMLElement, parent: HTMLElement) => void;

export interface AppRequest {
  record: ManifestApp;
  /** The base every model path resolves against. */
  baseUrl: string;
  /** The area the host gave the viewer. */
  container: HTMLElement;
  /** The picture's element, which fills `container` when no app holds it. */
  viewport: HTMLElement;
  viewer: ViewerHandle;
  /** Called whenever the picture moved, so the viewer draws it again. */
  moved?: () => void;
}

/** One app in one mount. */
export interface ShownApp {
  readonly record: ManifestApp;
  /** Settles once the app is shown, refused, or abandoned by `dispose`. */
  readonly ready: Promise<void>;
  /** The reason the app is not shown, or null. */
  refusal(): string | null;
  /** Take the app away: its disposer, its stylesheet, its element; the
   * picture is put back filling the viewer's area. A pending load is
   * abandoned and its start never called. Idempotent. */
  dispose(): void;
}

/** The sentence a reader sees, and the console reads. */
export const REFUSAL_PREFIX = "This model's app is not shown: ";

const APP_STYLE = 'position:absolute;left:0;top:0;width:100%;height:100%;'
  + 'overflow:hidden;';

const NOTICE_STYLE = 'position:absolute;left:8px;top:8px;z-index:3;'
  + 'max-width:calc(100% - 16px);box-sizing:border-box;padding:6px 10px;'
  + 'border-radius:4px;background:rgba(150,36,28,0.92);color:#fff;'
  + 'font:13px system-ui,sans-serif;white-space:pre-wrap;';

/** Whether two records name the same app: the same files, or the same
 * refusal. Files are named by their content, so the same names are the
 * same bytes (design Decision 9). */
export function sameApp(a: ManifestApp, b: ManifestApp): boolean {
  if ('refusal' in a || 'refusal' in b) {
    return 'refusal' in a && 'refusal' in b && a.refusal === b.refusal;
  }
  return a.script === b.script
    && (a.stylesheet ?? null) === (b.stylesheet ?? null);
}

function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

/** Why a file did not load, asked once more of the server: its status,
 * or the error the fetch met (a `file:` page has no status to give). */
async function failureOf(url: string): Promise<string> {
  try {
    const response = await fetch(url, { cache: 'no-store' });
    return response.ok
      ? 'the browser would not use it' : `HTTP ${response.status}`;
  } catch (error) {
    return messageOf(error);
  }
}

export function mountApp(request: AppRequest): ShownApp {
  return mountAppWith((element, parent) => { parent.append(element); }, request);
}

export function mountAppWith(attach: Attach, request: AppRequest): ShownApp {
  const { record, baseUrl, container, viewport, viewer } = request;
  const doc = container.ownerDocument;
  type State = 'loading' | 'starting' | 'running' | 'refused' | 'disposed';
  let state: State = 'loading';
  let reason: string | null = null;
  let element: HTMLElement | null = null;
  let link: HTMLLinkElement | null = null;
  let script: HTMLScriptElement | null = null;
  let notice: HTMLElement | null = null;
  let disposer: (() => void) | null = null;
  // Settled by `dispose`, so a load that never ends cannot hold a
  // republish, or the mount, forever.
  let abandon: () => void = () => undefined;
  const abandoned = new Promise<void>((resolve) => { abandon = resolve; });
  // Settled once a refusal has been shown.
  let shown: Promise<void> = Promise.resolve();

  /** The picture fills the viewer's area again, as its first child. */
  const placeBack = (): void => {
    if (viewport.parentElement !== container) container.prepend(viewport);
    request.moved?.();
  };

  const runDisposer = (): void => {
    const running = disposer;
    disposer = null;
    if (running === null) return;
    try {
      running();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('the model\'s app failed as it was taken away', error);
    }
  };

  /** Everything the app put in the page goes; the picture fills the area. */
  const takeAway = (): void => {
    runDisposer();
    element?.remove();
    element = null;
    script?.remove();
    script = null;
    link?.remove();
    link = null;
    placeBack();
  };

  const showNotice = (sentence: string): void => {
    notice = doc.createElement('div');
    notice.className = 'machinome-app-refusal';
    notice.setAttribute('role', 'alert');
    notice.style.cssText = NOTICE_STYLE;
    notice.textContent = sentence;
    container.append(notice);
    // eslint-disable-next-line no-console
    console.error(sentence);
  };

  /** Refuse the app (design Decision 8). Once an app has been started its
   * disposal is deferred to a microtask, since React cannot unmount from
   * inside its own render; the notice is shown after it. */
  const refuse = (sentence: string): void => {
    if (state === 'refused' || state === 'disposed') return;
    const started = state === 'starting' || state === 'running';
    state = 'refused';
    reason = sentence;
    const finish = (): void => {
      if (state === 'disposed') return;
      takeAway();
      showNotice(REFUSAL_PREFIX + sentence);
    };
    if (!started) {
      finish();
      return;
    }
    shown = new Promise<void>((resolve) => {
      queueMicrotask(() => { finish(); resolve(); });
    });
  };

  /** Attach `node` and wait for its load or its error, or for `dispose`. */
  const loaded = (node: HTMLElement): Promise<'load' | 'error' | 'abandoned'> =>
    Promise.race([
      new Promise<'load' | 'error'>((resolve) => {
        node.addEventListener('load', () => resolve('load'), { once: true });
        node.addEventListener('error', () => resolve('error'), { once: true });
        attach(node, doc.head);
      }),
      abandoned.then(() => 'abandoned' as const),
    ]);

  const run = async (): Promise<void> => {
    if ('refusal' in record) {
      refuse(record.refusal);
      return;
    }
    if (record.stylesheet !== undefined) {
      const url = baseUrl + record.stylesheet;
      link = doc.createElement('link');
      link.rel = 'stylesheet';
      link.setAttribute('href', url);
      const outcome = await loaded(link);
      if (state === 'disposed') return;
      if (outcome !== 'load') {
        refuse(`${record.stylesheet} could not be loaded (${await failureOf(url)})`);
        return;
      }
    }
    const url = baseUrl + record.script;
    const node = doc.createElement('script');
    script = node;
    node.setAttribute('src', url);
    let heard = false;
    let detail: unknown;
    // Taken from the event synchronously, on the element that sent it.
    node.addEventListener(APP_EVENT, (event) => {
      if (heard) return;
      heard = true;
      detail = (event as CustomEvent).detail;
    });
    const outcome = await loaded(node);
    node.remove();
    if (script === node) script = null;
    if (state === 'disposed') return;
    if (outcome !== 'load') {
      refuse(`${record.script} could not be loaded (${await failureOf(url)})`);
      return;
    }
    const sent = detail as { contract?: unknown; start?: unknown } | null | undefined;
    const cannot = (what: string): void => {
      refuse(`${record.script} is not an app this viewer can start (${what})`);
    };
    if (!heard) {
      cannot(`it sent no ${APP_EVENT} event`);
      return;
    }
    if (sent === null || typeof sent !== 'object') {
      cannot(`it sent ${JSON.stringify(sent)}`);
      return;
    }
    if (sent.contract !== APP_CONTRACT) {
      cannot(`it sent contract ${JSON.stringify(sent.contract)}`);
      return;
    }
    if (typeof sent.start !== 'function') {
      cannot('it sent no start function');
      return;
    }
    const root = doc.createElement('div');
    root.className = 'machinome-app';
    root.style.cssText = APP_STYLE;
    container.append(root);
    element = root;
    state = 'starting';
    const host: AppHost = {
      contract: APP_CONTRACT,
      element: root,
      viewport,
      viewer,
      refuse: (sentence: string) => refuse(String(sentence)),
    };
    let returned: unknown;
    try {
      returned = (sent.start as (host: AppHost) => unknown)(host);
    } catch (error) {
      refuse(`it failed as it started: ${messageOf(error)}`);
      await shown;
      return;
    }
    // Kept even when the app refused while it started: the refusal's
    // deferred disposal is the one that calls it.
    disposer = typeof returned === 'function' ? returned as () => void : null;
    if (state === 'starting') {
      state = 'running';
      request.moved?.();
      return;
    }
    await shown;
  };

  const ready = run().catch((error: unknown) => {
    refuse(`it could not be loaded: ${messageOf(error)}`);
    return shown;
  });

  return {
    record,
    ready,
    refusal: () => reason,
    dispose(): void {
      if (state === 'disposed') return;
      state = 'disposed';
      abandon();
      takeAway();
      notice?.remove();
      notice = null;
    },
  };
}
