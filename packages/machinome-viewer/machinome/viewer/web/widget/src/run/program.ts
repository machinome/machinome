/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The compiled program, loaded from a version 5 document (design §4).
//
// Reproduces what machinome's `simulation/program.py` `Program`
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
  expressionGeneration, kinkLevels, NodeId, prepare, shapeOf, structureOf,
  valueOf,
} from '../expressions';
import type { KinkLevel, PathShape } from '../expressions';
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

/** A self-read cut placed the driven coordinate NOWHERE
 * (`simulation/program.py`'s `LandingInvariantError`).
 *
 * The landing is bracketed by stepping out from the segment's own
 * arithmetic with the stride doubling from one ulp, and 200 doublings
 * cover every distance a double can express. A cut exists because the
 * level crossed the surface, so the branch differs somewhere on either
 * side of it and a bracket is found by construction. This is therefore a
 * broken invariant of the run rather than a dt that is too coarse -- the
 * `StopInvariantError` it is modelled on says the same of a stop -- and
 * it is raised rather than committing a value the design says is never
 * committed. The tick committed nothing. */
export class LandingInvariantError extends Error {
  readonly kind = 'landing';
}

/** Every refusal a TICK can make, as the protocol reports it. */
export type RefusalKind =
  'law' | 'crossings' | 'conflict' | 'stop' | 'landing';

export function refusalKind(error: unknown): RefusalKind | null {
  if (error instanceof UnsupportedLaw) return 'law';
  if (error instanceof TooManyCrossings) return 'crossings';
  if (error instanceof RunConflict) return 'conflict';
  if (error instanceof StopInvariantError) return 'stop';
  if (error instanceof LandingInvariantError) return 'landing';
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

/** `block` is DERIVED by the loader and never published: a document
 * declaring `kind: "block"` is refused as an unknown kind exactly as it
 * always was, because `EDGE_KINDS` -- which validates the PUBLISHED kind
 * -- does not carry it (design D1.3). */
export type EdgeKind = 'law' | 'wiring' | 'formula' | 'check' | 'block';

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
  /** This LEVEL quantity's shape along the path, DERIVED at load from
   * the published expression (openspec `solve-at-the-kink`, design D1).
   * The published `affine` flag above is two-valued and says nothing
   * about a quantity that is not affine; this says whether it is
   * PIECEWISE affine, and so solvable at its own kinks. */
  shape: PathShape;
  /** The kinks of that level, in the expression's own postorder --
   * `null` unless `shape` is `'kinked'`. */
  kinks: readonly KinkLevel[] | null;
}

export interface ProgramPlan {
  skeleton: string;
  jumps: ProgramJump[];
  /** The SKELETON's shape along the path, derived at load under this
   * plan's own jump names as the constants (design D1). */
  shape: PathShape;
  /** The skeleton's kinks -- `null` unless `shape` is `'kinked'`. */
  kinks: readonly KinkLevel[] | null;
}

/** How ONE driven end whose own law READS it is integrated
 * (`simulation/program.py`'s `_Retained`), derived at LOAD from the
 * published plan and the document's bindings table.
 *
 * The plan's jump nodes that do NOT depend on the driven coordinate keep
 * ADR-107's whole partition -- built by `partition` itself, over a plan
 * of exactly that subset -- and the ones that DO are WALKED inside each
 * of its pieces, their branches read at the piece's LEFT END from the
 * value the coordinate RETAINS there. A midpoint is no use to a
 * dependent node: the coordinate's value there is a consequence of the
 * branch being asked for. */
export interface RetainedReading {
  /** The driven id, which is `edge.gives[index]`. */
  own: string;
  /** The plan's jumps that DEPEND on `own`, in the plan's own postorder. */
  dependent: ProgramJump[];
  /** The plan with only the INDEPENDENT jumps -- a well formed plan of
   * its own, because dependence is upward closed along the nesting. */
  outer: ProgramPlan;
  /** Whether the SKELETON is affine along the path. READ off the edge's
   * published per-end `affine` flag, never recomputed: for a
   * plan-bearing law that flag IS `_affine_in_sources(plan.skeleton)`
   * (`Edge._affine_ends`). */
  affine: boolean;
  /** The SKELETON's own shape, DERIVED (design D1): what decides whether
   * the driven coordinate's own path is affine in `t` on a piece, and so
   * whether a dependent level's crossing is solved or searched. The FULL
   * plan's skeleton under the FULL plan's jump names -- `outer` holds
   * the same text, and a placeholder of a dependent node is a constant
   * of the piece just as an independent one is. */
  shape: PathShape;
  kinks: readonly KinkLevel[] | null;
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
  /** One SHAPE per driven end, derived at load (design D1): the plan's
   * skeleton where the end carries a plan, the published expression
   * where it carries none, and `null` for every kind but a law. Read
   * beside the published flag by `Run.locate`, which solves a stop on a
   * KINKED end as it already solves one on an affine end. */
  shapes: PathShape[];
  /** That end's kinks -- `null` unless its shape is `'kinked'`. */
  kinks: (readonly KinkLevel[] | null)[];
  plans: (ProgramPlan | null)[];
  /** The driven ends this edge's own law READS -- the `gives` whose id
   * is also one of its `needs` -- each with the two-layer reading of its
   * plan, derived once at load. EMPTY for every other edge, which is the
   * one test `edgeIncrements` makes before taking ADR-107's path
   * unchanged. */
  retained: (RetainedReading | null)[];
  /** A wiring's one factor; a formula's or check's per-need factors. */
  factor: number;
  factors: number[];
  constant: number;
  slot: string | null;
  /** The `_Block` reading for a compound BLOCK edge, and `null` for
   * every other kind: a block is ONE entry of the program, so the
   * loader contracts the cycle and `run.ts` meets it through the edge
   * interface it already calls (design D1.3, D6). */
  block: ProgramBlock | null;
}

