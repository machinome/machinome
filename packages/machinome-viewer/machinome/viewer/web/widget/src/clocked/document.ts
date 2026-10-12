/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The compiled CLOCKED machine, loaded from a version 8 document
// (OpenSpec `execute-the-commit`, design §1, §2, §7, §8; machinome
// ADR-125, ADR-126, ADR-128).
//
// Reproduces what machinome's `simulation/clocked.py` PUBLISHES, read
// backwards: the `states` table beside `drivers`, the machine's
// identity, its clock name, the reserved own-name every bound reads its
// own coordinate under, one entry per committing relation, one entry per
// (coordinate, side) constraint, and the two limits the solve is defined
// by.
//
// The consumer RECOMPUTES none of what compile time decided. `shapes` is
// read, never re-derived (design §6): `_shape_of` is a hundred lines of
// structural rules and a consumer that classified a level differently
// would cut a kinked path differently and land on a different float.
// What IS derived here is exactly what ADR-128 §4 says is derived: the
// bank's id ORDER (the drivers table's key order, then the states
// table's, then the clock), because every number a clocked bank holds is
// already in the document and publishing a table of them would publish
// something a consumer must be told to ignore.
//
// Every shape this engine cannot execute is refused HERE, when the
// document is loaded, naming the offending key and quoting the source --
// the surface `loadProgram` already refuses a program on.

import { BindingTable } from '../bindings';
import { freeVariables } from '../evaluator';
import { retainedKinkLevels, NodeId, prepare, withExpressions } from
  '../expressions';
import type { KinkLevel, PathShape } from '../expressions';
import { evaluateExpression, JUMP_PRIMITIVES } from '../run/program';
import type {
  JumpPrimitive, PathHost, ProgramJump, ProgramLimits, ProgramPlan,
} from '../run/program';
import type { Manifest, ManifestDriver, ManifestInstruction } from '../types';

// ---------------------------------------------------------------------
// The refusals a clocked request can make, and the KINDS the corpus
// pins them by (design §11). The four kinds are the framework's own
// exception class names, so a corpus entry recording `"kind":
// "JointRangeError"` is matched by a field of the error rather than by
// its prose.
// ---------------------------------------------------------------------

export type ClockedRefusalKind =
  'TooManyEvents' | 'ClockedError' | 'ValueError' | 'JointRangeError';

/** A clocked machine, or a request over one, this viewer refuses. */
export class ClockedError extends Error {
  readonly kind: ClockedRefusalKind;

  constructor(message: string, kind: ClockedRefusalKind = 'ClockedError') {
    super(message);
    this.kind = kind;
  }
}

/** One request would cross more surfaces of one relation or one
 * constraint than the machine's own `limits.max_crossings` admits. The
 * request committed nothing. */
export class TooManyEvents extends ClockedError {
  constructor(message: string) { super(message, 'TooManyEvents'); }
}

/** Two relations wrote one id at one landing, or a commit computed a
 * value that is not a value a machine can stand at. The request
 * committed nothing. */
export class ClockedConflict extends ClockedError {
  constructor(message: string) { super(message, 'ClockedError'); }
}

/** A COMMIT inside a request carried a compiled coordinate outside its
 * declared bound, judged over the final bank (design §8). The request
 * committed nothing and never posed. */
export class ClockedRangeError extends ClockedError {
  constructor(message: string) { super(message, 'JointRangeError'); }
}

/** A request this machine has no meaning for: an input it does not
 * declare, a state named as an input, `by` and `to` together or
 * neither, or -- in this build -- a request on the clock. */
export class ClockedRequestError extends ClockedError {
  constructor(message: string) { super(message, 'ValueError'); }
}

// ---------------------------------------------------------------------
// What the document publishes, as this module holds it
// ---------------------------------------------------------------------

/** One committing relation, compiled against one clocked document
 * (`simulation/clocked.py`'s `Committing`). */
export interface LoadedCommit {
  sources: readonly string[];
  targets: readonly string[];
  /** The event level's own jump: its primitive and its published level
   * expression. */
  primitive: JumpPrimitive;
  level: string;
  /** One published expression per target, aligned with `targets`. */
  law: readonly string[];
  /** Per INPUT that can move this level, the jump its events are
   * located on -- typed by the published `shapes` entry and never by a
   * classification made here. An input absent from this map cannot move
   * the level and is not examined for it (`Committing.moves_with`). */
  jumps: ReadonlyMap<string, ProgramJump>;
  description: string;
  statedBy: string;
}

/** One compiled constraint's plan as ONE moving input sees it
 * (`Bounded.plans`, `Bounded.shapes`, `Bounded.kinks`). */
