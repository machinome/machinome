/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// How a law that jumps is integrated over one tick
// (`simulation/program.py`'s `JumpPlan`, `_branch_of`, `_surfaces`,
// `_deduplicated`, `_merged`, `_along`, `_too_many`, `_no_level`,
// reproduced function for function).
//
// The tick moves the law's sources along the straight line from the
// values they hold to those values plus the increments they were given,
// parametrised by `t` in [0, 1]. That path is cut at every crossing of
// every jump surface it meets. On each open piece every jump node holds
// one BRANCH, read by evaluating its level quantity at the piece's
// MIDPOINT -- a point genuinely inside it, so the value read there IS
// the branch, at any magnitude and from either direction of travel. The
// law with those branches substituted is continuous on the closed piece,
// so the increment is the plain sum of its change over the pieces: no
// epsilon, no one-sided limit rule, no direction test anywhere.

import {
  evaluateExpression, JumpPrimitive, LandingInvariantError, ProgramJump,
  ProgramLimits, ProgramPlan, TooManyCrossings, UnsupportedLaw,
} from './program';
import type {
  BlockMember, LoadedProgram, PathHost, ProgramBlock, RetainedReading,
} from './program';
import { ExpressionPath, movingNames, UnsupportedPathNode, withExpressions } from '../expressions';
import type { KinkLevel } from '../expressions';
import { kinkLevel } from './program';
import { constantContact, hasMovingSource } from './contact-proof';
import { alongSources, copyHolding, curved } from './motion';

/** A SELECTOR's placeholder bound to the branch the block read at its
 * piece's midpoint (design D3). A forced node is a CONSTANT on the
 * piece: its crossings were located over the whole stretch and are not
 * located again, and every reading of its branch is the number the block
 * substituted. */
export type Forced = Record<string, number> | null;

function isForced(forced: Forced, name: string): boolean {
  return forced !== null
    && Object.prototype.hasOwnProperty.call(forced, name);
}

/** One jump surface met inside one tick. `level` is the surface value in
 * the LEVEL QUANTITY's own units and `t` is the fraction of the tick at
 * which it was reached. */
export interface CrossingRecord {
  tick: number;
  relation: string;
  coordinate: string;
  primitive: string;
  level: number;
  t: number;
}

/** A whole number, never a NEGATIVE zero: the producer's `math.floor`,
 * `math.ceil` and `math.trunc` return Python ints, which have no signed
 * zero, and `float(0)` is +0.0. */
function whole(value: number): number {
  return value === 0 ? 0 : value;
}

const COMPARISONS: Record<string, (level: number) => boolean> = {
  '<': (level) => level < 0,
  '<=': (level) => level <= 0,
  '>': (level) => level > 0,
  '>=': (level) => level >= 0,
  '==': (level) => level === 0,
  '!=': (level) => level !== 0,
};

/** What a jump reads on a piece whose level quantity sits at `level`. */
export function branchOf(primitive: JumpPrimitive, level: number): number {
  if (primitive === 'floor') return whole(Math.floor(level));
  if (primitive === 'ceil') return whole(Math.ceil(level));
  // The producer's `(x > 0) - (x < 0)`, which is 0 at negative zero
  // where a runtime's own sign function answers -0.
  if (primitive === 'sign') {
    return (level > 0 ? 1 : 0) - (level < 0 ? 1 : 0);
  }
  // Not a constant but the integer QUOTIENT: with `q` fixed the node
  // reads `a - q * b`, which is continuous in `t`.
  if (primitive === '%') return whole(Math.trunc(level));
  return COMPARISONS[primitive](level) ? 1 : 0;
}

// ---------------------------------------------------------------------
// The float primitives the far-side landing is defined in terms of
// (design D3). `math.ulp`, `math.nextafter` and `math.copysign` have no
// JavaScript equivalents, so `_ordinal`/`_from_ordinal` are reproduced
// over a `Float64Array`/`BigInt64Array` view of the same eight bytes and
// the other three are built on them. `BigInt` rather than `number`
// because the ordinal range is the whole of int64 and `2**63` is not
// exactly representable as a double.
// ---------------------------------------------------------------------

const BYTES = new ArrayBuffer(8);
const AS_FLOAT = new Float64Array(BYTES);
const AS_BITS = new BigInt64Array(BYTES);
const TWO_63 = 2n ** 63n;

/** A float as the integer its bits order by, so two floats can be
 * bisected in FLOAT space: adjacent floats differ by one here, at any
 * magnitude, with no tolerance anywhere, and `-0` maps to the same
 * ordinal `0` as `+0`. */
export function ordinalOf(value: number): bigint {
  AS_FLOAT[0] = value;
  const bits = AS_BITS[0];
  return bits >= 0n ? bits : -TWO_63 - bits;
}

export function fromOrdinal(whole: bigint): number {
  AS_BITS[0] = whole < 0n ? -TWO_63 - whole : whole;
  return AS_FLOAT[0];
}

/** The distance from `value` to the next representable float away from
 * zero -- `math.ulp`. */
export function ulpOf(value: number): number {
  const magnitude = Math.abs(value);
  return fromOrdinal(ordinalOf(magnitude) + 1n) - magnitude;
}

/** The next representable float after `x` in the direction of `y` --
 * `math.nextafter`. */
export function nextAfter(x: number, y: number): number {
  if (x === y) return y;
  return fromOrdinal(ordinalOf(x) + (y > x ? 1n : -1n));
}

/** `math.copysign(1.0, value)`: -1 for a negative, NEGATIVE ZERO
 * included. */
export function copySign(value: number): number {
  return (value < 0 || Object.is(value, -0)) ? -1 : 1;
}

export function tooMany(described: string, coordinate: string,
                        primitive: string, count: number,
                        limits: ProgramLimits): TooManyCrossings {
  return new TooManyCrossings(
    `${described}: over one tick ${coordinate} would cross ${count} ` +
    `surfaces of ${primitive}, more than the ${limits.maxCrossings} a ` +
    'single law is admitted in one tick. A dt that coarse is not resolving ' +
    'the mechanism: the crossings between the frames are what a jump law ' +
    'is FOR. Step in smaller ticks. The tick committed nothing: the bank, ' +
    'the tick count and the tree stand as they were.');
}

export function chattering(described: string, coordinate: string,
                           primitive: string): UnsupportedLaw {
  return new UnsupportedLaw(
    `${described}: ${coordinate} stands exactly on a surface of its ` +
    `${primitive} and each branch carries the level back across it -- a ` +
    'sliding mode, not a mechanism. The framework integrates a law piece ' +
    'by piece, and there is no piece here to integrate. The tick committed ' +
    'nothing: the bank, the tick count and the tree stand as they were.');
}

export function unlanded(described: string, coordinate: string,
                         primitive: string,
                         strides: number): LandingInvariantError {
  return new LandingInvariantError(
    `${described}: ${coordinate} was cut at a surface of ${primitive} and ` +
    `no value within ${strides} doublings of a ulp of the segment's own ` +
    'arithmetic reads the other branch, so the cut placed the coordinate ' +
    'nowhere. The level crossed that surface, so this is a broken ' +
    'invariant of the run rather than a dt that is too coarse. The tick ' +
    'committed nothing: the bank, the tick count and the tree stand as ' +
    'they were.');
}

export function noLevel(primitive: string, described: string,
                        coordinate: string, reason?: string): UnsupportedLaw {
  const what = reason ?? (primitive === '%'
    ? 'a divisor of zero' : 'a division by zero in its level quantity');
  return new UnsupportedLaw(
    `${described}: its ${primitive} meets ${what} somewhere on this tick's ` +
    'path, so there is no level quantity to locate a crossing on. The tick ' +
    `committed nothing and ${coordinate} stands where it stood: state the ` +
    'relation so the divisor never reaches zero.');
}

/** The sources at `t` along the tick's straight path. At `t === 1` this
 * is exactly `start + delta`, the same float the caller computed,
 * because it is the same arithmetic. */
export function along(start: Record<string, number>,
                      delta: Record<string, number>,
                      t: number): Record<string, number> {
  return alongSources(start, delta, t);
}

/** A jump's surfaces between two values of its level quantity. */
export function surfacesOf(
  jump: ProgramJump, low: number, high: number, inclusive: boolean,
  limits: ProgramLimits, refuse: (count: number | null) => never,
): number[] {
  if (jump.primitive === 'sign' || jump.primitive in COMPARISONS) {
    const first = low <= high ? low : high;
    const last = low <= high ? high : low;
    if ((first < 0 && 0 < last) || (inclusive && first <= 0 && 0 <= last)) {
      return [0];
    }
    return [];
  }
  const first = low <= high ? low : high;
  const last = low <= high ? high : low;
  if (!Number.isFinite(first) || !Number.isFinite(last)) {
    refuse(null);
  }
  const span = Math.ceil(last) - Math.floor(first) - 1;
  if (span > limits.maxCrossings) {
    refuse(span);
  }
  const levels: number[] = [];
  if (inclusive) {
    for (let whole = Math.floor(first); whole <= Math.ceil(last); whole += 1) {
      if (first <= whole && whole <= last) levels.push(whole);
    }
  } else {
    for (let whole = Math.floor(first) + 1; whole < Math.ceil(last);
         whole += 1) {
      if (first < whole && whole < last) levels.push(whole);
    }
  }
  if (jump.primitive === '%') {
    // `fmod` is `a - b * trunc(a / b)`, and `trunc` is zero on the whole
    // of (-1, 1): the operator is CONTINUOUS where `a / b` crosses zero
    // and jumps only at a nonzero integer of it.
    return levels.filter((level) => level !== 0);
  }
  return levels;
}

