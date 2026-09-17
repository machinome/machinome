/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The CLOCKED conformance corpus (design §15, ADR-128).
// `src/clocked-corpus.json` is solid-node's `tests/clocked-corpus.json`,
// copied BYTE FOR BYTE from branch `clocked-machine` -- taken at head
// `1a959d3`, which is one follow-up commit past the `2d2dc2b` the design
// records and leaves the file byte-identical (139 262 bytes, md5
// `852b86b804ebd785f6e6b1f5568fb01a`, `tools/generate_clocked_corpus.py`
// regenerates it unchanged). The numbers in it are the framework's,
// produced by the framework's own clocked executor and never recomputed
// a second way.
//
// **Agreement is EXACT, bit for bit.** That is the one substantive
// difference from the running corpus, which compares floats within the
// run's own `1e-9`. A clocked executor has no such window: every event
// is SOLVED by division and two relations are ONE event exactly when
// their landings are the SAME float, so a consumer agreeing only within
// a tolerance would merge events this framework keeps apart. The file
// carries `"tolerance": {"float": 0.0}` so the claim is a field of the
// file and not a convention of its reader, and this suite READS it.
//
// A DISAGREEMENT IS A BUG IN THIS ENGINE. Not a tolerance to widen, not
// a scenario to skip, not a fixture to edit.
//
// NO DEPARTURE AND NO DEFERRAL. Cycle 5 left one of each -- a request
// that moves the CLOCK, which that build refused -- and this cycle
// executes them: all 76 steps of all 30 machines, all 722 recorded
// numbers, `Regulator`, `Lift` and `ClockAlone` included. The census at
// the foot of this file is read off the replay ITSELF, so a later build
// cannot narrow the suite by declaring a departure without failing
// there; the census at the head is derived from the FILE, so a corpus
// regenerated wider or narrower is loud without anyone running the
// producer's generator.

import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { bindingTable } from '../bindings';
import type { Manifest } from '../types';
import { loadClocked } from './document';
import { clockedMachine } from './machine';
import type { ClockedMachine, ClockedSnapshot } from './machine';

interface CorpusMove {
  input: string;
  by?: number;
  to?: number;
}

interface CorpusStep {
  move?: CorpusMove;
  snapshot?: string;
  restore?: string;
  reset?: boolean;
}

interface CorpusCommit {
  relations: string[];
  fraction: number;
  value: number;
  targets: Record<string, number>;
}

interface CorpusStop {
  coordinate: string;
  side: string;
  bound: number;
  value: number;
  input: number;
  fraction: number;
}

interface CorpusRequest {
  bank: Record<string, number>;
  admitted?: number;
  commits?: CorpusCommit[];
  stops?: CorpusStop[];
  refused?: { kind: string; names: string[] };
}

interface CorpusMachine {
  name: string;
  document: Record<string, unknown>;
  script: CorpusStep[];
  requests: CorpusRequest[];
}

interface Corpus {
  generated_by: string;
  corpus: string;
  tolerance: { float: number };
  machines: CorpusMachine[];
}

// Read from the FILE and parsed here, never imported as a module: the
// bundler's JSON import round-trips the file through `JSON.stringify`,
// which turns `-0.0` into `0` -- and `Standing`'s recorded stop fraction
// IS `-0.0`, which `Object.is` distinguishes. A browser reading a real
// document goes through `Response.json()`, which preserves it, so the
// hazard is the test harness's alone; reading the bytes is what keeps
// the suite comparing what the producer wrote.
const CORPUS_BYTES = readFileSync(
  new URL('../clocked-corpus.json', import.meta.url));

const fixture = JSON.parse(CORPUS_BYTES.toString('utf8')) as Corpus;

/** The corpus's OWN tolerance, read from the fixture and never from a
 * constant here. It is ZERO, and every comparison below is `toBe` --
 * `Object.is`, which tells `-0` from `0`, as `Standing`'s recorded stop
 * fraction requires. */
const FLOAT = fixture.tolerance.float;

/** The steps of a machine's script that move its OWN clock, found by the
 * document's `clocked.clock` field and never by a list of names. These
 * are the steps this build EXECUTES like any other (design §11). */
function clockMoves(entry: CorpusMachine): number[] {
  const clocked = (entry.document.clocked ?? {}) as { clock?: string | null };
  const clock = clocked.clock ?? null;
  if (clock === null) return [];
  const found: number[] = [];
  entry.script.forEach((step, index) => {
    if (step.move !== undefined && step.move.input === clock) found.push(index);
  });
  return found;
}

