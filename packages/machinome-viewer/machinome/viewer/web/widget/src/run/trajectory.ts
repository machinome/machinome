/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */
import { withExpressions } from '../expressions';
import { activeShape } from './active-shape';
import { evaluateExpression, UnsupportedLaw } from './program';
import type { LoadedProgram, ProgramBlock, ProgramEdge, ProgramPlan } from './program';
import { along, blockOrder, branchesAt, deduplicated, expressionKinkBreaks, merged, partition, tooMany, Walk } from './jumps';
import type { CrossingRecord, WalkPiece } from './jumps';
import { Motion, propagations, sourceDeltas } from './motion';
import type { Piece, Propagation } from './motion';
import { edgeIncrements, linearOf } from './edges';

type Motions = Map<string, Motion>;
type Bank = Record<string, number>;

function cutsOf(program: LoadedProgram, motions: Motions): number[] {
  let cuts = [0, 1];
  for (const motion of motions.values()) cuts = merged(cuts, motion.cuts(), program.limits.crossingTolerance);
  return cuts;
}

function sourcesAt(motions: Motions, left: number, right: number): [Bank, Bank] {
  const selected = new Map([...motions].map(([name, motion]) => [name, motion.restrict(left, right)]));
  const start = Object.fromEntries([...selected].map(([name, motion]) => [name, motion.start]));
  const delta = [...selected.values()].every(motion => motion.affine)
    ? Object.fromEntries([...selected].map(([name, motion]) => [name, motion.end - motion.start]))
    : sourceDeltas(selected);
  return [start, delta];
}

function motionOf(key: string, values: Bank, deltas: Bank, trace: Propagation): Motion {
  return trace.motions.get(key) ?? Motion.line(values[key], deltas[key]);
}

function sourceKey(program: LoadedProgram, edge: ProgramEdge, key: string): string {
  return key === program.clock && edge.timeDrive !== undefined ? edge.timeDrive : key;
}

function lawMotion(program: LoadedProgram, edge: ProgramEdge, index: number,
                   motions: Motions, initial: number, crossings: CrossingRecord[] | null,
                   tick: number, forced: Bank | null = null, closed = false): [Motion, boolean] {
  if ([...motions.values()].every(motion => motion.constant)) return [Motion.line(initial, 0), false];
  return withExpressions(() => {
    const plan = edge.plans[index];
    let reading = edge.retained[index] ?? null;
    const expression = plan?.skeleton ?? edge.expressions[index];
    if (expression === null) return [Motion.line(initial, 0), false];
    const standing = { ...Object.fromEntries([...motions].filter(([, m]) => m.constant)
      .map(([name, m]) => [name, m.start])), ...forced };
    const classify = (branches: Bank) => activeShape(program.nodeOf(expression),
      { ...standing, ...branches }, program.bindings.roots());
    const whole = classify({});
    const affine = whole.shape !== null && [...motions.values()].every(m => m.affine);
    if (reading && affine && reading.shape !== whole.shape) {
      reading = { ...reading, shape: whole.shape,
        kinks: whole.shape === 'kinked' ? whole.kinks : null };
    }
    const pieces: Piece[] = [];
    let current = initial;
    let landed = false;
    let allAffine = true;
    const cuts = cutsOf(program, motions);
    for (let at = 0; at < cuts.length - 1; at += 1) {
      const left = cuts[at];
      const right = cuts[at + 1];
      const [start, delta] = sourcesAt(motions, left, right);
      const found: CrossingRecord[] | null = crossings === null ? null : [];
      const local: WalkPiece[] = [];
      if (reading) {
        start[reading.own] = current;
        const result = new Walk(program, reading, start, delta, edge.description,
          edge.gives[index], forced).run(found, tick, false, local, closed || right < 1);
        if (!local.length) {
          const held = current;
          local.push([0, 1, () => held, null]);
        }
        current = result.landing === null ? current + result.increment : result.landing;
        landed ||= result.landing !== null;
      } else {
        const partitions = plan ? partition(program, plan, start, delta, edge.description,
          edge.gives[index], found, tick, forced, null, closed || right < 1) : [0, 1];
        for (let part = 0; part < partitions.length - 1; part += 1) {
          const low = partitions[part];
          const high = partitions[part + 1];
          const branches = plan ? branchesAt(program, plan, start, delta, (low + high) / 2,
            plan.jumps.length, edge.description, edge.gives[index], forced) : {};
          const evaluate = (t: number) => evaluateExpression(program, expression, { ...along(start, delta, t), ...branches });
          const base = evaluate(low);
          const from = current;
          const value = (t: number) => from + (evaluate(t) - base);
          local.push([low, high, value, branches]);
          current = value(high);
        }
      }
      const width = right - left;
      for (const [a, b, evaluate, branches] of local) {
        if (b <= a) continue;
        const shape = branches === null ? null : classify(branches);
        const pieceAffine = shape === null || (shape.shape !== null
          && [...motions].every(([name, m]) => !shape.names.has(name) || m.affine));
        const breaks = pieceAffine && shape?.shape === 'kinked'
          ? expressionKinkBreaks(program, shape.kinks, start, delta, branches ?? {},
            a, b, program.limits.crossingTolerance) : [];
        allAffine &&= pieceAffine;
        const edges = [a, ...breaks, b];
        for (let part = 0; part < edges.length - 1; part += 1) {
          const low = edges[part];
          const high = edges[part + 1];
          let fn = evaluate;
          if (pieceAffine) {
            const lowValue = evaluate(low);
            const slope = (evaluate(high) - lowValue) / (high - low);
            fn = t => lowValue + slope * (t - low);
          }
          const frozen = fn;
          pieces.push([left + width * low, left + width * high, t => frozen((t - left) / width)]);
        }
      }
      if (found) crossings!.push(...found.map(entry => ({ ...entry, t: left + width * entry.t })));
    }
    return [new Motion(initial, current, pieces, allAffine), landed];
  });
}

