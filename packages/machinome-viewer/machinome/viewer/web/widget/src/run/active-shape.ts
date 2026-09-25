/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */
import { calleeName, structureOf } from '../expressions';
import type { KinkLevel, NodeId, PathShape } from '../expressions';

interface Reading {
  shape: PathShape;
  names: ReadonlySet<string>;
  kinks: readonly KinkLevel[];
  zero: boolean;
}

/** Classify the existing DAG with the producer's literal-zero fold. This
 * inspects structure only: expression evaluation still has one seam. Node
 * IDs are used only inside the caller's withExpressions scope. */
export function activeShape(root: NodeId, standing: Record<string, number>,
                            bindings?: ReadonlyMap<string, NodeId>): Reading {
  const constant = (zero = false): Reading =>
    ({ shape: 'constant', names: new Set(), kinks: [], zero });
  const memo = new Map<NodeId, Reading>();
  const movable = (shape: PathShape): boolean => shape !== null;
  const visit = (id: NodeId): Reading => {
    const cached = memo.get(id);
    if (cached) return cached;
    const node = structureOf(id);
    let found: Reading;
    if (node.kind === 'const') {
      found = { ...constant(node.value === 0),
        shape: typeof node.value === 'number' ? 'constant' : null };
    } else if (node.kind === 'name') {
      const name = node.name!;
      if (Object.prototype.hasOwnProperty.call(standing, name)) found = constant(standing[name] === 0);
      else if (bindings?.has(name)) found = visit(bindings.get(name)!);
      else found = { shape: 'affine', names: new Set([name]), kinks: [], zero: false };
    } else {
      const children = node.children.map(visit);
      const [left, right] = children;
      if (node.kind === 'binary' && (
        (node.op === '*' && (left.zero || right.zero))
        || (node.op === '/' && left.zero))) found = constant(true);
      else if (node.kind === 'binary' && node.op === '+' && left.zero) found = right;
      else if (node.kind === 'binary' && (node.op === '+' || node.op === '-') && right.zero) found = left;
      else {
        let shape: PathShape = null;
        if (children.length && children.every(child => child.shape === 'constant')) shape = 'constant';
        else if (node.kind === 'unary' && (node.op === '+' || node.op === '-')) shape = left.shape;
        else if (node.kind === 'binary') {
          if (node.op === '+' || node.op === '-') {
            if (movable(left.shape) && movable(right.shape)) {
              shape = children.some(child => child.shape === 'kinked') ? 'kinked' : 'affine';
            }
          } else if (node.op === '*') {
            if (left.shape === 'constant') shape = right.shape;
            else if (right.shape === 'constant') shape = left.shape;
          } else if (node.op === '/' && right.shape === 'constant') shape = left.shape;
        }
        const callee = node.kind === 'call' ? calleeName(id) : null;
        const kink = callee === 'abs' || callee === 'min' || callee === 'max';
        if (kink && shape !== 'constant' && children.every(child => movable(child.shape))) shape = 'kinked';
        const kinks = children.flatMap(child => [...child.kinks]);
        if (kink) kinks.push({ a: node.children[0], b: callee === 'abs' ? null : node.children[1] });
        found = { shape, names: new Set(children.flatMap(child => [...child.names])), kinks, zero: false };
      }
    }
    memo.set(id, found);
    return found;
  };
  return visit(root);
}
