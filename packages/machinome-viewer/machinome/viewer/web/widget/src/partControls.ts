/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// What a document's `controls` table means, and what a gesture on one
// decides (OpenSpec `drive-the-run-by-touch`, design D1-D3, D6, D10,
// D11, D17).
//
// This module imports neither the DOM nor three.js. A vector is a tuple
// of three numbers, a ray is an origin and a direction, and a matrix is
// the sixteen COLUMN-MAJOR numbers three.js's `Matrix4.elements` holds
// -- so every decision here is a node test beside `runControls.test.ts`.
// `viewer.ts` keeps the three.js and the DOM and decides nothing, which
// is the same split `drive-the-run-on-screen` made for the panel.
//
// Nothing here writes a coordinate, poses a part or talks to the run.
// The planner's whole output is "issue this one relative move now, or
// nothing"; the part is posed by what the run COMMITS, never by the
// pointer (design D12).

import type { Manifest, ManifestControl, ManifestNode } from './types';
import { affineCoordinate } from './expressions';
import { bindingTable } from './bindings';

export type Vec3 = readonly [number, number, number];

/** One entry of the table, validated and in the viewer's own spelling.
 * The fields the producer publishes, carried through unchanged. */
export interface LoadedControl {
  /** The table's key: the control's qualified display name. */
  name: string;
  kind: 'button' | 'turn' | 'slide';
  part: readonly string[];
  /** A button's instruction, or null for a turn. */
  instruction: string | null;
  /** A turn's input, or null for a button. */
  input: string | null;
  /** A turn's published ratio, or null for a button. */
  perUnit: number | null;
  joint: readonly string[];
  coordinate: string;
  axis: Vec3;
  origin: Vec3;
  operationSpan?: readonly [number, number];
}

/** As much of a loaded program as reading the table needs: the
 * coordinates it publishes. `LoadedProgram` satisfies it; a test hand-
 * writes one. */
export interface ControlProgramView {
  coordinates: Readonly<Record<string, unknown>>;
}

const KINDS = ['button', 'turn', 'slide'];

function shown(value: unknown): string {
  if (typeof value === 'string') return JSON.stringify(value);
  if (value === undefined) return 'nothing';
  if (typeof value === 'object' && value !== null) {
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }
  return String(value);
}

function listed(keys: readonly string[]): string {
  return keys.length === 0 ? 'none' : keys.join(', ');
}

function pathOf(path: readonly string[]): string {
  return path.join('/') || '<root>';
}

/** The one node a name path reaches, in `requirePath`'s own vocabulary
 * (design D1.3) -- so a control's bad path reads exactly as a host's
 * bad path does, and a reader who has met one has met both. */
function requireNode(root: ManifestNode,
                     path: readonly string[]): ManifestNode {
  let current = root;
  for (let index = 0; index < path.length; index += 1) {
    const matches = (current.children ?? [])
      .filter((child) => child.name === path[index]);
    if (matches.length !== 1) {
      const reason = matches.length === 0 ? 'Unknown' : 'Ambiguous';
      throw new Error(`${reason} assembly path: ${pathOf(path)}`);
    }
    current = matches[0];
  }
  return current;
}

function isNamePath(value: unknown): value is string[] {
  return Array.isArray(value)
    && value.every((name) => typeof name === 'string');
}

function isPrefix(prefix: readonly string[],
                  path: readonly string[]): boolean {
  return prefix.length <= path.length
    && prefix.every((name, index) => path[index] === name);
}

function requireVector(refuse: (why: string) => never,
                       field: string, value: unknown): Vec3 {
  if (!Array.isArray(value) || value.length !== 3
      || !value.every((one) => typeof one === 'number'
                      && Number.isFinite(one))) {
    throw refuse(
      `whose "${field}" is not three finite numbers (${shown(value)})`);
  }
  return [value[0], value[1], value[2]];
}

/** Read, validate and order a document's `controls` table (design D1).
 *
 * Every refusal names the document, the control's key and the offending
 * value: a refusal nobody can act on is not a refusal. A document with
 * no key at all gets `[]` and reaches exactly the code it reached
 * before this viewer knew of controls (D2).
 *
 * `program` is the loaded program, or null for a document carrying
 * none -- which is every version 1 to 4 document, and a version 5 one
 * without a run. A table on such a document is refused: a control has
 * nothing to submit a request to, and ignoring it silently would hide a
 * producer's mistake.
 */
