/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// A committed bank poses the geometry (design §5, ADR-046). Nothing new
// is evaluated: the widget evaluates in a version 5 document exactly
// what it evaluates in a version 4 one, from a WIDER scope -- the bank's
// coordinate ids beside the driver ids, and the program's clock name
// bound to elapsed simulation seconds.

import { describe, expect, it } from 'vitest';
import { poseScope, posed } from './pose';
import { EMPTY_BINDINGS } from '../bindings';
import { evalExpr } from '../evaluator';
import { WidgetTree } from '../tree';
import type { ManifestNode } from '../types';

const bank = {
  units_entry: 1,
  'units.drum.turn': 36,
  'tens.drum.turn': 0,
};

describe('the scope a committed bank makes', () => {
  it('binds the bank nested at every segment, and the clock beside it', () => {
    const scope = poseScope(bank, 'time', 2.5, EMPTY_BINDINGS);
    expect(scope.time).toBe(0);
    expect(scope.drivers).toEqual({
      units_entry: 1,
      units: { drum: { turn: 36 } },
      tens: { drum: { turn: 0 } },
      time: 2.5,
    });
    expect(scope.bindings).toBeUndefined();
  });

  it('resolves a three-segment coordinate id to its committed value', () => {
    const scope = poseScope(bank, 'time', 0, EMPTY_BINDINGS);
    expect(evalExpr('(-1 * units.drum.turn)', scope)).toBe(-36);
    expect(evalExpr('time', scope)).toBe(0);
  });

  it('binds the clock to zero with no run, which is where the rest pose is',
     () => {
       expect(poseScope(bank, 'time', 0, EMPTY_BINDINGS).drivers)
         .toMatchObject({ time: 0 });
     });

  it('leaves $t at zero, because no expression of a version 5 document '
     + 'reads it', () => {
    expect(poseScope(bank, 'time', 99, EMPTY_BINDINGS).time).toBe(0);
  });
});

describe('what a frame says moved', () => {
  const node = (name: string, expression: string): ManifestNode => ({
    name, type: 'AssemblyNode', color: null,
    operations: [['r', expression, [0, 0, 1]]],
  });

  const root: ManifestNode = {
    name: 'root', type: 'AssemblyNode', color: null, operations: [],
    children: [node('units', 'units.drum.turn'), node('tens', 'tens.drum.turn')],
  };

  it('re-evaluates only the parts that read a coordinate that moved', () => {
    const tree = new WidgetTree(root, '/', null, EMPTY_BINDINGS);
    tree.update(poseScope(bank, 'time', 0, EMPTY_BINDINGS));
    const idle = tree.group.children[1].matrix.clone();
    const moving = tree.group.children[0].matrix.clone();

    const next = { ...bank, 'units.drum.turn': 72 };
    tree.update(poseScope(next, 'time', 0.1, EMPTY_BINDINGS),
                posed(['units.drum.turn']));

    expect(tree.group.children[0].matrix.equals(moving)).toBe(false);
    expect(tree.group.children[1].matrix.equals(idle)).toBe(true);
    tree.dispose();
  });

  it('is a driver change set that never claims time moved', () => {
    expect(posed(['units.drum.turn']))
      .toEqual({ time: false, drivers: new Set(['units.drum.turn']) });
    expect(posed([])).toEqual({ time: false, drivers: new Set() });
  });
});