/** Every number nested anywhere inside a recorded request. */
function numbersIn(value: unknown): number {
  if (typeof value === 'boolean') return 0;
  if (typeof value === 'number') return 1;
  if (Array.isArray(value)) {
    return value.reduce((total: number, one) => total + numbersIn(one), 0);
  }
  if (typeof value === 'object' && value !== null) {
    return Object.values(value)
      .reduce((total: number, one) => total + numbersIn(one), 0);
  }
  return 0;
}

/** What the replay below ACTUALLY compared, accumulated by `replayStep`
 * itself. The closing census at the foot of this file reads it, so the
 * claim "every step is replayed" is derived from the replay rather than
 * asserted beside it: a step skipped, departed from or deferred moves
 * these numbers and fails there. */
const compared = { machines: new Set<string>(), steps: 0, numbers: 0 };

function machineOf(entry: CorpusMachine): ClockedMachine {
  const url = `clocked-corpus.json#${entry.name}`;
  const document = entry.document as unknown as Manifest;
  return clockedMachine(
    loadClocked(document, url, bindingTable(document, url)));
}

function exactly(found: unknown, want: unknown, where: string): void {
  expect(found, where).toBe(want);
}

describe('the clocked corpus', () => {
  it('states exactness as a field of its own', () => {
    expect(fixture.tolerance).toEqual({ float: 0 });
    expect(FLOAT).toBe(0);
    expect(fixture.generated_by).toBe('tools/generate_clocked_corpus.py');
    expect(fixture.corpus).toBe('tests/clocked_project/');
  });

  it('is the producer\'s file, byte for byte', () => {
    expect(CORPUS_BYTES.length).toBe(139262);
    expect(createHash('md5').update(CORPUS_BYTES).digest('hex'))
      .toBe('852b86b804ebd785f6e6b1f5568fb01a');
  });

  it('carries a NEGATIVE ZERO, which the reader must preserve', () => {
    // The one value in the file that a `JSON.stringify` round trip
    // destroys, and the reason this suite reads bytes rather than
    // importing the module.
    const standing = fixture.machines.find((one) => one.name === 'Standing');
    const fraction = (standing as CorpusMachine)
      .requests[0].stops?.[0].fraction;
    expect(Object.is(fraction, -0)).toBe(true);
  });

  it('carries thirty machines, every one of them version 8', () => {
    expect(fixture.machines.length).toBe(30);
    for (const entry of fixture.machines) {
      expect(entry.document.version, entry.name).toBe(8);
      expect(entry.document.clocked, entry.name).toBeDefined();
      expect(entry.document.states, entry.name).toBeDefined();
      expect(entry.document.program, entry.name).toBeUndefined();
      expect(entry.requests.length, entry.name).toBe(entry.script.length);
    }
  });
});

// ---------------------------------------------------------------------
// The CENSUS (design §15). Derived from the file -- a `move` whose input
// is that machine's own `clocked.clock` -- and never from a list here,
// so a corpus regenerated wider or narrower is loud without anyone
// running the generator.
// ---------------------------------------------------------------------

describe('the census this build claims', () => {
  const steps = fixture.machines.reduce(
    (total, entry) => total + entry.script.length, 0);
  const clocked = fixture.machines
    .filter((entry) => clockMoves(entry).length > 0);

  it('is 76 steps over 30 machines', () => {
    expect(fixture.machines.length).toBe(30);
    expect(steps).toBe(76);
  });

  it('names the three machines that move a clock, off the file', () => {
    expect(clocked.map((entry) => entry.name).sort())
      .toEqual(['ClockAlone', 'Lift', 'Regulator']);
    // Every one of them moves its clock at its FIRST step -- which this
    // build EXECUTES, so everything downstream of it is compared too.
    for (const entry of clocked) expect(clockMoves(entry)[0]).toBe(0);
  });

  it('carries 722 recorded numbers in all', () => {
    let recorded = 0;
    for (const entry of fixture.machines) {
      for (const request of entry.requests) recorded += numbersIn(request);
    }
    expect(recorded).toBe(722);
  });

  it('counts the 13 machines whose interlocks this build must execute',
     () => {
       const bounded = fixture.machines.filter((entry) => (
         ((entry.document.clocked as { bounds: unknown[] }).bounds).length > 0));
       expect(bounded.length).toBe(13);
       expect(bounded.reduce((total, entry) => total + entry.script.length, 0))
         .toBe(36);
     });

  it('is derived from the file: a machine added to it is counted', () => {
    // Task 1.3, in the suite rather than only in a scratch copy: the
    // census reads the file, so a corpus that grew a machine moves these
    // numbers instead of quietly replaying fewer.
    const widened = JSON.parse(JSON.stringify(fixture)) as Corpus;
    const extra = JSON.parse(JSON.stringify(
      widened.machines[0])) as CorpusMachine;
    extra.name = 'Invented';
    widened.machines.push(extra);
    const grown = widened.machines.reduce(
      (total, entry) => total + entry.script.length, 0);
    expect(widened.machines.length).toBe(31);
    expect(grown).toBe(76 + extra.script.length);
    expect(grown).not.toBe(steps);
  });

  it('is derived from the file: a clock request is found by the clock\'s '
     + 'own name', () => {
       const doctored = JSON.parse(JSON.stringify(
         fixture.machines.find((one) => one.name === 'Counter'),
       )) as CorpusMachine;
       expect(clockMoves(doctored)).toEqual([]);
       (doctored.document.clocked as { clock: string | null }).clock = 'crank';
       // `Counter`'s script moves `crank` at step 0, so declaring the
       // clock to BE `crank` makes step 0 a clock request -- found by the
       // document's own field and not by a list of machine names.
       expect(clockMoves(doctored)[0]).toBe(0);
     });
});