function blockMotion(program: LoadedProgram, block: ProgramBlock, values: Bank,
                     deltas: Bank, trace: Propagation, crossings: CrossingRecord[] | null,
                     tick: number, landings: Bank | null): [string, number][] {
  const first = crossings?.length ?? 0;
  const sourceMaps = block.members.map(member => new Map(member.edge.needs.map(key =>
    [key, block.gives.includes(key) ? Motion.line(values[key], 0)
      : motionOf(sourceKey(program, member.edge, key), values, deltas, trace)])));
  let cuts = [0, 1];
  block.members.forEach((member, index) => {
    const plan = member.selectorPlan;
    if (!plan) return;
    const sources = sourceMaps[index];
    const reads = withExpressions(() => new Set(plan.jumps.flatMap(jump =>
      [...activeShape(program.nodeOf(jump.level), {}, program.bindings.roots()).names])));
    const outer = cutsOf(program, new Map([...sources].filter(([name]) => reads.has(name))));
    cuts = merged(cuts, outer.slice(1, -1), program.limits.crossingTolerance);
    for (let part = 0; part < outer.length - 1; part += 1) {
      const left = outer[part];
      const right = outer[part + 1];
      const [start, delta] = sourcesAt(sources, left, right);
      const found: CrossingRecord[] | null = crossings === null ? null : [];
      const local = partition(program, plan, start, delta, member.edge.description,
        member.own, found, tick, null, null, right < 1);
      cuts = merged(cuts, local.slice(1, -1).map(t => left + (right - left) * t), program.limits.crossingTolerance);
      if (found) crossings!.push(...found.map(entry => ({ ...entry, t: left + (right - left) * entry.t })));
    }
  });
  const current = Object.fromEntries(block.gives.map(key => [key, values[key]]));
  const pieces = new Map(block.gives.map(key => [key, [] as Piece[]]));
  const affine = new Map(block.gives.map(key => [key, true]));
  const landed = new Set<string>();
  for (let part = 0; part < cuts.length - 1; part += 1) {
    const left = cuts[part];
    const right = cuts[part + 1];
    const forced = block.members.map((member, index) => {
      const [start, delta] = sourcesAt(sourceMaps[index], left, right);
      return member.selectorPlan ? branchesAt(program, member.selectorPlan, start, delta,
        .5, member.selectorPlan.jumps.length, member.edge.description, member.own) : {};
    });
    const determined = new Map<string, Motion>();
    for (const index of blockOrder(block, forced, left, right)) {
      const member = block.members[index];
      const own = member.own;
      const sources = new Map(member.edge.needs.map(key => [key,
        key in current ? determined.get(key) ?? Motion.line(current[key], 0)
          : motionOf(sourceKey(program, member.edge, key), values, deltas, trace).restrict(left, right)]));
      const found: CrossingRecord[] | null = crossings === null ? null : [];
      const [motion, didLand] = lawMotion(program, member.edge, 0, sources, current[own],
        found, tick, forced[index], right < 1);
      determined.set(own, motion);
      current[own] = motion.end;
      affine.set(own, affine.get(own)! && motion.affine);
      if (didLand) landed.add(own);
      const width = right - left;
      pieces.get(own)!.push(...motion.pieces.map(([a, b, fn]): Piece =>
        [left + width * a, left + width * b, t => fn((t - left) / width)]));
      if (found) crossings!.push(...found.map(entry => ({ ...entry, t: left + width * entry.t })));
    }
  }
  for (const key of block.gives) {
    trace.motions.set(key, new Motion(values[key], current[key], pieces.get(key)!, affine.get(key)!));
    if (landings && landed.has(key)) landings[key] = current[key];
  }
  if (crossings) crossings.splice(first, crossings.length - first,
    ...crossings.slice(first).sort((a, b) => a.t - b.t));
  return block.gives.map(key => [key, current[key] - values[key]]);
}

