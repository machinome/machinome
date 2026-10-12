// Diagnostic only: run from either viewer checkout against the same v12 export.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
const esbuild = require(resolve(process.cwd(), 'machinome_viewer/widget/node_modules/esbuild'));
const source = [
  'export { Engine } from "./machinome_viewer/widget/src/run/engine.ts";',
  'export { Run } from "./machinome_viewer/widget/src/run/run.ts";',
].join('\n');
const output = esbuild.buildSync({
  stdin: { contents: source, resolveDir: process.cwd(), sourcefile: 'probe.ts', loader: 'ts' },
  bundle: true, platform: 'node', format: 'cjs', write: false,
}).outputFiles[0].text;
const Module = require('node:module');
const loaded = new Module('probe.cjs', null);
loaded.filename = resolve(process.cwd(), 'probe.cjs');
loaded.paths = Module._nodeModulePaths(process.cwd());
loaded._compile(output, loaded.filename);
const { Engine, Run } = loaded.exports;
const manifest = process.argv[2];
if (!manifest) throw new Error('Pass the pinned manifest.json path.');
const document = JSON.parse(readFileSync(manifest, 'utf8'));
const mode = process.argv[3] ?? 'free';
const counts = { constraintLevel: 0, deltasOf: 0, searchedConstraint: 0 };
const samples = createHash('sha256');
for (const name of Object.keys(counts)) {
  const original = Run.prototype[name];
  Run.prototype[name] = function (...args) {
    counts[name] += 1;
    const result = original.apply(this, args);
    if (name === 'constraintLevel') {
      samples.update(`${args[0].identifier}\0${args[0].side}\0`);
      for (const value of [args[4], result]) {
        const bits = Buffer.allocUnsafe(8);
        bits.writeDoubleLE(value);
        samples.update(bits);
      }
    }
    return result;
  };
}
const digest = (bank) => {
  const hash = createHash('sha256');
  for (const key of Object.keys(bank).sort()) {
    hash.update(key);
    hash.update(Buffer.from([0]));
    const bits = Buffer.allocUnsafe(8);
    bits.writeDoubleLE(bank[key]);
    hash.update(bits);
  }
  return hash.digest('hex');
};
const engine = Engine.load(document, { dt: 0.1 });
if (mode === 'raised') engine.move('carriage_elevation', { to: 6 });
const saved = engine.snapshot();
const command = engine.move('crank_rotation', { to: 90, duration: 0.5 });
const before = process.cpuUsage();
const ticks = [];
for (let index = 0; index < (mode === 'raised' ? 1 : 5); index += 1) {
  engine.advance(1);
  const bank = engine.state();
  ticks.push({ index: index + 1, bank: digest(bank), count: Object.keys(bank).length,
    crank: bank.crank_rotation, counters: { ...counts } });
}
const cpu = process.cpuUsage(before);
const first = engine.snapshot();
let replay = null;
if (mode === 'raised') {
  engine.restore(saved);
  const retry = engine.move('crank_rotation', { to: 90, duration: 0.5 });
  engine.advance(1);
  replay = { status: retry.status, exact: JSON.stringify(engine.snapshot()) === JSON.stringify(first),
    bank: digest(engine.state()), crank: engine.state().crank_rotation };
}
console.log(JSON.stringify({ manifest, mode, status: command.status,
  admitted: command.admitted, cpuSeconds: (cpu.user + cpu.system) / 1e6,
  samples: samples.digest('hex'), ticks, replay }, null, 2));
