/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
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
import { ConvexProfile, profileOverlap } from './run/profiles';

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
  /** Loaded-program-owned finite profiles, never a page-global registry. */
  profiles?: readonly ConvexProfile[];
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
let peakNodes = 0;
// Expression TEXT -> its DAG root. The strings are the ones the loaded
// document already holds; this map adds an entry, not a copy (D8).
let expressionRoots = new Map<string, NodeId>();

function intern(key: string, build: () => Node): NodeId {
  const existing = table.get(key);
  if (existing !== undefined) return existing;
  const id = nodes.length;
  nodes.push(build());
  peakNodes = Math.max(peakNodes, nodes.length);
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
  return withExpressions(() => {
    const parsed = tokenize(plainLiterals(expression));
    if (parsed === null) {
      throw new Error('Cannot evaluate an empty expression');
    }
    const rootId = build(parsed, expression);
    expressionRoots.set(expression, rootId);
    return rootId;
  });
}

// ---------------------------------------------------------------------
// Lifetime (D8). The store is a pure cache -- emptying it costs a
// re-parse and can never cost a wrong number -- retained by a mount
// count rather than by any one viewer's identity, so one widget's
// dispose can never stall another's animation. `EXPRESSION_LIMITS` is a
// mutable exported object so a test can lower the ceiling without
// building fifty thousand nodes to reach it.
// ---------------------------------------------------------------------

// ADR-043's finite headroom for OBSOLETE expression state, never a limit
// on the working set of what is loaded (OpenSpec
// `keep-a-live-model-parsed`, design Decision 1). The store is reclaimed
// when it holds `nodes` or more, and only where obsolete state is
// created: at the start of an outermost document load
// (`withDocumentLoad`), at the end of a refused load, when a validated
// document is settled installed or abandoned (`DocumentSettlement`), and
// at every viewer's disposal (`releaseExpressions`), the last one
// emptying the store whatever it holds. Ordinary operations -- poses,
// drawn frames, clocked requests, run ticks, tree updates -- never
// reclaim, so a loaded graph of any size is reused from one operation to
// the next. `everyOperation` is a source-only switch for the widget's
// own tests: when true, every outermost operation also empties the store
// at its start once it holds `nodes` or more, as before this change.
export const EXPRESSION_LIMITS = { nodes: 125_000, everyOperation: false };

let mountCount = 0;
let scopeDepth = 0;
let disposalPending = false;
// The lowest store size at which a reclamation requested inside an open
// scope empties the store when the outermost scope ends; `Infinity` when
// none is pending. Several requests produce at most one reset.
let pendingThreshold = Infinity;

/** Honoured at once with no scope open, or at the end of the outermost
 * open scope: never between two acquisitions or during a walk. */
function requestReclamation(threshold: number): void {
  if (scopeDepth > 0) {
    pendingThreshold = Math.min(pendingThreshold, threshold);
  } else if (nodes.length >= threshold) {
    resetStore();
  }
}

function scoped<T>(action: () => T): T {
  scopeDepth += 1;
  try {
    return action();
  } finally {
    scopeDepth -= 1;
    if (scopeDepth === 0) {
      const reclaim = (disposalPending && mountCount === 0)
        || nodes.length >= pendingThreshold;
      disposalPending = false;
      pendingThreshold = Infinity;
      if (reclaim) resetStore();
    }
  }
}

/** One synchronous preparation AND use of node references. An ordinary
 * operation never reclaims the store (see `EXPRESSION_LIMITS`), unless
 * the suite's `everyOperation` switch is on; a protected operation may
 * exceed the headroom while it runs. Raw IDs/maps must not survive this
 * scope without source + generation. Never wrap an async callback: a
 * scope cannot span an await. */
export function withExpressions<T>(action: () => T): T {
  if (scopeDepth === 0 && EXPRESSION_LIMITS.everyOperation
      && nodes.length >= EXPRESSION_LIMITS.nodes) resetStore();
  return scoped(action);
}

/** What the viewer tells the store about a validated document: it was
 * installed, replacing what it displaced, or abandoned without being
 * installed. The first call wins; later calls do nothing. Holds a
 * generation and a count, never a node id. */
export interface DocumentSettlement {
  installed(): void;
  abandoned(): void;
}

/** One synchronous document load: a `withExpressions` scope that, when
 * outermost, first empties the store if it holds `EXPRESSION_LIMITS.nodes`
 * or more, so the obsolete state of whatever it replaces is gone before
 * the incoming document is prepared. A refused load requests a
 * reclamation at that threshold at its end. A successful one returns
 * its value with the document's settlement: `installed()` requests a
 * reclamation at the threshold plus the nodes this load added while the
 * generation is the one it ended in, so an installation keeps its own
 * incoming graph and reclaims only what other operations prepared while
 * it waited, and at the threshold once the generation has moved;
 * `abandoned()` requests one at the threshold. */
export function withDocumentLoad<T>(action: () => T):
    { value: T; settlement: DocumentSettlement } {
  if (scopeDepth === 0 && nodes.length >= EXPRESSION_LIMITS.nodes) resetStore();
  const start = nodes.length;
  let added = 0;
  let generation = 0;
  const value = scoped(() => {
    try {
      const result = action();
      added = nodes.length - start;
      generation = storeGeneration;
      return result;
    } catch (error) {
      requestReclamation(EXPRESSION_LIMITS.nodes);
      throw error;
    }
  });
  let settled = false;
  return {
    value,
    settlement: {
      installed() {
        if (settled) return;
        settled = true;
        requestReclamation(EXPRESSION_LIMITS.nodes
          + (storeGeneration === generation ? added : 0));
      },
      abandoned() {
        if (settled) return;
        settled = true;
        requestReclamation(EXPRESSION_LIMITS.nodes);
      },
    },
  };
}

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
  // The flat pass (Decision 7): every program, and the served program
  // and pass, go with the nodes they index.
  flatPrograms = new WeakMap();
  forgetServedFlatPass();
  storeGeneration += 1;
}

/** One more mount is holding the shared table. */
export function retainExpressions(): void {
  mountCount += 1;
}

/** One mount is done with the shared table: its graph is obsolete. Every
 * release requests a reclamation at `EXPRESSION_LIMITS.nodes`, so a
 * disposed viewer's graph is not kept beside the survivors' beyond that
 * headroom; the last release empties the store whatever it holds. Both
 * wait for the end of an open scope, where they make at most one reset,
 * and the last release's is cancelled if a mount is retained before
 * then. Harmless if called without a matching retain. */
