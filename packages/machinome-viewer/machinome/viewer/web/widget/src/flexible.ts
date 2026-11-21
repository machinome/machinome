/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// Geometry that follows the machine, evaluated the way pose already is.
//
// A flexible node carries no mesh. It carries the analytic spec its
// evaluator reads plus one expression per shape parameter, in the same
// scope operation expressions are evaluated in (`$t` and the nested
// driver map). Evaluating shape is therefore the same mechanism as
// evaluating pose with `geometry = f(params)` where the matrix path has
// `matrix = f(params)`, and it is bounded by the same rule: a node
// recomputes only on frames where a free variable of one of its own
// expressions changed. On such a frame its parameters are evaluated, and
// its geometry is rebuilt only when one of their values differs from the
// ones its present vertex data was built from: the shape is a function of
// the spec and the values alone, so equal values would write equal data.
//
// What makes that affordable at frame rate is molejo's declared
// tessellation. Vertex count, vertex ordering and the whole index follow
// the DOCUMENT and never a parameter, so the buffers are allocated once
// per node -- by the first evaluation, which is the only call that can
// know the counts -- and every later binding refills the same
// `Float32Array` in place. Nothing is reallocated, no attribute is
// replaced, and the index is never rewritten.

import * as THREE from 'three';
import { evaluate, validate, MolejoBuffers } from 'molejo';
import { EvalScope, evalPrepared, freeVariables } from './evaluator';
import { BindingTable, EMPTY_BINDINGS } from './bindings';
import { expressionGeneration, NodeId, prepare, withExpressions } from './expressions';
import { ManifestFlexible } from './types';
import { MaterialKind, MaterialPresentation, releaseMaterial } from './presentation';

/** Every `tech` this package can evaluate. A document naming another one
 * is refused rather than rendered wrong -- the posture the loader
 * already takes toward an undeclared driver id. */
export const FLEXIBLE_TECHNOLOGIES: readonly string[] = ['molejo'];

export function evaluatesTech(tech: string): boolean {
  return FLEXIBLE_TECHNOLOGIES.includes(tech);
}

/** The technologies, listed for an error message. */
export function knownTechnologies(): string {
  return [...FLEXIBLE_TECHNOLOGIES].sort().join(', ');
}

/** Why the bundled evaluator cannot read `spec`, or `null` if it can.
 *
 * This viewer does not read a spec. Which documents are readable -- the
 * version they declare, the vocabulary they use -- is the evaluator's
 * question, and ADR-057 put the document through here opaquely on
 * purpose. So this asks molejo and carries its answer back verbatim,
 * which is also why the message a caller builds from it says something
 * specific rather than "invalid spec".
 *
 * Called once per node at construction, never per frame. */
export function specRefusal(spec: unknown): string | null {
  try {
    validate(spec);
    return null;
  } catch (error) {
    return error instanceof Error ? error.message : String(error);
  }
}

/** The one mesh of one flexible node, and the buffers behind it.
 *
 * Owns the spec, the parsed parameter expressions, their free-variable
 * union (this node's geometry dependency set, exactly parallel to the
 * one its operations have), the molejo buffers and the three.js
 * geometry wired onto them.
 */
export class FlexibleShape {
  readonly mesh: THREE.Mesh;

  private readonly tech: string;
  private readonly spec: Record<string, unknown>;
  private readonly geometry: THREE.BufferGeometry;
  private params: [string, string][];
  private freeVars: ReadonlySet<string> | undefined;
  // The document's bindings table (design D2, D6), document-scoped like
  // `WidgetTree`'s own field: `EMPTY_BINDINGS` for a document with
  // nothing shared.
  private bindings: BindingTable;
  // Undefined until the first evaluation: molejo derives the counts from
  // the spec, so the first call is what allocates and writes the index.
  private buffers: MolejoBuffers | undefined;
  // The parameter values, in the order of `params`, that the vertex data
  // now in `buffers` was built from. The invariant: whenever this is
  // defined, the position array holds exactly what the evaluator produces
  // from `spec` and these values, and the bounds were computed from that
  // array. Only `evaluate` writes the buffers, so only it may set this --
  // after the write, never before -- and it is forgotten before every
  // write and by `rebind`. A writer of the position array that does not
  // go through `evaluate` must forget it too.
  private built: number[] | undefined;
  // The root node of each parameter expression, in the order of `params`,
  // with the expression store's generation they were prepared in (OpenSpec
  // `rebuild-a-flexible-part-for-less`, design Decision 1). A cache of the
  // store, keyed by text and generation; it holds no value. Read only
  // inside `readParameters`'s own scope, and only while the store's
  // generation is still this one: a reclamation raises the generation and
  // the next read prepares every text again. Dropped by `rebind`, since
  // the texts may have changed; set only after a read that prepared every
  // text completed, so a refusal leaves it as it stood.
  private roots: { generation: number; ids: NodeId[] } | undefined;

