/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The evaluation scope a qualified id is read through (design D10,
// ADR-046).
//
// A dotted id is member access to the parser: `units.drum.turn` arrives
// at the evaluator as the parts `['units', 'drum', 'turn']`, and the
// scope has to be nested as deep as the id is long for the chain to
// find a number at the end of it. The shipped builder nested ONE level
// -- it split at the first dot -- which is enough for a two-segment
// driver id and is exactly nothing for a three-segment one: the chain
// finds `{'drum.turn': 7}` under `units`, no `drum` in it, and resolves
// to `undefined`, which arithmetic turns into `NaN`.
//
// Every joint coordinate id a program publishes is three segments or
// more (`units.drum.turn`), so the run cannot pose a single part
// without this; and a three-segment DRIVER id in a version 2 to 4
// document has been silently broken the same way all along. One builder
// serves both, which is why it is here and not in the engine.

import type { DriverScope } from '../evaluator';

/** `{'units.drum.turn': 7}` as `{units: {drum: {turn: 7}}}`, nesting at
 * every segment of every id. A bare id stays a number at the top. */
export function nest(flat: Record<string, number>): DriverScope {
  const scope: DriverScope = {};
  for (const id in flat) {
    if (!Object.prototype.hasOwnProperty.call(flat, id)) continue;
    const parts = id.split('.');
    if (parts.length === 1) {
      scope[id] = flat[id];
      continue;
    }
    let owner = scope as Record<string, unknown>;
    for (let index = 0; index < parts.length - 1; index += 1) {
      const part = parts[index];
      const found = owner[part];
      if (typeof found === 'object' && found !== null) {
        owner = found as Record<string, unknown>;
      } else {
        const made: Record<string, unknown> = {};
        owner[part] = made;
        owner = made;
      }
    }
    owner[parts[parts.length - 1]] = flat[id];
  }
  return scope;
}

/** Refuse an id set that cannot be nested: one id that is a strict
 * PREFIX of another, segment for segment (`a.b` beside `a.b.c`), would
 * have to make one number an object.
 *
 * Nothing the framework publishes produces that shape today. The
 * refusal is what keeps it loud if it ever does, rather than letting
 * one of the two values disappear into the other. */
export function assertNestable(ids: Iterable<string>): void {
  const seen = new Set<string>();
  for (const id of ids) seen.add(id);
  for (const id of seen) {
    const parts = id.split('.');
    for (let cut = 1; cut < parts.length; cut += 1) {
      const prefix = parts.slice(0, cut).join('.');
      if (seen.has(prefix)) {
        throw new Error(
          `the identifiers "${prefix}" and "${id}" cannot both hold a ` +
          `value: "${prefix}" would have to be a number and an object at ` +
          'once, because an expression reads a qualified id as member ' +
          'access at every segment. Refusing rather than letting one of ' +
          'the two disappear into the other.',
        );
      }
    }
  }
}