export function releaseExpressions(): void {
  if (mountCount === 0) return;
  mountCount -= 1;
  if (mountCount === 0 && scopeDepth === 0) {
    resetStore();
    return;
  }
  if (mountCount === 0) disposalPending = true;
  requestReclamation(EXPRESSION_LIMITS.nodes);
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
let profileInspectionVisits = 0;

/** Source-only structural work counter, never a host capability. */
export function profileInspectionMetrics(): number { return profileInspectionVisits; }

export function expressionMetrics(): { nodes: number; peakNodes: number; resolutions: number } {
  return { nodes: nodes.length, peakNodes, resolutions };
}

export function resetExpressionMetrics(): void {
  resolutions = 0;
  profileInspectionVisits = 0;
  peakNodes = nodes.length;
  resetFlatPassCounters();
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
  } else if (first === 'profileOverlap' && scope.profiles !== undefined) {
    value = (...args: number[]) => profileOverlap(scope.profiles!, ...args as [number, number,
      number, number, number, number, number, number]);
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
    && a.profiles === b.profiles
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
  // The flat pass (Decision 6): a node the served program covers is read
  // from it, a comparison handed out as the boolean the walk gives.
  if (servedPass === passCounter && id < servedSlotOf.length) {
    const slot = servedSlotOf[id];
    if (slot >= 0) return servedKinds[slot] === 1 ? servedSlots[slot] !== 0 : servedSlots[slot];
  }
  const result = compute(id, scope);
  nodeValue[id] = result;
  nodeStamp[id] = passCounter;
  resolutions += 1;
  return result;
}

// ---------------------------------------------------------------------
// The flat pass (OpenSpec `evaluate-a-pose-in-one-flat-pass`, design
// Decisions 1-10). On a large bound document nearly every node depends
// on whichever input moves, so the memoized walk above computes the
// whole graph at every pose. A binding table's graph is therefore
// compiled ONCE per table and store generation into a flat program over
// typed arrays, run in one loop before a pose (`WidgetTree.update` and
// `admit` call `prepareFlatPass` first), and read by `valueOf` for that
// pass. The walk stays the reference, and computes everything the
// program does not cover exactly as before.
//
// COVERED (Decision 1), reached from the table's roots in table order,
// a node whose every child is covered and that is:
//   - a literal whose value is a number;
//   - `$t` (one part), read as `scope.time`;
//   - a binding name (one part, an entry, not `$t` or `profileOverlap`),
//     which SHARES its root's slot: the same value and kind by
//     construction; every entry's own name node in the store gets it;
//   - another name, unless its first part is `$t`, `profileOverlap` or an
//     entry, or names something of the OpenSCAD context that is not a
//     number: an INPUT, read each run by `resolveName`'s own steps;
//   - unary `-`, as jokenizer's `-1 * v`;
//   - `+ - * / %`, and `< <= > >= == !=` (whose result is a boolean);
//   - a call whose callee is one of twenty listed names of the context
//     (`FLAT_FUNCTIONS`), not an entry, calling the very function object
//     `resolveName` returns for it.
// Everything else stays with the walk, and so does everything above it:
// `!`, unary `+`, `~`, `&&`, `||`, a ternary, `===`, `!==`, the bitwise
// operators, members, indexes, arrays, objects, non-numeric literals,
// `profileOverlap`, `random` and every unlisted function, a function or
// owner map used as a value.
//
// WHY EACH VALUE IS THE WALK'S (Decision 2). A slot holds a double and a
// kind fixed at compile: a comparison is a boolean, held as 1 or 0 and
// handed out as `slot !== 0`, so every walked parent and every caller
// receives `true` or `false` as before. Inside the program an operand is
// a number or such a boolean, and every covered operator gives the same
// result for `true`/`false` as for 1/0: arithmetic and the comparisons
// apply ToNumeric to two non-strings; `==` and `!=` between two booleans
// or two numbers are strict, and between a boolean and a number compare
// ToNumber(boolean); every listed function applies ToNumber to each
// argument first. A `Float64Array` keeps `-0` and `NaN`. A covered
// computation is a pure function of its slots, so an entry whose inputs
// did not change keeps a value equal to recomputing it.
//
// NOTHING HERE THROWS (Decision 3). Covered operations are arithmetic,
// comparisons and listed calls on numbers. Every place the walk can
// throw is uncovered or is detected by a run's reads and checks. An input
// missing, not a number, or reached through a truthy primitive owner (read
// without `in`) is ABSENT (Decision 4): the run computes nothing over it and
// the pass does not serve its cone, which the walk evaluates when a pose
// reads it, with the walk's value or its own error; the rest is served. A
// `drivers` value that is not an object, or a listed callee name present
// in the driver map, declines the whole pass, and a declined run writes
// nothing. An input supplied again counts as changed whatever its value,
// so nothing over it is served before it is recomputed. A throw inside the
// compile or a run is a defect: it is caught, the table is unserved for
// the store generation, and the pose is walked.
//
// WORK (Decision 5): every covered node has a CLASS, the set of inputs it
// depends on; entries are laid out in segments, one per class, ordered by
// class size and keeping postorder, and a run computes only the segments
// a changed input belongs to.
//
// THE SERVED SLOT INDEX (Decision 4): `valueOf` reads a node's slot from
// the program's own index when no input is absent, else from the program's
// VIEW for the run's absent set (the index with every node of the cones at
// -1), built only when the absent set differs from the last view's. A flat
// read costs the same either way.
//
// LIFETIME (Decision 7): programs live in a `WeakMap` keyed by the
// table's map object, replaced by `resetStore()` with every other
// node-keyed array; the served program, pass and index are forgotten
// there too.
// ---------------------------------------------------------------------

/** Source-only switches for the widget's own tests, never a host
 * capability: the smallest table compiled (a knob value, Decision 5),
 * and a self-check that compares every covered value with the walk's
 * after every run (Decision 10). */
export const FLAT_PASS = { minimumBindings: 1_000, verify: false };

// The twenty functions a covered call may name (Decision 1), as the
// objects `context` holds at module load. Each applies ToNumber to every
// argument first, never throws on numbers, returns a number and keeps no
// state.
const FLAT_FUNCTION_NAMES = [
  'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'sign', 'ln', 'log', 'mod',
  'abs', 'ceil', 'exp', 'floor', 'max', 'min', 'pow', 'round', 'sqrt',
] as const;

type FlatFunction = (...args: number[]) => number;

const FLAT_FUNCTIONS: readonly FlatFunction[] = FLAT_FUNCTION_NAMES.map((name) => {
  const listed = context[name];
  if (typeof listed !== 'function') {
    throw new Error(`The flat pass's listed function "${name}" is not a function`);
  }
  return listed as FlatFunction;
});

const FLAT_FUNCTION_INDEX: ReadonlyMap<string, number> =
  new Map(FLAT_FUNCTION_NAMES.map((name, index) => [name, index]));

// Entry operator codes. A call's code is FLAT_CALL + 4 * its function's
// index + its arity class (none, one, two, or more from the pool).
const FLAT_NEG = 0;
const FLAT_ADD = 1;
const FLAT_SUB = 2;
const FLAT_MUL = 3;
const FLAT_DIV = 4;
const FLAT_MOD = 5;
const FLAT_LT = 6;
const FLAT_LE = 7;
const FLAT_GT = 8;
const FLAT_GE = 9;
const FLAT_EQ = 10;
const FLAT_NE = 11;
const FLAT_CALL = 16;

const FLAT_BINARY: ReadonlyMap<string, number> = new Map([
  ['+', FLAT_ADD], ['-', FLAT_SUB], ['*', FLAT_MUL], ['/', FLAT_DIV], ['%', FLAT_MOD],
  ['<', FLAT_LT], ['<=', FLAT_LE], ['>', FLAT_GT], ['>=', FLAT_GE],
  ['==', FLAT_EQ], ['!=', FLAT_NE],
]);

const KIND_NUMBER = 0;
const KIND_BOOLEAN = 1;

interface FlatInput {
  /** The name's parts; `null` for `$t`. */
  readonly parts: readonly string[] | null;
  readonly slot: number;
}

interface FlatProgram {
  readonly generation: number;
  /** The store's node count at the compile: a node interned later has an
   * id at or above it and no slot. */
  readonly nodeCount: number;
  /** Node id -> slot, or -1 for a node the program does not cover. */
  readonly slotOf: Int32Array;
  /** Entries first, in run order (entry `e` writes slot `e`), then the
   * literals and the inputs. */
  readonly slots: Float64Array;
  readonly kinds: Uint8Array;
  readonly ops: Uint8Array;
  readonly left: Int32Array;
  readonly right: Int32Array;
  /** Argument slots of calls of more than two arguments. */
  readonly pool: Int32Array;
  readonly entries: number;
  readonly inputs: readonly FlatInput[];
  /** Phase one's reads, written to the slots only once all are checked. */
  readonly scratch: Float64Array;
  readonly words: number;
  readonly changed: Uint32Array;
  /** Segment `s` runs entries `segmentStart[s]` to `segmentStart[s + 1]`. */
  readonly segmentStart: Int32Array;
  readonly segmentMask: Uint32Array;
  /** The listed names its calls name: a driver of one of them declines. */
  readonly callees: readonly string[];
  readonly covered: number;
  /** Whether a run has completed since the compile. */
  ran: boolean;
  /** The inputs absent from the last completed run (Decision 4). */
  readonly absent: Uint32Array;
  /** Phase one's absent inputs, which become `absent` when the run completes. */
  readonly incoming: Uint32Array;
  /** The served slot index for `viewAbsent`: `slotOf` with every node over
   * an input of `viewAbsent` at -1; null until a run leaves one absent. */
  view: Int32Array | null;
  readonly viewAbsent: Uint32Array;
}

const NO_SLOTS = new Int32Array(0);

let flatPrograms = new WeakMap<ReadonlyMap<string, NodeId>, FlatProgram | null>();
let servedPass = -1;
let servedSlotOf: Int32Array = NO_SLOTS;
let servedSlots: Float64Array = new Float64Array(0);
let servedKinds: Uint8Array = new Uint8Array(0);
let servedInPart = false;

function forgetServedFlatPass(): void {
  servedPass = -1;
  servedSlotOf = NO_SLOTS;
  servedSlots = new Float64Array(0);
  servedKinds = new Uint8Array(0);
  servedInPart = false;
}

let flatCompiles = 0;
let flatRuns = 0;
let flatPartial = 0;
let flatDeclined = 0;
let flatFailures = 0;
let flatEntries = 0;
let flatViews = 0;
let flatCompared = 0;
let flatAbsentInputs = 0;
let lastProgram: { entries: number; segments: number; inputs: number; covered: number } =
  { entries: 0, segments: 0, inputs: 0, covered: 0 };

function resetFlatPassCounters(): void {
  flatCompiles = 0;
  flatRuns = 0;
  flatPartial = 0;
  flatDeclined = 0;
  flatFailures = 0;
  flatEntries = 0;
  flatViews = 0;
  flatCompared = 0;
  flatAbsentInputs = 0;
}

export interface FlatPassMetrics {
  /** Programs compiled. */
  readonly compiles: number;
  /** Runs that completed and served a pass, in full or in part. */
  readonly runs: number;
  /** Of `runs`, those that left an input absent and served the pass in
   * part, the absent inputs' cones left to the walk. */
  readonly partial: number;
  /** Runs that declined a scope whole (a `drivers` value that is not an
   * object, a driver named like a called function), leaving that pass to
   * the walk. */
  readonly declined: number;
  /** Compiles or runs that threw, leaving their table to the walk. */
  readonly failures: number;
  /** Entries computed by runs. */
  readonly entries: number;
  /** Served views built, one each time a run's absent set differs from the
   * one its program's view was built for. */
  readonly views: number;
  /** Values compared with the walk's by `FLAT_PASS.verify`. */
  readonly compared: number;
  /** The inputs absent from the last completed run. */
  readonly absentInputs: number;
  /** The last compiled program's entries, segments, inputs and covered
   * nodes. */
  readonly programEntries: number;
  readonly segments: number;
  readonly inputs: number;
  readonly coveredNodes: number;
}

/** The flat pass's counts (Decision 9), for the widget's own tests;
 * never on the mount handle. `resetExpressionMetrics()` zeroes the
 * counters. The work a pose performs is `expressionMetrics().resolutions`
 * plus `entries`. */
export function flatPassMetrics(): FlatPassMetrics {
  return {
    compiles: flatCompiles, runs: flatRuns, partial: flatPartial, declined: flatDeclined,
    failures: flatFailures, entries: flatEntries, views: flatViews, compared: flatCompared,
    absentInputs: flatAbsentInputs,
    programEntries: lastProgram.entries, segments: lastProgram.segments,
    inputs: lastProgram.inputs, coveredNodes: lastProgram.covered,
  };
}

/** A test probe: whether `valueOf` would read `id` from the flat pass in
 * the current pass. */
export function flatPassServes(id: NodeId): boolean {
  return servedPass === passCounter && id >= 0 && id < servedSlotOf.length
    && servedSlotOf[id] >= 0;
}

/** A test probe: whether the current pass is served in full, served in
 * part (an input absent, its cone left to the walk), or not served. */
export function flatPassServing(): 'full' | 'part' | 'none' {
  if (servedPass !== passCounter) return 'none';
  return servedInPart ? 'part' : 'full';
}

/** A name node that is a binding name of `bindings` (Decision 1). */
function isBindingName(node: NameNode, bindings: ReadonlyMap<string, NodeId>): boolean {
  const first = node.parts[0];
  return node.parts.length === 1 && first !== TIME_ID && first !== 'profileOverlap'
    && bindings.has(first);
}

/** Compile the part of `bindings`' graph the flat pass covers. */
function compileFlatPass(bindings: ReadonlyMap<string, NodeId>): FlatProgram {
  const count = nodes.length;
  // 0 unvisited, 1 open (on the current path), 2 finished.
  const state = new Uint8Array(count);
  // A covered node's class; -1 for one not covered.
  const classOf = new Int32Array(count).fill(-1);
  const covered: NodeId[] = [];
  const inputParts: (readonly string[] | null)[] = [];
  const inputNode: NodeId[] = [];
  const callees = new Set<string>();

  // Classes: sorted input-index lists, interned, with memoized unions so
  // the compile stays linear in the graph.
  const classMembers: number[][] = [[]];
  const classIds = new Map<string, number>([['', 0]]);
  const unions = new Map<string, number>();
  const internClass = (members: number[]): number => {
    const key = members.join(',');
    const found = classIds.get(key);
    if (found !== undefined) return found;
    const id = classMembers.length;
    classMembers.push(members);
    classIds.set(key, id);
    return id;
  };
  const unite = (a: number, b: number): number => {
    if (a === b || b === 0) return a;
    if (a === 0) return b;
    const key = a < b ? `${a},${b}` : `${b},${a}`;
    const found = unions.get(key);
    if (found !== undefined) return found;
    const x = classMembers[a];
    const y = classMembers[b];
    const merged: number[] = [];
    let i = 0;
    let j = 0;
    while (i < x.length || j < y.length) {
      if (j >= y.length || (i < x.length && x[i] < y[j])) merged.push(x[i++]);
      else if (i >= x.length || y[j] < x[i]) merged.push(y[j++]);
      else { merged.push(x[i++]); j += 1; }
    }
    const id = internClass(merged);
    unions.set(key, id);
    return id;
  };
  const done = (id: NodeId): boolean => id < count && state[id] === 2 && classOf[id] >= 0;
  const input = (id: NodeId, parts: readonly string[] | null): number => {
    const index = inputParts.length;
    inputParts.push(parts);
    inputNode.push(id);
    return internClass([index]);
  };

  const finish = (id: NodeId): void => {
    state[id] = 2;
    const node = nodes[id];
    let found = -1;
    switch (node.kind) {
      case 'const':
        if (typeof node.value === 'number') found = 0;
        break;
      case 'name': {
        const first = node.parts[0];
        if (first === TIME_ID) {
          if (node.parts.length === 1) found = input(id, null);
        } else if (first === 'profileOverlap') {
          // Resolved before the table when the scope carries profiles.
        } else if (bindings.has(first)) {
          if (node.parts.length === 1) {
            const root = bindings.get(first)!;
            if (done(root)) found = classOf[root];
          }
        } else if (!(first in context) || typeof context[first] === 'number') {
          found = input(id, node.parts);
        }
        break;
      }
      case 'unary':
        if (node.op === '-' && done(node.target)) found = classOf[node.target];
        break;
      case 'binary':
        if (FLAT_BINARY.has(node.op) && done(node.left) && done(node.right)) {
          found = unite(classOf[node.left], classOf[node.right]);
        }
        break;
      case 'call': {
        const callee = nodes[node.callee];
        if (callee.kind !== 'name' || callee.parts.length !== 1) break;
        const name = callee.parts[0];
        if (!FLAT_FUNCTION_INDEX.has(name) || bindings.has(name)) break;
        let cls = 0;
        let all = true;
        for (const arg of node.args) {
          if (!done(arg)) { all = false; break; }
          cls = unite(cls, classOf[arg]);
        }
        if (all) {
          found = cls;
          callees.add(name);
        }
        break;
      }
      default:
        break;
    }
    if (found >= 0) {
      classOf[id] = found;
      covered.push(id);
    }
  };

  // An iterative postorder (no recursion, no depth limit). A node popped
  // while still open is on the current path: a cycle, which leaves the
  // parent that reached it uncovered (`done` is false for it).
  const stack: number[] = [];
  for (const rootId of bindings.values()) {
    if (rootId < 0 || rootId >= count || state[rootId] !== 0) continue;
    stack.push(rootId);
    while (stack.length > 0) {
      const top = stack.pop()!;
      if (top < 0) { finish(~top); continue; }
      if (state[top] !== 0) continue;
      state[top] = 1;
      stack.push(~top);
      const node = nodes[top];
      switch (node.kind) {
        case 'unary': stack.push(node.target); break;
        case 'binary': stack.push(node.right, node.left); break;
        case 'call':
          for (let i = node.args.length - 1; i >= 0; i -= 1) stack.push(node.args[i]);
          break;
        case 'name':
          if (isBindingName(node, bindings)) stack.push(bindings.get(node.parts[0])!);
          break;
        default:
          break;
      }
    }
  }

  // Segments (Decision 5): one per class, ordered by the number of
  // inputs it holds, each keeping postorder. A child's class is a subset
  // of its parent's, so this is a dependency order.
  const isEntry = (node: Node): boolean =>
    node.kind === 'unary' || node.kind === 'binary' || node.kind === 'call';
  const perClass = new Int32Array(classMembers.length);
  let entries = 0;
  for (const id of covered) {
    if (isEntry(nodes[id])) { perClass[classOf[id]] += 1; entries += 1; }
  }
  const ranked = classMembers.map((_, id) => id).filter((id) => perClass[id] > 0)
    .sort((a, b) => classMembers[a].length - classMembers[b].length || a - b);
  const words = Math.max(1, Math.ceil(inputParts.length / 32));
  const segmentStart = new Int32Array(ranked.length + 1);
  const segmentMask = new Uint32Array(ranked.length * words);
  const cursor = new Int32Array(classMembers.length);
  let start = 0;
  ranked.forEach((cls, segment) => {
    segmentStart[segment] = start;
    cursor[cls] = start;
    start += perClass[cls];
    for (const member of classMembers[cls]) {
      segmentMask[segment * words + (member >>> 5)] |= 1 << (member & 31);
    }
  });
  segmentStart[ranked.length] = start;

  // Slots: entries in run order, then literals and inputs; then every
  // binding name shares its root's slot.
  const slotOf = new Int32Array(count).fill(-1);
  let leaves = 0;
  for (const id of covered) {
    const node = nodes[id];
    if (isEntry(node)) slotOf[id] = cursor[classOf[id]]++;
    else if (!(node.kind === 'name' && isBindingName(node, bindings))) leaves += 1;
  }
  const slots = new Float64Array(entries + leaves);
  const kinds = new Uint8Array(entries + leaves);
  let leaf = entries;
  for (const id of covered) {
    const node = nodes[id];
    if (node.kind === 'const') {
      slots[leaf] = node.value as number;
      slotOf[id] = leaf++;
    } else if (node.kind === 'name' && !isBindingName(node, bindings)) {
      slotOf[id] = leaf++;
    }
  }
  let coveredCount = 0;
  for (const id of covered) {
    const node = nodes[id];
    if (node.kind === 'name' && isBindingName(node, bindings)) {
      slotOf[id] = slotOf[bindings.get(node.parts[0])!];
    }
    coveredCount += 1;
  }
  // Every entry's own name node in the store, read by an operation or
  // not: found by the intern table's key, so nothing is minted.
  for (const [name, root] of bindings) {
    const nameId = table.get(`n${name}`);
    if (nameId === undefined || nameId >= count || slotOf[nameId] >= 0) continue;
    const node = nodes[nameId];
    if (node.kind !== 'name' || !isBindingName(node, bindings)) continue;
    if (root < 0 || root >= count || slotOf[root] < 0) continue;
    slotOf[nameId] = slotOf[root];
    coveredCount += 1;
  }

  const ops = new Uint8Array(entries);
  const left = new Int32Array(entries);
  const right = new Int32Array(entries);
  const pool: number[] = [];
  for (const id of covered) {
    const node = nodes[id];
    if (!isEntry(node)) continue;
    const slot = slotOf[id];
    if (node.kind === 'unary') {
      ops[slot] = FLAT_NEG;
      left[slot] = slotOf[node.target];
    } else if (node.kind === 'binary') {
      const op = FLAT_BINARY.get(node.op)!;
      ops[slot] = op;
      if (op >= FLAT_LT) kinds[slot] = KIND_BOOLEAN;
      left[slot] = slotOf[node.left];
      right[slot] = slotOf[node.right];
    } else if (node.kind === 'call') {
      const fn = FLAT_FUNCTION_INDEX.get((nodes[node.callee] as NameNode).parts[0])!;
      const arity = node.args.length;
      ops[slot] = FLAT_CALL + 4 * fn + Math.min(arity, 3);
      if (arity === 1) {
        left[slot] = slotOf[node.args[0]];
      } else if (arity === 2) {
        left[slot] = slotOf[node.args[0]];
        right[slot] = slotOf[node.args[1]];
      } else if (arity > 2) {
        left[slot] = pool.length;
        right[slot] = arity;
        for (const arg of node.args) pool.push(slotOf[arg]);
      }
    }
  }

  return {
    generation: storeGeneration,
    nodeCount: count,
    slotOf, slots, kinds, ops, left, right,
    pool: Int32Array.from(pool),
    entries,
    inputs: inputParts.map((parts, index) => ({ parts, slot: slotOf[inputNode[index]] })),
    scratch: new Float64Array(inputParts.length),
    words,
    changed: new Uint32Array(words),
    segmentStart, segmentMask,
    callees: [...callees],
    covered: coveredCount,
    ran: false,
    absent: new Uint32Array(words),
    incoming: new Uint32Array(words),
    view: null,
    viewAbsent: new Uint32Array(words),
  };
}

/** Entries `start` to `end` of `program`, in order. */
function runFlatEntries(program: FlatProgram, start: number, end: number): void {
  const { slots, ops, left, right, pool } = program;
  for (let entry = start; entry < end; entry += 1) {
    const op = ops[entry];
    const a = left[entry];
    const b = right[entry];
    let value: number;
    switch (op) {
      // -1 * v, not -v: jokenizer's own unary rule, as `applyUnary`.
      case FLAT_NEG: value = -1 * slots[a]; break;
      case FLAT_ADD: value = slots[a] + slots[b]; break;
      case FLAT_SUB: value = slots[a] - slots[b]; break;
      case FLAT_MUL: value = slots[a] * slots[b]; break;
      case FLAT_DIV: value = slots[a] / slots[b]; break;
      case FLAT_MOD: value = slots[a] % slots[b]; break;
      case FLAT_LT: value = slots[a] < slots[b] ? 1 : 0; break;
      case FLAT_LE: value = slots[a] <= slots[b] ? 1 : 0; break;
      case FLAT_GT: value = slots[a] > slots[b] ? 1 : 0; break;
      case FLAT_GE: value = slots[a] >= slots[b] ? 1 : 0; break;
      // On two doubles `==` is `===`, and `!=` is `!==`.
      case FLAT_EQ: value = slots[a] === slots[b] ? 1 : 0; break;
      case FLAT_NE: value = slots[a] !== slots[b] ? 1 : 0; break;
      default: {
        const call = op - FLAT_CALL;
        const fn = FLAT_FUNCTIONS[call >> 2];
        switch (call & 3) {
          case 0: value = fn(); break;
          case 1: value = fn(slots[a]); break;
          case 2: value = fn(slots[a], slots[b]); break;
          default: {
            const args = new Array<number>(b);
            for (let i = 0; i < b; i += 1) args[i] = slots[pool[a + i]];
            value = fn(...args);
          }
        }
      }
    }
    slots[entry] = value;
  }
}

/** Whether mask `a` from word `at` and mask `b`, of `words` words, meet. */
function masksMeet(a: Uint32Array, at: number, b: Uint32Array, words: number): boolean {
  for (let word = 0; word < words; word += 1) {
    if ((a[at + word] & b[word]) !== 0) return true;
  }
  return false;
}

/** One two-phase run (Decision 4): with nothing written, decline (-1) a
 * scope that is not about one input, then read every input or mark it
 * absent; then store the present inputs that changed (one absent from the
 * last run counts as changed, whatever its value) and run the segments
 * they belong to, all of them on the first run after the compile, except
 * those over an absent input. Returns the number of absent inputs. */
function runFlatPass(program: FlatProgram, scope: EvalScope): number {
  const drivers = scope.drivers as unknown;
  const hasDrivers = drivers !== undefined;
  // `in` on anything but an object throws in the walk: leave it there.
  if (hasDrivers && (drivers === null
      || (typeof drivers !== 'object' && typeof drivers !== 'function'))) return -1;
  const driverMap = drivers as Record<string, unknown>;
  if (hasDrivers) {
    // A driver named like a called function is what `resolveName` would
    // call, and the walk throws its own TypeError for it.
    for (const callee of program.callees) if (callee in driverMap) return -1;
  }
  const { inputs, scratch, slots, incoming } = program;
  incoming.fill(0);
  let absentCount = 0;
  for (let i = 0; i < inputs.length; i += 1) {
    const parts = inputs[i].parts;
    let value: unknown;
    if (parts === null) {
      value = scope.time;
    } else {
      const first = parts[0];
      if (hasDrivers && first in driverMap) value = driverMap[first];
      else if (first in context) value = context[first];
      else value = undefined;
      for (let p = 1; p < parts.length; p += 1) {
        // `readMember`, except that a truthy owner that is not an object
        // or a function is not read with `in` (the walk throws there): the
        // input is absent.
        if (!value) { value = undefined; break; }
        if (typeof value !== 'object' && typeof value !== 'function') { value = undefined; break; }
        const part = parts[p];
        value = part in (value as object) ? (value as Record<string, unknown>)[part] : undefined;
      }
    }
    if (typeof value !== 'number') {
      incoming[i >>> 5] |= 1 << (i & 31);
      absentCount += 1;
      continue;
    }
    scratch[i] = value;
  }

  const { changed, words, segmentStart, segmentMask, absent } = program;
  const first = !program.ran;
  changed.fill(0);
  for (let i = 0; i < inputs.length; i += 1) {
    const word = i >>> 5;
    const bit = 1 << (i & 31);
    // An absent input's slot is not written, and nothing over it is run.
    if ((incoming[word] & bit) !== 0) continue;
    const slot = inputs[i].slot;
    // By `Object.is`: -0 and 0 differ, NaN equals NaN. An input absent
    // from the last run counts as changed whatever its value: every
    // segment over it was skipped since.
    if (first || (absent[word] & bit) !== 0 || !Object.is(scratch[i], slots[slot])) {
      slots[slot] = scratch[i];
      changed[word] |= bit;
    }
  }
  absent.set(incoming);
  const segments = segmentStart.length - 1;
  for (let segment = 0; segment < segments; segment += 1) {
    if (!first && !masksMeet(segmentMask, segment * words, changed, words)) continue;
    if (absentCount > 0 && masksMeet(segmentMask, segment * words, absent, words)) continue;
    const start = segmentStart[segment];
    const end = segmentStart[segment + 1];
    runFlatEntries(program, start, end);
    flatEntries += end - start;
  }
  program.ran = true;
  return absentCount;
}

/** The slot index a completed run serves (Decision 4): the program's own
 * when no input is absent, else its view for the absent set, built only
 * when that set differs from the one the view was built for. */
function servedSlotIndex(program: FlatProgram, absentCount: number): Int32Array {
  if (absentCount === 0) return program.slotOf;
  const { absent, words, viewAbsent } = program;
  if (program.view !== null) {
    let same = true;
    for (let word = 0; word < words; word += 1) {
      if (viewAbsent[word] !== absent[word]) { same = false; break; }
    }
    if (same) return program.view;
  }
  // The cones: every segment whose class holds an absent input, and the
  // absent inputs' own slots. A binding name shares its root's slot, so it
  // goes with its root.
  const blocked = new Uint8Array(program.slots.length);
  const { segmentStart, segmentMask, inputs } = program;
  for (let segment = 0; segment < segmentStart.length - 1; segment += 1) {
    if (masksMeet(segmentMask, segment * words, absent, words)) {
      blocked.fill(1, segmentStart[segment], segmentStart[segment + 1]);
    }
  }
  for (let i = 0; i < inputs.length; i += 1) {
    if ((absent[i >>> 5] & (1 << (i & 31))) !== 0) blocked[inputs[i].slot] = 1;
  }
  const view = program.slotOf.slice();
  for (let id = 0; id < view.length; id += 1) {
    const slot = view[id];
    if (slot >= 0 && blocked[slot] === 1) view[id] = -1;
  }
  program.view = view;
  viewAbsent.set(absent);
  flatViews += 1;
  return view;
}

function formatFlatValue(value: unknown): string {
  return `${Object.is(value, -0) ? '-0' : String(value)} (${typeof value})`;
}

function describeFlatNode(id: NodeId): string {
  const node = nodes[id];
  switch (node.kind) {
    case 'const': return `a literal ${formatFlatValue(node.value)}`;
    case 'name': return `the name "${node.name}"`;
    case 'unary': return `a unary "${node.op}"`;
    case 'binary': return `a binary "${node.op}"`;
    case 'call': return `a call of "${(nodes[node.callee] as NameNode).name}"`;
    default: return `a ${node.kind}`;
  }
}

/** `FLAT_PASS.verify` (Decision 10): every node the pass is about to serve
 * (`slotOf`, the served slot index) evaluated by the walk -- before the
 * pass is served, so no slot is read -- and compared with its slot's
 * handed-out value by `Object.is`. Leaves first, then the entries in run
 * order, then the binding names, so the walk of each finds its children
 * already memoized. A node of a cone has no slot there and is not
 * checked. */
function verifyFlatPass(program: FlatProgram, slotOf: Int32Array,
                        bindings: ReadonlyMap<string, NodeId>, scope: EvalScope): void {
  const { slots, kinds, entries } = program;
  const owner = new Int32Array(slots.length).fill(-1);
  const aliases: NodeId[] = [];
  for (let id = 0; id < slotOf.length; id += 1) {
    const slot = slotOf[id];
    if (slot < 0) continue;
    const node = nodes[id];
    if (node.kind === 'name' && isBindingName(node, bindings)) aliases.push(id);
    else owner[slot] = id;
  }
  const check = (id: NodeId): void => {
    const slot = slotOf[id];
    const flat = kinds[slot] === KIND_BOOLEAN ? slots[slot] !== 0 : slots[slot];
    const walked = valueOf(id, scope);
    flatCompared += 1;
    if (!Object.is(flat, walked)) {
      throw new Error(
        `The flat pass differs from the walk at node ${id}, ${describeFlatNode(id)}: `
        + `flat ${formatFlatValue(flat)}, walk ${formatFlatValue(walked)}`);
    }
  };
  for (let slot = entries; slot < slots.length; slot += 1) if (owner[slot] >= 0) check(owner[slot]);
  for (let slot = 0; slot < entries; slot += 1) if (owner[slot] >= 0) check(owner[slot]);
  for (const id of aliases) check(id);
}

/** The flat pass's one entry (Decision 6), called first by
 * `WidgetTree.update` and `admit`: compile this table's program if it has
 * none in this store generation, run it, and serve the current pass from
 * it, in full or, with an input absent, in part. A table smaller than
 * `FLAT_PASS.minimumBindings`, or none, returns at once; a scope declined
 * whole, or a failure, leaves the pass to the walk. Never throws, except for the source-only self-check's
 * mismatch. */
export function prepareFlatPass(scope: EvalScope): void {
  const bindings = scope.bindings;
  if (bindings === undefined || bindings.size < FLAT_PASS.minimumBindings) return;
  ensurePass(scope);
  if (servedPass === passCounter) return;
  let program = flatPrograms.get(bindings);
  if (program === null) return;
  let absentCount: number;
  let slotIndex: Int32Array = NO_SLOTS;
  try {
    if (program === undefined || program.generation !== storeGeneration) {
      program = compileFlatPass(bindings);
      flatPrograms.set(bindings, program);
      flatCompiles += 1;
      lastProgram = {
        entries: program.entries, segments: program.segmentStart.length - 1,
        inputs: program.inputs.length, covered: program.covered,
      };
    }
    absentCount = runFlatPass(program, scope);
    if (absentCount >= 0) slotIndex = servedSlotIndex(program, absentCount);
  } catch {
    flatPrograms.set(bindings, null);
    flatFailures += 1;
    return;
  }
  if (absentCount < 0) {
    flatDeclined += 1;
    return;
  }
  flatRuns += 1;
  if (absentCount > 0) flatPartial += 1;
  flatAbsentInputs = absentCount;
  if (FLAT_PASS.verify) verifyFlatPass(program, slotIndex, bindings, scope);
  servedPass = passCounter;
  servedSlotOf = slotIndex;
  servedSlots = program.slots;
  servedKinds = program.kinds;
  servedInPart = absentCount > 0;
}

/** Inspect a document expression, including binding aliases, before execution.
 * Returns whether the reserved profile call occurs. This is structural: a
 * profile index must be a literal leaf, never a computed scalar. */
export function inspectProfileExpression(
  root: NodeId, bindings?: ReadonlyMap<string, NodeId>, profileCount?: number,
): boolean {
  return inspectProfile(root, bindings, profileCount);
}

/** Validation-owned negative facts for one binding map and generation. Acquire,
 * use and discard inside one synchronous withExpressions operation. Running
 * Bounds keep inspectProfileExpression and their own profile-table context. */
export function validationProfileInspector(bindings?: ReadonlyMap<string, NodeId>):
  (root: NodeId) => boolean {
  const generation = expressionGeneration();
  const clear = new Set<NodeId>();
  return (root) => {
    if (generation !== expressionGeneration()) {
      throw new Error('Profile inspection references escaped their expression generation');
    }
    return inspectProfile(root, bindings, undefined, clear);
  };
}

function inspectProfile(
  root: NodeId, bindings?: ReadonlyMap<string, NodeId>, profileCount?: number,
  clear?: Set<NodeId>,
): boolean {
  let found = false;
  const seen = new Set<NodeId>();
  const pending: { id: NodeId; calleeOfProfile: boolean }[] =
    [{ id: root, calleeOfProfile: false }];
  const push = (id: NodeId, calleeOfProfile = false): void => {
    pending.push({ id, calleeOfProfile });
  };
  while (pending.length > 0) {
    const { id, calleeOfProfile } = pending.pop()!;
    const node = nodes[id];
    if (node.kind === 'name' && node.name === 'profileOverlap') {
      if (!calleeOfProfile) throw new Error('profileOverlap must be called directly');
      continue;
    }
    // A reserved name's direct-callee context must be checked even when
    // this node was visited in a different position of this same walk.
    if (seen.has(id) || clear?.has(id)) continue;
    seen.add(id);
    profileInspectionVisits += 1;
    switch (node.kind) {
      case 'name': {
        const binding = bindings?.get(node.parts[0]);
        if (binding !== undefined) push(binding);
        break;
      }
      case 'call': {
        const callee = nodes[node.callee];
        let directProfile = false;
        if (callee.kind === 'name' && callee.name === 'profileOverlap') {
          found = true;
          directProfile = true;
          if (node.args.length !== 8) {
            throw new Error('profileOverlap requires exactly eight arguments');
          }
          for (const index of node.args.slice(0, 2)) {
            const literal = nodes[index];
            if (literal.kind !== 'const' || typeof literal.value !== 'number'
                || !Number.isSafeInteger(literal.value) || literal.value < 0) {
              throw new Error('profileOverlap profile indices must be literal nonnegative integers');
            }
            if (profileCount !== undefined && literal.value >= profileCount) {
              throw new Error('profileOverlap profile index is outside the table');
            }
          }
        }
        for (let i = node.args.length - 1; i >= 0; i--) push(node.args[i]);
        push(node.callee, directProfile);
        break;
      }
      case 'unary': push(node.target); break;
      case 'binary': push(node.right); push(node.left); break;
      case 'member': push(node.owner); break;
      case 'index': push(node.key); push(node.owner); break;
      case 'ternary': push(node.whenFalse); push(node.whenTrue); push(node.predicate); break;
      case 'array':
        for (let i = node.items.length - 1; i >= 0; i--) push(node.items[i]);
        break;
      case 'object':
        for (let i = node.values.length - 1; i >= 0; i--) push(node.values[i]);
        break;
      default: break;
    }
  }
  // Publish only after the ENTIRE walk succeeds and contains no profile call.
  // A positive or failed traversal contributes no negative structural facts.
  if (!found && clear) for (const id of seen) clear.add(id);
  return found;
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

/** Reconstructible owner of a PathValue. The numerical walk stays in
 * PathValue unchanged; only its generation-qualified working data is
 * rebuilt. A reset between points must bind the ORIGINAL piece values,
 * not treat the new point as the start of a different piece. */
export class ExpressionPath {
  private generation = -1;
  private path?: PathValue;
  private standing?: Record<string, number>;

  constructor(private readonly expression: string,
              private readonly moving: ReadonlySet<string>,
              private readonly bindings: () => ReadonlyMap<string, NodeId> | undefined) {}

  private current(): PathValue {
    if (this.generation !== expressionGeneration()) {
      this.path = new PathValue(prepare(this.expression), this.moving, this.bindings());
      this.generation = expressionGeneration();
      if (this.standing !== undefined) this.path.bind(this.standing);
    }
    return this.path!;
  }

  bind(values: Record<string, number>, firstSampleOfSearch = false): unknown {
    return withExpressions(() => {
      // Binding a new piece does not need to reconstruct the old one.
      this.standing = undefined;
      const path = this.current();
      const result = path.bind(values, firstSampleOfSearch);
      this.standing = path.boundInputs();
      return result;
    });
  }

  at(values: Record<string, number>): unknown {
    return withExpressions(() => this.current().at(values));
  }

  /** A Bound search may retain this path across searches only when no
   * standing call can produce a new value without changed numeric inputs. */
  reusableStanding(): boolean {
    return this.path?.reusableStanding() ?? false;
  }
}

export class PathValue {
  /** The moving cone, in the WHOLE graph's postorder, decided the first
   * time this quantity is bound (D2). `null` until then. */
  private order: NodeId[] | null = null;
  private movingOrderSet: ReadonlySet<NodeId> = new Set();

  /** Every node's value at the last bind. `at` never changes this map. */
  private readonly bound = new Map<NodeId, unknown>();

  /** Scratch, valid only for the duration of one `bind`/`at` call. */
  private readonly computed = new Map<NodeId, unknown>();

  /** The whole graph's postorder, decided once and reused by every later
   * piece (D2). */
  private walked: NodeId[] = [];

  /** Stable dependencies and unresolved bank leaves of this path graph. */
  private readonly children = new Map<NodeId, readonly NodeId[]>();
  private readonly inputs: NodeId[] = [];
  private readonly inputValues = new Map<NodeId, { present: boolean; value: unknown }>();
  private readonly calls: NodeId[] = [];

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
    return this.bound.get(id);
  }

  private inputAt(id: NodeId, values: Record<string, number>):
    { present: boolean; value: unknown } {
    const name = (nodes[id] as NameNode).name;
    const present = Object.prototype.hasOwnProperty.call(values, name);
    return { present, value: present ? values[name] : undefined };
  }

  /** The original piece's relevant inputs for `ExpressionPath` to
   * reconstruct this bound path after an expression-table reset. The
   * snapshot was already taken by `bind`; no caller bank is walked here.
   * A null prototype keeps a bank key named `__proto__` ordinary. */
  boundInputs(): Record<string, number> {
    if (this.order === null) throw new Error('PathValue.boundInputs() before bind()');
    const values = Object.create(null) as Record<string, number>;
    for (const id of this.inputs) {
      const input = this.inputValues.get(id)!;
      if (input.present) values[(nodes[id] as NameNode).name] = input.value as number;
    }
    return values;
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

  /** A new piece: decide the moving cone on the first bind, then retain
   * unaffected values across later pieces. `at` samples are scratch and
   * cannot contaminate this bound snapshot. */
  bind(values: Record<string, number>, firstSampleOfSearch = false): unknown {
    const deciding = this.order === null;
    this.computed.clear();
    if (deciding) {
      const walk = this.postorder();
      // Decide whether the WHOLE graph is path-safe before evaluating any
      // node. An unsupported ternary or short-circuit may have an untaken
      // child that throws; eagerly walking that child and only then falling
      // back would change generic valueOf's observable error semantics.
      for (const id of walk) {
        const node = nodes[id];
        if (node.kind === 'call') {
          const callee = nodes[node.callee];
          if (callee.kind === 'name' && callee.name === 'profileOverlap') {
            throw new UnsupportedPathNode('PathValue: profileOverlap uses program-scoped data');
          }
        }
        if (node.kind === 'binary' && (node.op === '&&' || node.op === '||')) {
          throw new UnsupportedPathNode(`PathValue: a short-circuit "${node.op}"`);
        }
        if (node.kind === 'member' || node.kind === 'index'
            || node.kind === 'ternary' || node.kind === 'array'
            || node.kind === 'object') {
          throw new UnsupportedPathNode(`PathValue: a ${node.kind} node`);
        }
        if (node.kind === 'name' && node.parts.length > 1
            && node.parts[0] !== TIME_ID
            && !this.bindings?.has(node.parts[0])
            && !Object.prototype.hasOwnProperty.call(values, node.name)
            && !(node.parts[0] in context)) {
          throw new UnsupportedPathNode(
            `PathValue: the multi-part name "${node.name}" is neither in the run's bank nor resolvable through $t, a binding or the OpenSCAD context -- the one shape flat and nested resolution could disagree on.`);
        }
      }
      this.walked = walk;
      const moves = new Map<NodeId, boolean>();
      const order: NodeId[] = [];
      for (const id of walk) {
        const node = nodes[id];
        const children = this.childrenOf(id);
        this.children.set(id, children);
        if (node.kind === 'call') this.calls.push(id);
        if (node.kind === 'name' && children.length === 0
            && node.parts[0] !== TIME_ID) {
          this.inputs.push(id);
          this.inputValues.set(id, this.inputAt(id, values));
        }
        const value = this.valueAt(id, values);
        resolutions += 1;
        this.bound.set(id, value);
        const nodeMoves = node.kind === 'name' && children.length === 0
          ? this.movesByName(id)
          : children.some((child) => moves.get(child) === true);
        moves.set(id, nodeMoves);
        if (nodeMoves) order.push(id);
      }
      this.order = order;
      this.movingOrderSet = new Set(order);
      return this.bound.get(this.root);
    }

    const dirty = new Set<NodeId>();
    for (const id of this.inputs) {
      const next = this.inputAt(id, values);
      const previous = this.inputValues.get(id)!;
      if (next.present !== previous.present
          || !Object.is(next.value, previous.value)) {
        dirty.add(id);
        this.inputValues.set(id, next);
      }
    }
    if (dirty.size === 0 && !firstSampleOfSearch) return this.bound.get(this.root);
    if (firstSampleOfSearch && [...dirty].every((id) => this.movingOrderSet.has(id))) {
      // An unchanged standing graph needs no whole-postorder scan. The
      // moving order is that postorder's stable subsequence, and every
      // changed leaf is already inside it.
      for (const id of this.order!) {
        const value = this.valueAt(id, values);
        resolutions += 1;
        this.bound.set(id, value);
      }
      return this.bound.get(this.root);
    }
    for (const id of this.walked) {
      if (!dirty.has(id) && !(firstSampleOfSearch && this.movingOrderSet.has(id))
          && !this.children.get(id)!.some((child) => dirty.has(child))) continue;
      const value = this.valueAt(id, values);
      resolutions += 1;
      this.bound.set(id, value);
      dirty.add(id);
    }
    return this.bound.get(this.root);
  }

  /** A LATER point of the SAME piece: only the moving cone (D2). Every
   * node computed charges the resolution probe (D8); a quantity whose
   * whole expression stands charges nothing. */
  at(values: Record<string, number>): unknown {
    const order = this.order;
    if (order === null) {
      throw new Error('PathValue.at() called before bind()');
    }
    if (order.length === 0) return this.bound.get(this.root);
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

  reusableStanding(): boolean {
    return this.order !== null && this.calls.every((id) =>
      this.bound.get((nodes[id] as CallNode).callee) !== Math.random);
  }
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
  /** Reconstructible derived operands, when retained beyond one scope. */
  readonly current?: () => KinkLevel;
}

/** Kink descriptors may live for the lifetime of a loaded program. Keep
 * their source and postorder index, not an unqualified old integer.
 * Rebuild the list once per generation, shared by all its descriptors. */
export function retainedKinkLevels(expression: string,
                                  bindings: () => ReadonlyMap<string, NodeId> | undefined):
readonly KinkLevel[] {
  return withExpressions(() => {
    let generation = -1;
    let levels: readonly KinkLevel[];
    const current = (): readonly KinkLevel[] => {
      if (generation !== expressionGeneration()) {
        levels = kinkLevels(prepare(expression), bindings());
        generation = expressionGeneration();
      }
      return levels;
    };
    return current().map((level, index) => ({
      ...level,
      current: () => current()[index],
    }));
  });
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
