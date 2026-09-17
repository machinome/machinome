/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// ONE REQUEST: the commit, the request loop, the session and the
// refusals (OpenSpec `execute-the-commit`, design §7, §9, §11, §12).

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { bindingTable } from '../bindings';
import type { Manifest } from '../types';
import { halfToEven } from './commit';
import { loadClocked } from './document';
import type { ClockedDocument, LoadedMachine } from './document';
import { clockedMachine } from './machine';
import type { ClockedMachine } from './machine';

const fixture = JSON.parse(readFileSync(
  new URL('../clocked-corpus.json', import.meta.url), 'utf8')) as {
    machines: { name: string; document: Record<string, unknown> }[];
  };

function loaded(document: Record<string, unknown>): LoadedMachine {
  const url = 'machine.json';
  return loadClocked(document as unknown as ClockedDocument, url,
                     bindingTable(document as unknown as Manifest, url));
}

function corpusMachine(name: string): ClockedMachine {
  const found = fixture.machines.find((one) => one.name === name);
  if (found === undefined) throw new Error(`no corpus machine ${name}`);
  return clockedMachine(loaded(
    JSON.parse(JSON.stringify(found.document)) as Record<string, unknown>));
}

const FREE = { default: 0, range: null, unit: null, dtype: null, scale: null };
const COUNT = {
  default: 0, range: null, unit: null, dtype: 'int', scale: null,
};

function handMade(law: string, states: Record<string, unknown> = { n: COUNT },
                  targets: string[] = ['n']): ClockedMachine {
  return clockedMachine(loaded({
    format: 'solid-node-export',
    version: 8,
    drivers: { x: FREE },
    states,
    instructions: {},
    bindings: [],
    clocked: {
      identity: 'hand-written',
      clock: null,
      own: '_own',
      commits: [{
        sources: ['x', ...Object.keys(states)],
        targets,
        at: { primitive: 'floor', level: '(x / 1.0)' },
        law: targets.map(() => law),
        shapes: { x: 'affine' },
        description: '(x, n) commits n',
        stated_by: 'Hand',
      }],
      bounds: [],
      limits: { crossing_tolerance: 1e-12, max_crossings: 1000 },
    },
  }));
}

// ---------------------------------------------------------------------
// The COMMIT (design §7)
// ---------------------------------------------------------------------

describe('halfToEven, the rounding an integer state takes', () => {
  it('is Python\'s `round` and not `Math.round`', () => {
    // Hand-computed from the rule: a half goes to the EVEN neighbour.
    // `Math.round`'s own answers are quoted beside each, and four of the
    // six differ.
    expect(halfToEven(0.5)).toBe(0); // Math.round(0.5) === 1
    expect(halfToEven(1.5)).toBe(2); // Math.round(1.5) === 2
    expect(halfToEven(2.5)).toBe(2); // Math.round(2.5) === 3
    expect(halfToEven(-0.5)).toBe(0); // Math.round(-0.5) === -0
    expect(halfToEven(-1.5)).toBe(-2); // Math.round(-1.5) === -1
    expect(halfToEven(-2.5)).toBe(-2); // Math.round(-2.5) === -2
    expect(halfToEven(3.5)).toBe(4); // Math.round(3.5) === 4
    expect(halfToEven(4.5)).toBe(4); // Math.round(4.5) === 5
  });

  it('returns an INT, which has no negative zero', () => {
    // Python's `round` returns an int and `int` has no signed zero:
    // `round(-0.5)` is `0`. Normalising here is what keeps a banked
    // value comparable under `Object.is`.
    expect(Object.is(halfToEven(-0.5), -0)).toBe(false);
    expect(Object.is(halfToEven(-0.4), -0)).toBe(false);
    expect(Object.is(Math.round(-0.5), -0)).toBe(true);
  });

  it('leaves a value that is not a half alone', () => {
    expect(halfToEven(2.4)).toBe(2);
    expect(halfToEven(2.6)).toBe(3);
    expect(halfToEven(-2.4)).toBe(-2);
    expect(halfToEven(-2.6)).toBe(-3);
  });
});

