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
  EXPRESSION_LIMITS, expressionGeneration, expressionMetrics, prepare,
  releaseExpressions, resetExpressionMetrics, retainExpressions, valueOf,
} from './expressions';
import { bindingTable } from './bindings';
import { Manifest } from './types';
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

  it('resolves sign by the producer\'s formula, including at negative zero', () => {
    // `solid_node.math.sign` is `(x > 0) - (x < 0)`, which is 0 at
    // -0.0; `Math.sign(-0)` is -0. No parity case pinned it, and the
    // run reads a `sign` branch off the same formula (design §8, §15
    // finding 3), so the two runtimes have to agree here.
    expect(valueOf(prepare('sign(-0.0)'), { time: 0 } as never)).toBe(0);
    expect(Object.is(evalExpr('sign(-0.0)', { time: 0 }), 0)).toBe(true);
    expect(evalExpr('sign(-3)', { time: 0 })).toBe(-1);
    expect(evalExpr('sign(0)', { time: 0 })).toBe(0);
    expect(evalExpr('sign(3)', { time: 0 })).toBe(1);
    // And through a driver, where the negative zero is a VALUE rather
    // than a literal the parser folds.
    expect(Object.is(
      evalExpr('sign(x)', { time: 0, drivers: { x: -0 } }), 0)).toBe(true);
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

// OpenSpec `read-expression-bindings`, increment 2 (design D1, D3, D4).
// A binding name is an ordinary name that resolves into the shared DAG:
// `scope.bindings` maps a name to the root of that entry's expression,
// and name resolution consults it between `$t` and the driver map.
describe('valueOf: binding resolution (D1)', () => {
  it('resolves a binding name to the value of the expression it names', () => {
    const bindingRoot = prepare('($t * 43200.0)');
    const scope = {
      time: 0.25, bindings: new Map([['_b0', bindingRoot]]),
    } as never;

    expect(valueOf(prepare('(_b0 / 2.0)'), scope))
      .toBe(valueOf(prepare('(($t * 43200.0) / 2.0)'), scope));
  });

  it('resolves a name that is both a binding and a driver as the binding', () => {
    // The loader refuses such a document (3.1); this is the resolution
    // ORDER underneath that refusal, and it must favour the binding even
    // though nothing here enforces the refusal itself.
    const bindingRoot = prepare('(9500001 + 1)');
    const scope = {
      time: 0, drivers: { shadowed: -1 },
      bindings: new Map([['shadowed', bindingRoot]]),
    } as never;

    expect(valueOf(prepare('shadowed'), scope)).toBe(9500002);
  });

  it('$t still wins over everything, including a binding named $t', () => {
    const scope = { time: 7, bindings: new Map() } as never;
    expect(valueOf(prepare('$t'), scope)).toBe(7);
  });

  it('a name in neither is still undefined, and still NaN through evalExpr', () => {
    const scope = { time: 0, bindings: new Map() } as never;
    expect(valueOf(prepare('nope'), scope)).toBeUndefined();
    expect(evalExpr('(nope * 2)', scope)).toBeNaN();
  });

  it('resolves a chain of bindings, one naming the next', () => {
    // Exactly the DAG shape a table naming an entry produces (D1): the
    // root of "_b1" IS the name node for "_b0", not a copy of it.
    const b0 = prepare('($t * 2.0)');
    const b1 = prepare('_b0');
    const b2 = prepare('_b1');
    const scope = {
      time: 0.5,
      bindings: new Map([['_b0', b0], ['_b1', b1], ['_b2', b2]]),
    } as never;

    expect(valueOf(prepare('_b2'), scope)).toBe(1.0);
  });
});

describe('valueOf: work performed through a binding (D1, D6, D9)', () => {
  it('one pass over two expressions naming the same entry resolves its chain once', () => {
    const chain = pastedExpression();
    const bindingRoot = prepare(chain);
    const scope = {
      time: 0, bindings: new Map([['_b0', bindingRoot]]),
      drivers: { x_axis: { motor: freshMotor() } },
    } as never;

    resetExpressionMetrics();
    valueOf(prepare('_b0'), scope);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);

    valueOf(prepare('(_b0 + 1.0)'), scope);
    // Only the new outer "+ 1" node (and the constant) are new work; the
    // chain behind "_b0" is not walked again.
    expect(expressionMetrics().resolutions).toBeLessThanOrEqual(first + 2);
  });

  it('a pass at a new $t resolves the chain behind the binding again', () => {
    const bindingRoot = prepare('($t * 3.0)');
    const scope1 = { time: 0.111, bindings: new Map([['_b0', bindingRoot]]) } as never;
    const scope2 = { time: 0.222, bindings: new Map([['_b0', bindingRoot]]) } as never;

    resetExpressionMetrics();
    valueOf(prepare('_b0'), scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(prepare('_b0'), scope2);
    expect(expressionMetrics().resolutions).toBe(first * 2);
  });

  it('an entry no expression names is never resolved', () => {
    const readEntry = prepare('(9600001 + 1)');
    const unreadEntry = prepare('(9600002 + 2)');
    const scope = {
      time: 0, bindings: new Map([['_read', readEntry], ['_unread', unreadEntry]]),
    } as never;

    resetExpressionMetrics();
    valueOf(prepare('_read'), scope);
    const afterRead = expressionMetrics().resolutions;
    expect(afterRead).toBeGreaterThan(0);

    // Within the SAME pass (same scope object), resolving "_unread" now
    // costs its own work -- proof it was not already touched as a side
    // effect of resolving "_read".
    valueOf(prepare('_unread'), scope);
    expect(expressionMetrics().resolutions).toBeGreaterThan(afterRead);
  });
});

// D3: the correctness hazard the shared DAG introduces. The name node
// for "_b3" is ONE node id for the whole page, so the pass comparison
// must include the binding map -- otherwise two documents at equal time
// and drivers would share one memoized value for two different tables.
describe('valueOf: the binding map is part of the pass (D3)', () => {
  it('two maps binding one name to different roots give each its own value', () => {
    const name = '_shared_pass_name_d3';
    const aRoot = prepare('(9700001 + 1)');
    const bRoot = prepare('(9700002 + 2)');
    const time = 0.5;
    const scopeA = { time, bindings: new Map([[name, aRoot]]) } as never;
    const scopeB = { time, bindings: new Map([[name, bRoot]]) } as never;

    const nameNode = prepare(name);
    expect(valueOf(nameNode, scopeA)).toBe(9700002);
    expect(valueOf(nameNode, scopeB)).toBe(9700004);
  });

  it('two distinct map objects with equal contents share one pass', () => {
    const name = '_equal_maps_d3';
    const root = prepare('(9800001 + 1)');
    const time = 0.75;
    const scope1 = { time, bindings: new Map([[name, root]]) } as never;
    const scope2 = { time, bindings: new Map([[name, root]]) } as never;
    const nameNode = prepare(name);

    resetExpressionMetrics();
    valueOf(nameNode, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(nameNode, scope2);
    expect(expressionMetrics().resolutions).toBe(first);
  });

  it('an absent bindings map and an empty one are the same pass', () => {
    const id = prepare('(1 + 1)');
    const time = 0.8181;
    const scope1 = { time, bindings: new Map() } as never;
    const scope2 = { time } as never;

    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBe(first);
  });

  it('a version 1-3 scope with no bindings compares exactly as it does today', () => {
    // Every existing pass-detection case (above) constructs a scope with
    // no `bindings` key at all and stays green unedited by this
    // increment -- this is the same claim, named for the D3 change.
    const id = prepare('(x_axis.motor + 1)');
    const motor = freshMotor();
    const scope1 = { time: 0, drivers: { x_axis: { motor } } } as never;
    const scope2 = { time: 0, drivers: { x_axis: { motor } } } as never;

    resetExpressionMetrics();
    valueOf(id, scope1);
    const first = expressionMetrics().resolutions;
    expect(first).toBeGreaterThan(0);
    valueOf(id, scope2);
    expect(expressionMetrics().resolutions).toBe(first);
  });
});

// D4: a `BindingTable` holds node ids OUTSIDE the shared store. A store
// reset (the node ceiling, or the last mount releasing) hands ids out
// again from zero, so a table built before such a reset must re-prepare
// its roots rather than naming a reallocated node.
describe('expressionGeneration and the reset guard (D4)', () => {
  it('rises on a reset and not otherwise', () => {
    const before = expressionGeneration();
    prepare('(9900001 + 1)'); // an ordinary preparation: no reset
    expect(expressionGeneration()).toBe(before);

    retainExpressions();
    prepare('(9900002 + 2)');
    releaseExpressions(); // the only holder releasing: the store resets

    expect(expressionGeneration()).toBe(before + 1);
  });

  it('a held BindingTable re-prepares its roots after a reset, and evaluates correctly', () => {
    const original = EXPRESSION_LIMITS.nodes;
    const manifest: Manifest = {
      format: 'solid-node-export', version: 4, animation: { fps: 30, frames: 360 },
      bindings: [{ name: '_b0', expression: '(9900101 + 1)' }],
      root: { name: 'root', type: 'AssemblyNode', color: null, operations: [] },
    };

    const table = bindingTable(manifest, '/m.json');
    const beforeReset = table.roots()!.get('_b0')!;
    expect(valueOf(beforeReset, { time: 0 } as never)).toBe(9900102);

    // '(9900101 + 1)' interns exactly 3 nodes: two constants, one
    // binary. Lower the ceiling to force a reset on the NEXT
    // preparation, between building the table above and reading it
    // again below.
    EXPRESSION_LIMITS.nodes = 3;
    try {
      prepare('(9900201 + 1)'); // trips the ceiling; resetStore() runs

      // The exact hazard D4 exists to prevent: the id from before the
      // reset now names whatever the store handed that id out to next,
      // which is no longer "_b0"'s expression.
      expect(expressionGeneration()).toBeGreaterThan(0);
      expect(valueOf(beforeReset, { time: 0 } as never)).not.toBe(9900102);

      // `roots()` notices the generation moved and re-prepares: the
      // value is still the right one.
      const afterReset = table.roots()!.get('_b0')!;
      expect(valueOf(afterReset, { time: 0 } as never)).toBe(9900102);
    } finally {
      EXPRESSION_LIMITS.nodes = original;
    }
  });
});
