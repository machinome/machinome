/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The wire between the main thread and the run (design §2): one request
// type carries the cadence, everything else is a request with a
// correlated reply, and a bank travels positionally against the `order`
// the `ready` message fixed once.

import { describe, expect, it } from 'vitest';
import {
  bankOf, errorOf, movedIndices, namesOf, refusalOf,
} from './protocol';
import { RunConflict, TooManyCrossings, refusalKind } from './program';

const order = ['crank', 'units.drum.turn', 'tens.drum.turn'];

describe('the positional bank', () => {
  it('is the state in the order ready fixed', () => {
    const bank = bankOf(
      { 'tens.drum.turn': 3, crank: 1, 'units.drum.turn': 2 }, order);
    expect(bank).toBeInstanceOf(Float64Array);
    expect([...bank]).toEqual([1, 2, 3]);
  });

  it('reports what moved as INDICES into that order', () => {
    const before = bankOf({ crank: 1, 'units.drum.turn': 2,
                            'tens.drum.turn': 3 }, order);
    const after = bankOf({ crank: 1, 'units.drum.turn': 5,
                           'tens.drum.turn': 3 }, order);
    expect(movedIndices(before, after)).toEqual([1]);
    expect(namesOf(order, movedIndices(before, after)))
      .toEqual(['units.drum.turn']);
  });

  it('reports nothing when a coordinate reached the value it held', () => {
    const bank = bankOf({ crank: 1, 'units.drum.turn': 2,
                          'tens.drum.turn': 3 }, order);
    expect(movedIndices(bank, bank)).toEqual([]);
  });
});

describe('a refusal', () => {
  it('carries the framework\'s own message text and the kind', () => {
    const error = new RunConflict('two relations disagree on units.drum.turn');
    const reply = refusalOf(error, 7, 42, refusalKind(error));
    expect(reply).toEqual({
      t: 'refusal', id: 7, tick: 42, kind: 'conflict',
      message: 'two relations disagree on units.drum.turn',
    });
  });

  it('names the crossing limit as its own kind', () => {
    const error = new TooManyCrossings('over one tick ... 1001 surfaces');
    expect(refusalOf(error, 1, 2, refusalKind(error)).kind).toBe('crossings');
  });

  it('falls back to "unknown" for anything else', () => {
    expect(refusalOf(new Error('boom'), 1, 2, refusalKind(new Error('boom')))
      .kind).toBe('unknown');
  });
});

describe('an error', () => {
  it('carries the request id and the message, and nothing changed', () => {
    expect(errorOf(new Error("'crank' is already owned"), 9))
      .toEqual({ t: 'error', id: 9, message: "'crank' is already owned" });
  });
});
