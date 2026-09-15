/**
 * @vitest-environment jsdom
 */
/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The part gesture's DOM behaviour against a STUB host (design D17, and
// the seam `inspector.test.ts` already uses for `mount`): `mount()`
// builds a `THREE.WebGLRenderer`, which jsdom cannot give a context
// for, so this test never calls the real one. It calls
// `partSurfaceWith(host)` directly -- which is exactly what `mount()`
// does with the real collaborators -- and `outcomeLabelIn(container)`,
// the transient report's own factory.
//
// What is tested here is everything jsdom can reach: the cursor, the
// title, the label's text and lifetime, the press, the drag's one-at-a-
// time requests, and the five sides a gesture ends on. The geometry is
// the host's `reader`, and the browser proves it (tests/
// test_running_document.py).

import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';
import { outcomeLabelIn, partSurfaceWith } from './viewer';
import type {
  PartSurface, PartSurfaceHost, Point, SweepReader,
} from './viewer';
import type { LoadedControl } from './partControls';
import type { OutcomeReport } from './runControls';

const BUTTON: LoadedControl = {
  name: 'units dial',
  kind: 'button',
  part: ['units', 'input', 'dial'],
  instruction: 'Add one',
  input: null,
  perUnit: null,
  joint: ['units', 'input'],
  coordinate: 'units.input.turn',
  axis: [1, 0, 0],
  origin: [0, 0, 0],
};

const TURN: LoadedControl = {
  name: 'turn units',
  kind: 'turn',
  part: ['units', 'input', 'dial'],
  instruction: null,
  input: 'units_entry',
  perUnit: -36,
  joint: ['units', 'input'],
  coordinate: 'units.input.turn',
  axis: [1, 0, 0],
  origin: [0, 0, 0],
};

interface Deferred {
  promise: Promise<OutcomeReport | null>;
  settle(report: OutcomeReport | null): Promise<void>;
}

function deferred(): Deferred {
  let resolve: (report: OutcomeReport | null) => void = () => undefined;
  const promise = new Promise<OutcomeReport | null>((done) => {
    resolve = done;
  });
  return {
    promise,
    async settle(report) {
      resolve(report);
      // Two turns of the microtask queue: the surface's own `.then`,
      // and whatever it issues from inside it.
      await promise;
      await Promise.resolve();
      await Promise.resolve();
    },
  };
}

function pointer(type: string, init: {
  clientX?: number; clientY?: number; pointerId?: number; button?: number;
} = {}): PointerEvent {
  const event = new MouseEvent(type, {
    bubbles: true,
    cancelable: true,
    clientX: init.clientX ?? 0,
    clientY: init.clientY ?? 0,
    button: init.button ?? 0,
  });
  Object.defineProperty(event, 'pointerId',
                        { value: init.pointerId ?? 1 });
  return event as unknown as PointerEvent;
}

const surfaces: PartSurface[] = [];

function stubs(options: { delta?: number; reader?: boolean } = {}) {
  const container = document.createElement('div');
  const canvas = document.createElement('canvas');
  container.append(canvas);
  document.body.append(container);
  const orbit = { enabled: true };
  const captured: number[] = [];
  const released: number[] = [];
  Object.assign(canvas, {
    setPointerCapture: (id: number) => { captured.push(id); },
    releasePointerCapture: (id: number) => { released.push(id); },
  });

  let under: readonly LoadedControl[] | null = null;
  const picks: Point[] = [];
  const highlighted: readonly LoadedControl[][] = [];
  const restored: number[] = [];
  const triggers: { name: string; at: Point }[] = [];
  const moves: { input: string; by: number; seconds: number; at: Point }[] = [];
  const pending: Deferred[] = [];
  let noRun = false;

  const reader: SweepReader = {
    read: () => options.delta ?? 0,
  };

  const host: PartSurfaceHost = {
    container,
    canvas,
    orbit,
    pick(x, y) {
      picks.push({ x, y });
      return under;
    },
    highlight(controls) {
      (highlighted as readonly LoadedControl[][] as LoadedControl[][])
        .push([...controls]);
      return () => { restored.push(highlighted.length); };
    },
    reader: () => (options.reader === false ? null : reader),
    nudge: () => ({ amount: 1, seconds: 0.2 }),
    trigger(name, at) {
      triggers.push({ name, at });
      if (noRun) {
        return null;
      }
      const one = deferred();
      pending.push(one);
      return one.promise;
    },
    move(input, by, seconds, at) {
      moves.push({ input, by, seconds, at });
      if (noRun) {
        return null;
      }
      const one = deferred();
      pending.push(one);
      return one.promise;
    },
  };

  const surface = partSurfaceWith(host);
  surfaces.push(surface);
  return {
    host, container, canvas, orbit, captured, released, picks, highlighted,
    restored, triggers, moves, pending, surface,
    show(controls: readonly LoadedControl[]) { under = controls; },
    silence() { noRun = true; },
  };
}