/** Certified boundary cut locations, using the producer's original source
 * delta rather than a reconstructed (end - start) chord. */
function followBoundaryCuts(program: LoadedProgram, edge: ProgramEdge,
                            expression: string, plan: ProgramPlan | null,
                            start: Bank, delta: Bank, tick: number): number[] {
  const skeleton = plan?.skeleton ?? expression;
  const parts = plan ? partition(program, plan, start, delta,
    edge.description, edge.gives[0], null, tick) : [0, 1];
  const cuts = [...parts];
  for (let i = 0; i < parts.length - 1; i += 1) {
    const left = parts[i];
    const right = parts[i + 1];
    const branches = plan ? branchesAt(program, plan, start, delta,
      (left + right) / 2, plan.jumps.length, edge.description, edge.gives[0]) : {};
    const shape = withExpressions(() => activeShape(program.nodeOf(skeleton),
      branches, program.bindings.roots()));
    if (shape.shape === null) {
      throw new UnsupportedLaw(`${edge.description}: Follow envelope is not certified piecewise affine.`);
    }
    if (shape.shape === 'kinked') {
      cuts.push(...expressionKinkBreaks(program, shape.kinks, start, delta, branches,
        left, right, program.limits.crossingTolerance));
    }
  }
  return [...new Set(cuts)].sort((a, b) => a - b);
}

/** The absolute retained projection, including both numeric sides of a cut. */
export function followIncrements(program: LoadedProgram, edge: ProgramEdge, values: Bank,
                                 deltas: Bank, tick: number, landings: Bank | null): [string, number][] {
  const trace = propagations.get(deltas);
  const own = edge.gives[0];
  const names = edge.needs.slice(0, 2);
  const sources = new Map(names.map(name => [name,
    trace?.motions.get(name) ?? Motion.line(values[name], deltas[name] ?? 0)]));
  for (const [name, motion] of sources) {
    if (!motion.affine || motion.pieces.length !== 1) {
      throw new UnsupportedLaw(`${edge.description}: Follow source ${name} lacks one certified affine path.`);
    }
  }
  if ([...sources.values()].every(motion => motion.constant
      && (motion.start !== 0 || Object.is(motion.start, motion.end)))) return [[own, 0]];
  const start = Object.fromEntries(names.map(name => [name, sources.get(name)!.start]));
  const delta = Object.fromEntries(names.map(name => [name, deltas[name] ?? 0]));
  const lower = edge.lower!;
  const upper = edge.upper!;
  const cuts = [...new Set([
    ...followBoundaryCuts(program, edge, lower, edge.lowerPlan, start, delta, tick),
    ...followBoundaryCuts(program, edge, upper, edge.upperPlan, start, delta, tick),
  ])].sort((a, b) => a - b);
  const scopeAt = (t: number, closure: boolean): Bank => Object.fromEntries(names.map(name => {
    const motion = sources.get(name)!;
    return [name, closure ? motion.pieces[0][2](t) : motion.at(t)];
  }));
  const direct = (t: number): [number, number] => {
    const scope = scopeAt(t, false);
    return [evaluateExpression(program, lower, scope), evaluateExpression(program, upper, scope)];
  };
  const absolute = (expression: string, plan: ProgramPlan | null, middle: number):
  ((t: number) => number) => {
    if (plan === null) return t => evaluateExpression(program, expression, scopeAt(t, true));
    const middleScope = scopeAt(middle, false);
    const zero = Object.fromEntries(names.map(name => [name,
      Object.is(middleScope[name], -0) ? -0 : 0]));
    const branches = branchesAt(program, plan, middleScope, zero, 0,
      plan.jumps.length, edge.description, own);
    return t => evaluateExpression(program, plan.skeleton,
      { ...scopeAt(t, true), ...branches });
  };
  let current = values[own];
  const project = (low: number, high: number): void => {
    if (![low, high, current].every(Number.isFinite)) {
      throw new UnsupportedLaw(`${edge.description}: Follow encountered a non-finite envelope or retained value.`);
    }
    // Python's max(low, min(current, high)) selects its first operand at
    // equality. Math.min/Math.max select signed zero by a different rule.
    const inner = current <= high ? current : high;
    current = low >= inner ? low : inner;
  };
  const closures: [number, number, number, number][] = [];
  project(...direct(0));
  for (let i = 0; i < cuts.length - 1; i += 1) {
    const left = cuts[i];
    const right = cuts[i + 1];
    const middle = (left + right) / 2;
    const lowAt = absolute(lower, edge.lowerPlan, middle);
    const highAt = absolute(upper, edge.upperPlan, middle);
    project(lowAt(left), highAt(left));
    const lowClose = lowAt(right);
    const highClose = highAt(right);
    project(lowClose, highClose);
    closures.push([right, current, lowClose, highClose]);
    project(...direct(right));
  }
  if (landings !== null) landings[own] = current;
  if (trace && ![...sources.values()].every(motion => motion.constant)) {
    (trace.followCuts ??= new Map()).set(own, cuts);
    (trace.followClosures ??= new Map()).set(own, closures);
  }
  return [[own, current - values[own]]];
}

