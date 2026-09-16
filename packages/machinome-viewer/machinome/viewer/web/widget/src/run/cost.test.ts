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
import clearing from '../../../../tests/fixtures/clearing/viewer.json';
import carriage from '../../../../tests/fixtures/carriage/viewer.json';
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

/** Ticks per second where each tick needs something done first. */
function drivenPerSecond(label: string, engine: Engine, ticks: number,
                         before: (tick: number) => void): number {
  const started = performance.now();
  for (let tick = 0; tick < ticks; tick += 1) {
    before(tick);
    engine.advance(1);
  }
  const seconds = (performance.now() - started) / 1000;
  const rate = Math.round(ticks / seconds);
  // eslint-disable-next-line no-console
  console.log(`  ${label}: ${ticks} ticks in ${seconds.toFixed(3)} s ` +
              `= ${rate} ticks/s`);
  return rate;
}

/** `ShiftedCarry` with its CARRIAGE FROZEN at position zero: every
 * selector's branch substituted for the value it holds at `shift = 0`,
 * and the need a switched-out term named removed with it.
 *
 * The honest baseline design D9 asks for -- THE SAME LAWS as three
 * separate edges, with no block anywhere -- built from the producer's
 * own published document rather than written here. `_j2`, `_j3`, `_j6`
 * and `_j7` are the four selectors (levels `_b2`, the binding for
 * `(shift - 0.5)`); `_j0` is the lower wheel's own. */
