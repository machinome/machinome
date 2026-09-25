/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The document's binding table (OpenSpec `read-expression-bindings`,
// design D1-D7; ADR-044). machinome's `expression-bindings` (ADR-080)
// stopped writing the same subexpression out over and over: a version-4
// document publishes each subexpression that occurs more than once as
// one named entry in an ordered top-level `bindings` array, referenced
// by bare name everywhere it occurred. This module is the document-level
// object that owns:
//
//   - VALIDATION (D7): a table this viewer cannot resolve is refused
//     HERE, at construction, naming the entry or the name and quoting
//     the source URL -- before `assertRenderable` (viewer.ts) walks the
//     document's operations and `params` expressions through it. What is
//     NOT validated here is a name an entry references that is neither
//     $t, another entry, nor a declared driver id: that is the existing
//     undeclared-driver refusal, and it is made by the caller (D7's own
//     split), which has the document's operations and `params`
//     expressions to report it against too.
//
//   - ROOTS (D1, D4): each entry's expression is `prepare`d into the
//     shared DAG exactly as an operation's is, giving `EvalScope.bindings`
//     a name -> node id map. The map is document-scoped even though the
//     DAG store is page-scoped (D2): the object built here is the one
//     that travels in the scope, never a module-level table. `roots()`
//     re-prepares if the store was reset since the last call (D4),
//     comparing `expressionGeneration()`.
//
//   - THE CLOSURE (D5): which INPUTS an expression reads, as distinct
//     from which NAMES it mentions (`freeVariables`, page-scoped and
//     binding-unaware on purpose). Computed once at construction, in
//     table order -- forward-only makes one pass enough -- from each
//     entry's own free names, keyed by name and holding no node id, so
//     it survives a store reset untouched.

import { expressionGeneration, NodeId, prepare, withExpressions } from './expressions';
import { freeVariables } from './evaluator';
import { Manifest, ManifestBinding } from './types';

export interface BindingTable {
  /** name -> the interned root of that binding's expression, for the
   * scope. `undefined` for a document with no table -- structurally
   * distinct from an empty one, though the two compare equal wherever
   * a binding map is compared (D3). Acquire and consume this raw map
   * inside the SAME withExpressions operation as any other roots used
   * with it. Retained pose scopes reacquire it through a getter. */
  roots(): ReadonlyMap<string, NodeId> | undefined;
  /** `names` with every binding name replaced by what it transitively
   * reads. A name that is not an entry -- $t, a driver id, or a
   * dangling reference -- is left in the set unchanged. */
  closure(names: ReadonlySet<string>): ReadonlySet<string>;
}

export const EMPTY_BINDINGS: BindingTable = {
  roots: () => undefined,
  closure: (names) => names,
};