export function propagate(program: LoadedProgram, edge: ProgramEdge, values: Bank,
                          deltas: Bank, crossings: CrossingRecord[] | null, tick: number,
                          landings: Bank | null): [string, number][] {
  const found: CrossingRecord[] = [];
  const result = propagated(program, edge, values, deltas, found, tick, landings);
  const byCoordinate = new Map<string, CrossingRecord[]>();
  for (const entry of found) {
    const key = JSON.stringify([entry.relation, entry.coordinate]);
    const entries = byCoordinate.get(key) ?? [];
    entries.push(entry);
    byCoordinate.set(key, entries);
  }
  for (const entries of byCoordinate.values()) {
    const count = deduplicated(entries.map(entry => [entry.t, 0]), program.limits.crossingTolerance).length;
    if (count > program.limits.maxCrossings) {
      const entry = entries[entries.length - 1];
      throw tooMany(entry.relation, entry.coordinate, entry.primitive, count, program.limits);
    }
  }
  if (crossings) crossings.push(...found);
  return result;
}

function propagated(program: LoadedProgram, edge: ProgramEdge, values: Bank,
                    deltas: Bank, crossings: CrossingRecord[] | null, tick: number,
                    landings: Bank | null): [string, number][] {
  const trace = propagations.get(deltas)!;
  const legacy = () => edgeIncrements(program, edge, values, { ...deltas }, crossings, tick, landings);
  if (edge.kind === 'follow') {
    edge.gives.forEach(key => trace.untraced.add(key));
    return followIncrements(program, edge, values, deltas, tick, landings);
  }
  if (edge.kind === 'play' || edge.needs.some(key => trace.untraced.has(key))) {
    edge.gives.forEach(key => trace.untraced.add(key));
    return legacy();
  }
  if (edge.kind === 'block') return blockMotion(program, edge.block!, values, deltas, trace, crossings, tick, landings);
  if (edge.kind === 'law') {
    const sources = new Map(edge.needs.map(key => [key,
      motionOf(sourceKey(program, edge, key), values, deltas, trace)]));
    const linear = [...sources.values()].every(m => m.affine && !m.cuts().length);
    if (linear && !edge.plans.some(Boolean) && edge.shapes.every(shape => shape === 'constant' || shape === 'affine')) {
      const result = legacy();
      for (const [key, increment] of result) trace.motions.set(key, Motion.line(values[key], increment));
      return result;
    }
    if (linear && !edge.gives.some(key => trace.demanded.has(key))) return legacy();
    return edge.gives.map((key, index) => {
      const [motion, landed] = lawMotion(program, edge, index, sources, values[key], crossings, tick);
      trace.motions.set(key, motion);
      if (landed && landings) landings[key] = motion.end;
      return [key, motion.end - values[key]];
    });
  }
  const result = legacy();
  if (edge.kind === 'wiring' || edge.kind === 'formula') {
    const sources = new Map(edge.needs.map(key => [key, motionOf(key, values, deltas, trace)]));
    const cuts = cutsOf(program, sources);
    for (const [key, increment] of result) {
      const at = (t: number) => {
        const local = Object.fromEntries([...sources].map(([need, source]) => [need, source.at(t) - values[need]]));
        return values[key] + (edge.kind === 'wiring' ? local[edge.needs[0]] * edge.factor : linearOf(edge, local, 0));
      };
      trace.motions.set(key, new Motion(values[key], values[key] + increment,
        cuts.slice(0, -1).map((a, i) => [a, cuts[i + 1], at]), [...sources.values()].every(m => m.affine)));
    }
  }
  return result;
}
