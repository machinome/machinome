/* Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later */
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { Engine } from './engine';
import type { RunDocument } from './program';

interface Row {
  driver: string; to: number; status: string; admitted: number;
  bank: Record<string, number>; crossings: Record<string, unknown>[];
  stops: Record<string, unknown>[]; seconds: number;
}
interface Fixture {
  cases: { name: string; document: RunDocument; rows: Row[]; partitioned: Row[] }[];
}

function matches(actual: unknown, expected: unknown, tolerance: number, field = ''): void {
  if (typeof expected === 'number' && field !== 'tick' && field !== 'level') {
    expect(typeof actual, field).toBe('number');
    expect(Math.abs((actual as number) - expected), field).toBeLessThanOrEqual(
      tolerance * Math.max(1, Math.abs(actual as number), Math.abs(expected)));
  } else if (Array.isArray(expected)) {
    expect((actual as unknown[]).length, field).toBe(expected.length);
    expected.forEach((value, i) => matches((actual as unknown[])[i], value, tolerance, `${field}[${i}]`));
  } else if (expected !== null && typeof expected === 'object') {
    expect(Object.keys(actual as object).sort(), field).toEqual(Object.keys(expected).sort());
    for (const [key, value] of Object.entries(expected)) matches((actual as Record<string, unknown>)[key], value, tolerance, key);
  } else expect(actual, field).toEqual(expected);
}

describe('unchanged Curta diagnostic exports', () => {
  for (const name of ['curta-6', 'curta-7', 'curta-11', 'curta-11-constrained']) {
    it(`${name}: full banks, commands and records, whole and restored portions`, async () => {
      const fixture = JSON.parse(readFileSync(new URL(
        `../../../../tests/fixtures/source-timing/${name}.json`, import.meta.url), 'utf8')) as Fixture;
      const entry = fixture.cases[0];
      const engine = Engine.load(entry.document, { dt: .1, record: 4096 });
      const started = performance.now();
      const run = async (row: Row) => {
        // Permit runner RPC and test reporting between expensive requests.
        // No yield, subdivision or timing change occurs within a request.
        await new Promise<void>(resolve => setTimeout(resolve, 0));
        const cross = engine.crossings().length;
        const stop = engine.stops().length;
        const before = performance.now();
        const command = engine.move(row.driver, { to: row.to });
        const seconds = (performance.now()-before)/1000;
        matches(command.status, row.status, 0);
        matches(command.admitted, row.admitted, 1e-9);
        matches(engine.state(), row.bank, 1e-9);
        matches(engine.crossings().slice(cross), row.crossings, 1e-9);
        matches(engine.stops().slice(stop).map(item => ({ time_drives: [], ...item })), row.stops, 1e-9);
        return seconds;
      };
      for (const row of entry.rows.slice(0, -1)) await run(row);
      const snapshot = engine.snapshot();
      const bulkSeconds = await run(entry.rows[entry.rows.length - 1]);
      const whole = engine.state();
      expect(whole['tens.turn']).toBeCloseTo(704, 8);
      engine.restore(snapshot);
      for (const row of entry.partitioned) await run(row);
      matches(engine.state(), whole, 1e-9);
      console.log(`${name}: bulk ${bulkSeconds.toFixed(3)}s; full replay ${((performance.now()-started)/1000).toFixed(3)}s`);
    }, 240_000);
  }
});
