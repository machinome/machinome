/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The shared expression DAG (OpenSpec `share-expression-subtrees`,
// design D1-D12; ADR-043). A published expression may paste the same
// subexpression thousands of times over (solid2's `OpenSCADConstant`
// builds an expression by string concatenation), and one such
// expression may appear under many operations of one document.
// `jokenizer`'s own tree-walking `evaluate` has no way to notice it is
// computing the same thing twice: two structurally identical parse
// subtrees are two objects, and its visitor has nowhere to put a memo.
//
// This module replaces that walk with a hash-consed DAG:
//
//   prepare(expression) -> a parsed expression is turned ONCE into a
//   node id, interned bottom-up into a table shared by the whole page
//   (D2, D8): a structurally identical subtree, wherever it occurs,
//   becomes the same node. The parse tree is dropped as soon as its
//   root is interned -- nothing here retains it.
//
//   valueOf(id, scope) -> a memoized walk of the DAG, stamped by an
//   evaluation PASS (D6): a pass is a set of scope values, not a
//   syntactic event, so two calls carrying equal values -- the common
//   case while animation plays two `tree.update` walks per frame with
//   two different scope OBJECTS -- cost nothing the second time.
//
//   freeNames(id) -> the node's free-variable set, computed once per
//   node and memoized beside it (D11): the same three rules
//   `freeVariables` always had (a dotted driver id is one name, a
//   call's callee is never a variable, a generic member's variables
//   come from its owner), now read off the DAG instead of a fresh walk
//   of the whole parse tree.
//
// `jokenizer` stays the parser (`tokenize`); its `evaluate` and
// `ExpressionVisitor` are not imported here or anywhere else in this
// package (D1). Every semantic rule this module reproduces --
// unary `-` as `-1 * v`, `&&`/`||` short-circuiting their right side, a
// name resolved by `in` with a falsy-owner guard, a truthy primitive
// owner throwing jokenizer's own native `TypeError` -- is reproduced
// DELIBERATELY and VERBATIM (D1, D5), against jokenizer's own
// `Tokenizer.js`/`ExpressionVisitor.js`/`Settings.js`, and not
// invented or smoothed over.

import { tokenize } from 'jokenizer';
import type {
  ArrayExpression, AssignExpression, BinaryExpression, CallExpression,
  Expression, GroupExpression, IndexerExpression, LiteralExpression,
  MemberExpression, ObjectExpression, TernaryExpression, UnaryExpression,
  VariableExpression,
} from 'jokenizer';

// ---------------------------------------------------------------------
// Parsing: the exponent-literal rewrite (moved here from evaluator.ts,
// where it belongs to parsing) plus jokenizer's `tokenize`.
// ---------------------------------------------------------------------

// Python's str() is the only formatter between the producer and this
// reader, and it prints a float in exponent notation below 1e-4 and at
// or above 1e16 -- so `6.103515625e-05` (a fine screw's millimetres per
// microstep) and `1.59e-15` (a placement that missed zero) are ordinary
// document content. jokenizer's number rule is digits, separator,
// digits, and it throws at the `e`, refusing the whole expression and
// with it the model. Rewrite such a literal to plain decimal before
// tokenizing.
//
// The rewrite shifts the decimal point through the digit string rather
// than reconstructing the number: exact at any magnitude, where a
// Number() round-trip could round the tail and toFixed() returns
// exponent form itself above 1e21, which would put the bug back for
// large values.
//
// Only a literal is matched. A digit must precede the `e` and a digit
// must follow the optional sign, and the character before must not be
// one a name can contain -- so `1e-5` is rewritten while a driver named
// `e5`, a member `stage.e10` and the function `exp` are left alone. The
// preceding character is matched rather than looked behind, because a
// lookbehind is a parse error in a browser too old for it and would
// take the whole bundle down with it.
const EXPONENT_LITERAL = /(^|[^\w.$])(\d+)(?:\.(\d+))?[eE]([-+]?\d+)/g;

function plainLiterals(expression: string): string {
  return expression.replace(
    EXPONENT_LITERAL,
    (_match, before: string, whole: string, fraction = '', exponent: string) => {
      const digits = whole + fraction;
      const point = whole.length + Number(exponent);
      if (point <= 0) return `${before}0.${'0'.repeat(-point)}${digits}`;
      if (point >= digits.length) {
        return `${before}${digits}${'0'.repeat(point - digits.length)}`;
      }
      return `${before}${digits.slice(0, point)}.${digits.slice(point)}`;
    },
  );
}

// ---------------------------------------------------------------------
// The animation time's name in an expression, and the one free variable
// that is not a driver id (kept here, exported through evaluator.ts).
// ---------------------------------------------------------------------

export const TIME_ID = '$t';

// Driver values as the expressions read them: nested by qualified id, so
// `x_axis.motor` resolves as member access. A root-declared driver is a
// number at the top level.
export type DriverScope = Record<string, number | Record<string, number>>;

export interface EvalScope {
  /** Normalized animation time, bound as `$t`. */
  time: number;
  /** The document's drivers, in NATIVE driver units. */
  drivers?: DriverScope;
}

// ---------------------------------------------------------------------
// The shared node table (D2).
//
// A node is one of ten kinds, keyed structurally: kind, operator or
// name, and the ids of already-interned children -- so a small integer
// key string, built once per parse node and discarded unless it interns
// a NEW node, decides sharing. The table is an array of tagged records
// rather than jokenizer's parallel-arrays-of-primitives layout D2
// motivates by memory: the document sizes this change measures against
// (a few hundred nodes) make that difference immaterial, and nothing in
// this module's public surface (D12) exposes the internal shape either
// way.
// ---------------------------------------------------------------------

export type NodeId = number;

interface ConstNode { readonly kind: 'const'; readonly value: unknown; }
interface NameNode {
  readonly kind: 'name';
  readonly name: string;
  readonly parts: readonly string[];
}
interface UnaryNode {
  readonly kind: 'unary'; readonly op: string; readonly target: NodeId;
}
interface BinaryNode {
  readonly kind: 'binary'; readonly op: string;
  readonly left: NodeId; readonly right: NodeId;
}
interface CallNode {
  readonly kind: 'call'; readonly callee: NodeId; readonly args: readonly NodeId[];
}
interface MemberNode {
  readonly kind: 'member'; readonly owner: NodeId; readonly name: string;
}
interface IndexNode {
  readonly kind: 'index'; readonly owner: NodeId; readonly key: NodeId;
}
interface TernaryNode {
  readonly kind: 'ternary';
  readonly predicate: NodeId; readonly whenTrue: NodeId; readonly whenFalse: NodeId;
}
interface ArrayNode { readonly kind: 'array'; readonly items: readonly NodeId[]; }
interface ObjectNode {
  readonly kind: 'object';
  readonly names: readonly string[]; readonly values: readonly NodeId[];
}

type Node =
  | ConstNode | NameNode | UnaryNode | BinaryNode | CallNode | MemberNode
  | IndexNode | TernaryNode | ArrayNode | ObjectNode;

let table = new Map<string, NodeId>();
let nodes: Node[] = [];
// Expression TEXT -> its DAG root. The strings are the ones the loaded
// document already holds; this map adds an entry, not a copy (D8).
let expressionRoots = new Map<string, NodeId>();

function intern(key: string, build: () => Node): NodeId {
  const existing = table.get(key);
  if (existing !== undefined) return existing;
  const id = nodes.length;
  nodes.push(build());
  table.set(key, id);
  return id;
}

// A literal is keyed by its value AND its typeof, so the number `1` and
// the string `"1"` never collide, and `typeof null === 'object'` is
// special-cased so `null` collides with nothing else either. A numeric
// zero is keyed by `Object.is` so a future `-0` reaching this table by
// any route (jokenizer's own grammar never hands a Literal node a
// negative value; `-0` always parses as `Unary(-, Literal(0))`) keys
// apart from `0` rather than colliding on `String(-0) === String(0)`.
function literalKey(value: unknown): string {
  if (value === null) return 'c:null';
  if (typeof value === 'number') {
    if (Number.isNaN(value)) return 'c:number:NaN';
    if (Object.is(value, -0)) return 'c:number:-0';
    return `c:number:${String(value)}`;
  }
  return `c:${typeof value}:${String(value)}`;
}

const EXPRESSION_PREVIEW_LENGTH = 80;

function truncate(expression: string): string {
  return expression.length > EXPRESSION_PREVIEW_LENGTH
    ? `${expression.slice(0, EXPRESSION_PREVIEW_LENGTH)}…`
    : expression;
}

// D10: an expression form the DAG cannot support is refused THE MOMENT
// it is built -- which is load time, since `assertRenderable` walks
// every expression of a document through `freeVariables` before
// anything is rendered (viewer.ts). Named and quoted (truncated: a
// published expression may be megabytes) rather than left to surface
// as a bare evaluator error on some later frame.
function refuse(form: string, expression: string): never {
  throw new Error(
    `Cannot evaluate a "${form}" expression: ${truncate(expression)}`,
  );
}

// `x_axis.motor` parses as `Member{owner: Variable{x_axis}, name: motor}`.
// A Member chain rooted in a plain name folds to ONE name node (D3):
// exactly what the old `dottedName()` did for `freeVariables`, moved
// here so building and evaluating share one answer. A Member whose
// owner is not a plain name chain (`f(1).x` -- nothing the producer
// emits, but jokenizer accepts it) returns null and stays a generic
// member node.
function dottedChain(raw: Expression): string[] | null {
  if (raw.type === 'Variable') {
    return [(raw as VariableExpression).name];
  }
  if (raw.type === 'Member') {
    const member = raw as MemberExpression;
    const ownerParts = dottedChain(member.owner);
    return ownerParts === null ? null : [...ownerParts, member.name];
  }
  return null;
}

function internConst(value: unknown): NodeId {
  return intern(literalKey(value), () => ({ kind: 'const', value }));
}

function internName(parts: readonly string[]): NodeId {
  const name = parts.join('.');
  return intern(`n${name}`, () => ({ kind: 'name', name, parts }));
}

function internUnary(op: string, target: NodeId): NodeId {
  return intern(`u${op}:${target}`, () => ({ kind: 'unary', op, target }));
}

function internBinary(op: string, left: NodeId, right: NodeId): NodeId {
  return intern(`b${op}:${left},${right}`,
                () => ({ kind: 'binary', op, left, right }));
}

function internCall(callee: NodeId, args: readonly NodeId[]): NodeId {
  return intern(`f${callee}:${args.join(',')}`,
                () => ({ kind: 'call', callee, args }));
}

function internMember(owner: NodeId, name: string): NodeId {
  return intern(`m${owner}:${name}`, () => ({ kind: 'member', owner, name }));
}

function internIndex(owner: NodeId, key: NodeId): NodeId {
  return intern(`i${owner}:${key}`, () => ({ kind: 'index', owner, key }));
}

function internTernary(predicate: NodeId, whenTrue: NodeId,
                        whenFalse: NodeId): NodeId {
  return intern(`?${predicate}:${whenTrue}:${whenFalse}`,
                () => ({ kind: 'ternary', predicate, whenTrue, whenFalse }));
}

function internArray(items: readonly NodeId[]): NodeId {
  return intern(`[${items.join(',')}]`, () => ({ kind: 'array', items }));
}

function internObject(names: readonly string[],
                       values: readonly NodeId[]): NodeId {
  const key = `{${names.map((name, i) => `${name}:${values[i]}`).join(',')}}`;
  return intern(key, () => ({ kind: 'object', names, values }));
}

// The `^` -> `pow(...)` rewrite, including the rule that a leading unary
// minus stays OUTSIDE the call (`-2 ^ 2` is `-(2^2)`, as OpenSCAD binds
// it), folds into this Binary case (D4) rather than staying a separate
// tree-copying pass. Only the LEFT operand is inspected for the hoist,
// exactly as the old `powify` did.
function buildPow(raw: BinaryExpression, source: string): NodeId {
  const rawLeft = raw.left as UnaryExpression;
  const negated = rawLeft.type === 'Unary'
    && (rawLeft.operator === '-' || rawLeft.operator === '+');
  const baseRaw = negated ? rawLeft.target : raw.left;
  const baseId = build(baseRaw, source);
  const exponentId = build(raw.right, source);
  const powId = internCall(internName(['pow']), [baseId, exponentId]);
  return negated ? internUnary(rawLeft.operator, powId) : powId;
}

// The recursive builder: jokenizer's parse tree -> a DAG node id,
// interning bottom-up (D2) so every child already has an id when its
// parent is keyed. `source` is threaded through only for a refusal's
// message (D10); nothing here retains the parse tree itself once its
// root is interned.
function build(raw: Expression, source: string): NodeId {
  switch (raw.type) {
    case 'Func':
      return refuse('Func', source);
    case 'Assign':
      // Unreachable through jokenizer's own grammar (an Assign node is
      // only ever produced inside an Object literal's member list, and
      // the Object case below never calls build() on the Assign itself)
      // -- kept as the same refusal D10 names for a bare one, defensively.
      return refuse('Assign', source);

    case 'Literal':
      return internConst((raw as LiteralExpression).value);

    case 'Variable':
    case 'Member': {
      const chain = dottedChain(raw);
      if (chain !== null) {
        return internName(chain);
      }
      const member = raw as MemberExpression;
      return internMember(build(member.owner, source), member.name);
    }

    case 'Unary': {
      const unary = raw as UnaryExpression;
      return internUnary(unary.operator, build(unary.target, source));
    }

    case 'Group': {
      // jokenizer requires exactly one expression inside a Group; a
      // single one collapses transparently (D10) rather than becoming a
      // node of its own.
      const items = (raw as GroupExpression).expressions;
      if (items.length !== 1) {
        throw new Error('Group Expression can contain only one expression');
      }
      return build(items[0], source);
    }

    case 'Object': {
      const object = raw as ObjectExpression;
      const names: string[] = [];
      const values: NodeId[] = [];
      for (const member of object.members as AssignExpression[]) {
        names.push(member.name);
        values.push(build(member.right, source));
      }
      return internObject(names, values);
    }

    case 'Array': {
      const items = (raw as ArrayExpression).items
        .map((item) => build(item, source));
      return internArray(items);
    }

    case 'Binary': {
      const binary = raw as BinaryExpression;
      if (binary.operator === '^') {
        return buildPow(binary, source);
      }
      return internBinary(
        binary.operator, build(binary.left, source), build(binary.right, source),
      );
    }

    case 'Indexer': {
      const indexer = raw as IndexerExpression;
      return internIndex(
        build(indexer.owner, source), build(indexer.key, source),
      );
    }

    case 'Call': {
      const call = raw as CallExpression;
      const args = call.args.map((arg) => build(arg, source));
      return internCall(build(call.callee, source), args);
    }

    case 'Ternary': {
      const ternary = raw as TernaryExpression;
      return internTernary(
        build(ternary.predicate, source),
        build(ternary.whenTrue, source),
        build(ternary.whenFalse, source),
      );
    }

    default:
      throw new Error(`Unsupported expression type ${(raw as Expression).type}`);
  }
}

/** The expression's root node id: parses and interns it the first time,
 * reads the string map after (D12). */
export function prepare(expression: string): NodeId {
  const cached = expressionRoots.get(expression);
  if (cached !== undefined) return cached;

  // The node ceiling (D8), checked here -- at the START of a NEW
  // preparation, never mid-build -- so a table that has grown past it
  // (a long `solid develop` session republishing hundreds of document
  // versions) is dropped whole before the next expression is built,
  // rather than risking a partially-built DAG whose ids a caller
  // already holds. One document never reaches the ceiling on its own
  // (D8): the whole grasshopper clock interns 267 nodes.
  if (nodes.length >= EXPRESSION_LIMITS.nodes) {
    resetStore();
  }

  const parsed = tokenize(plainLiterals(expression));
  if (parsed === null) {
    throw new Error('Cannot evaluate an empty expression');
  }
  const rootId = build(parsed, expression);
  expressionRoots.set(expression, rootId);
  return rootId;
}

// ---------------------------------------------------------------------
// Lifetime (D8). The store is a pure cache -- emptying it costs a
// re-parse and can never cost a wrong number -- retained by a mount
// count rather than by any one viewer's identity, so one widget's
// dispose can never stall another's animation. `EXPRESSION_LIMITS` is a
// mutable exported object so a test can lower the ceiling without
// building fifty thousand nodes to reach it.
// ---------------------------------------------------------------------

export const EXPRESSION_LIMITS = { nodes: 50_000 };

let mountCount = 0;

function resetStore(): void {
  // Everything keyed by node id (D8): the intern table, the expression
  // string map, the free-variable sets, the memo's value/stamp arrays,
  // the pass counter and the remembered last scope. Node ids are handed
  // out again from zero, so a surviving stamp array would let a new
  // node inherit an old node's value; fresh arrays and a forgotten last
  // scope make the first pass after a reset an ordinary cold one.
  // `resolutions` is a separate, explicitly-reset counter (D9) and is
  // left alone here.
  table = new Map();
  nodes = [];
  expressionRoots = new Map();
  freeMemo = [];
  nodeValue = [];
  nodeStamp = [];
  passCounter = 0;
  lastScope = undefined;
}

/** One more mount is holding the shared table. */
export function retainExpressions(): void {
  mountCount += 1;
}

/** One mount is done with the shared table. Empties it once the last
 * holder releases; harmless if called without a matching retain. */
export function releaseExpressions(): void {
  if (mountCount === 0) return;
  mountCount -= 1;
  if (mountCount === 0) {
    resetStore();
  }
}

// ---------------------------------------------------------------------
// Metrics (D9): a test-visible count of subexpression resolutions and
// of the shared table's size, so the win this change makes is asserted
// as work performed rather than as elapsed time. Not a host capability
// (D9, tasks.md 5.1): it is a widget-source export for the widget's own
// tests, never on the mount handle, so the viewer API version does not
// move for it.
// ---------------------------------------------------------------------

let resolutions = 0;

export function expressionMetrics(): { nodes: number; resolutions: number } {
  return { nodes: nodes.length, resolutions };
}

export function resetExpressionMetrics(): void {
  resolutions = 0;
}

// ---------------------------------------------------------------------
// The OpenSCAD math context (moved here from evaluator.ts, which keeps
// re-exporting `TIME_ID`/`EvalScope`/`DriverScope` and its own
// `evalExpr`/`freeVariables` -- this is where those names are actually
// consumed now, in name resolution (D5) below).
// ---------------------------------------------------------------------

// Math's built-in properties are non-enumerable, so a plain
// Object.assign({}, Math) would copy nothing -- walk them explicitly.
const context: Record<string, unknown> = {};
for (const name of Object.getOwnPropertyNames(Math)) {
  context[name] = (Math as unknown as Record<string, unknown>)[name];
}

// OpenSCAD names and semantics that differ from JS Math.
context.ln = Math.log;
context.log = (base: number, value: number) => Math.log(value) / Math.log(base);
context.mod = (a: number, b: number) => a % b;
context.sin = (degrees: number) => Math.sin((degrees * Math.PI) / 180);
context.cos = (degrees: number) => Math.cos((degrees * Math.PI) / 180);
context.tan = (degrees: number) => Math.tan((degrees * Math.PI) / 180);
context.asin = (value: number) => (Math.asin(value) * 180) / Math.PI;
context.acos = (value: number) => (Math.acos(value) * 180) / Math.PI;
context.atan = (value: number) => (Math.atan(value) * 180) / Math.PI;
context.atan2 = (y: number, x: number) => (Math.atan2(y, x) * 180) / Math.PI;

// ---------------------------------------------------------------------
// Name resolution (D5): the first part of a dotted (or bare) name is
// resolved in the order the old spread scope established -- `$t`, then
// the driver map (`in`-checked, so a driver whose value is `0` is
// found), then the OpenSCAD context, else `undefined`. Every further
// part reproduces jokenizer's `readVar` in the shape it has: a falsy
// owner (including an absent one) yields `undefined`, a truthy
// primitive owner throws the identical native `TypeError`, an object
// without the key yields `undefined`, and one with it yields the value.
// ---------------------------------------------------------------------

/** One further step of a dotted chain, or of a generic Member access:
 * jokenizer's `readVar` for a single candidate scope, verbatim. */
function readMember(owner: unknown, part: string): unknown {
  if (!owner) return undefined;
  // The `in` operator throws its own native TypeError for a truthy
  // primitive owner (a number, a string, a boolean) -- deliberately
  // not caught or reworded here (D5).
  return part in (owner as object)
    ? (owner as Record<string, unknown>)[part] : undefined;
}

function resolveName(parts: readonly string[], scope: EvalScope): unknown {
  const [first, ...rest] = parts;
  let value: unknown;
  if (first === TIME_ID) {
    value = scope.time;
  } else if (scope.drivers !== undefined && first in scope.drivers) {
    value = (scope.drivers as Record<string, unknown>)[first];
  } else if (first in context) {
    value = context[first];
  } else {
    value = undefined;
  }
  for (const part of rest) {
    value = readMember(value, part);
  }
  return value;
}

function applyUnary(op: string, value: unknown): unknown {
  switch (op) {
    case '!': return !value;
    case '+': return +(value as number);
    // -1 * v, not -v (D1): jokenizer's own unary rule, verbatim.
    case '-': return -1 * (value as number);
    case '~': return ~(value as number);
    default: throw new Error(`Unknown unary operator ${op}`);
  }
}

function applyBinary(op: string, left: unknown, right: unknown): unknown {
  /* eslint-disable eqeqeq */
  switch (op) {
    case '|': return (left as number) | (right as number);
    case '^': return (left as number) ^ (right as number);
    case '&': return (left as number) & (right as number);
    case '===': return left === right;
    case '!==': return left !== right;
    case '==': return left == right;
    case '!=': return left != right;
    case '<<': return (left as number) << (right as number);
    case '>>>': return (left as number) >>> (right as number);
    case '>>': return (left as number) >> (right as number);
    case '<=': return (left as number) <= (right as number);
    case '>=': return (left as number) >= (right as number);
    case '<': return (left as number) < (right as number);
    case '>': return (left as number) > (right as number);
    case '+': return (left as number) + (right as number);
    case '-': return (left as number) - (right as number);
    case '*': return (left as number) * (right as number);
    case '/': return (left as number) / (right as number);
    case '%': return (left as number) % (right as number);
    default: throw new Error(`Unknown binary operator ${op}`);
  }
  /* eslint-enable eqeqeq */
}

// ---------------------------------------------------------------------
// The evaluation pass (D6). A pass is a set of scope VALUES, not a
// syntactic event: `valueOf` is handed one scope object per
// `tree.update` walk (`viewer.ts`'s `scope()`), so the identity fast
// path is the common case within one walk, and the value comparison
// behind it is what makes the SECOND walk of a playing frame -- today's
// `setTime` update and the animation loop's update, two different scope
// OBJECTS carrying the same numbers -- free.
//
// The driver maps are compared RECURSIVELY, because
// `DriverStore.scope()` builds a fresh nested object for every
// qualified owner on every call: two scopes carrying identical values
// share no nested object, so a comparison that stopped at the owner
// would call every qualified-driver document changed on every call.
// ---------------------------------------------------------------------

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function mapsEqual(a: Record<string, unknown>, b: Record<string, unknown>): boolean {
  const aKeys = Object.keys(a);
  if (aKeys.length !== Object.keys(b).length) return false;
  for (const key of aKeys) {
    if (!(key in b)) return false;
    const av = a[key];
    const bv = b[key];
    if (typeof av === 'number' && typeof bv === 'number') {
      if (!Object.is(av, bv)) return false;
    } else if (isPlainObject(av) && isPlainObject(bv)) {
      if (!mapsEqual(av, bv)) return false;
    } else {
      // Anything else -- a function, a string, null, undefined, an
      // array, or a type mismatch between the two -- counts as
      // changed, so an unexpected shape costs a recomputation and
      // never a stale number.
      return false;
    }
  }
  return true;
}

function scopesEqual(a: EvalScope, b: EvalScope): boolean {
  return Object.is(a.time, b.time)
    && mapsEqual(a.drivers ?? {}, b.drivers ?? {});
}

let passCounter = 0;
let lastScope: EvalScope | undefined;
let nodeValue: unknown[] = [];
let nodeStamp: number[] = [];

function ensurePass(scope: EvalScope): void {
  // The identity fast path, checked on EVERY valueOf call (D6): true
  // for every evalExpr call of one tree.update walk.
  if (scope === lastScope) return;
  if (lastScope !== undefined && scopesEqual(scope, lastScope)) {
    lastScope = scope;
    return;
  }
  passCounter += 1;
  lastScope = scope;
}

function compute(id: NodeId, scope: EvalScope): unknown {
  const node = nodes[id];
  switch (node.kind) {
    case 'const':
      return node.value;
    case 'name':
      return resolveName(node.parts, scope);
    case 'unary':
      return applyUnary(node.op, valueOf(node.target, scope));
    case 'binary': {
      // && and || short-circuit their right side (D1): the right node
      // is not even visited, let alone resolved and stamped, unless it
      // is needed.
      if (node.op === '&&') {
        const left = valueOf(node.left, scope);
        return left ? valueOf(node.right, scope) : left;
      }
      if (node.op === '||') {
        const left = valueOf(node.left, scope);
        return left || valueOf(node.right, scope);
      }
      return applyBinary(node.op, valueOf(node.left, scope), valueOf(node.right, scope));
    }
    case 'call': {
      const callee = valueOf(node.callee, scope) as (...args: unknown[]) => unknown;
      const args = node.args.map((arg) => valueOf(arg, scope));
      return callee(...args);
    }
    case 'member':
      return readMember(valueOf(node.owner, scope), node.name);
    case 'index': {
      const owner = valueOf(node.owner, scope);
      const key = valueOf(node.key, scope) as PropertyKey;
      return owner != null ? (owner as Record<PropertyKey, unknown>)[key] : null;
    }
    case 'ternary':
      return valueOf(node.predicate, scope)
        ? valueOf(node.whenTrue, scope) : valueOf(node.whenFalse, scope);
    case 'array':
      return node.items.map((item) => valueOf(item, scope));
    case 'object': {
      const result: Record<string, unknown> = {};
      node.names.forEach((name, i) => {
        result[name] = valueOf(node.values[i], scope);
      });
      return result;
    }
    default:
      throw new Error(`Unsupported node kind ${(node as Node).kind}`);
  }
}

/** The memoized DAG walk (D6). A node is computed when its STAMP is not
 * the current pass's -- never the value, so a node whose value is
 * `undefined` or `NaN` memoizes correctly. */
export function valueOf(id: NodeId, scope: EvalScope): unknown {
  ensurePass(scope);
  if (nodeStamp[id] === passCounter) return nodeValue[id];
  const result = compute(id, scope);
  nodeValue[id] = result;
  nodeStamp[id] = passCounter;
  resolutions += 1;
  return result;
}

// ---------------------------------------------------------------------
// Free variables (D11): computed once per NODE and memoized beside it,
// the same three rules `freeVariables` always had -- a name node
// contributes its dotted id, a call node the union of its ARGS only
// (never its callee), a generic member node its owner's set -- now read
// off the DAG instead of a fresh walk of the whole parse tree. Every
// other node kind's set is the union of its children's, which is
// exactly what the old walk's generic fallback did for them too.
// ---------------------------------------------------------------------

const EMPTY_NAMES: ReadonlySet<string> = new Set();
let freeMemo: (ReadonlySet<string> | undefined)[] = [];

function union(sets: readonly ReadonlySet<string>[]): ReadonlySet<string> {
  if (sets.length === 0) return EMPTY_NAMES;
  if (sets.length === 1) return sets[0];
  const found = new Set<string>();
  for (const set of sets) {
    for (const name of set) found.add(name);
  }
  return found;
}

function computeFree(id: NodeId): ReadonlySet<string> {
  const node = nodes[id];
  switch (node.kind) {
    case 'const':
      return EMPTY_NAMES;
    case 'name':
      return new Set([node.name]);
    case 'unary':
      return freeNames(node.target);
    case 'binary':
      return union([freeNames(node.left), freeNames(node.right)]);
    case 'call':
      // The callee is never a variable (D11): only the arguments.
      return union(node.args.map((arg) => freeNames(arg)));
    case 'member':
      return freeNames(node.owner);
    case 'index':
      return union([freeNames(node.owner), freeNames(node.key)]);
    case 'ternary':
      return union([
        freeNames(node.predicate), freeNames(node.whenTrue), freeNames(node.whenFalse),
      ]);
    case 'array':
      return union(node.items.map((item) => freeNames(item)));
    case 'object':
      return union(node.values.map((item) => freeNames(item)));
    default:
      throw new Error(`Unsupported node kind ${(node as Node).kind}`);
  }
}

/** `expression`'s free-variable set, off the DAG (D11): computed once
 * per node and memoized beside it. */
export function freeNames(id: NodeId): ReadonlySet<string> {
  const cached = freeMemo[id];
  if (cached !== undefined) return cached;
  const result = computeFree(id);
  freeMemo[id] = result;
  return result;
}
