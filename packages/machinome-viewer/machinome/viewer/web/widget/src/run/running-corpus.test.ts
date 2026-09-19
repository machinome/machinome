/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The conformance corpus (design §9, ADR-047). `src/running-corpus.json`
// is machinome's `tests/running-corpus.json`, copied byte for byte: the
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
import { loadProgram } from './program';
import type { ProgramBlock, RunDocument } from './program';

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
    expect(fixture.machines).toHaveLength(22);
    expect(new Set(fixture.machines.map((one) => one.name)).size).toBe(19);
    expect(fixture.machines.reduce((total, one) => total + one.ticks.length, 0))
      .toBe(378);
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
  'an in-block gate crossing inside a tick',
  'a stop on a kinked determiner inside a tick',
  'an explicit play edge',
  'play retention and reversal release',
  'play pickup at both flanks',
  'a three-edge play cascade',
  'a downstream play stop located from its driver',
  'non-integer play contact',
  'split play requests',
  'play snapshot replay',
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
  expressions?: (string | null)[];
  plans?: ({ jumps: { name: string; primitive: string; level: string }[] }
           | null)[];
}

/** The CONTINUOUS SELECTIONS of the symbolic vocabulary -- a law built
 * over one of these is piecewise affine, and the producer's own
 * `tools/generate_running_corpus.py`'s `KINKS`, copied here verbatim. */
const KINKS = ['abs', 'min', 'max'];

/** Every function `expression` calls, closed transitively over the
 * fixture's OWN bindings table -- the generator's `_calls(expression,
 * bindings)`, reproduced here as a TEST-LOCAL reading (design D2, option
 * 1) rather than by extending `structureOf` (which deliberately reports
 * a call's ARGUMENTS and not its callee, an engine module this guard
 * must not change for a test's benefit). A callee is an identifier
 * immediately followed by `(`; `freeVariables` already never reports one
 * as a free name (the parser's own `Call` node keeps its callee out of
 * that set), so walking the bindings table through `freeVariables` here
 * cannot mistake a callee for a name to resolve. */