export function readControls(
  document: Manifest,
  sourceUrl: string,
  program: ControlProgramView | null,
): LoadedControl[] {
  const table = document.controls;
  if (table === undefined || table === null) {
    return [];
  }
  if (typeof table !== 'object' || Array.isArray(table)) {
    throw new Error(
      `${sourceUrl} carries a "controls" table that is not an object `
      + `(${shown(table)}). Refusing the document rather than presenting `
      + 'an affordance nobody declared.');
  }
  if (program === null) {
    throw new Error(
      `${sourceUrl} carries a "controls" table (${
        listed(Object.keys(table))}) and no program. A control has `
      + 'nothing to submit a request to: refusing the document rather '
      + 'than presenting an affordance with nothing to ask.');
  }

  const instructions = Object.keys(document.instructions ?? {});
  const drivers = Object.keys(document.drivers ?? {});
  const coordinates = Object.keys(program.coordinates ?? {});
  const loaded: LoadedControl[] = [];
  // What each kind has already claimed. Two Turns may share a part only
  // when they select different validated joints: the named handles can
  // then distinguish them without guessing a body drag. Buttons and
  // Slides retain the one-per-kind-and-part rule.
  const claimed = new Map<string, string>();

  for (const name of Object.keys(table)) {
    const entry = (table as Record<string, unknown>)[name];
    const refuse = (why: string): never => {
      throw new Error(
        `${sourceUrl} declares the control "${name}" ${why}. Refusing the `
        + 'document rather than presenting a control the viewer cannot '
        + 'resolve.');
    };

    if (typeof entry !== 'object' || entry === null || Array.isArray(entry)) {
      refuse(`whose entry is not an object (${shown(entry)})`);
    }
    const control = entry as unknown as ManifestControl;

    if (!KINDS.includes(control.kind)) {
      refuse(`with kind ${shown(control.kind)}, which is neither "button" `
             + 'nor "turn" nor "slide"');
    }
    const kind = control.kind as LoadedControl['kind'];

    for (const field of ['part', 'joint'] as const) {
      if (!isNamePath(control[field])) {
        refuse(`whose "${field}" is not a list of node names `
               + `(${shown(control[field])})`);
      }
    }
    const part = control.part;
    const joint = control.joint;

    let jointNode: ManifestNode;
    try {
      requireNode(document.root, part);
      jointNode = requireNode(document.root, joint);
    } catch (error) {
      refuse(`whose path does not resolve: ${
        error instanceof Error ? error.message : String(error)}`);
      throw error;
    }

    if (!isPrefix(joint, part)) {
      refuse(`whose joint ${pathOf(joint)} is neither the part `
             + `${pathOf(part)} nor one of its ancestors; a control's `
             + 'coordinate is the one owned by the nearest ancestor-or-self '
             + 'of the part, so the gesture\'s geometry would be meaningless');
    }

    let instruction: string | null = null;
    let input: string | null = null;
    let perUnit: number | null = null;
    if (kind === 'button') {
      if (typeof control.instruction !== 'string'
          || !instructions.includes(control.instruction)) {
        refuse(`naming the instruction ${shown(control.instruction)}, which `
               + 'its instructions table does not declare; it declares: '
               + `${listed(instructions)}`);
      }
      instruction = control.instruction as string;
    } else {
      if (typeof control.input !== 'string'
          || !drivers.includes(control.input)) {
        refuse(`naming the input ${shown(control.input)}, which its drivers `
               + `table does not declare; it declares: ${listed(drivers)}`);
      }
      input = control.input as string;
      if (typeof control.per_unit !== 'number'
          || !Number.isFinite(control.per_unit) || control.per_unit === 0) {
        refuse(`whose "per_unit" is ${shown(control.per_unit)}, which is not `
               + 'a finite non-zero number: the gesture would have no '
               + 'quantum');
      }
      perUnit = control.per_unit as number;
    }

    if (!coordinates.includes(control.coordinate)) {
      refuse(`naming the coordinate ${shown(control.coordinate)}, which its `
             + 'program does not publish; it publishes: '
             + `${listed(coordinates)}`);
    }

    const axis = requireVector(refuse, 'axis', control.axis);
    const origin = requireVector(refuse, 'origin', control.origin);
    if (length3(axis) === 0) {
      refuse('whose "axis" has no direction (it is [0, 0, 0])');
    }

    // D6's one condition, corrected at review: the joint's placement
    // must be the LEADING RUN of its node's operations -- zero or more
    // translations and then the rotation naming this coordinate -- so
    // that `axis` and `origin`, which the framework publishes in the
    // node's OWN frame, really are in the frame `matrixWorld` maps from.
    // Both shapes the producer publishes qualify: `r` alone for a joint
    // through its node's placed origin, and `t(-a), r, t(a)` for a
    // `Revolute(at=a)`, whose entry publishes `origin = a`.
    let operationSpan: readonly [number, number] | undefined;
    if (control.operation_span !== undefined) {
      const span = control.operation_span;
      if (!Array.isArray(span) || span.length !== 2
          || !span.every(Number.isInteger) || span[0] < 0
          || span[1] <= span[0] || span[1] > jointNode.operations.length) {
        refuse(`whose operation span ${shown(span)} is outside its joint placement`);
      }
      operationSpan = [span[0], span[1]];
      const block = jointNode.operations.slice(span[0], span[1]);
      const roots = bindingTable(document, sourceUrl).roots();
      const near = (a: number, b: number): boolean => Math.abs(a - b) < 1e-9;
      const scalar = (expression: string, slope: number, offset: number): boolean => {
        const affine = affineCoordinate(expression, control.coordinate, roots);
        return affine !== null && near(affine[0], slope) && near(affine[1], offset);
      };
      const direction = normalize3(axis);
      const isTranslation = block.length === 1 && block[0][0] === 't'
        && block[0][1].every((expression, i) => scalar(expression, direction[i], 0));
      const r = block.length === 3 ? block[1] : block[0];
      const isRotation = r[0] === 'r' && scalar(r[1], 1, 0)
        && r[2].every((value, i) => near(value, direction[i]))
        && (block.length === 1 && origin.every(value => near(value, 0))
          || block.length === 3 && block[0][0] === 't' && block[2][0] === 't'
            && block[0][1].every((expression, i) => scalar(expression, 0, -origin[i]))
            && block[2][1].every((expression, i) => scalar(expression, 0, origin[i])));
      const domain = (program.coordinates[control.coordinate] as { domain?: string }).domain;
      if (kind === 'slide' && domain !== 'translational'
          || kind === 'turn' && domain !== 'rotational') {
        refuse(`whose ${kind} requires a ${kind === 'slide' ? 'translational' : 'rotational'} placement, not ${shown(domain)}`);
      }
      if (!(isTranslation && domain === 'translational'
            || isRotation && domain === 'rotational')) {
        refuse(`whose operation span ${shown(span)} is not the complete placement of ${shown(control.coordinate)}`);
      }
    } else if (kind === 'slide') {
      refuse('whose sliding placement requires an operation span');
    } else if (leadingRotation(jointNode) !== control.coordinate) {
      const placement = leadingRotation(jointNode);
      refuse(`whose joint ${pathOf(joint)} is not posed by `
             + `${shown(control.coordinate)} as the leading run of its own `
             + 'operations -- zero or more translations and then one '
             + `rotation over that coordinate; it is posed by `
             + `${placement === null ? 'no leading rotation' : shown(placement)}`);
    }

    // JSON preserves path boundaries even if a node name contains a
    // separator. The selected joint, not an input or display name, is
    // the physical freedom a Turn handle owns.
    const key = JSON.stringify(kind === 'turn'
      ? [kind, part, joint] : [kind, part]);
    const already = claimed.get(key);
    if (already !== undefined) {
      refuse(`on the part ${pathOf(part)}${kind === 'turn'
        ? ` and selected joint ${pathOf(joint)}` : ''}, which "${already}" already `
             + `declares a ${shown(kind)} on; one gesture would have two `
             + 'meanings and the viewer would have to choose');
    }
    claimed.set(key, name);

    loaded.push({
      name,
      kind,
      part: [...part],
      instruction,
      input,
      perUnit,
      joint: [...joint],
      coordinate: control.coordinate,
      axis,
      origin,
      ...(operationSpan === undefined ? {} : { operationSpan }),
    });
  }

  return loaded;
}

