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

import { evaluate as jokEvaluate, tokenize as jokTokenize } from 'jokenizer';
import { describe, expect, it } from 'vitest';
import {
  EXPRESSION_LIMITS, expressionMetrics, prepare, releaseExpressions,
  resetExpressionMetrics, retainExpressions, valueOf,
} from './expressions';
// The comparison baseline for increment 2's semantics tests: at this
// point in the cycle `evaluator.ts` is UNCHANGED, so `evalExpr` still
// runs jokenizer's own `tokenize` + the established `^`/exponent
// rewrites + jokenizer's own `evaluate` (D1's "jokenizer's own
// evaluate" comparison, transitively -- the two numeric
// implementations this cycle briefly runs side by side, design.md
// "Risks / Trade-offs").
import { evalExpr } from './evaluator';

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

function pastedExpression(): string {
  let e = 'x_axis.motor';
  for (let round = 0; round < 12; round += 1) {
    e = `(sin(${e}) + cos(${e}))`;
  }
  return e;
}

// The pass/memo state (D6) is module-level, spanning the whole file's
// tests as it spans a whole page's viewers. A test that wants to
// observe a GENUINE first resolution -- not a memo hit left standing by
// an earlier test that happened to use an equal-valued scope -- needs a
// scope value no earlier test could have used. This hands out such
// values, so every "first touch" below is real.
let sentinelMotor = 1_000_000;
function freshMotor(): number {
  sentinelMotor += 1;
  return sentinelMotor;
}

describe('valueOf: semantics agree with the shipped evaluator', () => {
  const agrees = (expression: string,
                   scope: { time: number; drivers?: Record<string, unknown> }) => {
    const viaDag = valueOf(prepare(expression), scope as never);
    const viaShipped = evalExpr(expression, scope as never);
    expect(viaDag).toBeCloseTo(viaShipped, 9);
  };

  it('agrees on degree trig through the OpenSCAD context', () => {
    agrees('sin(90)', { time: 0 });
    agrees('cos(180)', { time: 0 });
    agrees('asin(0.5)', { time: 0 });
    agrees('atan2(1, 1)', { time: 0 });
  });

  it('agrees on mod, ln and log(base, value)', () => {
    agrees('mod(7, 3)', { time: 0 });
    agrees('ln(2.5)', { time: 0 });
    agrees('log(2, 8)', { time: 0 });
  });

  it('agrees on ^ under a leading minus', () => {
    agrees('(-2 ^ 2)', { time: 0 });
    agrees('(5 ^ 2)', { time: 0 });
  });

  it('agrees on a dotted driver term', () => {
    agrees('(x_axis.motor * 0.0125)', { time: 0, drivers: { x_axis: { motor: 8000 } } });
  });

  it('agrees when a driver shadows a context name', () => {
    agrees('(sin * 2)', { time: 0, drivers: { sin: 5 } });
  });

  it('agrees when a driver value is 0', () => {
    agrees('(x_axis.motor * 2)', { time: 0, drivers: { x_axis: { motor: 0 } } });
  });

  it('agrees on a ternary', () => {
    agrees('(x_axis.motor ? 1 : -1)', { time: 0, drivers: { x_axis: { motor: 8000 } } });
    agrees('(x_axis.motor ? 1 : -1)', { time: 0, drivers: { x_axis: { motor: 0 } } });
  });

  it('short-circuits && without forcing an undefined right side', () => {
    // `nope` names nothing: forcing it would read `undefined` into the
    // arithmetic below and the two implementations would disagree.
    expect(valueOf(prepare('(0 && (1 / nope))'), { time: 0 } as never)).toBe(0);
    expect(evalExpr('(0 && (1 / nope))', { time: 0 })).toBe(0);
  });
});

