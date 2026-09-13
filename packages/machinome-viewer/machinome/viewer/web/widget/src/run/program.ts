/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The compiled program, loaded from a version 5 document (design §4).
//
// Reproduces what solid-node's `simulation/program.py` `Program`
// PUBLISHES, read backwards: the coordinates in the order the program
// propagates them, the values it computes and never stores, the edges
// in propagation order with their expressions, their affinity and their
// jump plans, the declared bounds, the reaching-inputs table, the five
// constants the algorithm is defined by, and the clock name.
//
// The engine READS all six things the framework decided at compile time
// -- the edge order, each law's `affine` flag, each plan's postorder,
// level quantity and rewrite, the `sources` table and the `limits` --
// and recomputes none of them. What it DERIVES is exactly what §5 of the
// framework's own design says is derived: the `determiner` inversion of
// `gives`, the bank-key set, and everything the tick computes.
//
// Every shape the engine cannot execute is refused HERE, when the
// document is loaded, naming what is wrong and quoting the source --
// never met first while a frame is being rendered or a tick integrated.

import { BindingTable, bindingTable } from '../bindings';
import { freeVariables } from '../evaluator';
import {
  expressionGeneration, NodeId, prepare, valueOf,
} from '../expressions';
import {
  Manifest, ManifestBinding, ManifestDriver, ManifestInstruction,
} from '../types';
import { assertNestable, nest } from './scope';

/** A law cannot be compiled into the running program, or cannot be
 * integrated over a tick: its level quantity meets a division by zero
 * somewhere on the tick's path, or a jump carries nowhere to keep its
 * history. The tick committed nothing. */
export class UnsupportedLaw extends Error {
  readonly kind = 'law';
}

/** One tick would cut a law's path more times than the run admits. The
 * tick committed nothing. */
export class TooManyCrossings extends Error {
  readonly kind = 'crossings';
}

/** Two increments disagreed on one coordinate over one tick, or a
 * check's prediction disagreed with what its coordinate received. The
 * tick committed nothing. */
export class RunConflict extends Error {
  readonly kind = 'conflict';
}

/** A coordinate left a declared bound over a tick and locating the stop
 * stopped no input that was moving: a broken invariant of the run rather
 * than a dt that is too coarse. The tick committed nothing. */
export class StopInvariantError extends Error {
  readonly kind = 'stop';
}

/** Every refusal a TICK can make, as the protocol reports it. */
export type RefusalKind = 'law' | 'crossings' | 'conflict' | 'stop';

export function refusalKind(error: unknown): RefusalKind | null {
  if (error instanceof UnsupportedLaw) return 'law';
  if (error instanceof TooManyCrossings) return 'crossings';
  if (error instanceof RunConflict) return 'conflict';
  if (error instanceof StopInvariantError) return 'stop';
  return null;
}

/** The ten jump primitives a published plan may name (design §4 item 8).
 * This list is the engine's forward-compatibility seam: a framework
 * that grows an eleventh inside version 5 is refused rather than
 * integrated with a branch rule this engine invented. */
export const JUMP_PRIMITIVES = [
  'floor', 'ceil', 'sign', '%', '<', '<=', '>', '>=', '==', '!=',
] as const;

export type JumpPrimitive = typeof JUMP_PRIMITIVES[number];

export type EdgeKind = 'law' | 'wiring' | 'formula' | 'check';

const EDGE_KINDS: readonly EdgeKind[] = ['law', 'wiring', 'formula', 'check'];

export interface ProgramCoordinate {
  kind: 'input' | 'coordinate';
  initial: number;
  unit: string | null;
  domain: string | null;
}

export interface ProgramJump {
  name: string;
  primitive: JumpPrimitive;
  level: string;
  affine: boolean;
}

export interface ProgramPlan {
  skeleton: string;
  jumps: ProgramJump[];
}

export type ProgramBound = number | null | { expression: string };