/** One member of a block: an ordinary law edge, its SELECTORS, and what
 * a selection can and cannot switch off what it reads (design D1.4-D1.6,
 * `simulation/program.py`'s `_Block.__init__`). */
export interface BlockMember {
  readonly edge: ProgramEdge;
  /** The member's single driven end, which is `edge.gives[0]`. */
  readonly own: string;
  /** The member's own published plan, or `null` for a law with no jump
   * in it at all. */
  readonly plan: ProgramPlan | null;
  /** The jumps of that plan whose LEVEL reads no id the block gives. */
  readonly selectors: readonly ProgramJump[];
  /** A plan of the member's SELECTORS ALONE over its own published
   * skeleton -- a well formed plan, because selectorhood is upward
   * closed along the nesting. `null` where the member carries no plan. */
  readonly selectorPlan: ProgramPlan | null;
  /** The block's ids this member reads under the ALL-ZERO fold, its own
   * driven end excluded: what no selection can switch off. */
  readonly unconditional: ReadonlySet<string>;
  /** What it reads unfolded BEYOND that: what a selection switches. */
  readonly switched: ReadonlySet<string>;
}

/** A nontrivial strongly connected component of the program's dependency
 * graph, re-derived at LOAD from the published edges' own `needs` and
 * `gives` (design D1). */
