/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import { describe, expect, it, vi } from 'vitest';
import corpus from '../running-corpus.json';
import { loadProgram, StopInvariantError } from './program';
import type { RunDocument } from './program';
import { Run } from './run';

// The unmodified producer document is the central regression. Variants below
// change only the named relationship to exercise the surrounding admission rules.
function machine(mode = 'lower', turns = 0): Run {
  const doc: any = structuredClone(corpus.machines.find(x => x.name === 'PeriodicStop')!.document);
  const p = doc.program;
  p.coordinates.crank.initial += 360 * turns;
  p.coordinates['drum.turn'].initial -= 360 * turns;
  p.coordinates['bell.turn'].initial -= 360 * turns;
  if (mode === 'upper') {
    doc.bindings[0].expression = 'crank';
    p.coordinates['drum.turn'].initial *= -1;
    p.coordinates['bell.turn'].initial *= -1;
    p.spans['bell.turn'] = { low: null, high: {
      expression: '(360 * floor((drum.turn - 10.8) / 360)) + 125.22',
    } };
  } else if (mode === 'fixed') {
    p.spans['bell.turn'].low = -125.22;
  } else if (mode === 'relieving') {
    p.spans['bell.turn'].low.expression += ' - motor';
  } else if (mode === 'disengaged') {
    doc.bindings[0].expression = '-crank - motor * 0';
    for (const edge of p.edges.slice(0, 2)) edge.needs.push('motor');
    p.sources['drum.turn'].push('motor');
    p.sources['bell.turn'].push('motor');
  } else if (mode === 'simultaneous') {
    p.spans['free.turn'] = structuredClone(p.spans['bell.turn']);
    p.coordinates['free.turn'].initial = -120;
    p.edges[2].needs = ['crank'];
    p.edges[2].expressions = ['-crank'];
    p.sources['free.turn'] = ['crank'];
  } else if (mode === 'time') {
    doc.version = 10;
    delete doc.drivers.crank; delete doc.drivers.motor;
    delete p.coordinates.crank; delete p.coordinates.motor;
    delete p.sources.crank; delete p.sources.motor;
    doc.bindings = [];
    p.edges[0].needs = ['time'];
    p.edges[0].expressions = ['-120 - 7200*time'];
    p.edges[1].needs = ['drum.turn'];
    p.edges[1].expressions = ['drum.turn'];
    p.edges[2].needs = ['time'];
    p.edges[2].expressions = ['10*time'];
    p.sources = {'drum.turn': ['@time:0'], 'bell.turn': ['@time:0'],
                 'free.turn': ['@time:2']};
    p.time_drives = [{id:'@time:0', edge:0}, {id:'@time:2', edge:2}];
  } else if (mode === 'compound') {
    p.spans['bell.turn'].low.expression = 'crank * motor - .1';
    p.coordinates.crank.initial = 0;
    p.coordinates['bell.turn'].initial = 0;
    p.edges = p.edges.filter((edge: any) => edge.gives[0] !== 'bell.turn');
    p.sources['bell.turn'] = [];
  }
  return new Run(loadProgram(doc as RunDocument, 'periodic-contact'), .1, 64);
}

