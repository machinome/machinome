/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Posing from a committed bank (design §5, ADR-046).
//
// There is NO second pose path and no second table of poses. The
// framework's "a committed bank poses the geometry" makes a joint's
// placement its coordinate's id and a flexible leaf's `params` an
// expression over bank ids, so the widget evaluates in a version 5
// document exactly what it evaluates in a version 4 one -- from a wider
// scope. `flexible.ts` needs no change at all.

import type { BindingTable } from '../bindings';
import type { EvalScope } from '../evaluator';
import type { ChangeSet } from '../tree';
import { nest } from './scope';

/** The evaluation scope one committed bank makes.
 *
 * `time` (`$t`) stays 0: no expression of a version 5 document reads it.
 * The program's own CLOCK NAME is a bank-shaped name instead -- under a
 * run it binds to elapsed simulation seconds, which never wrap, and with
 * no run it binds to zero, the instant the rest pose is defined at. */
export function poseScope(bank: Record<string, number>, clock: string,
                          elapsedSeconds: number,
                          bindings: BindingTable): EvalScope {
  return {
    time: 0,
    drivers: nest({ ...bank, [clock]: elapsedSeconds }),
    bindings: bindings.roots(),
  };
}

/** The evaluation scope one CLOCKED bank makes (OpenSpec
 * `execute-the-commit`, design §10).
 *
 * `poseScope`'s, with ONE difference: `time` is the playback's `$t`
 * rather than the fixed `0` a running document poses at. A version 8
 * document publishes the ordinary `animation` object, so a geometry that
 * is a formula of `$t` animates while the bank STANDS -- which is
 * exactly the preview ADR-128 §10 gives a clocked model. The clock, when
 * the root declares an elapsed base, is a BANK ID like any other and
 * needs no injection: it is in `bank` already.
 */
export function clockedScope(bank: Record<string, number>, time: number,
                             bindings: BindingTable): EvalScope {
  return {
    time,
    drivers: nest(bank),
    bindings: bindings.roots(),
  };
}

/** What a frame's `moved` ids mean to the tree's bounded re-evaluation.
 *
 * `ChangeSet.drivers` already means "the qualified ids whose values
 * moved this frame", and a coordinate id is a qualified id -- so a
 * machine whose carry is idle re-evaluates only the nodes the moving
 * drum reaches. `time` is never claimed: rendering does not advance
 * `$t` under a run. */
export function posed(moved: readonly string[]): ChangeSet {
  return { time: false, drivers: new Set(moved) };
}
