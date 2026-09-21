/*
 * machinome-viewer - the browser viewer for machinome models
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
  /** OpenSpec `read-expression-bindings`, design D1-D3: a version-4
   * document's shared-subexpression table, name -> the interned root of
   * that entry's expression. Document-scoped (`bindings.ts` builds it,
   * never a module-level map here), so it travels in the scope exactly
   * as driver values do. Resolved between `$t` and the driver map (D1),
   * and part of the pass comparison (D3): the name node for one binding
   * name is one node id for the whole page, so two documents' tables
   * must never be allowed to share its memoized value. */
  bindings?: ReadonlyMap<string, NodeId>;
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
  // (a long `machinome develop` session republishing hundreds of document
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

// D4: a `BindingTable` (bindings.ts) holds node ids OUTSIDE this store,
// prepared once at load. A reset hands ids out again from zero, so a
// held map built before one would name a reallocated node -- or worse,
// nothing at all. `storeGeneration` is what lets a holder notice: it
// rises on every reset and on nothing else, so re-preparing is a single
// integer comparison per pass and a real re-parse only after a genuine
// reset.
let storeGeneration = 0;

/** The current store generation. Rises by exactly one on every
 * `resetStore()` and is unchanged otherwise (D4). */
export function expressionGeneration(): number {
  return storeGeneration;
}

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
  storeGeneration += 1;
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