export interface ProgramSpan {
  low: ProgramBound;
  high: ProgramBound;
}

export interface ProgramEdge {
  kind: EdgeKind;
  needs: string[];
  gives: string[];
  description: string;
  statedBy: string;
  /** A law's expression per driven end; `null` for a constant law.
   * Empty for every other kind. */
  expressions: (string | null)[];
  /** One flag per driven end: whether this edge's value is affine in
   * its sources along the tick's path. Read, never recomputed. */
  affine: boolean[];
  plans: (ProgramPlan | null)[];
  /** A wiring's one factor; a formula's or check's per-need factors. */
  factor: number;
  factors: number[];
  constant: number;
  slot: string | null;
}

export interface ProgramLimits {
  crossingTolerance: number;
  subdivisions: number;
  bisectionRounds: number;
  maxCrossings: number;
  agreement: number;
}

export interface Determination {
  edge: ProgramEdge;
  index: number;
}

export interface LoadedProgram {
  identity: string;
  clock: string;
  /** The bank's id order, fixed at load: the published coordinate order,
   * inputs first. */
  order: readonly string[];
  inputs: readonly string[];
  coordinates: Readonly<Record<string, ProgramCoordinate>>;
  initial: Readonly<Record<string, number>>;
  intermediates: readonly string[];
  edges: readonly ProgramEdge[];
  spans: Readonly<Record<string, ProgramSpan>>;
  sources: Readonly<Record<string, readonly string[]>>;
  limits: ProgramLimits;
  determiner: ReadonlyMap<string, Determination>;
  /** Every branch placeholder, and the plan that binds it. */
  placeholders: ReadonlyMap<string, ProgramPlan>;
  drivers: Readonly<Record<string, ManifestDriver>>;
  instructions: Readonly<Record<string, ManifestInstruction>>;
  bindings: BindingTable;
  /** Every id an expression of this document may name: the clock, the
   * bank's coordinates and the published computed values. A plan's own
   * placeholders are legal only inside that plan and are not here. */
  declaredNames: ReadonlySet<string>;
  /** One interned root per published expression, re-prepared when the
   * shared store's generation moves (design D12). */
  nodeOf(expression: string): NodeId;
}

/** A version 5 document, as far as the run is concerned. The tree, the
 * pieces and the animation block are somebody else's business. */
