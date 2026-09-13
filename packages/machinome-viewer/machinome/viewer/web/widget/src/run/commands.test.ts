/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The handle a `move` or a `rate` returns (`simulation/run.py`'s `class
// Command` and `driver.py`'s `RampProgram`, reproduced). What a command
// admits over a tick is a PURE FUNCTION of the number of ticks since it
// started, so a replayed run admits exactly the same travel.

import { describe, expect, it } from 'vitest';
import { Command } from './commands';
import { Run } from './run';
import { loadProgram } from './program';
import type { LoadedProgram, RunDocument } from './program';
import type { ManifestDriver } from '../types';

const float: ManifestDriver = {
  default: 0, range: null, unit: 'deg', dtype: null, scale: null,
};
const integer: ManifestDriver = {
  default: 0, range: null, unit: 'step', dtype: 'int', scale: null,
};
const scaled: ManifestDriver = {
  default: 0, range: null, unit: 'mm', dtype: null, scale: 0.01,
};

describe('a move', () => {
  it('with no duration lands entirely at the tick it was requested on', () => {
    const command = new Command('crank', 'move', float, 4,
                                { native: 20, ticks: 0, value: 0 });
    expect(command.admits(4, 0.05)).toBe(20);
    expect(command.admits(5, 0.05)).toBe(0);
    expect(command.admits(3, 0.05)).toBe(0);
    expect(command.finished(4)).toBe(true);
  });

  it('ramped, admits value_at(k) - value_at(k - 1)', () => {
    const command = new Command('crank', 'move', float, 0,
                                { native: 20, ticks: 4, value: 0 });
    expect(command.admits(0, 0.05)).toBe(0);
    expect(command.admits(1, 0.05)).toBe(5);
    expect(command.admits(2, 0.05)).toBe(5);
    expect(command.admits(4, 0.05)).toBe(5);
    expect(command.admits(5, 0.05)).toBe(0);
    expect(command.finished(3)).toBe(false);
    expect(command.finished(4)).toBe(true);
  });

  it('distributes an integer ramp as start + floor(delta*k / ticks)', () => {
    const command = new Command('motor', 'move', integer, 0,
                                { native: 10, ticks: 4, value: 0 });
    // floor(10*1/4)=2, floor(10*2/4)=5, floor(10*3/4)=7, then the target.
    expect([1, 2, 3, 4].map((k) => command.admits(k, 0.05)))
      .toEqual([2, 3, 2, 3]);
  });

  it('floors a NEGATIVE integer delta, where truncation would differ', () => {
    const command = new Command('motor', 'move', integer, 0,
                                { native: -10, ticks: 4, value: 0 });
    // Python's `//` floors: -3, -5, -8, then the target -10.
    expect([1, 2, 3, 4].map((k) => command.admits(k, 0.05)))
      .toEqual([-3, -2, -3, -2]);
    expect([1, 2, 3, 4].reduce(
      (total, k) => total + command.admits(k, 0.05), 0)).toBe(-10);
  });
});

describe('a rate', () => {
  it('admits cumulative(k) - cumulative(k - 1)', () => {
    const command = new Command('lever', 'rate', float, 0,
                                { nativeRate: 4 });
    expect(command.admits(0, 0.05)).toBe(0);
    expect(command.admits(1, 0.05)).toBeCloseTo(0.2, 12);
    expect(command.admits(2, 0.05)).toBeCloseTo(4 * 0.05 * 2 - 4 * 0.05, 12);
    expect(command.finished(100)).toBe(false);
    expect(command.requested).toBeNull();
    expect(command.remaining).toBeNull();
    expect(command.rate).toBe(4);
  });

  it('truncates an integer rate toward zero, both ways', () => {
    const forward = new Command('motor', 'rate', integer, 0,
                                { nativeRate: 7 });
    // trunc(7*0.1*k): 0, 1, 2, 2, 2, 3 -> increments 0, 1, 1, 0, 0, 1
    expect([1, 2, 3, 4, 5].map((k) => forward.admits(k, 0.1)))
      .toEqual([0, 1, 1, 0, 1]);
    const backward = new Command('motor', 'rate', integer, 0,
                                 { nativeRate: -7 });
    expect([1, 2, 3, 4, 5].map((k) => backward.admits(k, 0.1)))
      .toEqual([0, -1, -1, 0, -1]);
  });
});

describe('the design units a caller states a request in', () => {
  it('converts native travel back through the declared scale', () => {
    const command = new Command('axis', 'move', scaled, 0,
                                { native: 500, ticks: 1, value: 0 });
    expect(command.requested).toBe(5);
    command.admittedNative = 200;
    expect(command.admitted).toBe(2);
    expect(command.remaining).toBe(3);
  });

  it('leaves an unscaled driver\'s numbers alone', () => {
    const command = new Command('crank', 'move', float, 0,
                                { native: 20, ticks: 1, value: 0 });
    expect(command.requested).toBe(20);
    expect(command.admitted).toBe(0);
  });
});

describe('cancel', () => {
  it('stops an active command where it stands', () => {
    const command = new Command('crank', 'move', float, 0,
                                { native: 20, ticks: 4, value: 0 });
    command.cancel();
    expect(command.status).toBe('cancelled');
  });

  it('leaves a retired command reporting what it reported', () => {
    const command = new Command('crank', 'move', float, 0,
                                { native: 20, ticks: 4, value: 0 });
    command.status = 'blocked';
    command.cancel();
    expect(command.status).toBe('blocked');
  });
});

// ---------------------------------------------------------------------
// The refusals: a request the run declines, leaving the run untouched.
// ---------------------------------------------------------------------

const LIMITS = {
  crossing_tolerance: 1e-12, subdivisions: 64, bisection_rounds: 64,
  max_crossings: 1000, agreement: 1e-9,
};

function program(): LoadedProgram {
  return loadProgram({
    format: 'solid-node-export',
    version: 5,
    drivers: { crank: { ...float } },
    instructions: {},
    program: {
      identity: 'bench', clock: 'time',
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'wheel.turn': {
          kind: 'coordinate', initial: 0, unit: null, domain: null,
        },
      },
      intermediates: [],
      edges: [{
        kind: 'law', needs: ['crank'], gives: ['wheel.turn'],
        description: 'crank drives wheel.turn', stated_by: 'Bench',
        expressions: ['(2 * crank)'], affine: [true], plans: [null],
      }],
      spans: {},
      sources: { crank: ['crank'], 'wheel.turn': ['crank'] },
      limits: { ...LIMITS },
    },
  } as unknown as RunDocument, 'bench://commands');
}