beforeEach(() => {
  document.body.replaceChildren();
});

describe('a hand chooses one physical freedom', () => {
  const SLIDE: LoadedControl = { ...TURN, name: 'lift crank', kind: 'slide',
    input: 'lift', perUnit: 1, coordinate: 'units.input.lift' };

  it('drags an ordinary sliding part directly', () => {
    const bench = stubs({ delta: 2 });
    bench.surface.refresh([SLIDE], true);
    bench.show([SLIDE]);
    bench.canvas.dispatchEvent(pointer('pointerdown'));
    bench.canvas.dispatchEvent(pointer('pointermove', { clientX: 10 }));
    expect(bench.moves).toEqual([{ input: 'lift', by: 1, seconds: 0.2,
      at: { x: 10, y: 0 } }]);
  });

  it('does not guess a freedom on an ambiguous body drag', () => {
    const bench = stubs({ delta: -40 });
    bench.surface.refresh([BUTTON, TURN, SLIDE], true);
    bench.show([BUTTON, TURN, SLIDE]);
    bench.canvas.dispatchEvent(pointer('pointerdown'));
    bench.canvas.dispatchEvent(pointer('pointermove', { clientX: 100 }));
    expect(bench.moves).toEqual([]);
  });

  it('makes both handles reachable after a touch selection; a handle never presses the body', () => {
    const bench = stubs({ delta: 2 });
    bench.host.point = () => ({ x: 100, y: 100 });
    bench.surface.refresh([BUTTON, TURN, SLIDE], true);
    bench.show([BUTTON, TURN, SLIDE]);
    bench.canvas.dispatchEvent(pointer('pointerdown'));
    bench.canvas.dispatchEvent(pointer('pointerup'));
    expect(bench.triggers).toHaveLength(1);
    const handles = bench.container.querySelectorAll<HTMLButtonElement>('.part-gesture-handle');
    expect(handles).toHaveLength(2);
    const slide = Array.from(handles).find(one => one.dataset.control === SLIDE.name)!;
    slide.dispatchEvent(pointer('pointerdown'));
    bench.canvas.dispatchEvent(pointer('pointermove', { clientX: 20 }));
    bench.canvas.dispatchEvent(pointer('pointerup', { clientX: 20 }));
    expect(bench.moves[0].input).toBe('lift');
    expect(bench.triggers).toHaveLength(1);
  });

  it('ends a held gesture when the document is replaced', () => {
    const bench = stubs();
    bench.surface.refresh([TURN], true);
    bench.show([TURN]);
    bench.canvas.dispatchEvent(pointer('pointerdown'));
    bench.surface.refresh([SLIDE], true);
    expect(bench.surface.engaged()).toBe(false);
    expect(bench.orbit.enabled).toBe(true);
  });

  it('does not pick through a panel button into the machine', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], true);
    bench.show([BUTTON]);
    const panel = document.createElement('button');
    bench.container.append(panel);
    panel.dispatchEvent(pointer('pointerdown'));
    panel.dispatchEvent(pointer('pointerup'));
    expect(bench.triggers).toEqual([]);
    expect(bench.orbit.enabled).toBe(true);
  });
});

afterEach(() => {
  surfaces.splice(0).forEach((surface) => surface.dispose());
  document.body.replaceChildren();
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe('the part surface presents nothing it was not asked for (D2, D14)',
         () => {
  it('installs no listener for a document that declares no control', () => {
    const bench = stubs();
    bench.surface.refresh([], true);
    bench.show([BUTTON]);
    bench.canvas.dispatchEvent(pointer('pointerdown'));
    expect(bench.picks).toEqual([]);
    expect(bench.orbit.enabled).toBe(true);
    expect(bench.triggers).toEqual([]);
  });

  it('installs no listener when the host suppressed the affordance', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], false);
    bench.show([BUTTON]);
    bench.canvas.dispatchEvent(pointer('pointerdown'));
    expect(bench.picks).toEqual([]);
    expect(bench.orbit.enabled).toBe(true);
  });

  it('takes the listeners away again when the affordance is suppressed',
     () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], true);
    bench.show([BUTTON]);
    bench.surface.refresh([BUTTON], false);
    bench.canvas.dispatchEvent(pointer('pointerdown'));
    expect(bench.picks).toEqual([]);
  });
});