export interface BoundPlan {
  plan: ProgramPlan;
  /** The SKELETON's shape in this input, as published. */
  shape: PathShape;
  /** The skeleton's kinks, derived from the published skeleton -- `null`
   * unless `shape` is `'kinked'`. */
  kinks: readonly KinkLevel[] | null;
}

/** One side of one bounded coordinate's declared range, as the level a
 * request is clipped against (`simulation/clocked.py`'s `Bounded`). */
export interface LoadedBound {
  coordinate: string;
  side: 'low' | 'high';
  unit: string | null;
  /** The published CHAIN: the bounded coordinate composed down to
   * declared drivers and states. */
  chain: string;
  /** The declared bound, with its own coordinate under the reserved
   * own-name and each read already substituted by its own chain. */
  bound: string;
  /** The LEVEL, which the CONSUMER forms: `value - bound` on the high
   * side, `bound - value` on the low (ADR-128 §7, "publishing it as
   * well would publish the bound twice"). */
  level: string;
  /** The published jump plan of that level, or `null` where it carries
   * no jump. */
  plan: ProgramPlan | null;
  /** Per input that can move the level, the plan re-shaped for it. An
   * input absent from this map leaves the level CONSTANT along the
   * path: it is not examined during the clip, and is judged only at the
   * end of the request (`Bounded.moves_with`). */
  plans: ReadonlyMap<string, BoundPlan>;
  /** The bank ids the LEVEL reads, the own-name excluded, sorted. */
  names: readonly string[];
  /** The bank ids the CHAIN reads, sorted. */
  chainNames: readonly string[];
  node: string;
  joint: string;
  description: string;
}

/** A version 8 document's compiled machine, loaded and validated.
 *
 * Satisfies `PathHost`, which is what lets the clip call the run's own
 * `planPartition` and `branchesAt` rather than a second partition. */
export interface LoadedMachine extends PathHost {
  identity: string;
  /** The free name elapsed seconds bind to, or `null` for a machine
   * that declares no time base. */
  clock: string | null;
  /** The free name every bound reads its own coordinate under, bound for
   * the length of one request. */
  own: string;
  /** The bank's id order, DERIVED (design §2): the drivers table's key
   * order, then the states table's, then the clock. */
  order: readonly string[];
  drivers: Readonly<Record<string, ManifestDriver>>;
  states: Readonly<Record<string, ManifestDriver>>;
  instructions: Readonly<Record<string, ManifestInstruction>>;
  /** Every id at its published default, and the clock at zero. */
  initial: Readonly<Record<string, number>>;
  commits: readonly LoadedCommit[];
  bounds: readonly LoadedBound[];
  /** Every id an expression of this document may name: the bank's ids.
   * A plan's branch placeholders are legal only inside that plan. */
  declaredNames: ReadonlySet<string>;
  /** Every branch placeholder, and the plan that binds it. */
  placeholders: ReadonlyMap<string, ProgramPlan>;
}