/** The expression of the rotation that ENDS a node's leading run of
 * translations, or null when the run does not end in a rotation.
 *
 * `operationsMatrix` composes a node's operations as `M_n · … · M_1`,
 * so the first entry of the list is applied FIRST -- innermost -- and
 * the leading run is what a point of the node's own frame meets before
 * anything else. */
export function leadingRotation(node: ManifestNode): string | null {
  for (const operation of node.operations) {
    if (operation[0] === 'r') {
      return operation[1];
    }
  }
  return null;
}

// ---------------------------------------------------------------------
// The gesture's geometry (design D6, D10). Pure vector math over
// tuples: no three.js type reaches this file, and `viewer.ts` hands in
// `matrixWorld.elements` and the ray it built from the pointer.

export interface Ray {
  origin: Vec3;
  direction: Vec3;
}

/** A line in world space: a point on it and a unit direction. */
export interface WorldLine {
  origin: Vec3;
  axis: Vec3;
}

/** Signed position of the closest point on the rail to the pointer ray.
 * Below ~8.6 degrees from end-on, this problem is ill-conditioned; the
 * caller must ask for another view, not invent pixels per millimetre. */
export function slidePosition(ray: Ray, line: WorldLine): number | null {
  const direction = normalize3(ray.direction);
  const axis = normalize3(line.axis);
  const cosine = dot3(direction, axis);
  const sineSquared = Math.max(0, 1 - cosine * cosine);
  if (sineSquared < EDGE_ON * EDGE_ON) return null;
  const offset = sub3(ray.origin, line.origin);
  return (dot3(offset, axis) - cosine * dot3(offset, direction)) / sineSquared;
}