/** One entry per surface actually reached: a crossing that falls on a
 * sub-interval boundary is located twice, from either side. */
export function deduplicated(found: [number, number][],
                             tolerance: number): [number, number][] {
  const ordered = [...found].sort(
    (a, b) => (a[0] - b[0]) || (a[1] - b[1]));
  const kept: [number, number][] = [];
  for (const entry of ordered) {
    const last = kept[kept.length - 1];
    if (last !== undefined && last[1] === entry[1]
        && entry[0] - last[0] <= tolerance) {
      continue;
    }
    kept.push(entry);
  }
  return kept;
}

/** The partition with `found` folded in: two cuts closer than the
 * tolerance are ONE, and the partition always ends at exactly `end` --
 * 1 for a tick's own partition, and the stretch's own right end for the
 * kink breakpoints located INSIDE one piece of it (openspec
 * `solve-at-the-kink`, design D2). */
export function merged(cuts: number[], found: number[],
                       tolerance: number, end = 1): number[] {
  const ordered = [...cuts, ...found].sort((a, b) => a - b);
  const kept = [ordered[0]];
  for (const where of ordered.slice(1)) {
    if (where - kept[kept.length - 1] > tolerance) kept.push(where);
  }
  kept[kept.length - 1] = end;
  return kept;
}

// ---------------------------------------------------------------------
// WHERE A KINKED QUANTITY'S KINKS CUT A STRETCH (openspec
// `solve-at-the-kink`, design D2; `_KinkCuts.between`).
//
// A kinked quantity is affine on each stretch between its own
// breakpoints, so the stretch is cut there and each sub-piece SOLVED.
// The kinks come in the expression's own POSTORDER, so a kink nested
// inside another's level is cut FIRST, and on each sub-interval the
// earlier kinks have already produced the level that follows is affine
// in the fraction -- so its zero is ONE DIVISION. No sampling, no
// bisection, and no tolerance but the crossing tolerance two crossings
// are already folded under.
//
// A breakpoint is NOT a crossing (design D3): the quantity is
// continuous there, so it is recorded nowhere, enters no partition an
// increment is summed over, lands no coordinate on a far side and
// counts toward no maximum. It exists only inside a SOLVE.
// ---------------------------------------------------------------------

/** The breakpoints STRICTLY INSIDE `[left, right]`, sorted and merged,
 * where `level(kink, t)` gives that kink's level quantity at `t`. */
export function kinkBreaks(kinks: readonly KinkLevel[],
                           level: (kink: KinkLevel, t: number) => number,
                           left: number, right: number,
                           tolerance: number): number[] {
  let cuts = [left, right];
  for (const one of kinks) {
    const found: number[] = [];
    for (let at = 0; at < cuts.length - 1; at += 1) {
      const lowT = cuts[at];
      const highT = cuts[at + 1];
      const low = level(one, lowT);
      const high = level(one, highT);
      if (high === low || !Number.isFinite(low) || !Number.isFinite(high)) {
        // A level that does not MOVE over a sub-interval reaches nothing
        // inside it -- the same statement `Walk.searched` makes of a
        // jump level.
        continue;
      }
      if (!(Math.min(low, high) < 0 && 0 < Math.max(low, high))) continue;
      const where = lowT + (highT - lowT) * (0 - low) / (high - low);
      if (lowT < where && where < highT) found.push(where);
    }
    if (found.length > 0) cuts = merged(cuts, found, tolerance, right);
  }
  return cuts.slice(1, -1);
}

/** One caller's own LEVEL path values (design D7, ADR-060; ADR-124's
 * `_LevelPaths`): one `PathValue` per jump PLACEHOLDER, re-bound when the
 * PIECE token it is asked under changes and taken at a point otherwise
 * (D6). A piece is identified by a strictly increasing integer handed out
 * by `newPiece()` -- never by a transient object -- so no value computed
 * under one piece can be read back under another's, even though
 * JavaScript's `Map` keying by object identity would already prevent the
 * hazard ADR-124 records (D6).
 *
 * A jump whose level the path evaluator REFUSES (D9) falls back to the
 * ordinary whole-graph `levelOf` for every future point of that SAME
 * jump: the refusal is a structural property of the expression, decided
 * once. */
export class LevelPaths {
  private readonly paths = new Map<string, ExpressionPath>();

  private readonly bound = new Map<string, number>();

  private readonly disabled = new Set<string>();

  private counter = 0;

  constructor(private readonly program: PathHost,
              private readonly moving: ReadonlySet<string>) {}

  /** A fresh, strictly increasing piece token (D6). */
  newPiece(): number { this.counter += 1; return this.counter; }

  value(plan: ProgramPlan, jump: ProgramJump, piece: number,
        values: Record<string, number>, described: string,
        coordinate: string): number {
    if (this.disabled.has(jump.name)) {
      return levelOf(this.program, plan, jump, values, described, coordinate);
    }
    let path = this.paths.get(jump.name);
    if (path === undefined) {
      path = new ExpressionPath(jump.level, this.moving, this.program.bindings.roots);
      this.paths.set(jump.name, path);
    }
    const bind = this.bound.get(jump.name) !== piece;
    if (bind) this.bound.set(jump.name, piece);
    let level: number;
    try {
      level = Number(bind ? path.bind(values) : path.at(values));
    } catch (error) {
      if (!(error instanceof UnsupportedPathNode)) throw error;
      this.disabled.add(jump.name);
      return levelOf(this.program, plan, jump, values, described, coordinate);
    }
    if (!Number.isFinite(level)) {
      throw noLevel(jump.primitive, described, coordinate,
                    Number.isNaN(level)
                      ? 'a level quantity that is not a number'
                      : undefined);
    }
    return level;
  }
}

function levelAt(program: PathHost, plan: ProgramPlan, jump: ProgramJump,
                 start: Record<string, number>, delta: Record<string, number>,
                 t: number, inner: Record<string, number>,
                 described: string, coordinate: string,
                 paths: LevelPaths | null = null, piece = 0): number {
  const values = along(start, delta, t);
  for (const name in inner) {
    if (Object.prototype.hasOwnProperty.call(inner, name)) {
      values[name] = inner[name];
    }
  }
  if (paths !== null) {
    return paths.value(plan, jump, piece, values, described, coordinate);
  }
  return levelOf(program, plan, jump, values, described, coordinate);
}

function levelOf(program: PathHost, plan: ProgramPlan, jump: ProgramJump,
                 values: Record<string, number>, described: string,
                 coordinate: string): number {
  void plan;
  const level = evaluateExpression(program, jump.level, values);
  if (!Number.isFinite(level)) {
    // Python raises `ZeroDivisionError` where this runtime answers
    // Infinity or NaN, and refuses a non-finite level for the integer
    // primitives outright. Either way there is no level quantity to
    // locate a crossing on.
    throw noLevel(jump.primitive, described, coordinate,
                  Number.isNaN(level)
                    ? 'a level quantity that is not a number'
                    : undefined);
  }
  return level;
}

/** Every jump node's branch at one point of the path, in POSTORDER, so a
 * node nested inside another's argument is determined first.
 *
 * Exported for the CLOCKED clip, which reads each piece's branches at
 * its midpoint exactly as this does (`JumpPlan._branches`; OpenSpec
 * `execute-the-commit`, design §8). */
export function branchesAt(program: PathHost, plan: ProgramPlan,
                    start: Record<string, number>,
                    delta: Record<string, number>, t: number, count: number,
                    described: string, coordinate: string,
                    forced: Forced = null,
                    paths: LevelPaths | null = null): Record<string, number> {
  const values = along(start, delta, t);
  const found: Record<string, number> = {};
  // `branchesAt` is a ONE-SHOT point (design D7): every jump here is
  // asked its branch exactly once for this `t`, so a `paths` a caller
  // supplies still shares a jump's decided STRUCTURE with any other use
  // of it in the same scope, but always BINDS -- a fresh piece token.
  const piece = paths === null ? 0 : paths.newPiece();
  for (const jump of plan.jumps.slice(0, count)) {
    // A node the caller FORCED reads the branch it was given and its
    // level is never evaluated: one of the two places a block's selector
    // is read (design D3).
    const branch = isForced(forced, jump.name)
      ? (forced as Record<string, number>)[jump.name]
      : branchOf(jump.primitive,
                 paths === null
                   ? levelOf(program, plan, jump, values, described,
                             coordinate)
                   : paths.value(plan, jump, piece, values, described,
                                coordinate));
    found[jump.name] = branch;
    values[jump.name] = branch;
  }
  return found;
}