describe('the commit', () => {
  it('evaluates the published law over the PRE-EVENT bank', () => {
    const machine = handMade('(n + 1)');
    const request = machine.move('x', { by: 3 });
    // Each event reads the bank as it stood BEFORE it, so the counter
    // walks one at a time rather than reading its own new value.
    expect(request.commits.map((one) => one.targets.n)).toEqual([1, 2, 3]);
  });

  it('rounds an `int` target half to EVEN, once, and scales nothing', () => {
    // `Scaled` declares a state of `scale: 10.0` and a law whose value
    // is the literal 4.0: a commit law READS native values and RETURNS
    // native ones, so nothing is divided by the scale.
    const scaled = corpusMachine('Scaled');
    scaled.move('crank', { by: 400 });
    expect(scaled.state().value).toBe(4);
    // `Calculator`'s `halved` is the corpus's one law that lands an
    // integer state exactly halfway: `((floor(feed/100) * 2) + 1) / 2`
    // is 0.5, 1.5, 2.5 … and half to EVEN walks it 0, 2, 2, 4 where
    // `Math.round` would walk it 1, 2, 3, 4. The corpus's own
    // `move('feed', by=350)` records three commits, 2, 2, 4.
    const calculator = corpusMachine('Calculator');
    const request = calculator.move('feed', { by: 350 });
    expect(request.commits.map((one) => one.targets.halved))
      .toEqual([2, 2, 4]);
  });

  it('coerces a law whose top node is a COMPARISON to a number', () => {
    // `n` starts at 0, so the law reads 1, 1, 1 at the first three
    // events and then 0 once `n` has reached 1 and `x` has passed it --
    // the point being that a BOOLEAN is banked as a number at all.
    const machine = handMade('(n < 1)');
    const request = machine.move('x', { by: 3 });
    expect(request.commits.map((one) => one.targets.n)).toEqual([1, 0, 1]);
  });

  it('REFUSES a non-finite commit, and commits nothing', () => {
    // A document cannot express a raise (ADR-128 §16, and the
    // framework's own follow-up of 2026-09-17): a consumer that computes
    // a non-finite commit value refuses the request rather than banking
    // it.
    const machine = handMade('(1.0 / n)');
    const before = machine.state();
    let caught: { kind?: string; message?: string } = {};
    expect(() => {
      try {
        machine.move('x', { by: 3 });
      } catch (error) {
        caught = error as { kind?: string; message?: string };
        throw error;
      }
    }).toThrow();
    expect(caught.kind).toBe('ClockedError');
    expect(caught.message).toContain('not a value a machine can stand at');
    expect(machine.state()).toEqual(before);
  });
});

// ---------------------------------------------------------------------
// The REQUEST (design §6, §7)
// ---------------------------------------------------------------------