describe('hover is a cursor, a title and a highlight (D7)', () => {
  it('names every control on the hovered part', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON, TURN], true);
    bench.show([BUTTON, TURN]);
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 40, clientY: 50 }));
    bench.surface.pollHover();

    expect(bench.picks).toEqual([{ x: 40, y: 50 }]);
    expect(bench.canvas.style.cursor).toBe('pointer');
    expect(bench.canvas.getAttribute('title'))
      .toBe('units dial · turn units');
    expect(bench.highlighted).toEqual([[BUTTON, TURN]]);
  });

  it('casts at most once per poll, however many times the pointer moved',
     () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], true);
    bench.show([BUTTON]);
    for (let step = 0; step < 5; step += 1) {
      bench.canvas.dispatchEvent(
        pointer('pointermove', { clientX: step, clientY: 0 }));
    }
    bench.surface.pollHover();
    bench.surface.pollHover();
    expect(bench.picks).toEqual([{ x: 4, y: 0 }]);
  });

  it('clears the cursor, the title and the highlight on unhover', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], true);
    bench.show([BUTTON]);
    bench.canvas.dispatchEvent(pointer('pointermove', { clientX: 1 }));
    bench.surface.pollHover();
    expect(bench.canvas.style.cursor).toBe('pointer');

    bench.show(null as unknown as readonly LoadedControl[]);
    bench.canvas.dispatchEvent(pointer('pointermove', { clientX: 400 }));
    bench.surface.pollHover();
    expect(bench.canvas.style.cursor).toBe('');
    expect(bench.canvas.hasAttribute('title')).toBe(false);
    expect(bench.restored).toHaveLength(1);
  });

  it('does not cast while a gesture is engaged', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], true);
    bench.show([BUTTON]);
    bench.canvas.dispatchEvent(
      pointer('pointerdown', { clientX: 10, clientY: 10 }));
    bench.picks.length = 0;
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 11, clientY: 10 }));
    bench.surface.pollHover();
    expect(bench.picks).toEqual([]);
  });
});

describe('a press is a pointerup inside the threshold (D8)', () => {
  it('submits the declared instruction, at the point it was made', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON, TURN], true);
    bench.show([BUTTON, TURN]);
    bench.canvas.dispatchEvent(
      pointer('pointerdown', { clientX: 100, clientY: 120 }));
    bench.canvas.dispatchEvent(
      pointer('pointerup', { clientX: 102, clientY: 121 }));
    expect(bench.triggers).toEqual([
      { name: 'Add one', at: { x: 102, y: 121 } },
    ]);
    expect(bench.moves).toEqual([]);
  });

  it('suspends the camera, captures the pointer and stops the event', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], true);
    bench.show([BUTTON]);
    const down = pointer('pointerdown', { clientX: 5, clientY: 5,
      pointerId: 7 });
    const seen: string[] = [];
    // OrbitControls' own listener lives on the canvas; the surface's is
    // a CAPTURE listener on the container, an ancestor, so it runs
    // strictly first and this never fires.
    bench.canvas.addEventListener('pointerdown', () => seen.push('orbit'));
    bench.canvas.dispatchEvent(down);
    expect(seen).toEqual([]);
    expect(bench.orbit.enabled).toBe(false);
    expect(bench.captured).toEqual([7]);
    expect(bench.surface.engaged()).toBe(true);

    bench.canvas.dispatchEvent(pointer('pointerup', { pointerId: 7 }));
    expect(bench.orbit.enabled).toBe(true);
    expect(bench.released).toEqual([7]);
    expect(bench.surface.engaged()).toBe(false);
  });

  it('is a DRAG once the pointer has travelled, and not a press again', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], true);
    bench.show([BUTTON]);
    bench.canvas.dispatchEvent(
      pointer('pointerdown', { clientX: 100, clientY: 100 }));
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 110, clientY: 100 }));
    // Back inside the threshold: still a drag.
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 100, clientY: 100 }));
    bench.canvas.dispatchEvent(
      pointer('pointerup', { clientX: 100, clientY: 100 }));
    expect(bench.triggers).toEqual([]);
  });

  it('stays a press inside four pixels', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], true);
    bench.show([BUTTON]);
    bench.canvas.dispatchEvent(
      pointer('pointerdown', { clientX: 100, clientY: 100 }));
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 102, clientY: 102 }));
    bench.canvas.dispatchEvent(
      pointer('pointerup', { clientX: 102, clientY: 102 }));
    expect(bench.triggers).toHaveLength(1);
  });

  it('does nothing at all on a part that carries only a turn', () => {
    const bench = stubs();
    bench.surface.refresh([TURN], true);
    bench.show([TURN]);
    bench.canvas.dispatchEvent(pointer('pointerdown', { clientX: 3 }));
    bench.canvas.dispatchEvent(pointer('pointerup', { clientX: 3 }));
    expect(bench.triggers).toEqual([]);
    expect(bench.moves).toEqual([]);
  });
});