export interface RunDocument extends Omit<Partial<Manifest>, 'version'> {
  version: number;
  drivers?: Record<string, ManifestDriver>;
  instructions?: Record<string, ManifestInstruction>;
  bindings?: ManifestBinding[];
  program?: unknown;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function quoted(value: unknown): string {
  const text = JSON.stringify(value);
  if (text === undefined) return String(value);
  return text.length > 80 ? `${text.slice(0, 80)}…` : text;
}

/** The computed values this program publishes and no edge determines.
 *
 * Design §15 finding 1: the acceptance document publishes six of them.
 * They are harmless while nothing reads them and fatal the moment
 * something does, so the refusal is scoped to being READ -- inside the
 * program by `loadProgram` itself, and by a pose expression through the
 * document loader, which asks this. */
export function uncomputedValues(program: LoadedProgram): ReadonlySet<string> {
  const given = new Set<string>();
  for (const edge of program.edges) {
    for (const id of edge.gives) given.add(id);
  }
  return new Set(program.intermediates.filter((id) => !given.has(id)));
}

/** One published expression, evaluated over one set of values.
 *
 * THE ONE PLACE `src/run/` evaluates anything (design D11). Every call
 * builds a FRESH scope object: `expressions.ts` memoizes by a pass stamp
 * and takes an identity fast path -- a scope object it has already seen
 * is assumed to hold the same values -- so an engine that reused one
 * object and mutated it between evaluations would read the PREVIOUS
 * evaluation's memoized numbers, silently and everywhere. The rule is
 * kept by having exactly one call site rather than by discipline at
 * many.
 *
 * `values` carries the names this expression may read: an edge's sources
 * and, inside a jump plan, that plan's branch placeholders. A binding
 * name resolves through the document's own table, lazily, where it is
 * read -- which is why a table carrying a placeholder-bearing entry (a
 * shape the ratified bindings requirement does not describe; design §15
 * finding 2) costs this viewer nothing. */
export function evaluateExpression(
  program: LoadedProgram,
  expression: string,
  values: Record<string, number>,
): number {
  const value = valueOf(program.nodeOf(expression), {
    time: 0,
    drivers: nest(values),
    bindings: program.bindings.roots(),
  });
  return typeof value === 'number' ? value : Number(value);
}

export function loadProgram(
  document: RunDocument,
  sourceUrl: string,
  bindings?: BindingTable,
): LoadedProgram {
  const refuse = (detail: string): never => {
    throw new Error(
      `${sourceUrl} declares document version ${document.version} and ` +
      `${detail} The document is malformed: refusing it rather than ` +
      'running a machine this viewer cannot execute.');
  };

  const raw = document.program;
  if (raw === undefined || raw === null) {
    return refuse(
      'carries no "program" object. A version 5 document is a version 4 ' +
      'one plus the compiled mechanical program, and without it there is ' +
      'nothing to run.');
  }
  if (!isObject(raw)) {
    return refuse(`its "program" is ${quoted(raw)}, not an object.`);
  }

  // 1. Every published key, by name.
  for (const key of ['identity', 'clock', 'coordinates', 'intermediates',
                     'edges', 'spans', 'sources', 'limits']) {
    if (!(key in raw)) {
      return refuse(`its program carries no "${key}" key.`);
    }
  }
  if (typeof raw.identity !== 'string') {
    return refuse(`its program's "identity" is ${quoted(raw.identity)}, ` +
                  'not a string.');
  }
  if (typeof raw.clock !== 'string') {
    return refuse(`its program's "clock" is ${quoted(raw.clock)}, not a ` +
                  'string.');
  }
  const identity = raw.identity;
  const clock = raw.clock;

  // 12. The five constants the algorithm is defined by.
  if (!isObject(raw.limits)) {
    return refuse(`its program's "limits" is ${quoted(raw.limits)}, not an ` +
                  'object.');
  }
  const limitKeys = ['crossing_tolerance', 'subdivisions', 'bisection_rounds',
                     'max_crossings', 'agreement'] as const;
  for (const key of limitKeys) {
    const value = (raw.limits as Record<string, unknown>)[key];
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      return refuse(
        `its program's limit "${key}" is ${quoted(value)}, which is not a ` +
        'finite number. The five limits are what the integration is ' +
        'defined by: there is no default to fall back on.');
    }
  }
  const limitValues = raw.limits as Record<string, number>;
  const limits: ProgramLimits = {
    crossingTolerance: limitValues.crossing_tolerance,
    subdivisions: limitValues.subdivisions,
    bisectionRounds: limitValues.bisection_rounds,
    maxCrossings: limitValues.max_crossings,
    agreement: limitValues.agreement,
  };