function substituted(program: PathHost, plan: ProgramPlan,
                     start: Record<string, number>,
                     delta: Record<string, number>, t: number,
                     branches: Record<string, number>): number {
  const values = along(start, delta, t);
  for (const name in branches) {
    if (Object.prototype.hasOwnProperty.call(branches, name)) {
      values[name] = branches[name];
    }
  }
  return evaluateExpression(program, plan.skeleton, values);
}

function crossingsOf(
  program: PathHost, plan: ProgramPlan, jump: ProgramJump,
  start: Record<string, number>, delta: Record<string, number>,
  inner: Record<string, number>, left: number, right: number,
  described: string, coordinate: string,
  paths: LevelPaths | null = null, piece = 0, closed = false,
): [number, number][] {
  const limits = program.limits;
  const refuse = (count: number | null): never => {
    if (count === null) throw noLevel(jump.primitive, described, coordinate);
    throw tooMany(described, coordinate, jump.primitive, count, limits);
  };
  // An affine level quantity is determined everywhere on the stretch by
  // its two endpoint values, so every surface between them is SOLVED
  // -- all of them, which is what makes a crank that passes three
  // tooth windows in one tick add three throws rather than one.
  //
  // `closed` takes the stretch's RIGHT end inclusively, for a sub-piece
  // another sub-piece continues from (openspec `solve-at-the-kink`,
  // design D4 (a)). The LEFT end is exclusive either way: at the piece's
  // own left end that surface is not one the piece crosses, and at an
  // interior breakpoint it was reached by the sub-piece before.
  const solved = (lowT: number, highT: number,
                  closed: boolean): [number, number][] => {
    const low = levelAt(program, plan, jump, start, delta, lowT, inner,
                        described, coordinate, paths, piece);
    const high = levelAt(program, plan, jump, start, delta, highT, inner,
                         described, coordinate, paths, piece);
    if (high === low) return [];
    const found: [number, number][] = [];
    for (const level of surfacesOf(jump, low, high, closed, limits, refuse)) {
      if (closed && level === low) continue;
      found.push([lowT + (highT - lowT) * (level - low) / (high - low), level]);
    }
    return found;
  };
  if (jump.affine && !curved(delta)) return solved(left, right, closed);
  if (jump.shape === 'kinked' && !curved(delta)) {
    // A KINKED level is affine on each sub-interval between its own
    // kinks, so the piece is cut there -- recording nothing, counting
    // toward nothing -- and each sub-piece is solved.
    const at = (t: number): Record<string, number> => {
      const values = along(start, delta, t);
      for (const name in inner) {
        if (Object.prototype.hasOwnProperty.call(inner, name)) {
          values[name] = inner[name];
        }
      }
      return values;
    };
    const breaks = kinkBreaks(jump.kinks!, (kink, t) => kinkLevel(
      program, kink, at(t)), left, right, limits.crossingTolerance);
    if (breaks.length === 0) {
      // No kink is reached inside this piece, so the level IS affine
      // over the whole of it.
      return solved(left, right, closed);
    }
    const edges = [left, ...breaks, right];
    let found: [number, number][] = [];
    for (let at2 = 0; at2 < edges.length - 1; at2 += 1) {
      // The right end is INCLUSIVE for every sub-piece but the last, so
      // a surface lying exactly on an interior breakpoint is not lost
      // between the two sub-pieces that meet there; `deduplicated` is
      // what stops it being taken twice, and it exists for exactly this.
      found = found.concat(
        solved(edges[at2], edges[at2 + 1], closed || at2 < edges.length - 2));
    }
    return deduplicated(found, limits.crossingTolerance);
  }
  // Anything else: sampled, bracketed and bisected.
  const width = (right - left) / limits.subdivisions;
  const points: number[] = [];
  for (let step = 0; step < limits.subdivisions; step += 1) {
    points.push(left + width * step);
  }
  points.push(right);
  const levels = points.map((where) => levelAt(
    program, plan, jump, start, delta, where, inner, described, coordinate,
    paths, piece));
  const found: [number, number][] = [];
  for (let step = 0; step < limits.subdivisions; step += 1) {
    const low = levels[step];
    const high = levels[step + 1];
    for (const level of surfacesOf(jump, low, high, true, limits, refuse)) {
      if (low === level) {
        // A sample that IS on the surface is the crossing; taking it
        // exactly is what keeps the answer exact when a crossing falls
        // on a sub-interval boundary.
        found.push([points[step], level]);
      } else if (high === level) {
        found.push([points[step + 1], level]);
      } else {
        found.push([bisect(program, plan, jump, start, delta, inner, level,
                           points[step], points[step + 1], described,
                           coordinate, paths, piece), level]);
      }
    }
    if (found.length > limits.maxCrossings) break;
  }
  return found;
}

function bisect(program: PathHost, plan: ProgramPlan, jump: ProgramJump,
                start: Record<string, number>, delta: Record<string, number>,
                inner: Record<string, number>, level: number, low: number,
                high: number, described: string, coordinate: string,
                paths: LevelPaths | null = null, piece = 0): number {
  let below = levelAt(program, plan, jump, start, delta, low, inner,
                      described, coordinate, paths, piece) - level;
  let lower = low;
  let upper = high;
  for (let round = 0; round < program.limits.bisectionRounds; round += 1) {
    if (upper - lower <= program.limits.crossingTolerance) break;
    const middle = (lower + upper) / 2;
    const here = levelAt(program, plan, jump, start, delta, middle, inner,
                         described, coordinate, paths, piece) - level;
    if (here === 0 || (here < 0) !== (below < 0)) {
      upper = middle;
    } else {
      lower = middle;
      below = here;
    }
  }
  return (lower + upper) / 2;
}

export function partition(program: PathHost, plan: ProgramPlan,
                   start: Record<string, number>,
                   delta: Record<string, number>, described: string,
                   coordinate: string, crossings: CrossingRecord[] | null,
                   tick: number, forced: Forced = null,
                   given: LevelPaths | null = null, closed = false): number[] {
  const limits = program.limits;
  const paths = given ?? new LevelPaths(program, movingNames(delta));
  let cuts = [0, 1];
  const located: [number, number, string, number][] = [];
  plan.jumps.forEach((jump, index) => {
    // The block located this node's crossings over the WHOLE stretch
    // already, and its branch is a constant on this piece: re-locating
    // it here is the second reading this design exists to remove.
    if (isForced(forced, jump.name)) return;
    let found: [number, number][] = [];
    for (let at = 0; at < cuts.length - 1; at += 1) {
      const left = cuts[at];
      const right = cuts[at + 1];
      const inner = branchesAt(program, plan, start, delta,
                               (left + right) / 2, index, described,
                               coordinate, forced, paths);
      const piece = paths.newPiece();
      found = found.concat(crossingsOf(program, plan, jump, start, delta,
                                       inner, left, right, described,
                                       coordinate, paths, piece, closed && right === 1));
      if (found.length > limits.maxCrossings) {
        throw tooMany(described, coordinate, jump.primitive, found.length,
                      limits);
      }
    }
    if (found.length === 0) return;
    found = deduplicated(found, limits.crossingTolerance);
    cuts = merged(cuts, found.map(([where]) => where),
                  limits.crossingTolerance);
    if (cuts.length - 2 > limits.maxCrossings) {
      throw tooMany(described, coordinate, jump.primitive, cuts.length - 2,
                    limits);
    }
    for (const [where, level] of found) {
      located.push([where, index, jump.primitive, level]);
    }
  });
  if (crossings !== null && located.length > 0) {
    // Sorted by the fraction of the tick, and by the graph's postorder
    // where two coincide, so the listing is deterministic.
    located.sort((a, b) => (a[0] - b[0]) || (a[1] - b[1]));
    for (const [where, , primitive, level] of located) {
      crossings.push({
        tick, relation: described, coordinate, primitive, level, t: where,
      });
    }
  }
  return cuts;
}

/** The CONTINUOUS part of this law's change over one tick. */
export function planIncrement(
  program: LoadedProgram, plan: ProgramPlan, start: Record<string, number>,
  delta: Record<string, number>, described: string, coordinate: string,
  crossings: CrossingRecord[] | null, tick: number, forced: Forced = null,
): number {
  if (!Object.values(delta).some((value) => value !== 0)) {
    // A zero-length path contributes zero without evaluating anything --
    // and must never reach the sum below, where a one-point piece would
    // read as minus a jump.
    return 0;
  }
  const paths = new LevelPaths(program, movingNames(delta));
  const cuts = partition(program, plan, start, delta, described, coordinate,
                         crossings, tick, forced, paths);
  let total = 0;
  for (let at = 0; at < cuts.length - 1; at += 1) {
    const left = cuts[at];
    const right = cuts[at + 1];
    const branches = branchesAt(program, plan, start, delta,
                                (left + right) / 2, plan.jumps.length,
                                described, coordinate, forced, paths);
    total += substituted(program, plan, start, delta, right, branches)
      - substituted(program, plan, start, delta, left, branches);
  }
  return total;
}

// ---------------------------------------------------------------------
// A law that READS THE COORDINATE IT DRIVES (`_Retained` and `_Walk`,
// design D2). Reuses `partition`, `branchesAt`, `levelOf`, `surfacesOf`
// and `branchOf` above rather than a second copy of any of them: a copy
// would drift from them at the first correction either received, which
// is exactly the failure the conformance corpus exists to prevent.
// ---------------------------------------------------------------------