describe('a drag issues one quantum at a time (D11, D12)', () => {
  const engage = (delta: number) => {
    const bench = stubs({ delta });
    bench.surface.refresh([TURN], true);
    bench.show([TURN]);
    bench.canvas.dispatchEvent(
      pointer('pointerdown', { clientX: 100, clientY: 100 }));
    return bench;
  };

  it('asks for one whole quantum, signed through the ratio', async () => {
    const bench = engage(-40);
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 100, clientY: 140 }));
    // -40 degrees of sweep on per_unit = -36 asks for +1 DIGIT.
    expect(bench.moves).toEqual([
      { input: 'units_entry', by: 1, seconds: 0.2,
        at: { x: 100, y: 140 } },
    ]);
  });

  it('keeps at most one in flight and asks again when it retires',
     async () => {
    const bench = engage(-40);
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 100, clientY: 140 }));
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 100, clientY: 180 }));
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 100, clientY: 220 }));
    // Three quanta of sweep, one request.
    expect(bench.moves).toHaveLength(1);

    await bench.pending[0].settle({
      status: 'completed', admitted: 1, unit: 'digit', message: null,
    });
    expect(bench.moves).toHaveLength(2);
  });

  it('leaves the origin where it is when a request is blocked, and issues '
     + 'nothing more while the drag is held there', async () => {
    const bench = engage(-40);
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 100, clientY: 140 }));
    expect(bench.moves).toHaveLength(1);
    await bench.pending[0].settle({
      status: 'blocked', admitted: 0, unit: 'digit', message: null,
    });
    expect(bench.moves).toHaveLength(1);
    for (let step = 0; step < 5; step += 1) {
      bench.canvas.dispatchEvent(
        pointer('pointermove', { clientX: 100, clientY: 200 + step }));
    }
    expect(bench.moves).toHaveLength(1);
  });

  it('never moves anything on a part with no measurable geometry',
     () => {
    const bench = stubs({ delta: -40, reader: false });
    bench.surface.refresh([TURN], true);
    bench.show([TURN]);
    bench.canvas.dispatchEvent(
      pointer('pointerdown', { clientX: 100, clientY: 100 }));
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 100, clientY: 200 }));
    expect(bench.moves).toEqual([]);
  });
});

