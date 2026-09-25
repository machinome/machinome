/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import { describe, expect, it } from 'vitest';
import corpus from '../time-drive-corpus.json';
import runningCorpus from '../running-corpus.json';
import { Engine } from './engine';
import { loadProgram } from './program';
import type { RunDocument } from './program';
import type { Command } from './commands';
import type { RunState } from './run';
import { assertRenderable } from '../viewer';
import type { Manifest } from '../types';
import astrarium from '../../../../tests/fixtures/astrarium/viewer.json';
import { createSession } from './worker';
import type { Reply } from './protocol';

// Copied byte for byte from the producer at 0ce71cd. Never regenerate expected
// numbers here or widen the fixture's agreement window.
function near(actual: number, expected: number): void {
  expect(Math.abs(actual - expected)).toBeLessThanOrEqual(
    corpus.tolerance.float * Math.max(1, Math.abs(actual), Math.abs(expected)));
}

function records(actual: object[], expected: object[]): void {
  expect(actual).toHaveLength(expected.length);
  actual.forEach((item, index) => {
    const wanted = expected[index] as Record<string, unknown>;
    const got = item as Record<string, unknown>;
    expect(Object.keys(got).filter(key => key !== 'tick').sort())
      .toEqual(Object.keys(wanted).sort());
    for (const [key, value] of Object.entries(wanted)) {
      if (['t', 'value', 'admitted'].includes(key)) near(got[key] as number, value as number);
      else expect(got[key], key).toEqual(value);
    }
  });
}

describe('producer time-drive corpus', () => {
  it('keeps all seven machines and every recorded tick', () => {
    expect(corpus.machines.map(machine => machine.name)).toEqual([
      'TimeAffine', 'TimeEnabled', 'AstrariumClock', 'IndependentTimeDrives',
      'TimeRelease', 'MixedTimeDrive', 'CurvedTimeStop',
    ]);
    expect(corpus.machines.reduce((sum, machine) => sum + machine.ticks.length, 0)).toBe(54);
  });

  it.each(corpus.machines)('replays $name at dt=$dt', machine => {
    const engine = Engine.load(machine.document as RunDocument, {
      dt: machine.dt, record: 1000, sourceUrl: `time-drive-corpus.json#${machine.name}`,
    });
    const handles = new Map<string, Command>();
    const saved = new Map<string, RunState>();
    for (let step = 1; step <= machine.steps; step += 1) {
      let beforeCrossings = engine.crossings().length;
      let beforeStops = engine.stops().length;
      for (const action of machine.script) {
        if (action.tick !== step) continue;
        if ('move' in action && action.move) {
          const { input, ...request } = action.move;
          handles.set(action.handle!, engine.move(input, request));
        } else if ('rate' in action && action.rate) {
          handles.set(action.handle!, engine.rate(action.rate.input, action.rate.rate)!);
        } else if ('snapshot' in action && action.snapshot) {
          saved.set(action.snapshot, engine.snapshot());
        } else if ('restore' in action && action.restore) {
          engine.restore(saved.get(action.restore)!);
          beforeCrossings = beforeStops = 0;
        } else if ('reset' in action && action.reset) {
          engine.reset();
          beforeCrossings = beforeStops = 0;
        } else throw new Error(`unknown corpus action ${JSON.stringify(action)}`);
      }
      // A sequence step includes its instantaneous commands and its advance.
      engine.advance();
      const wanted = machine.ticks[step - 1];
      expect(engine.tick()).toBe(wanted.tick);
      near(engine.clock(), wanted.time);
      expect(Object.keys(engine.state()).sort()).toEqual(Object.keys(wanted.bank).sort());
      for (const [key, value] of Object.entries(wanted.bank)) near(engine.state()[key], value);
      records(engine.crossings().slice(beforeCrossings), wanted.crossings);
      records(engine.stops().slice(beforeStops), wanted.stops);
      records([...handles].map(([handle, command]) => ({
        handle, status: command.status, admitted: command.admitted,
      })), wanted.commands);
      expect(engine.state()).not.toHaveProperty('time');
      expect(Object.keys(engine.state()).some(id => id.startsWith('@time:'))).toBe(false);
    }
  });
});