function callsOf(expression: string,
                 bindings: Record<string, string>): Set<string> {
  const found = new Set<string>();
  const seen = new Set<string>();
  const pending = [expression];
  while (pending.length > 0) {
    const text = pending.pop()!;
    if (seen.has(text)) continue;
    seen.add(text);
    for (const match of text.matchAll(/([A-Za-z_][A-Za-z0-9_]*)\s*\(/g)) {
      found.add(match[1]);
    }
    for (const name of freeVariables(text)) {
      if (name in bindings) pending.push(bindings[name]);
    }
  }
  return found;
}

/** The coordinates a LAW with no jump plan drives whose published
 * expression -- closed over the fixture's bindings table through
 * `callsOf` -- calls one of `KINKS`: `tools/generate_running_corpus.py`'s
 * `_kinked_laws`, mirrored here and re-derived from the corpus's own
 * documents only, the absent plan and the expression, never by asking
 * the run engine what it classified -- this stays true after
 * `solve-at-the-kink` gives the engine a classification of its own. An
 * absent `plans` array counts as all-null, exactly as the producer's own
 * `plans = edge.get('plans') or [None] * len(edge.get('gives', ()))`
 * does. */
function kinkedLawsOf(edges: GuardEdge[],
                      bindings: Record<string, string>): Set<string> {
  const found = new Set<string>();
  for (const edge of edges) {
    if (edge.kind !== 'law') continue;
    const gives = edge.gives ?? [];
    const plans = edge.plans ?? gives.map(() => null);
    const expressions = edge.expressions ?? [];
    gives.forEach((name, index) => {
      const plan = plans[index];
      if (plan !== null && plan !== undefined) return;
      const expression = expressions[index];
      if (expression === null || expression === undefined) return;
      const calls = callsOf(expression, bindings);
      if (KINKS.some((kink) => calls.has(kink))) found.add(name);
    });
  }
  return found;
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

/** `(gates, selectors)` for `edge`'s jumps carrying `primitive`, each a
 * list of the free names its level reads (resolved transitively through
 * `bindings`, exactly as `selectionOf` resolves a level) --
 * `tools/generate_running_corpus.py`'s `_in_block_names`, mirrored here
 * and never taken from `loadProgram`.
 *
 * A GATE names a coordinate `gives` holds OTHER than `edge`'s own driven
 * end, ADR-121's self-read excluded because a self-read imposes no
 * order; a SELECTOR names none of `gives` at all. A jump naming only
 * `edge`'s own driven end is neither, and is not returned. */
function inBlockNames(edge: GuardEdge, primitive: string,
                      bindings: Record<string, string>, gives: Set<string>):
{ gates: Set<string>[]; selectors: Set<string>[] } {
  const own = new Set(edge.gives ?? []);
  const gates: Set<string>[] = [];
  const selectors: Set<string>[] = [];
  for (const plan of edge.plans ?? []) {
    if (plan === null || plan === undefined) continue;
    const levels = new Map<string, string>();
    for (const jump of plan.jumps) levels.set(jump.name, jump.level);
    for (const jump of plan.jumps) {
      if (jump.primitive !== primitive) continue;
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
      const reaches = new Set(
        [...names].filter((name) => gives.has(name) && !own.has(name)));
      if (reaches.size > 0) {
        gates.push(reaches);
      } else if (![...names].some((name) => gives.has(name))) {
        selectors.push(names);
      }
    }
  }
  return { gates, selectors };
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
    const playEdges = (program.edges ?? []).filter(
      (edge) => edge.kind === 'play');
    if (playEdges.length > 0) {
      seen.add('an explicit play edge');
      if (playEdges.length >= 3) seen.add('a three-edge play cascade');
      if (playEdges.some((edge) => {
        const measured = edge as GuardEdge & { low: number; high: number };
        return !Number.isInteger(measured.low)
          || !Number.isInteger(measured.high);
      })) seen.add('non-integer play contact');
      if (entry.script.some((action) => action.snapshot !== undefined)
          && entry.script.some((action) => action.restore !== undefined)) {
        seen.add('play snapshot replay');
      }

      const targets = entry.script
        .filter((action) => action.move?.to !== undefined)
        .map((action) => [action.move!.input, action.move!.to!] as const);
      if (targets.some((first, index) => {
        const second = targets[index + 1];
        const third = targets[index + 2];
        return second !== undefined && third !== undefined
          && first[0] === second[0] && second[0] === third[0]
          && ((first[1] < second[1] && second[1] < third[1])
            || (first[1] > second[1] && second[1] > third[1]));
      })) seen.add('split play requests');

      const retained = playEdges[0].gives![0];
      const source = playEdges[0].needs[0];
      const retainedDeltas = entry.ticks.slice(1).map(
        (tick, index) => tick.bank[retained] - entry.ticks[index].bank[retained]);
      const sourceDeltas = entry.ticks.slice(1).map(
        (tick, index) => tick.bank[source] - entry.ticks[index].bank[source]);
      if (retainedDeltas.some((delta, index) =>
        delta !== 0 && retainedDeltas[index + 1] === 0
        && sourceDeltas[index] * sourceDeltas[index + 1] < 0)) {
        seen.add('play retention and reversal release');
      }
      if (retainedDeltas.some((delta) => delta > 0)
          && retainedDeltas.some((delta) => delta < 0)) {
        seen.add('play pickup at both flanks');
      }
      const chained = new Set(playEdges.slice(1).map((edge) => edge.gives![0]));
      if (entry.ticks.some((tick) =>
        tick.stops.some((stop) => chained.has(stop.coordinate)))) {
        seen.add('a downstream play stop located from its driver');
      }
    }
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
    // The coordinates whose determiner is a law that is PIECEWISE AFFINE
    // and carries no jump plan: a stop on one cannot be located by
    // dividing once over the tick.
    const kinked = kinkedLawsOf(program.edges ?? [], bindings);
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
        if (kinked.has(stop.coordinate) && stop.t > 0 && stop.t < 1) {
          seen.add('a stop on a kinked determiner inside a tick');
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
      // An IN-BLOCK GATE CROSSING located strictly inside a tick: the
      // previous tick's bank is what "moved" is measured against, so the
      // first tick (no predecessor) is skipped.
      if (previous !== null) {
        const changed = new Set(Object.keys(tick.bank).filter(
          (name) => previous![name] !== tick.bank[name]));
        for (const crossing of tick.crossings) {
          if (!(crossing.t > 0 && crossing.t < 1)) continue;
          const index = memberOf(program.edges ?? [], crossing.coordinate);
          if (!selectors.has(index)) continue;
          const { gates, selectors: blockers } = inBlockNames(
            (program.edges ?? [])[index], crossing.primitive, bindings,
            blockGives);
          if (!gates.some((names) => [...names].some((name) => changed.has(name)))) {
            continue;
          }
          if (blockers.some((names) => [...names].some((name) => changed.has(name))
            || [...names].some((name) => !(name in tick.bank)))) {
            continue;
          }
          seen.add('an in-block gate crossing inside a tick');
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
    // `Train` states no block at all, so it supplies no in-block gate
    // crossing either.
    expect(uncoveredFeatures(trimmed)).toContain(
      'an in-block gate crossing inside a tick');
    // `Train` DOES carry a kinked plan-less determiner (`slide.travel`,
    // a `min`/`max`/`abs` law with no jump plan) but records no stop on
    // it at all, so trimming to `Train` loses the feature too.
    expect(uncoveredFeatures(trimmed)).toContain(
      'a stop on a kinked determiner inside a tick');
  });

  it('refuses play fixtures whose recorded behavior is narrowed', () => {
    const withoutSplit = fixture.machines.map((entry) => {
      if (!['PlayCorpus', 'MeasuredPlayCorpus'].includes(entry.name)) {
        return entry;
      }
      let moves = 0;
      return {
        ...entry,
        script: entry.script.filter((action) =>
          action.move === undefined || ++moves <= 2),
      };
    });
    expect(uncoveredFeatures(withoutSplit)).toContain('split play requests');

    const withoutRelease = fixture.machines.map((entry) => {
      if (!['PlayCorpus', 'MeasuredPlayCorpus'].includes(entry.name)) return entry;
      return {
        ...entry,
        ticks: entry.ticks.map((tick, index) => ({
          ...tick, bank: {
            ...tick.bank, 'first.turn': index, 'wheel.turn': index,
          },
        })),
      };
    });
    expect(uncoveredFeatures(withoutRelease))
      .toContain('play retention and reversal release');

    const withoutDownstreamStop = fixture.machines.map((entry) => ({
      ...entry,
      ticks: entry.ticks.map((tick) => ({
        ...tick,
        stops: tick.stops.filter((stop) => stop.coordinate !== 'third.turn'),
      })),
    }));
    expect(uncoveredFeatures(withoutDownstreamStop))
      .toContain('a downstream play stop located from its driver');
  });
});

// ---------------------------------------------------------------------
// The order discrimination (design D5, tasks 4), mirroring the
// producer's own `BlockOrderTest`. `blockOrder` (run/jumps.ts:1142) is
// module-local and not exported, but it is not the seam: it reads a
// block only through `block.activeReads(index, forced[index])`, and
// `ProgramBlock` is a plain interface whose `activeReads` is an ordinary
// method member -- already substituted this way by `jumps.test.ts`'s
// `watched()` -- and `ProgramEdge.block` is a mutable field of a loaded
// program. `activeReads` has exactly one non-test caller in the whole
// widget (`jumps.ts:1145`), so substituting it changes the ORDER and
// nothing else. NO seam is added to `src/run/` for this test's benefit.
// ---------------------------------------------------------------------

/** A scenario's engine, its block edges' blocks optionally replaced by a
 * stand-in whose `activeReads` answers the EMPTY SET. That makes every
 * member ready in `blockOrder`'s first Kahn round, so it pushes them in
 * `remaining`'s order -- `0..n-1` over `block.members` -- which IS the
 * published listing order (task 4.2). */
export function loadScenario(entry: CorpusMachine,
                             forceListingOrder: boolean): Engine {
  const program = loadProgram(entry.document as RunDocument,
    `running-corpus.json#${entry.name}`);
  if (forceListingOrder) {
    for (const edge of program.edges) {
      if (edge.block === null) continue;
      const block = edge.block;
      edge.block = {
        members: block.members,
        gives: block.gives,
        activeReads: () => new Set<string>(),
      };
    }
  }
  return new Engine(program, entry.dt, entry.steps + 1);
}

/** Every committed tick's bank the replay disagrees with, under the
 * corpus's own tolerance rule -- the producer's `BlockOrderTest`, shape
 * for shape. */
export function bankDisagreements(entry: CorpusMachine,
                                  forceListingOrder: boolean): string[] {
  const engine = loadScenario(entry, forceListingOrder);
  const script = new Map<number, CorpusScript[]>();
  for (const action of entry.script) {
    const found = script.get(action.tick);
    if (found === undefined) script.set(action.tick, [action]);
    else found.push(action);
  }
  const handles = new Map<string, Command>();
  const ordered: string[] = [];
  const snapshots = new Map<string, unknown>();
  const disagreements: string[] = [];
  for (let step = 1; step <= entry.steps; step += 1) {
    for (const action of script.get(step) ?? []) {
      applyAction(engine, action, handles, ordered, snapshots);
    }
    engine.advance(1);
    const expected = entry.ticks[step - 1];
    const bank = engine.state();
    for (const [id, value] of Object.entries(expected.bank)) {
      if (!near(bank[id], value)) {
        disagreements.push(`tick ${step} ${id}: corpus ${value}, run ${bank[id]}`);
      }
    }
  }
  return disagreements;
}

describe('a block is ordered PIECE BY PIECE, not by its listing (design D5)',
  () => {
    const shiftedCarry = fixture.machines.find(
      (one) => one.name === 'ShiftedCarry' && one.dt === 0.05)!;

    it('4.2 the substitution really forces the PUBLISHED LISTING order', () => {
      const program = loadProgram(shiftedCarry.document as RunDocument,
        'running-corpus.json#ShiftedCarry');
      const blockEdge = program.edges.find((edge) => edge.block !== null)!;
      const block = blockEdge.block as ProgramBlock;
      exact(block.gives.join(','), 'higher.turn,carry.travel',
            'the block\'s members, in the order this loaded program lists '
            + 'them');
      // The SAME order the document's own edges publish them in
      // (`memberOf`, this file's own mirror of `_member_of`): edge index
      // 1 gives `higher.turn`, edge index 2 gives `carry.travel`.
      const rawEdges = (shiftedCarry.document as
        { program: { edges: GuardEdge[] } }).program.edges;
      exact(block.gives.map((name) => memberOf(rawEdges, name)).join(','),
            '1,2', 'the block members\' own index among the published edges');
      // blockOrder starts `remaining` as `block.members.map((_, i) => i)`
      // -- `0, 1` over this same listing -- and with every `activeReads`
      // answering the empty set every member is ready in the first Kahn
      // round, so `ready` (a `.filter` over `remaining`) keeps that exact
      // order: the FORCED order is `0, 1`, the published listing order.
    });

    it('4.3 an engine running the block in the published listing order '
       + 'disagrees with the corpus, the run that orders it per piece '
       + 'does not', () => {
      // The first half is what stops the second from passing by breaking
      // the fixture.
      expect(bankDisagreements(shiftedCarry, false)).toEqual([]);
      const substituted = bankDisagreements(shiftedCarry, true);
      expect(substituted.length).toBeGreaterThan(0);
      expect(substituted[0]).toBe(
        'tick 2 higher.turn: corpus 0.16666666666666669, run 0');
    });
  });
