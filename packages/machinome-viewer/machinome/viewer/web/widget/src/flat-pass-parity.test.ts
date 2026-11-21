/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The flat pass's parity proof (OpenSpec `evaluate-a-pose-in-one-flat-pass`,
// design Decision 10). The minimum is lowered to 0 and the self-check is
// on, so every pose of every committed document with a bindings table
// compiles its table, runs it, and compares every covered value with the
// walk's before the pass is served. At every pose, every operation,
// flexible parameter and colour condition of the document, and every
// entry of its table by name, is also evaluated with the pass served and
// again under an equal scope in a pass the flat pass does not serve, and
// the two are compared by `Object.is` (a throw by its message). Every pose
// is counted as served in full, served in part (an input it reads absent,
// its cone left to the walk) or not served.
//
// What each document poses: a clocked one by `clockedMachine` with a
// `pose` hook posing every bank it commits by `clockedScope`, over the
// corpus script or every declared instruction and a move of every driver;
// a running one by `Engine` tick by tick, posing `poseScope` of each state;
// the source-timing exports at the banks their rows record; the parity
// fixture's cases at their own scopes through its table.
//
// Every document is read from its bytes: a JSON import drops `-0`.

import { readFileSync } from 'node:fs';
import * as THREE from 'three';
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest';

const { loadAsync } = vi.hoisted(() => ({
  loadAsync: vi.fn(() => Promise.resolve(new THREE.BoxGeometry())),
}));

vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({
  STLLoader: class { loadAsync = loadAsync; },
}));

import {
  FLAT_PASS, flatPassMetrics, flatPassServing, prepare, prepareFlatPass,
  resetExpressionMetrics, valueOf, withExpressions,
} from './expressions';
import type { EvalScope } from './expressions';
import { evalExpr } from './evaluator';
import { bindingTable } from './bindings';
import type { BindingTable } from './bindings';
import { WidgetTree } from './tree';
import { assertRenderable } from './viewer';
import { loadClocked } from './clocked/document';
import { clockedMachine } from './clocked/machine';
import type { ClockedMachine, ClockedSnapshot } from './clocked/machine';
import { Engine } from './run/engine';
import type { RunDocument } from './run/program';
import { clockedScope, poseScope } from './run/pose';
import type { Manifest, ManifestDriver, ManifestNode } from './types';

const read = (path: string): any => JSON.parse(
  readFileSync(new URL(path, import.meta.url)).toString('utf8'));
const fixture = (path: string): any => read(`../../../../../tests/fixtures/${path}`);

// ---------------------------------------------------------------------
// The prover: one document, its poses, and the comparison at each.
// ---------------------------------------------------------------------

type Outcome = { value: unknown } | { error: string };

function outcome(action: () => unknown): Outcome {
  try {
    return { value: action() };
  } catch (error) {
    return { error: `${(error as Error)?.constructor?.name}: ${(error as Error)?.message}` };
  }
}

function sameOutcome(a: Outcome, b: Outcome): boolean {
  if ('error' in a || 'error' in b) {
    return 'error' in a && 'error' in b && a.error === b.error;
  }
  return Object.is(a.value, b.value);
}

const show = (o: Outcome): string => ('error' in o ? o.error
  : `${Object.is(o.value, -0) ? '-0' : String(o.value)} (${typeof o.value})`);

let moves = 0;
/** A pass nothing else uses, so the next scope starts an unserved one. */
function movePass(): void {
  moves += 1;
  withExpressions(() => valueOf(prepare('0'), { time: -1e9 - moves }));
}

interface Figures {
  document: string;
  entries: number;
  poses: number;
  fullPoses: number;
  partPoses: number;
  unservedPoses: number;
  compiles: number;
  runs: number;
  partial: number;
  declined: number;
  views: number;
  failures: number;
  compared: number;
  programEntries: number;
  segments: number;
  inputs: number;
  coveredNodes: number;
  comparisons: number;
  refusals: number;
  mismatches: string[];
}

const report: Figures[] = [];

/** Every expression string a node's operations, flexible parameters and
 * colour conditions carry. */
