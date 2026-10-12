/*
 * Read-only opt-in diagnostic for the pinned installed Curta v13 document.
 * Set CURTA_INSTALLED_PROFILE_DOCUMENT to its absolute path.
 */
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { expect, it, vi } from 'vitest';

const measured = vi.hoisted(() => ({ calls: 0, pairs: new Set<string>(),
  placements: 0, placed: new Set<string>(), trace: [] as string[],
  boundTrace: [] as string[], boundExpressions: new Set<string>(),
  cacheStats: null as null | {
    pairHits: number; placementHits: number;
    pairEntries: number; placementEntries: number;
  } }));

vi.mock('./profiles', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./profiles')>();
  const bits = (value: number): string => {
    const view = new DataView(new ArrayBuffer(8));
    view.setFloat64(0, value, false);
    return view.getBigUint64(0, false).toString(16).padStart(16, '0');
  };
  return { ...actual, withProfileIntegrationCache: (
    table: Parameters<typeof actual.withProfileIntegrationCache>[0],
    action: Parameters<typeof actual.withProfileIntegrationCache>[1],
  ) => {
    if (process.env.PROFILE_CACHE_BENCH_DISABLE === '1') return action({
      pairHits: 0, placementHits: 0, pairEntries: 0, placementEntries: 0,
    });
    return actual.withProfileIntegrationCache(table, (stats) => {
      try { return action(stats); }
      finally { measured.cacheStats = { ...stats }; }
    });
  }, profileOverlap: (
    table: readonly unknown[], leftIndex: number, rightIndex: number,
    la: number, lx: number, ly: number, ra: number, rx: number, ry: number,
  ) => {
    measured.calls += 1;
    const left = `${leftIndex}:${bits(la)}:${bits(lx)}:${bits(ly)}`;
    const right = `${rightIndex}:${bits(ra)}:${bits(rx)}:${bits(ry)}`;
    measured.placements += 2;
    measured.placed.add(left);
    measured.placed.add(right);
    measured.pairs.add(`${left}|${right}`);
    const result = actual.profileOverlap(table as Parameters<typeof actual.profileOverlap>[0],
      leftIndex, rightIndex, la, lx, ly, ra, rx, ry);
    measured.trace.push(`${left}|${right}=${bits(result)}`);
    return result;
  } };
});

vi.mock('./program', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./program')>();
  const bits = (value: number): string => {
    const view = new DataView(new ArrayBuffer(8));
    view.setFloat64(0, value, false);
    return view.getBigUint64(0, false).toString(16).padStart(16, '0');
  };
  return { ...actual, evaluateExpression: (
    program: Parameters<typeof actual.evaluateExpression>[0],
    expression: string, values: Record<string, number>,
  ) => {
    const result = actual.evaluateExpression(program, expression, values);
    if (measured.boundExpressions.has(expression)) {
      const scope = Object.keys(values).sort().map((name) => `${name}:${bits(values[name])}`);
      measured.boundTrace.push(`${expression}|${scope.join(',')}=${bits(result)}`);
    }
    return result;
  } };
});

import { loadProgram } from './program';
import type { RunDocument } from './program';
import { Run } from './run';

const path = process.env.CURTA_INSTALLED_PROFILE_DOCUMENT;
it.skipIf(!path)('reports one pinned installed Curta v13 integration attempt', () => {
  const document = JSON.parse(readFileSync(path!, 'utf8')) as RunDocument;
  const program = loadProgram(document, 'producer://curta-installed-profile-v13.json');
  for (const span of Object.values(program.spans)) {
    if (span.low !== null && typeof span.low === 'object') {
      measured.boundExpressions.add(span.low.expression);
    }
    if (span.high !== null && typeof span.high === 'object') {
      measured.boundExpressions.add(span.high.expression);
    }
  }
  const run = new Run(program, 0.1, 8);
  const request = run.move('crank_rotation', { to: 18, duration: 0.1 });
  const startCpu = process.cpuUsage();
  const start = performance.now();
  run.advance();
  const cpu = process.cpuUsage(startCpu);
  const state = run.state();
  const bankBits = Object.keys(state).sort().map((name) => {
    const view = new DataView(new ArrayBuffer(8));
    view.setFloat64(0, state[name], false);
    return [name, view.getBigUint64(0, false).toString(16).padStart(16, '0')];
  });
  const digest = createHash('sha256').update(JSON.stringify(bankBits)).digest('hex');
  const bankMap = Object.fromEntries(bankBits);
  const oraclePath = process.env.CURTA_INSTALLED_PROFILE_ORACLE;
  if (oraclePath) {
    const oracle = JSON.parse(readFileSync(oraclePath, 'utf8')) as {
      document_identity: string; bank_bits: Record<string, string>;
      request: { status: string; admitted_bits: string }; tick: number;
      stops: unknown[];
    };
    expect(program.identity).toBe(oracle.document_identity);
    expect(request.status).toBe(oracle.request.status);
    const admitted = new DataView(new ArrayBuffer(8));
    admitted.setFloat64(0, request.admitted, false);
    expect(admitted.getBigUint64(0, false).toString(16).padStart(16, '0'))
      .toBe(oracle.request.admitted_bits);
    expect(run.snapshot().tick).toBe(oracle.tick);
    expect(run.stops()).toEqual(oracle.stops);
    expect(bankMap).toEqual(oracle.bank_bits);
  }
  console.log(JSON.stringify({ profile: 'installed-curta-v13-one-tick',
    identity: program.identity, status: request.status, admitted: request.admitted,
    bankCount: bankBits.length, bankDigest: digest, calls: measured.calls,
    orderedContactDigest: createHash('sha256').update(JSON.stringify(measured.trace)).digest('hex'),
    boundEvaluations: measured.boundTrace.length,
    orderedBoundDigest: createHash('sha256').update(JSON.stringify(measured.boundTrace)).digest('hex'),
    distinctPairs: measured.pairs.size, placements: measured.placements,
    distinctPlacements: measured.placed.size, cacheStats: measured.cacheStats,
    executedPlacements: measured.placements - (measured.cacheStats?.pairHits ?? 0) * 2
      - (measured.cacheStats?.placementHits ?? 0),
    cpuSeconds: (cpu.user + cpu.system) / 1e6,
    wallSeconds: (performance.now() - start) / 1000 }));
});