/** How far the bracket for a far-side landing is grown, in doublings of
 * one ulp. `_WALK_STRIDES`: 200 doublings cover every distance a double
 * can express. */
const WALK_STRIDES = 200;

/** Whether a jump node's level sits EXACTLY on one of its surfaces
 * (`_on_surface`).
 *
 * Asked only at a piece's LEFT END under a self-read, where the value is
 * the coordinate's own retained one and the question is which branch the
 * piece begins under -- never of a midpoint, which is a point genuinely
 * inside its piece. */
export function onSurface(jump: ProgramJump, level: number): boolean {
  if (jump.primitive === 'sign' || jump.primitive in COMPARISONS) {
    return level === 0;
  }
  if (!Number.isFinite(level)) return false;
  // `%` is continuous where `a / b` crosses zero, so zero is not one of
  // its surfaces.
  if (jump.primitive === '%' && level === 0) return false;
  return level === Math.floor(level);
}

/** Python's `//` on two integers: FLOOR, where BigInt `/` truncates
 * toward zero. The two differ for a negative odd sum, which is every
 * other bisection round on a negative coordinate. */
function halved(sum: bigint): bigint {
  const quotient = sum / 2n;
  return (sum < 0n && quotient * 2n !== sum) ? quotient - 1n : quotient;
}

/** The nearest representable value on the FAR side of a surface
 * (`simulation/program.py`'s `far_side_of`).
 *
 * `branchAt(value)` reads the jump node's branch at one value of the
 * quantity being landed; `near` is the branch on the side the value came
 * from; `direction` is the sign of its travel; `unlanded` builds the
 * invariant error for a bracket that cannot be found.
 *
 * Membership of a value in the far side is decided by EVALUATING the
 * branch there, never by comparing the value to the surface: a solved
 * value at which the branch has already changed IS the landing, a strict
 * comparison against a representable threshold lands on the next value
 * beyond it, and a non-strict one lands on the threshold itself. The
 * bisection runs in FLOAT ORDINAL space, so adjacent floats differ by
 * one at any magnitude and no tolerance is involved.
 *
 * `scale` is the SEGMENT the landing sits on -- the largest magnitude
 * among the ends of the path being walked -- and it sizes the first step
 * of the bracket search, together with the landed value's own. The step
 * must be a distance THIS segment can express: the ulp of a value that
 * happens to be `0.0` is a denormal, and two hundred doublings of it
 * reach about 1e-263, which is no distance at all on a segment a
 * millimetre long. Scaling by the segment rather than by the landed
 * value alone is what lets a bank standing at exactly zero report its
 * stop instead of raising a broken invariant (machinome ADR-128,
 * closure 2). A caller that passes no `scale` keeps the value's own ulp
 * exactly as before, which is what `Walk.farSide` does: NO RUNNING
 * LANDING MOVES.
 *
 * Extracted from `Walk.farSide`, which still calls it, so the clocked
 * event solver and the clocked clip land by the SAME walk rather than a
 * second one (OpenSpec `execute-the-commit`, design §5 -- the
 * framework's own extraction, `machinome/simulation/program.py`
 * lines 1578-1646). */
export function farSideOf(branchAt: (value: number) => number, near: number,
                          ownStar: number, direction: number,
                          unlandedError: () => Error, scale = 0): number {
  const step = ulpOf(Math.max(Math.abs(ownStar), Math.abs(scale)));
  let inside: number | null;
  let far: number | null;
  if (branchAt(ownStar) !== near) {
    // The segment's arithmetic already landed PAST the surface, which
    // it does about as often as it lands short, so the bracket is
    // sought in both directions.
    far = ownStar;
    inside = null;
    for (let power = 0; power < WALK_STRIDES; power += 1) {
      const candidate = ownStar - direction * step * (2 ** power);
      if (branchAt(candidate) === near) {
        inside = candidate;
        break;
      }
    }
    if (inside === null) {
      // Unreachable by construction, and loud rather than silent
      // because of it: the cut exists because the level crossed this
      // surface, so the branch differs somewhere on either side of it,
      // and 200 doublings of a ulp cover every distance a double
      // expresses. NO TEST CAN REACH THIS; committing `ownStar`
      // instead would commit a value the design says is never
      // committed.
      throw unlandedError();
    }
  } else {
    inside = ownStar;
    far = null;
    for (let power = 0; power < WALK_STRIDES; power += 1) {
      const candidate = ownStar + direction * step * (2 ** power);
      if (branchAt(candidate) !== near) {
        far = candidate;
        break;
      }
    }
    if (far === null) {
      throw unlandedError();
    }
  }
  let low = ordinalOf(inside);
  let high = ordinalOf(far);
  for (;;) {
    const span = high - low;
    if ((span < 0n ? -span : span) <= 1n) break;
    const middle = halved(low + high);
    if (branchAt(fromOrdinal(middle)) === near) low = middle;
    else high = middle;
  }
  return fromOrdinal(high);
}

/** One driven end's piece-by-piece walk over one tick (`_Walk`). */
export type WalkPiece = [number, number, (t: number) => number,
  Record<string, number> | null];

export class Walk {
  private readonly delta: Record<string, number>;

  private taken = 0;
  private closedRight = false;

  constructor(private readonly program: LoadedProgram,
              private readonly reading: RetainedReading,
              private readonly start: Record<string, number>,
              delta: Record<string, number>,
              private readonly described: string,
              private readonly coordinate: string,
              // A SELECTOR's level reads no coordinate the block
              // determines -- the driven end included -- so a forced
              // node is always an INDEPENDENT one in ADR-057's split,
              // and forcing reaches the whole walk through layer one
              // alone (design D3).
              private readonly forced: Forced = null) {
    this.delta = copyHolding(delta, this.reading.own);
    // The driven coordinate's own source moves by NOTHING along the
    // path: what it holds on a piece is what the pieces before it
    // produced, never an increment the tick handed it.
    this.delta[this.reading.own] = 0;
    // Design D5/D7: layer one's own `LevelPaths`, over the walk's moving
    // names; one `PathValue` for the OUTER skeleton, over those same
    // names; and one `PathValue` per DEPENDENT jump's level, over those
    // names PLUS the driven coordinate -- because `levelOfJump` hands
    // that coordinate its own value at every point, so a dependent
    // node's level MOVES with it even though `this.delta` deliberately
    // zeroes its source (above).
    const moving = movingNames(this.delta);
    this.outerPaths = new LevelPaths(this.program, moving);
    this.skeletonPath = new ExpressionPath(
      this.reading.outer.skeleton, moving, this.program.bindings.roots);
    const own = new Set(moving);
    own.add(this.reading.own);
    for (const jump of this.reading.dependent) {
      this.levelPaths.set(
        jump.name, new ExpressionPath(jump.level, own, this.program.bindings.roots));
    }
  }

  /** Layer one's own level paths (D7). */
  private readonly outerPaths: LevelPaths;

  /** One path value for the outer skeleton, re-bound whenever `branches`
   * changes object identity -- a new piece (D6). */
  private readonly skeletonPath: ExpressionPath;

  private skeletonBound: Record<string, number> | null = null;

  private skeletonDisabled = false;

  /** One path value per DEPENDENT jump's level (D5, D7). */
  private readonly levelPaths = new Map<string, ExpressionPath>();

  private readonly levelBound = new Map<string, Record<string, number>>();

  private readonly levelDisabled = new Set<string>();

  // ------------------------------------------------------------------
  // The two layers

  run(crossings: CrossingRecord[] | null, tick: number, cutting = false,
      trajectory: WalkPiece[] | null = null, closed = false):
  { increment: number; landing: number | null; cuts: number[] } {
    this.closedRight = closed;
    const own = this.reading.own;
    const own0 = this.start[own];
    let moves = false;
    for (const name in this.delta) {
      if (!Object.prototype.hasOwnProperty.call(this.delta, name)) continue;
      if (name !== own && this.delta[name]) moves = true;
    }
    if (!moves) {
      // A tick in which no SOURCE moves contributes zero without
      // evaluating the law, exactly as any other law's does.
      return { increment: 0, landing: null, cuts: [0, 1] };
    }
    const outer = this.outerCuts(crossings, tick);
    let ownLeft = own0;
    let landed = false;
    const cuts = [0];
    for (let at = 0; at < outer.length - 1; at += 1) {
      const left = outer[at];
      const right = outer[at + 1];
      const outerBranches = this.outerBranches(left, right);
      let t = left;
      for (;;) {
        const branches = this.decide(t, right, ownLeft, outerBranches);
        const base = this.skeletonAt(t, branches);
        const from = ownLeft;
        /** The driven coordinate's own path on this piece -- one
         * ordinary evaluation, because the substituted skeleton does not
         * name it.
         *
         * The skeleton's CHANGE is taken FIRST. Left to right,
         * `(from + S) - base` rounds whenever `|S|` is comparable to
         * `|from|`, so a piece whose skeleton does not move would still
         * shift the coordinate by an ulp; taken this way an unchanged
         * skeleton adds a true zero and the coordinate keeps the exact
         * float it held. */
        const ownAt = (s: number): number =>
          from + (this.skeletonAt(s, branches) - base);
        const cut = this.firstCut(t, right, ownLeft, branches, ownAt);
        trajectory?.push([t, cut === null ? right : cut[0], ownAt, branches]);
        if (cutting && this.reading.kinks !== null) {
          // The SKELETON's own kinks, inside the piece this branch
          // reading holds over: between two of them the driven
          // coordinate's value is affine in `t`. Asked ONLY when the
          // caller wants the cuts -- a stop being localized -- so an
          // ordinary tick pays nothing for them (design D4 (c)).
          for (const where of this.skeletonCuts(
            t, cut === null ? right : cut[0], branches)) {
            cuts.push(where);
          }
        }
        if (cut === null) {
          ownLeft = ownAt(right);
          break;
        }
        const [where, crossed] = cut;
        const ownStar = ownAt(where);
        this.taken += 1;
        if (this.taken > this.program.limits.maxCrossings) {
          throw tooMany(this.described, this.coordinate,
                        crossed[0][1].primitive, this.taken,
                        this.program.limits);
        }
        ownLeft = this.land(crossed, where, ownLeft, ownStar, branches);
        landed = true;
        if (crossings !== null) {
          for (const [level, jump] of crossed) {
            crossings.push({
              tick,
              relation: this.described,
              coordinate: this.coordinate,
              primitive: jump.primitive,
              level,
              t: where,
            });
          }
        }
        cuts.push(where);
        t = where;
        if (t === right) break;
      }
      cuts.push(right);
    }
    return {
      increment: ownLeft - own0,
      landing: landed ? ownLeft : null,
      cuts,
    };
  }

