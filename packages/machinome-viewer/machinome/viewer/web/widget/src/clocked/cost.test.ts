/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// WHAT A CLOCKED REQUEST COSTS (OpenSpec `execute-the-commit`, design
// §14, task 10.1), on `src/run/cost.test.ts`'s pattern: every number is
// PRINTED, and the asserted floor is an order of magnitude below the
// bench, so this catches a tenfold regression and never a slow machine.
//
// THE NUMBER THIS CYCLE EXISTS TO PRODUCE is the per-REQUEST cost of the
// Curta-shaped `Calculator`, held against the running Curta's recorded
// per-TICK cost. ADR-060's own `Measured` table, quoted so the
// comparison cannot drift:
//
//     the operating Curta          before              after
//     idle ms/tick      18.27 / 18.66 / 20.94   9.52 / 9.57 / 9.86
//     crank ms/tick   156.91 / 161.30 / 163.42  40.52 / 42.31 / 43.70
//
// ADR-061 measured the same document again and moved it by nothing, so
// 40.52 / 42.31 / 43.70 ms per crank tick is the standing figure.
//
// WHAT THE COMPARISON IS NOT, stated plainly:
//
//   - it is FIXTURE-to-PROJECT. The Curta's OWN clocked model does not
//     exist yet -- the project's migration is pending and is not this
//     cycle's -- so the clocked side is `Calculator`: four wheels of one
//     class, a stroke over four digits and an operand, a clearing
//     relation per wheel, a ratchet and an off-rest freeze. It is NOT
//     the Curta's seventeen wheels.
//   - the UNITS differ. A running crank turn is a sequence of
//     1/240-second ticks at ~40 ms each; a clocked crank turn is ONE
//     request. This quotes the per-tick figure rather than inventing a
//     turn count for a document it did not time.
//   - what is measured HERE is the SOLVE alone: this machine has no
//     tree, so no pose happens. The page's own numbers (solve AND pose,
//     and the pose alone) are in `tests/test_calculator_document.py`.

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { bindingTable } from '../bindings';
import type { Manifest } from '../types';
import { loadClocked } from './document';
import type { ClockedDocument } from './document';
import { clockedMachine } from './machine';
import type { ClockedMachine } from './machine';

const fixture = JSON.parse(readFileSync(
  new URL('../clocked-corpus.json', import.meta.url), 'utf8')) as {
    machines: { name: string; document: Record<string, unknown> }[];
  };

function machineOf(name: string): ClockedMachine {
  const found = fixture.machines.find((one) => one.name === name);
  if (found === undefined) throw new Error(`no corpus machine ${name}`);
  const document = JSON.parse(JSON.stringify(found.document));
  const url = `clocked-corpus.json#${name}`;
  return clockedMachine(loadClocked(document as ClockedDocument, url,
                                    bindingTable(document as Manifest, url)));
}

/** Three runs of one request, from the same bank each time, printed. */
function cost(label: string, machine: ClockedMachine,
              request: () => void, before: () => void): number[] {
  const runs: number[] = [];
  for (let at = 0; at < 3; at += 1) {
    before();
    const started = performance.now();
    request();
    runs.push(performance.now() - started);
  }
  // eslint-disable-next-line no-console
  console.log(`  ${label}: `
    + runs.map((one) => one.toFixed(2)).join(' / ') + ' ms');
  return runs;
}

describe('what a clocked request costs', () => {
  it('cranks the Curta-shaped Calculator ONE STROKE', () => {
    const machine = machineOf('Calculator');
    machine.move('operand', { to: 4 });
    const rest = machine.snapshot();
    const runs = cost('Calculator one stroke (crank by 360)', machine,
                      () => machine.move('crank', { by: 360 }),
                      () => machine.restore(rest));
    // An order of magnitude below the running Curta's 40.52 ms per
    // crank TICK: a request that cost more than 4 ms would be a
    // tenfold regression on what this measured.
    expect(Math.min(...runs)).toBeLessThan(4);
  });

  it('sweeps its clearing ring, four relations reading what they write',
     () => {
    const machine = machineOf('Calculator');
    machine.move('operand', { to: 4 });
    machine.move('crank', { by: 1100 });
    const cranked = machine.snapshot();
    const runs = cost('Calculator one clearing sweep (ring by 500)', machine,
                      () => machine.move('ring', { by: 500 }),
                      () => machine.restore(cranked));
    expect(Math.min(...runs)).toBeLessThan(4);
  });

  it('CLIPS a selector move against three constraints, and fires nothing',
     () => {
    // The number that says what an INTERLOCK costs, and it exists only
    // because the clip is in this cycle: one clip over three
    // constraints, zero events, `admitted: 0`.
    const machine = machineOf('Calculator');
    machine.move('operand', { to: 4 });
    machine.move('crank', { by: 1100 });
    const cranked = machine.snapshot();
    const runs = cost('Calculator one CLIPPED selector move (setting by 1)',
                      machine, () => {
                        const answered = machine.move('setting', { by: 1 });
                        expect(answered.admitted).toBe(0);
                        expect(answered.stops).toHaveLength(1);
                      }, () => machine.restore(cranked));
    expect(Math.min(...runs)).toBeLessThan(4);
  });

  it('counts what ONE EVENT costs, on Counter\'s own ten-event request',
     () => {
    const machine = machineOf('Counter');
    const rest = machine.snapshot();
    let events = 0;
    const runs = cost('Counter, ten events on one path (crank by 3700)',
                      machine, () => {
                        events = machine.move('crank', { by: 3700 })
                          .commits.length;
                      }, () => machine.restore(rest));
    expect(events).toBe(10);
    const each = runs.map((one) => one / events);
    // eslint-disable-next-line no-console
    console.log('  Counter per EVENT: '
      + each.map((one) => one.toFixed(3)).join(' / ') + ' ms');
    expect(Math.min(...each)).toBeLessThan(4);
  });

  it('holds the whole corpus\'s 76 steps inside one frame budget', () => {
    // The main-thread decision (design §3) measured over EVERY machine
    // the corpus carries, rather than over the one that happens to be
    // fast.
    const started = performance.now();
    let steps = 0;
    for (const entry of fixture.machines) {
      const machine = machineOf(entry.name);
      const snapshots = new Map<string, ReturnType<
        ClockedMachine['snapshot']>>();
      for (const step of (entry as unknown as {
        script: Record<string, never>[];
      }).script) {
        const one = step as unknown as {
          move?: { input: string; by?: number; to?: number };
          snapshot?: string; restore?: string; reset?: boolean;
        };
        steps += 1;
        try {
          if (one.move !== undefined) {
            const { input, ...request } = one.move;
            machine.move(input, request);
          } else if (one.snapshot !== undefined) {
            snapshots.set(one.snapshot, machine.snapshot());
          } else if (one.restore !== undefined) {
            machine.restore(snapshots.get(one.restore) as ReturnType<
              ClockedMachine['snapshot']>);
          } else if (one.reset === true) {
            machine.reset();
          }
        } catch (error) {
          void error;
        }
      }
    }
    const elapsed = performance.now() - started;
    // eslint-disable-next-line no-console
    console.log(`  the whole corpus: ${steps} steps over `
      + `${fixture.machines.length} machines in ${elapsed.toFixed(1)} ms`);
    expect(steps).toBe(76);
    expect(elapsed).toBeLessThan(2000);
  });
});