function truncate(expression: string): string {
  return expression.length > 80 ? `${expression.slice(0, 80)}…` : expression;
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/** Build and validate `document`'s binding table, or `EMPTY_BINDINGS` if
 * it carries none. Throws, naming the entry or the name and quoting
 * `sourceUrl`, for any table this viewer cannot resolve (D7) -- except
 * the dangling-reference case, which is the caller's to make (see the
 * module comment). */
export function bindingTable(document: Manifest, sourceUrl: string): BindingTable {
  const raw = document.bindings;
  if (raw === undefined) {
    return EMPTY_BINDINGS;
  }
  if (!Array.isArray(raw)) {
    throw new Error(
      `${sourceUrl} declares a "bindings" value that is not an array. The ` +
      'document is malformed: refusing it rather than rendering part of ' +
      'a machine it does not understand.',
    );
  }

  const entries: ManifestBinding[] = raw.map((entry, index) => {
    if (!isPlainObject(entry)
        || typeof entry.name !== 'string'
        || typeof entry.expression !== 'string') {
      throw new Error(
        `${sourceUrl}'s bindings entry ${index} is not a {name, expression} ` +
        'object. The document is malformed: refusing it rather than ' +
        'rendering part of a machine it does not understand.',
      );
    }
    return { name: entry.name, expression: entry.expression };
  });

  // Every entry's name and its position, known up front (D7): what
  // distinguishes "names a later entry" from "names nothing this table
  // knows about" is whether the name is anywhere in this map at all.
  const indexOf = new Map<string, number>();
  entries.forEach((entry, index) => {
    if (indexOf.has(entry.name)) {
      throw new Error(
        `${sourceUrl} declares the binding "${entry.name}" more than once. ` +
        'Two entries under one name: which one an expression meant is ' +
        'unknowable, so the document is refused.',
      );
    }
    indexOf.set(entry.name, index);
  });

  const declaredDrivers = new Set(Object.keys(document.drivers ?? {}));
  entries.forEach((entry) => {
    if (declaredDrivers.has(entry.name)) {
      throw new Error(
        `${sourceUrl}'s binding "${entry.name}" is also a declared driver ` +
        'id. One of the two is unreachable: refusing the document rather ' +
        'than guessing which the producer meant.',
      );
    }
  });

  // The transitive closure (D5), computed forward-only in table order:
  // by the time entry K is reached, every entry it may legally name
  // (index < K) already has its own inputs computed. Also validates the
  // forward-only guarantee itself, and reaches `prepare`'s own D10
  // refusal for an expression this evaluation cannot support.
  const inputsOf = new Map<string, ReadonlySet<string>>();
  entries.forEach((entry, index) => {
    const names = freeVariables(entry.expression);
    const inputs = new Set<string>();
    for (const name of names) {
      const at = indexOf.get(name);
      if (at === undefined) {
        // $t, a declared driver id, or a name this table knows nothing
        // of -- not distinguished here; see the module comment.
        inputs.add(name);
        continue;
      }
      if (at >= index) {
        throw new Error(
          at === index
            ? `${sourceUrl}'s binding "${entry.name}" names itself ` +
              `(${truncate(entry.expression)}). An entry's expression may ` +
              'only name entries earlier in the table: refusing the ' +
              'document rather than recursing forever.'
            : `${sourceUrl}'s binding "${entry.name}" names "${name}", ` +
              'which appears later in the table. An entry\'s expression ' +
              'may only name entries earlier in the table: refusing the ' +
              'document rather than recursing forever.',
        );
      }
      for (const transitive of inputsOf.get(name)!) inputs.add(transitive);
    }
    inputsOf.set(entry.name, inputs);
  });

  // Prepared here and remembered (D1): an entry's expression is
  // `prepare`d exactly as an operation's is, giving the root node id
  // `EvalScope.bindings` names it by. The guard against a store reset
  // (D4): this table holds ids OUTSIDE the shared store, so a reset
  // between one call and the next -- the node ceiling tripping during a
  // long `machinome develop` session, or the last mount releasing -- would
  // leave `cachedRoots` naming reallocated nodes. `expressionGeneration()`
  // is one integer comparison per call and a real re-prepare only after
  // a genuine reset; the entries' expression STRINGS cost nothing to
  // keep, since they are the document's own.
  let cachedGeneration = -1;
  let cachedRoots: Map<string, NodeId> | undefined;

  const roots = (): ReadonlyMap<string, NodeId> => withExpressions(() => {
    if (cachedRoots === undefined || cachedGeneration !== expressionGeneration()) {
      const map = new Map<string, NodeId>();
      entries.forEach((entry) => map.set(entry.name, prepare(entry.expression)));
      cachedRoots = map;
      cachedGeneration = expressionGeneration();
    }
    return cachedRoots;
  });

  const closure = (names: ReadonlySet<string>): ReadonlySet<string> => {
    const result = new Set<string>();
    for (const name of names) {
      const inputs = inputsOf.get(name);
      if (inputs === undefined) {
        result.add(name);
      } else {
        for (const input of inputs) result.add(input);
      }
    }
    return result;
  };

  return { roots, closure };
}