  constructor(name: string, flexible: ManifestFlexible,
              color: string | null, bindings: BindingTable = EMPTY_BINDINGS,
              private readonly presentation = new MaterialPresentation()) {
    if (!evaluatesTech(flexible.tech)) {
      throw new Error(
        `The node "${name}" is a flexible part evaluated by ` +
        `"${flexible.tech}", which this viewer cannot evaluate; it ` +
        `evaluates: ${knownTechnologies()}. Refusing it rather than ` +
        'rendering a wrong shape.',
      );
    }
    // The same refusal one step further in: a technology this viewer
    // evaluates, carrying a spec its evaluator cannot read -- a document
    // written for an older molejo, say. Caught here rather than left to
    // the first evaluate(), so it names the node at load instead of
    // surfacing as a bare evaluator error on some later frame.
    const refusal = specRefusal(flexible.spec);
    if (refusal !== null) {
      throw new Error(
        `The node "${name}" is a flexible part whose spec this viewer's ` +
        `${flexible.tech} cannot read: ${refusal}. Refusing it rather ` +
        'than failing while rendering.',
      );
    }
    this.tech = flexible.tech;
    this.spec = flexible.spec;
    this.params = parameterList(flexible);
    this.bindings = bindings;
    this.geometry = new THREE.BufferGeometry();
    // Flat shading, because that is the look every other part already
    // has: an STL arrives non-indexed, so the vertex normals computed
    // for it are per-face. This geometry is indexed and shares its rim
    // vertices between the wall and the caps, so smooth normals would
    // round the rim off and disagree with the rigid part beside it.
    // Shading from the derivatives also spares an O(V) normal pass on
    // every frame a driver moves.
    this.mesh = presentation.mesh(this.geometry, FLEXIBLE, color);
  }

  /** Every input this node's parameter expressions read, `$t` included --
   * a binding name closed over the document's table (design D5, D6),
   * exactly parallel to `WidgetTree`'s own `free`.
   *
   * The union is the node's geometry dependency set. Computed once off
   * the evaluator's cached parse and dropped whenever a reconcile
   * replaces the expressions. */
  get free(): ReadonlySet<string> {
    if (this.freeVars === undefined) {
      const found = new Set<string>();
      for (const [, expression] of this.params) {
        for (const name of freeVariables(expression)) {
          found.add(name);
        }
      }
      this.freeVars = this.bindings.closure(found);
    }
    return this.freeVars;
  }

  /** Whether `flexible` describes the same shape this already evaluates.
   *
   * Only `tech` and `spec` decide it: the parameter expressions are
   * rebindable in place, because the counts they feed are the
   * document's, not theirs. */
  describes(flexible: ManifestFlexible): boolean {
    return flexible.tech === this.tech
      && JSON.stringify(flexible.spec) === JSON.stringify(this.spec);
  }

  /** Point the same buffers at new expressions, and forget which inputs
   * the old ones read. Unconditional (design D6): unlike `WidgetTree`'s
   * own reconcile, this is already called only when the spec is
   * unchanged (`describes`), so there is no cheaper case to distinguish
   * -- it always needs the freshly-installed table regardless of
   * whether the expressions or the table actually differ. */
  rebind(flexible: ManifestFlexible, bindings: BindingTable = EMPTY_BINDINGS): void {
    this.params = parameterList(flexible);
    this.bindings = bindings;
    this.freeVars = undefined;
    // New expressions or a new table: what the buffers were built from
    // is no longer comparable position by position, so the next
    // evaluation rebuilds.
    this.built = undefined;
    // And the next read prepares the new texts.
    this.roots = undefined;
  }

  setColor(color: string | null): void {
    this.presentation.recolor(this.mesh, color);
  }