  // 2. The coordinates, in published order.
  if (!isObject(raw.coordinates)) {
    return refuse(`its program's "coordinates" is ` +
                  `${quoted(raw.coordinates)}, not an object.`);
  }
  const order: string[] = [];
  const inputs: string[] = [];
  const coordinates: Record<string, ProgramCoordinate> = {};
  const initial: Record<string, number> = {};
  for (const [id, entry] of Object.entries(raw.coordinates)) {
    if (!isObject(entry)) {
      return refuse(`its coordinate "${id}" is ${quoted(entry)}, not an ` +
                    'object.');
    }
    if (entry.kind !== 'input' && entry.kind !== 'coordinate') {
      return refuse(
        `its coordinate "${id}" declares kind ${quoted(entry.kind)}; a ` +
        'published coordinate is either an "input" a command may move or ' +
        'a "coordinate" a relation moves.');
    }
    if (typeof entry.initial !== 'number' || !Number.isFinite(entry.initial)) {
      return refuse(
        `its coordinate "${id}" declares initial ${quoted(entry.initial)}, ` +
        'which is not a finite number. The rest value is the one number a ' +
        'consumer cannot compute for itself.');
    }
    order.push(id);
    if (entry.kind === 'input') inputs.push(id);
    coordinates[id] = {
      kind: entry.kind,
      initial: entry.initial,
      unit: typeof entry.unit === 'string' ? entry.unit : null,
      domain: typeof entry.domain === 'string' ? entry.domain : null,
    };
    initial[id] = entry.initial;
  }
  const bank = new Set(order);

  // 3. The inputs and the drivers table must be the same set: the
  // framework asserts the identity, and a consumer holding both tables
  // has to check it, because which one is authoritative is otherwise
  // unknowable.
  const declaredDrivers = Object.keys(document.drivers ?? {});
  const onlyProgram = inputs.filter((id) => !(id in (document.drivers ?? {})));
  const onlyTable = declaredDrivers.filter((id) => !inputs.includes(id));
  if (onlyProgram.length > 0 || onlyTable.length > 0) {
    const parts: string[] = [];
    if (onlyProgram.length > 0) {
      parts.push(`${onlyProgram.sort().join(', ')} is an input of the ` +
                 'program that the "drivers" table does not declare');
    }
    if (onlyTable.length > 0) {
      parts.push(`${onlyTable.sort().join(', ')} is declared in the ` +
                 '"drivers" table and is not an input of the program');
    }
    return refuse(`${parts.join(', and ')}. The two tables name one set of ` +
                  'inputs; which of them is authoritative is otherwise ' +
                  'unknowable.');
  }

  // The published computed values.
  if (!Array.isArray(raw.intermediates)
      || raw.intermediates.some((id) => typeof id !== 'string')) {
    return refuse(`its program's "intermediates" is ` +
                  `${quoted(raw.intermediates)}, not an array of ids.`);
  }
  const intermediates = raw.intermediates as string[];
  const known = new Set([...bank, ...intermediates]);

  // 4. An id set that cannot be nested.
  try {
    assertNestable(known);
  } catch (error) {
    return refuse(`${(error as Error).message}`);
  }

  // 5. The clock is a free name in the same scope as the bank.
  if (known.has(clock) || clock in (document.drivers ?? {})) {
    return refuse(
      `its program's clock is named "${clock}", which is also a coordinate ` +
      'or a declared driver id. The clock binds beside the whole bank in ' +
      'one evaluation scope, so a value under that id would be silently ' +
      'overwritten.');
  }

