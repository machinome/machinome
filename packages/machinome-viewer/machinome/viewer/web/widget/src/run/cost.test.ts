/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// What a tick costs (design §12 risk 2, tasks 8.3). A non-affine level
// quantity samples `subdivisions` points and bisects up to
// `bisection_rounds` rounds per crossing, per jump node, per segment; an
// affine one solves. This measures both, and the acceptance machine
// beside them, so a later regression is a NUMBER rather than an
// impression.
//
// The floors asserted are deliberately an order of magnitude below the
// numbers measured on the bench, so this catches a tenfold regression
// and never a slow machine. The measurement itself is printed.

import { describe, expect, it } from 'vitest';
import corpus from '../running-corpus.json';
import acceptance from '../../../../tests/fixtures/pascaline/viewer.json';
import lock from '../../../../tests/fixtures/lock/viewer.json';
import { Engine } from './engine';
import type { RunDocument } from './program';

interface Machine { name: string; dt: number; document: unknown }

const machines =
  (corpus as unknown as { machines: Machine[] }).machines;

function ticksPerSecond(label: string, engine: Engine, ticks: number): number {
  const started = performance.now();
  engine.advance(ticks);
  const seconds = (performance.now() - started) / 1000;
  const rate = Math.round(ticks / seconds);
  // eslint-disable-next-line no-console
  console.log(`  ${label}: ${ticks} ticks in ${seconds.toFixed(3)} s ` +
              `= ${rate} ticks/s`);
  return rate;
}

describe('the cost of a tick', () => {
  const carry = machines.find((one) => one.name === 'CarryLead')!;

  it('solves an affine plan', () => {
    const engine = Engine.load(carry.document as RunDocument,
                               { dt: carry.dt, record: null });
    engine.move('column', { by: 100000, duration: carry.dt * 20000 });
    expect(ticksPerSecond('CarryLead, affine plans', engine, 20000))
      .toBeGreaterThan(10000);
  });

  it('searches when the same plan is not affine', () => {
    const searched = JSON.parse(JSON.stringify(carry.document));
    for (const edge of searched.program.edges) {
      for (const plan of edge.plans ?? []) {
        if (plan) for (const jump of plan.jumps) jump.affine = false;
      }
    }
    const engine = Engine.load(searched as RunDocument,
                               { dt: carry.dt, record: null });
    engine.move('column', { by: 5000, duration: carry.dt * 1000 });
    expect(ticksPerSecond('CarryLead, plans forced to search', engine, 1000))
      .toBeGreaterThan(1000);
  });

  it('pays nothing for a constraint in a machine that declares none',
     () => {
    // The no-regression floor the other way (design D9): `Train`
    // declares no bound reading another coordinate, so nothing this
    // cycle added may cost it anything.
    const train = machines.find((one) => one.name === 'Train')!;
    const engine = Engine.load(train.document as RunDocument,
                               { dt: train.dt, record: null });
    engine.move('crank', { by: 100000, duration: train.dt * 20000 });
    expect(ticksPerSecond('Train, no constraint', engine, 20000))
      .toBeGreaterThan(17000);
  });

  it('samples a constraint through the corpus\'s blocking ticks', () => {
    // `Captured`: the key held by the turned plug. Every tick of the
    // withdrawal samples the key's own low bound over a two-edge
    // sub-program.
    const captured = machines.find((one) => one.name === 'Captured')!;
    const engine = Engine.load(captured.document as RunDocument,
                               { dt: captured.dt, record: null });
    engine.move('twist', { by: 30, duration: captured.dt });
    engine.advance(1);
    engine.move('feed', { by: -5, duration: captured.dt * 2000 });
    expect(ticksPerSecond('Captured, blocking ticks', engine, 2000))
      .toBeGreaterThan(11000);
  });

  it('evaluates nothing when the lock stands idle', () => {
    // Three constraints declared and none of them examined: a quiet
    // tick must cost what a program with no constraint costs.
    const engine = Engine.load(lock as unknown as RunDocument,
                               { dt: 1 / 240, record: null });
    expect(ticksPerSecond('the lock, idle', engine, 2400))
      .toBeGreaterThan(1500);
  });

  it('samples five bounds over a seven-edge sub-program', () => {
    // The worst case this cycle has: advancing the key moves what all
    // three of the lock's bounds read, so every tick samples.
    const engine = Engine.load(lock as unknown as RunDocument,
                               { dt: 1 / 240, record: null });
    engine.move('insertion', { by: -60, duration: 10 });
    expect(ticksPerSecond('the lock, advancing the key', engine, 2400))
      .toBeGreaterThan(15);
  }, 120_000);

  it('runs the acceptance machine far faster than real time', () => {
    const engine = Engine.load(acceptance as unknown as RunDocument,
                               { dt: 1 / 240, record: null });
    engine.move('units_entry', { by: 10, duration: 10 });
    // Real time at dt = 1/240 is 240 ticks a second.
    expect(ticksPerSecond('the Pascaline at dt = 1/240', engine, 2400))
      .toBeGreaterThan(2400);
  });
});