describe('one request', () => {
  it('converts `by` and `to` through the driver\'s scale and dtype, and '
     + 'reports the admitted travel back in DESIGN units', () => {
    // `ScaledStroke`'s `move('lift', by=30)` on a `scale: 0.5` driver
    // travels 60 native units, is clipped at native 9, and reports
    // `admitted: 4.5`.
    const scaled = corpusMachine('ScaledStroke');
    const request = scaled.move('lift', { by: 30 });
    expect(request.admitted).toBe(4.5);
    expect(scaled.state().lift).toBe(9);
    // `Calculator`'s `move('operand', to=4)` on an `int` driver standing
    // at 1 reports `admitted: 3`.
    const calculator = corpusMachine('Calculator');
    expect(calculator.move('operand', { to: 4 }).admitted).toBe(3);
  });

  it('resumes the solve from each landing, so a surface that reads a '
     + 'committed state moves with it', () => {
    // `Counter`'s tens digit is written by a law reading the units digit
    // the SAME event wrote: ten events on one path, and the carry lands
    // where the bank says it does.
    const counter = corpusMachine('Counter');
    const request = counter.move('crank', { by: 3700 });
    expect(request.commits).toHaveLength(10);
    expect(counter.state()).toEqual({ crank: 3700, units: 0, tens: 1 });
  });

  it('is ONE event where two relations land on the SAME float', () => {
    const same = corpusMachine('SamePair');
    const request = same.move('crank', { by: 400 });
    expect(request.commits).toHaveLength(1);
    expect(request.commits[0].relations).toHaveLength(2);
    // ... and TWO where their landings are one representable value
    // apart, which is what `UlpPair` is built on.
    const ulp = corpusMachine('UlpPair');
    expect(ulp.move('crank', { by: 400 }).commits).toHaveLength(2);
  });

  it('REFUSES two relations writing one state at one landing', () => {
    const machine = corpusMachine('Conflict');
    const before = machine.state();
    let caught: { kind?: string; message?: string } = {};
    try {
      machine.move('crank', { by: 200 });
    } catch (error) {
      caught = error as { kind?: string; message?: string };
    }
    expect(caught.kind).toBe('ClockedError');
    expect(caught.message).toContain('written by two committing relations');
    expect(machine.state()).toEqual(before);
  });

  it('REFUSES a path crossing more surfaces than the machine admits', () => {
    const machine = corpusMachine('Counter');
    const before = machine.state();
    let caught: { kind?: string } = {};
    try {
      machine.move('crank', { by: 400000 });
    } catch (error) {
      caught = error as { kind?: string };
    }
    expect(caught.kind).toBe('TooManyEvents');
    expect(machine.state()).toEqual(before);
  });

  it('never poses a refused request: the bank stands exactly as it did',
     () => {
    // ATOMICITY, proved from the outside: the bank before and after a
    // refusal, id for id -- the pose included, which the `pose` hook
    // observes.
    const posed: Record<string, number>[] = [];
    const found = fixture.machines.find((one) => one.name === 'Shut');
    const machine = clockedMachine(
      loaded(JSON.parse(JSON.stringify(
        (found as { document: unknown }).document)) as Record<string, unknown>),
      { pose: (bank) => { posed.push({ ...bank }); } });
    const before = machine.state();
    expect(() => machine.move('crank', { by: 1000 })).toThrow();
    expect(machine.state()).toEqual(before);
    expect(posed).toEqual([]);
  });

  it('poses the bank BEFORE assigning it, so a refused pose stands too',
     () => {
    const machine = clockedMachine(loaded({
      format: 'solid-node-export',
      version: 8,
      drivers: { x: FREE },
      states: { n: COUNT },
      instructions: {},
      bindings: [],
      clocked: {
        identity: 'hand-written',
        clock: null,
        own: '_own',
        commits: [{
          sources: ['x', 'n'],
          targets: ['n'],
          at: { primitive: 'floor', level: '(x / 1.0)' },
          law: ['(n + 1)'],
          shapes: { x: 'affine' },
          description: '(x, n) commits n',
          stated_by: 'Hand',
        }],
        bounds: [],
        limits: { crossing_tolerance: 1e-12, max_crossings: 1000 },
      },
    }), { pose: () => { throw new Error('the tree refused'); } });
    const before = machine.state();
    expect(() => machine.move('x', { by: 3 })).toThrow('the tree refused');
    expect(machine.state()).toEqual(before);
  });
});

// ---------------------------------------------------------------------
// The SESSION (design §12)
// ---------------------------------------------------------------------

