// Read-only no-WebGL replay of the pinned Curta program. Run from either
// viewer checkout so esbuild bundles that checkout's current TypeScript.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import Module from 'node:module';
import { performance } from 'node:perf_hooks';

const require = createRequire(import.meta.url);
const esbuild = require(resolve(process.cwd(), 'machinome_viewer/widget/node_modules/esbuild'));
const output = (await esbuild.build({
  stdin: {
    contents: 'export { Engine } from "./machinome_viewer/widget/src/run/engine.ts";',
    resolveDir: process.cwd(), sourcefile: 'curta-cache-probe.ts', loader: 'ts',
  },
  bundle: true, platform: 'node', format: 'cjs', write: false,
})).outputFiles[0].text;
const loaded = new Module('curta-cache-probe.cjs', null);
loaded.filename = resolve(process.cwd(), 'curta-cache-probe.cjs');
loaded.paths = Module._nodeModulePaths(process.cwd());
loaded._compile(output, loaded.filename);
const { Engine } = loaded.exports;

if (process.argv.length !== 3) throw Error('Pass one pinned manifest.json path.');
const document = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const bits = (number) => {
  const buffer = Buffer.allocUnsafe(8);
  buffer.writeDoubleBE(number);
  return buffer.toString('hex');
};
const asBits = (value) => Array.isArray(value) ? value.map(asBits)
  : value !== null && typeof value === 'object'
    ? Object.fromEntries(Object.entries(value).map(([key, one]) => [key, asBits(one)]))
    : typeof value === 'number' ? bits(value) : value;
const bankHash = (bank) => {
  const hash = createHash('sha256');
  for (const key of Object.keys(bank).sort()) {
    hash.update(key);
    hash.update(Buffer.from([0]));
    const buffer = Buffer.allocUnsafe(8);
    buffer.writeDoubleLE(bank[key]);
    hash.update(buffer);
  }
  return hash.digest('hex');
};
const recordHash = (records) => createHash('sha256')
  .update(JSON.stringify(asBits(records))).digest('hex');
const measure = (action) => {
  const before = process.cpuUsage();
  const wall = performance.now();
  const result = action();
  const cpu = process.cpuUsage(before);
  return { result, cpuSeconds: (cpu.user + cpu.system) / 1e6,
    wallSeconds: (performance.now() - wall) / 1000 };
};
const engine = Engine.load(document, { dt: 1 / 240, record: 512 });
const rows = [];
const capture = (label, timing) => {
  const bank = engine.state();
  rows.push({ label, status: timing?.result.status ?? null,
    admitted: timing?.result.admitted === undefined ? null : bits(timing.result.admitted),
    cpuSeconds: timing?.cpuSeconds ?? null, wallSeconds: timing?.wallSeconds ?? null,
    tick: engine.tick(), clock: bits(engine.clock()), bankHash: bankHash(bank),
    coordinates: Object.keys(bank).length,
    crossingCount: engine.crossings().length, crossingHash: recordHash(engine.crossings()),
    stopCount: engine.stops().length, stopHash: recordHash(engine.stops()),
    cacheEntries: engine.run?.blockReuse?.size ?? null });
};
capture('rest');
const prep = measure(() => engine.move('crank_rotation', { to: 90 }));
capture('prep90', prep);
const snapshot = engine.snapshot();
for (let index = 1; index <= 3; index += 1) {
  const timing = measure(() => {
    const command = engine.move('reverser_height', { by: -1, duration: 0.2 });
    engine.advance(48);
    return command;
  });
  capture(`gesture-${index}`, timing);
}
engine.restore(snapshot);
capture('restore-prep');
const replay = measure(() => {
  const command = engine.move('reverser_height', { by: -1, duration: 0.2 });
  engine.advance(48);
  return command;
});
capture('replay-gesture-1', replay);
const normal = Engine.load(document, { dt: 0.1, record: 512 });
const normalTiming = measure(() => {
  const command = normal.move('crank_rotation', { to: 18, duration: 0.1 });
  normal.advance(1);
  return command;
});
rows.push({ label: 'normal18', status: normalTiming.result.status,
  admitted: bits(normalTiming.result.admitted),
  cpuSeconds: normalTiming.cpuSeconds, wallSeconds: normalTiming.wallSeconds,
  tick: normal.tick(), clock: bits(normal.clock()), bankHash: bankHash(normal.state()),
  coordinates: Object.keys(normal.state()).length,
  crossingCount: normal.crossings().length, crossingHash: recordHash(normal.crossings()),
  stopCount: normal.stops().length, stopHash: recordHash(normal.stops()),
  cacheEntries: normal.run?.blockReuse?.size ?? null });
process.stdout.write(JSON.stringify({ identity: document.program.identity, rows }) + '\n');