  /** Layer one: ADR-107's own partition, over the jump nodes that do not
   * depend on the driven coordinate. */
  private outerCuts(crossings: CrossingRecord[] | null,
                    tick: number): number[] {
    if (this.reading.outer.jumps.length === 0) return [0, 1];
    return partition(this.program, this.reading.outer, this.start, this.delta,
                     this.described, this.coordinate, crossings, tick,
                     this.forced, this.outerPaths, this.closedRight);
  }

  private outerBranches(left: number, right: number): Record<string, number> {
    if (this.reading.outer.jumps.length === 0) return {};
    return branchesAt(this.program, this.reading.outer, this.start, this.delta,
                      (left + right) / 2, this.reading.outer.jumps.length,
                      this.described, this.coordinate, this.forced,
                      this.outerPaths);
  }

  // ------------------------------------------------------------------
  // The branches at a piece's LEFT END

  /** Every dependent node's branch at the piece's left end, in the
   * graph's postorder, with the driven coordinate at its RETAINED value
   * and every other source at `t`.
   *
   * A node whose level sits exactly on a surface takes the branch its
   * OPERATOR gives; if the level then LEAVES the surface into the other
   * branch's region, it is flipped there -- a zero-length piece -- and
   * every branch is decided again. A node flipped twice is a sliding
   * mode and refuses the tick. */
  private decide(t: number, right: number, ownLeft: number,
                 outerBranches: Record<string, number>):
  Record<string, number> {
    const forced = new Map<string, number>();
    const attempts = 2 * this.reading.dependent.length + 1;
    for (let attempt = 0; attempt < attempts; attempt += 1) {
      const { branches, sitting } =
        this.tentative(t, ownLeft, outerBranches, forced);
      let flip: [ProgramJump, number] | null = null;
      for (const jump of this.reading.dependent) {
        const surface = sitting.get(jump.name);
        if (surface === undefined) continue;
        const probe = this.probe(jump, surface, t, right, ownLeft, branches);
        if (probe === null) continue;
        // The branch of the region the level leaves the surface INTO --
        // the one immediately on that side -- and NEVER the branch at
        // the probe itself. A `floor` whose level departs downward from
        // `k` enters `(k - 1, k)` whatever the sample that showed it
        // moving reached, and a piece is integrated under the branch at
        // its own LEFT END: on a gate that changes the rate rather than
        // holding the part, that sample is several surfaces away and its
        // branch is not this piece's.
        const wanted = branchOf(jump.primitive, nextAfter(surface, probe));
        if (wanted !== branches[jump.name]) {
          flip = [jump, wanted];
          break;
        }
      }
      if (flip === null) return branches;
      const [jump, wanted] = flip;
      if (forced.has(jump.name)) {
        throw chattering(this.described, this.coordinate, jump.primitive);
      }
      forced.set(jump.name, wanted);
    }
    throw chattering(this.described, this.coordinate,
                     this.reading.dependent[0].primitive);
  }

  private tentative(t: number, ownLeft: number,
                    outerBranches: Record<string, number>,
                    forced: Map<string, number>):
  { branches: Record<string, number>; sitting: Map<string, number> } {
    const branches = { ...outerBranches };
    const sitting = new Map<string, number>();
    for (const jump of this.reading.dependent) {
      const level = this.levelOfJump(jump, t, ownLeft, branches);
      if (onSurface(jump, level)) sitting.set(jump.name, level);
      const chosen = forced.get(jump.name);
      branches[jump.name] = chosen === undefined
        ? branchOf(jump.primitive, level) : chosen;
    }
    return { branches, sitting };
  }

  /** The level's value at the FIRST point of the piece at which it
   * differs from the surface it sits on -- an inequality between two
   * evaluated floats, with no tolerance in it. */
  private probe(jump: ProgramJump, surface: number, t: number, right: number,
                ownLeft: number,
                branches: Record<string, number>): number | null {
    if (this.constantContact(jump, t, right, ownLeft, branches)) return null;
    const base = this.skeletonAt(t, branches);
    const subdivisions = this.program.limits.subdivisions;
    for (let step = 1; step <= subdivisions; step += 1) {
      const s = t + (right - t) * step / subdivisions;
      // The skeleton's change taken FIRST, as `ownAt` takes it.
      const own = ownLeft + (this.skeletonAt(s, branches) - base);
      const level = this.levelOfJump(jump, s, own, branches);
      if (level !== surface
          && !this.constantContact(jump, t, s, ownLeft, branches)) return level;
    }
    return null;
  }

  private constantContact(jump: ProgramJump, left: number, right: number,
                          ownLeft: number,
                          branches: Record<string, number>): boolean {
    if (curved(this.delta)) return false;
    return withExpressions(() => {
      const roots = this.program.bindings.roots();
      const level = this.program.nodeOf(jump.level);
      if (!hasMovingSource(level, this.delta, roots)) return false;
      const values = { ...along(this.start, this.delta, left), ...branches };
      return constantContact(this.program.nodeOf(this.reading.outer.skeleton),
                             level, values, this.delta, this.reading.own,
                             ownLeft, right - left, roots);
    });
  }

  // ------------------------------------------------------------------
  // The FIRST surface strictly inside the piece

  private firstCut(t: number, right: number, ownLeft: number,
                   branches: Record<string, number>,
                   ownAt: (s: number) => number):
  [number, [number, ProgramJump][]] | null {
    const found: [number, number, ProgramJump][] = [];
    for (const jump of this.reading.dependent) {
      const crossing = this.crossing(jump, t, right, ownLeft, branches, ownAt);
      if (crossing !== null) found.push([crossing[0], crossing[1], jump]);
    }
    if (found.length === 0) return null;
    let first = found[0][0];
    for (const [where] of found) if (where < first) first = where;
    // Two dependent nodes crossing at one fraction are ONE cut, and each
    // takes its far side.
    const crossed: [number, ProgramJump][] = found
      .filter(([where]) => where - first <= this.program.limits.crossingTolerance)
      .map(([, level, jump]) => [level, jump]);
    return [first, crossed];
  }