  /** Evaluate the parameters in `scope` and refill the buffers if a value
   * moved.
   *
   * The first call allocates them and wires the attributes; a later one
   * writes into the arrays already on the GPU's side of the fence, but
   * only when one of the values differs from the ones the buffers were
   * built from. Two values are the same when `Object.is` says so: `-0`
   * and `0` differ, and `NaN` is the same as `NaN`. When none differs
   * the part keeps its vertex data, its bounds and its buffers: the
   * evaluator is not called, nothing is uploaded and no bounds pass runs.
   *
   * The parameters are read by their prepared roots (`readParameters`):
   * each value, and each refusal, is the one `evalExpr` of its text gives,
   * in the order of their names, the first refusal winning. A parameter
   * expression that throws does so before anything is written or
   * forgotten. */
  evaluate(scope: EvalScope): void {
    const next = this.readParameters(scope);

    if (this.holdsBuiltFrom(next)) {
      return;
    }

    // Forgotten before the evaluator is asked: if it refuses, whatever
    // the buffers hold afterwards is described by nothing, and the next
    // evaluation rebuilds.
    this.built = undefined;
    const values: Record<string, number> = {};
    this.params.forEach(([name], i) => {
      values[name] = next[i];
    });

    const buffers = evaluate(this.spec, values, this.buffers);
    if (this.buffers === undefined) {
      this.buffers = buffers;
      this.geometry.setIndex(new THREE.BufferAttribute(buffers.index, 1));
      this.geometry.setAttribute(
        'position', new THREE.BufferAttribute(buffers.positions, 3));
    }
    const positions = this.geometry.getAttribute('position');
    positions.needsUpdate = true;
    // The camera frames on these, and a spring that changed length has
    // changed both: three.js's two bounds, number for number, in two
    // passes over the array.
    computeFlexibleBounds(this.geometry);
    this.built = next;
  }

  /** JUDGE the parameters in `scope` without showing them (OpenSpec
   * `draw-a-press-from-its-first-frame`, design D1): refuse exactly what
   * `evaluate` would refuse, with the same error, and write nothing.
   *
   * Every parameter is read as `evaluate` reads it, by the same reader
   * (`readParameters`: its prepared root, the value and the refusal
   * `evalExpr` of its text gives, in the order of the names), so a
   * throwing expression throws here first, with the same error. When the
   * part has buffers and the values are the ones they were built from
   * (`Object.is`), molejo has already accepted exactly these values and
   * is not asked again.
   * Otherwise molejo evaluates them into buffers of its own, which are
   * dropped: the part's buffers, its geometry, its bounds and what it
   * remembers having built from are all left as they stood, so a later
   * `evaluate` of the same values still rebuilds. */
  admit(scope: EvalScope): void {
    const next = this.readParameters(scope);

    if (this.holdsBuiltFrom(next)) {
      return;
    }

    const values: Record<string, number> = {};
    this.params.forEach(([name], i) => {
      values[name] = next[i];
    });
    evaluate(this.spec, values);
  }

  /** The parameter values in `scope`, in the order of `params`: for each,
   * `evalExpr`'s call, `evalPrepared(prepare(text), scope)`, without the
   * lookup when the roots this part holds are of the store's present
   * generation.
   *
   * One scope for the whole read, the generation read inside it: a reset
   * never runs while a scope is open, so the roots cannot go stale
   * between the check and the last evaluation. When the roots are not
   * reused, each text is prepared just before its own evaluation, so a
   * text that cannot be prepared refuses at its own place in name order,
   * after every earlier parameter was evaluated, as `evalExpr` would. The
   * roots are committed only after the loop. */
  private readParameters(scope: EvalScope): number[] {
    return withExpressions(() => {
      const generation = expressionGeneration();
      const held = this.roots;
      const reuse = held !== undefined && held.generation === generation;
      const params = this.params;
      const ids: NodeId[] = reuse ? held.ids : new Array(params.length);
      const values: number[] = new Array(params.length);
      for (let i = 0; i < params.length; i += 1) {
        const id = reuse ? ids[i] : (ids[i] = prepare(params[i][1]));
        values[i] = evalPrepared(id, scope);
      }
      if (!reuse) this.roots = { generation, ids };
      return values;
    });
  }

  /** Whether `next` are the values the buffers were built from: the part
   * has buffers, remembers what they were built from, and every value is
   * the same under `Object.is`. The one test `evaluate` and `admit` skip
   * by. */
  private holdsBuiltFrom(next: number[]): boolean {
    const built = this.built;
    return this.buffers !== undefined && built !== undefined
      && next.length === built.length
      && next.every((value, i) => Object.is(value, built[i]));
  }

  dispose(): void {
    this.geometry.dispose();
    releaseMaterial(this.mesh);
  }
}