describe('a gesture ends on every side an interaction can (D13)', () => {
  const paths: [string, (bench: ReturnType<typeof stubs>) => void][] = [
    ['a release', (bench) => {
      bench.canvas.dispatchEvent(pointer('pointerup', { pointerId: 3 }));
    }],
    ['a cancelled pointer', (bench) => {
      bench.canvas.dispatchEvent(pointer('pointercancel', { pointerId: 3 }));
    }],
    ['lost pointer capture', (bench) => {
      bench.canvas.dispatchEvent(
        pointer('lostpointercapture', { pointerId: 3 }));
    }],
    ['the window losing focus', () => {
      window.dispatchEvent(new Event('blur'));
    }],
    ['the page ceasing to be displayed', () => {
      Object.defineProperty(document, 'hidden',
                            { configurable: true, get: () => true });
      document.dispatchEvent(new Event('visibilitychange'));
    }],
  ];

  paths.forEach(([name, stop]) => {
    it(`ends on ${name}, and gives the camera back`, () => {
      const bench = stubs({ delta: -40 });
      bench.surface.refresh([TURN], true);
      bench.show([TURN]);
      bench.canvas.dispatchEvent(
        pointer('pointerdown', { clientX: 10, clientY: 10, pointerId: 3 }));
      bench.canvas.dispatchEvent(
        pointer('pointermove', { clientX: 10, clientY: 60, pointerId: 3 }));
      expect(bench.surface.engaged()).toBe(true);
      expect(bench.orbit.enabled).toBe(false);
      const issued = bench.moves.length;

      stop(bench);

      expect(bench.surface.engaged()).toBe(false);
      expect(bench.orbit.enabled).toBe(true);
      expect(bench.released).toEqual([3]);
      expect(bench.canvas.style.cursor).toBe('');
      expect(bench.canvas.hasAttribute('title')).toBe(false);

      // Nothing new is requested afterwards.
      bench.canvas.dispatchEvent(
        pointer('pointermove', { clientX: 10, clientY: 300, pointerId: 3 }));
      expect(bench.moves).toHaveLength(issued);
      Object.defineProperty(document, 'hidden',
                            { configurable: true, get: () => false });
    });
  });

  it('leaves a move already in flight to retire and report', async () => {
    const bench = stubs({ delta: -40 });
    bench.surface.refresh([TURN], true);
    bench.show([TURN]);
    bench.canvas.dispatchEvent(
      pointer('pointerdown', { clientX: 10, clientY: 10, pointerId: 3 }));
    bench.canvas.dispatchEvent(
      pointer('pointermove', { clientX: 10, clientY: 60, pointerId: 3 }));
    expect(bench.moves).toHaveLength(1);

    bench.canvas.dispatchEvent(pointer('pointerup', { pointerId: 3 }));
    // It was not cancelled: it settles on its own, and nothing follows.
    await bench.pending[0].settle({
      status: 'completed', admitted: 1, unit: 'digit', message: null,
    });
    expect(bench.moves).toHaveLength(1);
  });

  it('takes the listeners with it on dispose', () => {
    const bench = stubs();
    bench.surface.refresh([BUTTON], true);
    bench.show([BUTTON]);
    bench.surface.dispose();
    bench.canvas.dispatchEvent(pointer('pointerdown'));
    window.dispatchEvent(new Event('blur'));
    expect(bench.picks).toEqual([]);
    expect(bench.orbit.enabled).toBe(true);
  });
});

describe('the transient outcome label (D9)', () => {
  const report = (status: OutcomeReport['status'],
                  admitted: number | null = null): OutcomeReport => ({
    status, admitted, unit: 'digit', message: null,
  });

  it('writes formatOutcome\'s own words, beside the point it was made at',
     () => {
    const container = document.createElement('div');
    document.body.append(container);
    const label = outcomeLabelIn(container);

    label.show(report('active'), { x: 40, y: 60 });
    const element = container.querySelector('.part-outcome') as HTMLElement;
    expect(element).not.toBeNull();
    expect(element.getAttribute('role')).toBe('status');
    expect(element.textContent).toBe('running…');
    expect(element.style.left).toBe('52px');
    expect(element.style.top).toBe('72px');
  });

  it('is REPLACED by the next report rather than stacked', () => {
    const container = document.createElement('div');
    document.body.append(container);
    const label = outcomeLabelIn(container);
    label.show(report('active'), { x: 0, y: 0 });
    label.show(report('blocked', 0), { x: 10, y: 10 });
    expect(container.querySelectorAll('.part-outcome')).toHaveLength(1);
    expect(container.textContent).toBe('blocked after 0 digit');
  });

  it('says exactly what a blocked nudge on the panel says', () => {
    const container = document.createElement('div');
    document.body.append(container);
    const label = outcomeLabelIn(container);
    label.show(report('completed', 1), { x: 0, y: 0 });
    expect(container.textContent).toBe('completed');
    label.show(report('cancelled'), { x: 0, y: 0 });
    expect(container.textContent).toBe('cancelled');
  });

  it('is taken away after a few seconds, and the clock restarts on each '
     + 'report', () => {
    vi.useFakeTimers();
    const container = document.createElement('div');
    document.body.append(container);
    const label = outcomeLabelIn(container, 1000);

    label.show(report('active'), { x: 0, y: 0 });
    vi.advanceTimersByTime(900);
    expect(container.querySelector('.part-outcome')).not.toBeNull();
    // A second report restarts the clock rather than inheriting it.
    label.show(report('completed', 1), { x: 0, y: 0 });
    vi.advanceTimersByTime(900);
    expect(container.querySelector('.part-outcome')).not.toBeNull();
    vi.advanceTimersByTime(200);
    expect(container.querySelector('.part-outcome')).toBeNull();
  });

  it('goes away on dispose, whatever the clock says', () => {
    vi.useFakeTimers();
    const container = document.createElement('div');
    document.body.append(container);
    const label = outcomeLabelIn(container, 1000);
    label.show(report('active'), { x: 0, y: 0 });
    label.remove();
    expect(container.querySelector('.part-outcome')).toBeNull();
    vi.advanceTimersByTime(5000);
    expect(container.querySelector('.part-outcome')).toBeNull();
  });
});
