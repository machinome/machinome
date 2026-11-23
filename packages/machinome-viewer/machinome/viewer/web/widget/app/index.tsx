/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// `@machinome/viewer/app`: the helper a model's own app imports (OpenSpec
// `show-a-models-own-app`, design Decision 7). Four names:
//
//   <Viewport/>    places the model's picture where the app renders it;
//   useMachine()   the clocked machine's committed bank, whether a
//                  transition is being drawn and the layers the document
//                  declares, re-rendering after every change, whoever
//                  made it;
//   usePlay()      plays a declared instruction, as the panel's button does;
//   useViewer()    the mount's handle, whole.
//
// The viewer's own bundle carries none of this: React is the convention of
// the helper, bundled into each app by `app-build.mjs`.

import {
  useCallback, useContext, useLayoutEffect, useRef, useSyncExternalStore,
} from 'react';
import type { CSSProperties, JSX } from 'react';
import type { ClockedRequest, Layer, ViewerHandle } from '../src/viewer';
import { AppRefusal, HostContext } from './host';
import type { AppHost } from './host';

function useHost(): AppHost {
  const host = useContext(HostContext);
  if (host === null) {
    throw new Error('@machinome/viewer/app is used outside a model\'s app '
                    + 'the viewer started');
  }
  return host;
}

/** The mount's handle, whole: every member a host page has. */
export function useViewer(): ViewerHandle {
  return useHost().viewer;
}

/** What `useMachine()` answers: the committed bank, frozen, and whether a
 * drawn transition is running. While one runs, the bank already stands at
 * its end. */
export interface MachineReading {
  bank: Readonly<Record<string, number>>;
  drawing: boolean;
  /** The layers the document declares, as the handle's `layers()` answers
   * them: the same array until a republish changes the list. */
  layers: readonly Layer[];
}

export type { Layer };

const NOT_CLOCKED = 'this model is not a clocked machine; ';

/** One store per host: one subscription to the handle's
 * `onMachineChange`, and one cached reading, replaced exactly when a
 * notification arrives, so its identity changes exactly then. */
class MachineStore {
  private reading: MachineReading | null = null;
  private readonly callbacks = new Set<() => void>();
  private cancel: (() => void) | null = null;

  constructor(private readonly viewer: ViewerHandle) {}

  private read(): MachineReading {
    const machine = this.viewer.machine();
    // A republish that took the machine away: the hook refuses on its
    // next render; the store keeps answering.
    if (machine === null) {
      return Object.freeze({ bank: Object.freeze({}), drawing: false,
                             layers: this.viewer.layers() });
    }
    return Object.freeze({
      bank: Object.freeze({ ...machine.state() }),
      drawing: machine.drawing(),
      layers: this.viewer.layers(),
    });
  }

  getSnapshot = (): MachineReading => {
    if (this.reading === null) this.reading = this.read();
    return this.reading;
  };

  subscribe = (callback: () => void): (() => void) => {
    this.callbacks.add(callback);
    if (this.cancel === null) {
      this.cancel = this.viewer.onMachineChange(() => {
        this.reading = this.read();
        for (const one of [...this.callbacks]) one();
      });
      // A change made between the first render and this subscription
      // reached nobody: read again, and say so if it differs.
      const now = this.read();
      if (this.reading === null || !sameReading(this.reading, now)) {
        this.reading = now;
        callback();
      }
    }
    return () => {
      this.callbacks.delete(callback);
      if (this.callbacks.size === 0 && this.cancel !== null) {
        this.cancel();
        this.cancel = null;
      }
    };
  };
}

function sameReading(a: MachineReading, b: MachineReading): boolean {
  if (a.drawing !== b.drawing || a.layers !== b.layers) return false;
  const keys = Object.keys(a.bank);
  if (keys.length !== Object.keys(b.bank).length) return false;
  return keys.every((key) => Object.is(a.bank[key], b.bank[key]));
}

const stores = new WeakMap<AppHost, MachineStore>();

function storeOf(host: AppHost): MachineStore {
  let store = stores.get(host);
  if (store === undefined) {
    store = new MachineStore(host.viewer);
    stores.set(host, store);
  }
  return store;
}

/** The clocked machine's committed bank and whether a transition is being
 * drawn. The component re-renders after every change of either, whoever
 * made it -- the app, the panel of another page, a host script, the clock
 * -- and the reading it gets is the same object until one arrives. Refuses
 * the app on a model that is not a clocked machine. */
export function useMachine(): MachineReading {
  const host = useHost();
  if (host.viewer.machine() === null) {
    throw new AppRefusal(`${NOT_CLOCKED}useMachine() reads a clocked `
                         + 'machine\'s bank');
  }
  const store = storeOf(host);
  return useSyncExternalStore(store.subscribe, store.getSnapshot);
}

/** A function that plays a declared instruction, as the panel's button
 * does: one request, its transition drawn over the declared duration. It
 * answers the request; a refusal is thrown as the machine's own error, for
 * the app to say where it wants. Refuses the app on a model that is not a
 * clocked machine. */
export function usePlay(): (name: string) => ClockedRequest {
  const viewer = useViewer();
  if (viewer.machine() === null) {
    throw new AppRefusal(`${NOT_CLOCKED}usePlay() plays a clocked `
                         + 'machine\'s instructions');
  }
  return useCallback((name: string): ClockedRequest => {
    const machine = viewer.machine();
    if (machine === null) {
      throw new AppRefusal(`${NOT_CLOCKED}usePlay() plays a clocked `
                           + 'machine\'s instructions');
    }
    return machine.trigger(name);
  }, [viewer]);
}

export interface ViewportProps {
  className?: string;
  style?: CSSProperties;
}

/** The model's picture, where the app renders this: a `div` the app sizes,
 * into which the picture is moved; the picture follows its size. One per
 * app: a second takes the picture from the first. */
export function Viewport({ className, style }: ViewportProps): JSX.Element {
  const host = useHost();
  const place = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    if (place.current !== null) place.current.append(host.viewport);
  }, [host]);
  return <div ref={place} className={className} style={style} />;
}