/** A version 8 document, as far as the clocked machine is concerned. */
export interface ClockedDocument extends Omit<Partial<Manifest>, 'version'> {
  version: number;
  states?: unknown;
  clocked?: unknown;
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

const PATH_SHAPES: readonly string[] = ['constant', 'affine', 'kinked'];

/** The jump primitives an EVENT may be stated with (`_EVENT_CALLS` and
 * `_EVENT_OPERATORS`). `%` is deliberately absent: `a % b` is not
 * integer valued, so it is not a level whose steps are events. */
const EVENT_PRIMITIVES: readonly string[] = [
  'floor', 'ceil', 'sign', '<', '<=', '>', '>=', '==', '!=',
];

/** Read `document`'s compiled clocked machine, or refuse it by name.
 *
 * `bindings` is the document's own table, already built and validated:
 * every expression slot below is a STRING naming bank ids and
 * `bindings` entries, exactly as a published program's is, and reaches
 * the same interning the run already uses. */
export function loadClocked(document: ClockedDocument, sourceUrl: string,
                            bindings: BindingTable): LoadedMachine {
  return withExpressions(() => loadClockedScoped(document, sourceUrl, bindings));
}

function loadClockedScoped(document: ClockedDocument, sourceUrl: string,
                            bindings: BindingTable): LoadedMachine {
  const refuse = (reason: string): never => {
    throw new ClockedError(
      `${sourceUrl} carries a clocked machine this viewer cannot ` +
      `execute: ${reason}. Refusing the document rather than running ` +
      'part of a machine it does not understand.');
  };

  if (document.program !== undefined) {
    refuse('it carries a `program` object as well as a `clocked` one, ' +
           'which is two machines. A root publishes one or the other: ' +
           'version 8 is a property of the ROOT\'S DECLARATION, and it ' +
           'dominates');
  }
  const raw = document.clocked;
  if (raw === undefined) {
    refuse('it declares version 8 and carries no `clocked` object. A ' +
           'clocked document carries its compiled machine, exactly as a ' +
           'version 5 document carries its `program`');
  }
  if (!isObject(raw)) {
    refuse(`its \`clocked\` is ${quoted(raw)}, not an object`);
  }
  const clocked = raw as Record<string, unknown>;

  if (typeof clocked.identity !== 'string' || clocked.identity === '') {
    refuse(`its \`clocked.identity\` is ${quoted(clocked.identity)}, not a ` +
           'string');
  }
  if (clocked.clock !== null && typeof clocked.clock !== 'string') {
    refuse(`its \`clocked.clock\` is ${quoted(clocked.clock)}, which is ` +
           'neither a name nor null');
  }
  if (typeof clocked.own !== 'string' || clocked.own === '') {
    refuse(`its \`clocked.own\` is ${quoted(clocked.own)}, not the reserved ` +
           'name a bound reads its own coordinate under');
  }
  const identity = clocked.identity as string;
  const clock = clocked.clock as string | null;
  const own = clocked.own as string;

  // --- the two tables -----------------------------------------------
  const drivers = readDeclarations(document.drivers, 'drivers', refuse);
  const states = readDeclarations(
    (document as { states?: unknown }).states, 'states', refuse);
  for (const id of Object.keys(states)) {
    if (Object.prototype.hasOwnProperty.call(drivers, id)) {
      refuse(`the id "${id}" is declared both as a driver and as a state, ` +
             'and the bank holds one value per id');
    }
  }
  if (clock !== null) {
    if (Object.prototype.hasOwnProperty.call(drivers, clock)
        || Object.prototype.hasOwnProperty.call(states, clock)) {
      refuse(`its clock is named "${clock}", which is also a declared ` +
             'driver or state');
    }
  }

  // The bank's id order, DERIVED (design §2). Both tables are published
  // with SORTED keys, so this is deterministic for a given document and
  // stable across republication; it is the order a host reads on the
  // handle and the order a snapshot serializes in.
  const order: string[] = [
    ...Object.keys(drivers), ...Object.keys(states),
    ...(clock === null ? [] : [clock]),
  ];
  const initial: Record<string, number> = {};
  for (const [id, declaration] of Object.entries(drivers)) {
    initial[id] = declaration.default;
  }
  for (const [id, declaration] of Object.entries(states)) {
    initial[id] = declaration.default;
  }
  // Under an elapsed base the clock stands at ZERO, which is the instant
  // the rest pose is defined at (ADR-127).
  if (clock !== null) initial[clock] = 0;

  const declaredNames = new Set(order);

  // --- the expression store ------------------------------------------
  const nodeOf = (expression: string): NodeId =>
    withExpressions(() => prepare(expression));

  /** Every free name of `expression`, closed over the bindings table:
   * a binding name resolves away to what it transitively reads. */
  const namesOf = (expression: string): Set<string> =>
    new Set(bindings.closure(freeVariables(expression)));

  const assertNames = (expression: string, allowed: ReadonlySet<string>,
                       where: string): void => {
    for (const name of namesOf(expression)) {
      if (!allowed.has(name)) {
        refuse(`${where} reads "${name}", which this machine declares ` +
               `nowhere; its bank is: ${order.join(', ') || 'none'}`);
      }
    }
    // Interning also VALIDATES: an expression form this evaluator cannot
    // read is refused here rather than met mid-request.
    nodeOf(expression);
  };

  // --- the limits ----------------------------------------------------
  const rawLimits = clocked.limits;
  if (!isObject(rawLimits)) {
    refuse(`its \`clocked.limits\` is ${quoted(rawLimits)}, not an object`);
  }
  const limitsObject = rawLimits as Record<string, unknown>;
  const finite = (key: string): number => {
    const value = limitsObject[key];
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      refuse(`its \`clocked.limits.${key}\` is ${quoted(value)}, not a ` +
             'finite number');
    }
    return value as number;
  };
  const limits: ProgramLimits = {
    crossingTolerance: finite('crossing_tolerance'),
    maxCrossings: finite('max_crossings'),
    // A clocked level is SOLVED, never sampled or bisected: every
    // published shape is `constant`, `affine` or `kinked`, and anything
    // else is refused below, so the sampling constants a running
    // document publishes have no counterpart here and no clocked path
    // reaches them. They are NaN rather than an invented number,
    // because a number invented here would be a sampling resolution
    // this document never stated (design §1).
    subdivisions: NaN,
    bisectionRounds: NaN,
    agreement: NaN,
  };

  const host: PathHost = { limits, bindings, nodeOf };
  const placeholders = new Map<string, ProgramPlan>();