describe('valueOf: missing and odd owners (D5)', () => {
  it('resolves an undeclared bare name as undefined, so arithmetic on it is NaN', () => {
    expect(valueOf(prepare('nope'), { time: 0 } as never)).toBeUndefined();
    expect(evalExpr('(nope * 2)', { time: 0 })).toBeNaN();
  });

  it('resolves a dotted id whose owner is undeclared as undefined', () => {
    expect(valueOf(prepare('x_axis.motor'), { time: 0 } as never)).toBeUndefined();
  });

  it('resolves a dotted id whose owner is a falsy primitive as undefined', () => {
    expect(valueOf(prepare('x_axis.motor'),
                   { time: 0, drivers: { x_axis: null } } as never)).toBeUndefined();
  });

  it('throws the native TypeError jokenizer throws when the owner is a truthy primitive', () => {
    const expression = 'x_axis.motor';

    let expected: unknown;
    try {
      jokEvaluate(jokTokenize(expression), { x_axis: 5, $t: 0 });
    } catch (error) {
      expected = error;
    }
    expect(expected).toBeInstanceOf(TypeError);

    expect(() => valueOf(prepare(expression),
                          { time: 0, drivers: { x_axis: 5 } } as never))
      .toThrow((expected as TypeError).message);
  });

  it('resolves a dotted id whose owner object lacks the key as undefined', () => {
    expect(valueOf(prepare('x_axis.motor'),
                   { time: 0, drivers: { x_axis: { other: 1 } } } as never)).toBeUndefined();
  });

  it('resolves a dotted id whose owner object holds the key', () => {
    expect(valueOf(prepare('x_axis.motor'),
                   { time: 0, drivers: { x_axis: { motor: 8000 } } } as never)).toBe(8000);
  });
});

describe('valueOf: counts (D6, D9)', () => {
  it('one pass resolves fewer than 100 nodes for the pasted expression', () => {
    const id = prepare(pastedExpression());
    resetExpressionMetrics();
    valueOf(id, { time: 0, drivers: { x_axis: { motor: freshMotor() } } } as never);
    expect(expressionMetrics().resolutions).toBeLessThan(100);
    expect(expressionMetrics().resolutions).toBeGreaterThan(0);
  });

  it('a second expression sharing every subtree resolves zero further nodes in the pass', () => {
    const expr = pastedExpression();
    const id = prepare(expr);
    const secondId = prepare(`(${expr} + 1)`);
    const scope = { time: 0, drivers: { x_axis: { motor: freshMotor() } } } as never;

    resetExpressionMetrics();
    valueOf(id, scope);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(secondId, scope);
    // Only the new outer "+ 1" node (and the constant 1) are new work.
    expect(expressionMetrics().resolutions).toBeLessThanOrEqual(first + 2);
  });

  it('a pass at a new $t resolves the distinct subexpressions again', () => {
    const id = prepare(pastedExpression());
    const motor = freshMotor();
    const scope1 = { time: 0.4111, drivers: { x_axis: { motor } } } as never;
    const scope2 = { time: 0.4222, drivers: { x_axis: { motor } } } as never;

    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBe(first * 2);
  });
});

