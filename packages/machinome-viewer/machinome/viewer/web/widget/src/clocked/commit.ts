/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// What a committing relation WRITES at one event
// (`simulation/clocked.py`'s `Committing.commit` and
// `simulation/state.py`'s `State.committed`; OpenSpec
// `execute-the-commit`, design §7).
//
// One published expression per target, evaluated over the PRE-EVENT
// bank with the input at its landing, through the same interned DAG the
// pose uses. Nothing is integrated and nothing is scaled: a commit is
// evaluated at ONE POINT, so `floor` means `floor` and `%` means `%`.

import { evaluateExpression } from '../run/program';
import { ClockedConflict } from './document';
import type { LoadedCommit, LoadedMachine } from './document';

/** Python's `round`: HALF TO EVEN, and an integer result, which has no
 * signed zero.
 *
 * `Math.round` takes a half toward +infinity and is wrong here --
 * `Math.round(0.5)` is 1 where this is 0, `Math.round(-0.5)` is -0 where
 * this is 0, `Math.round(2.5)` is 3 where this is 2. A state declaring
 * `dtype: "int"` counts whole native units and takes the nearest one,
 * rounded ONCE; a repeated rounding drifts and a single one does not. */
export function halfToEven(value: number): number {
  if (!Number.isFinite(value)) return value;
  const low = Math.floor(value);
  const rest = value - low;
  let found: number;
  if (rest > 0.5) found = low + 1;
  else if (rest < 0.5) found = low;
  // Exactly halfway: the EVEN neighbour.
  else found = low % 2 === 0 ? low : low + 1;
  // Python's `round` returns an INT, and an int has no negative zero:
  // `round(-0.5)` is `0`, not `-0`. Normalising here is what keeps a
  // banked value comparable to the corpus's `Object.is` semantics.
  return found === 0 ? 0 : found;
}

/** A commit that computed an infinity or a NaN
 * (`clocked.py`'s `_not_a_value`, the framework's follow-up of
 * 2026-09-17).
 *
 * Judged BEFORE the integer rounding, so an integer state refuses by
 * the same message rather than by a rounding overflow that names
 * neither the relation nor the state. The REQUEST is refused whole and
 * commits nothing: a bank holding a non-finite value poses nothing,
 * satisfies no bound and carries no later event. ADR-128 §16 states it
 * for the consumer too -- a document cannot express a raise. */
function notAValue(commit: LoadedCommit, identifier: string,
                   value: number): ClockedConflict {
  return new ClockedConflict(
    `${commit.description}: the law computed ${value} for the state ` +
    `'${identifier}', which is not a value a machine can stand at -- a ` +
    'bank holding it poses nothing, satisfies no bound and carries no ' +
    'later event. The request committed nothing: the bank and the tree ' +
    'stand as they were.');
}

/** This relation's targets and the values it writes at one event, read
 * from the PRE-EVENT bank with the input at its landing.
 *
 * A law returning a plain number publishes that number, and it is a real
 * answer -- the asymmetry with a running law edge, whose `null` means
 * "contributes no increment". A law whose TOP node is a comparison still
 * banks a number, so the result is coerced once. */
export function committed(machine: LoadedMachine, commit: LoadedCommit,
                          bank: Record<string, number>, inputId: string,
                          landing: number): Record<string, number> {
  const values = { ...bank };
  values[inputId] = landing;
  const written: Record<string, number> = {};
  commit.targets.forEach((identifier, index) => {
    const raw = Number(
      evaluateExpression(machine, commit.law[index], values));
    if (!Number.isFinite(raw)) throw notAValue(commit, identifier, raw);
    const declaration = machine.states[identifier];
    // NO `scale` is applied at a commit and none is published for one: a
    // commit law READS native values and RETURNS native values, so
    // dividing by `scale` here would lose a factor of it at every event
    // (`State.committed`'s own note).
    written[identifier] = declaration !== undefined
      && declaration.dtype === 'int' ? halfToEven(raw) : raw;
  });
  return written;
}