const run = () => new Run(program(), 0.05, null);

describe('a request the run declines', () => {
  it('refuses a move stating neither by nor to', () => {
    expect(() => run().move('crank', {})).toThrow(/by=|to=/);
  });

  it('refuses a move stating both by and to', () => {
    expect(() => run().move('crank', { by: 1, to: 2 })).toThrow(/by=|to=/);
  });

  it('refuses a duration that is not a whole number of ticks', () => {
    let message = '';
    try {
      run().move('crank', { by: 1, duration: 0.07 });
    } catch (error) {
      message = String(error);
    }
    expect(message).toContain('0.07');
    expect(message).toContain('0.05');
  });

  it('refuses an input that is not a declared one, listing them', () => {
    let message = '';
    try {
      run().move('wheel.turn', { by: 1, duration: 0.05 });
    } catch (error) {
      message = String(error);
    }
    expect(message).toContain('wheel.turn');
    expect(message).toContain('crank');
  });

  it('refuses a second command on an owned input, naming the owner', () => {
    const running = run();
    running.move('crank', { by: 1, duration: 0.1 });
    let message = '';
    try {
      running.move('crank', { by: 1, duration: 0.1 });
    } catch (error) {
      message = String(error);
    }
    expect(message).toContain('crank');
    expect(message).toContain('one owner at a time');
  });

  it('completes an active rate with rate(input, 0), and is otherwise a no-op',
     () => {
       const running = run();
       expect(running.rate('crank', 0)).toBeNull();
       const command = running.rate('crank', 4)!;
       const released = running.rate('crank', 0);
       expect(released).toBe(command);
       expect(command.status).toBe('completed');
       // And the input is free again.
       expect(() => running.rate('crank', 2)).not.toThrow();
     });

  it('refuses an instruction the document does not declare', () => {
    expect(() => run().trigger('Nope')).toThrow(/Nope/);
  });
});
