/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The helper a model's app imports, `@machinome/viewer/app` (OpenSpec
// `show-a-models-own-app`, design Decision 7 and Decision 15, H1 to H6):
// real React and React DOM, rendered by the helper's own `start` into a
// FAKE host whose handle is written by hand -- `onMachineChange`,
// `machine()` and its `state()`, `drawing()` and `trigger()` -- so what is
// proved is the helper's reading of the contract, not the viewer's.

import { useState } from 'react';
import { flushSync } from 'react-dom';
import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';
import { Viewport, useMachine, usePlay, useViewer } from './index';
import { start } from './start';

interface FakeHost {
  host: {
    contract: 1;
    element: HTMLElement;
    viewport: HTMLElement;
    viewer: unknown;
    refuse: ReturnType<typeof vi.fn>;
  };
  /** Replace the bank the fake machine answers, without notifying. */
  set(bank: Record<string, number>): void;
  setDrawing(drawing: boolean): void;
  setLayers(layers: readonly unknown[]): void;
  notify(): void;
  listeners(): number;
  trigger: ReturnType<typeof vi.fn>;
  state: ReturnType<typeof vi.fn>;
  refusal: Error;
}

function fakeHost(options: { clocked?: boolean } = {}): FakeHost {
  const clocked = options.clocked ?? true;
  const listeners = new Set<() => void>();
  let bank: Record<string, number> = { 'w0.digit': 0, crank: 0 };
  let drawing = false;
  const refusal = new Error("the machine refuses the instruction 'Nope'");
  const state = vi.fn(() => ({ ...bank }));
  const trigger = vi.fn((name: string) => {
    if (name === 'Nope') throw refusal;
    bank = { ...bank, crank: bank.crank + 360 };
    return { input: 'crank', admitted: 360 };
  });
  const machine = { state, drawing: () => drawing, trigger };
  let layers: readonly unknown[] = Object.freeze([
    Object.freeze({ key: 'electrical', label: 'Electrical path' }),
  ]);
  const viewer = {
    onMachineChange(listener: () => void) {
      listeners.add(listener);
      return () => { listeners.delete(listener); };
    },
    machine: () => (clocked ? machine : null),
    layers: () => layers,
  };
  const element = document.createElement('div');
  document.body.append(element);
  const viewport = document.createElement('div');
  viewport.className = 'machinome-viewport';
  return {
    host: { contract: 1, element, viewport, viewer, refuse: vi.fn() },
    set(next) { bank = next; },
    setDrawing(next) { drawing = next; },
    setLayers(next) { layers = next; },
    notify() { for (const listener of [...listeners]) listener(); },
    listeners: () => listeners.size,
    trigger,
    state,
    refusal,
  };
}

async function settle(): Promise<void> {
  for (let i = 0; i < 40; i += 1) await Promise.resolve();
}

const disposers: Array<() => void> = [];
function show(App: () => JSX.Element | null, fake: FakeHost): () => void {
  const dispose = start(App, fake.host as never) as () => void;
  disposers.push(dispose);
  return dispose;
}

beforeEach(() => {
  document.body.replaceChildren();
});

afterEach(() => {
  disposers.splice(0).forEach((dispose) => dispose());
  document.body.replaceChildren();
  vi.restoreAllMocks();
});