describe('periodic first-contact attribution', () => {
  it('the old endpoint-only attribution fails the producer case', () => {
    const run = machine();
    const internal = run as any;
    const spy = vi.spyOn(internal, 'constraintGroup').mockImplementation(
      (constraint: any, admissions: any, values: any, held: any) =>
        constraint.candidates.filter((candidate: string) => {
          if (!admissions[candidate]) return false;
          const alone = {[candidate]: admissions[candidate]};
          const level = (t: number) => internal.constraintLevel(
            constraint, held, values, alone, t, internal.bank[constraint.identifier]);
          return level(1) > level(0);
        }));
    try { expect(() => run.move('crank', {to:840})).toThrow(StopInvariantError); }
    finally { spy.mockRestore(); }
    expect(run.move('crank', {to:840}).status).toBe('blocked');
  });
  for (const mode of ['lower', 'upper']) {
    for (const turns of [0, 3]) {
      for (const target of [830, 840]) {
        it(`${mode}, turn ${turns}, endpoint ${target}`, () => {
          const run = machine(mode, turns);
          const request = run.move('crank', {to:target + 360*turns});
          expect(request.status).toBe('blocked');
          expect(request.admitted).toBeCloseTo(5.22, 7);
          expect(run.state().crank).toBeCloseTo(125.22 + 360*turns, 7);
          expect(run.stops()[0].inputs).toEqual(['crank']);
        });
      }
    }
  }
  it('keeps fixed, short and timed controls', () => {
    for (const [mode, to, duration] of [
      ['fixed', 840, 0], ['lower', 150, 0], ['lower', 840, 2],
    ] as const) {
      const run = machine(mode);
      const request = run.move('crank', {to, duration});
      for (let i=0; i<20; i++) run.advance();
      expect(request.status).toBe('blocked');
      expect(run.state().crank).toBeCloseTo(125.22, 7);
    }
  });
  it('replays, holds idle, allows relief, and retries without backlog', () => {
    const run = machine();
    const before = run.snapshot();
    run.move('crank', {to:840});
    const stopped = run.snapshot();
    run.restore(before); run.move('crank', {to:840});
    expect(run.snapshot()).toEqual(stopped);
    run.advance(); expect(run.state()).toEqual(stopped.bank);
    expect(run.move('crank', {by:720}).status).toBe('blocked');
    expect(run.move('crank', {by:-.05}).status).toBe('completed');
    expect(run.move('crank', {by:720}).status).toBe('blocked');
    expect(run.state().crank).toBeCloseTo(125.22, 7);
  });
  for (const mode of ['lower', 'relieving', 'disengaged']) {
    it(`lets ${mode} independent/relieving/disengaged motion finish`, () => {
      const run = machine(mode);
      const turn = run.move('crank', {to:840, duration:.1});
      const other = run.move('motor', {by:10, duration:.1});
      run.advance();
      expect(turn.status).toBe('blocked');
      expect(other.status).toBe('completed');
      expect(run.state().motor).toBe(10);
      expect(run.stops()[0].inputs).toEqual(['crank']);
      expect(turn.admitted).toBeCloseTo(mode === 'relieving' ? 720*5.22/710 : 5.22, 7);
    });
  }
  it('keeps both simultaneous contacts', () => {
    const run = machine('simultaneous'); run.move('crank', {to:840});
    expect(run.stops()).toHaveLength(2);
    expect(run.stops()[0].t).toBe(run.stops()[1].t);
  });
  it('stops a time admission without stopping time or another time drive', () => {
    const run = machine('time');
    for (let i=1; i<=2; i++) {
      run.advance();
      expect(run.state()['bell.turn']).toBeCloseTo(-125.22, 7);
      expect(run.clock()).toBe(i*.1);
      expect(run.state()['free.turn']).toBe(i);
      expect(run.stops()[i-1].inputs).toEqual([]);
      expect(run.stops()[i-1].time_drives).toEqual(['@time:0']);
    }
  });
  it('still refuses a compound-only push atomically', () => {
    const run = machine('compound'); const before = run.snapshot();
    const first = run.move('crank', {by:1, duration:.1});
    const second = run.move('motor', {by:1, duration:.1});
    expect(() => run.advance()).toThrow(StopInvariantError);
    expect(run.snapshot()).toEqual(before);
    expect([first.status, second.status]).toEqual(['refused', 'refused']);
    expect(run.stops()).toEqual([]);
  });
  it('preserves the final inside assertion and atomic rollback', () => {
    const run = machine(); const before = run.snapshot();
    const spy = vi.spyOn(run as any, 'assertInside').mockImplementation(() => {
      throw new StopInvariantError('probe');
    });
    try {
      expect(() => run.move('crank', {to:840})).toThrow('probe');
      expect(run.snapshot()).toEqual(before); expect(run.stops()).toEqual([]);
    } finally { spy.mockRestore(); }
  });
});
