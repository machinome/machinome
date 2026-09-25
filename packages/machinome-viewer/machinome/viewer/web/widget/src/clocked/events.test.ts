/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The EVENT SOLVE (OpenSpec `execute-the-commit`, design §6, mirroring
// `simulation/clocked.py`'s `Committing.next_event` and `_located`).
//
// The corpus pins the whole of it against the producer's own numbers;
// what is pinned HERE is each rule of the solve on its own, so a
// disagreement names the rule rather than a machine.

import { describe, expect, it } from 'vitest';
import { bindingTable } from '../bindings';
import { nextAfter } from '../run/jumps';
import type { Manifest } from '../types';
import { loadClocked } from './document';
import type { ClockedDocument, LoadedMachine } from './document';
import { nextEvent } from './events';

function machineOf(clocked: Record<string, unknown>,
                   drivers: Record<string, unknown>,
                   states: Record<string, unknown>): LoadedMachine {
  const document = {
    format: 'machinome-export',
    version: 8,
    drivers,
    states,
    instructions: {},
    bindings: [],
    clocked: {
      identity: 'hand-written',
      clock: null,
      own: '_own',
      bounds: [],
      limits: { crossing_tolerance: 1e-12, max_crossings: 1000 },
      ...clocked,
    },
  };
  const url = 'hand.json';
  return loadClocked(document as unknown as ClockedDocument, url,
                     bindingTable(document as unknown as Manifest, url));
}

const FREE = { default: 0, range: null, unit: null, dtype: null, scale: null };
const COUNT = {
  default: 0, range: null, unit: null, dtype: 'int', scale: null,
};

function stepper(primitive: string, level: string,
                 shape = 'affine'): LoadedMachine {
  return machineOf({
    commits: [{
      sources: ['x', 'n'],
      targets: ['n'],
      at: { primitive, level },
      law: ['(n + 1)'],
      shapes: { x: shape },
      description: '(x, n) commits n',
      stated_by: 'Hand',
    }],
  }, { x: FREE }, { n: COUNT });
}

describe('where a committing relation fires on one path', () => {
  it('takes BOTH ends of the path: a request ENDING exactly on a surface '
     + 'has reached it', () => {
    const machine = stepper('floor', '(x / 360.0)');
    // `move('x', by=360)` with `at = floor(x / 360)` IS one stroke.
    const found = nextEvent(machine, machine.commits[0], { x: 0, n: 0 }, 'x',
                            0, 360);
    expect(found).not.toBeNull();
    expect((found as { landing: number }).landing).toBe(360);
    expect((found as { where: number }).where).toBe(1);
  });

  it('lands on the FAR side, which for a STRICT surface is the next '
     + 'representable value', () => {
    const machine = stepper('>', '(x - 1.0)');
    const found = nextEvent(machine, machine.commits[0], { x: 0, n: 0 }, 'x',
                            0, 2);
    // `x > 1` is false AT 1 and true one representable value beyond it.
    expect((found as { landing: number }).landing)
      .toBe(nextAfter(1, Infinity));
  });

  it('leaves a strict surface reached EXACTLY AT THE ENDPOINT to the next '
     + 'request (closure 1)', () => {
    const machine = stepper('>', '(x - 1.0)');
    // The landing lies BEYOND this request's endpoint, so the crossing
    // belongs to the request whose PATH CONTAINS its landing.
    expect(nextEvent(machine, machine.commits[0], { x: 0, n: 0 }, 'x', 0, 1))
      .toBeNull();
    // ... and the request that BEGINS on it takes it at fraction zero.
    const next = nextEvent(machine, machine.commits[0], { x: 1, n: 0 }, 'x',
                           1, 1);
    expect((next as { where: number }).where).toBe(0);
    expect((next as { landing: number }).landing)
      .toBe(nextAfter(1, Infinity));
  });

  it('fires NOTHING for a request resuming from its own landing', () => {
    const machine = stepper('floor', '(x / 360.0)');
    // The path begins ON the surface and the next representable value
    // reads the SAME branch: the machine already stands on the far side.
    expect(nextEvent(machine, machine.commits[0], { x: 360, n: 1 }, 'x', 360,
                     360)).not.toBeNull();
    const resumed = nextEvent(machine, machine.commits[0], { x: 360, n: 1 },
                              'x', 360, 10);
    expect(resumed).toBeNull();
  });

  it('fires only RISING steps, read AT THE LANDING', () => {
    const machine = stepper('floor', '(x / 360.0)');
    // Dragging backwards crosses the same surfaces the other way, and
    // `floor` FALLS there: nothing fires.
    expect(nextEvent(machine, machine.commits[0], { x: 720, n: 2 }, 'x', 720,
                     -400)).toBeNull();
    // A mechanism that commits on the other edge negates its own level.
    const other = stepper('floor', '((0.0 - x) / 360.0)');
    expect(nextEvent(other, other.commits[0], { x: 720, n: 2 }, 'x', 720,
                     -400)).not.toBeNull();
  });

  it('adds the path\'s OWN opening surface when the level starts on one',
     () => {
    const machine = stepper('>=', '(x - 0.0)');
    // `x >= 0` is already 1 at x = 0, so the level starts ON its one
    // surface and the request resuming from it takes nothing...
    expect(nextEvent(machine, machine.commits[0], { x: 0, n: 0 }, 'x', 0, 5))
      .toBeNull();
    // ... while a request arriving from below fires at the surface
    // itself, a NON-STRICT comparison landing on the threshold.
    const arriving = nextEvent(machine, machine.commits[0], { x: -5, n: 0 },
                               'x', -5, 5);
    expect((arriving as { landing: number }).landing).toBe(0);
  });

  it('finds EVERY surface of an affine level, and reports the first', () => {
    const machine = stepper('floor', '(x / 360.0)');
    // Three tooth windows in one request: the first is reported and the
    // caller resumes from its landing, which is what makes a crank
    // passing three windows commit three strokes rather than one.
    const found = nextEvent(machine, machine.commits[0], { x: 0, n: 0 }, 'x',
                            0, 1100);
    expect((found as { landing: number }).landing).toBe(360);
  });

  it('cuts a KINKED level at its own breakpoints', () => {
    // The SHAPE is READ, never re-derived: the document publishes
    // `kinked` and the solve cuts at the breakpoint because of it.
    const machine = stepper('floor', 'abs((x - 5.0))', 'kinked');
    expect(machine.commits[0].jumps.get('x')?.shape).toBe('kinked');
    // `floor(|x - 5|)` falls to zero at x = 5 and rises again: the
    // breakpoint is inside the path, and the piece after it carries its
    // own surfaces.
    const found = nextEvent(machine, machine.commits[0], { x: 0, n: 0 }, 'x',
                            0, 12);
    expect(found).not.toBeNull();
    // Rising on the way DOWN to the kink is impossible -- |x-5| falls --
    // so the first rising step is on the far side of it, at x = 6.
    expect((found as { landing: number }).landing).toBe(6);
  });

  it('is not examined at all for an input its `shapes` does not name', () => {
    const machine = stepper('floor', '(x / 360.0)');
    expect(machine.commits[0].jumps.has('y')).toBe(false);
    expect(nextEvent(machine, machine.commits[0], { x: 0, n: 0 }, 'y', 0,
                     1000)).toBeNull();
  });

  it('locates nothing on a zero-length path', () => {
    const machine = stepper('floor', '(x / 360.0)');
    expect(nextEvent(machine, machine.commits[0], { x: 0, n: 0 }, 'x', 0, 0))
      .toBeNull();
  });
});