function frozenTwin(document: unknown): RunDocument {
  const frozen = JSON.parse(JSON.stringify(document));
  const branches: Record<string, string> = {
    _j0: '1', _j2: '0', _j3: '1', _j6: '1', _j7: '0',
  };
  for (const edge of frozen.program.edges) {
    for (const plan of edge.plans ?? []) {
      if (!plan) continue;
      for (const [name, value] of Object.entries(branches)) {
        plan.skeleton = plan.skeleton.split(name).join(value);
      }
      plan.jumps = plan.jumps.filter(
        (jump: { name: string }) => !(jump.name in branches));
    }
  }
  // With the carriage frozen the lever reads the LOWER wheel only, so
  // the edge no longer waits on the higher one and the cycle is gone.
  // Its published expression is restated for the same reason: it is the
  // SAME LAW with `shift` frozen at the literal 0, which is exactly the
  // producer's `FixedZero`.
  for (const edge of frozen.program.edges) {
    if (edge.gives[0] === 'carry.travel') {
      edge.needs = edge.needs.filter((key: string) => key !== 'higher.turn');
      edge.expressions = [
        '((lower.turn * 1.0) * (carry.travel < 1.0))',
      ];
      // `(x + (higher.turn * 0))` folded, which is exactly what the
      // producer's own compiler leaves when the term is not stated.
      edge.plans[0].skeleton = '((lower.turn * 1) * _j8)';
    }
  }
  // And the twin is PUBLISHED in the order it runs in, as the producer
  // publishes `FixedZero`: with the carriage frozen the lever waits on
  // the lower wheel and the higher wheel waits on the lever, so the
  // cycle's own listing order is no longer a topological one -- which
  // the loader refuses by name, as it should.
  const order = ['lower.turn', 'carry.travel', 'higher.turn'];
  frozen.program.edges.sort(
    (a: { gives: string[] }, b: { gives: string[] }) =>
      order.indexOf(a.gives[0]) - order.indexOf(b.gives[0]));
  return frozen as RunDocument;
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
    // declares no bound reading another coordinate, so nothing that
    // cycle added may cost it anything -- and it states no law reading
    // the coordinate it drives either, so nothing THIS cycle added may
    // either. A document with no self-read pays one array-length test
    // per edge per tick and nothing else: measured on this bench at
    // 140 663 ticks/s before and 165 250 ticks/s after, which is to say
    // inside this host's run-to-run spread (design D8, tasks 10.2).
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

  it('solves a self-read whose skeleton IS affine', () => {
    // The corpus's own `Clearing`: one dial, one ring, one setter, and a
    // skeleton the producer published as affine -- so every self-read
    // crossing of it is SOLVED from the piece's two endpoint values.
    const machine = machines.find((one) => one.name === 'Clearing')!;
    const engine = Engine.load(machine.document as RunDocument,
                               { dt: machine.dt, record: null });
    engine.move('ring', { by: 100000, duration: machine.dt * 20000 });
    // Raised (openspec `walk-only-what-moves`, ADR-060): only the
    // self-read walk's moving cone is walked per point now, measured on
    // this bench at 5919 -> 14042 ticks/s.
    expect(ticksPerSecond('Clearing, a solved self-read', engine, 20000))
      .toBeGreaterThan(4000);
  }, 120_000);

  it('searches six self-read dials through a `clamp01` window', () => {
    // The Curta's own clearing interface: six dials, each its own
    // self-read edge, each with a `clamp01` station window that makes
    // the SKELETON non-affine -- so every one of its self-read crossings
    // falls to the 64-sample search plus its bisection. This is the
    // worst case this cycle has, and the number is what it costs.
    const engine = Engine.load(clearing as unknown as RunDocument,
                               { dt: 1 / 240, record: null });
    engine.move('clearing', { by: 1, duration: 10 });
    // Raised (ADR-060): 209 -> 321 ticks/s on this bench.
    expect(ticksPerSecond('the Curta fixture at dt = 1/240', engine, 2400))
      .toBeGreaterThan(150);
  }, 240_000);

  // -------------------------------------------------------------------
  // What a BLOCK costs (design D9, tasks 13). The absolute numbers are
  // this host's; the RATIOS are what this cycle records, against the
  // producer's own 1.6x a frozen twin, 2.0x on a crossing tick and 22x
  // for a searched stop.
  // -------------------------------------------------------------------

  const shifted = machines.find((one) => one.name === 'ShiftedCarry')!;

  it('costs about what its members cost, against a FROZEN TWIN and a '
     + 'tick that crosses the detent', () => {
    const quietEngine = Engine.load(shifted.document as RunDocument,
                                    { dt: shifted.dt, record: null });
    quietEngine.move('crank', { by: 20000, duration: shifted.dt * 20000 });
    const quiet = ticksPerSecond('ShiftedCarry, a quiet block tick',
                                 quietEngine, 20000);

    const twinEngine = Engine.load(frozenTwin(shifted.document),
                                   { dt: shifted.dt, record: null });
    twinEngine.move('crank', { by: 20000, duration: shifted.dt * 20000 });
    const twin = ticksPerSecond('ShiftedCarry, the frozen twin',
                                twinEngine, 20000);

    // The carriage driven across its detent and back, one tick each
    // way, so EVERY tick is a two-piece tick with two Kahn orders.
    const crossingEngine = Engine.load(shifted.document as RunDocument,
                                       { dt: shifted.dt, record: null });
    crossingEngine.move('crank', { by: 4000, duration: shifted.dt * 4000 });
    const crossing = drivenPerSecond(
      'ShiftedCarry, a crossing tick', crossingEngine, 4000,
      (tick) => crossingEngine.move('shift', {
        by: tick % 2 === 0 ? 1 : -1, duration: shifted.dt,
      }));

    // eslint-disable-next-line no-console
    console.log(`  a quiet block tick costs ${(twin / quiet).toFixed(1)}x `
                + 'the same laws with the carriage frozen, and a crossing '
                + `tick ${(quiet / crossing).toFixed(1)}x a quiet one `
                + "(the producer measured 1.6x and 2.0x)");
    // Raised (ADR-060): quiet 4320 -> 9859, crossing 2189 -> 4746 ticks/s
    // on this bench.
    expect(quiet).toBeGreaterThan(3000);
    expect(twin).toBeGreaterThan(quiet);
    expect(crossing).toBeGreaterThan(1500);
  }, 240_000);

  it('runs the Curta carriage: ONE BLOCK OF SEVEN', () => {
    // Four dials and three levers contracted into one entry, at the
    // framework's own step.
    const engine = Engine.load(carriage as unknown as RunDocument,
                               { dt: 0.02, record: null });
    engine.move('crank', { by: 36000, duration: 0.02 * 2000 });
    // Raised (ADR-060): 292 -> 738 ticks/s on this bench.
    expect(ticksPerSecond('the Curta carriage at dt = 0.02', engine, 2000))
      .toBeGreaterThan(200);
  }, 240_000);

  it('SEARCHES a stop on a block coordinate -- the expensive case', () => {
    // `affine` is FALSE on every give of a block, so a stop on one of
    // them is up to `subdivisions` samples plus `bisectionRounds`, each
    // of which re-locates the selector partition and re-runs the whole
    // block.
    //
    // The corpus's own first tick of `RangedBlock` is that tick: the
    // lever is driven INTO its range and the stop is located inside it.
    // It is replayed from a snapshot of the rest state so every tick
    // measured is the same one, and the QUIET control below is measured
    // through the same restore, so the ratio is the stop's alone.
    const ranged = machines.find((one) => one.name === 'RangedBlock')!;
    const engine = Engine.load(ranged.document as RunDocument,
                               { dt: ranged.dt, record: null });
    const rest = engine.snapshot();
    const quiet = drivenPerSecond(
      'RangedBlock, a quiet tick (restored)', engine, 400, () => {
        engine.restore(rest as never);
        engine.move('spin', { by: 0.1, duration: ranged.dt });
      });
    const stopped = drivenPerSecond(
      'RangedBlock, a SEARCHED stop (restored)', engine, 400, () => {
        engine.restore(rest as never);
        engine.move('spin', { by: 2, duration: ranged.dt });
        engine.move('shift', { by: 1, duration: ranged.dt });
      });
    // eslint-disable-next-line no-console
    console.log(`  a searched stop costs ${(quiet / stopped).toFixed(1)}x a `
                + 'quiet tick of the same machine');
    expect(stopped).toBeGreaterThan(5);
    expect(quiet).toBeGreaterThan(stopped);
  }, 240_000);

  it('runs the acceptance machine far faster than real time', () => {
    const engine = Engine.load(acceptance as unknown as RunDocument,
                               { dt: 1 / 240, record: null });
    engine.move('units_entry', { by: 10, duration: 10 });
    // Real time at dt = 1/240 is 240 ticks a second.
    expect(ticksPerSecond('the Pascaline at dt = 1/240', engine, 2400))
      .toBeGreaterThan(2400);
  });
});