/** A rebuilt flexible part's bounding box and bounding sphere: the
 * numbers three.js 0.156.1's `BufferGeometry.computeBoundingBox` and
 * `computeBoundingSphere` write, in two passes over the position array
 * where those make three through the attribute's accessors (OpenSpec
 * `rebuild-a-flexible-part-for-less`, design Decision 2).
 *
 * It performs three.js's operations in three.js's order. The box is
 * `Box3.setFromBufferAttribute`: from `+Infinity` and `-Infinity`, per
 * vertex `Math.min` of each coordinate and then `Math.max`. The sphere's
 * centre is `Box3.getCenter`: `(0, 0, 0)` for an empty box, else
 * `(min + max) * 0.5`; its radius is the square root of the largest
 * `Math.max` of `dx * dx + dy * dy + dz * dz`, `dx` being centre minus
 * vertex. The box three.js computes a second time for the sphere is not
 * computed again: it is the same six numbers from the same array. Like
 * three.js it writes into the geometry's `Box3` and `Sphere` and
 * allocates them only when they are null.
 *
 * The guard: the fast path runs only on a position attribute whose
 * `getX`, `getY` and `getZ` are `THREE.BufferAttribute.prototype`'s own,
 * with item size 3 over a `Float32Array` (whose denormalization is the
 * identity, so `normalized` needs no check), and no morph positions.
 * Anything else -- no position attribute, an interleaved, half-float or
 * GL attribute, another item size, an accessor of its own, a morph
 * target -- is bounded by three.js's two functions. When a bound comes
 * out not a number (the box's `min` or the radius, three.js's two
 * conditions) three.js's two functions are called afterwards, so the
 * console receives exactly what three.js reports.
 *
 * `flexible-rebuild.test.ts` (B1 to B3) runs three.js's own functions
 * beside this one on every suite run, with the installed three.js. */
export function computeFlexibleBounds(geometry: THREE.BufferGeometry): void {
  const attribute = geometry.attributes.position as THREE.BufferAttribute | undefined;
  const accessors = THREE.BufferAttribute.prototype;
  if (attribute === undefined
      || geometry.morphAttributes.position
      || attribute.getX !== accessors.getX
      || attribute.getY !== accessors.getY
      || attribute.getZ !== accessors.getZ
      || attribute.itemSize !== 3
      || !(attribute.array instanceof Float32Array)) {
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
    return;
  }
  const array = attribute.array;
  const count = attribute.count;

  let minX = +Infinity;
  let minY = +Infinity;
  let minZ = +Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  let maxZ = -Infinity;
  for (let i = 0; i < count; i += 1) {
    const x = array[i * 3];
    const y = array[i * 3 + 1];
    const z = array[i * 3 + 2];
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    minZ = Math.min(minZ, z);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
    maxZ = Math.max(maxZ, z);
  }
  if (geometry.boundingBox === null) geometry.boundingBox = new THREE.Box3();
  geometry.boundingBox.min.set(minX, minY, minZ);
  geometry.boundingBox.max.set(maxX, maxY, maxZ);

  if (geometry.boundingSphere === null) geometry.boundingSphere = new THREE.Sphere();
  const empty = maxX < minX || maxY < minY || maxZ < minZ;
  const cx = empty ? 0 : (minX + maxX) * 0.5;
  const cy = empty ? 0 : (minY + maxY) * 0.5;
  const cz = empty ? 0 : (minZ + maxZ) * 0.5;
  let most = 0;
  for (let i = 0; i < count; i += 1) {
    const dx = cx - array[i * 3];
    const dy = cy - array[i * 3 + 1];
    const dz = cz - array[i * 3 + 2];
    most = Math.max(most, dx * dx + dy * dy + dz * dz);
  }
  const radius = Math.sqrt(most);
  geometry.boundingSphere.center.set(cx, cy, cz);
  geometry.boundingSphere.radius = radius;

  if (Number.isNaN(minX) || Number.isNaN(minY) || Number.isNaN(minZ)
      || Number.isNaN(radius)) {
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
  }
}

function parameterList(flexible: ManifestFlexible): [string, string][] {
  // Sorted, so the values handed to the evaluator are built in one
  // order whatever order the document's object happens to hold.
  return Object.keys(flexible.params).sort()
    .map((name): [string, string] => [name, flexible.params[name]]);
}

// Kept beside the shape rather than imported from `tree.ts`, which
// imports this module: the same two materials, with the flat shading a
// swept indexed surface needs to look like the rigid parts around it.
function materialForFlexible(color: string | THREE.Color | null): THREE.Material {
  if (color === null) {
    return new THREE.MeshNormalMaterial({ flatShading: true });
  }
  return new THREE.MeshStandardMaterial({
    color: new THREE.Color(color),
    metalness: 0.1,
    roughness: 0.6,
    flatShading: true,
  });
}

/** A flexible part's kind of material (OpenSpec
 * `share-one-material-per-appearance`, design Decision 1). */
export const FLEXIBLE: MaterialKind = { name: 'flexible', make: materialForFlexible };
