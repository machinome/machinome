/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The DRAWING of one clocked transition (OpenSpec `play-the-instruction`,
// design §3, §4, §5, §7). Decided in node, where `clockedControls.ts` and
// `bounds.ts` already are: the rule is a rule and not a browser.
//
// The module takes NO machine, which is the structural half of "one
// solve per press" -- the frame loop's collaborator has nothing to solve
// with. The last test here counts the executor's calls to say so.

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { bindingTable } from '../bindings';
import type { Manifest } from '../types';
import { loadClocked } from './document';
import type { ClockedDocument } from './document';
import { clockedMachine } from './machine';
import type { ClockedRequest } from './machine';
import { drawing } from './drawing';

const fixture = JSON.parse(readFileSync(
  new URL('../clocked-corpus.json', import.meta.url), 'utf8')) as {
    machines: { name: string; document: Record<string, unknown> }[];
  };

function corpusMachine(name: string) {
  const found = fixture.machines.find((one) => one.name === name);
  if (found === undefined) throw new Error(`no corpus machine ${name}`);
  const document = JSON.parse(JSON.stringify(found.document)) as
    Record<string, unknown>;
  const url = `clocked-corpus.json#${name}`;
  return clockedMachine(loadClocked(
    document as unknown as ClockedDocument, url,
    bindingTable(document as unknown as Manifest, url)));
}

/** A request shaped exactly as `move` returns one, written by hand so a
 * fraction can be put where a test needs it. */
function request(part: Partial<ClockedRequest> = {}): ClockedRequest {
  return {
    input: 'x',
    by: 10,
    to: null,
    origin: 0,
    end: 10,
    commits: [],
    admitted: 10,
    stops: [],
    ...part,
  };
}

const TWO_COMMITS: ClockedRequest = request({
  commits: [
    { relations: ['a'], fraction: 0.25, value: 2.5, targets: { n: 1 } },
    { relations: ['b'], fraction: 0.75, value: 7.5, targets: { n: 2,
                                                               m: 9 } },
  ],
});

const START = { x: 0, n: 0, m: 0 };

describe('the drawn VALUE is `Ramp`\'s rule', () => {
  it('is linear between the two ends the request reports', () => {
    const drawn = drawing(TWO_COMMITS, START, 4, false);
    expect(drawn.advance(0).value).toBe(0);
    expect(drawn.advance(1).value).toBe(2.5);
    expect(drawn.advance(2).value).toBe(5);
    expect(drawn.advance(3).value).toBe(7.5);
    expect(drawn.advance(4).value).toBe(10);
  });

  it('ends on the request\'s OWN `end`, not a computed approximation of '
     + 'it', () => {
       // 1/3 of a second at a time never sums to 1.0, and the endpoint is
       // contract while the values between are sampling.
       const one = request({ origin: 0.1, end: 0.30000000000000004 });
       const drawn = drawing(one, { x: 0.1 }, 1, false);
       expect(drawn.advance(1).value).toBe(0.30000000000000004);
       expect(drawn.advance(1).value).toBe(one.end);
     });

  it('holds at the origin before the drawing starts and at the end past '
     + 'it', () => {
       const drawn = drawing(TWO_COMMITS, START, 4, false);
       expect(drawn.advance(-1).value).toBe(0);
       expect(drawn.advance(400).value).toBe(10);
       expect(drawn.advance(400).done).toBe(true);
     });
});

describe('the drawn BANK applies every commit the fraction has reached',
         () => {
           it('applies none before the first commit\'s fraction', () => {
             const drawn = drawing(TWO_COMMITS, START, 4, false);
             expect(drawn.advance(0).bank).toEqual({ x: 0, n: 0, m: 0 });
             // Just BEFORE 0.25 of four seconds.
             expect(drawn.advance(0.999).bank.n).toBe(0);
           });

           it('applies a commit AT its own fraction, and not before', () => {
             const drawn = drawing(TWO_COMMITS, START, 4, false);
             expect(drawn.advance(1).bank.n).toBe(1);
             expect(drawn.advance(1).bank.m).toBe(0);
             expect(drawn.advance(2.999).bank.n).toBe(1);
             expect(drawn.advance(3).bank).toEqual({ x: 7.5, n: 2, m: 9 });
           });

           it('reports as MOVED exactly the ids the frame changed', () => {
             const drawn = drawing(TWO_COMMITS, START, 4, false);
             // Frame 0 is measured against where the TREE stands when the
             // drawing begins -- the request's own end, which the machine
             // posed as part of itself -- so frame 0 moves everything the
             // transition will undo.
             expect(drawn.advance(0).moved.sort()).toEqual(['m', 'n', 'x']);
             expect(drawn.advance(0.5).moved).toEqual(['x']);
             expect(drawn.advance(1).moved.sort()).toEqual(['n', 'x']);
             expect(drawn.advance(3).moved.sort()).toEqual(['m', 'n', 'x']);
             expect(drawn.advance(4).moved).toEqual(['x']);
           });

           it('lands on the request\'s end with EVERY commit applied', () => {
             const drawn = drawing(TWO_COMMITS, START, 4, false);
             const last = drawn.advance(4);
             expect(last.done).toBe(true);
             expect(last.bank).toEqual({ x: 10, n: 2, m: 9 });
           });
         });

describe('the drawing lands ON the machine\'s own bank', () => {
  it('is the same values, id for id, for a real request', () => {
    const machine = corpusMachine('Pawl');
    const start = machine.state();
    const answered = machine.move('crank', { by: 1100 });
    const drawn = drawing(answered, start, 2, false);
    const last = drawn.advance(2);
    expect(last.bank).toEqual(machine.state());
    expect(last.value).toBe(machine.state().crank);
  });

  it('and `land()` from ANY point gives that same frame', () => {
    const machine = corpusMachine('Pawl');
    const start = machine.state();
    const answered = machine.move('crank', { by: 1100 });
    const drawn = drawing(answered, start, 2, false);
    drawn.advance(0.3);
    const landed = drawn.land();
    expect(landed.done).toBe(true);
    expect(landed.bank).toEqual(machine.state());
    expect(landed.value).toBe(answered.end);
  });
});

describe('a DOWNWARD transition is drawn by the same rule', () => {
  const falling = request({
    by: -10,
    origin: 10,
    end: 0,
    admitted: -10,
    commits: [
      { relations: ['a'], fraction: 0.25, value: 7.5, targets: { n: 1 } },
      { relations: ['b'], fraction: 0.75, value: 2.5, targets: { n: 2 } },
    ],
  });

  it('falls linearly and applies its commits at the same fractions', () => {
    const drawn = drawing(falling, { x: 10, n: 0 }, 4, false);
    expect(drawn.advance(0).value).toBe(10);
    expect(drawn.advance(1).value).toBe(7.5);
    expect(drawn.advance(1).bank.n).toBe(1);
    expect(drawn.advance(2.999).bank.n).toBe(1);
    expect(drawn.advance(3).bank.n).toBe(2);
    expect(drawn.advance(4).value).toBe(0);
    expect(drawn.advance(4).bank).toEqual({ x: 0, n: 2 });
  });
});

describe('a WHOLE-NUMBER input is whole at every frame', () => {
  it('rises by whole units and lands exactly on the end', () => {
    const rising = request({ origin: 0, end: 7, by: 7, admitted: 7 });
    const drawn = drawing(rising, { x: 0 }, 7, true);
    const seen: number[] = [];
    for (let at = 0; at <= 70; at += 1) seen.push(drawn.advance(at / 10).value);
    for (const value of seen) expect(Number.isInteger(value)).toBe(true);
    expect(Math.max(...seen)).toBe(7);
    expect(seen[seen.length - 1]).toBe(7);
  });

  it('never passes the end the machine reported, FALLING -- which is the '
     + 'one place this differs from `Ramp`\'s floor', () => {
       const falling = request({ origin: 7, end: 0, by: -7, admitted: -7 });
       const drawn = drawing(falling, { x: 7 }, 7, true);
       const seen: number[] = [];
       for (let at = 0; at <= 70; at += 1) {
         seen.push(drawn.advance(at / 10).value);
       }
       for (const value of seen) {
         expect(Number.isInteger(value)).toBe(true);
         expect(value).toBeGreaterThanOrEqual(0);
         expect(value).toBeLessThanOrEqual(7);
       }
       // `Ramp`'s own `Math.floor(delta)` would have gone to -1 here:
       // floor(-0.1) is -1, and 7 + (-1) is 6 at a tenth of a second --
       // fine -- but at the last sample before the end floor(-6.9) is -7
       // while a further tenth gives floor(-7.0) = -7, and a FALLING ramp
       // whose delta is not exact overshoots. Truncating toward the
       // origin cannot.
       expect(seen[seen.length - 1]).toBe(0);
     });
});

describe('the degenerate transitions', () => {
  it('lands a duration of ZERO in one frame', () => {
    const drawn = drawing(TWO_COMMITS, START, 0, false);
    const first = drawn.advance(0);
    expect(first.done).toBe(true);
    expect(first.value).toBe(10);
    expect(first.bank).toEqual({ x: 10, n: 2, m: 9 });
  });

  it('draws NOTHING for a request admitted at zero travel', () => {
    const held = request({ by: 1, origin: 0, end: 0, admitted: 0 });
    const drawn = drawing(held, { x: 0 }, 2, false);
    expect(drawn.advance(0).moved).toEqual([]);
    expect(drawn.advance(1).moved).toEqual([]);
    expect(drawn.advance(1).value).toBe(0);
  });

  it('lands a ZERO-SPAN request\'s `fraction: 1` commits at the end', () => {
    // The producer's own rule for a span of zero (`machine.ts`'s
    // `span === 0 ? 1 : …`): such a commit belongs at the end of the
    // drawing, which is where a zero-span drawing begins and ends.
    const zero = request({
      origin: 5,
      end: 5,
      admitted: 0,
      commits: [{ relations: ['a'], fraction: 1, value: 5,
                  targets: { n: 3 } }],
    });
    const drawn = drawing(zero, { x: 5, n: 0 }, 2, false);
    expect(drawn.advance(0).bank.n).toBe(0);
    expect(drawn.advance(1.999).bank.n).toBe(0);
    expect(drawn.advance(2).bank.n).toBe(3);
    expect(drawn.advance(2).done).toBe(true);
  });
});

describe('ONE SOLVE per press, structurally', () => {
  it('advances two hundred frames with no machine in scope at all', () => {
    const machine = corpusMachine('Calculator');
    let solves = 0;
    const counted = {
      ...machine,
      move: (input: string, one: { by?: number; to?: number }) => {
        solves += 1;
        return machine.move(input, one);
      },
      trigger: (name: string) => {
        solves += 1;
        return machine.trigger(name);
      },
    };
    const start = counted.state();
    const answered = counted.trigger('Stroke');
    expect(solves).toBe(1);
    // The drawing takes the REQUEST, the bank before it and the duration.
    // It is handed no machine, so there is nothing for it to call.
    const drawn = drawing(answered, start, 2, false);
    for (let at = 0; at <= 200; at += 1) drawn.advance(at * 0.01);
    drawn.land();
    expect(solves).toBe(1);
    expect(drawn.land().bank).toEqual(counted.state());
  });
});