// ---------------------------------------------------------------------
// The replay
// ---------------------------------------------------------------------

function replayStep(machine: ClockedMachine, step: CorpusStep,
                    expected: CorpusRequest,
                    snapshots: Map<string, ClockedSnapshot>,
                    where: string, census = false): void {
  if (census) {
    compared.steps += 1;
    compared.numbers += numbersIn(expected);
  }
  if (step.move !== undefined) {
    const { input, ...request } = step.move;
    const before = machine.state();
    if (expected.refused !== undefined) {
      let caught: unknown;
      try {
        machine.move(input, request);
        throw new Error(`${where}: expected a refusal and got a request`);
      } catch (error) {
        caught = error;
      }
      const failure = caught as { kind?: string; message?: string };
      expect(failure.kind, `${where} kind`).toBe(expected.refused.kind);
      for (const name of expected.refused.names) {
        expect(failure.message, `${where} names ${name}`).toContain(name);
      }
      // A refused request commits NOTHING: the bank after it is the bank
      // before it.
      expect(machine.state(), where).toEqual(before);
    } else {
      const result = machine.move(input, request);
      exactly(result.admitted, expected.admitted, `${where} admitted`);
      expect(result.commits.length, `${where} commits`)
        .toBe((expected.commits as CorpusCommit[]).length);
      result.commits.forEach((found, index) => {
        const want = (expected.commits as CorpusCommit[])[index];
        expect(found.relations, `${where} commit ${index} relations`)
          .toEqual(want.relations);
        exactly(found.fraction, want.fraction,
                `${where} commit ${index} fraction`);
        exactly(found.value, want.value, `${where} commit ${index} value`);
        expect(Object.keys(found.targets).sort(),
               `${where} commit ${index} targets`)
          .toEqual(Object.keys(want.targets).sort());
        for (const [id, value] of Object.entries(want.targets)) {
          exactly(found.targets[id], value,
                  `${where} commit ${index} ${id}`);
        }
      });
      expect(result.stops.length, `${where} stops`)
        .toBe((expected.stops as CorpusStop[]).length);
      result.stops.forEach((found, index) => {
        const want = (expected.stops as CorpusStop[])[index];
        expect(found.coordinate, `${where} stop ${index}`)
          .toBe(want.coordinate);
        expect(found.side, `${where} stop ${index}`).toBe(want.side);
        exactly(found.bound, want.bound, `${where} stop ${index} bound`);
        exactly(found.value, want.value, `${where} stop ${index} value`);
        exactly(found.input, want.input, `${where} stop ${index} input`);
        exactly(found.fraction, want.fraction,
                `${where} stop ${index} fraction`);
      });
    }
  } else if (step.snapshot !== undefined) {
    snapshots.set(step.snapshot, machine.snapshot());
  } else if (step.restore !== undefined) {
    machine.restore(snapshots.get(step.restore) as ClockedSnapshot);
  } else if (step.reset === true) {
    machine.reset();
  } else {
    throw new Error(`${where}: unknown script step`);
  }
  const bank = machine.state();
  expect(Object.keys(bank).sort(), where)
    .toEqual(Object.keys(expected.bank).sort());
  for (const [id, value] of Object.entries(expected.bank)) {
    exactly(bank[id], value, `${where} bank ${id}`);
  }
}

