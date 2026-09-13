/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// What a live rebuild does to a live run (OpenSpec
// `drive-the-run-on-screen`, design §3).
//
// The workflow design's own rule: "Live updates must invalidate or
// explicitly migrate incompatible simulation state, not preserve
// coordinates solely because strings happen to match". `identity` is the
// digest the framework publishes to answer it -- the root class, the
// bank's ids, the inputs' declarations, the spans and every edge's ends,
// direction and expression -- so an edit that moves a law changes it and
// an edit that moves a mesh does not.

import { describe, expect, it } from 'vitest';
import { RunRuntime } from './runtime';
import { republishPlan } from './republish';
import corpus from '../running-corpus.json';
import type { RunDocument } from './program';

const machine = (corpus as unknown as {
  machines: { name: string; dt: number; document: unknown }[];
}).machines[0];

const running = { identity: 'abc123', dt: 1 / 240 };

describe('republishPlan', () => {
  it('keeps the run when the machine and the step size are unchanged', () => {
    const plan = republishPlan(running, { identity: 'abc123', dt: 1 / 240 });

    expect(plan.keep).toBe(true);
    expect(plan.outcome).toBe('kept');
    expect(plan.message).toMatch(/where it was|kept|continued/i);
  });

  it('restarts the run when the published program is another machine', () => {
    const plan = republishPlan(running, { identity: 'def456', dt: 1 / 240 });

    expect(plan.keep).toBe(false);
    expect(plan.outcome).toBe('restarted');
    // It says WHICH of the two it did, and why: a coordinate is not
    // carried across two different mechanisms.
    expect(plan.message).toMatch(/mechanism|machine/i);
    expect(plan.message).toMatch(/reset|restart/i);
  });

  it('restarts the run when the step size changed', () => {
    const plan = republishPlan(running, { identity: 'abc123', dt: 1 / 120 });

    expect(plan.keep).toBe(false);
    expect(plan.outcome).toBe('restarted');
    expect(plan.message).toMatch(/step size/i);
  });

  it('starts one when a republished document gains a program', () => {
    const plan = republishPlan(null, running);

    expect(plan.keep).toBe(false);
    expect(plan.outcome).toBe('started');
  });

  it('ends one when a republished document loses its program', () => {
    const plan = republishPlan(running, null);

    expect(plan.keep).toBe(false);
    expect(plan.outcome).toBe('ended');
  });

  it('says nothing about a document that never carried a program', () => {
    const plan = republishPlan(null, null);

    expect(plan.keep).toBe(false);
    expect(plan.outcome).toBe('none');
    expect(plan.message).toBeNull();
  });
});

describe('a kept run', () => {
  it('stands exactly where the rebuild found it', async () => {
    // The keep path is the run being LEFT ALONE: the same runtime, the
    // same bank, the same step count, the same elapsed clock. Driven
    // here through the real engine in-thread, which is what `viewer.ts`
    // holds across a `manifestChanged()`.
    const runtime = RunRuntime.start(machine.document as RunDocument, {
      dt: machine.dt, record: null,
    });
    await runtime.ready;
    const moving = runtime.move('crank', { by: 1, duration: 4 * machine.dt });
    await runtime.step(4);
    await moving;
    const before = { tick: runtime.tick(), elapsed: runtime.elapsedSeconds(),
                     bank: runtime.bank() };

    const plan = republishPlan(
      { identity: runtime.identity(), dt: machine.dt },
      { identity: runtime.identity(), dt: machine.dt });

    expect(plan.keep).toBe(true);
    expect(runtime.tick()).toBe(before.tick);
    expect(runtime.elapsedSeconds()).toBe(before.elapsed);
    expect(runtime.bank()).toEqual(before.bank);
    expect(before.tick).toBeGreaterThan(0);
    runtime.dispose();
  });
});