  // --- the commits ---------------------------------------------------
  const rawCommits = clocked.commits;
  if (!Array.isArray(rawCommits)) {
    refuse(`its \`clocked.commits\` is ${quoted(rawCommits)}, not a list`);
  }
  const commits = (rawCommits as unknown[]).map((entry, index) =>
    readCommit(entry, index, {
      refuse, drivers, states, clock, order, declaredNames, namesOf,
      assertNames, nodeOf, bindings,
    }));

  // --- the bounds ----------------------------------------------------
  const rawBounds = clocked.bounds;
  if (!Array.isArray(rawBounds)) {
    refuse(`its \`clocked.bounds\` is ${quoted(rawBounds)}, not a list`);
  }
  const bounds = (rawBounds as unknown[]).map((entry, index) =>
    readBound(entry, index, {
      refuse, drivers, clock, own, declaredNames, namesOf, assertNames,
      nodeOf, bindings, placeholders, order, limits,
    }));

  return {
    identity,
    clock,
    own,
    order,
    drivers,
    states,
    instructions: readInstructions(document.instructions, refuse, drivers,
                                   states, clock),
    initial,
    commits,
    bounds,
    declaredNames,
    placeholders,
    limits: host.limits,
    bindings,
    nodeOf,
  };
}

type Refuse = (reason: string) => never;

/** A driver or state table, read field by field. ADR-128 §3 publishes a
 * state in the SAME five fields as a driver, with the same meanings, so
 * this reads both. */
function readDeclarations(raw: unknown, key: string,
                          refuse: Refuse): Record<string, ManifestDriver> {
  if (raw === undefined) {
    refuse(`it carries no \`${key}\` table; a version 8 document publishes ` +
           'one for each, even when it is empty');
  }
  if (!isObject(raw)) {
    refuse(`its \`${key}\` is ${quoted(raw)}, not an object`);
  }
  const found: Record<string, ManifestDriver> = {};
  for (const [id, entry] of Object.entries(raw as Record<string, unknown>)) {
    if (!isObject(entry)) {
      refuse(`its \`${key}.${id}\` is ${quoted(entry)}, not a declaration`);
    }
    const declaration = entry as Record<string, unknown>;
    if (typeof declaration.default !== 'number'
        || !Number.isFinite(declaration.default)) {
      refuse(`its \`${key}.${id}.default\` is ` +
             `${quoted(declaration.default)}, not a finite number`);
    }
    if (declaration.range !== null
        && !(Array.isArray(declaration.range)
             && declaration.range.length === 2
             && declaration.range.every(
               (one) => one === null || typeof one === 'number'))) {
      refuse(`its \`${key}.${id}.range\` is ${quoted(declaration.range)}, ` +
             'which is neither null nor a pair');
    }
    if (declaration.unit !== null && typeof declaration.unit !== 'string') {
      refuse(`its \`${key}.${id}.unit\` is ${quoted(declaration.unit)}`);
    }
    if (declaration.dtype !== null && declaration.dtype !== 'int'
        && declaration.dtype !== 'float') {
      refuse(`its \`${key}.${id}.dtype\` is ${quoted(declaration.dtype)}, ` +
             'which is neither "int", "float" nor null');
    }
    if (declaration.scale !== null
        && (typeof declaration.scale !== 'number'
            || !Number.isFinite(declaration.scale))) {
      refuse(`its \`${key}.${id}.scale\` is ${quoted(declaration.scale)}, ` +
             'which is neither a finite number nor null');
    }
    found[id] = {
      default: declaration.default as number,
      range: declaration.range as number[] | null,
      unit: declaration.unit as string | null,
      dtype: declaration.dtype as string | null,
      scale: declaration.scale as number | null,
    };
  }
  return found;
}

/** The instruction table of a version 8 document, read and VALIDATED
 * against what this viewer can play (OpenSpec `play-the-instruction`,
 * design §10).
 *
 * `drivers`, `states` and `clock` are the machine's own tables, already
 * read: an instruction naming a state, the clock, or a name nothing
 * declares is refused HERE, by name, on the surface a malformed
 * `clocked` object is already refused on. A producer's compile refuses
 * each of these before a document exists, so a document carrying one is
 * one this viewer cannot trust to say what a press MEANS -- and
 * refusing it keeps `published implies playable` reaching the chrome,
 * which therefore needs no arity logic of its own. */
function readInstructions(raw: unknown, refuse: Refuse,
                          drivers: Record<string, ManifestDriver>,
                          states: Record<string, ManifestDriver>,
                          clock: string | null):