export function dot3(a: Vec3, b: Vec3): number {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

export function cross3(a: Vec3, b: Vec3): Vec3 {
  return [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0],
  ];
}

export function sub3(a: Vec3, b: Vec3): Vec3 {
  return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
}

export function length3(a: Vec3): number {
  return Math.sqrt(dot3(a, a));
}

export function normalize3(a: Vec3): Vec3 {
  const size = length3(a);
  if (size === 0) {
    throw new Error('a zero-length vector has no direction');
  }
  return [a[0] / size, a[1] / size, a[2] / size];
}

/** The world line a control turns about, from the JOINT node's world
 * matrix (ADR-112 §3, design D6).
 *
 * `elements` is three.js's COLUMN-MAJOR sixteen. `origin` is carried by
 * the full affine map and `axis` by its rotation alone, then
 * normalized. This is exact WHILE THE JOINT TURNS: the joint's own
 * rotation fixes the own-frame line `(origin, axis)`, so `W · L` is the
 * same line at every joint angle and the plane does not move under the
 * drag that is moving the part.
 */
export function worldLine(elements: readonly number[],
                          axis: Vec3, origin: Vec3): WorldLine {
  const e = elements;
  const point: Vec3 = [
    e[0] * origin[0] + e[4] * origin[1] + e[8] * origin[2] + e[12],
    e[1] * origin[0] + e[5] * origin[1] + e[9] * origin[2] + e[13],
    e[2] * origin[0] + e[6] * origin[1] + e[10] * origin[2] + e[14],
  ];
  const direction: Vec3 = [
    e[0] * axis[0] + e[4] * axis[1] + e[8] * axis[2],
    e[1] * axis[0] + e[5] * axis[1] + e[9] * axis[2],
    e[2] * axis[0] + e[6] * axis[1] + e[10] * axis[2],
  ];
  return { origin: point, axis: normalize3(direction) };
}

/** Where a ray meets the plane through `plane.origin` normal to
 * `plane.axis`, or null for a ray PARALLEL to it -- where the
 * intersection runs away toward infinity and a pixel of pointer
 * movement becomes an unbounded jump in angle. */
