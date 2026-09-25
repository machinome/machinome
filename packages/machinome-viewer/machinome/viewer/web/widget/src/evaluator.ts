/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// Evaluates the raw operation expressions from the manifest (OpenSCAD
// expressions of `$t` and of qualified driver ids, e.g. "(360 * $t)" or
// "(x_axis.motor * 0.1125)") to numbers.
//
// A qualified driver id is a DOTTED name, and the parser reads it as
// member access -- so the scope carries driver values as a NESTED map
// (`{x_axis: {motor: 8000}}`) and the grammar needs no extension at all
// (ADR-056 stage 3b, D1; spike/expressions/FINDINGS.md sub-question 3).
// A driver declared on the root keeps its bare name and sits at the top
// level of that map.
//
// Beside evaluation this module answers WHICH inputs an expression
// depends on. Free variables come from the parsed tree, so a `Call`'s
// callee is never a variable and a `Member` chain is one dotted name
// rather than its pieces.
//
// share-expression-subtrees (ADR-043) moved the actual parsing,
// interning, evaluation and free-variable derivation into
// `expressions.ts`'s shared hash-consed DAG (D12): a repeated
// subexpression -- pasted many times into one expression, or repeated
// across many of a document's expressions -- costs one resolution per
// evaluation pass, not one per occurrence. This module keeps its public
// names (`evalExpr`, `freeVariables`, `TIME_ID`, `EvalScope`,
// `DriverScope`) as thin delegations over that table, so every other
// module's imports are unchanged.

import { freeNames, prepare, valueOf, withExpressions } from './expressions';
import type { DriverScope, EvalScope } from './expressions';

export type { DriverScope, EvalScope };
export { TIME_ID } from './expressions';

export function evalExpr(expression: string, scope: EvalScope): number {
  return withExpressions(() => {
    const value = valueOf(prepare(expression), scope);
    return typeof value === 'number' ? value : Number(value);
  });
}

/** Every input `expression` reads: `$t` and qualified driver ids.
 *
 * Read off the shared DAG (prepared once, shared across every operation
 * and expression that carries the same text): an operation is
 * time-driven iff `$t` is in this set, driver-driven iff any declared
 * driver id is, static iff the set is empty, and mixed when both.
 */
export function freeVariables(expression: string): ReadonlySet<string> {
  return withExpressions(() => freeNames(prepare(expression)));
}