describe('valueOf: pass detection over a nested driver map (D6)', () => {
  const expr = '(x_axis.motor + y_axis.motor)';

  it('does not resolve again for the SAME scope object (identity fast path)', () => {
    const id = prepare(expr);
    const scope = {
      time: 0, drivers: { x_axis: { motor: freshMotor() }, y_axis: { motor: 0 } },
    } as never;
    resetExpressionMetrics();
    valueOf(id, scope);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope);
    expect(expressionMetrics().resolutions).toBe(first);
  });

  it('does not resolve again for a NEW object carrying equal nested values', () => {
    // Exactly DriverStore.scope()'s shape (D6): a fresh nested map every
    // call, equal in value to the last one.
    const id = prepare(expr);
    const motor = freshMotor();
    const scope1 = { time: 0, drivers: { x_axis: { motor }, y_axis: { motor: 0 } } } as never;
    const scope2 = { time: 0, drivers: { x_axis: { motor }, y_axis: { motor: 0 } } } as never;
    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBe(first);
  });

  it('resolves again when a nested number changes', () => {
    const id = prepare(expr);
    const motor = freshMotor();
    const scope1 = { time: 0, drivers: { x_axis: { motor }, y_axis: { motor: 0 } } } as never;
    const scope2 = { time: 0, drivers: { x_axis: { motor: motor + 1 }, y_axis: { motor: 0 } } } as never;
    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBeGreaterThan(first);
  });

  it('treats 0 and -0 as different, by Object.is', () => {
    // A dedicated expression: 0 and freshMotor()'s huge sentinel would
    // never collide anyway, so this one genuinely needs the literal
    // zero pair, and no other test in this file uses it.
    const zeroId = prepare('(x_axis.zero_sentinel + y_axis.motor)');
    const motor = freshMotor();
    const scope1 = {
      time: 0, drivers: { x_axis: { zero_sentinel: 0 }, y_axis: { motor } },
    } as never;
    const scope2 = {
      time: 0, drivers: { x_axis: { zero_sentinel: -0 }, y_axis: { motor } },
    } as never;
    resetExpressionMetrics();
    valueOf(zeroId, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(zeroId, scope2);
    expect(expressionMetrics().resolutions).toBeGreaterThan(first);
  });

  it('treats NaN as equal to NaN, by Object.is', () => {
    const id = prepare(expr);
    const motor = freshMotor();
    const scope1 = { time: 0, drivers: { x_axis: { motor: NaN }, y_axis: { motor } } } as never;
    const scope2 = { time: 0, drivers: { x_axis: { motor: NaN }, y_axis: { motor } } } as never;
    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBe(first);
  });

  it('resolves again when a driver key is added or removed', () => {
    const id = prepare(expr);
    const motor = freshMotor();
    const scope1 = { time: 0, drivers: { x_axis: { motor } } } as never;
    const scope2 = { time: 0, drivers: { x_axis: { motor }, y_axis: { motor: 0 } } } as never;
    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBeGreaterThan(first);
  });

  it('resolves again when a nested owner key is added or removed', () => {
    const id = prepare(expr);
    const motor = freshMotor();
    const scope1 = { time: 0, drivers: { x_axis: { motor }, y_axis: {} } } as never;
    const scope2 = { time: 0, drivers: { x_axis: { motor }, y_axis: { motor: 0 } } } as never;
    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBeGreaterThan(first);
  });

  it('resolves again, rather than skipping, when a driver value is not a number or a plain object', () => {
    // `expr` never dereferences x_axis here -- this is a SCOPE-level
    // comparison, not a member-access evaluation.
    const id = prepare('y_axis.motor');
    const motor = freshMotor();
    const scope1 = { time: 0, drivers: { x_axis: { motor }, y_axis: { motor } } } as never;
    const scope2 = { time: 0, drivers: { x_axis: 'nope', y_axis: { motor } } } as never;
    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBeGreaterThan(first);
  });

  it('treats an absent drivers map the same as an empty one', () => {
    const id = prepare('(1 + 1)');
    const scope1 = { time: 0.9991, drivers: {} } as never;
    const scope2 = { time: 0.9991 } as never;
    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBe(first);
  });
});

describe('retainExpressions / releaseExpressions (D8)', () => {
  it('a release without a retain is harmless', () => {
    expect(() => releaseExpressions()).not.toThrow();
    expect(() => releaseExpressions()).not.toThrow();
  });

  it('the table survives a release while another holder remains', () => {
    retainExpressions(); // holder A
    retainExpressions(); // holder B
    const id = prepare('(5100001 + 1)');
    const before = expressionMetrics().nodes;

    releaseExpressions(); // A releases; B still holds it
    expect(expressionMetrics().nodes).toBe(before);
    expect(prepare('(5100001 + 1)')).toBe(id); // not rebuilt: same id

    releaseExpressions(); // B releases too, balancing this test
  });

  it('is emptied when the last release lands, and preparing afterwards works at a fresh id', () => {
    retainExpressions();
    prepare('(5200002 + 2)');
    expect(expressionMetrics().nodes).toBeGreaterThan(0);

    releaseExpressions(); // the only holder: the table empties

    expect(expressionMetrics().nodes).toBe(0);

    const rebuilt = prepare('(5200002 + 2)');
    expect(valueOf(rebuilt, { time: 0 } as never)).toBe(5200004);
  });

  it('drops and rebuilds the table when the node ceiling is passed', () => {
    const original = EXPRESSION_LIMITS.nodes;
    // '(5300001 + 1)' interns exactly 3 nodes: two constants, one binary.
    EXPRESSION_LIMITS.nodes = 3;
    try {
      const first = prepare('(5300001 + 1)');
      expect(expressionMetrics().nodes).toBe(3);
      expect(valueOf(first, { time: 0 } as never)).toBe(5300002);

      // The ceiling is checked at the start of the NEXT preparation
      // (D8): passing it drops the whole store before this one is built.
      const second = prepare('(5300002 + 2)');
      expect(expressionMetrics().nodes).toBe(3); // only the second expression's
      expect(valueOf(second, { time: 0 } as never)).toBe(5300004);
    } finally {
      EXPRESSION_LIMITS.nodes = original;
    }
  });
});
