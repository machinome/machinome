/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// A DRAG is a SERIES of requests, and that is correct (OpenSpec
// `execute-the-commit`, design §13, task 7.4).
//
// Because the executor is synchronous a pointer move cannot interleave
// with another: request N+1 starts from the bank request N left. ADR-128
// closure 1 is what makes this safe -- a request resuming from its own
// landing fires nothing, and a surface reached exactly at an endpoint
// belongs to the request that BEGINS on it -- so no event is skipped and
// none fires twice.
//
// THE EQUIVALENCE IS CLAIMED ONLY WHERE NO CONSTRAINT BINDS, and
// ADR-126 says why: the clip is read ONCE per request. `Gate` is the
// fixture for the difference, and it is asserted here rather than left
// as prose.

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { bindingTable } from '../bindings';
import type { Manifest } from '../types';
import { loadClocked } from './document';
import type { ClockedDocument } from './document';
import { clockedMachine } from './machine';
import type { ClockedMachine } from './machine';

interface Step {
  move?: { input: string; by?: number; to?: number };
  snapshot?: string;
  restore?: string;
  reset?: boolean;
}

interface Machine {
  name: string;
  document: Record<string, unknown>;
  script: Step[];
}

const fixture = JSON.parse(readFileSync(
  new URL('../clocked-corpus.json', import.meta.url), 'utf8')) as {
    machines: Machine[];
  };

function machineOf(entry: Machine): ClockedMachine {
  const document = JSON.parse(JSON.stringify(entry.document));
  const url = `clocked-corpus.json#${entry.name}`;
  return clockedMachine(loadClocked(
    document as ClockedDocument, url,
    bindingTable(document as Manifest, url)));
}

/** Replay one script, splitting each `move` into `parts` consecutive
 * sub-requests over the SAME PATH. `parts === 1` is the script as
 * recorded.
 *
 * Every sub-request is stated as a `to`, and the LAST one is stated as
 * the whole request's own target, so the split covers exactly the path
 * the whole request covers: a sum of `by=travel/parts` would land a
 * float or two short of it, and on an INTEGER driver would re-round at
 * every part -- neither of which is a statement about the solver.
 *
 * A step the whole request REFUSES is skipped in both runs, so the two
 * are compared over the same prefix. */
function replay(entry: Machine, parts: number): Record<string, number> {
  const machine = machineOf(entry);
  const snapshots = new Map<string, ReturnType<ClockedMachine['snapshot']>>();
  for (const step of entry.script) {
    if (step.move !== undefined) {
      const { input } = step.move;
      const declaration = machine.drivers()[input];
      const scale = declaration.scale ?? 1;
      const from = machine.state()[input] * scale;
      const target = step.move.to !== undefined
        ? step.move.to : from + (step.move.by as number);
      // A refusal is not a travel to split: both runs skip it, and the
      // rehearsal is made on a machine of its own so nothing is banked.
      const rehearsal = machineOf(entry);
      rehearsal.restore({
        identity: machine.identity(), bank: machine.state(),
      });
      try {
        rehearsal.move(input, { to: target });
      } catch {
        continue;
      }
      for (let at = 1; at <= parts; at += 1) {
        machine.move(input, {
          to: at === parts ? target : from + (target - from) * (at / parts),
        });
      }
    } else if (step.snapshot !== undefined) {
      snapshots.set(step.snapshot, machine.snapshot());
    } else if (step.restore !== undefined) {
      machine.restore(snapshots.get(
        step.restore) as ReturnType<ClockedMachine['snapshot']>);
    } else if (step.reset === true) {
      machine.reset();
    }
  }
  return machine.state();
}

/** The machines that declare NO constraint and NO clock: the ones the
 * equivalence is claimed over. Derived from the file. */
const unbounded = fixture.machines.filter((entry) => {
  const clocked = entry.document.clocked as {
    bounds: unknown[]; clock: string | null;
  };
  return clocked.bounds.length === 0 && clocked.clock === null;
});

describe('splitting a request where NO constraint binds', () => {
  it('covers the unbounded machines, named -- the 17 that declare no '
     + 'bound, less the two whose only requests move a clock', () => {
    expect(fixture.machines.filter((one) => ((one.document.clocked as {
      bounds: unknown[];
    }).bounds).length === 0)).toHaveLength(17);
    expect(unbounded.map((one) => one.name)).toEqual([
      'Counter', 'KinkedCounter', 'Register', 'Clearer', 'SamePair',
      'SwappedPair', 'UlpPair', 'Strict', 'NonStrict', 'Scaled', 'Rounded',
      'JumpsOnly', 'Ceiling', 'Signed', 'Conflict',
    ]);
  });

  for (const entry of unbounded) {
    it(`leaves the same bank on ${entry.name}`, () => {
      const whole = replay(entry, 1);
      for (const parts of [2, 3, 5]) {
        expect(replay(entry, parts), `${entry.name} in ${parts}`)
          .toEqual(whole);
      }
    });
  }

  it('holds for the machines whose laws read what an earlier event wrote',
     () => {
    // `Counter`, `Register` and `Clearer` are the cases that could go
    // wrong: the events fire at the same landings in the same order, so
    // the bank is the same however the path is cut.
    for (const name of ['Counter', 'Register', 'Clearer']) {
      const entry = fixture.machines.find(
        (one) => one.name === name) as Machine;
      expect(replay(entry, 4), name).toEqual(replay(entry, 1));
    }
  });
});

describe('splitting a request where a constraint DOES bind', () => {
  it('is NOT equivalent, and `Gate` is the recorded difference', () => {
    const entry = fixture.machines.find(
      (one) => one.name === 'Gate') as Machine;
    // ONE request, clipped against the CLOSED gate: 300 admitted.
    const once = machineOf(entry);
    expect(once.move('crank', { by: 1000 }).admitted).toBe(300);
    // TWO requests over the same path: the first commits the opening,
    // and the second is clipped against the bank that opening left.
    const twice = machineOf(entry);
    expect(twice.move('crank', { by: 200 }).admitted).toBe(200);
    expect(twice.move('crank', { by: 800 }).admitted).toBe(800);
    expect(twice.state().crank).toBe(1000);
    expect(once.state().crank).toBe(300);
    // The clip is read ONCE per request: that is the clocked quantum
    // (ADR-126's own rejected alternative), and it is behaviour rather
    // than a rounding difference.
    expect(once.state()).not.toEqual(twice.state());
  });
});