type MutableDocument = typeof corpus.machines[0]['document'];
const document = () => structuredClone(corpus.machines[0].document);

describe('time-drive document validation', () => {
  it('accepts the real v10 document through the public viewer gate', () => {
    expect(() => assertRenderable(astrarium as unknown as Manifest, '/time.json')).not.toThrow();
  });
  it('loads a clock source without making it an input', () => {
    const program = loadProgram(document() as RunDocument, '/time.json');
    expect(program.inputs).toEqual([]);
    expect(program.order).toEqual(['shaft.turn']);
  });

  const malformed: [string, (doc: MutableDocument) => void, RegExp][] = [
    ['missing mapping', doc => { delete (doc.program as any).time_drives; }, /time_drives/],
    ['empty mapping', doc => { doc.program.time_drives = []; }, /time_drives/],
    ['old version', doc => { doc.version = 9; }, /version 10|version-10/],
    ['nonarray mapping', doc => { (doc.program as any).time_drives = {}; }, /time_drives/],
    ['duplicate mapping', doc => { doc.program.time_drives.push(doc.program.time_drives[0]); }, /time_drives/],
    ['wrong ID', doc => { doc.program.time_drives[0].id = '@time:2'; }, /time_drives/],
    ['bad index', doc => { doc.program.time_drives[0].edge = 3; }, /time_drives/],
    ['fractional index', doc => { doc.program.time_drives[0].edge = 0.5; }, /time_drives/],
    ['clock target', doc => { doc.program.edges[0].gives = ['time']; }, /time/],
    ['non-clock edge', doc => { doc.program.edges[0].needs = ['shaft.turn']; }, /time/],
    ['wrong clock', doc => { doc.program.clock = 'otherTime'; }, /clock/],
    ['fake bank value', doc => { (doc.program.coordinates as any)['@time:0'] = { kind: 'coordinate', initial: 0 }; }, /@time/],
    ['unknown candidate', doc => { (doc.program.sources as any)['shaft.turn'] = ['@time:99']; }, /sources/],
  ];
  it.each(malformed)('refuses %s before executing', (_name, mutate, reason) => {
    const broken = document();
    mutate(broken);
    expect(() => loadProgram(broken as RunDocument, '/broken-time.json')).toThrow(reason);
    expect(() => loadProgram(broken as RunDocument, '/broken-time.json')).toThrow('/broken-time.json');
  });
});

