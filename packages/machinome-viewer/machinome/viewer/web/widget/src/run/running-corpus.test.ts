/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The conformance corpus (design §9, ADR-047). `src/running-corpus.json`
// is solid-node's `tests/running-corpus.json`, copied byte for byte: the
// numbers in it are the framework's, produced by the framework's own run
// and never recomputed a second way. This suite replays every scenario
// through the shipped engine and compares it tick by tick.
//
// A DISAGREEMENT IS A BUG IN THIS ENGINE. Not a tolerance to widen, not
// a scenario to skip, not a fixture to edit.

import { describe, expect, it } from 'vitest';
import corpus from '../running-corpus.json';
import { Engine } from './engine';
import type { Command } from './commands';
import type { RunDocument } from './program';

interface CorpusCrossing {
  relation: string;
  coordinate: string;
  primitive: string;
  level: number;
  t: number;
}

interface CorpusStop {
  coordinate: string;
  bound: string;
  value: number;
  t: number;
  inputs: string[];
}

interface CorpusCommand {
  handle: string;
  status: string;
  admitted: number;
}

interface CorpusTick {
  tick: number;
  bank: Record<string, number>;
  crossings: CorpusCrossing[];
  stops: CorpusStop[];
  commands: CorpusCommand[];
}

interface CorpusScript {
  tick: number;
  handle?: string;
  handles?: string[];
  move?: { input: string; by?: number; to?: number; duration?: number };
  rate?: { input: string; rate: number };
  trigger?: string;
  snapshot?: string;
  restore?: string;
}

interface CorpusMachine {
  name: string;
  dt: number;
  steps: number;
  document: unknown;
  script: CorpusScript[];
  ticks: CorpusTick[];
}

interface Corpus {
  generated_by: string;
  corpus: string;
  tolerance: { float: number };
  machines: CorpusMachine[];
}

const fixture = corpus as unknown as Corpus;

// The corpus's OWN tolerance, read from the fixture and never from a
// constant here: it is the run's published agreement window, and a
// suite that carried its own copy could drift from it silently.
const FLOAT = fixture.tolerance.float;

/** The fixture's float rule, verbatim: `|a - b| <= tol * max(1, |a|, |b|)`. */
function near(actual: number, expected: number): boolean {
  return Math.abs(actual - expected)
    <= FLOAT * Math.max(1, Math.abs(actual), Math.abs(expected));
}

function label(entry: CorpusMachine, tick: number, key: string): string {
  return `${entry.name} at dt=${entry.dt}, tick ${tick}, ${key}`;
}

/** EXACT: discrete state, names, orders and levels. */
function exact(actual: unknown, expected: unknown, where: string): void {
  if (!Object.is(actual, expected)) {
    throw new Error(
      `${where}: expected ${JSON.stringify(expected)}, got ` +
      `${JSON.stringify(actual)}`);
  }
}

/** RELATIVE: bank values, fractions, admitted travel, stop values. */
function close(actual: number, expected: number, where: string): void {
  if (typeof actual !== 'number' || !near(actual, expected)) {
    throw new Error(
      `${where}: expected ${expected} within ${FLOAT} relative, got ` +
      `${actual}`);
  }
}

function applyAction(engine: Engine, action: CorpusScript,
                     handles: Map<string, Command>,
                     ordered: string[],
                     snapshots: Map<string, unknown>): void {
  const remember = (name: string, command: Command) => {
    if (!handles.has(name)) ordered.push(name);
    handles.set(name, command);
  };
  if (action.move !== undefined) {
    const { input, ...request } = action.move;
    remember(action.handle!, engine.move(input, request));
  } else if (action.rate !== undefined) {
    remember(action.handle!, engine.rate(action.rate.input, action.rate.rate)!);
  } else if (action.trigger !== undefined) {
    const issued = engine.trigger(action.trigger);
    action.handles!.forEach((name, index) => remember(name, issued[index]));
  } else if (action.snapshot !== undefined) {
    snapshots.set(action.snapshot, engine.snapshot());
  } else if (action.restore !== undefined) {
    engine.restore(snapshots.get(action.restore) as never);
  } else {
    throw new Error(`unknown script action ${JSON.stringify(action)}`);
  }
}

function replay(entry: CorpusMachine): void {
  const engine = Engine.load(entry.document as RunDocument, {
    dt: entry.dt,
    record: entry.steps + 1,
    sourceUrl: `running-corpus.json#${entry.name}`,
  });

  const script = new Map<number, CorpusScript[]>();
  for (const action of entry.script) {
    const found = script.get(action.tick);
    if (found === undefined) script.set(action.tick, [action]);
    else found.push(action);
  }

  const handles = new Map<string, Command>();
  const ordered: string[] = [];
  const snapshots = new Map<string, unknown>();
  let crossingsSeen = 0;
  let stopsSeen = 0;

  for (let step = 1; step <= entry.steps; step += 1) {
    for (const action of script.get(step) ?? []) {
      applyAction(engine, action, handles, ordered, snapshots);
    }
    engine.advance(1);

    const expected = entry.ticks[step - 1];
    const allCrossings = engine.crossings();
    const allStops = engine.stops();
    const crossings = allCrossings.slice(crossingsSeen);
    const stops = allStops.slice(stopsSeen);
    crossingsSeen = allCrossings.length;
    stopsSeen = allStops.length;

    exact(engine.tick(), expected.tick, label(entry, step, 'tick'));

    const bank = engine.state();
    exact(Object.keys(bank).sort().join(','),
          Object.keys(expected.bank).sort().join(','),
          label(entry, step, 'the bank\'s ids'));
    for (const [id, value] of Object.entries(expected.bank)) {
      close(bank[id], value, label(entry, step, `bank ${id}`));
    }

    exact(crossings.length, expected.crossings.length,
          label(entry, step, 'the number of crossings'));
    expected.crossings.forEach((one, index) => {
      const got = crossings[index];
      const where = label(entry, step, `crossing ${index}`);
      exact(got.relation, one.relation, `${where} relation`);
      exact(got.coordinate, one.coordinate, `${where} coordinate`);
      exact(got.primitive, one.primitive, `${where} primitive`);
      exact(got.level, one.level, `${where} level`);
      close(got.t, one.t, `${where} t`);
    });

    exact(stops.length, expected.stops.length,
          label(entry, step, 'the number of stops'));
    expected.stops.forEach((one, index) => {
      const got = stops[index];
      const where = label(entry, step, `stop ${index}`);
      exact(got.coordinate, one.coordinate, `${where} coordinate`);
      exact(got.bound, one.bound, `${where} bound`);
      exact(got.inputs.join(','), one.inputs.join(','), `${where} inputs`);
      close(got.value, one.value, `${where} value`);
      close(got.t, one.t, `${where} t`);
    });

    // The fixture lists commands in the order the handles were created,
    // which is the order this replay created them too.
    exact(ordered.join(','), expected.commands.map((one) => one.handle).join(','),
          label(entry, step, 'the commands listed'));
    expected.commands.forEach((one) => {
      const command = handles.get(one.handle)!;
      const where = label(entry, step, `command ${one.handle}`);
      exact(command.status, one.status, `${where} status`);
      close(command.admitted, one.admitted, `${where} admitted`);
    });
  }
}

