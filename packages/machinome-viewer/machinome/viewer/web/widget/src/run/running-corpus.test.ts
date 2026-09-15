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
import { freeVariables } from '../evaluator';
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
    expect(fixture.machines).toHaveLength(19);
    expect(new Set(fixture.machines.map((one) => one.name)).size).toBe(16);
    expect(fixture.machines.reduce((total, one) => total + one.ticks.length, 0))
      .toBe(356);
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
  'a bound reading another coordinate',
  'a stop reached by the motion of what a bound reads',
  'a command retired blocked',
  'a rate',
  'a snapshot',
  'a restore',
  'a relative instruction',
  'an absolute instruction',
  'a tick carrying both a crossing and a stop',
  'a law that reads the coordinate it drives',
  'a self-read coordinate holding at its gate while its input moves on',
  'a tick carrying both a self-read crossing and a stop',
  'a switched source',
  'a selection crossing inside a tick',
  'a tick carrying both a selection crossing and a stop',
];

/** Every free name `expression` reads, through the fixture's OWN
 * bindings table: the generator's `free_names(expression, bindings)`,
 * reproduced here rather than borrowed from `loadProgram`, because this
 * guard must be red on a narrowed corpus even when the engine is
 * broken. */
function freeNamesOf(expression: string,
                     bindings: Record<string, string>): Set<string> {
  const found = new Set<string>();
  const seen = new Set<string>();
  const pending = [expression];
  while (pending.length > 0) {
    const text = pending.pop()!;
    if (seen.has(text)) continue;
    seen.add(text);
    for (const name of freeVariables(text)) {
      if (name in bindings) pending.push(bindings[name]);
      else found.add(name);
    }
  }
  return found;
}

/** One published edge, as this guard reads it. */
interface GuardEdge {
  kind: string;
  needs: string[];
  gives?: string[];
  plans?: ({ jumps: { name: string; primitive: string; level: string }[] }
           | null)[];
}

/** The index of the edge determining `coordinate`, or `-1` --
 * `tools/generate_running_corpus.py`'s `_member_of`, over the published
 * edges INCLUDING the checks, exactly as the generator indexes them. */
function memberOf(edges: GuardEdge[], coordinate: string): number {
  for (let index = 0; index < edges.length; index += 1) {
    if ((edges[index].gives ?? []).includes(coordinate)) return index;
  }
  return -1;
}

/** What the BLOCKS give, and each member's SELECTOR primitives --
 * `tools/generate_running_corpus.py`'s `_selection`, mirrored here and
 * never taken from `loadProgram`: this guard must be red on a narrowed
 * corpus even when the engine is broken.
 *
 * A block is a strongly connected component of the graph over the edges'
 * own `needs` and `gives` with a need the edge itself gives excluded; a
 * selector is a jump of a member's plan whose `level` -- placeholders
 * resolved transitively into their own jumps' levels, every name closed
 * over the document's bindings table -- names no id the block gives. The
 * primitives reported are the ones a selector of that member has and no
 * OTHER jump of it has, so a crossing carrying one is a selection
 * crossing and not a gate that happens to share an operator. */
function selectionOf(edges: GuardEdge[], bindings: Record<string, string>):
{ gives: Set<string>; selectors: Map<number, Set<string>> } {
  const kept = edges.filter((edge) => edge.kind !== 'check');
  const determiner = new Map<string, number>();
  kept.forEach((edge, index) => {
    for (const name of edge.gives ?? []) determiner.set(name, index);
  });
  const after = kept.map((edge) => {
    const own = new Set(edge.gives ?? []);
    const found = new Set<number>();
    for (const name of edge.needs ?? []) {
      if (own.has(name)) continue;
      const source = determiner.get(name);
      if (source !== undefined) found.add(source);
    }
    return found;
  });
  const members = new Set<number>();
  for (let start = 0; start < kept.length; start += 1) {
    const seen = new Set<number>();
    const pending = [...after[start]];
    while (pending.length > 0) {
      const node = pending.pop()!;
      if (seen.has(node)) continue;
      seen.add(node);
      pending.push(...after[node]);
    }
    if (seen.has(start)) members.add(start);
  }
  const gives = new Set<string>();
  for (const index of members) {
    for (const name of kept[index].gives ?? []) gives.add(name);
  }
  const selectors = new Map<number, Set<string>>();
  for (const index of members) {
    const found = new Set<string>();
    const other = new Set<string>();
    for (const plan of kept[index].plans ?? []) {
      if (plan === null || plan === undefined) continue;
      const levels = new Map<string, string>();
      for (const jump of plan.jumps) levels.set(jump.name, jump.level);
      for (const jump of plan.jumps) {
        const names = new Set<string>();
        const pending = [jump.level];
        while (pending.length > 0) {
          const text = pending.pop()!;
          for (const name of freeNamesOf(text, bindings)) {
            const inner = levels.get(name);
            if (inner !== undefined) pending.push(inner);
            else names.add(name);
          }
        }
        if ([...names].some((name) => gives.has(name))) {
          other.add(jump.primitive);
        } else {
          found.add(jump.primitive);
        }
      }
    }
    selectors.set(index, new Set(
      [...found].filter((primitive) => !other.has(primitive))));
  }
  return { gives, selectors };
}