function expressionsOf(node: ManifestNode | undefined, found: string[] = []): string[] {
  if (node === undefined) return found;
  const strings = (value: unknown): void => {
    if (typeof value === 'string') found.push(value);
    else if (Array.isArray(value)) value.forEach(strings);
  };
  node.operations.forEach((operation) => (operation as unknown[]).slice(1).forEach(strings));
  for (const value of Object.values(node.flexible?.params ?? {})) strings(value);
  const color = node.color as unknown;
  if (typeof color === 'object' && color !== null && typeof (color as { when?: unknown }).when === 'string') {
    found.push((color as { when: string }).when);
  }
  for (const child of node.children ?? []) expressionsOf(child, found);
  return found;
}

class Prover {
  private tree?: WidgetTree;
  private readonly expressions: string[];
  poses = 0;
  fullPoses = 0;
  partPoses = 0;
  unservedPoses = 0;
  comparisons = 0;
  refusals = 0;
  readonly mismatches: string[] = [];

  constructor(readonly name: string, readonly table: BindingTable,
              readonly entryNames: readonly string[], private readonly root?: ManifestNode) {
    this.expressions = [...new Set([...expressionsOf(root), ...entryNames])];
  }

  async mount(): Promise<this> {
    if (this.root !== undefined) {
      this.tree = new WidgetTree(this.root, '/', null, this.table);
      await this.tree.loaded;
    }
    return this;
  }

  dispose(): void {
    this.tree?.dispose();
  }

  /** One pose, through the tree when the document has one, else through
   * the pose entry alone; then the comparison. Rethrows a refusal. */
  pose(scope: EvalScope, extra: readonly string[] = []): void {
    this.poses += 1;
    let refusal: unknown;
    try {
      if (this.tree !== undefined) this.tree.update(scope);
      else withExpressions(() => prepareFlatPass(scope));
    } catch (error) {
      const message = (error as Error)?.message ?? String(error);
      if (message.startsWith('The flat pass differs')) this.mismatches.push(message);
      else refusal = error;
    }
    const serving = flatPassServing();
    if (serving === 'full') this.fullPoses += 1;
    else if (serving === 'part') this.partPoses += 1;
    else this.unservedPoses += 1;
    this.compare(scope, extra.length === 0 ? this.expressions : [...this.expressions, ...extra]);
    if (refusal !== undefined) {
      this.refusals += 1;
      throw refusal;
    }
  }

  private compare(scope: EvalScope, expressions: readonly string[]): void {
    const served = expressions.map((expression) => [
      outcome(() => withExpressions(() => valueOf(prepare(expression), scope))),
      outcome(() => evalExpr(expression, scope)),
    ]);
    movePass();
    const copy: EvalScope = { ...scope };
    const walked = expressions.map((expression) => [
      outcome(() => withExpressions(() => valueOf(prepare(expression), copy))),
      outcome(() => evalExpr(expression, copy)),
    ]);
    movePass();
    expressions.forEach((expression, i) => {
      for (const k of [0, 1]) {
        this.comparisons += 1;
        if (!sameOutcome(served[i][k], walked[i][k])) {
          this.mismatches.push(`${expression}: served ${show(served[i][k])}, walk ${show(walked[i][k])}`);
        }
      }
    });
  }

  /** Run `action`, counting a refusal rather than stopping the replay. */
  attempt(action: () => void): void {
    try {
      action();
    } catch {
      // A refused request or pose: the comparison has already been made.
    }
  }

  figures(): Figures {
    const metrics = flatPassMetrics();
    return {
      document: this.name, entries: this.entryNames.length,
      poses: this.poses, fullPoses: this.fullPoses, partPoses: this.partPoses,
      unservedPoses: this.unservedPoses,
      compiles: metrics.compiles, runs: metrics.runs, partial: metrics.partial,
      declined: metrics.declined, views: metrics.views,
      failures: metrics.failures, compared: metrics.compared,
      programEntries: metrics.programEntries, segments: metrics.segments,
      inputs: metrics.inputs, coveredNodes: metrics.coveredNodes,
      comparisons: this.comparisons, refusals: this.refusals, mismatches: this.mismatches,
    };
  }
}

