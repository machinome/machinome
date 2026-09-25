/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The main thread's side of the run (design D2, D3, D9). The render loop
// drives the cadence and there is ALWAYS ONE ADVANCE IN FLIGHT: a page
// whose tab is hidden gets no animation frame, sends no advance and
// accumulates no backlog; a worker that takes longer than a frame drops
// display frames and never a tick.

import { describe, expect, it } from 'vitest';
import { RunRuntime } from './runtime';
import type { Request } from './protocol';
import corpus from '../running-corpus.json';
import type { RunDocument } from './program';

const train = (corpus as unknown as {
  machines: { name: string; dt: number; document: unknown }[];
}).machines.find((machine) => machine.name === 'Train')!;

const document = train.document as RunDocument;

/** A port that records what the main thread sent and replies only when
 * this test says so. */
class FakePort {
  readonly sent: Request[] = [];
  private handler: ((reply: unknown) => void) | undefined;

  post(request: Request): void {
    this.sent.push(request);
  }

  onReply(handler: (reply: unknown) => void): void {
    this.handler = handler;
  }

  dispose(): void {}

  /** Answer the oldest unanswered advance with an empty frame. */
  answerAdvance(): void {
    const request = this.sent.find(
      (one) => one.t === 'advance' && !this.answered.has(one.id));
    if (request === undefined) throw new Error('no advance outstanding');
    this.answered.add((request as { id: number }).id);
    this.handler!({
      t: 'frame', id: (request as { id: number }).id, tick: 1, clock: 0,
      bank: new Float64Array(6), moved: [], crossings: [], stops: [],
      commands: [],
    });
  }

  refuse(): void {
    const request = this.sent.find(
      (one) => one.t === 'advance' && !this.answered.has(one.id));
    this.answered.add((request as { id: number }).id);
    this.handler!({
      t: 'refusal', id: (request as { id: number }).id, tick: 1,
      kind: 'conflict', message: 'two increments disagree',
    });
  }

  ready(): void {
    this.handler!({
      t: 'ready', id: 0, identity: 'x', clock: 'time', dt: 0.05,
      order: ['crank'], coordinates: {}, bank: new Float64Array(1),
    });
  }

  private readonly answered = new Set<number>();

  advances(): Request[] {
    return this.sent.filter((one) => one.t === 'advance');
  }
}

function runtime(port: FakePort, dt = 0.05): RunRuntime {
  const built = RunRuntime.start(document, {
    dt, record: null, port, frameBudget: 1 / 60,
  });
  port.ready();
  built.start();
  return built;
}

describe('one advance in flight', () => {
  it('sends nothing until a whole tick is earned, then one advance',
     () => {
       const port = new FakePort();
       const run = runtime(port);
       // At dt = 0.05 one 60 Hz frame earns a third of a tick, so the
       // first two frames send nothing and the remainder is carried.
       run.frame(1 / 60);
       run.frame(1 / 60);
       expect(port.advances()).toHaveLength(0);
       run.frame(1 / 60);
       expect(port.advances()).toHaveLength(1);
       expect((port.advances()[0] as { ticks: number }).ticks).toBe(1);
     });

  it('sends nothing more while one is outstanding, keeping the elapsed time',
     () => {
       const port = new FakePort();
       const run = runtime(port);
       run.frame(1);
       expect(port.advances()).toHaveLength(1);
       // Three more frames' worth of wall time while the first advance
       // is still outstanding: nothing is sent, and the elapsed time is
       // not thrown away.
       run.frame(1 / 60);
       run.frame(1 / 60);
       run.frame(1 / 60);
       expect(port.advances()).toHaveLength(1);
       port.answerAdvance();
       run.frame(1 / 60);
       expect(port.advances()).toHaveLength(2);
       expect((port.advances()[1] as { ticks: number }).ticks).toBe(1);
     });
});

describe('the debt', () => {
  it('carries the fractional remainder so a slow speed never stalls', () => {
    const port = new FakePort();
    const run = runtime(port);
    run.setSpeed(0.1);
    // At x0.1 one 60 Hz frame earns 0.00167 simulated seconds: a runtime
    // that rounded to zero ticks a frame would stall forever.
    let seen = 0;
    let asked = 0;
    for (let frame = 0; frame < 120; frame += 1) {
      run.frame(1 / 60);
      while (port.advances().length > seen) {
        asked += (port.advances()[seen] as { ticks: number }).ticks;
        seen += 1;
        port.answerAdvance();
      }
    }
    // Two seconds of wall time at x0.1 is 0.2 simulated seconds, which
    // is four ticks at dt = 0.05 -- the fourth still a frame or two of
    // carried remainder away at the moment the loop stops.
    expect(asked).toBeGreaterThanOrEqual(3);
    expect(asked).toBeLessThanOrEqual(4);
  });

  it('is capped at four frames\' worth, losing the wall time beyond it',
     () => {
       const port = new FakePort();
       const run = runtime(port);
       // A ten-second stall at dt = 0.05 would be 200 ticks in one burst.
       run.frame(10);
       const first = port.advances()[0] as { ticks: number };
       // The cap is four frame budgets of simulated time: 4/60 s, which
       // is one whole tick at dt = 0.05 and not two hundred.
       expect(first.ticks).toBeLessThanOrEqual(
         Math.floor((4 / 60) / 0.05) + 1);
       expect(first.ticks).toBeGreaterThan(0);
     });
});

describe('commands', () => {
  it('are posted in order while an advance is outstanding', () => {
    const port = new FakePort();
    const run = runtime(port);
    run.frame(1);
    void run.move('crank', { by: 1, duration: 0.5 });
    void run.rate('lever', 4);
    void run.cancel('crank');
    const ops = port.sent.filter((one) => one.t === 'command')
      .map((one) => (one as { op: string }).op);
    expect(ops).toEqual(['move', 'rate', 'cancel']);
    // And the advance was sent before them, which is the ordering the
    // worker applies: a command lands before the next tick it integrates.
    expect(port.sent.map((one) => one.t))
      .toEqual(['load', 'advance', 'command', 'command', 'command']);
  });
});

describe('a refusal', () => {
  it('pauses the run rather than retrying sixty times a second', () => {
    const port = new FakePort();
    const run = runtime(port);
    run.frame(1);
    expect(run.running()).toBe(true);
    port.refuse();
    expect(run.running()).toBe(false);
    run.frame(1);
    expect(port.advances()).toHaveLength(1);
  });
});

describe('the worker', () => {
  it('falls back in-thread when the Worker constructor throws', async () => {
    const run = RunRuntime.start(document, {
      dt: 0.05,
      record: null,
      workerFactory: () => { throw new Error('worker-src none'); },
    });
    expect(run.runsInWorker).toBe(false);
    await run.ready;
    expect(run.identity()).toBe(
      (document.program as { identity: string }).identity);
    run.dispose();
  });

  it('runs the same engine in-thread, tick for tick', async () => {
    const run = RunRuntime.start(document, {
      dt: 0.05,
      record: null,
      workerFactory: () => { throw new Error('no worker here'); },
    });
    await run.ready;
    const done = run.move('crank', { by: 20, duration: 0.5 });
    await run.step(10);
    const [outcome] = await done;
    expect(outcome.status).toBe('completed');
    expect(outcome.admitted).toBeCloseTo(20, 12);
    expect(run.tick()).toBe(10);
    expect(run.bank()['first.turn']).toBeCloseTo(40, 12);
    run.dispose();
  });
});
