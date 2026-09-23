// Diagnostic only: use the same frozen production export and Python oracle
// from either viewer checkout; no WebGL or primary bundle is involved.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
const esbuild = require(resolve(process.cwd(), 'machinome_viewer/widget/node_modules/esbuild'));
const Module = require('node:module');
const output = esbuild.buildSync({
  stdin: { contents: 'export { Engine } from "./machinome_viewer/widget/src/run/engine.ts";',
    resolveDir: process.cwd(), sourcefile: 'curta-stage-probe.ts', loader: 'ts' },
  bundle: true, platform: 'node', format: 'cjs', write: false,
}).outputFiles[0].text;
const loaded = new Module('curta-stage-probe.cjs', null);
loaded.filename = resolve(process.cwd(), 'curta-stage-probe.cjs');
loaded.paths = Module._nodeModulePaths(process.cwd());
loaded._compile(output, loaded.filename);
const { Engine } = loaded.exports;
const [manifest, oraclePath] = process.argv.slice(2);
if (!manifest || !oraclePath) throw Error('Pass frozen manifest and Python oracle paths.');
const document = JSON.parse(readFileSync(manifest, 'utf8'));
const oracle = JSON.parse(readFileSync(oraclePath, 'utf8'));
const engine = Engine.load(document, { dt: 0.1 });
const report = {};
function stage(name, status) {
  const bank = engine.state();
  const expected = oracle[name];
  if (Object.keys(bank).length !== 214) throw Error(`${name}: not 214 coordinates`);
  if (status !== expected.status) throw Error(`${name}: ${status} != ${expected.status}`);
  for (const [key, value] of Object.entries(expected.bank)) {
    if (bank[key] !== value) throw Error(`${name}: ${key}: ${bank[key]} != ${value}`);
  }
  report[name] = { status, crank: bank.crank_rotation, coordinates: 214 };
}
stage('rest', 'rest');
const lift = engine.move('carriage_elevation', { to: 6 });
stage('lift', lift.status);
const saved = engine.snapshot();
const blocked = engine.move('crank_rotation', { to: 90, duration: 0.5 });
engine.advance(1);
stage('blocked', blocked.status);
const stopped = JSON.stringify(engine.snapshot());
engine.restore(saved);
const replay = engine.move('crank_rotation', { to: 90, duration: 0.5 });
engine.advance(1);
if (JSON.stringify(engine.snapshot()) !== stopped) throw Error('blocked snapshot replay differs');
stage('replay', replay.status);
const relief = engine.move('carriage_elevation', { to: 0 });
stage('relief', relief.status);
const afterRelief = engine.move('crank_rotation', { to: 90, duration: 0.5 });
engine.advance(5);
stage('after_relief', afterRelief.status);
engine.reset();
const outward = engine.move('crank_rotation', { by: 90, duration: 0.5 });
engine.advance(5);
stage('outward', outward.status);
const returned = engine.move('crank_rotation', { to: 360, duration: 1.5 });
engine.advance(15);
stage('return', returned.status);
console.log(JSON.stringify({ manifest, oraclePath, stages: report }, null, 2));