  private crossing(jump: ProgramJump, t: number, right: number,
                   ownLeft: number, branches: Record<string, number>,
                   ownAt: (s: number) => number): [number, number] | null {
    const limits = this.program.limits;
    const refuse = (count: number | null): never => {
      if (count === null) {
        throw noLevel(jump.primitive, this.described, this.coordinate);
      }
      throw tooMany(this.described, this.coordinate, jump.primitive, count,
                    limits);
    };
    // Note the difference from `crossingsOf`, which returns ALL the
    // surfaces between the two endpoints: under a self-read the path
    // is known only until the branch changes, so the walk takes the
    // FIRST and decides again. Three tooth windows in one tick are
    // still three throws, as three successive pieces.
    const solved = (left: number, stop: number, ownLow: number,
                    ownHigh: number,
                    closed: boolean): [number, number] | null => {
      const low = this.levelOfJump(jump, left, ownLow, branches);
      const high = this.levelOfJump(jump, stop, ownHigh, branches);
      if (high === low) return null;
      if (this.constantContact(jump, left, stop, ownLow, branches)) return null;
      const found = surfacesOf(jump, low, high, closed, limits, refuse)
        .filter((level) => !(closed && level === low));
      if (found.length === 0) return null;
      let best: [number, number] | null = null;
      for (const level of found) {
        const where = left + (stop - left) * (level - low) / (high - low);
        if (best === null || where < best[0]) best = [where, level];
      }
      return best;
    };
    if (curved(this.delta)) {
      return this.searched(jump, t, right, ownLeft, branches, ownAt, refuse);
    }
    if (jump.affine && this.reading.affine) {
      return solved(t, right, ownLeft, ownAt(right), this.closedRight && right === 1);
    }
    const jumpShape = jump.affine ? 'affine' : jump.shape;
    if (jumpShape === null || this.reading.shape === null) {
      return this.searched(jump, t, right, ownLeft, branches, ownAt, refuse);
    }
    // At least one of the two is KINKED and neither is curved, so the
    // piece is SOLVED on sub-intervals (openspec `solve-at-the-kink`,
    // design D4 (b)). The SKELETON's breakpoints come FIRST, because
    // they are what make the driven coordinate's own path `ownAt` affine
    // at all; the LEVEL's ride that path, so they are located INSIDE
    // each skeleton sub-piece, with the coordinate read by interpolation
    // between that sub-piece's two ends.
    const outer = [t, ...this.skeletonCuts(t, right, branches), right];
    for (let index = 0; index < outer.length - 1; index += 1) {
      const left = outer[index];
      const stop = outer[index + 1];
      const ownLow = left === t ? ownLeft : ownAt(left);
      const ownHigh = ownAt(stop);
      const inner = [left, ...this.levelCuts(jump, left, stop, ownLow,
                                             ownHigh, branches), stop];
      for (let step = 0; step < inner.length - 1; step += 1) {
        const lowT = inner[step];
        const highT = inner[step + 1];
        // Left to right, and the FIRST surface strictly inside the PIECE
        // wins -- `firstCut`'s own rule. The right end is inclusive for
        // every sub-piece but the very last, and the left end is
        // exclusive throughout, which is `searched`'s "the surface a
        // piece STARTS on is not one it crosses".
        const found = solved(
          lowT, highT,
          lowT === left ? ownLow : ownAt(lowT),
          highT === stop ? ownHigh : ownAt(highT),
          (this.closedRight && right === 1)
            || !(index === outer.length - 2 && step === inner.length - 2));
        if (found !== null) return found;
      }
    }
    return null;
  }

  /** The SKELETON's kink breakpoints strictly inside `[left, right]`,
   * under this piece's branch reading (`_skeleton_cuts`). */
  private skeletonCuts(left: number, right: number,
                       branches: Record<string, number>): number[] {
    if (this.reading.kinks === null || curved(this.delta)) return [];
    const at = (t: number): Record<string, number> => {
      const values = along(this.start, this.delta, t);
      for (const name in branches) {
        if (Object.prototype.hasOwnProperty.call(branches, name)) {
          values[name] = branches[name];
        }
      }
      return values;
    };
    return kinkBreaks(
      this.reading.kinks, (kink, t) => kinkLevel(this.program, kink, at(t)),
      left, right, this.program.limits.crossingTolerance);
  }

  /** A KINKED level's own breakpoints inside ONE skeleton sub-piece,
   * where the driven coordinate's path is affine and so reads by
   * interpolation between its two ends (`_level_cuts`). */
  private levelCuts(jump: ProgramJump, left: number, right: number,
                    ownLow: number, ownHigh: number,
                    branches: Record<string, number>): number[] {
    if (jump.kinks === null) return [];
    const span = right - left;
    const at = (t: number): Record<string, number> => {
      const values = along(this.start, this.delta, t);
      values[this.reading.own] = span === 0
        ? ownLow : ownLow + (ownHigh - ownLow) * (t - left) / span;
      for (const name in branches) {
        if (Object.prototype.hasOwnProperty.call(branches, name)) {
          values[name] = branches[name];
        }
      }
      return values;
    };
    return kinkBreaks(
      jump.kinks, (kink, t) => kinkLevel(this.program, kink, at(t)),
      left, right, this.program.limits.crossingTolerance);
  }

  /** A level that is not affine along the path: sampled, bracketed and
   * bisected on the same three tolerances a jump search already uses,
   * and stopped at the FIRST surface it reaches. */
  private searched(jump: ProgramJump, t: number, right: number,
                   ownLeft: number, branches: Record<string, number>,
                   ownAt: (s: number) => number,
                   refuse: (count: number | null) => never):
  [number, number] | null {
    const limits = this.program.limits;
    const width = (right - t) / limits.subdivisions;
    let previous = this.levelOfJump(jump, t, ownLeft, branches);
    for (let step = 1; step <= limits.subdivisions; step += 1) {
      const s = t + width * step;
      const level = this.levelOfJump(jump, s, ownAt(s), branches);
      if (level === previous) {
        // A level that does not MOVE crosses nothing. Worth saying here
        // and nowhere else: a dependent node whose branch holds the
        // driven coordinate still sits exactly on the surface it was
        // landed at for the whole piece, and an inclusive search would
        // report that surface as reached over and over.
        continue;
      }
      const found = surfacesOf(jump, previous, level, true, limits, refuse)
        // The surface a sub-interval STARTS on is not one it crosses. At
        // the piece's left end that surface is `decide`'s to answer, and
        // at an interior sample it was reached in the sub-interval
        // before and reported there -- the far-side landing leaves the
        // coordinate reading the far branch, so a level that walks on
        // from a surface it was placed at is LEAVING it.
        .filter((surface) => surface !== previous);
      // `surfacesOf` counts upward, so the surface the path reaches
      // FIRST is the one nearest the sample it starts from: `found[0]`
      // is the LAST one a DESCENDING level crosses, and cutting there
      // would integrate everything before it under a branch the path had
      // already left.
      const nearest = [...found].sort(
        (a, b) => Math.abs(a - previous) - Math.abs(b - previous));
      for (const surface of nearest) {
        // A sample that IS on the surface is the crossing, at that
        // sample; there is nothing to bisect toward.
        const where = level === surface
          ? s
          : this.bisectTo(jump, surface, previous, s - width, s, branches,
                          ownAt);
        // Every crossing strictly inside the piece is returned, one a
        // hair from its left end included: folding that one away would
        // integrate the piece under the near-side branch and drive the
        // part through its gap. `merged` and `deduplicated` belong to
        // layer one only.
        if (where > t) return [where, surface];
      }
      previous = level;
    }
    return null;
  }

  /** The bracket `[low, high]` narrowed onto `level`.
   *
   * `below` is the level at `low`, and `searched` has already excluded a
   * surface EQUAL to it, so the sign test below brackets something: a
   * `below` of zero would put every round in the `else` arm and collapse
   * the answer onto `high`. */
  private bisectTo(jump: ProgramJump, level: number, below: number,
                   low: number, high: number,
                   branches: Record<string, number>,
                   ownAt: (s: number) => number): number {
    const limits = this.program.limits;
    let under = below - level;
    let lower = low;
    let upper = high;
    for (let round = 0; round < limits.bisectionRounds; round += 1) {
      if (upper - lower <= limits.crossingTolerance) break;
      const middle = (lower + upper) / 2;
      const here =
        this.levelOfJump(jump, middle, ownAt(middle), branches) - level;
      if (here === 0 || (here < 0) !== (under < 0)) {
        upper = middle;
      } else {
        lower = middle;
        under = here;
      }
    }
    return (lower + upper) / 2;
  }

  // ------------------------------------------------------------------
  // The FAR-SIDE landing

  /** After a cut the driven coordinate is placed at the nearest
   * representable value on the FAR side of the surface.
   *
   * ADR-108's "committed AT its bound exactly", transposed to a surface
   * that is not stated in the coordinate's own units: the segment's
   * arithmetic finds the landing, and the landing is then walked to the
   * adjacent float. Where the piece did NOT move the coordinate there is
   * nothing to walk -- the level crossed by the sources' motion while
   * the gate held, and the coordinate stands where it stood. */
  private land(crossed: [number, ProgramJump][], where: number,
               ownLeft: number, ownStar: number,
               branches: Record<string, number>): number {
    if (ownStar === ownLeft) return ownStar;
    const direction = copySign(ownStar - ownLeft);
    let landing = ownStar;
    for (const [, jump] of crossed) {
      landing = this.farSide(jump, where, landing, direction, branches);
    }
    return landing;
  }

  private farSide(jump: ProgramJump, where: number, ownStar: number,
                  direction: number,
                  branches: Record<string, number>): number {
    const near = branches[jump.name];
    const branchAt = (value: number): number =>
      branchOf(jump.primitive,
               this.levelOfJump(jump, where, value, branches));
    // At fixed crossing sources the threshold may have overtaken the part.
    // Establish the LOCAL near-to-far orientation before the ordinal walk;
    // stationary thresholds keep their original point-evaluation path.
    if (withExpressions(() => hasMovingSource(
      this.program.nodeOf(jump.level), this.delta, this.program.bindings.roots()))) {
      const onNear = branchAt(ownStar) === near;
      const step = ulpOf(ownStar);
      let oriented: number | null = null;
      for (let power = 0; power < WALK_STRIDES; power += 1) {
        for (const side of [direction, -direction]) {
          const candidate = ownStar + side * step * (2 ** power);
          if ((branchAt(candidate) === near) !== onNear) {
            oriented = onNear ? side : -side;
            break;
          }
        }
        if (oriented !== null) break;
      }
      if (oriented === null) {
        throw unlanded(this.described, this.coordinate, jump.primitive, WALK_STRIDES);
      }
      direction = oriented;
    }
    // NO `scale`: a running landing is walked from the landed value's
    // own ulp, exactly as it was before the extraction (design §5). The
    // ulp-of-zero reading is closed on the CLOCKED side alone, so no
    // running landing moves.
    return farSideOf(branchAt, near, ownStar, direction,
                     () => unlanded(this.described, this.coordinate,
                                    jump.primitive, WALK_STRIDES));
  }

