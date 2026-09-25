/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */
import { calleeName, expressionGeneration, structureOf, withExpressions } from '../expressions';
import type { NodeId } from '../expressions';
import { activeShape } from './active-shape';
import { checkedLawValue, evaluateExpression, UnsupportedLaw } from './program';
import type { LoadedProgram, ProgramBlock, ProgramEdge, ProgramPlan } from './program';
import { along, blockOrder, branchesAt, deduplicated, expressionKinkBreaks, merged, partition, tooMany, Walk } from './jumps';
import type { CrossingRecord, WalkPiece } from './jumps';
import { Motion, propagations, sourceDeltas } from './motion';
import type { ConstantBlockEntry, Piece, Propagation } from './motion';
import { edgeIncrements, linearOf } from './edges';

type Motions = Map<string, Motion>;
type Bank = Record<string, number>;

// Terminal correction may evaluate a relation at its authored endpoint.
// Only a closed numeric graph may be read again: `random`, a shadowed
// function, or a coercing object must keep the original evaluation cadence.
const CLOSED_CALLS = new Set([
  'abs', 'acosh', 'asinh', 'atanh', 'cbrt', 'ceil', 'cosh', 'exp',
  'expm1', 'floor', 'fround', 'hypot', 'ln', 'log1p', 'log2',
  'log10', 'max', 'min', 'mod', 'pow', 'round', 'sign', 'sinh',
  'sqrt', 'tanh', 'trunc',
]);
const CLOSED_CONSTANTS = new Set([
  'E', 'LN2', 'LN10', 'LOG2E', 'LOG10E', 'PI', 'SQRT1_2', 'SQRT2',
]);
// Unlike context.sin/cos/tan/asin/acos/atan/atan2/log, the listed Math
// callees are captured when the expression evaluator loads. Reject obvious
// pre-import replacements, but this is not proof against a Proxy disguising
// itself as native; standard Math at module import is the platform precondition.
// The live-delegating wrappers are deliberately not in CLOSED_CALLS.
const CAPTURED_MATH = new Map<string, boolean>([...CLOSED_CALLS]
  .filter(name => name !== 'mod' && name !== 'sign')
  .map(name => {
    const method = name === 'ln' ? 'log' : name;
    try {
      const fn = (Math as unknown as Record<string, unknown>)[method];
      return [name, typeof fn === 'function'
        && Function.prototype.toString.call(fn).includes('[native code]')];
    } catch {
      return [name, false];
    }
  }));

function closedTerminalLaw(program: LoadedProgram, edge: ProgramEdge, values: Bank,
                           includePlans = false): boolean {
  try {
    return withExpressions(() => {
      const bindings = program.bindings.roots();
      const available = new Set(Object.keys(values));
      const placeholders = new Set(includePlans ? edge.plans.flatMap(plan =>
        plan === null ? [] : plan.jumps.map(jump => jump.name)) : []);
      const safe = new Set<NodeId>();
      const visiting = new Set<NodeId>();
      const check = (root: NodeId): boolean => {
        const stack: [NodeId, boolean][] = [[root, false]];
        while (stack.length) {
          const [id, done] = stack.pop()!;
          if (safe.has(id)) continue;
          if (done) {
            visiting.delete(id);
            safe.add(id);
            continue;
          }
          if (visiting.has(id)) return false;
          visiting.add(id);
          const node = structureOf(id);
          let children = node.children;
          if (node.kind === 'const') {
            if (!(typeof node.value === 'boolean'
              || (typeof node.value === 'number' && Number.isFinite(node.value)))) return false;
          } else if (node.kind === 'name' && node.name !== null) {
            const head = node.name.split('.')[0];
            const binding = bindings?.get(head);
            if (binding !== undefined) {
              if (head !== node.name) return false;
              children = [binding];
            } else if (!placeholders.has(node.name)
                && !(available.has(node.name) && Number.isFinite(values[node.name]))
                && !CLOSED_CONSTANTS.has(node.name)) return false;
          } else if (node.kind === 'call') {
            const name = calleeName(id);
            if (name === null || !CLOSED_CALLS.has(name)
                || bindings?.has(name) || available.has(name)) return false;
            if (CAPTURED_MATH.get(name) === false) return false;
          } else if (node.kind !== 'unary' && node.kind !== 'binary'
                     && node.kind !== 'ternary') return false;
          stack.push([id, true]);
          for (let index = children.length - 1; index >= 0; index -= 1) {
            stack.push([children[index], false]);
          }
        }
        return true;
      };
      const expressions = includePlans ? [...edge.expressions,
        ...edge.plans.flatMap(plan => plan === null ? []
          : [plan.skeleton, ...plan.jumps.map(jump => jump.level)])] : edge.expressions;
      return expressions.every(expression =>
        expression === null || check(program.nodeOf(expression)));
    });
  } catch {
    // The scheduled evaluator, not this preflight, owns the first error.
    return false;
  }
}

