/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Reading a version 8 document, and refusing one BY NAME (OpenSpec
// `execute-the-commit`, design §1, §2, §7, §8).
//
// The documents under test are the corpus's OWN -- the producer's, not
// hand-written -- so what is read here is what the framework publishes,
// and a doctored copy of one is what each refusal is proved on.

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { bindingTable } from '../bindings';
import type { Manifest } from '../types';
import { loadClocked } from './document';
import type { ClockedDocument } from './document';

interface CorpusMachine {
  name: string;
  document: Record<string, unknown>;
}

const fixture = JSON.parse(readFileSync(
  new URL('../clocked-corpus.json', import.meta.url), 'utf8')) as {
    machines: CorpusMachine[];
  };

function documentOf(name: string): Record<string, unknown> {
  const found = fixture.machines.find((one) => one.name === name);
  if (found === undefined) throw new Error(`no corpus machine ${name}`);
  return JSON.parse(JSON.stringify(found.document));
}

function load(document: Record<string, unknown>, url = 'machine.json') {
  const manifest = document as unknown as Manifest;
  return loadClocked(document as unknown as ClockedDocument, url,
                     bindingTable(manifest, url));
}

function refusal(document: Record<string, unknown>): string {
  try {
    load(document);
  } catch (error) {
    return (error as Error).message;
  }
  throw new Error('the document was not refused');
}

describe('a version 8 document is read field by field', () => {
  it('reads the machine\'s identity, clock and reserved own-name', () => {
    const machine = load(documentOf('Calculator'));
    expect(machine.identity).toBe(
      '6eb8e57724cde8a15bc10a2966d02e039ba6fa4aee8c3392bb02c951064eb4a7');
    expect(machine.clock).toBe(null);
    expect(machine.own).toBe('_own');
    expect(load(documentOf('Regulator')).clock).toBe('time');
  });

  it('DERIVES the bank\'s id order: drivers, then states, then the clock',
     () => {
       // ADR-128 §4 publishes no `coordinates` table, because every
       // number a clocked bank holds is already in the document.
       expect(load(documentOf('Calculator')).order).toEqual([
         'crank', 'feed', 'operand', 'ring', 'setting',
         'halved', 'w0.digit', 'w1.digit', 'w2.digit', 'w3.digit',
       ]);
       expect(load(documentOf('Regulator')).order)
         .toEqual(['engaged', 'count', 'time']);
     });

  it('banks every declaration at its default, and the clock at zero', () => {
    const machine = load(documentOf('Calculator'));
    expect(machine.initial).toEqual({
      crank: 0, feed: 0, operand: 1, ring: 0, setting: 0,
      halved: 0, 'w0.digit': 0, 'w1.digit': 0, 'w2.digit': 0, 'w3.digit': 0,
    });
    expect(load(documentOf('Regulator')).initial.time).toBe(0);
  });

  it('reads `states` as a SECOND driver table, five fields and all', () => {
    const machine = load(documentOf('Calculator'));
    expect(machine.states['w0.digit']).toEqual({
      default: 0, range: [0, 9], unit: null, dtype: 'int', scale: null,
    });
    expect(machine.drivers.operand).toEqual({
      default: 1, range: [0, 9], unit: null, dtype: 'int', scale: null,
    });
    // A STATE is never a handle: the split IS the handle rule.
    expect(Object.keys(machine.drivers))
      .not.toContain('w0.digit');
  });

  it('reads each commit: sources, targets, the event level and the law',
     () => {
       const machine = load(documentOf('Counter'));
       expect(machine.commits).toHaveLength(1);
       const [commit] = machine.commits;
       expect(commit.sources).toEqual(['crank', 'units', 'tens']);
       expect(commit.targets).toEqual(['units', 'tens']);
       expect(commit.primitive).toBe('floor');
       expect(commit.level).toBe('(crank / 360)');
       expect(commit.law).toHaveLength(2);
       expect(commit.description)
         .toBe('(crank, units, tens) commits (units, tens)');
       expect(commit.statedBy).toBe('Counter');
       // `shapes` names the ONE input that can move this level, and that
       // is what `moves_with` answers.
       expect([...commit.jumps.keys()]).toEqual(['crank']);
       expect(commit.jumps.get('crank')?.affine).toBe(true);
     });

  it('reads each bound, and forms the LEVEL itself by subtraction', () => {
    const machine = load(documentOf('Pawl'));
    expect(machine.bounds).toHaveLength(1);
    const [bound] = machine.bounds;
    expect(bound.coordinate).toBe('crank_dial.turn');
    expect(bound.side).toBe('low');
    expect(bound.unit).toBe('deg');
    expect(bound.chain).toBe('crank');
    expect(bound.bound).toBe('(6.0 * floor(_b6))');
    // The low side is `bound - value`; the published SKELETON is that
    // same level with the jump nodes replaced by placeholders.
    expect(bound.level).toBe('((6.0 * floor(_b6)) - crank)');
    expect(bound.plan?.skeleton).toBe('((6.0 * _j0) - crank)');
    expect(bound.node).toBe('Dial');
    expect(bound.joint).toBe('turn');
    // The level's own bank ids, closed over the bindings table.
    expect(bound.names).toEqual(['crank']);
    expect(bound.chainNames).toEqual(['crank']);
  });

  it('reads a bound stated as a plain NUMBER', () => {
    const machine = load(documentOf('Stroke'));
    const high = machine.bounds.find((one) => one.side === 'high');
    expect(high?.bound).toBe('9');
    expect(high?.level).toBe('(lift - 9)');
  });

  it('admits `constant` in a BOUND\'s shapes, where a commit\'s publishes '
     + 'only affine and kinked', () => {
       // `Calculator`'s freeze: the crank moves the level only THROUGH
       // its jumps, so the level itself is constant in it.
       const machine = load(documentOf('Calculator'));
       const freeze = machine.bounds.find(
         (one) => one.coordinate === 'knob.travel' && one.side === 'low');
       expect(freeze?.plans.get('crank')?.shape).toBe('constant');
       expect(freeze?.plans.get('setting')?.shape).toBe('affine');
       expect(freeze?.plans.get('crank')?.plan.jumps.map((one) => one.shape))
         .toEqual(['affine', 'affine']);
       expect(freeze?.plans.get('setting')?.plan.jumps.map(
         (one) => one.shape)).toEqual(['constant', 'constant']);
     });

  it('leaves a constraint no driver moves out of the clip entirely', () => {
    // `Decorative` and `Untouchable` publish a numeric `value` with
    // `shapes: {}`: constant along every path, examined only at the end
    // of a request.
    for (const name of ['Decorative', 'Untouchable']) {
      const machine = load(documentOf(name));
      for (const bound of machine.bounds) expect(bound.plans.size).toBe(0);
    }
  });

  it('loads every machine of the corpus', () => {
    for (const entry of fixture.machines) {
      expect(() => load(documentOf(entry.name)), entry.name).not.toThrow();
    }
  });

  it('never reaches a SAMPLED level: every published shape is constant, '
     + 'affine or kinked', () => {
       // The clocked limits carry no sampling resolution and no
       // bisection round count, because a clocked level is SOLVED. This
       // is the structural claim that makes that safe.
       for (const entry of fixture.machines) {
         const machine = load(documentOf(entry.name));
         expect(Number.isNaN(machine.limits.subdivisions), entry.name)
           .toBe(true);
         expect(Number.isNaN(machine.limits.bisectionRounds), entry.name)
           .toBe(true);
         for (const commit of machine.commits) {
           for (const jump of commit.jumps.values()) {
             expect(['affine', 'kinked'], entry.name).toContain(jump.shape);
           }
         }
         for (const bound of machine.bounds) {
           for (const plan of bound.plans.values()) {
             expect(['constant', 'affine', 'kinked'], entry.name)
               .toContain(plan.shape);
             for (const jump of plan.plan.jumps) {
               expect(['constant', 'affine', 'kinked'], entry.name)
                 .toContain(jump.shape);
             }
           }
         }
       }
     });

  it('reads the two limits the solve is defined by', () => {
    const machine = load(documentOf('Counter'));
    expect(machine.limits.crossingTolerance).toBe(1e-12);
    expect(machine.limits.maxCrossings).toBe(1000);
  });
});

describe('a clocked machine this viewer cannot execute is refused by name',
         () => {
           it('when the document carries no `clocked` object', () => {
             const document = documentOf('Counter');
             delete document.clocked;
             expect(refusal(document))
               .toContain('carries no `clocked` object');
           });

           it('when it carries BOTH a program and a clocked object', () => {
             const document = documentOf('Counter');
             document.program = {};
             expect(refusal(document)).toContain('which is two machines');
           });

           it('when the identity, clock or own-name is mistyped', () => {
             for (const [key, value, said] of [
               ['identity', 7, '`clocked.identity`'],
               ['clock', 7, '`clocked.clock`'],
               ['own', null, '`clocked.own`'],
             ] as [string, unknown, string][]) {
               const document = documentOf('Counter');
               (document.clocked as Record<string, unknown>)[key] = value;
               expect(refusal(document)).toContain(said);
             }
           });

           it('when an `at.primitive` is outside the kinds an event may be '
              + 'stated with', () => {
                const document = documentOf('Counter');
                const commits = (document.clocked as { commits: unknown[] })
                  .commits;
                ((commits[0] as { at: Record<string, unknown> }).at)
                  .primitive = '%';
                const said = refusal(document);
                expect(said).toContain('at.primitive is "%"');
                expect(said).toContain('floor, ceil, sign');
              });

           it('when a commit `shapes` value is neither affine nor kinked',
              () => {
                const document = documentOf('Counter');
                const commits = (document.clocked as { commits: unknown[] })
                  .commits;
                (commits[0] as { shapes: Record<string, unknown> })
                  .shapes.crank = 'constant';
                expect(refusal(document))
                  .toContain('shapes.crank is "constant"');
              });

           it('when `law` is not aligned with `targets`', () => {
             const document = documentOf('Counter');
             const commits = (document.clocked as { commits: unknown[] })
               .commits;
             (commits[0] as { law: string[] }).law = ['(units + 1)'];
             expect(refusal(document))
               .toContain('1 expressions for 2 targets');
           });

           it('when a commit target is not a declared state', () => {
             const document = documentOf('Counter');
             const commits = (document.clocked as { commits: unknown[] })
               .commits;
             (commits[0] as { targets: string[] }).targets = ['crank', 'tens'];
             expect(refusal(document))
               .toContain('which is not a declared state');
           });

           it('when a bound is missing a key, or its side is neither low '
              + 'nor high', () => {
                const document = documentOf('Pawl');
                const bounds = (document.clocked as { bounds: unknown[] })
                  .bounds;
                const kept = JSON.parse(JSON.stringify(bounds[0]));
                delete (bounds[0] as Record<string, unknown>).coordinate;
                expect(refusal(document)).toContain('.coordinate is');
                bounds[0] = kept;
                (bounds[0] as Record<string, unknown>).side = 'middle';
                expect(refusal(document)).toContain('.side is "middle"');
              });

           it('when a bound\'s plan is malformed', () => {
             const document = documentOf('Pawl');
             const bounds = (document.clocked as { bounds: unknown[] }).bounds;
             const plan = (bounds[0] as { plan: { jumps: unknown[] } }).plan;
             (plan.jumps[0] as Record<string, unknown>).primitive = 'wobble';
             expect(refusal(document))
               .toContain('plan.jumps[0].primitive is "wobble"');
           });

           it('when a bound\'s per-input shape is outside the three', () => {
             const document = documentOf('Pawl');
             const bounds = (document.clocked as { bounds: unknown[] }).bounds;
             const shapes = (bounds[0] as { shapes: Record<string, unknown> })
               .shapes;
             (shapes.crank as Record<string, unknown>).level = 'curved';
             expect(refusal(document))
               .toContain('shapes.crank.level is "curved"');
           });

           it('when a bound\'s per-input jump shapes are not one per jump',
              () => {
                const document = documentOf('Pawl');
                const bounds = (document.clocked as { bounds: unknown[] })
                  .bounds;
                const entry = bounds[0] as {
                  shapes: Record<string, unknown>;
                };
                const shapes = entry.shapes;
                (shapes.crank as Record<string, unknown>).jumps = [];
                expect(refusal(document))
                  .toContain('not one shape for each of the plan\'s 1 jumps');
              });

           it('when a `states` entry is not a declaration', () => {
             const document = documentOf('Counter');
             (document.states as Record<string, unknown>).tens = 3;
             expect(refusal(document)).toContain('`states.tens` is 3');
           });

           it('when a state declares a dtype this viewer does not read',
              () => {
                const document = documentOf('Counter');
                ((document.states as Record<string, Record<string, unknown>>)
                  .tens).dtype = 'decimal';
                expect(refusal(document))
                  .toContain('`states.tens.dtype` is "decimal"');
              });

           it('when an id is declared both as a driver and as a state', () => {
             const document = documentOf('Counter');
             (document.drivers as Record<string, unknown>).tens =
               (document.states as Record<string, unknown>).tens;
             expect(refusal(document))
               .toContain('is declared both as a driver and as a state');
           });

           it('when the clock collides with a declared id', () => {
             const document = documentOf('Counter');
             (document.clocked as Record<string, unknown>).clock = 'crank';
             expect(refusal(document))
               .toContain('which is also a declared driver or state');
           });

           it('when an expression names an identifier nothing declares',
              () => {
                const document = documentOf('Counter');
                const commits = (document.clocked as { commits: unknown[] })
                  .commits;
                ((commits[0] as { at: Record<string, unknown> }).at).level =
                  '(handle / 360)';
                expect(refusal(document))
                  .toContain('reads "handle", which this machine declares '
                             + 'nowhere');
              });

           it('when a limit is missing or not finite', () => {
             const document = documentOf('Counter');
             (document.clocked as { limits: Record<string, unknown> })
               .limits.max_crossings = null;
             expect(refusal(document))
               .toContain('`clocked.limits.max_crossings` is null');
           });
         });