Record<string, ManifestInstruction> {
  if (raw === undefined) return {};
  if (!isObject(raw)) {
    refuse(`its \`instructions\` is ${quoted(raw)}, not an object`);
  }
  const found: Record<string, ManifestInstruction> = {};
  for (const [name, entry] of Object.entries(raw as Record<string, unknown>)) {
    if (!isObject(entry)) {
      refuse(`its \`instructions.${name}\` is ${quoted(entry)}`);
    }
    const where = `its \`instructions.${name}\``;
    const at = (key: string): string => `its \`instructions.${name}.${key}\``;
    const instruction = entry as Record<string, unknown>;
    const relative = instruction.by !== undefined;
    if (relative === (instruction.targets !== undefined)) {
      refuse(`${where} states ${relative ? 'BOTH a travel AND a landing'
        : 'NEITHER a travel NOR a landing'}: an instruction states ` +
             'exactly one of `by` and `targets` -- how far its driver ' +
             'travels, or where it lands');
    }
    const stated = relative ? instruction.by : instruction.targets;
    if (!isObject(stated)) {
      refuse(`${at(relative ? 'by' : 'targets')} is ` +
             `${quoted(stated)}, not an object`);
    }
    const named = Object.keys(stated as Record<string, unknown>);
    if (named.length !== 1) {
      refuse(`${where} names ${named.length} drivers ` +
             `(${named.map((one) => `"${one}"`).join(', ') || 'none'}); ` +
             'an instruction under a clocked root is ONE request over ONE ' +
             'driver, and sequencing several is a program\'s job');
    }
    const [inputId] = named;
    if (!Object.prototype.hasOwnProperty.call(drivers, inputId)) {
      if (Object.prototype.hasOwnProperty.call(states, inputId)) {
        refuse(`${where} names "${inputId}", which is a declared state ` +
               'and not a driver: a state is written by the machine at an ' +
               'event, and a request moves a DRIVER');
      }
      if (clock !== null && inputId === clock) {
        refuse(`${where} names "${inputId}", which is this machine\'s ` +
               'clock: elapsed seconds are advanced by the transport and ' +
               'by nothing else, and no instruction may name them');
      }
      refuse(`${where} names "${inputId}", which this machine declares ` +
             `nowhere; declared: ${Object.keys(drivers).sort().join(', ')
               || 'none'}`);
    }
    const amount = (stated as Record<string, unknown>)[inputId];
    if (typeof amount !== 'number' || !Number.isFinite(amount)) {
      refuse(`${where} states ${quoted(amount)} for "${inputId}", which is ` +
             'not a finite number of design units');
    }
    const duration = instruction.duration;
    if (typeof duration !== 'number' || !Number.isFinite(duration)
        || duration < 0) {
      refuse(`${at('duration')} is ${quoted(duration)}, not a finite ` +
             'number of seconds at or above zero; a duration is how long a ' +
             'consumer DRAWS the transition, and zero lands it at once');
    }
    found[name] = entry as unknown as ManifestInstruction;
  }
  return found;
}

interface CommitContext {
  refuse: Refuse;
  drivers: Record<string, ManifestDriver>;
  states: Record<string, ManifestDriver>;
  clock: string | null;
  order: readonly string[];
  declaredNames: ReadonlySet<string>;
  namesOf(expression: string): Set<string>;
  assertNames(expression: string, allowed: ReadonlySet<string>,
              where: string): void;
  nodeOf(expression: string): NodeId;
  bindings: BindingTable;
}