describe('the viewer reproduces the framework\'s own clocked corpus', () => {
  for (const entry of fixture.machines) {
    it(`replays ${entry.name}`, () => {
      const machine = machineOf(entry);
      const snapshots = new Map<string, ClockedSnapshot>();
      compared.machines.add(entry.name);
      entry.script.forEach((step, index) => {
        const where = `${entry.name} step ${index} ${JSON.stringify(step)}`;
        // EVERY step, with no branch of any kind: a `move` naming the
        // machine's clock is one more request on one more input.
        replayStep(machine, step, entry.requests[index], snapshots, where,
                   true);
      });
    });
  }
});

// ---------------------------------------------------------------------
// The CENSUS THIS BUILD CLOSES (design §11), read off the replay above
// rather than asserted beside it: `replayStep` counts what it actually
// compared, so a step departed from, deferred or skipped fails HERE.
// ---------------------------------------------------------------------

describe('the census, closed', () => {
  it('replayed every machine, every step and every recorded number', () => {
    expect(compared.machines.size).toBe(30);
    expect(compared.steps).toBe(76);
    expect(compared.numbers).toBe(722);
  });
});

describe('the exactness claim, proved rather than declared', () => {
  it('rejects a recorded landing moved by ONE representable value', () => {
    const entry = JSON.parse(JSON.stringify(
      fixture.machines.find((one) => one.name === 'UlpPair'),
    )) as CorpusMachine;
    const step = entry.requests.findIndex(
      (one) => (one.commits ?? []).length > 0);
    const commits = entry.requests[step].commits as CorpusCommit[];
    const value = commits[0].value;
    // The ordinal walk's own `nextAfter`, on the value the corpus
    // records: one representable value away, and well inside the `1e-9`
    // window the RUNNING corpus would have accepted it under.
    const drifted = value + Math.max(Math.abs(value), Number.MIN_VALUE)
      * Number.EPSILON;
    expect(drifted).not.toBe(value);
    expect(Math.abs(drifted - value)).toBeLessThan(1e-9 * Math.abs(drifted));
    commits[0].value = drifted;
    const machine = machineOf(entry);
    const snapshots = new Map<string, ClockedSnapshot>();
    expect(() => entry.script.forEach((one, index) => replayStep(
      machine, one, entry.requests[index], snapshots,
      `UlpPair step ${index}`))).toThrow();
  });

  it('rejects the CLOCK landing 0.49999999999999994 moved by ONE '
     + 'representable value', () => {
       // The strangest number in the file, and the one a reader is most
       // tempted to "fix" to 0.5: `Regulator`'s first release lands one
       // representable value BELOW the ideal instant, which is the
       // far-side landing rule working rather than a rounding error
       // (ADR-127, "An event on the clock is an event"). Moved by one
       // ulp -- to 0.5 itself -- the replay must go red.
       const entry = JSON.parse(JSON.stringify(
         fixture.machines.find((one) => one.name === 'Regulator'),
       )) as CorpusMachine;
       const commits = entry.requests[0].commits as CorpusCommit[];
       expect(commits[0].value).toBe(0.49999999999999994);
       const drifted = 0.5;
       expect(drifted).not.toBe(commits[0].value);
       expect(Math.abs(drifted - commits[0].value))
         .toBeLessThan(1e-9 * drifted);
       commits[0].value = drifted;
       const machine = machineOf(entry);
       const snapshots = new Map<string, ClockedSnapshot>();
       // The throw must be the COMPARISON failing on that very number,
       // not any refusal the replay might raise on the way there.
       expect(() => entry.script.forEach((one, index) => replayStep(
         machine, one, entry.requests[index], snapshots,
         `Regulator step ${index}`))).toThrow(/commit 0 value/);
     });

  it('rejects a recorded STOP fraction moved by one representable value',
     () => {
       const entry = JSON.parse(JSON.stringify(
         fixture.machines.find((one) => one.name === 'Pawl'),
       )) as CorpusMachine;
       const step = entry.requests.findIndex(
         (one) => (one.stops ?? []).length > 0);
       const stops = entry.requests[step].stops as CorpusStop[];
       const fraction = stops[0].fraction;
       stops[0].fraction = fraction * (1 + Number.EPSILON);
       expect(stops[0].fraction).not.toBe(fraction);
       const machine = machineOf(entry);
       const snapshots = new Map<string, ClockedSnapshot>();
       expect(() => entry.script.forEach((one, index) => replayStep(
         machine, one, entry.requests[index], snapshots,
         `Pawl step ${index}`))).toThrow();
     });
});