describe('H1: useMachine re-renders on a notification, and only then changes', () => {
  it('H1: a notification gives a new frozen snapshot; a render for another reason gives the same one', async () => {
    const fake = fakeHost();
    const seen: Array<{ bank: Readonly<Record<string, number>>; drawing: boolean }> = [];
    let bump = (): void => undefined;
    function App() {
      const [count, setCount] = useState(0);
      bump = () => setCount((n) => n + 1);
      const machine = useMachine();
      seen.push(machine);
      return (
        <div>
          <Viewport />
          <span className="digit">{machine.bank['w0.digit']}</span>
          <span className="count">{count}</span>
          <span className="drawing">{String(machine.drawing)}</span>
        </div>
      );
    }
    const dispose = show(App, fake);
    await settle();
    expect(fake.listeners(), 'one subscription per host').toBe(1);
    const first = seen[seen.length - 1];
    expect(first.bank).toEqual({ 'w0.digit': 0, crank: 0 });
    expect(Object.isFrozen(first)).toBe(true);
    expect(Object.isFrozen(first.bank)).toBe(true);

    flushSync(() => bump());
    expect(fake.host.element.querySelector('.count')!.textContent).toBe('1');
    expect(seen[seen.length - 1], 'no notification, the same snapshot').toBe(first);

    fake.set({ 'w0.digit': 3, crank: 0 });
    fake.setDrawing(true);
    fake.notify();
    await settle();
    const second = seen[seen.length - 1];
    expect(second).not.toBe(first);
    expect(second).toEqual({
      bank: { 'w0.digit': 3, crank: 0 }, drawing: true,
      layers: [{ key: 'electrical', label: 'Electrical path' }],
    });
    expect(fake.host.element.querySelector('.digit')!.textContent).toBe('3');
    expect(fake.host.element.querySelector('.drawing')!.textContent).toBe('true');

    // A notification with nothing changed is still a new snapshot: it
    // says what was read may be stale, and the hook reads again.
    fake.notify();
    await settle();
    expect(seen[seen.length - 1]).not.toBe(second);
    expect(seen[seen.length - 1]).toEqual(second);

    dispose();
    disposers.splice(0);
    expect(fake.listeners(), 'unmounting unsubscribes').toBe(0);
    expect(fake.host.element.children).toHaveLength(0);
  });
});

describe('H2: a change between the first render and the subscription is not lost', () => {
  it('H2: the bank read at subscription replaces the one read at render', async () => {
    const fake = fakeHost();
    let reads = 0;
    fake.state.mockImplementation(() => {
      reads += 1;
      return reads === 1 ? { 'w0.digit': 0 } : { 'w0.digit': 7 };
    });
    function App() {
      const { bank } = useMachine();
      return <div><Viewport /><span className="digit">{bank['w0.digit']}</span></div>;
    }
    show(App, fake);
    await settle();
    expect(fake.host.element.querySelector('.digit')!.textContent).toBe('7');
  });
});

describe('H3: usePlay plays an instruction and rethrows its refusal', () => {
  it('H3: play(name) calls trigger(name), answering its request; a refusal is the machine\'s own error', async () => {
    const fake = fakeHost();
    let answered: unknown = null;
    let caught: unknown = null;
    function App() {
      const play = usePlay();
      return (
        <div>
          <Viewport />
          <button className="stroke" onClick={() => { answered = play('Stroke'); }}>Stroke</button>
          <button className="nope" onClick={() => {
            try { play('Nope'); } catch (error) { caught = error; }
          }}>Nope</button>
        </div>
      );
    }
    show(App, fake);
    fake.host.element.querySelector<HTMLButtonElement>('.stroke')!.click();
    expect(fake.trigger).toHaveBeenCalledWith('Stroke');
    expect(answered).toEqual({ input: 'crank', admitted: 360 });
    fake.host.element.querySelector<HTMLButtonElement>('.nope')!.click();
    expect(caught).toBe(fake.refusal);
    expect(fake.host.refuse).not.toHaveBeenCalled();
  });
});

describe('H4: <Viewport/> places the picture, and an app with none is refused', () => {
  it('H4: the viewport is adopted by the component\'s own element', () => {
    const fake = fakeHost();
    function App() {
      return <main><Viewport className="picture" style={{ height: '70%' }} /><nav>keys</nav></main>;
    }
    show(App, fake);
    const place = fake.host.viewport.parentElement;
    expect(place).not.toBeNull();
    expect(place!.className).toBe('picture');
    expect(place!.style.height).toBe('70%');
    expect(fake.host.element.contains(fake.host.viewport)).toBe(true);
    expect(fake.host.refuse).not.toHaveBeenCalled();
  });

  it('H4: an app that places no <Viewport/> refuses', () => {
    const fake = fakeHost();
    function App() {
      return <nav>keys</nav>;
    }
    show(App, fake);
    expect(fake.host.refuse).toHaveBeenCalledTimes(1);
    expect(fake.host.refuse).toHaveBeenCalledWith(
      'it places no <Viewport/>, so the model would not be seen');
  });
});

