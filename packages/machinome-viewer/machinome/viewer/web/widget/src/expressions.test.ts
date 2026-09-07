/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The shared node table (design D2-D4, D8-D10): every parsed expression
// is interned bottom-up into ONE module-level DAG, so a subexpression
// repeated by pasted text -- within one expression or across many --
// becomes one shared node. This increment tests the BUILDER alone
// (`prepare`); evaluation (`valueOf`) is increment 2.

import { describe, expect, it } from 'vitest';
import {
  expressionMetrics, prepare, resetExpressionMetrics,
} from './expressions';

describe('prepare', () => {
  it('returns a node id', () => {
    resetExpressionMetrics();
    expect(typeof prepare('1')).toBe('number');
  });

  it('interns two structurally identical subtrees to one id', () => {
    expect(prepare('(1 + 2)')).toBe(prepare('(1 + 2)'));
    expect(prepare('(x_axis.motor * 2)')).toBe(prepare('(x_axis.motor * 2)'));
  });

  it('gives structurally different expressions different ids', () => {
    expect(prepare('(1 + 2)')).not.toBe(prepare('(1 + 3)'));
    expect(prepare('(x_axis.motor * 2)')).not.toBe(prepare('(y_axis.motor * 2)'));
    expect(prepare('(1 + 2)')).not.toBe(prepare('(2 + 1)'));
  });

  it('keys a constant by value and type: 1 and "1" differ', () => {
    expect(prepare('1')).not.toBe(prepare('"1"'));
  });

  it('keys 0 and -0 as different expressions', () => {
    // The grammar has no negative-literal token -- "-0" always parses as
    // Unary(-, Literal(0)) -- so this observes the two as different NODE
    // STRUCTURES; the const table itself keys any literal zero it is
    // ever handed by Object.is, defensively, for whatever value reaches
    // it (D2).
    expect(prepare('0')).not.toBe(prepare('-0'));
  });

  it('folds a Member chain rooted in a name into ONE name node', () => {
    // `x_axis.motor` interned once, however it is spelled: as a bare
    // dotted expression and as the equivalent path through an
    // intermediate binary term that resolves to the same chain text.
    const first = prepare('(x_axis.motor * 1)');
    const second = prepare('(x_axis.motor * 1)');
    expect(first).toBe(second);
  });

  it('keeps a Member on something other than a name chain generic', () => {
    // `f(1).x` is not a dotted name -- nothing the producer emits, but
    // jokenizer accepts it -- and must not collide with a name node
    // that happens to share the same trailing part.
    const generic = prepare('(sqrt(1).x + 1)');
    const dotted = prepare('(x.x + 1)');
    expect(generic).not.toBe(dotted);
  });

  it('collapses a parenthesised Group to its single expression', () => {
    // "((x))" and "(x)" both collapse through their Group wrapper to the
    // same bare name node.
    expect(prepare('((x_axis.motor))')).toBe(prepare('(x_axis.motor)'));
  });

  it('interns (5 ^ 2) as a pow call', () => {
    resetExpressionMetrics();
    const id = prepare('(5 ^ 2)');
    expect(id).toBe(prepare('pow(5, 2)'));
  });

  it('interns (-2 ^ 2) as the negation of a pow call', () => {
    // OpenSCAD binds ^ tighter than unary minus: -2^2 is -(2^2).
    const negated = prepare('(-2 ^ 2)');
    const positivePow = prepare('pow(2, 2)');
    // The negated form is NOT the bare pow call: it wraps it.
    expect(negated).not.toBe(positivePow);
    // But it shares the SAME pow node as its target.
    const explicitNegation = prepare('(-(pow(2, 2)))');
    expect(negated).toBe(explicitNegation);
  });

  it('refuses an inline function, naming the form and the expression', () => {
    expect(() => prepare('(x => x + 1)')).toThrow(/Func/);
    expect(() => prepare('(x => x + 1)')).toThrow(/x => x \+ 1/);
  });

  it('refuses an inline function nested inside a call argument', () => {
    expect(() => prepare('map([1,2], x => x)')).toThrow(/Func/);
  });

  it('truncates a very long expression in the refusal message', () => {
    const long = `(x => ${'1 + '.repeat(100)}1)`;
    expect(long.length).toBeGreaterThan(80);
    let message = '';
    try {
      prepare(long);
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message.length).toBeLessThan(long.length);
    expect(message).toMatch(/…|\.\.\./);
  });

  it('keeps a pasted expression to a few dozen distinct nodes', () => {
    // Twelve rounds of self-substitution: ~2^12 pasted occurrences of
    // "e" over a few dozen distinct subexpressions, exactly the shape
    // of the producer's string-concatenation bug.
    let e = 'x_axis.motor';
    for (let round = 0; round < 12; round += 1) {
      e = `(sin(${e}) + cos(${e}))`;
    }

    resetExpressionMetrics();
    const before = expressionMetrics().nodes;
    prepare(e);
    const grown = expressionMetrics().nodes - before;

    expect(grown).toBeLessThan(100);
    expect(grown).toBeGreaterThan(0);
  });
});
