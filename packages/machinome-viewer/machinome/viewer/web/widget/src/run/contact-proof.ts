/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Conservative algebraic certificates, NOT replacement bank arithmetic.
// All finite binary inputs are exact rationals. Unknown expressions and
// nonzero slopes (however small) never certify constant relative contact.
import { calleeName, structureOf } from '../expressions';
import type { NodeId } from '../expressions';

type Rational = readonly [bigint, bigint];
type Affine = readonly [Rational, Rational];
type Bindings = ReadonlyMap<string, NodeId>;
const ZERO: Rational = [0n, 1n];
const ONE: Rational = [1n, 1n];

function rational(n: bigint, d = 1n): Rational {
  if (d === 0n) throw new RangeError('zero denominator');
  if (n === 0n) return ZERO;
  if (d < 0n) { n = -n; d = -d; }
  let a = n < 0n ? -n : n;
  let b = d;
  while (b !== 0n) { const rem = a % b; a = b; b = rem; }
  return [n / a, d / a];
}
function add(a: Rational, b: Rational): Rational {
  return rational(a[0] * b[1] + b[0] * a[1], a[1] * b[1]);
}
function neg(a: Rational): Rational { return [-a[0], a[1]]; }
function sub(a: Rational, b: Rational): Rational { return add(a, neg(b)); }
function mul(a: Rational, b: Rational): Rational {
  return rational(a[0] * b[0], a[1] * b[1]);
}
function div(a: Rational, b: Rational): Rational {
  return rational(a[0] * b[1], a[1] * b[0]);
}
function number(value: number): Rational {
  if (!Number.isFinite(value)) throw new RangeError('nonfinite input');
  if (value === 0) return ZERO;
  const bytes = new DataView(new ArrayBuffer(8));
  bytes.setFloat64(0, value);
  const bits = bytes.getBigUint64(0);
  const exponent = Number((bits >> 52n) & 0x7ffn);
  const fraction = bits & ((1n << 52n) - 1n);
  let n = exponent === 0 ? fraction : fraction + (1n << 52n);
  if (bits >> 63n) n = -n;
  const shift = (exponent === 0 ? 1 : exponent) - 1023 - 52;
  return shift >= 0 ? rational(n << BigInt(shift))
    : rational(n, 1n << BigInt(-shift));
}

export function hasMovingSource(root: NodeId, delta: Record<string, number>,
                                bindings: Bindings = new Map()): boolean {
  const seen = new Set<NodeId>();
  const pending = [root];
  while (pending.length) {
    const id = pending.pop()!;
    if (seen.has(id)) continue;
    seen.add(id);
    const node = structureOf(id);
    if (node.kind === 'name') {
      if (delta[node.name!]) return true;
      const bound = bindings.get(node.name!);
      if (bound !== undefined) pending.push(bound);
    } else pending.push(...node.children);
  }
  return false;
}

function affinePiece(root: NodeId, inputs: Map<string, Affine>,
                     bindings: Bindings, splits: Rational[] = []): Affine | null {
  const memo = new Map<NodeId, Affine | null>();
  const visit = (id: NodeId): Affine | null => {
    if (memo.has(id)) return memo.get(id)!;
    memo.set(id, null); // Invalid cyclic bindings cannot furnish a proof.
    const node = structureOf(id);
    const args = node.children.map(visit);
    let result: Affine | null = null;
    if (node.kind === 'const' && typeof node.value === 'number') {
      result = [number(node.value), ZERO];
    } else if (node.kind === 'name') {
      const bound = bindings.get(node.name!);
      result = inputs.get(node.name!) ?? (bound === undefined ? null : visit(bound));
    } else if (node.kind === 'unary' && args[0] !== null) {
      if (node.op === '-') result = [neg(args[0][0]), neg(args[0][1])];
      else if (node.op === '+') result = args[0];
    } else if (node.kind === 'binary') {
      const [a, b] = args;
      const zero = (v: Affine | null): boolean =>
        v !== null && v[0][0] === 0n && v[1][0] === 0n;
      if (node.op === '*' && (zero(a) || zero(b))) result = [ZERO, ZERO];
      else if (a !== null && b !== null) {
        if (node.op === '+') result = [add(a[0], b[0]), add(a[1], b[1])];
        else if (node.op === '-') result = [sub(a[0], b[0]), sub(a[1], b[1])];
        else if (node.op === '*' && (a[1][0] === 0n || b[1][0] === 0n)) {
          result = [mul(a[0], b[0]), add(mul(a[0], b[1]), mul(a[1], b[0]))];
        } else if (node.op === '/' && b[1][0] === 0n && b[0][0] !== 0n) {
          result = [div(a[0], b[0]), div(a[1], b[0])];
        }
      }
    } else if (node.kind === 'call' && args.every(a => a !== null)) {
      const name = calleeName(id);
      const a = args[0]!;
      if (name === 'abs' && args.length === 1) {
        const end = add(a[0], a[1]);
        if (a[0][0] >= 0n && end[0] >= 0n) result = a;
        else if (a[0][0] <= 0n && end[0] <= 0n) result = [neg(a[0]), neg(a[1])];
        else splits.push(div(neg(a[0]), a[1]));
      } else if ((name === 'min' || name === 'max') && args.length === 2) {
        const b = args[1]!;
        const low = sub(a[0], b[0]);
        const high = sub(add(a[0], a[1]), add(b[0], b[1]));
        if (low[0] >= 0n && high[0] >= 0n) result = name === 'max' ? a : b;
        else if (low[0] <= 0n && high[0] <= 0n) result = name === 'max' ? b : a;
        else splits.push(div(neg(low), sub(high, low)));
      }
    }
    memo.set(id, result);
    return result;
  };
  return visit(root);
}

export function constantContact(skeleton: NodeId, level: NodeId,
                                values: Record<string, number>,
                                delta: Record<string, number>, own: string,
                                ownValue: number, width: number,
                                bindings: Bindings = new Map(),
                                maxPieces = 1024): boolean {
  try {
    const span = number(width);
    const inputs = new Map<string, Affine>(Object.entries(values).map(([n, v]) =>
      [n, [number(v), mul(number(delta[n] ?? 0), span)]]));
    const origin = affinePiece(skeleton, new Map([...inputs].map(([n, v]) =>
      [n, [v[0], ZERO]])), bindings);
    if (origin === null) return false;
    const pending: [Rational, Rational][] = [[ZERO, ONE]];
    for (let piece = 0; piece < maxPieces; piece += 1) {
      if (!pending.length) return true;
      const [left, right] = pending.pop()!;
      const local = new Map<string, Affine>([...inputs].map(([n, v]) =>
        [n, [add(v[0], mul(v[1], left)), mul(v[1], sub(right, left))]]));
      const splits: Rational[] = [];
      const path = affinePiece(skeleton, local, bindings, splits);
      if (path !== null) {
        local.set(own, [add(number(ownValue), sub(path[0], origin[0])), path[1]]);
        const contact = affinePiece(level, local, bindings, splits);
        if (contact !== null) {
          if (contact[1][0] !== 0n) return false;
          continue;
        }
      }
      if (!splits.length) return false;
      const middle = add(left, mul(sub(right, left), splits[0]));
      if (sub(middle, left)[0] <= 0n || sub(right, middle)[0] <= 0n) return false;
      pending.push([middle, right], [left, middle]);
    }
    return false;
  } catch (error) {
    if (!(error instanceof RangeError)) throw error;
    return false; // The ordinary executor retains its own error semantics.
  }
}