/** The per-document claims (Decision 10), and the line in the report. */
function conclude(prover: Prover): void {
  const figures = prover.figures();
  prover.dispose();
  report.push(figures);
  console.log(`${figures.document}: entries ${figures.entries}, poses ${figures.poses} `
    + `(in full ${figures.fullPoses}, in part ${figures.partPoses}, not served `
    + `${figures.unservedPoses}), compiles ${figures.compiles}, runs ${figures.runs}, `
    + `partial ${figures.partial}, declined ${figures.declined}, views ${figures.views}, `
    + `failures ${figures.failures}, compared ${figures.compared}, `
    + `programEntries ${figures.programEntries}, segments ${figures.segments}, `
    + `inputs ${figures.inputs}, covered ${figures.coveredNodes}, `
    + `comparisons ${figures.comparisons}, refusals ${figures.refusals}`);
  expect(figures.mismatches, figures.document).toEqual([]);
  expect(figures.compiles, figures.document).toBeGreaterThanOrEqual(1);
  expect(figures.runs, figures.document).toBeGreaterThanOrEqual(1);
  expect(figures.failures, figures.document).toBe(0);
  expect(figures.compared, figures.document).toBeGreaterThan(0);
}

// A seeded sweep: the same values on every run.
function seeded(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Targets for one input: its range ends and a seeded sweep inside it, or
 * travels either way where it declares no range. */
function targets(declaration: ManifestDriver | undefined, random: () => number):
    { to?: number; by?: number }[] {
  const range = declaration?.range as [number, number] | null | undefined;
  if (range !== null && range !== undefined) {
    const [low, high] = range;
    return [{ to: low }, { to: high },
      ...[0, 1, 2].map(() => ({ to: low + (high - low) * random() }))];
  }
  return [{ by: 1 }, { by: -1 }, ...[0, 1].map(() => ({ by: 4 * random() - 2 }))];
}

const namesOf = (document: { bindings?: { name: string }[] }): string[] =>
  (document.bindings ?? []).map((entry) => entry.name);

// ---------------------------------------------------------------------
// The drivers of a pose, by kind of document.
// ---------------------------------------------------------------------

interface ClockedStep {
  move?: { input: string; by?: number; to?: number };
  trigger?: string;
  snapshot?: string;
  restore?: string;
  reset?: boolean;
}

function driveClocked(prover: Prover, machineOf: (pose: (bank: Record<string, number>) => void) =>
  ClockedMachine, steps: ClockedStep[] | null, instructions: readonly string[],
  random: () => number): void {
  const table = prover.table;
  const machine = machineOf((bank) => prover.pose(clockedScope(bank, 0, table)));
  prover.attempt(() => prover.pose(clockedScope(machine.state(), 0, table)));
  const snapshots = new Map<string, ClockedSnapshot>();
  const script: ClockedStep[] = steps ?? instructions.map((trigger) => ({ trigger }));
  if (steps === null) {
    for (const [id, declaration] of Object.entries(machine.drivers())) {
      for (const request of targets(declaration, random)) script.push({ move: { input: id, ...request } });
    }
  }
  for (const step of script) {
    prover.attempt(() => {
      if (step.move !== undefined) {
        const { input, ...request } = step.move;
        machine.move(input, request);
      } else if (step.trigger !== undefined) {
        machine.trigger(step.trigger);
      } else if (step.snapshot !== undefined) {
        snapshots.set(step.snapshot, machine.snapshot());
      } else if (step.restore !== undefined) {
        machine.restore(snapshots.get(step.restore)!);
      } else if (step.reset) {
        machine.reset();
      }
    });
    // The bank standing after the request, at a second animation time.
    prover.attempt(() => prover.pose(clockedScope(machine.state(), 0.37, table)));
  }
}

interface RunningAction {
  tick?: number;
  move?: { input: string; by?: number; to?: number; duration?: number };
  rate?: { input: string; rate: number };
  trigger?: string;
  snapshot?: string;
  restore?: string;
  reset?: boolean;
}

function driveRunning(prover: Prover, engine: Engine, steps: number,
                      script: RunningAction[]): void {
  const table = prover.table;
  const pose = (): void => prover.attempt(() =>
    prover.pose(poseScope(engine.state(), engine.clockName(), engine.clock(), table)));
  const snapshots = new Map<string, unknown>();
  pose();
  for (let step = 1; step <= steps; step += 1) {
    for (const action of script) {
      if (action.tick !== step) continue;
      prover.attempt(() => {
        if (action.move !== undefined) {
          const { input, ...request } = action.move;
          engine.move(input, request);
        } else if (action.rate !== undefined) {
          engine.rate(action.rate.input, action.rate.rate);
        } else if (action.trigger !== undefined) {
          engine.trigger(action.trigger);
        } else if (action.snapshot !== undefined) {
          snapshots.set(action.snapshot, engine.snapshot());
        } else if (action.restore !== undefined) {
          engine.restore(snapshots.get(action.restore) as never);
        } else if (action.reset) {
          engine.reset();
        }
      });
    }
    prover.attempt(() => engine.advance(1));
    pose();
  }
}

/** A running fixture has no script: every declared instruction, then
 * every input to its targets, each followed by twenty ticks. */
function fixtureScript(document: any, random: () => number): { steps: number; script: RunningAction[] } {
  const script: RunningAction[] = [];
  let tick = 1;
  for (const trigger of Object.keys(document.instructions ?? {})) {
    script.push({ tick, trigger });
    tick += 20;
  }
  for (const [input, declaration] of Object.entries(document.drivers ?? {})) {
    for (const request of targets(declaration as ManifestDriver, random)) {
      script.push({ tick, move: { input, ...request } });
      tick += 20;
    }
  }
  return { steps: tick, script };
}

// ---------------------------------------------------------------------
// The documents
// ---------------------------------------------------------------------

describe('the flat pass agrees with the walk on every committed document with a table', () => {
  const saved = { ...FLAT_PASS };
  beforeAll(() => {
    FLAT_PASS.minimumBindings = 0;
    FLAT_PASS.verify = true;
  });
  afterAll(() => {
    Object.assign(FLAT_PASS, saved);
    const lines = report.map((one) => [
      one.document, one.entries, one.poses, one.fullPoses, one.partPoses, one.unservedPoses,
      one.compiles, one.runs, one.partial, one.declined, one.views, one.failures, one.compared,
      one.programEntries, one.segments, one.inputs, one.coveredNodes, one.comparisons,
      one.refusals,
    ].join(' | '));
    console.log(['document | entries | poses | in full | in part | not served | compiles '
      + '| runs | partial | declined | views | failures | compared | programEntries | segments '
      + '| inputs | covered | comparisons | refusals', ...lines].join('\n'));
  });

  const FIXTURES: { name: string; path: string }[] = [
    { name: 'calculator', path: 'calculator/viewer.json' },
    { name: 'lock', path: 'lock/viewer.json' },
    { name: 'touched', path: 'touched/viewer.json' },
    { name: 'pascaline', path: 'pascaline/viewer.json' },
    { name: 'carriage', path: 'carriage/viewer.json' },
    { name: 'clearing', path: 'clearing/viewer.json' },
    { name: 'astrarium', path: 'astrarium/viewer.json' },
    { name: 'pose-admission', path: 'pose-admission/manifest.json' },
    { name: 'direct-motion/columns', path: 'direct-motion/columns/manifest.json' },
  ];

  for (const { name, path } of FIXTURES) {
    it(`tests/fixtures/${name}`, async () => {
      const document = fixture(path) as Manifest;
      resetExpressionMetrics();
      const loaded = assertRenderable(document, `/${path}`);
      loaded.settlement.installed();
      const prover = await new Prover(`fixtures/${name}`, loaded.table,
        namesOf(document), document.root).mount();
      const random = seeded(0x5eed + name.length);
      if (loaded.machine !== null) {
        const machine = loaded.machine;
        driveClocked(prover, (pose) => clockedMachine(machine, { pose }), null,
          Object.keys(document.instructions ?? {}), random);
      } else if (loaded.program !== null) {
        const { steps, script } = fixtureScript(document, random);
        driveRunning(prover, new Engine(loaded.program, 1 / 30), steps, script);
      } else {
        throw new Error(`${name} is neither clocked nor running`);
      }
      conclude(prover);
    }, 120_000);
  }

  for (const name of ['curta-6', 'curta-7', 'curta-11', 'curta-11-constrained']) {
    it(`tests/fixtures/source-timing/${name}`, async () => {
      const entry = fixture(`source-timing/${name}.json`).cases[0];
      const document = entry.document as Manifest;
      resetExpressionMetrics();
      const loaded = assertRenderable(document, `/${name}.json`);
      loaded.settlement.installed();
      const program = loaded.program!;
      const prover = await new Prover(`source-timing/${name}`, loaded.table,
        namesOf(document), document.root).mount();
      // The banks the export records: the source-timed moves that reach
      // them take tens of seconds each, and parity needs only the banks.
      const banks: Record<string, number>[] = [
        { ...program.initial },
        ...entry.rows.map((row: { bank: Record<string, number> }) => row.bank),
        ...entry.partitioned.map((row: { bank: Record<string, number> }) => row.bank),
      ];
      for (const bank of banks) {
        prover.attempt(() => prover.pose(poseScope(bank, program.clock, 0, loaded.table)));
      }
      conclude(prover);
    }, 240_000);
  }

  const clockedCorpus = read('./clocked-corpus.json');
  for (const entry of clockedCorpus.machines.filter((one: any) => namesOf(one.document).length > 0)) {
    it(`clocked corpus ${entry.name}`, async () => {
      const url = `clocked-corpus.json#${entry.name}`;
      const document = entry.document as Manifest;
      resetExpressionMetrics();
      const table = bindingTable(document, url);
      const prover = await new Prover(`clocked/${entry.name}`, table, namesOf(document),
        document.root).mount();
      driveClocked(prover, (pose) => clockedMachine(
        loadClocked(document as never, url, table), { pose }), entry.script, [], seeded(1));
      conclude(prover);
    }, 120_000);
  }

  const runningCorpus = read('./running-corpus.json');
  runningCorpus.machines.forEach((entry: any, index: number) => {
    if (namesOf(entry.document).length === 0) return;
    it(`running corpus ${entry.name} #${index}`, async () => {
      const url = `running-corpus.json#${entry.name}`;
      resetExpressionMetrics();
      const table = bindingTable(entry.document as Manifest, url);
      const prover = await new Prover(`running/${entry.name}#${index}`, table,
        namesOf(entry.document), entry.document.root).mount();
      const engine = Engine.load(entry.document as RunDocument, { dt: entry.dt, sourceUrl: url });
      driveRunning(prover, engine, entry.steps, entry.script);
      conclude(prover);
    }, 120_000);
  });

  const timeCorpus = read('./time-drive-corpus.json');
  for (const entry of timeCorpus.machines.filter((one: any) => namesOf(one.document).length > 0)) {
    it(`time-drive corpus ${entry.name}`, async () => {
      const url = `time-drive-corpus.json#${entry.name}`;
      resetExpressionMetrics();
      const table = bindingTable(entry.document as Manifest, url);
      const prover = await new Prover(`time-drive/${entry.name}`, table,
        namesOf(entry.document), entry.document.root).mount();
      const engine = Engine.load(entry.document as RunDocument, { dt: entry.dt, sourceUrl: url });
      driveRunning(prover, engine, entry.steps, entry.script);
      conclude(prover);
    }, 120_000);
  }

  it('run/follow-wrapped-v12.json', async () => {
    const document = read('./run/follow-wrapped-v12.json');
    const commands = read('./run/follow-wrapped-commands-v12.json');
    const url = 'follow-wrapped-v12.json';
    resetExpressionMetrics();
    const table = bindingTable(document as Manifest, url);
    const prover = await new Prover('run/follow-wrapped-v12', table, namesOf(document),
      document.root).mount();
    const engine = Engine.load(document as RunDocument, { dt: commands.dt, sourceUrl: url });
    const script: RunningAction[] = commands.steps.map(
      (step: { move: RunningAction['move'] }, index: number) => ({ tick: 1 + 5 * index, move: step.move }));
    driveRunning(prover, engine, 5 * commands.steps.length, script);
    conclude(prover);
  }, 120_000);

  it('parity-fixture.json, case by case through its table', async () => {
    const parity = read('./parity-fixture.json');
    resetExpressionMetrics();
    const table = bindingTable({ bindings: parity.bindings, drivers: parity.drivers } as Manifest,
      'parity-fixture.json');
    const prover = new Prover('parity-fixture', table, namesOf(parity));
    for (const one of parity.cases as { expression: string; scope: EvalScope }[]) {
      const scope: EvalScope = { ...one.scope, get bindings() { return table.roots(); } };
      // The case's own expression beside every entry, served and walked.
      prover.attempt(() => prover.pose(scope, [one.expression]));
    }
    conclude(prover);
  }, 120_000);
});