export function intersectPlane(ray: Ray, plane: WorldLine): Vec3 | null {
  const denominator = dot3(ray.direction, plane.axis);
  if (denominator === 0) {
    return null;
  }
  const t = dot3(sub3(plane.origin, ray.origin), plane.axis) / denominator;
  return [
    ray.origin[0] + ray.direction[0] * t,
    ray.origin[1] + ray.direction[1] * t,
    ray.origin[2] + ray.direction[2] * t,
  ];
}

/** The signed angle in DEGREES from `from` to `to` about `axis`,
 * right-handed -- the same sense and the same units `operationsMatrix`
 * turns the joint in, so a sweep of `s` degrees is a coordinate delta
 * of `s`. Both directions are projected into the plane normal to
 * `axis` first, so a component along it costs nothing. */
export function sweepAngle(from: Vec3, to: Vec3, axis: Vec3): number {
  const flat = (v: Vec3): Vec3 => {
    const along = dot3(v, axis);
    return [v[0] - axis[0] * along, v[1] - axis[1] * along,
      v[2] - axis[2] * along];
  };
  const a = flat(from);
  const b = flat(to);
  const radians = Math.atan2(dot3(cross3(a, b), axis), dot3(a, b));
  return radians * (180 / Math.PI);
}

/** How a gesture measures its sweep. Chosen ONCE, from the pointerdown
 * ray, and fixed for the gesture: orbiting is suspended, so the camera
 * cannot move and the measurement cannot change meaning half-way
 * through. */
export type SweepMode = 'plane' | 'screen';

/** About 8.6 degrees between the ray and the joint's plane. Below it
 * the plane intersection runs away toward infinity; above it the
 * in-plane measurement is the honest one, because it is the angle the
 * maker's hand is actually making about the part's own axle. */
export const EDGE_ON = 0.15;

/** The world radius below which the direction from the axis to the
 * pointer carries no angle at all -- the pointer came down ON the axis.
 * This is a conditioning bound, not a human-scale tolerance: above it
 * the in-plane angle is well defined, and the maker who pressed very
 * near the axle simply gets a coarse first reading. */
export const MIN_RADIUS = 1e-6;

export interface ModeChoice {
  mode: SweepMode;
  /** The in-plane reference direction, for `'plane'`; null otherwise. */
  reference: Vec3 | null;
  /** What a screen-measured angle is multiplied by, for `'screen'`. */
  screenSign: number;
}

/** Which way to measure, and from where (design D10).
 *
 * The screen fallback's sign: a rotation about an axis pointing TOWARD
 * the viewer reads counter-clockwise on screen, so the screen angle --
 * measured in a y-up frame, which is the CSS frame with `dy` negated --
 * is multiplied by `+1` when `A · (O − camera) < 0` and `−1` otherwise.
 * Exactly edge-on that dot product is zero and the sign is genuinely
 * arbitrary; the convention is `+1`, and the maker who finds the dial
 * turning the wrong way orbits a few degrees and gets the in-plane
 * mode.
 */
export function chooseMode(ray: Ray, line: WorldLine,
                           camera: Vec3): ModeChoice {
  const facing = dot3(line.axis, sub3(line.origin, camera));
  const screen: ModeChoice = {
    // `< 0` is the geometry; `=== 0` is exactly edge-on, where the
    // dot product says nothing and the documented convention is `+1`.
    mode: 'screen', reference: null, screenSign: facing <= 0 ? 1 : -1,
  };
  if (Math.abs(dot3(ray.direction, line.axis)) < EDGE_ON) {
    return screen;
  }
  const met = intersectPlane(ray, line);
  if (met === null) {
    return screen;
  }
  const radius = sub3(met, line.origin);
  if (length3(radius) <= MIN_RADIUS) {
    return screen;
  }
  return { mode: 'plane', reference: normalize3(radius), screenSign: 1 };
}

// ---------------------------------------------------------------------
// The planner (design D11). It holds where the last COMMITTED quantum
// ended, where the sweep stands, whether a request is in flight and
// which direction is stalled -- and answers one question: issue this
// relative move now, or nothing.

export type QuantumOutcome =
  'completed' | 'blocked' | 'refused' | 'cancelled';