function readCommit(entry: unknown, index: number,
                    context: CommitContext): LoadedCommit {
  const { refuse } = context;
  const where = `its \`clocked.commits[${index}]\``;
  if (!isObject(entry)) refuse(`${where} is ${quoted(entry)}, not an object`);
  const commit = entry as Record<string, unknown>;
  const idList = (key: string): string[] => {
    const value = commit[key];
    if (!Array.isArray(value)
        || !value.every((one) => typeof one === 'string')) {
      refuse(`${where}.${key} is ${quoted(value)}, not a list of ids`);
    }
    for (const id of value as string[]) {
      if (!context.declaredNames.has(id)) {
        refuse(`${where}.${key} names "${id}", which this machine ` +
               'declares nowhere');
      }
    }
    return value as string[];
  };
  const sources = idList('sources');
  const targets = idList('targets');
  for (const id of targets) {
    if (!Object.prototype.hasOwnProperty.call(context.states, id)) {
      refuse(`${where}.targets names "${id}", which is not a declared ` +
             'state; a relation commits STATES');
    }
  }
  const at = commit.at;
  if (!isObject(at)) refuse(`${where}.at is ${quoted(at)}, not an object`);
  const atObject = at as Record<string, unknown>;
  const primitive = atObject.primitive;
  if (typeof primitive !== 'string'
      || !EVENT_PRIMITIVES.includes(primitive)) {
    refuse(`${where}.at.primitive is ${quoted(primitive)}; an event is ` +
           `stated with one of ${EVENT_PRIMITIVES.join(', ')}`);
  }
  if (typeof atObject.level !== 'string') {
    refuse(`${where}.at.level is ${quoted(atObject.level)}, not an ` +
           'expression');
  }
  const level = atObject.level as string;
  context.assertNames(level, context.declaredNames, `${where}.at.level`);

  const law = commit.law;
  if (!Array.isArray(law) || !law.every((one) => typeof one === 'string')) {
    refuse(`${where}.law is ${quoted(law)}, not a list of expressions`);
  }
  if ((law as string[]).length !== targets.length) {
    refuse(`${where}.law carries ${(law as string[]).length} expressions ` +
           `for ${targets.length} targets; a published law is one ` +
           'expression per target, aligned with `targets`');
  }
  for (const expression of law as string[]) {
    context.assertNames(expression, context.declaredNames, `${where}.law`);
  }

  const shapes = commit.shapes;
  if (!isObject(shapes)) {
    refuse(`${where}.shapes is ${quoted(shapes)}, not an object`);
  }
  const jumps = new Map<string, ProgramJump>();
  for (const [input, shape] of Object.entries(
    shapes as Record<string, unknown>)) {
    if (!Object.prototype.hasOwnProperty.call(context.drivers, input)
        && input !== context.clock) {
      refuse(`${where}.shapes names "${input}", which is neither a ` +
             'declared driver nor this machine\'s clock');
    }
    // A COMMIT's `shapes` publishes only the two shapes a level whose
    // crossings are located may have; `constant` is a BOUND's reading
    // alone (`_published_commit` against `_published_bound`).
    if (shape !== 'affine' && shape !== 'kinked') {
      refuse(`${where}.shapes.${input} is ${quoted(shape)}; a commit's ` +
             'level is published `affine` or `kinked`');
    }
    jumps.set(input, {
      name: `${index}:at`,
      primitive: primitive as JumpPrimitive,
      level,
      // `_Jump.affine` is `shape in ('constant', 'affine')`.
      affine: shape === 'affine',
      shape: shape as PathShape,
      kinks: shape === 'kinked'
        ? retainedKinkLevels(level, context.bindings.roots) : null,
    });
  }

  if (typeof commit.description !== 'string') {
    refuse(`${where}.description is ${quoted(commit.description)}`);
  }
  if (typeof commit.stated_by !== 'string') {
    refuse(`${where}.stated_by is ${quoted(commit.stated_by)}`);
  }
  return {
    sources,
    targets,
    primitive: primitive as JumpPrimitive,
    level,
    law: law as string[],
    jumps,
    description: commit.description as string,
    statedBy: commit.stated_by as string,
  };
}

interface BoundContext {
  refuse: Refuse;
  drivers: Record<string, ManifestDriver>;
  /** The machine's clock name, or `null`. A compiled CONSTRAINT may not
   * name it anywhere (`run-the-clock`, design §4). */
  clock: string | null;
  own: string;
  declaredNames: ReadonlySet<string>;
  namesOf(expression: string): Set<string>;
  assertNames(expression: string, allowed: ReadonlySet<string>,
              where: string): void;
  nodeOf(expression: string): NodeId;
  bindings: BindingTable;
  placeholders: Map<string, ProgramPlan>;
  order: readonly string[];
  limits: ProgramLimits;
}