  // 6, 7, 8, 9, 10. The edges.
  if (!Array.isArray(raw.edges)) {
    return refuse(`its program's "edges" is ${quoted(raw.edges)}, not an ` +
                  'array.');
  }
  const placeholders = new Map<string, ProgramPlan>();
  const edges: ProgramEdge[] = [];
  raw.edges.forEach((entry, position) => {
    if (!isObject(entry)) {
      return refuse(`its edge ${position} is ${quoted(entry)}, not an ` +
                    'object.');
    }
    const where = `its edge ${position}`;
    const kind = entry.kind;
    if (typeof kind !== 'string' || !EDGE_KINDS.includes(kind as EdgeKind)) {
      return refuse(
        `${where} declares kind ${quoted(kind)}, which this engine cannot ` +
        `execute; it executes: ${EDGE_KINDS.join(', ')}.`);
    }
    const needs = entry.needs;
    const gives = entry.gives;
    if (!Array.isArray(needs) || needs.some((id) => typeof id !== 'string')
        || !Array.isArray(gives) || gives.some((id) => typeof id !== 'string')) {
      return refuse(`${where} declares "needs" or "gives" that is not an ` +
                    'array of ids.');
    }
    const description = typeof entry.description === 'string'
      ? entry.description : `edge ${position}`;
    const statedBy = typeof entry.stated_by === 'string'
      ? entry.stated_by : 'the program';

    for (const id of [...needs, ...gives]) {
      if (!known.has(id)) {
        return refuse(
          `${where} (${description}) names "${id}", which is neither a bank ` +
          'coordinate nor a published computed value.');
      }
    }

    const edge: ProgramEdge = {
      kind: kind as EdgeKind,
      needs: needs as string[],
      gives: gives as string[],
      description,
      statedBy,
      expressions: [],
      affine: (gives as string[]).map(() => true),
      plans: (gives as string[]).map(() => null),
      factor: 0,
      factors: [],
      constant: 0,
      slot: null,
    };

    if (kind === 'law') {
      const expressions = entry.expressions;
      const affine = entry.affine;
      const plans = entry.plans;
      if (!Array.isArray(expressions) || expressions.length !== gives.length) {
        return refuse(
          `${where} (${description}) is a law whose "expressions" ` +
          `(${quoted(expressions)}) is not aligned with its ${gives.length} ` +
          'driven end(s).');
      }
      if (!Array.isArray(affine) || affine.length !== gives.length) {
        return refuse(
          `${where} (${description}) is a law whose "affine" ` +
          `(${quoted(affine)}) is not aligned with its ${gives.length} ` +
          'driven end(s).');
      }
      if (!Array.isArray(plans) || plans.length !== gives.length) {
        return refuse(
          `${where} (${description}) is a law whose "plans" ` +
          `(${quoted(plans)}) is not aligned with its ${gives.length} ` +
          'driven end(s).');
      }
      edge.expressions = expressions.map((text) => {
        if (text === null) return null;
        if (typeof text !== 'string') {
          return refuse(`${where} (${description}) carries the expression ` +
                        `${quoted(text)}, which is not a string.`);
        }
        return text;
      });
      edge.affine = affine.map((flag) => flag === true);
      edge.plans = plans.map((plan, index) => {
        if (plan === null || plan === undefined) return null;
        if (!isObject(plan) || typeof plan.skeleton !== 'string'
            || !Array.isArray(plan.jumps)) {
          return refuse(`${where} (${description}) carries a jump plan that ` +
                        `is not a {skeleton, jumps} object: ${quoted(plan)}.`);
        }
        const jumps: ProgramJump[] = plan.jumps.map((jump) => {
          if (!isObject(jump) || typeof jump.name !== 'string'
              || typeof jump.level !== 'string') {
            return refuse(`${where} (${description}) carries a jump that is ` +
                          `not a {name, primitive, level, affine} object: ` +
                          `${quoted(jump)}.`);
          }
          if (typeof jump.primitive !== 'string'
              || !(JUMP_PRIMITIVES as readonly string[])
                .includes(jump.primitive)) {
            return refuse(
              `${where} (${description}) carries a jump whose primitive is ` +
              `${quoted(jump.primitive)}; this engine reads a branch from: ` +
              `${JUMP_PRIMITIVES.join(', ')}. A primitive it does not know ` +
              'would have to be integrated with a branch rule it invented.');
          }
          return {
            name: jump.name,
            primitive: jump.primitive as JumpPrimitive,
            level: jump.level,
            affine: jump.affine === true,
          };
        });
        const built: ProgramPlan = { skeleton: plan.skeleton, jumps };
        for (const jump of jumps) {
          const owner = placeholders.get(jump.name);
          if (owner !== undefined) {
            return refuse(
              `two jump plans name a jump node "${jump.name}". The producer ` +
              'mints a placeholder across the whole document precisely so ' +
              'they cannot: sharing one would give two different jump nodes ' +
              'one published subexpression.');
          }
          placeholders.set(jump.name, built);
        }
        void index;
        return built;
      });
    } else if (kind === 'wiring') {
      if (typeof entry.factor !== 'number' || !Number.isFinite(entry.factor)) {
        return refuse(`${where} (${description}) is a wiring whose "factor" ` +
                      `is ${quoted(entry.factor)}, not a finite number.`);
      }
      edge.factor = entry.factor;
      edge.factors = [entry.factor];
    } else {
      // A formula or a check: a coefficient map and a constant, on a slot.
      if (typeof entry.slot !== 'string') {
        return refuse(`${where} (${description}) is a ${kind} with no ` +
                      '"slot" naming the coordinate its formula is stated ' +
                      'on.');
      }
      if (!known.has(entry.slot)) {
        return refuse(`${where} (${description}) states its formula on the ` +
                      `slot "${entry.slot}", which is neither a bank ` +
                      'coordinate nor a published computed value.');
      }
      if (!Array.isArray(entry.factors)
          || entry.factors.length !== needs.length
          || entry.factors.some((value) => typeof value !== 'number'
                                || !Number.isFinite(value))) {
        return refuse(
          `${where} (${description}) is a ${kind} whose "factors" ` +
          `(${quoted(entry.factors)}) is not one finite number per named ` +
          `value; it names ${needs.length}.`);
      }
      if (typeof entry.constant !== 'number'
          || !Number.isFinite(entry.constant)) {
        return refuse(`${where} (${description}) is a ${kind} whose ` +
                      `"constant" is ${quoted(entry.constant)}, not a ` +
                      'finite number.');
      }
      edge.slot = entry.slot;
      edge.factors = entry.factors as number[];
      edge.constant = entry.constant;
      if (kind === 'check' && gives.length > 0) {
        return refuse(
          `${where} (${description}) is a check whose "gives" names ` +
          `${(gives as string[]).join(', ')}. A check determines nothing: ` +
          'it predicts what its coordinate should have received and ' +
          'compares.');
      }
      if (kind === 'formula' && gives.length !== 1) {
        return refuse(`${where} (${description}) is a formula with ` +
                      `${gives.length} driven ends; a formula has exactly ` +
                      'one.');
      }
    }
    edges.push(edge);
  });

