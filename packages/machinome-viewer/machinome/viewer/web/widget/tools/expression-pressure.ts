/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Source-only census beside UNINSTRUMENTED public-bundle acceptance.
// Takes an external project-owned export; copies no project asset here.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { loadProgram } from '../src/run/program';
import { Run } from '../src/run/run';
import { expressionMetrics, releaseExpressions, resetExpressionMetrics,
  retainExpressions, withExpressions } from '../src/expressions';
import { poseScope } from '../src/run/pose';
import { evalExpr } from '../src/evaluator';

const bytes = readFileSync(process.argv[2]);
const document = JSON.parse(bytes.toString());
retainExpressions();
resetExpressionMetrics();
const started = performance.now();
const program = loadProgram(document, process.argv[2]);
const loaded = expressionMetrics();
const loadMs = performance.now() - started;
const run = new Run(program, .1);
run.advance();
const idle = expressionMetrics();
const expressions: string[] = [];
function collect(value: unknown): void {
  if (typeof value === 'string') expressions.push(value);
  else if (Array.isArray(value)) value.forEach(collect);
  else if (value && typeof value === 'object') Object.values(value).forEach(collect);
}
function visit(node: typeof document.root): void {
  for (const op of node.operations ?? []) collect(op[1]);
  if (node.flexible) collect(node.flexible.params);
  for (const child of node.children ?? []) visit(child);
}
visit(document.root);
withExpressions(() => {
  const scope = poseScope(run.state(), program.clock, 0, program.bindings);
  for (const expression of expressions) evalExpr(expression, scope);
});
const posed = expressionMetrics();
releaseExpressions();
console.log(JSON.stringify({ document_sha256: createHash('sha256').update(bytes).digest('hex'),
  program_identity: program.identity, load_ms: loadMs, load: loaded, idle, pose: posed,
  pose_expressions: expressions.length, disposed: expressionMetrics() }, null, 2));