describe('time-drive boundary cases', () => {
  const entry = (name: string) => structuredClone(corpus.machines.find(item => item.name === name)!);

  it('publishes an instant winding commit before reporting its completion', () => {
    const replies: Reply[] = [];
    const session = createSession(reply => replies.push(reply));
    session.handle({ t: 'load', document: entry('AstrariumClock').document as RunDocument, dt: 1, record: 20 });
    session.handle({ t: 'advance', id: 1, ticks: 2 });
    session.handle({ t: 'command', id: 2, op: 'move', input: 'enabled', to: 0 });
    replies.length = 0;
    session.handle({ t: 'command', id: 3, op: 'move', input: 'wind', by: 2 });
    expect(replies.map(reply => reply.t)).toEqual(['issued', 'frame', 'outcome']);
    const frame = replies[1];
    if (frame.t !== 'frame') throw new Error('missing instantaneous commit');
    expect(frame.tick).toBe(2);
    expect(frame.clock).toBe(2);
    expect([...frame.bank]).toEqual([0, 2, 2, 0]);
  });

  it('instant input operations neither advance time nor reverse retained motion', () => {
    const engine = Engine.load(entry('AstrariumClock').document as RunDocument, { dt: 1 });
    engine.advance(2);
    engine.move('enabled', { to: 0 });
    engine.move('wind', { by: 2 });
    engine.move('enabled', { to: 1 });
    expect(engine.clock()).toBe(2);
    expect(engine.state()['shaft.turn']).toBe(2);
    expect(engine.state()['weight.drop']).toBe(0);
    expect(engine.commands()).toEqual([]);
    engine.advance();
    expect(engine.state()['shaft.turn']).toBe(3);
  });

  it('a nonlinear drive resumes at current global time with no backlog', () => {
    const doc = entry('TimeRelease').document;
    doc.program.edges[1].expressions = ['time * time'];
    doc.program.edges[1].affine = [false];
    const engine = Engine.load(doc as RunDocument, { dt: 1, record: 100 });
    engine.advance(4);
    near(engine.state()['shaft.turn'], 2.5);
    engine.move('release', { to: 100 });
    engine.advance();
    near(engine.state()['shaft.turn'], 11.5); // 2.5 + (5² - 4²), not 25
    expect(engine.clock()).toBe(5);
  });

  it.each([2, 0.5, 0.02])('keeps the curved train coherent at dt=%s', dt => {
    const engine = Engine.load(entry('CurvedTimeStop').document as RunDocument, { dt });
    engine.advance(Math.round(2 / dt));
    near(engine.state()['shaft.turn'], 2);
    near(engine.state()['follower.turn'], 2);
  });

  it('a grouped time relation stops all its targets together', () => {
    const doc = entry('IndependentTimeDrives').document;
    doc.program.edges[0].gives.push('other.turn');
    doc.program.edges[0].expressions.push('2 * time');
    doc.program.edges[0].affine.push(true);
    doc.program.edges[0].plans.push(null);
    doc.program.edges.splice(1, 1);
    doc.program.time_drives = [{ id: '@time:0', edge: 0 }];
    doc.program.sources['other.turn'] = ['@time:0'];
    const engine = Engine.load(doc as RunDocument, { dt: 1 });
    engine.advance(5);
    near(engine.state()['other.turn'], 2 * engine.state()['shaft.turn']);
    expect(engine.clock()).toBe(5);
  });

  it('keeps original edge IDs and local time through selector-block contraction', () => {
    // A local adaptation of the existing producer block, not a modified corpus:
    // drive its crank law from time, retaining the same selector and stop.
    const original = runningCorpus.machines.find(item => item.name === 'RangedBlock')!.document;
    const doc = JSON.parse(JSON.stringify(original).replace(/\bcrank\b/g, 'time'));
    doc.version = 10;
    delete doc.drivers.time;
    delete doc.program.coordinates.time;
    delete doc.program.sources.time;
    doc.program.time_drives = [{ id: '@time:1', edge: 1 }];
    for (const key of Object.keys(doc.program.sources)) {
      doc.program.sources[key] = doc.program.sources[key].map(
        (source: string) => source === 'time' ? '@time:1' : source);
    }
    const engine = Engine.load(doc as RunDocument, { dt: 1, record: 10 });
    engine.move('shift', { to: 1 });
    engine.advance(2);
    near(engine.state()['higher.turn'], 0.6);
    near(engine.state()['carry.travel'], 0.6);
    expect(engine.clock()).toBe(2);
    expect(engine.stops()[0].time_drives).toEqual(['@time:1']);
    expect(engine.stops()[0].inputs).toEqual([]);
  });

  it('a late conflicting writer rolls back autonomous state and history', () => {
    const doc = document();
    const second = structuredClone(doc.program.edges[0]);
    second.expressions = ['7 * time'];
    doc.program.edges.push(second);
    doc.program.time_drives.push({ id: '@time:1', edge: 1 });
    doc.program.sources['shaft.turn'].push('@time:1');
    const engine = Engine.load(doc as RunDocument, { dt: 1, record: 5 });
    const before = engine.snapshot();
    expect(() => engine.advance()).toThrow(/disagree|different/);
    expect(engine.snapshot()).toEqual(before);
    expect(engine.crossings()).toEqual([]);
    expect(engine.stops()).toEqual([]);
    expect(engine.trajectory()).toEqual([]);
  });
});