  // 11. The declared bounds.
  if (!isObject(raw.spans)) {
    return refuse(`its program's "spans" is ${quoted(raw.spans)}, not an ` +
                  'object.');
  }
  const spans: Record<string, ProgramSpan> = {};
  for (const [id, entry] of Object.entries(raw.spans)) {
    if (!bank.has(id)) {
      return refuse(`its program declares a range over "${id}", which the ` +
                    'bank does not hold.');
    }
    if (!isObject(entry)) {
      return refuse(`its program's range over "${id}" is ${quoted(entry)}, ` +
                    'not a {low, high} object.');
    }
    const sides: Record<string, ProgramBound> = {};
    for (const side of ['low', 'high']) {
      const bound = entry[side];
      if (bound === null || bound === undefined) {
        sides[side] = null;
      } else if (typeof bound === 'number' && Number.isFinite(bound)) {
        sides[side] = bound;
      } else if (isObject(bound) && typeof bound.expression === 'string') {
        sides[side] = { expression: bound.expression };
      } else {
        return refuse(
          `its program's ${side} bound on "${id}" is ${quoted(bound)}, ` +
          'which is neither absent, a finite number, nor an expression.');
      }
    }
    spans[id] = { low: sides.low, high: sides.high };
  }

  // 13. The reaching-inputs table.
  if (!isObject(raw.sources)) {
    return refuse(`its program's "sources" is ${quoted(raw.sources)}, not ` +
                  'an object.');
  }
  const sources: Record<string, string[]> = {};
  for (const [id, members] of Object.entries(raw.sources)) {
    if (!known.has(id)) {
      return refuse(`its program's "sources" table names "${id}", which is ` +
                    'neither a bank coordinate nor a published computed ' +
                    'value.');
    }
    if (!Array.isArray(members)) {
      return refuse(`its program's "sources" entry for "${id}" is ` +
                    `${quoted(members)}, not an array.`);
    }
    for (const member of members) {
      if (typeof member !== 'string' || !inputs.includes(member)) {
        return refuse(`its program's "sources" entry for "${id}" names ` +
                      `${quoted(member)}, which is not one of its inputs.`);
      }
    }
    sources[id] = members as string[];
  }