export function uncoveredFeatures(machines: CorpusMachine[]): string[] {
  const seen = new Set<string>();
  for (const entry of machines) {
    const document = entry.document as {
      program?: {
        coordinates?: Record<string, { initial?: number }>;
        edges?: GuardEdge[];
        spans?: Record<string, Record<string, unknown>>;
        sources?: Record<string, string[]>;
      };
      bindings?: { name: string; expression: string }[];
      instructions?: Record<string, Record<string, unknown>>;
    };
    const bindings: Record<string, string> = {};
    for (const item of document.bindings ?? []) {
      bindings[item.name] = item.expression;
    }
    const banked = new Set(Object.keys(document.program?.coordinates ?? {}));
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
    for (const [identifier, span] of Object.entries(program.spans ?? {})) {
      for (const side of ['low', 'high']) {
        const bound = span[side];
        if (bound === null || typeof bound !== 'object') continue;
        seen.add('a bound stated as an expression');
        const names = freeNamesOf(
          (bound as { expression: string }).expression, bindings);
        names.delete(identifier);
        for (const name of names) {
          if (banked.has(name)) seen.add('a bound reading another coordinate');
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
    // The driven ends a law of this machine READS: `needs` met with
    // `gives`, which is where the self-read is published and the one
    // thing a version 5 consumer reads as something else.
    const reads = new Set<string>();
    for (const edge of program.edges ?? []) {
      if (edge.kind !== 'law') continue;
      for (const key of edge.gives ?? []) {
        if (edge.needs.includes(key)) reads.add(key);
      }
    }
    if (reads.size > 0) seen.add('a law that reads the coordinate it drives');
    // The BLOCK and its SELECTORS, re-derived from the published edges
    // exactly as a consumer must: no key carries either.
    const { gives: blockGives, selectors } =
      selectionOf(program.edges ?? [], bindings);
    if ((program.edges ?? []).some(
      (edge, index) => selectors.has(index)
        && edge.needs.some((name) => blockGives.has(name)))) {
      seen.add('a switched source');
    }
    const sources = program.sources ?? {};
    let previous: Record<string, number> | null = null;
    for (const tick of entry.ticks) {
      if (tick.stops.length > 0) seen.add('a stop located inside a tick');
      for (const identifier of reads) {
        if (previous === null) continue;
        const held = previous[identifier] === tick.bank[identifier];
        const moved = (sources[identifier] ?? []).some(
          (reaching) => reaching in tick.bank
            && previous![reaching] !== tick.bank[reaching]);
        if (held && moved) {
          seen.add('a self-read coordinate holding at its gate while its '
                   + 'input moves on');
        }
      }
      if (tick.stops.length > 0
          && tick.crossings.some((one) => reads.has(one.coordinate))) {
        seen.add('a tick carrying both a self-read crossing and a stop');
      }
      for (const stop of tick.stops) {
        // A stop whose coordinate holds the SAME value before and after
        // its tick was reached by the motion of what the bound READS,
        // not by the coordinate's own.
        const before = previous !== null
          ? previous[stop.coordinate]
          : (program.coordinates ?? {})[stop.coordinate]?.initial;
        if (before !== undefined && before === tick.bank[stop.coordinate]) {
          seen.add('a stop reached by the motion of what a bound reads');
        }
      }
      const selection = tick.crossings.filter((one) => {
        const found = selectors.get(
          memberOf(program.edges ?? [], one.coordinate));
        return found !== undefined && found.has(one.primitive);
      });
      if (selection.length > 0) {
        seen.add('a selection crossing inside a tick');
        if (tick.stops.length > 0) {
          seen.add('a tick carrying both a selection crossing and a stop');
        }
      }
      if (tick.stops.length > 0 && tick.crossings.length > 0) {
        seen.add('a tick carrying both a crossing and a stop');
      }
      for (const command of tick.commands) {
        if (command.status === 'blocked') seen.add('a command retired blocked');
      }
      previous = tick.bank;
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
    expect(uncoveredFeatures(trimmed)).toContain(
      'a bound reading another coordinate');
    expect(uncoveredFeatures(trimmed)).toContain(
      'a stop reached by the motion of what a bound reads');
    // And the three the self-read added: `Train` states no law reading
    // the coordinate it drives, so all three go with it.
    expect(uncoveredFeatures(trimmed)).toContain(
      'a law that reads the coordinate it drives');
    expect(uncoveredFeatures(trimmed)).toContain(
      'a self-read coordinate holding at its gate while its input moves on');
    expect(uncoveredFeatures(trimmed)).toContain(
      'a tick carrying both a self-read crossing and a stop');
    // And one of the three the selection added: `Train`'s edges hold no
    // cycle at all, so it has no block and no selector.
    expect(uncoveredFeatures(trimmed)).toContain(
      'a selection crossing inside a tick');
  });
});
