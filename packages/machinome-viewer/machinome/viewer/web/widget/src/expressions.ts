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

  const parsed = tokenize(plainLiterals(expression));
  if (parsed === null) {
    throw new Error('Cannot evaluate an empty expression');
  }
  const rootId = build(parsed, expression);
  expressionRoots.set(expression, rootId);
  return rootId;
}

// ---------------------------------------------------------------------
// Metrics (D9): a test-visible count of subexpression resolutions and
// of the shared table's size, so the win this change makes is asserted
// as work performed rather than as elapsed time. `resolutions` is wired
// up in the next increment; the table size is real from the first one.
// ---------------------------------------------------------------------

let resolutions = 0;

export function expressionMetrics(): { nodes: number; resolutions: number } {
  return { nodes: nodes.length, resolutions };
}

export function resetExpressionMetrics(): void {
  resolutions = 0;
}
