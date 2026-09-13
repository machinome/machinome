/*
 * solid-node-viewer - the browser viewer for solid-node models
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