describe('H5: an app that fails as it renders is refused with its message', () => {
  it('H5: a render error refuses once, naming it', () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    const fake = fakeHost();
    function App(): JSX.Element {
      throw new Error('no rotor in slot 3');
    }
    show(App, fake);
    expect(fake.host.refuse).toHaveBeenCalledTimes(1);
    expect(fake.host.refuse).toHaveBeenCalledWith(
      'it failed as it rendered: no rotor in slot 3');
  });
});

describe('H6: the machine hooks refuse a model that is not a clocked machine', () => {
  it('H6: useMachine on a handle with no machine refuses by name', () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    const fake = fakeHost({ clocked: false });
    function App() {
      useMachine();
      return <Viewport />;
    }
    show(App, fake);
    expect(fake.host.refuse).toHaveBeenCalledTimes(1);
    expect(fake.host.refuse).toHaveBeenCalledWith(
      "this model is not a clocked machine; useMachine() reads a clocked machine's bank");
  });

  it('H6: usePlay on a handle with no machine refuses by name', () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    const fake = fakeHost({ clocked: false });
    function App() {
      usePlay();
      return <Viewport />;
    }
    show(App, fake);
    expect(fake.host.refuse).toHaveBeenCalledTimes(1);
    expect(fake.host.refuse).toHaveBeenCalledWith(
      "this model is not a clocked machine; usePlay() plays a clocked machine's instructions");
  });

  it('H6: useViewer answers the handle on any model', () => {
    const fake = fakeHost({ clocked: false });
    let viewer: unknown = null;
    function App() {
      viewer = useViewer();
      return <Viewport />;
    }
    show(App, fake);
    expect(viewer).toBe(fake.host.viewer);
    expect(fake.host.refuse).not.toHaveBeenCalled();
  });
});

describe('H7: useMachine answers the handle\'s layers', () => {
  it('H7: the reading carries the handle\'s list, its identity unchanged by a notification that changes nothing and new when the list changes', async () => {
    const fake = fakeHost();
    const seen: Array<{ layers?: readonly unknown[] }> = [];
    function App() {
      const machine = useMachine() as { layers?: readonly unknown[] };
      seen.push(machine);
      return (
        <div>
          <Viewport />
          <span className="layers">
            {(machine.layers ?? []).map((one: any) => one.label).join('|')}
          </span>
        </div>
      );
    }
    show(App, fake);
    await settle();
    const text = () => fake.host.element.querySelector('.layers')!.textContent;
    expect(text()).toBe('Electrical path');
    const first = seen[seen.length - 1];
    expect(first.layers).toBe((fake.host.viewer as any).layers());

    // A notification that changes no layer: the same list, by identity.
    flushSync(() => fake.notify());
    await settle();
    expect(seen[seen.length - 1].layers).toBe(first.layers);

    // A republish that changes the list: a new reading and a render.
    const next = Object.freeze([
      Object.freeze({ key: 'electrical', label: 'Electrical path' }),
      Object.freeze({ key: 'mechanical', label: 'Rotor stepping' }),
    ]);
    fake.setLayers(next);
    flushSync(() => fake.notify());
    await settle();
    expect(text()).toBe('Electrical path|Rotor stepping');
    expect(seen[seen.length - 1]).not.toBe(first);
    expect(seen[seen.length - 1].layers).toBe(next);
  });

  it('H7: a list that changes between the first render and the subscription is not lost', async () => {
    const fake = fakeHost();
    const early = Object.freeze([Object.freeze({ key: 'a', label: 'A' })]);
    const late = Object.freeze([Object.freeze({ key: 'b', label: 'B' })]);
    let reads = 0;
    (fake.host.viewer as any).layers = () => { reads += 1; return reads === 1 ? early : late; };
    function App() {
      const machine = useMachine() as { layers?: readonly any[] };
      return <div><Viewport /><span className="layers">{(machine.layers ?? []).map((one) => one.label).join('|')}</span></div>;
    }
    show(App, fake);
    await settle();
    expect(fake.host.element.querySelector('.layers')!.textContent).toBe('B');
  });
});