// `machinome.math.sign` is `(x > 0) - (x < 0)`: which side of zero its
// argument is on, with no branch. `Math.sign` agrees everywhere except
// at negative zero, where it answers -0 and the producer answers 0 --
// and the run reads the branch of a `sign` jump off this same formula
// (design §8, §15 finding 3), so one definition serves both.
context.sign = (value: number) => (value > 0 ? 1 : 0) - (value < 0 ? 1 : 0);

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
  } else if (scope.bindings !== undefined && scope.bindings.has(first)) {
    // A binding resolves BEFORE a driver id (D1, the framework's own
    // rule): a name that is both is a binding, never reported as an
    // undeclared driver. Its root is a node like any other -- this
    // recurses into the SAME memoized walk, so a binding read by many
    // operations costs one resolution per pass however many reach it.
    value = valueOf(scope.bindings.get(first)!, scope);
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

// The binding map (D3): compared identity-first, then by size and every
// name's node id. An absent map counts as an empty one, so a version 1-3
// scope with no `bindings` compares exactly as it does today. This is
// NOT `mapsEqual` -- that compares nested VALUES for the driver map;
// here two node ids are equal by `!==`, and a `Map` rather than a plain
// object is what `bindings.ts` and every call site already build.
//
// Exported: `tree.ts`'s reconcile (D6) needs the SAME comparison to
// decide whether a republished document's table differs from the one a
// node already holds -- reusing it here is what makes "difference" mean
// one thing on both sides of the pass boundary, rather than two
// independently-maintained notions that could drift apart.
export function bindingRootsEqual(a?: ReadonlyMap<string, NodeId>,
                                   b?: ReadonlyMap<string, NodeId>): boolean {
  if (a === b) return true;
  const aSize = a?.size ?? 0;
  const bSize = b?.size ?? 0;
  if (aSize !== bSize) return false;
  if (a === undefined) return true; // both empty (b is undefined too, or size 0)
  for (const [name, id] of a) {
    if (b!.get(name) !== id) return false;
  }
  return true;
}

function scopesEqual(a: EvalScope, b: EvalScope): boolean {
  return Object.is(a.time, b.time)
    && mapsEqual(a.drivers ?? {}, b.drivers ?? {})
    && bindingRootsEqual(a.bindings, b.bindings);
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

// ---------------------------------------------------------------------
// A READ-ONLY STRUCTURAL VIEW of the store (design D1.5 of
// `execute-the-selection`).
//
// The block's FOLD needs to know an expression's SHAPE -- which node is
// a multiplication, which child is the literal zero -- and not its
// value. It is a view of the store this module already holds, never a
// second parser and never a tree to build: a copy would drift from the
// one the evaluator uses at the first correction either received.
//
// `children` are exactly the ids `computeFree` walks, in that order, so
// a generic node's names are the union of its children's.
// ---------------------------------------------------------------------

export interface ExpressionStructure {
  /** `const`, `name`, `unary`, `binary`, `call`, `member`, `index`,
   * `ternary`, `array` or `object`. */
  readonly kind: string;
  /** A unary's or a binary's operator; `null` for every other kind. */
  readonly op: string | null;
  /** A `const` node's literal value; `undefined` for every other kind. */
  readonly value: unknown;
  /** A `name` node's whole dotted name; `null` for every other kind. */
  readonly name: string | null;
  readonly children: readonly NodeId[];
}

export function structureOf(id: NodeId): ExpressionStructure {
  const node = nodes[id];
  const blank = { op: null, value: undefined, name: null } as const;
  switch (node.kind) {
    case 'const':
      return { ...blank, kind: 'const', value: node.value, children: [] };
    case 'name':
      return { ...blank, kind: 'name', name: node.name, children: [] };
    case 'unary':
      return { ...blank, kind: 'unary', op: node.op, children: [node.target] };
    case 'binary':
      return {
        ...blank, kind: 'binary', op: node.op,
        children: [node.left, node.right],
      };
    case 'call':
      // The callee is never a variable (D11): only the arguments.
      return { ...blank, kind: 'call', children: node.args };
    case 'member':
      return { ...blank, kind: 'member', children: [node.owner] };
    case 'index':
      return { ...blank, kind: 'index', children: [node.owner, node.key] };
    case 'ternary':
      return {
        ...blank, kind: 'ternary',
        children: [node.predicate, node.whenTrue, node.whenFalse],
      };
    case 'array':
      return { ...blank, kind: 'array', children: node.items };
    case 'object':
      return { ...blank, kind: 'object', children: node.values };
    default:
      throw new Error(`Unsupported node kind ${(node as Node).kind}`);
  }
}

/** Prove a placement scalar is a * coordinate + b. This is structural,
 * not a sampling test: nonlinear expressions cannot masquerade as a joint
 * by agreeing at a few positions. Shared bindings use the same DAG. */
export function affineCoordinate(expression: string, coordinate: string,
                                 bindings?: ReadonlyMap<string, NodeId>):
  readonly [number, number] | null {
  type Affine = readonly [number, number];
  const memo = new Map<NodeId, Affine | null>();
  const visit = (id: NodeId): Affine | null => {
    if (memo.has(id)) return memo.get(id)!;
    memo.set(id, null); // Also refuses a cyclic binding supplied by a caller.
    const node = nodes[id];
    let result: Affine | null = null;
    if (node.kind === 'const' && typeof node.value === 'number') {
      result = [0, node.value];
    } else if (node.kind === 'name') {
      const binding = bindings?.get(node.name);
      result = binding === undefined
        ? (node.name === coordinate ? [1, 0] : null) : visit(binding);
    } else if (node.kind === 'unary' && ['+', '-'].includes(node.op)) {
      const a = visit(node.target);
      const sign = node.op === '-' ? -1 : 1;
      if (a !== null) result = [sign * a[0], sign * a[1]];
    } else if (node.kind === 'binary') {
      const a = visit(node.left);
      const b = visit(node.right);
      if (a !== null && b !== null) {
        if (node.op === '+') result = [a[0] + b[0], a[1] + b[1]];
        if (node.op === '-') result = [a[0] - b[0], a[1] - b[1]];
        if (node.op === '*' && (a[0] === 0 || b[0] === 0)) {
          result = [a[0] * b[1] + b[0] * a[1], a[1] * b[1]];
        }
        if (node.op === '/' && b[0] === 0 && b[1] !== 0) {
          result = [a[0] / b[1], a[1] / b[1]];
        }
      }
    }
    if (result !== null && !result.every(Number.isFinite)) result = null;
    memo.set(id, result);
    return result;
  };
  return visit(prepare(expression));
}

// ---------------------------------------------------------------------
// A quantity FOLLOWED along one tick's path (design D1-D9; ADR-060,
// mirroring machinome's ADR-124's `_PathValue`). The part of an
// expression that reads no name the step MOVES cannot change over one
// piece, so it is computed ONCE and read back; only the moving cone is
// walked per point. `PathValue` is a VIEW of the SAME interned DAG
// `valueOf` walks -- the same `applyUnary`/`applyBinary`/`readMember`
// and the same OpenSCAD `context` -- so bit-identity is a property of
// the construction rather than a test result (D1). It mints no node and
// holds no expression text.
// ---------------------------------------------------------------------

/** A node shape this path evaluator refuses rather than guesses (D9): a
 * generic member, an index, a ternary, an array, an object literal, or a
 * short-circuit `&&`/`||`. None occurs in any published document this
 * viewer executes today (verified: zero occurrences); a document that
 * ever did carry one falls back to `evaluateExpression` through this
 * error. */
export class UnsupportedPathNode extends Error {}

export class PathValue {
  /** The moving cone, in the WHOLE graph's postorder, decided the first
   * time this quantity is bound (D2). `null` until then. */
  private order: NodeId[] | null = null;

  /** Every node's value on the CURRENT piece that does not move (D2). */
  private readonly standing = new Map<NodeId, unknown>();

  /** Scratch, valid only for the duration of one `bind`/`at` call. */
  private readonly computed = new Map<NodeId, unknown>();

  /** The whole graph's postorder, decided once and reused by every later
   * piece (D2). */
  private walked: NodeId[] = [];

  constructor(private readonly root: NodeId,
              private readonly moving: ReadonlySet<string>,
              private readonly bindings?: ReadonlyMap<string, NodeId>) {}

  private childrenOf(id: NodeId): readonly NodeId[] {
    const node = nodes[id];
    switch (node.kind) {
      case 'const': return [];
      case 'name': {
        if (node.parts[0] === TIME_ID) return [];
        const binding = this.bindings?.get(node.parts[0]);
        // D3: a name that is a binding has the binding's root as its ONE
        // child, so it moves exactly when the binding's own expression
        // does.
        return binding === undefined ? [] : [binding];
      }
      case 'unary': return [node.target];
      case 'binary': return [node.left, node.right];
      case 'call': return [node.callee, ...node.args];
      case 'member': return [node.owner];
      case 'index': return [node.owner, node.key];
      case 'ternary': return [node.predicate, node.whenTrue, node.whenFalse];
      case 'array': return node.items;
      case 'object': return node.values;
      default: return [];
    }
  }

  private postorder(): NodeId[] {
    const out: NodeId[] = [];
    const seen = new Set<NodeId>();
    const stack: [NodeId, boolean][] = [[this.root, false]];
    while (stack.length > 0) {
      const [id, expanded] = stack.pop()!;
      if (expanded) { out.push(id); continue; }
      if (seen.has(id)) continue;
      seen.add(id);
      stack.push([id, true]);
      for (const child of this.childrenOf(id)) stack.push([child, false]);
    }
    return out;
  }

  /** Whether a LEAF name node (no binding, not `$t`) moves: the run's own
   * statement (D5), read off the FLAT bank's key space -- the same id
   * `valueAt` below resolves it by. */
  private movesByName(id: NodeId): boolean {
    const node = nodes[id];
    if (node.kind !== 'name') return false;
    return this.moving.has(node.name);
  }

  private read(id: NodeId): unknown {
    if (this.computed.has(id)) return this.computed.get(id);
    return this.standing.get(id);
  }

  /** One node's value at one point (D1, D4). Resolution order for a
   * `name` node mirrors `resolveName` exactly (review amendment, tasks.md
   * 1.4): `$t` first, then a binding (walked INTO, D3), then the WHOLE
   * dotted id read from the run's flat bank (D4), then -- absent from the
   * bank -- a single-part name's fallback to the OpenSCAD context, or a
   * multi-part name's fallback through the SAME context-then-`readMember`
   * chain `resolveName` takes; a multi-part name the bank does not hold
   * and whose first part resolves through none of the above is the one
   * shape flat and nested resolution could disagree on (D9 point 0) and
   * is REFUSED rather than guessed. */
  private valueAt(id: NodeId, values: Record<string, number>): unknown {
    const node = nodes[id];
    switch (node.kind) {
      case 'const':
        return node.value;
      case 'name': {
        const first = node.parts[0];
        if (first === TIME_ID) return 0;
        const binding = this.bindings?.get(first);
        if (binding !== undefined) {
          let value = this.read(binding);
          for (let i = 1; i < node.parts.length; i += 1) {
            value = readMember(value, node.parts[i]);
          }
          return value;
        }
        if (Object.prototype.hasOwnProperty.call(values, node.name)) {
          return values[node.name];
        }
        if (node.parts.length === 1) {
          return first in context ? context[first] : undefined;
        }
        if (first in context) {
          let value: unknown = context[first];
          for (let i = 1; i < node.parts.length; i += 1) {
            value = readMember(value, node.parts[i]);
          }
          return value;
        }
        throw new UnsupportedPathNode(
          `PathValue: the multi-part name "${node.name}" is neither in the `
          + 'run\'s bank nor resolvable through $t, a binding or the '
          + 'OpenSCAD context -- the one shape flat and nested resolution '
          + 'could disagree on.');
      }
      case 'unary':
        return applyUnary(node.op, this.read(node.target));
      case 'binary':
        if (node.op === '&&' || node.op === '||') {
          throw new UnsupportedPathNode(
            `PathValue: a short-circuit "${node.op}"`);
        }
        return applyBinary(node.op, this.read(node.left), this.read(node.right));
      case 'call': {
        const callee = this.read(node.callee) as (...a: unknown[]) => unknown;
        return callee(...node.args.map((arg) => this.read(arg)));
      }
      case 'member':
        throw new UnsupportedPathNode('PathValue: a generic member node');
      case 'index':
        throw new UnsupportedPathNode('PathValue: an index node');
      case 'ternary':
        throw new UnsupportedPathNode('PathValue: a ternary node');
      case 'array':
        throw new UnsupportedPathNode('PathValue: an array node');
      case 'object':
        throw new UnsupportedPathNode('PathValue: an object node');
      default:
        throw new UnsupportedPathNode(
          `PathValue: unsupported node kind ${(node as Node).kind}`);
    }
  }

  /** A new piece: recompute the standing part, deciding which nodes move
   * the FIRST time, in that same walk (D2). Every node computed charges
   * the resolution probe (D8). */
  bind(values: Record<string, number>): unknown {
    const deciding = this.order === null;
    const walk = deciding ? this.postorder() : this.walked;
    if (deciding) this.walked = walk;
    const moves = new Map<NodeId, boolean>();
    const order: NodeId[] = [];
    this.computed.clear();
    this.standing.clear();
    const known = deciding ? null : new Set(this.order!);
    for (const id of walk) {
      const value = this.valueAt(id, values);
      resolutions += 1;
      this.computed.set(id, value);
      if (deciding) {
        const node = nodes[id];
        const children = this.childrenOf(id);
        const nodeMoves = node.kind === 'name' && children.length === 0
          ? this.movesByName(id)
          : children.some((child) => moves.get(child) === true);
        moves.set(id, nodeMoves);
        if (nodeMoves) order.push(id); else this.standing.set(id, value);
      } else if (!known!.has(id)) {
        this.standing.set(id, value);
      }
    }
    if (deciding) this.order = order;
    const found = this.computed.get(this.root);
    this.computed.clear();
    return found;
  }

  /** A LATER point of the SAME piece: only the moving cone (D2). Every
   * node computed charges the resolution probe (D8); a quantity whose
   * whole expression stands charges nothing. */
  at(values: Record<string, number>): unknown {
    const order = this.order;
    if (order === null) {
      throw new Error('PathValue.at() called before bind()');
    }
    if (order.length === 0) return this.standing.get(this.root);
    this.computed.clear();
    for (const id of order) {
      const value = this.valueAt(id, values);
      resolutions += 1;
      this.computed.set(id, value);
    }
    const found = this.computed.get(this.root);
    this.computed.clear();
    return found;
  }

  /** The moving cone's size, or `-1` before the first `bind` (test-only,
   * D8's census). */
  movingNodes(): number { return this.order === null ? -1 : this.order.length; }

  /** The whole graph's node count (test-only, D8's census). */
  totalNodes(): number { return this.walked.length; }
}

/** The names a tick's path MOVES (D5): a source whose increment over the
 * step is non-zero. Never a branch placeholder -- a constant of its piece
 * by construction, and substituted into `values` per piece, never listed
 * in `delta`. */
export function movingNames(delta: Record<string, number>): ReadonlySet<string> {
  const found = new Set<string>();
  for (const name in delta) {
    if (!Object.prototype.hasOwnProperty.call(delta, name)) continue;
    if (delta[name]) found.add(name);
  }
  return found;
}

// ---------------------------------------------------------------------
// The SHAPE of a quantity followed along a tick's path, and the KINKS
// that cut it (openspec `solve-at-the-kink`, design D1-D2; machinome's
// ADR-123 `_shape_of`, `_kink_level` and `_KinkCuts`, mirrored over this
// interned DAG).
//
// The producer publishes one two-valued flag per followed quantity --
// affine in its sources, or not -- and its own classification is
// THREE-valued: a quantity built over `abs`, `min` or `max` is PIECEWISE
// AFFINE, affine between the points where it changes which operand it
// returns. That classification is STRUCTURAL: it reads the expression
// tree and nothing else. This viewer holds the same expressions, so it
// computes the same shape from the same text, and no document field is
// needed for it.
//
// A view of the SAME store `valueOf` walks: it mints no node and holds
// no expression text, exactly as `PathValue` does.
// ---------------------------------------------------------------------

/** `'constant'`, `'affine'`, `'kinked'`, or `null` for unclassified --
 * which goes on being sampled and bisected. */
export type PathShape = 'constant' | 'affine' | 'kinked' | null;

/** The CONTINUOUS SELECTIONS of the vocabulary: each returns one of its
 * operands exactly and is continuous where the operands meet
 * (`_KINK_CALLS`). */
const KINK_CALLS: ReadonlySet<string> = new Set(['abs', 'min', 'max']);

/** Constant, affine or kinked -- a shape an affine combination may be
 * built over (`_MOVABLE`). */
function movable(shape: PathShape): boolean {
  return shape === 'constant' || shape === 'affine' || shape === 'kinked';
}

/** An affine combination of movable operands is kinked exactly when one
 * of them is (`_joined`). */
function joined(...parts: PathShape[]): PathShape {
  return parts.includes('kinked') ? 'kinked' : 'affine';
}

/** A call's callee NAME, or `null` where the callee is not a plain name
 * (`structureOf` deliberately reports a call's arguments only, because
 * a callee is never a free variable). */
export function calleeName(id: NodeId): string | null {
  const node = nodes[id];
  if (node.kind !== 'call') return null;
  const callee = nodes[node.callee];
  return callee.kind === 'name' ? callee.name : null;
}

/** The children a STRUCTURAL walk follows: a binding name has the
 * binding's root as its ONE child, exactly as `PathValue.childrenOf`
 * and `foldedNames` already walk one, and a call's callee is not a
 * child at all. */
function shapeChildren(id: NodeId,
                       bindings?: ReadonlyMap<string, NodeId>): readonly NodeId[] {
  const node = nodes[id];
  switch (node.kind) {
    case 'const': return [];
    case 'name': {
      if (node.parts[0] === TIME_ID) return [];
      const binding = bindings?.get(node.parts[0]);
      return binding === undefined ? [] : [binding];
    }
    case 'unary': return [node.target];
    case 'binary': return [node.left, node.right];
    case 'call': return node.args;
    case 'member': return [node.owner];
    case 'index': return [node.owner, node.key];
    case 'ternary': return [node.predicate, node.whenTrue, node.whenFalse];
    case 'array': return node.items;
    case 'object': return node.values;
    default: return [];
  }
}

/** `root`'s shape in the sources along the path (`_shape_of`).
 *
 * `constants` are the names that are CONSTANT on the stretch being cut
 * -- a jump plan's own branch placeholders, which the producer spells
 * `$j…` and the document spells by the jump's own name. `bindings` is
 * the document's shared-subexpression table, walked INTO: a name it
 * defines takes the shape of that table's own expression.
 *
 * Conservative by construction: anything not listed -- another call, a
 * power, a product of two moving operands, a moving divisor, a
 * comparison -- is unclassified and goes on being searched, which is why
 * `max(0, sin(x))` stays searched although one of its pieces is
 * straight. `$t` is unclassified: no published running expression names
 * it, and guessing would be a silent divergence from the producer, whose
 * graph has no such node at all. A cyclic bindings table classifies as
 * unclassified rather than recursing (the loader refuses one anyway). */
export function shapeOf(root: NodeId, constants: ReadonlySet<string>,
                        bindings?: ReadonlyMap<string, NodeId>): PathShape {
  const memo = new Map<NodeId, PathShape>();
  const visit = (id: NodeId): PathShape => {
    const cached = memo.get(id);
    if (cached !== undefined) return cached;
    memo.set(id, null);
    const node = nodes[id];
    let found: PathShape = null;
    if (node.kind === 'const') {
      found = typeof node.value === 'number' ? 'constant' : null;
    } else if (node.kind === 'name') {
      if (node.parts[0] === TIME_ID) {
        found = null;
      } else {
        const binding = bindings?.get(node.parts[0]);
        if (binding !== undefined) {
          // A DOTTED name whose head is a binding is a member access on
          // the binding's value, which this classification does not read.
          found = node.parts.length === 1 ? visit(binding) : null;
        } else if (constants.has(node.name)) {
          found = 'constant';
        } else {
          found = 'affine';
        }
      }
    } else {
      const children = shapeChildren(id, bindings).map(visit);
      if (children.length === 0) {
        // `if not node.children: return None` -- a call with no argument
        // carries nothing of the path.
        found = null;
      } else if (children.every((child) => child === 'constant')) {
        found = 'constant';
      } else if (node.kind === 'call') {
        // A kink is the ONLY call that classifies, and it classifies by
        // its OPERANDS, never by its own node type.
        const callee = calleeName(id);
        found = callee !== null && KINK_CALLS.has(callee)
          && children.every(movable) ? 'kinked' : null;
      } else if (node.kind === 'unary') {
        found = (node.op === '-' || node.op === '+')
          && (children[0] === 'affine' || children[0] === 'kinked')
          ? children[0] : null;
      } else if (node.kind === 'binary') {
        const [left, right] = children;
        if (node.op === '+' || node.op === '-') {
          found = movable(left) && movable(right) ? joined(left, right) : null;
        } else if (node.op === '*') {
          if (left === 'constant' && movable(right)) found = joined(right);
          else if (right === 'constant' && movable(left)) found = joined(left);
          else found = null;
        } else if (node.op === '/') {
          found = right === 'constant' && movable(left) ? joined(left) : null;
        } else {
          found = null;
        }
      }
    }
    memo.set(id, found);
    return found;
  };
  return visit(root);
}

/** A kink node's LEVEL QUANTITY -- the continuous quantity whose one
 * surface, at zero, is where the node changes which operand it returns:
 * `x` for `abs(x)`, and `a - b` for `min(a, b)` and `max(a, b)`.
 *
 * Held as the two OPERAND node ids, never a minted node: the producer
 * mints a fresh `a - b`, and evaluating `a` minus `b` over the same DAG
 * is the same IEEE subtraction of the same two operands while leaving
 * the interning table free of nodes no expression names. */
export interface KinkLevel {
  readonly a: NodeId;
  /** `null` for `abs`, whose level is its argument alone. */
  readonly b: NodeId | null;
}

/** `root`'s kink nodes in the expression's own POSTORDER, so a kink
 * nested inside another's level is cut FIRST (`_KinkCuts.__init__`).
 * Walks INTO the bindings table exactly as `shapeOf` does. */
export function kinkLevels(root: NodeId,
                           bindings?: ReadonlyMap<string, NodeId>):
readonly KinkLevel[] {
  const found: KinkLevel[] = [];
  const seen = new Set<NodeId>();
  const stack: [NodeId, boolean][] = [[root, false]];
  while (stack.length > 0) {
    const [id, expanded] = stack.pop()!;
    if (expanded) {
      const callee = calleeName(id);
      if (callee !== null && KINK_CALLS.has(callee)) {
        const node = nodes[id] as CallNode;
        found.push(callee === 'abs'
          ? { a: node.args[0], b: null }
          : { a: node.args[0], b: node.args[1] });
      }
      continue;
    }
    if (seen.has(id)) continue;
    seen.add(id);
    stack.push([id, true]);
    for (const child of shapeChildren(id, bindings)) stack.push([child, false]);
  }
  return found;
}