export interface QuantumRequest {
  /** Design units of travel, signed: what `move(input, {by})` asks
   * for. */
  by: number;
  /** The direction in SWEEP terms, +1 or -1. Different from `by`'s sign
   * whenever `per_unit` is negative, which on a Pascaline dial it is. */
  step: number;
}

export class TurnPlanner {
  /** Degrees of sweep one quantum is worth: the input's CURRENT nudge
   * amount times the published ratio. At the default that is
   * `1 × 36 = 36°`, one digit of a Pascaline dial. */
  readonly quantum: number;

  private readonly amount: number;

  private readonly perUnit: number;

  private originValue = 0;

  private sweepValue = 0;

  /** The sweep direction of the request in flight, or null. */
  private flight: number | null = null;

  private stalledStep = 0;

  constructor(amount: number, perUnit: number) {
    this.amount = Math.abs(amount);
    this.perUnit = perUnit;
    this.quantum = Math.abs(amount * perUnit);
  }

  /** Add one `pointermove`'s signed angle. The sweep is UNWRAPPED --
   * deltas accumulate -- so a drag of more than half a turn keeps
   * counting instead of folding back. */
  advance(delta: number): void {
    this.sweepValue += delta;
  }

  get sweep(): number {
    return this.sweepValue;
  }

  /** The sweep value the last COMMITTED quantum ended at. */
  get origin(): number {
    return this.originValue;
  }

  get outstanding(): boolean {
    return this.flight !== null;
  }

  /** The direction whose last request did not complete, or 0. */
  get stalled(): number {
    return this.stalledStep;
  }

  /** What to issue now, or null -- and marks it outstanding.
   *
   * The count of quanta owed is never stored: it is RECOMPUTED from
   * `sweep − origin` every time, so a maker who drags forward and back
   * nets out instead of paying for both. */
  next(): QuantumRequest | null {
    if (this.flight !== null || !(this.quantum > 0)) {
      return null;
    }
    const owed = this.sweepValue - this.originValue;
    if (Math.abs(owed) < this.quantum) {
      // Back inside one quantum: the maker backed off, so the stall
      // that a blocked request left is released.
      this.stalledStep = 0;
      return null;
    }
    const step = owed < 0 ? -1 : 1;
    if (this.stalledStep === step) {
      return null;
    }
    // Division, because `per_unit` is coordinate units per input unit
    // and may be negative: a sweep of −36° on `per_unit = −36` asks for
    // `+1` digit.
    const by = (owed / this.perUnit < 0 ? -1 : 1) * this.amount;
    this.flight = step;
    return { by, step };
  }

  /** A request this gesture issued has retired.
   *
   * `completed` advances the origin by one quantum and clears the
   * stall, so the next quantum is asked for at once -- which is how a
   * fast drag catches up. Anything else leaves the origin where it is,
   * so a drag into a stop reports blocked and leaves NO backlog, and
   * latches that direction until the maker backs off or reverses. */
  retire(outcome: QuantumOutcome): void {
    const step = this.flight;
    this.flight = null;
    if (step === null) {
      return;
    }
    if (outcome === 'completed') {
      this.originValue += step * this.quantum;
      this.stalledStep = 0;
    } else {
      this.stalledStep = step;
    }
  }
}

// ---------------------------------------------------------------------
// The pick's visibility filter (design D5, task 4.2).

/** As much of a three.js `Object3D` as the filter reads. */
export interface VisibilityNode {
  visible: boolean;
  parent: VisibilityNode | null;
}

/** Whether `object` and every ancestor up to and including `root` are
 * visible.
 *
 * three.js's `Raycaster` in this version does NOT consult
 * `Object3D.visible` at all -- `intersectObject` tests only `layers` --
 * so a hit on a part the navigator hid, or focused out, comes back like
 * any other and has to be filtered HERE. This one predicate is what
 * makes "a part the viewer is not showing is not touchable" true, since
 * `applyVisibility` sets `mesh.visible = inFocusedSubtree` and
 * `group.visible = false` for a hidden subtree.
 */
export function visibleUpTo(object: VisibilityNode,
                            root: VisibilityNode | null): boolean {
  let current: VisibilityNode | null = object;
  while (current !== null) {
    if (!current.visible) {
      return false;
    }
    if (current === root) {
      return true;
    }
    current = current.parent;
  }
  return true;
}