describe('the session', () => {
  it('snapshots, restores and resets the bank', () => {
    const machine = corpusMachine('Counter');
    machine.move('crank', { by: 3700 });
    const taken = machine.snapshot();
    machine.move('crank', { by: -800 });
    expect(machine.state().crank).toBe(2900);
    machine.restore(taken);
    expect(machine.state()).toEqual({ crank: 3700, units: 0, tens: 1 });
    machine.reset();
    expect(machine.state()).toEqual({ crank: 0, units: 0, tens: 0 });
  });

  it('refuses a snapshot taken against ANOTHER machine, by identity', () => {
    const counter = corpusMachine('Counter');
    const register = corpusMachine('Register');
    let caught: { kind?: string; message?: string } = {};
    try {
      counter.restore(register.snapshot());
    } catch (error) {
      caught = error as { kind?: string; message?: string };
    }
    expect(caught.kind).toBe('ValueError');
    expect(caught.message).toContain('A snapshot restores into the machine');
    expect(counter.identity()).not.toBe(register.identity());
  });
});

// ---------------------------------------------------------------------
// The REFUSALS, and the KINDS the corpus pins them by (design §11)
// ---------------------------------------------------------------------

describe('a request this machine has no meaning for', () => {
  it('refuses an input it does not declare', () => {
    const machine = corpusMachine('Counter');
    let caught: { kind?: string; message?: string } = {};
    try {
      machine.move('handle', { by: 1 });
    } catch (error) {
      caught = error as { kind?: string; message?: string };
    }
    expect(caught.kind).toBe('ValueError');
    expect(caught.message).toContain('names no declared driver');
  });

  it('refuses a STATE named as an input', () => {
    const machine = corpusMachine('Counter');
    expect(() => machine.move('tens', { by: 1 })).toThrow(/names a State/);
  });

  it('refuses `by` and `to` together, or neither', () => {
    const machine = corpusMachine('Counter');
    expect(() => machine.move('crank', { by: 1, to: 2 }))
      .toThrow(/exactly one of by=/);
    expect(() => machine.move('crank', {})).toThrow(/exactly one of by=/);
  });

  it('refuses a request on the CLOCK by name, and loads the document all '
     + 'the same (design §9)', () => {
    const machine = corpusMachine('Regulator');
    expect(machine.clock()).toBe('time');
    // The bank STANDS at the initial instant, which is a real instant of
    // the machine: the document is not refused, only the one gesture.
    expect(machine.state()).toEqual({ engaged: 1, count: 0, time: 0 });
    let caught: { kind?: string; message?: string } = {};
    try {
      machine.move('time', { by: 5 });
    } catch (error) {
      caught = error as { kind?: string; message?: string };
    }
    expect(caught.kind).toBe('ValueError');
    expect(caught.message).toContain('clock to advance');
    expect(machine.state()).toEqual({ engaged: 1, count: 0, time: 0 });
    // Every ORDINARY request on an elapsed machine is taken.
    const lift = corpusMachine('Lift');
    expect(() => lift.move('lift', { by: 1 })).not.toThrow();
  });

  it('refuses the cadence verbs by name (design §4)', () => {
    const machine = corpusMachine('Counter');
    expect(() => machine.trigger('go')).toThrow(/NO runtime meaning/);
    expect(() => machine.step()).toThrow(/has no cadence/);
    expect(() => machine.rate('crank', 1)).toThrow(/no cadence for one/);
  });

  it('carries the four KINDS the corpus records', () => {
    // The corpus records a refused step as `{kind, names}` and nothing
    // else, so the kind is a FIELD of the error rather than its prose.
    const kinds = new Set<string>();
    for (const [name, act] of [
      ['Counter', (one: ClockedMachine) => one.move('crank', { by: 400000 })],
      ['Conflict', (one: ClockedMachine) => one.move('crank', { by: 200 })],
      ['Shut', (one: ClockedMachine) => one.move('crank', { by: 1000 })],
      ['Regulator', (one: ClockedMachine) => one.move('time', { by: 5 })],
    ] as [string, (one: ClockedMachine) => unknown][]) {
      try {
        act(corpusMachine(name));
      } catch (error) {
        kinds.add((error as { kind: string }).kind);
      }
    }
    expect([...kinds].sort()).toEqual(
      ['ClockedError', 'JointRangeError', 'TooManyEvents', 'ValueError']);
  });
});