export interface ProgramBlock {
  readonly members: readonly BlockMember[];
  /** Each member's single driven end, in the members' own order. */
  readonly gives: readonly string[];
  /** The block's ids `members[index]` still READS with `forced`'s
   * placeholders holding the branches it names -- the RUN-TIME fold
   * (`_Block._order`). A member's own driven end may be in it; the
   * ordering skips it, because a read of one's own end is ADR-121's
   * self-read and not a wait on anything else. */
  activeReads(index: number, forced: Record<string, number>):
  ReadonlySet<string>;
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

/** One bound that READS OTHER COORDINATES, compiled (design D1) --
 * `simulation/program.py`'s `Constraint` dataclass, derived here rather
 * than published, because the sub-program is a filter of `edges` and the
 * candidates a union over `sources`, with no decision in either
 * (ADR-110). */
export interface Constraint {
  identifier: string;
  side: 'low' | 'high';
  /** The bound's own expression, over the bounded coordinate's id and
   * `reads`. */
  expression: string;
  /** The bindings CLOSURE of the expression's free names, minus the own
   * id, sorted (design D2). */
  reads: readonly string[];
  /** The published edges determining the bounded coordinate and every
   * read, and what those need, in the program's own order; never a
   * check. */
  edges: readonly ProgramEdge[];
  /** The sorted union of `sources` over the bounded coordinate and every
   * read. */
  candidates: readonly string[];
}

/** As much of a loaded document as the PATH primitives need: the level
 * limits, the bindings table an expression resolves through, and the
 * interned root of one published expression.
 *
 * Extracted so `partition`, `planCuts`, `branchesAt`, `kinkLevel` and
 * `evaluateExpression` can be called by a CLOCKED machine, which carries
 * no coordinates, no edges and no program at all (OpenSpec
 * `execute-the-commit`, design §8 task 6.2). `LoadedProgram` satisfies
 * it, so the running engine's every call site is unchanged and the
 * running corpus replays byte for byte. */
export interface PathHost {
  limits: ProgramLimits;
  bindings: BindingTable;
  /** One interned root per published expression, re-prepared when the
   * shared store's generation moves (design D12). */
  nodeOf(expression: string): NodeId;
}

export interface LoadedProgram extends PathHost {
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
  /** One entry per bound that reads other coordinates, keyed
   * `` `${identifier}:${side}` `` (design D1). A side that is `null`, a
   * number, or an expression naming the bounded coordinate alone makes
   * no entry. */
  constraints: ReadonlyMap<string, Constraint>;
  /** Every branch placeholder, and the plan that binds it. */
  placeholders: ReadonlyMap<string, ProgramPlan>;
  drivers: Readonly<Record<string, ManifestDriver>>;
  instructions: Readonly<Record<string, ManifestInstruction>>;
  /** Every id an expression of this document may name: the clock, the
   * bank's coordinates and the published computed values. A plan's own
   * placeholders are legal only inside that plan and are not here. */
  declaredNames: ReadonlySet<string>;
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
  program: PathHost,
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

/** A KINK's LEVEL QUANTITY at one point of the path: `x` for `abs(x)`
 * and `a - b` for `min(a, b)` and `max(a, b)`, the subtraction taken of
 * two evaluations of the SAME DAG rather than of a minted node
 * (openspec `solve-at-the-kink`, design D2; `_kink_level`).
 *
 * Here beside `evaluateExpression` because `src/run/` reaches the
 * evaluator through this module ALONE -- `edges.test.ts` asserts it
 * structurally -- and on the PLAIN evaluator, as the producer left
 * `_KinkCuts` on `GraphValue.evaluate` (design D5). */
export function kinkLevel(program: PathHost, kink: KinkLevel,
                          values: Record<string, number>): number {
  const scope = {
    time: 0,
    drivers: nest(values),
    bindings: program.bindings.roots(),
  };
  const a = Number(valueOf(kink.a, scope));
  if (kink.b === null) return a;
  return a - Number(valueOf(kink.b, scope));
}

// ---------------------------------------------------------------------
// A SELECTION: the block, its selectors and the fold (design D1;
// `simulation/program.py`'s `_FOLDABLE`, `_folded`, `_reads_under`,
// `_selectors`, `_components` and `_strongly_connected`, reproduced
// function for function).
// ---------------------------------------------------------------------

/** The jump primitives whose ZERO BRANCH is held over an INTERVAL of the
 * level quantity, and which can therefore make a source SWITCHED:
 * `floor` over `[0, 1)`, `ceil` over `(-1, 0]`, a remainder's quotient
 * over `(-1, 1)` and a comparison over the whole of its false side.
 *
 * `sign` is the one that does NOT qualify -- `branchOf` answers `0` for
 * it only where the level is EXACTLY zero, one point and not an interval
 * -- so a `sign`-gated source is never switched, and a cycle whose only
 * gate is a `sign` is refused at LOAD rather than at the first tick. */
const FOLDABLE: readonly string[] =
  ['floor', 'ceil', '%', '<', '<=', '>', '>=', '==', '!='];

interface Folded {
  readonly zero: boolean;
  readonly names: ReadonlySet<string>;
}

const NO_NAMES: ReadonlySet<string> = new Set<string>();
const ZERO_FOLD: Folded = { zero: true, names: NO_NAMES };

function unionNames(parts: readonly ReadonlySet<string>[]): ReadonlySet<string> {
  if (parts.length === 0) return NO_NAMES;
  if (parts.length === 1) return parts[0];
  const found = new Set<string>();
  for (const part of parts) {
    for (const name of part) found.add(name);
  }
  return found;
}

/** One node of the shared DAG under one substitution, as the pair
 * `(is it the literal zero, what names does it still read)` -- the
 * producer's `_folded` read for its effect on NAMES (design D1.5).
 *
 * The viewer needs only the names, never the folded tree, so the rules
 * are applied in ONE bottom-up pass over the hash-consed DAG rather than
 * by minting nodes for a value nothing evaluates.
 *
 * Two rows are deliberately NOT zero-propagating, because the producer's
 * `is_zero` is true only of a NUMERIC LITERAL: `0 - y` becomes a UNARY
 * node, never a literal, and a unary minus over a zero stays a unary
 * node for the same reason.
 *
 * A BINDING name is walked INTO rather than reported: it stands for
 * exactly the subexpression the publication extracted, which is the
 * expression the producer folds. A binding carrying a placeholder is a
 * shape the producer really emits (`CarryLead`'s `_b6 = (360.0 * _j0)`),
 * and stopping the fold at the name would leave that zero unpropagated. */
function foldedNames(root: NodeId, substitution: Record<string, number>,
                     bindings: ReadonlyMap<string, NodeId> | undefined,
                     memo: Map<NodeId, Folded>): Folded {
  const cached = memo.get(root);
  if (cached !== undefined) return cached;
  const node = structureOf(root);
  let found: Folded;
  if (node.kind === 'name') {
    const name = node.name as string;
    if (Object.prototype.hasOwnProperty.call(substitution, name)) {
      // The producer replaces a substituted placeholder with a numeric
      // literal, so it contributes no name whatever its value.
      found = { zero: substitution[name] === 0, names: NO_NAMES };
    } else {
      const binding = bindings === undefined ? undefined : bindings.get(name);
      found = binding === undefined
        ? { zero: false, names: new Set([name]) }
        : foldedNames(binding, substitution, bindings, memo);
    }
  } else if (node.kind === 'const') {
    // `float(text) == 0.0`: a literal whose numeric value is zero in any
    // spelling (`0`, `0.0`, `-0.0`).
    found = typeof node.value === 'number' && node.value === 0
      ? ZERO_FOLD
      : { zero: false, names: NO_NAMES };
  } else if (node.kind === 'binary' && node.op !== null
             && ['*', '/', '+', '-'].includes(node.op)) {
    const left = foldedNames(node.children[0], substitution, bindings, memo);
    const right = foldedNames(node.children[1], substitution, bindings, memo);
    const both = () => ({
      zero: false, names: unionNames([left.names, right.names]),
    });
    if (node.op === '*') {
      found = (left.zero || right.zero) ? ZERO_FOLD : both();
    } else if (node.op === '/') {
      found = left.zero ? ZERO_FOLD : both();
    } else if (node.op === '+') {
      if (left.zero) found = right;
      else if (right.zero) found = left;
      else found = both();
    } else if (right.zero) {
      found = left;
    } else if (left.zero) {
      found = { zero: false, names: right.names };
    } else {
      found = both();
    }
  } else {
    found = {
      zero: false,
      names: unionNames(node.children.map(
        (child) => foldedNames(child, substitution, bindings, memo).names)),
    };
  }
  memo.set(root, found);
  return found;
}

/** Every coordinate a law still READS with `substitution`'s placeholders
 * holding the branches it names: the folded skeleton's free names, with
 * every SURVIVING placeholder followed into its own folded level
 * quantity, transitively -- `_reads_under`. */
export function readsUnder(plan: ProgramPlan,
                           substitution: Record<string, number>,
                           nodeOf: (expression: string) => NodeId,
                           bindings: ReadonlyMap<string, NodeId> | undefined):
ReadonlySet<string> {
  const byName = new Map<string, ProgramJump>();
  for (const jump of plan.jumps) byName.set(jump.name, jump);
  const memo = new Map<NodeId, Folded>();
  const pending = [...foldedNames(nodeOf(plan.skeleton), substitution,
                                  bindings, memo).names];
  const seen = new Set<string>();
  const found = new Set<string>();
  while (pending.length > 0) {
    const name = pending.pop() as string;
    if (seen.has(name)) continue;
    seen.add(name);
    const jump = byName.get(name);
    if (jump === undefined) {
      found.add(name);
      continue;
    }
    for (const inner of foldedNames(nodeOf(jump.level), substitution,
                                    bindings, memo).names) {
      pending.push(inner);
    }
  }
  return found;
}

/** A plan's SELECTORS: the jump nodes whose LEVEL QUANTITY reads no id in
 * `determined` -- a placeholder standing in that level resolved into the
 * jump it replaced, transitively, and every name closed over the
 * document's own bindings table (`_selectors`).
 *
 * Upward closed along the nesting for `_dependence`'s own reason: a
 * placeholder stands for exactly the subtree it replaced, and the plan
 * lists its jumps in POSTORDER, so an inner node is decided before the
 * node it sits in. */
function selectorsOf(plan: ProgramPlan, determined: ReadonlySet<string>,
                     namesOf: (expression: string) => ReadonlySet<string>):
ProgramJump[] {
  const reaches = new Map<string, boolean>();
  const found: ProgramJump[] = [];
  for (const jump of plan.jumps) {
    let touches = false;
    for (const name of namesOf(jump.level)) {
      if (determined.has(name) || reaches.get(name) === true) {
        touches = true;
        break;
      }
    }
    reaches.set(jump.name, touches);
    if (!touches) found.push(jump);
  }
  return found;
}

/** Tarjan over an adjacency list, ITERATIVELY -- a deep chain must not
 * exhaust the JavaScript stack any more than it may exhaust the
 * interpreter's -- with the components and their members in the list's
 * own order (`_strongly_connected`). */
export function stronglyConnected(
  after: readonly (readonly number[])[],
): number[][] {
  const indexOf = new Map<number, number>();
  const low = new Map<number, number>();
  const onStack = new Set<number>();
  const stack: number[] = [];
  const found: number[][] = [];
  let counter = 0;
  for (let root = 0; root < after.length; root += 1) {
    if (indexOf.has(root)) continue;
    const work: [number, number][] = [[root, 0]];
    while (work.length > 0) {
      const frame = work[work.length - 1];
      const node = frame[0];
      const step = frame[1];
      if (step === 0) {
        indexOf.set(node, counter);
        low.set(node, counter);
        counter += 1;
        stack.push(node);
        onStack.add(node);
      }
      if (step < after[node].length) {
        frame[1] = step + 1;
        const child = after[node][step];
        if (!indexOf.has(child)) {
          work.push([child, 0]);
        } else if (onStack.has(child)) {
          low.set(node, Math.min(low.get(node) as number,
                                 indexOf.get(child) as number));
        }
        continue;
      }
      work.pop();
      if (work.length > 0) {
        const parent = work[work.length - 1][0];
        low.set(parent, Math.min(low.get(parent) as number,
                                 low.get(node) as number));
      }
      if (low.get(node) === indexOf.get(node)) {
        const component: number[] = [];
        for (;;) {
          const other = stack.pop() as number;
          onStack.delete(other);
          component.push(other);
          if (other === node) break;
        }
        component.sort((a, b) => a - b);
        found.push(component);
      }
    }
  }
  found.sort((a, b) => a[0] - b[0]);
  return found;
}

/** The strongly connected components of the program's DEPENDENCY GRAPH,
 * in the published order: edge A precedes edge B when B reads a
 * coordinate A determines, with a coordinate an edge itself determines
 * EXCLUDED -- that is the self-read, which is not a wait on anything
 * else (`_components`).
 *
 * A `check` determines nothing, so nothing ever waits on it and it can
 * never be in a component; it is left exactly where it is published. */
export function componentsOf(list: readonly ProgramEdge[]): number[][] {
  const determines = new Map<string, number>();
  list.forEach((edge, index) => {
    for (const key of edge.gives) determines.set(key, index);
  });
  const after = list.map((edge) => {
    const own = new Set(edge.gives);
    const found: number[] = [];
    for (const key of edge.needs) {
      if (own.has(key)) continue;
      const source = determines.get(key);
      if (source !== undefined && !found.includes(source)) found.push(source);
    }
    return found;
  });
  return stronglyConnected(after);
}

/** The refusal a cycle no selection breaks has always had, with one
 * sentence saying what a switch would be (`_cycle_message`). */
function cycleMessage(stuck: readonly ProgramEdge[]): string {
  return (
    `the relations ${stuck.map((edge) => edge.description).join(', ')} form ` +
    'a cycle the run cannot order: each waits on a coordinate another ' +
    'determines. A running program is acyclic, because the rest render ' +
    'solved every relation in one direction. A dependency inside a cycle ' +
    'is admitted only where it is SWITCHED: a source that folding a jump ' +
    "node to zero removes from the law, where that node's level reads no " +
    'coordinate the cycle determines and its zero branch is one the node ' +
    'holds over an INTERVAL of that level -- floor, ceil, a remainder or a ' +
    'comparison, and not sign, whose zero is a single point.');
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
      shapes: (gives as string[]).map(() => null),
      kinks: (gives as string[]).map(() => null),
      plans: (gives as string[]).map(() => null),
      retained: [],
      factor: 0,
      factors: [],
      constant: 0,
      slot: null,
      block: null,
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
            // Derived below, once the interned roots and the bindings
            // table exist (design D1).
            shape: null,
            kinks: null,
          };
        });
        const built: ProgramPlan = {
          skeleton: plan.skeleton, jumps, shape: null, kinks: null,
        };
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

  // The SHAPE of every followed quantity, derived HERE, once, at load
  // (openspec `solve-at-the-kink`, design D1; machinome's ADR-123).
  //
  // The producer's own classification is STRUCTURAL -- it reads the
  // expression tree and nothing else -- and this viewer holds the same
  // expressions, so it computes the same shape from the same text. No
  // document field is read for it and no version moves for it.
  //
  // Derived per PUBLISHED QUANTITY and never per tick: it cannot change
  // over a run. It never weakens the published flag either -- the solve
  // for `affine: true` is untouched, and the shape is asked only where
  // that flag is false.
  const classify = (expression: string, constants: ReadonlySet<string>):
  { shape: PathShape; kinks: readonly KinkLevel[] | null } => {
    const root = nodeOf(expression);
    const roots = table.roots();
    const shape = shapeOf(root, constants, roots);
    return {
      shape,
      kinks: shape === 'kinked' ? kinkLevels(root, roots) : null,
    };
  };
  for (const edge of edges) {
    if (edge.kind !== 'law') continue;
    edge.gives.forEach((_key, index) => {
      const plan = edge.plans[index];
      if (plan !== null) {
        // A plan's own jump names are the branch PLACEHOLDERS, constant
        // on the piece being cut.
        const names: ReadonlySet<string> =
          new Set(plan.jumps.map((jump) => jump.name));
        const skeleton = classify(plan.skeleton, names);
        plan.shape = skeleton.shape;
        plan.kinks = skeleton.kinks;
        for (const jump of plan.jumps) {
          const level = classify(jump.level, names);
          jump.shape = level.shape;
          jump.kinks = level.kinks;
        }
        edge.shapes[index] = skeleton.shape;
        edge.kinks[index] = skeleton.kinks;
        return;
      }
      const expression = edge.expressions[index] ?? null;
      if (expression === null) {
        // A constant law has zero slope everywhere, which is affine and
        // moves nothing.
        edge.shapes[index] = 'constant';
        return;
      }
      const end = classify(expression, new Set<string>());
      edge.shapes[index] = end.shape;
      edge.kinks[index] = end.kinks;
    });
  }

  // The SELF-READ, recognised and read HERE, once, at load (design D1).
  //
  // A law edge whose `needs` intersects its `gives` reads the coordinate
  // it DRIVES, and what it reads there is the value that coordinate
  // RETAINS. No key is published for it -- the intersection IS the
  // recognition, the same question `serializer.py`'s `_reads_its_own`
  // asks to publish the document at version 6 -- so nothing here tests
  // the version number: a version 6 document whose program carries no
  // such edge takes exactly the path a version 5 one takes, and a
  // version 5 document is never given a reading.
  //
  // `Edge._retained_ends` and `_dependence` reproduced.
  for (const edge of edges) {
    if (edge.kind !== 'law') continue;
    const read = edge.gives.filter((key) => edge.needs.includes(key));
    if (read.length === 0) continue;
    if (read.length > 1 || edge.gives.length > 1) {
      refuse(
        `${edge.description} names ${read.sort().join(', ')} both among the ` +
        'values it reads and among the values it determines, and it ' +
        `determines ${edge.gives.length} of them: ` +
        `${[...edge.gives].sort().join(', ')}. A law reading its own driven ` +
        'end drives exactly ONE coordinate, because each driven end is ' +
        "walked over its own path and a member reading a sibling would need " +
        "that sibling's path while the sibling's own walk is cutting it.");
    }
    const own = read[0];
    if (!bank.has(own)) {
      refuse(
        `${edge.description} reads "${own}", the end it drives, which is a ` +
        'published computed value rather than a coordinate of the bank. A ' +
        'retained value is a history and only a coordinate the run banks ' +
        'keeps one: a computed value is recomputed from the bank on every ' +
        'tick, so there is nothing for the law to read back.');
    }
    const index = edge.gives.indexOf(own);
    const plan = edge.plans[index];
    // The SKELETON is the law with every jump node replaced by its
    // branch -- and for an end carrying no plan at all, the expression
    // itself is that skeleton, which is `_compiled_law`'s own
    // `plan.skeleton if plan is not None else graph`.
    const skeleton = plan === null ? edge.expressions[index] : plan.skeleton;
    if (skeleton !== null && skeleton !== undefined
        && namesOf(skeleton).has(own)) {
      refuse(
        `${edge.description} reads "${own}", the coordinate it drives, ` +
        'CONTINUOUSLY -- with every jump node replaced by its branch the ' +
        'expression still names it, so the relation is a differential ' +
        'equation rather than an increment, and f(end) - f(start) does not ' +
        'define one. A read must pass through a node that is PIECEWISE ' +
        'CONSTANT in it: floor, ceil, sign or a comparison. A remainder ' +
        'alone is not one, because a fixed quotient leaves a - q*b, which ' +
        `still carries the coordinate's slope. Quoting the expression: ` +
        `${quoted(skeleton)}.`);
    }
    if (plan === null) continue;
    // Dependence, propagated in the plan's own (postorder) jump order,
    // because a plan lists its jumps in postorder and a placeholder is
    // always defined before it is named. The free names are taken
    // through the document's BINDINGS TABLE -- `Clearing`'s band gate
    // reaches `wheel.turn` only through `_b3 = ((wheel.turn + 0.5) /
    // 360.0)`, and a viewer reading `freeVariables` alone would sort
    // that node INDEPENDENT and integrate the whole tick under one
    // branch.
    const dependence = new Map<string, boolean>();
    for (const jump of plan.jumps) {
      const names = namesOf(jump.level);
      let depends = names.has(own);
      if (!depends) {
        for (const name of names) {
          if (dependence.get(name) === true) {
            depends = true;
            break;
          }
        }
      }
      dependence.set(jump.name, depends);
    }
    const reading: RetainedReading = {
      own,
      dependent: plan.jumps.filter((jump) => dependence.get(jump.name)),
      outer: {
        skeleton: plan.skeleton,
        jumps: plan.jumps.filter((jump) => !dependence.get(jump.name)),
        // The same skeleton TEXT as the full plan's, and classified
        // under the full plan's names (design §7's last risk).
        shape: plan.shape,
        kinks: plan.kinks,
      },
      // READ, never recomputed: what compile time decided (ADR-047).
      affine: edge.affine[index],
      // DERIVED, above, from the FULL plan's skeleton under the FULL
      // plan's jump names.
      shape: plan.shape,
      kinks: plan.kinks,
    };
    edge.retained = edge.gives.map(
      (_key, at) => (at === index ? reading : null));
  }
  // The BLOCK, re-derived HERE, once, at load (design D1).
  //
  // A version 7 document carries NO NEW KEY: `Program.published` emits a
  // block's members as ordinary law edges in the producer's own
  // deterministic order, and that order is a LISTING and not an
  // execution order. Membership and selectorhood are FUNCTIONS of the
  // published edges, so a consumer derives them -- ADR-110's line, the
  // same one that makes `determiner` derived and `sources` published.
  //
  // Nothing here tests the version number: a version 7 document whose
  // edges hold no nontrivial component produces no block and takes
  // exactly the path a version 5 or 6 one takes.

  /** What cannot be a block member, refused by relation identity
   * (`_refuse_unselectable`). */
  const refuseUnselectable = (members: readonly ProgramEdge[]): void => {
    const listed = members.map((other) => other.description).join(', ');
    for (const edge of members) {
      if (edge.kind === 'wiring' || edge.kind === 'formula') {
        refuse(
          `${edge.description}, stated by ${edge.statedBy}: it is on a ` +
          `dependency cycle -- ${listed} -- and it carries no jump node, ` +
          'so no selection can switch what it reads. A cycle is admitted ' +
          'only where every dependency inside it is gated by a jump node ' +
          'whose level reads no coordinate the cycle determines. State the ' +
          'value as a relation whose law carries the gate.');
      }
    }
    for (const edge of members) {
      if (edge.gives.length !== 1) {
        refuse(
          `${edge.description}, stated by ${edge.statedBy}: it drives a ` +
          `GROUP and it is on a dependency cycle -- ${listed}. A member of ` +
          'a block drives ONE coordinate, because what a selection ' +
          "switches is decided per driven end off that end's own " +
          "expression, while a group's ends are claimed and bound " +
          'together. State each end as a relation of its own.');
      }
    }
    for (const edge of members) {
      if (!bank.has(edge.gives[0])) {
        refuse(
          `${edge.description}, stated by ${edge.statedBy}: it drives ` +
          `${edge.gives[0]}, which the running simulation does not own, ` +
          `and it is on a dependency cycle -- ${listed}. A block advances ` +
          'its coordinates PIECE BY PIECE inside a tick, and only a ' +
          'coordinate the run owns keeps that history -- a plain port and ' +
          'a derived coordinate are calculations the ordinary enumeration ' +
          'recomputes from the bank on every tick. State the relation into ' +
          'the joint coordinate and let the port follow it.');
      }
    }
  };

  /** One component read as a block: its selectors, its fold, and what a
   * selection can switch (`_Block.__init__`). */
  const blockOf = (members: readonly ProgramEdge[]): ProgramBlock => {
    const gives = members.map((member) => member.gives[0]);
    const determined: ReadonlySet<string> = new Set(gives);
    const built: BlockMember[] = members.map((member) => {
      const own = member.gives[0];
      const plan = member.plans.length > 0 ? member.plans[0] : null;
      if (plan === null) {
        // A law with no jump in it carries no selector at all, so
        // everything it reads in the block is unconditional.
        return {
          edge: member,
          own,
          plan: null,
          selectors: [],
          selectorPlan: null,
          unconditional: new Set(member.needs.filter(
            (key) => determined.has(key) && key !== own)),
          switched: new Set<string>(),
        };
      }
      const selectors = selectorsOf(plan, determined, namesOf);
      // ONE all-zero fold answers both questions the load asks, because
      // the fold is MONOTONE in the set of names sent to zero and the
      // all-zero assignment is therefore the minimum over every
      // assignment. A search over 2^n selector assignments would invite
      // 2^n folds per member and leave the load's cost undefined.
      const zero: Record<string, number> = {};
      for (const jump of selectors) {
        if (FOLDABLE.includes(jump.primitive)) zero[jump.name] = 0;
      }
      const inBlock = (keys: ReadonlySet<string>): Set<string> => new Set(
        [...keys].filter((key) => determined.has(key) && key !== own));
      // A read of the member's OWN driven end is ADR-121's self-read,
      // not a wait on anything else, and is excluded from both sets
      // exactly as the dependency graph excludes it.
      const whole = inBlock(readsUnder(plan, {}, nodeOf, table.roots()));
      const least = inBlock(readsUnder(plan, zero, nodeOf, table.roots()));
      return {
        edge: member,
        own,
        plan,
        selectors,
        selectorPlan: {
          skeleton: plan.skeleton,
          jumps: selectors,
          // The SAME skeleton text under the same plan's names.
          shape: plan.shape,
          kinks: plan.kinks,
        },
        unconditional: least,
        switched: new Set([...whole].filter((key) => !least.has(key))),
      };
    });
    return {
      members: built,
      gives,
      activeReads: (index, forced) => {
        const member = built[index];
        if (member.plan === null) return member.unconditional;
        const reads = readsUnder(member.plan, forced, nodeOf, table.roots());
        return new Set([...reads].filter((key) => determined.has(key)));
      },
    };
  };

  /** The members whose UNCONDITIONAL dependencies still form a cycle, or
   * `[]` (`_Block.unconditional_cycle`). Present on every piece, so it
   * is refused at LOAD with the message a plain cycle of two ordinary
   * laws has always had. */
  const unconditionalCycle = (block: ProgramBlock): ProgramEdge[] => {
    let remaining = block.members.map((_member, index) => index);
    const resolved = new Set<string>();
    while (remaining.length > 0) {
      const ready = remaining.filter((index) => [
        ...block.members[index].unconditional,
      ].every((key) => key === block.gives[index] || resolved.has(key)));
      if (ready.length === 0) {
        return remaining.map((index) => block.members[index].edge);
      }
      for (const index of ready) resolved.add(block.gives[index]);
      remaining = remaining.filter((index) => !ready.includes(index));
    }
    return [];
  };

  /** One block as the single edge the program carries (`_block_edge`). */
  const blockEdge = (block: ProgramBlock): ProgramEdge => {
    const needs: string[] = [];
    const statedBy: string[] = [];
    for (const member of block.members) {
      for (const key of member.edge.needs) {
        if (!needs.includes(key)) needs.push(key);
      }
      if (!statedBy.includes(member.edge.statedBy)) {
        statedBy.push(member.edge.statedBy);
      }
    }
    return {
      kind: 'block',
      needs,
      gives: [...block.gives],
      description: block.members.map(
        (member) => member.edge.description).join('; '),
      statedBy: statedBy.join(', '),
      expressions: [],
      // A block's value is piecewise in the SELECTOR partition AND
      // re-ordered across it, so a stop on one of its coordinates is
      // SEARCHED, never solved (design D4.2). `solve-at-the-kink` does
      // NOT lift that: a block has no single expression at all until a
      // branch vector is fixed, so it carries no shape either.
      affine: block.gives.map(() => false),
      shapes: block.gives.map(() => null),
      kinks: block.gives.map(() => null),
      plans: block.gives.map(() => null),
      retained: [],
      factor: 0,
      factors: [],
      constant: 0,
      slot: null,
      block,
    };
  };

  // `_blocked`: every nontrivial component contracted to ONE compound
  // entry at the index of its FIRST member, every other edge keeping its
  // published position and its relative order.
  let executed: ProgramEdge[] = edges;
  const components = componentsOf(edges);
  const made = new Map<number, ProgramEdge>();
  const taken = new Set<number>();
  for (const component of components) {
    if (component.length < 2) continue;
    const members = component.map((index) => edges[index]);
    refuseUnselectable(members);
    const block = blockOf(members);
    const stuck = unconditionalCycle(block);
    if (stuck.length > 0) refuse(cycleMessage(stuck));
    made.set(component[0], blockEdge(block));
    for (const index of component) taken.add(index);
  }
  if (made.size > 0) {
    executed = [];
    edges.forEach((edge, index) => {
      const found = made.get(index);
      if (found !== undefined) executed.push(found);
      else if (!taken.has(index)) executed.push(edge);
    });
  }

  // The contracted sequence VERIFIED to be a topological order of the
  // contracted graph, and never re-sorted (design D1.2). Kahn-ordering
  // it here -- which is what the producer does at construction -- would
  // silently accept a document whose published listing disagrees with
  // its own content, which is precisely the failure version 7 exists to
  // make loud. This viewer reads the order compile time decided
  // (ADR-047) and checks it.
  const determinedBy = new Map<string, number>();
  executed.forEach((edge, index) => {
    for (const key of edge.gives) determinedBy.set(key, index);
  });
  executed.forEach((edge, index) => {
    const own = new Set(edge.gives);
    for (const key of edge.needs) {
      if (own.has(key)) continue;
      const source = determinedBy.get(key);
      if (source !== undefined && source > index) {
        refuse(
          'its published edges are not in an order this engine can ' +
          `execute: ${edge.description} reads "${key}", which ` +
          `${executed[source].description} determines LATER in the ` +
          "published listing. The published order of a program's edges is " +
          "the order it runs in, with a block's members contracted to one " +
          'entry; a consumer that re-sorted them would be inventing an ' +
          'ordering decision the producer already made.');
      }
    }
  });

  // The inversion of `gives`, over the edges the engine EXECUTES: a
  // block give is determined by the block, at that give's position in
  // the block's own `gives` -- which is what `Run.locate` reads
  // `affine[index]` and `edgeCuts(..., index)` by (design D4.5).
  determiner.clear();
  executed.forEach((edge) => {
    edge.gives.forEach((id, index) => determiner.set(id, { edge, index }));
  });

  // 11 (continued). What a bound may read: the bounded coordinate's own
  // id together with every coordinate of the bank (design D3). An
  // intermediate, the clock, a branch placeholder or an unknown name is
  // still refused, by name, here.
  //
  // The SUB-PROGRAM of a constraint: the published edges determining
  // `keys` and everything they need, in the program's own order --
  // `Program._sub_program` reproduced, walked in reverse and reversed
  // again, a check never among them.
  const subProgram = (keys: readonly string[]): ProgramEdge[] => {
    const needed = new Set(keys);
    const chosen: ProgramEdge[] = [];
    for (let at = executed.length - 1; at >= 0; at -= 1) {
      const edge = executed[at];
      if (edge.kind === 'check') continue;
      if (edge.gives.some((key) => needed.has(key))) {
        chosen.push(edge);
        for (const key of edge.needs) needed.add(key);
      }
    }
    chosen.reverse();
    return chosen;
  };

  const intermediateSet = new Set(intermediates);
  const constraints = new Map<string, Constraint>();
  for (const [id, span] of Object.entries(spans)) {
    for (const side of ['low', 'high'] as const) {
      const bound = span[side];
      if (bound === null || typeof bound !== 'object') continue;
      const names = namesOf(bound.expression);
      for (const name of names) {
        if (name === id || bank.has(name)) continue;
        const why = intermediateSet.has(name)
          ? ': that name is a published computed value, not a coordinate '
            + 'of the bank, and a bound reads the STATE -- read the joint '
            + 'the port follows.'
          : '.';
        refuse(
          `the bound declared on "${id}" names "${name}", which it may ` +
          `not read${why} It may read: ${id} and any of the program's ` +
          `${order.length} coordinates. Quoting the expression: ` +
          `${quoted(bound.expression)}.`);
      }
      // D2: the reads are the CLOSURE minus the own id, sorted. A bound
      // naming no coordinate but its own is not a constraint: its
      // meaning, its path and its cost stay exactly what they are.
      const reads = [...names].filter((name) => name !== id).sort();
      if (reads.length === 0) continue;
      const keys = [id, ...reads];
      const candidates = [...new Set(
        keys.flatMap((key) => sources[key] ?? []))].sort();
      constraints.set(`${id}:${side}`, {
        identifier: id,
        side,
        expression: bound.expression,
        reads,
        edges: subProgram(keys),
        candidates,
      });
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
    edges: executed,
    spans,
    sources,
    limits,
    determiner,
    constraints,
    placeholders,
    drivers: document.drivers ?? {},
    instructions: document.instructions ?? {},
    bindings: table,
    declaredNames,
    nodeOf,
  };
}