  // ------------------------------------------------------------------
  // Evaluation

  private skeletonAt(t: number, branches: Record<string, number>): number {
    const values = along(this.start, this.delta, t);
    for (const name in branches) {
      if (Object.prototype.hasOwnProperty.call(branches, name)) {
        values[name] = branches[name];
      }
    }
    if (this.skeletonDisabled) {
      return evaluateExpression(this.program, this.reading.outer.skeleton,
                                values);
    }
    // Design D6/D7: a new BRANCHES object is a new piece -- re-bound
    // whenever the reference changes, and taken at a point otherwise.
    const bind = this.skeletonBound !== branches;
    if (bind) this.skeletonBound = branches;
    try {
      return Number(bind ? this.skeletonPath.bind(values)
                          : this.skeletonPath.at(values));
    } catch (error) {
      if (!(error instanceof UnsupportedPathNode)) throw error;
      this.skeletonDisabled = true;
      return evaluateExpression(this.program, this.reading.outer.skeleton,
                                values);
    }
  }

  private levelOfJump(jump: ProgramJump, t: number, ownValue: number,
                      branches: Record<string, number>): number {
    const values = along(this.start, this.delta, t);
    values[this.reading.own] = ownValue;
    for (const name in branches) {
      if (Object.prototype.hasOwnProperty.call(branches, name)) {
        values[name] = branches[name];
      }
    }
    const path = this.levelDisabled.has(jump.name)
      ? undefined : this.levelPaths.get(jump.name);
    if (path === undefined) {
      return levelOf(this.program, this.reading.outer, jump, values,
                     this.described, this.coordinate);
    }
    const bind = this.levelBound.get(jump.name) !== branches;
    if (bind) this.levelBound.set(jump.name, branches);
    let level: number;
    try {
      level = Number(bind ? path.bind(values) : path.at(values));
    } catch (error) {
      if (!(error instanceof UnsupportedPathNode)) throw error;
      this.levelDisabled.add(jump.name);
      return levelOf(this.program, this.reading.outer, jump, values,
                     this.described, this.coordinate);
    }
    if (!Number.isFinite(level)) {
      throw noLevel(jump.primitive, this.described, this.coordinate,
                    Number.isNaN(level)
                      ? 'a level quantity that is not a number'
                      : undefined);
    }
    return level;
  }
}

/** `{ increment, landing }`: what a self-read driven end MOVES BY over
 * the tick, and the ABSOLUTE value it holds at the tick's end where at
 * least one cut placed it -- `null` where none did
 * (`_Retained.increment`). */
export function retainedIncrement(
  program: LoadedProgram, reading: RetainedReading,
  start: Record<string, number>, delta: Record<string, number>,
  described: string, coordinate: string,
  crossings: CrossingRecord[] | null, tick: number, forced: Forced = null,
): { increment: number; landing: number | null } {
  const walk = new Walk(program, reading, start, delta, described, coordinate,
                        forced);
  const { increment, landing } = walk.run(crossings, tick);
  return { increment, landing };
}

/** The breakpoints the two layers together put on the path
 * (`_Retained.cuts`). */
export function retainedCuts(
  program: LoadedProgram, reading: RetainedReading,
  start: Record<string, number>, delta: Record<string, number>,
  described: string, coordinate: string, forced: Forced = null,
): number[] {
  const walk = new Walk(program, reading, start, delta, described, coordinate,
                        forced);
  return walk.run(null, 0, true).cuts;
}

/** The breakpoints this law's own jumps put on the tick's path.
 *
 * Between two consecutive cuts every jump node holds one branch, so a
 * law whose SKELETON is affine has a value that is affine in `t` there
 * -- which is what lets a stop on it be SOLVED piece by piece rather
 * than searched. */
export function planPartition(
  program: PathHost, plan: ProgramPlan, start: Record<string, number>,
  delta: Record<string, number>, described: string, coordinate: string,
  forced: Forced = null,
): number[] {
  if (!Object.values(delta).some((value) => value !== 0)) return [0, 1];
  return partition(program, plan, start, delta, described, coordinate,
                   null, 0, forced);
}

/** `planPartition` with the SKELETON's own kinks unioned in --
 * `Edge.cuts`, which is what `Run.locate` solves a stop on.
 *
 * A CLOCKED clip wants `planPartition` alone (`Bounded.clip` calls
 * `JumpPlan.cuts`, and cuts the skeleton's kinks INSIDE each piece with
 * that piece's branches held), which is why the two are separate
 * functions rather than one (OpenSpec `execute-the-commit`, design §8). */
export function planCuts(
  program: PathHost, plan: ProgramPlan, start: Record<string, number>,
  delta: Record<string, number>, described: string, coordinate: string,
  forced: Forced = null,
): number[] {
  if (!Object.values(delta).some((value) => value !== 0)) return [0, 1];
  const cuts = planPartition(program, plan, start, delta, described,
                             coordinate, forced);
  if (plan.kinks === null) return cuts;
  // The skeleton reads the plan's BRANCH PLACEHOLDERS, which are
  // constant only within ONE piece of the plan's partition, so its kinks
  // are located inside each piece with that piece's branches
  // substituted, and the per-piece lists are unioned with the plan's own
  // cuts (openspec `solve-at-the-kink`, design D4 (c)).
  const found: number[] = [];
  for (let at = 0; at < cuts.length - 1; at += 1) {
    const left = cuts[at];
    const right = cuts[at + 1];
    const branches = branchesAt(program, plan, start, delta,
                                (left + right) / 2, plan.jumps.length,
                                described, coordinate, forced);
    const point = (t: number): Record<string, number> => {
      const values = along(start, delta, t);
      for (const name in branches) {
        if (Object.prototype.hasOwnProperty.call(branches, name)) {
          values[name] = branches[name];
        }
      }
      return values;
    };
    for (const where of kinkBreaks(
      plan.kinks, (kink, t) => kinkLevel(program, kink, point(t)),
      left, right, program.limits.crossingTolerance)) {
      found.push(where);
    }
  }
  return found.length === 0
    ? cuts : merged(cuts, found, program.limits.crossingTolerance);
}

/** A PLAN-LESS kinked law's breakpoints over the whole tick, as one
 * piece: `[]` where no kink of it is reached, which is the statement
 * that its path IS affine over the tick (design D4 (c)). */
export function kinkedEndCuts(
  program: PathHost, kinks: readonly KinkLevel[],
  start: Record<string, number>, delta: Record<string, number>,
): number[] {
  const found = kinkBreaks(
    kinks, (kink, t) => kinkLevel(program, kink, along(start, delta, t)),
    0, 1, program.limits.crossingTolerance);
  return found.length === 0
    ? [] : merged([0, 1], found, program.limits.crossingTolerance);
}

// ---------------------------------------------------------------------
// A BLOCK, ordered PER PIECE (`_Block.increments`, `_Block._partition`,
// `_Block._forced`, `_Block._order`, `_Block._refused`, `_Block.cuts`
// and `_integrated`, design D2). Reuses `partition`, `branchesAt` and
// `merged` above rather than a second copy of any of them, for the same
// reason the walk reuses them.
// ---------------------------------------------------------------------

/** Each member's sources at the stretch's start, and their travel over
 * it. */
function sourcesOfBlock(program: LoadedProgram, block: ProgramBlock, values: Record<string, number>,
                        deltas: Record<string, number>):
{ starts: Record<string, number>[]; steps: Record<string, number>[] } {
  const starts: Record<string, number>[] = [];
  const steps: Record<string, number>[] = [];
  for (const member of block.members) {
    const start: Record<string, number> = {};
    const step: Record<string, number> = {};
    for (const key of member.edge.needs) {
      const source = key === program.clock ? member.edge.timeDrive ?? key : key;
      start[key] = values[source];
      step[key] = deltas[source];
    }
    starts.push(start);
    steps.push(step);
  }
  return { starts, steps };
}

/** The stretch cut at every crossing of every SELECTOR of every member,
 * in the members' own order and each member's postorder
 * (`_Block._partition`).
 *
 * Every selector's level reads only coordinates the block does not give,
 * so its path over the stretch is the linearisation `values + deltas·t`
 * that `along` already builds: nothing new locates anything. */
function blockPartition(program: LoadedProgram, block: ProgramBlock,
                        starts: Record<string, number>[],
                        steps: Record<string, number>[],
                        crossings: CrossingRecord[] | null,
                        tick: number): number[] {
  let cuts = [0, 1];
  block.members.forEach((member, index) => {
    const plan = member.selectorPlan;
    if (plan === null || plan.jumps.length === 0) return;
    const found: CrossingRecord[] | null = crossings === null ? null : [];
    const located = partition(program, plan, starts[index], steps[index],
                              member.edge.description, member.own, found, tick);
    if (found !== null && found.length > 0) {
      for (const entry of found) crossings!.push(entry);
    }
    if (located.length > 2) {
      cuts = merged(cuts, located.slice(1, -1),
                    program.limits.crossingTolerance);
    }
  });
  return cuts;
}