  // 14. A computed value an edge READS that no edge gives.
  const determiner = new Map<string, Determination>();
  for (const edge of edges) {
    edge.gives.forEach((id, index) => determiner.set(id, { edge, index }));
  }
  for (const edge of edges) {
    for (const id of edge.needs) {
      if (!bank.has(id) && !determiner.has(id)) {
        return refuse(
          `${edge.description} reads the computed value "${id}", which no ` +
          'edge determines. A computed value is not stored anywhere: one ' +
          'nothing computes has no number to read.');
      }
    }
    if (edge.slot !== null && !bank.has(edge.slot)
        && !determiner.has(edge.slot)) {
      return refuse(
        `${edge.description} is stated on the computed value ` +
        `"${edge.slot}", which no edge determines.`);
    }
  }

  // The interned roots, generation-guarded (design D12).
  let generation = -1;
  let roots = new Map<string, NodeId>();
  const nodeOf = (expression: string): NodeId => {
    if (generation !== expressionGeneration()) {
      roots = new Map();
      generation = expressionGeneration();
    }
    let found = roots.get(expression);
    if (found === undefined) {
      found = prepare(expression);
      roots.set(expression, found);
    }
    return found;
  };

  const table = bindings ?? bindingTable(document as Manifest, sourceUrl);

  // 10. Every expression's free names, closed over the bindings table
  // and minus the placeholders that are legal where it stands. A law
  // need not read every source, so the test is CONTAINMENT.
  const namesOf = (expression: string): ReadonlySet<string> =>
    table.closure(freeVariables(expression));

  const check = (expression: string, allowed: Set<string>,
                 what: string): void => {
    for (const name of namesOf(expression)) {
      if (!allowed.has(name)) {
        refuse(
          `${what} names "${name}", which it may not read. It may read: ` +
          `${[...allowed].sort().join(', ') || 'nothing'}. Quoting the ` +
          `expression: ${quoted(expression)}.`);
      }
    }
  };

  for (const edge of edges) {
    if (edge.kind !== 'law') continue;
    const allowed = new Set(edge.needs);
    edge.expressions.forEach((expression, index) => {
      if (expression !== null) {
        check(expression, allowed, `${edge.description}'s expression`);
      }
      const plan = edge.plans[index];
      if (plan === null) return;
      const inside = new Set([...allowed,
                              ...plan.jumps.map((jump) => jump.name)]);
      check(plan.skeleton, inside, `${edge.description}'s jump skeleton`);
      for (const jump of plan.jumps) {
        check(jump.level, inside,
              `${edge.description}'s ${jump.primitive} level quantity`);
      }
    });
  }
  for (const [id, span] of Object.entries(spans)) {
    for (const bound of [span.low, span.high]) {
      if (bound !== null && typeof bound === 'object') {
        check(bound.expression, new Set([id]),
              `the bound declared on "${id}"`);
      }
    }
  }

  const declaredNames = new Set<string>([clock, ...bank, ...intermediates]);

  return {
    identity,
    clock,
    order,
    inputs,
    coordinates,
    initial,
    intermediates,
    edges,
    spans,
    sources,
    limits,
    determiner,
    placeholders,
    drivers: document.drivers ?? {},
    instructions: document.instructions ?? {},
    bindings: table,
    declaredNames,
    nodeOf,
  };
}
