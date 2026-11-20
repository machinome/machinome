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
import { EvalScope, evalExpr, freeVariables } from './evaluator';
import { BindingTable, EMPTY_BINDINGS } from './bindings';
import { ManifestFlexible } from './types';

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

  constructor(name: string, flexible: ManifestFlexible,
              color: string | null, bindings: BindingTable = EMPTY_BINDINGS) {
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
    this.mesh = new THREE.Mesh(this.geometry,
                               materialForFlexible(color));
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
  }

  setColor(color: string | null): void {
    const previous = this.mesh.material;
    this.mesh.material = materialForFlexible(color);
    (Array.isArray(previous) ? previous : [previous])
      .forEach((material) => material.dispose());
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
   * A parameter expression that throws does so before anything is
   * written or forgotten. */
  evaluate(scope: EvalScope): void {
    const next: number[] = this.params.map(
      ([, expression]) => evalExpr(expression, scope));

    const built = this.built;
    if (this.buffers !== undefined && built !== undefined
        && next.length === built.length
        && next.every((value, i) => Object.is(value, built[i]))) {
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
    // changed both.
    this.geometry.computeBoundingBox();
    this.geometry.computeBoundingSphere();
    this.built = next;
  }

  dispose(): void {
    this.geometry.dispose();
    const materials = Array.isArray(this.mesh.material)
      ? this.mesh.material : [this.mesh.material];
    materials.forEach((material) => material.dispose());
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
function materialForFlexible(color: string | null): THREE.Material {
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