function cutsOf(program: LoadedProgram, motions: Motions): number[] {
  let cuts = [0, 1];
  for (const motion of motions.values()) cuts = merged(cuts, motion.cuts(), program.limits.crossingTolerance);
  return cuts;
}

function sourcesAt(motions: Motions, left: number, right: number): [Bank, Bank] {
  const selected = new Map([...motions].map(([name, motion]) => [name, motion.restrict(left, right)]));
  const start = Object.fromEntries([...selected].map(([name, motion]) => [name, motion.start]));
  const delta = [...selected.values()].every(motion => motion.affine && !motion.exactTerminal)
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
    const terminalSources = [...motions.values()].some(motion => motion.exactTerminal);
    const affine = whole.shape !== null && [...motions.values()].every(m => m.affine && !m.exactTerminal);
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
          edge.gives[index], forced, edge.statedBy).run(found, tick, false, local, closed || right < 1);
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
          const evaluate = (t: number) => checkedLawValue(edge, edge.gives[index],
            evaluateExpression(program, expression, { ...along(start, delta, t), ...branches }));
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
        const terminalPiece = terminalSources && shape !== null && [...motions].some(([name, m]) =>
          shape.names.has(name) && m.exactTerminal);
        const breaks = pieceAffine && shape?.shape === 'kinked'
          ? expressionKinkBreaks(program, shape.kinks, start, delta, branches ?? {},
            a, b, program.limits.crossingTolerance) : [];
        allAffine &&= pieceAffine && !terminalPiece;
        const edges = [a, ...breaks, b];
        for (let part = 0; part < edges.length - 1; part += 1) {
          const low = edges[part];
          const high = edges[part + 1];
          let fn = evaluate;
          if (pieceAffine && !terminalPiece) {
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

/** No expression is evaluated by this preflight. Uncertainty retains the walk. */
function constantBlockKey(program: LoadedProgram, block: ProgramBlock, values: Bank,
                          trace: Propagation, sourceMaps: readonly Motions[]):
  (string | number | boolean)[] | null {
  if (trace.blockReuse === undefined || trace.terminals !== undefined) return null;
  try {
    if (block.members.some(member => member.edge.timeDrive !== undefined
        || !closedTerminalLaw(program, member.edge, values, true))) return null;
    const names = new Set(block.gives);
    for (const member of block.members) {
      for (const name of member.edge.needs) names.add(name);
    }
    const key: (string | number | boolean)[] = [];
    for (const name of [...names].sort()) {
      if (!Object.prototype.hasOwnProperty.call(values, name)
          || typeof values[name] !== 'number' || !Number.isFinite(values[name])) return null;
      key.push(name, values[name]);
    }
    for (const sources of sourceMaps) {
      for (const [name, motion] of sources) {
        if (!motion.constant || !motion.affine || !Number.isFinite(motion.start)
            || !Number.isFinite(motion.end) || !Object.is(motion.start, motion.end)
            || motion.pieces.length !== 1 || motion.pieces[0][0] !== 0
            || motion.pieces[0][1] !== 1 || motion.cuts().length !== 0) return null;
        key.push(name, motion.start, motion.end, motion.exactTerminal);
      }
    }
    return key;
  } catch {
    return null;
  }
}

function sameBlockKey(left: readonly (string | number | boolean)[],
                      right: readonly (string | number | boolean)[]): boolean {
  return left.length === right.length && left.every((value, index) => Object.is(value, right[index]));
}

function blockMotion(program: LoadedProgram, block: ProgramBlock, values: Bank,
                     deltas: Bank, trace: Propagation, crossings: CrossingRecord[] | null,
                     tick: number, landings: Bank | null,
                     terminalAllowed = true): [string, number][] {
  const first = crossings?.length ?? 0;
  const sourceMaps = block.members.map(member => new Map(member.edge.needs.map(key =>
    [key, block.gives.includes(key) ? Motion.line(values[key], 0)
      : !terminalAllowed && trace.terminals?.has(sourceKey(program, member.edge, key))
        ? Motion.line(values[key], deltas[key])
        : motionOf(sourceKey(program, member.edge, key), values, deltas, trace)])));
  const reuseKey = constantBlockKey(program, block, values, trace, sourceMaps);
  const cached = reuseKey === null ? undefined : trace.blockReuse?.stored.get(block);
  if (cached !== undefined && cached.generation === expressionGeneration()
      && sameBlockKey(cached.key, reuseKey!)) {
    const result: [string, number][] = [];
    for (const output of cached.outputs) {
      trace.motions.set(output.name, new Motion(output.start, output.end,
        [[0, 1, () => output.start]], true, output.exactTerminal));
      result.push([output.name, output.increment]);
    }
    return result;
  }
  const earlierLandings = landings === null ? null : { ...landings };
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
  const terminalOutputs = new Set<string>();
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
      if (terminalAllowed && trace.terminals !== undefined && member.edge.needs.some(key =>
        trace.terminals!.has(sourceKey(program, member.edge, key)) || terminalOutputs.has(key))) {
        // The selected branch can fold a named source away. Inspect only
        // after the ordinary member walk succeeded, and never let this
        // metadata check replace its first error or activate a dead read.
        const expression = member.plan?.skeleton ?? member.edge.expressions[0];
        if (expression !== null) {
          try {
            const names = withExpressions(() => activeShape(program.nodeOf(expression),
              forced[index], program.bindings.roots()).names);
            if ([...names].some(name => trace.terminals!.has(sourceKey(program, member.edge, name))
                || terminalOutputs.has(name))) terminalOutputs.add(own);
          } catch {
            // An unsupported inspection leaves the original path intact.
          }
        }
      }
      const width = right - left;
      pieces.get(own)!.push(...motion.pieces.map(([a, b, fn]): Piece =>
        [left + width * a, left + width * b, t => fn((t - left) / width)]));
      if (found) crossings!.push(...found.map(entry => ({ ...entry, t: left + width * entry.t })));
    }
  }
  for (const key of block.gives) {
    const terminal = terminalOutputs.has(key)
      && !Object.is(values[key] + (current[key] - values[key]), current[key]);
    trace.motions.set(key, new Motion(values[key], current[key], pieces.get(key)!, affine.get(key)!, terminal));
    if (terminal) trace.terminals!.set(key, current[key]);
    if (landings && (landed.has(key) || terminal)) landings[key] = current[key];
  }
  if (crossings) crossings.splice(first, crossings.length - first,
    ...crossings.slice(first).sort((a, b) => a.t - b.t));
  const result: [string, number][] = block.gives.map(key => [key, current[key] - values[key]]);
  if (reuseKey !== null && (crossings === null || crossings.length === first)
      && landed.size === 0 && terminalOutputs.size === 0
      && (landings === null || (Object.keys(landings).length === Object.keys(earlierLandings!).length
        && Object.keys(landings).every(key => Object.is(landings[key], earlierLandings![key]))))) {
    const outputs = result.map(([name, increment]) => {
      const motion = trace.motions.get(name)!;
      return { name, start: motion.start, end: motion.end,
        exactTerminal: motion.exactTerminal, increment, motion };
    });
    if (outputs.every(({ start, end, increment, motion }) => Number.isFinite(start)
        && Number.isFinite(end) && Object.is(start, end) && Object.is(increment, 0)
        && motion.constant && motion.affine && motion.pieces.length === 1
        && motion.pieces[0][0] === 0 && motion.pieces[0][1] === 1
        && motion.cuts().length === 0)) {
      const entry: ConstantBlockEntry = {
        key: reuseKey,
        generation: expressionGeneration(),
        outputs: outputs.map(({ name, start, end, exactTerminal, increment }) =>
          ({ name, start, end, exactTerminal, increment })),
      };
      trace.blockReuse!.pending.set(block, entry);
    }
  }
  return result;
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
    const result = followIncrements(program, edge, values, deltas, tick, landings);
    if (trace.terminals !== undefined
        && edge.needs.slice(0, 2).some(key => trace.terminals!.has(key)) && landings) {
      const key = edge.gives[0];
      if (!Object.is(values[key] + result[0][1], landings[key])) {
        trace.terminals.set(key, landings[key]);
      }
    }
    return result;
  }
  if (edge.kind === 'play' || edge.needs.some(key => trace.untraced.has(key))) {
    edge.gives.forEach(key => trace.untraced.add(key));
    const terminalLaw = edge.kind === 'law' && trace.terminals !== undefined
      && edge.needs.some(key => trace.terminals!.has(sourceKey(program, edge, key)))
      && !edge.plans.some(Boolean) && closedTerminalLaw(program, edge, values);
    // The old untraced law evaluates its rounded end first, then its
    // start. Substitute only the exact end scope in that same two-read
    // sequence; do not first invoke the old endpoint (which may lie just
    // outside the authored domain).
    const start = terminalLaw
      ? Object.fromEntries(edge.needs.map(key => [key, values[key]])) : null;
    const end = terminalLaw
      ? Object.fromEntries(edge.needs.map(key =>
        [key, trace.terminals!.get(sourceKey(program, edge, key)) ?? values[key] + deltas[key]])) : null;
    const readings = new Map<string, [number, number]>();
    const result = terminalLaw ? edge.gives.map((key, index): [string, number] => {
      const expression = edge.expressions[index];
      if (expression === null) return [key, 0];
      const after = checkedLawValue(edge, key,
        evaluateExpression(program, expression, end!));
      const before = checkedLawValue(edge, key,
        evaluateExpression(program, expression, start!));
      readings.set(key, [before, after]);
      return [key, after - before];
    }) : legacy();
    if (edge.kind === 'play' && trace.terminals?.has(edge.needs[0]) && landings) {
      const key = edge.gives[0];
      if (!Object.is(values[key] + result[0][1], landings[key])) {
        trace.terminals.set(key, landings[key]);
      }
    }
    if (terminalLaw) {
      for (const [key, increment] of result) {
        const index = edge.gives.indexOf(key);
        const expression = edge.expressions[index];
        if (expression === null) continue;
        const [before, after] = readings.get(key)!;
        const endpoint = Object.is(values[key], before) ? after : values[key] + (after - before);
        trace.terminals!.set(key, endpoint);
        if (landings) landings[key] = endpoint;
        trace.motions.set(key, new Motion(values[key], endpoint,
          [[0, 1, t => values[key] + increment * t]], true, true));
      }
    }
    return result;
  }
  if (edge.kind === 'block') {
    const terminalAllowed = trace.terminals === undefined || edge.block!.members.every(member =>
      closedTerminalLaw(program, member.edge, values));
    return blockMotion(program, edge.block!, values, deltas, trace, crossings, tick,
      landings, terminalAllowed);
  }
  if (edge.kind === 'law') {
    const hasTerminal = trace.terminals !== undefined
      && edge.needs.some(key => trace.terminals!.has(sourceKey(program, edge, key)));
    const terminal = hasTerminal && closedTerminalLaw(program, edge, values);
    // A stateful or uncertain relation stays on its original traced path.
    // Marking it untraced would turn each Bound sample into a fresh prefix
    // replay and multiply random/custom calls.
    const sources = new Map(edge.needs.map(key => {
      const source = sourceKey(program, edge, key);
      return [key, hasTerminal && !terminal && trace.terminals!.has(source)
        ? Motion.line(values[key], deltas[key])
        : motionOf(source, values, deltas, trace)];
    }));
    const linear = [...sources.values()].every(m => m.affine && !m.cuts().length);
    if (terminal && !edge.plans.some(Boolean)
        && edge.shapes.every(shape => shape === 'constant' || shape === 'affine')) {
      const result = legacy();
      const start = Object.fromEntries([...sources].map(([name, path]) => [name, path.start]));
      const end = Object.fromEntries([...sources].map(([name, path]) => [name, path.end]));
      for (const [key, increment] of result) {
        const expression = edge.expressions[edge.gives.indexOf(key)];
        if (expression === null) continue;
        const before = checkedLawValue(edge, key,
          evaluateExpression(program, expression, start));
        const after = checkedLawValue(edge, key,
          evaluateExpression(program, expression, end));
        const endpoint = Object.is(values[key], before) ? after : values[key] + (after - before);
        trace.terminals!.set(key, endpoint);
        if (landings) landings[key] = endpoint;
        trace.motions.set(key, new Motion(values[key], endpoint,
          [[0, 1, t => values[key] + increment * t]], true, true));
      }
      return result;
    }
    if (!terminal && linear && !edge.plans.some(Boolean) && edge.shapes.every(shape => shape === 'constant' || shape === 'affine')) {
      const result = legacy();
      for (const [key, increment] of result) trace.motions.set(key, Motion.line(values[key], increment));
      return result;
    }
    if (!terminal && linear && !edge.gives.some(key => trace.demanded.has(key))) return legacy();
    return edge.gives.map((key, index) => {
      let [motion, landed] = lawMotion(program, edge, index, sources, values[key], crossings, tick);
      // A continuous endpoint may have an exact authored landing even when
      // held + (end - start) rounds beside it. Only a full terminal target
      // reaches this branch; retained offsets keep their integrated delta.
      if (terminal && edge.plans[index] === null && edge.retained[index] == null
          && edge.expressions[index] !== null) {
        const start = Object.fromEntries([...sources].map(([name, path]) => [name, path.start]));
        const end = Object.fromEntries([...sources].map(([name, path]) => [name, path.end]));
        const before = checkedLawValue(edge, key,
          evaluateExpression(program, edge.expressions[index]!, start));
        const after = checkedLawValue(edge, key,
          evaluateExpression(program, edge.expressions[index]!, end));
        const exact = Object.is(values[key], before) ? after : values[key] + (after - before);
        motion = new Motion(values[key], exact, motion.pieces, false, true);
        landed = true;
      }
      trace.motions.set(key, motion);
      if (terminal) {
        trace.terminals ??= new Map();
        trace.terminals.set(key, motion.end);
      }
      if ((landed || terminal) && landings) landings[key] = motion.end;
      return [key, motion.end - values[key]];
    });
  }
  const result = legacy();
  if (edge.kind === 'wiring' || edge.kind === 'formula') {
    const sources = new Map(edge.needs.map(key => [key, motionOf(key, values, deltas, trace)]));
    const terminal = trace.terminals !== undefined
      && edge.needs.some(key => trace.terminals!.has(key));
    const cuts = cutsOf(program, sources);
    for (const [key, increment] of result) {
      const at = (t: number) => {
        const local = Object.fromEntries([...sources].map(([need, source]) => [need, source.at(t) - values[need]]));
        return values[key] + (edge.kind === 'wiring' ? local[edge.needs[0]] * edge.factor : linearOf(edge, local, 0));
      };
      let endpoint = values[key] + increment;
      if (terminal) {
        const before = edge.kind === 'wiring'
          ? sources.get(edge.needs[0])!.start * edge.factor
          : linearOf(edge, Object.fromEntries([...sources].map(([name, path]) => [name, path.start])));
        const after = edge.kind === 'wiring'
          ? sources.get(edge.needs[0])!.end * edge.factor
          : linearOf(edge, Object.fromEntries([...sources].map(([name, path]) => [name, path.end])));
        endpoint = Object.is(values[key], before) ? after : values[key] + (after - before);
      }
      trace.motions.set(key, new Motion(values[key], endpoint,
        cuts.slice(0, -1).map((a, i) => [a, cuts[i + 1], at]),
        [...sources.values()].every(m => m.affine), terminal));
      if (terminal) {
        trace.terminals ??= new Map();
        trace.terminals.set(key, endpoint);
        if (landings) landings[key] = endpoint;
      }
    }
  }
  return result;
}
