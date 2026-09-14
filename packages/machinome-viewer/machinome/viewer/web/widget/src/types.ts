/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The manifest.json format written by solid_node/core/export.py

export type RawRotation = ['r', string, number[]];
export type RawTranslation = ['t', string[]];
export type RawOperation = RawRotation | RawTranslation;

// A part whose GEOMETRY follows the machine -- a spring, a belt, a loom
// -- travels as the analytic spec its evaluator reads plus one
// expression per parameter, never as a mesh: there is no per-frame
// artifact to publish, and evaluating shape is the same mechanism as
// evaluating pose with `geometry = f(params)` instead of
// `matrix = f(params)`.
export interface ManifestFlexible {
  // The technology that evaluates `spec`. A consumer that does not know
  // it refuses the document naming it, rather than rendering a wrong
  // shape -- the posture it already takes toward an undeclared driver.
  tech: string;
  // The evaluator's own document, embedded verbatim as the producer's
  // adapter serialized it. Opaque here on purpose: its schema belongs to
  // the evaluator, which is the only thing that reads it.
  spec: Record<string, unknown>;
  // One raw, unevaluated expression string per shape parameter, in the
  // same evaluation scope and with the same verbatim guarantee as an
  // operation's: `$t` and qualified driver ids survive to the client.
  params: Record<string, string>;
}

export interface ManifestNode {
  name: string;
  type: string;
  color: string | null;
  operations: RawOperation[];
  // A rigid node has a model (path relative to the manifest) and no
  // children; a non-rigid node has children.
  model?: string;
  // The builder publishes the source mtime with each model reference.  It is
  // part of the geometry identity: a source edit can retain the same path.
  mtime?: number;
  children?: ManifestNode[];
  // A flexible leaf: geometry from a spec, and neither a model nor
  // children below it. Present only in a version 3 document.
  flexible?: ManifestFlexible;
}

// Every document version this package renders. The producer emits the
// LOWEST version its content needs -- a document holding no flexible
// node is byte-identical to the version 2 it always was -- so accepting
// the whole union is accepting exactly what the producer can emit.
export type ManifestVersion = 1 | 2 | 3 | 4 | 5;

// One entry of a version-4 document's shared-subexpression table
// (OpenSpec `read-expression-bindings`, ADR-044). `expression` names
// only `$t`, declared driver ids and entries earlier in the array --
// the ordering guarantee `bindings.ts` validates and relies on.
export interface ManifestBinding {
  name: string;
  expression: string;
}

// One declared driver, as the producer publishes it. Presentation
// metadata only: `range` is never a clamp.
export interface ManifestDriver {
  default: number;
  range: number[] | null;
  unit: string | null;
  dtype: string | null;
  scale: number | null;
}

// One declared instruction: what a button press means. `targets` are in
// DESIGN units, keyed by qualified driver id; the conversion to native
// driver units happens here, once, through the driver table.
export interface ManifestInstruction {
  /** Where the drivers LAND. An absolute instruction states these. */
  targets?: Record<string, number>;
  /** How far the drivers TRAVEL from where they stand. A relative
   * instruction states these instead, and travels only in a version 5
   * document: below it a relative instruction is omitted from the table
   * altogether, so a shipped viewer reading `targets` off every entry
   * cannot meet one. */
  by?: Record<string, number>;
  duration: number;
}

// One declared control: how a PERSON issues a request on a part
// (solid-node ADR-112, OpenSpec `declare-controls-on-parts`). A version
// 5 document whose tree declares at least one carries a `controls`
// table keyed by qualified control name; the entry carries no
// expression, so it never enters the `bindings` pass.
//
// Deliberately typed as the producer publishes it -- `per_unit`, not
// `perUnit` -- because this is the wire shape. `partControls.ts`
// validates it field by field and hands back a `LoadedControl`.
export interface ManifestControl {
  /** `"button"` -- a press submitting an instruction -- or `"turn"` --
   * a drag issuing relative moves on an input. */
  kind: string;
  /** The node-name path, from the document's root down, of the node a
   * person touches. */
  part: string[];
  /** A button's instruction: a key of the same document's
   * `instructions`. */
  instruction?: string;
  /** A turn's input: a key of the same document's `drivers`. */
  input?: string;
  /** The coordinate units the part moves per DESIGN unit the input
   * travels, MEASURED at the rest bank. */
  per_unit?: number;
  /** The node-name path of the node the control's coordinate poses. */
  joint: string[];
  /** That coordinate's qualified id: a key of `program.coordinates`. */
  coordinate: string;
  /** The joint's axis, in the joint node's OWN frame. */
  axis: number[];
  /** The point the joint moves the part about, in the same frame. */
  origin: number[];
}

export interface Manifest {
  format: string;
  version: ManifestVersion;
  animation: {
    fps: number;
    frames: number;
    // The seconds of machine time one turn of `$t` covers, published when
    // the root declares a time base (solid-node `declared-time-base`).
    // Additive: the expressions already carry `$t * loop`, so a document
    // without it plays `frames / fps` exactly as it always did.
    loop?: number;
  };
  // Every qualified driver id the document's expressions may reference.
  // A version 1 document has no table at all, and a version 2 document
  // whose tree declares no drivers has an empty one -- both mean the
  // same thing to this viewer: nothing to bind but `$t`.
  drivers?: Record<string, ManifestDriver>;
  // Additive within version 2: an instruction moves a driver, so a
  // document carrying instructions carries a non-empty `drivers` table
  // too, and a consumer without driver evaluation already refuses that
  // loudly -- nobody can misread the added key.
  instructions?: Record<string, ManifestInstruction>;
  // Every subexpression that occurs more than once among this document's
  // expressions, published once and referenced by name (version 4).
  // Absent from a document with nothing shared, so a version 1-3
  // document is typed exactly as it is without this change.
  bindings?: ManifestBinding[];
  /** The compiled mechanical program a version 5 document carries: the
   * bank of coordinates with their rest values, the values the program
   * computes and never stores, the edges in propagation order with their
   * expressions, affinity and jump plans, the declared bounds, the
   * reaching-inputs table, the five constants the algorithm is defined
   * by, and the free name elapsed simulation seconds bind to.
   *
   * Deliberately opaque here: `run/program.ts` reads it field by field
   * and refuses by name everything the engine cannot execute, which is a
   * validation no structural type can perform. */
  program?: unknown;
  /** The controls a version 5 document's parts carry, keyed and ordered
   * by qualified control name (solid-node ADR-112 §6). ADDITIVE within
   * version 5: the key is absent when the tree declares none, and a
   * document carrying none is read exactly as it was before this viewer
   * knew of controls. Validated by `partControls.ts`'s `readControls`
   * at load, on `assertRenderable`'s own refusal surface. */
  controls?: Record<string, ManifestControl>;
  root: ManifestNode;
}