function readBound(entry: unknown, index: number,
                   context: BoundContext): LoadedBound {
  const { refuse, own } = context;
  const where = `its \`clocked.bounds[${index}]\``;
  if (!isObject(entry)) refuse(`${where} is ${quoted(entry)}, not an object`);
  const bound = entry as Record<string, unknown>;
  const text = (key: string): string => {
    const value = bound[key];
    if (typeof value !== 'string' || value === '') {
      refuse(`${where}.${key} is ${quoted(value)}, not a string`);
    }
    return value as string;
  };
  const coordinate = text('coordinate');
  const side = bound.side;
  if (side !== 'low' && side !== 'high') {
    refuse(`${where}.side is ${quoted(side)}, which is neither "low" nor ` +
           '"high"');
  }
  if (bound.unit !== null && typeof bound.unit !== 'string') {
    refuse(`${where}.unit is ${quoted(bound.unit)}`);
  }
  const chain = text('value');
  // A `bound` slot is a NUMBER where the declaration was a plain one,
  // and an EXPRESSION reading the own-name and the bank where it was
  // stated as one (design §8). A number is turned into its own literal
  // text so the LEVEL below is one expression, and the literal is
  // CHECKED to read back as the very same double -- a bound this
  // evaluator could not re-read exactly is refused rather than clipped
  // against a value the document did not state.
  let declared: string;
  if (typeof bound.bound === 'number') {
    if (!Number.isFinite(bound.bound)) {
      refuse(`${where}.bound is ${quoted(bound.bound)}, not a finite number`);
    }
    declared = String(bound.bound);
    const read = evaluateExpression(
      { limits: context.limits, bindings: context.bindings,
        nodeOf: context.nodeOf }, declared, {});
    if (read !== bound.bound) {
      refuse(`${where}.bound is ${quoted(bound.bound)}, which this ` +
             `evaluator reads back as ${read}`);
    }
  } else {
    declared = text('bound');
  }
  const node = text('node');
  const joint = text('joint');
  const description = text('description');

  // The LEVEL is the CONSUMER'S OWN SUBTRACTION (ADR-128 §7): `value -
  // bound` on the high side, `bound - value` on the low. Publishing it
  // as well would publish the bound twice.
  const level = side === 'high'
    ? `(${chain} - ${declared})` : `(${declared} - ${chain})`;

  const overTheBank = new Set([...context.declaredNames, own]);
  // NOTHING STOPS A CLOCK, guarded at the LOAD (`run-the-clock`,
  // design §4; machinome ADR-127). The producer cannot write a
  // constraint that follows the clock: `compile_bounds` builds its
  // chains over the drivers and the states and NOT the clock
  // (`clocked.py:1368-1377`), and `_over_the_bank` refuses any free name
  // that survives a composed chain and is not a bank id
  // (`clocked.py:1448-1487`). A hand-written or corrupted document
  // could, and would then be CLIPPED against a coordinate the clock
  // drives -- so the consumer refuses exactly what the producer does,
  // rather than being silently wider.
  //
  // `declaredNames` is NOT narrowed: the clock is a bank id and a legal
  // name in a commit's level, in a commit's law and in the tree's own
  // pose expressions. The refusal belongs where the fact is.
  const clock = context.clock;
  if (clock !== null) {
    const clockIn = (expression: string, key: string): void => {
      if (!context.namesOf(expression).has(clock)) return;
      context.refuse(
        `${where}.${key} reads "${clock}", which is this machine's CLOCK. ` +
        'A published constraint may not follow it: a stop is compiled over ' +
        'the bank -- the drivers and the states -- and a clock-driven ' +
        'coordinate is not something a stop can hold, because a declared ' +
        'range is a MECHANICAL stop and nothing is in the way of the next ' +
        'second');
    };
    clockIn(chain, 'value');
    clockIn(declared, 'bound');
    // The level is the consumer's own subtraction of the two above, so
    // this can only fire where one of them already did -- it is here
    // because the contract names all three.
    clockIn(level, 'level');
  }
  context.assertNames(chain, context.declaredNames, `${where}.value`);
  context.assertNames(declared, overTheBank, `${where}.bound`);
  context.assertNames(level, overTheBank, `${where}'s level`);

  const names = [...context.namesOf(level)]
    .filter((name) => name !== own).sort();
  const chainNames = [...context.namesOf(chain)].sort();

  // --- the published plan --------------------------------------------
  const rawPlan = bound.plan;
  let plan: ProgramPlan | null = null;
  let published: { name: string; primitive: JumpPrimitive;
                   level: string; affine: boolean; }[] = [];
  let skeleton = level;
  if (rawPlan !== null) {
    if (!isObject(rawPlan)) {
      refuse(`${where}.plan is ${quoted(rawPlan)}, which is neither a plan ` +
             'nor null');
    }
    const planObject = rawPlan as Record<string, unknown>;
    if (typeof planObject.skeleton !== 'string') {
      refuse(`${where}.plan.skeleton is ${quoted(planObject.skeleton)}`);
    }
    skeleton = planObject.skeleton as string;
    if (!Array.isArray(planObject.jumps)) {
      refuse(`${where}.plan.jumps is ${quoted(planObject.jumps)}, not a list`);
    }
    published = (planObject.jumps as unknown[]).map((one, at) => {
      if (!isObject(one)) {
        refuse(`${where}.plan.jumps[${at}] is ${quoted(one)}`);
      }
      const jump = one as Record<string, unknown>;
      if (typeof jump.name !== 'string' || jump.name === '') {
        refuse(`${where}.plan.jumps[${at}].name is ${quoted(jump.name)}`);
      }
      if (typeof jump.primitive !== 'string'
          || !(JUMP_PRIMITIVES as readonly string[]).includes(jump.primitive)) {
        refuse(`${where}.plan.jumps[${at}].primitive is ` +
               `${quoted(jump.primitive)}; this engine reads ` +
               `${JUMP_PRIMITIVES.join(', ')}`);
      }
      if (typeof jump.level !== 'string') {
        refuse(`${where}.plan.jumps[${at}].level is ${quoted(jump.level)}`);
      }
      if (typeof jump.affine !== 'boolean') {
        refuse(`${where}.plan.jumps[${at}].affine is ${quoted(jump.affine)}`);
      }
      return {
        name: jump.name as string,
        primitive: jump.primitive as JumpPrimitive,
        level: jump.level as string,
        affine: jump.affine as boolean,
      };
    });
    // A jump's own level may name the plan's EARLIER placeholders, as
    // the skeleton may name all of them: a node nested inside another's
    // argument is determined first, which is the postorder the plan is
    // published in.
    const inside = new Set(overTheBank);
    published.forEach((jump, at) => {
      context.assertNames(jump.level, inside,
                          `${where}.plan.jumps[${at}].level`);
      if (inside.has(jump.name)) {
        refuse(`${where}.plan declares the placeholder "${jump.name}" twice`);
      }
      inside.add(jump.name);
    });
    context.assertNames(skeleton, inside, `${where}.plan.skeleton`);
  }

  // --- the per-input readings -----------------------------------------
  const rawShapes = bound.shapes;
  if (!isObject(rawShapes)) {
    refuse(`${where}.shapes is ${quoted(rawShapes)}, not an object`);
  }
  const plans = new Map<string, BoundPlan>();
  for (const [input, reading] of Object.entries(
    rawShapes as Record<string, unknown>)) {
    if (!Object.prototype.hasOwnProperty.call(context.drivers, input)) {
      // The clock is the case a reader will actually meet, so it is said
      // rather than lumped in with "not a declared driver".
      if (input === context.clock) {
        refuse(`${where}.shapes names "${input}", which is this machine's ` +
               'CLOCK. A published constraint may not be moved by it: a ' +
               'stop is compiled over the bank -- the drivers and the ' +
               'states -- and nothing is in the way of the next second, so ' +
               'no declared stop ever clips a request that moves the clock');
      }
      refuse(`${where}.shapes names "${input}", which is not a declared ` +
             'driver');
    }
    if (!isObject(reading)) {
      refuse(`${where}.shapes.${input} is ${quoted(reading)}, not an object`);
    }
    const shapes = reading as Record<string, unknown>;
    // A BOUND's `shapes` admits `constant` as well as `affine` and
    // `kinked`, where a commit's publishes only the latter two: a
    // level a driver moves only THROUGH ITS JUMPS is `constant` in it,
    // which `Calculator`'s freeze publishes (design §8).
    if (typeof shapes.level !== 'string'
        || !PATH_SHAPES.includes(shapes.level)) {
      refuse(`${where}.shapes.${input}.level is ${quoted(shapes.level)}; ` +
             `a constraint level is published ${PATH_SHAPES.join(', ')}`);
    }
    if (!Array.isArray(shapes.jumps)
        || (shapes.jumps as unknown[]).length !== published.length) {
      refuse(`${where}.shapes.${input}.jumps is ${quoted(shapes.jumps)}, ` +
             `not one shape for each of the plan's ${published.length} jumps`);
    }
    const jumpShapes = (shapes.jumps as unknown[]).map((one, at) => {
      if (typeof one !== 'string' || !PATH_SHAPES.includes(one)) {
        refuse(`${where}.shapes.${input}.jumps[${at}] is ${quoted(one)}; ` +
               `a jump's level is published ${PATH_SHAPES.join(', ')}`);
      }
      return one as PathShape;
    });
    const jumps: ProgramJump[] = published.map((jump, at) => ({
      name: jump.name,
      primitive: jump.primitive,
      level: jump.level,
      // `_Jump.affine` is `shape in ('constant', 'affine')` -- the
      // shape THIS INPUT sees, not the plan's published two-valued
      // flag, because a request solves over the per-input plan.
      affine: jumpShapes[at] !== 'kinked',
      shape: jumpShapes[at],
      kinks: jumpShapes[at] === 'kinked'
        ? retainedKinkLevels(jump.level, context.bindings.roots)
        : null,
    }));
    const shape = shapes.level as PathShape;
    plans.set(input, {
      plan: {
        skeleton,
        jumps,
        shape,
        kinks: shape === 'kinked'
          ? retainedKinkLevels(skeleton, context.bindings.roots)
          : null,
      },
      shape,
      kinks: shape === 'kinked'
        ? retainedKinkLevels(skeleton, context.bindings.roots)
        : null,
    });
  }

  if (rawPlan !== null) {
    // The plan AS PUBLISHED, carrying the producer's own two-valued
    // `affine` flag: what a reader sees, and what the placeholders
    // register against. A request never solves over it -- it solves
    // over the per-input plan above, whose jumps carry the shape THAT
    // INPUT sees.
    plan = {
      skeleton,
      jumps: published.map((jump) => ({
        ...jump, shape: null as PathShape, kinks: null,
      })),
      shape: null,
      kinks: null,
    };
    for (const jump of published) {
      context.placeholders.set(jump.name, plan);
    }
  }

  return {
    coordinate,
    side: side as 'low' | 'high',
    unit: bound.unit as string | null,
    chain,
    bound: declared,
    level,
    plan,
    plans,
    names,
    chainNames,
    node,
    joint,
    description,
  };
}
