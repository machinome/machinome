/* Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later */
import { describe, expect, it } from 'vitest';
import fixture from '../../../../tests/fixtures/source-timing/compact.json';
import { Engine } from './engine';
import type { RunDocument } from './program';

function matches(actual: unknown, expected: unknown, agreement: number, field = ''): void {
  if (typeof expected === 'number') {
    if (field === 'tick' || field === 'level') {
      expect(actual).toBe(expected);
      return;
    }
    expect(typeof actual).toBe('number');
    expect(Math.abs((actual as number)-expected)).toBeLessThanOrEqual(
      agreement*Math.max(1, Math.abs(actual as number), Math.abs(expected)));
  } else if (Array.isArray(expected)) {
    expect(Array.isArray(actual)).toBe(true);
    expect((actual as unknown[]).length).toBe(expected.length);
    expected.forEach((value, i) => matches((actual as unknown[])[i], value, agreement, field));
  } else if (expected !== null && typeof expected === 'object') {
    expect(Object.keys(actual as object).sort()).toEqual(Object.keys(expected).sort());
    Object.entries(expected).forEach(([key, value]) => matches(
      (actual as Record<string, unknown>)[key], value, agreement, key));
  } else expect(actual).toBe(expected);
}

describe('producer source-timing fixtures', () => {
  it.each([null, 128])('does not reset the crossing budget at inherited boundaries (record %s)', record => {
    const document = structuredClone(fixture.cases.find(entry => entry.name === 'crossing-budget')!.document);
    document.program.limits.max_crossings = 2;
    const engine = Engine.load(document as unknown as RunDocument, { dt: .1, record });
    const before = engine.state();
    const command = engine.move('crank', { to: 4, duration: .1 });
    expect(() => engine.advance()).toThrow(/surfaces/);
    expect(engine.state()).toEqual(before);
    expect(command.status).toBe('refused');
    expect(engine.tick()).toBe(0);
    expect(engine.crossings()).toEqual([]);
  });
  for (const entry of fixture.cases) {
    const agreement = entry.document.program.limits.agreement;
    it(`${entry.name}: bulk, reverse and repeat match all records`, () => {
      const engine = Engine.load(entry.document as unknown as RunDocument,
                                 { dt: .1, record: 128 });
      for (const row of entry.rows) {
        const command = engine.move('crank', { to: row.to });
        matches(command.status, row.status, agreement);
        matches(command.admitted, row.admitted, agreement);
        matches(engine.state(), row.bank, agreement);
        matches(engine.crossings(), row.crossings, agreement);
        // Python's dataclass always carries an empty time_drives tuple;
        // the browser omits that optional key for command-only stops.
        matches(engine.stops().map(stop => ({ time_drives: [], ...stop })), row.stops, agreement);
      }
    });
    it(`${entry.name}: restored whole and partitioned requests agree`, () => {
      const engine = Engine.load(entry.document as unknown as RunDocument,
                                 { dt: .1, record: 128 });
      const initial = engine.snapshot();
      const whole = engine.move('crank', { to: 4 });
      const bank = engine.state();
      const admitted = whole.admitted;
      engine.restore(initial);
      let total = 0;
      for (let n = 1; n <= 16; n += 1) {
        const command = engine.move('crank', { to: n/4 });
        total += command.admitted;
        if (command.status === 'blocked') break;
        expect(command.status).toBe('completed');
      }
      matches(engine.state(), bank, agreement);
      matches(total, admitted, agreement);
    });
  }
});