describe('the running corpus', () => {
  it('is the framework\'s own fixture, unedited', () => {
    expect(fixture.generated_by).toBe('tools/generate_running_corpus.py');
    expect(fixture.corpus).toBe('tests/running_project/machine.py');
    expect(fixture.machines).toHaveLength(13);
    expect(new Set(fixture.machines.map((one) => one.name)).size).toBe(11);
    expect(fixture.machines.reduce((total, one) => total + one.ticks.length, 0))
      .toBe(260);
  });

  fixture.machines.forEach((entry, index) => {
    it(`replays ${entry.name} at dt=${entry.dt} (scenario ${index + 1})`, () => {
      replay(entry);
    });
  });
});

// ---------------------------------------------------------------------
// The width guard (design §9, tasks 1.2): a mirror of the generator's
// `uncovered_features`, computed over the COMMITTED fixture. It reads
// the fixture only, so it is red exactly when the fixture is narrowed --
// which is what makes a corpus copied in from a future framework loud
// here without anyone running the generator.
// ---------------------------------------------------------------------

const COMPARISONS = ['<', '<=', '>', '>=', '==', '!='];

const REQUIRED = [
  'floor', 'ceil', 'sign', '%', 'a comparison',
  'a multi-source law',
  'a stop located inside a tick',
  'a bound stated as an expression',
  'a command retired blocked',
  'a rate',
  'a snapshot',
  'a restore',
  'a relative instruction',
  'an absolute instruction',
  'a tick carrying both a crossing and a stop',
];

export function uncoveredFeatures(machines: CorpusMachine[]): string[] {
  const seen = new Set<string>();
  for (const entry of machines) {
    const document = entry.document as {
      program?: {
        edges?: {
          kind: string; needs: string[];
          plans?: ({ jumps: { primitive: string }[] } | null)[];
        }[];
        spans?: Record<string, Record<string, unknown>>;
      };
      instructions?: Record<string, Record<string, unknown>>;
    };
    const program = document.program ?? {};
    for (const edge of program.edges ?? []) {
      if (edge.kind === 'law' && edge.needs.length > 1) {
        seen.add('a multi-source law');
      }
      for (const plan of edge.plans ?? []) {
        if (plan === null || plan === undefined) continue;
        for (const jump of plan.jumps) {
          seen.add(COMPARISONS.includes(jump.primitive)
            ? 'a comparison' : jump.primitive);
        }
      }
    }
    for (const span of Object.values(program.spans ?? {})) {
      for (const side of ['low', 'high']) {
        if (span[side] !== null && typeof span[side] === 'object') {
          seen.add('a bound stated as an expression');
        }
      }
    }
    for (const instruction of Object.values(document.instructions ?? {})) {
      seen.add('targets' in instruction
        ? 'an absolute instruction' : 'a relative instruction');
    }
    for (const action of entry.script) {
      if (action.rate !== undefined) seen.add('a rate');
      if (action.snapshot !== undefined) seen.add('a snapshot');
      if (action.restore !== undefined) seen.add('a restore');
    }
    for (const tick of entry.ticks) {
      if (tick.stops.length > 0) seen.add('a stop located inside a tick');
      if (tick.stops.length > 0 && tick.crossings.length > 0) {
        seen.add('a tick carrying both a crossing and a stop');
      }
      for (const command of tick.commands) {
        if (command.status === 'blocked') seen.add('a command retired blocked');
      }
    }
  }
  return REQUIRED.filter((feature) => !seen.has(feature));
}

describe('the corpus\'s width', () => {
  it('exercises every feature the producer\'s generator requires', () => {
    expect(uncoveredFeatures(fixture.machines)).toEqual([]);
  });

  it('is refused when the corpus is narrowed', () => {
    // The same guard over a deliberately trimmed copy: drop every
    // machine that carries a jump plan, a stop or a rate and the list
    // of uncovered features is no longer empty.
    const trimmed = fixture.machines.filter(
      (entry) => entry.name === 'Train');
    expect(uncoveredFeatures(trimmed).length).toBeGreaterThan(0);
    expect(uncoveredFeatures(trimmed)).toContain('floor');
    expect(uncoveredFeatures(trimmed)).toContain('a stop located inside a tick');
  });
});