/** Every selector's branch, read at one point of the stretch
 * (`_Block._forced`). */
function blockBranches(program: LoadedProgram, block: ProgramBlock,
                       starts: Record<string, number>[],
                       steps: Record<string, number>[],
                       where: number): Record<string, number>[] {
  return block.members.map((member, index) => {
    const plan = member.selectorPlan;
    if (plan === null || plan.jumps.length === 0) return {};
    return branchesAt(program, plan, starts[index], steps[index], where,
                      plan.jumps.length, member.edge.description, member.own);
  });
}

/** The refusal a still-cyclic piece makes, word for word
 * (`_Block._refused`). The WORDS are the producer's; the FLOATS are
 * spelled by each runtime -- Python's `repr` writes `1.0` where
 * JavaScript's `String` writes `1` -- and neither runtime ever sees the
 * other's message, because a refusal is not corpus state. */
function blockRefused(block: ProgramBlock, remaining: readonly number[],
                      forced: Record<string, number>[], left: number,
                      right: number): string {
  const branches: string[] = [];
  for (const index of remaining) {
    for (const jump of block.members[index].selectors) {
      branches.push(`${block.gives[index]}: ${jump.primitive} on `
                    + `${jump.level} reads ${forced[index][jump.name]}`);
    }
  }
  const stuck = remaining.map(
    (index) => block.members[index].edge.description).join(', ');
  return (
    `over the piece [${left}, ${right}] of this tick the relations ` +
    `${stuck} form a cycle the run cannot order: each waits on a ` +
    'coordinate another determines, and the selection this piece was read ' +
    'under leaves every dependency on this cycle active. The selectors ' +
    `read ${branches.join('; ') || 'nothing'}. The tick committed nothing: ` +
    'the bank, the tick count and the tree stand as they were.');
}

/** The members of this piece, ordered over the dependencies its own
 * selection leaves ACTIVE (`_Block._order`). */
export function blockOrder(block: ProgramBlock, forced: Record<string, number>[],
                    left: number, right: number): number[] {
  const active = block.members.map(
    (_member, index) => block.activeReads(index, forced[index]));
  let remaining = block.members.map((_member, index) => index);
  const resolved = new Set<string>();
  const order: number[] = [];
  while (remaining.length > 0) {
    const ready = remaining.filter((index) => [...active[index]].every(
      (key) => key === block.gives[index] || resolved.has(key)));
    if (ready.length === 0) {
      throw new UnsupportedLaw(
        blockRefused(block, remaining, forced, left, right));
    }
    for (const index of ready) {
      order.push(index);
      resolved.add(block.gives[index]);
    }
    remaining = remaining.filter((index) => !ready.includes(index));
  }
  return order;
}

/** One block member over one piece: `(increment, landing)`, by the
 * machinery that already governs it -- ADR-107's partition and ADR-121's
 * walk -- with its selectors FORCED (`_integrated`). */
function memberIncrement(program: LoadedProgram, member: BlockMember,
                         start: Record<string, number>,
                         delta: Record<string, number>,
                         crossings: CrossingRecord[] | null, tick: number,
                         forced: Forced):
{ increment: number; landing: number | null } {
  const edge = member.edge;
  const plan = member.plan;
  if (plan === null) {
    const expression = edge.expressions.length > 0 ? edge.expressions[0] : null;
    if (expression === null) return { increment: 0, landing: null };
    const end: Record<string, number> = {};
    for (const key in start) {
      if (Object.prototype.hasOwnProperty.call(start, key)) {
        end[key] = start[key] + delta[key];
      }
    }
    return {
      increment: evaluateExpression(program, expression, end)
        - evaluateExpression(program, expression, start),
      landing: null,
    };
  }
  const reading = edge.retained.length > 0 ? edge.retained[0] : null;
  if (reading === null) {
    return {
      increment: planIncrement(program, plan, start, delta, edge.description,
                               member.own, crossings, tick, forced),
      landing: null,
    };
  }
  return retainedIncrement(program, reading, start, delta, edge.description,
                           member.own, crossings, tick, forced);
}

/** The block's contribution to each of its coordinates over one stretch:
 * the selectors located FIRST over the whole stretch, and then the
 * members run PIECE BY PIECE in the order each piece's own selection
 * gives (`_Block.increments`, design D2).
 *
 * Complete and side-effect-free with `crossings`, `tick` and `landings`
 * absent -- `Run.along` and `Run.pushes` call it that way -- and still
 * refusing a genuinely cyclic piece under the SAME midpoint reading and
 * the SAME ordering the tick uses (design D2.7). */
export function blockIncrements(
  program: LoadedProgram, block: ProgramBlock,
  values: Record<string, number>, deltas: Record<string, number>,
  crossings: CrossingRecord[] | null, tick: number,
  landings: Record<string, number> | null,
): [string, number][] {
  const { starts, steps } = sourcesOfBlock(program, block, values, deltas);
  const located: CrossingRecord[] | null = crossings === null ? null : [];
  const cuts = blockPartition(program, block, starts, steps, located, tick);
  const advanced: Record<string, number> = {};
  const total: Record<string, number> = {};
  for (const key of block.gives) {
    advanced[key] = values[key];
    total[key] = 0;
  }
  const landed = new Set<string>();
  const orders = new Map<string, number[]>();
  for (let at = 0; at < cuts.length - 1; at += 1) {
    const left = cuts[at];
    const right = cuts[at + 1];
    const forced = blockBranches(program, block, starts, steps,
                                 (left + right) / 2);
    // Keyed by the vector of actual branch VALUES and not of booleans:
    // `branchOf` answers an integer for `floor`, `ceil` and `%`, so a
    // crank passing three tooth windows in one tick gives three keys.
    // `whole()` has already normalised `-0` to `0`, so the two zeros
    // cannot key two entries.
    const vector = forced.map((entry) => Object.keys(entry).sort().map(
      (name) => `${name}=${entry[name]}`).join(',')).join('|');
    let order = orders.get(vector);
    if (order === undefined) {
      order = blockOrder(block, forced, left, right);
      orders.set(vector, order);
    }
    const held: Record<string, number> = { ...advanced };
    const piece: Record<string, number> = {};
    for (const index of order) {
      const member = block.members[index];
      const own = member.own;
      const start: Record<string, number> = {};
      const delta: Record<string, number> = {};
      for (const key of member.edge.needs) {
        if (Object.prototype.hasOwnProperty.call(held, key)) {
          // A key the block DOES give: the BLOCK-ADVANCED value it holds
          // at this piece's start, moving by the increment computed for
          // it ON THIS PIECE -- zero where this piece's order has not
          // reached it yet.
          start[key] = held[key];
          delta[key] = Object.prototype.hasOwnProperty.call(piece, key)
            ? piece[key] : 0;
        } else {
          start[key] = starts[index][key] + steps[index][key] * left;
          delta[key] = steps[index][key] * (right - left);
        }
      }
      const found: CrossingRecord[] | null = located === null ? null : [];
      const { increment, landing } = memberIncrement(
        program, member, start, delta, found, tick, forced[index]);
      piece[own] = increment;
      total[own] += increment;
      if (landing === null) advanced[own] = advanced[own] + increment;
      else {
        advanced[own] = landing;
        landed.add(own);
      }
      if (found !== null && found.length > 0) {
        const width = right - left;
        for (const entry of found) {
          located!.push({ ...entry, t: left + entry.t * width });
        }
      }
    }
  }
  if (located !== null && located.length > 0) {
    // In the order the path meets them, as ADR-107's own partition
    // reports a law's: a selector's crossing is located over the whole
    // stretch and a member's own is rescaled out of its piece, and the
    // listing must not depend on which of the two was computed first.
    located.sort((a, b) => a.t - b.t);
    for (const entry of located) crossings!.push(entry);
  }
  if (landings !== null) {
    for (const key of landed) {
      // What the block reports is the ABSOLUTE value it has advanced the
      // coordinate to by the stretch's END -- the landing plus every
      // later piece's increment -- because `Run.landed` commits a
      // reported landing absolutely and would otherwise discard the
      // motion after it (design D4.1).
      landings[key] = advanced[key];
    }
  }
  return block.gives.map((key) => [key, total[key]]);
}

/** The breakpoints a block puts on the path for one of its coordinates:
 * the SELECTOR partition (`_Block.cuts`).
 *
 * `Run.locate` reaches this only through the AFFINE path and a block's
 * gives are never affine, so nothing calls it today. It is defined
 * rather than left to throw because `piecewise` becomes meaningful over
 * it the day a later cycle classifies a block give as affine under a
 * fixed branch vector (design D4.3). */
export function blockCuts(program: LoadedProgram, block: ProgramBlock,
                          values: Record<string, number>,
                          deltas: Record<string, number>): number[] {
  const { starts, steps } = sourcesOfBlock(program, block, values, deltas);
  return blockPartition(program, block, starts, steps, null, 0);
}
