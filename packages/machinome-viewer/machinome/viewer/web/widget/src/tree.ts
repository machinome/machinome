/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Mirrors the manifest tree as a three.js Group hierarchy. Each node's
// local matrix is recomputed from scratch from its evaluated operations
// on every time change (stateless per frame), and three.js composes
// ancestors naturally: world = ancestors' matrices * own matrix, the
// same composition as AbstractBaseNode.mesh (own operations first,
// then each ancestor's, up the tree).

import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { mergeVertices } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import { ManifestMarking, ManifestNode, RawOperation } from './types';
import { EvalScope, evalExpr, freeVariables, TIME_ID } from './evaluator';
import { bindingRootsEqual } from './expressions';
import { BindingTable, EMPTY_BINDINGS } from './bindings';
import { FlexibleShape } from './flexible';

/** What changed since the last update, when not everything did.
 *
 * `drivers` holds the qualified ids whose values moved this frame. A
 * node recomputes its matrix when time advanced and it reads `$t`, or
 * when one of its own free variables is in that set -- so a slider on
 * one axis costs the operations of that axis and nothing else. */
export interface ChangeSet {
  time: boolean;
  drivers: ReadonlySet<string>;
}

export type Changed = ChangeSet | 'all';

const stlLoader = new STLLoader();

export type AssemblyPath = readonly string[];

export interface AssemblyNode {
  name: string;
  path: string[];
  color: string | null;
  model: boolean;
  children: AssemblyNode[];
}

export function assemblyPathKey(path: AssemblyPath): string {
  return JSON.stringify(path);
}

export function materialForColor(color: string | null): THREE.Material {
  if (color === null) {
    return new THREE.MeshNormalMaterial();
  }
  return new THREE.MeshStandardMaterial({
    color: new THREE.Color(color),
    metalness: 0.1,
    roughness: 0.6,
  });
}

/** The anti-z-fighting lift, in document units (millimetres).
 *
 * The artifact carries NO offset -- machinome design D5 states the
 * offset is the VIEWER's rendering constant, not a claim about where the
 * part's surface is -- so the viewer supplies it, and `polygonOffset`
 * alone cannot: its units are denominated in the depth buffer's smallest
 * resolvable difference, which varies with the camera, so no fixed unit
 * count is a fixed world bias.
 *
 * The magnitude is a DERIVED BOUND, not a guess. The producer subdivides
 * a wrapped decal so it follows its cylinder to within the part's own
 * tessellation precision `t` (the part's declared `linear_deflection`,
 * or the framework default 0.1 mm), and chords sag INWARD, so the depth
 * of any interpenetration is bounded by the decal's own chordal sag, at
 * most `t`. 0.15 is 1.5x the framework default: it covers every part
 * declaring no tolerance and every part declaring up to 0.15 mm, with
 * margin. The residual is recorded rather than hidden -- a part
 * declaring a `linear_deflection` ABOVE 0.15 mm may still punch through,
 * and the remedy then is a framework finding (publish the tolerance, or
 * lift in the producer), not a viewer knob. */
export const MARKING_LIFT = 0.15;

/** Displace every vertex along its OWN normal by {@link MARKING_LIFT}.
 *
 * A rigid transform preserves it, so the lift stays perpendicular to the
 * surface under every operation the part carries -- which is what makes
 * it a rendering constant and not a placement.
 *
 * The direction relies on a property the producer HAS and its export
 * spec does not yet promise: a decal's triangles wind with their normal
 * AWAY from the part. `tree.test.ts` pins that on the committed fixture,
 * so a producer that ever wound the other way fails there by name rather
 * than drawing digits inside the roll. */
export function liftAlongNormals(geometry: THREE.BufferGeometry): void {
  const position = geometry.getAttribute('position');
  const normal = geometry.getAttribute('normal');
  if (position === undefined || normal === undefined) {
    return;
  }
  for (let index = 0; index < position.count; index += 1) {
    position.setXYZ(
      index,
      position.getX(index) + normal.getX(index) * MARKING_LIFT,
      position.getY(index) + normal.getY(index) * MARKING_LIFT,
      position.getZ(index) + normal.getZ(index) * MARKING_LIFT,
    );
  }
  position.needsUpdate = true;
  // The vertices moved: anything already derived from where they were
  // is stale, and `visibleBounds` recomputes a null box on demand.
  geometry.boundingBox = null;
  geometry.boundingSphere = null;
}

/** A decal's material: its OWN declared colour (inheritance never
 * reaches a marking), drawn over the surface it lies on.
 *
 * `DoubleSide` because an open sheet has a back and must not vanish when
 * the camera crosses its plane; `polygonOffset` at the MINIMUM bias
 * that separates two surfaces the depth buffer cannot tell apart, on top
 * of the world-space lift, for the case a viewer is zoomed far enough
 * out that 0.15 mm falls below one depth-buffer step. Staying at the
 * minimum is deliberate: a large offset starts letting a decal show
 * through a part standing genuinely in front of it. Depth is written
 * normally -- a decal that did not would show through everything drawn
 * after it. */
export function markingMaterial(color: string): THREE.Material {
  const material = materialForColor(color) as THREE.MeshStandardMaterial;
  material.side = THREE.DoubleSide;
  material.polygonOffset = true;
  material.polygonOffsetFactor = -1;
  material.polygonOffsetUnits = -1;
  return material;
}

/** One marking as this viewer holds it: the entry the document
 * published, and the mesh drawn for it.
 *
 * `freshFromArtifact` is the node's own flag, per marking and
 * INDEPENDENT of it, for the reason the node's exists: the manifest
 * publishes after the artifact, so the reconcile that follows an
 * `artifactChanged` would otherwise see a moved `mtime` for bytes
 * already on screen and refetch them. A marking's stamp and its part's
 * are independent, which is the whole point of the producer's currency
 * split. */
export interface LoadedMarking {
  name: string;
  model: string;
  mtime: number | undefined;
  color: string;
  mesh: THREE.Mesh;
  freshFromArtifact: boolean;
}

function disposeMesh(mesh: THREE.Mesh): void {
  mesh.geometry.dispose();
  const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
  materials.forEach((material) => material.dispose());
}

function markingRecord(entry: ManifestMarking, mesh: THREE.Mesh): LoadedMarking {
  return {
    name: entry.name, model: entry.model, mtime: entry.mtime,
    color: entry.color, mesh, freshFromArtifact: false,
  };
}

export class WidgetTree {
  group: THREE.Group;
  operations: RawOperation[];
  children: WidgetTree[];
  name: string;
  private model: string | undefined;
  private mtime: number | undefined;
  private color: string | null;
  // Set when artifactChanged() has already fetched this node's current
  // geometry. The manifest publishes after the artifact (PRD D3), so the
  // reconcile that follows would otherwise see an unmoved mtime as stale and
  // refetch bytes already on screen. Consumed by the next reconcile either way,
  // so a later genuine change is still detected.
  private freshFromArtifact = false;
  // The union of this node's operations' free variables, CLOSED OVER the
  // document's bindings table (OpenSpec `read-expression-bindings`,
  // design D5, D6): the inputs the operations actually read, not merely
  // the names they mention. Computed once and dropped whenever a
  // reconcile replaces the operations or installs a different table.
  private freeVars: ReadonlySet<string> | undefined;
  // A flexible leaf's geometry: no model to fetch, no children below it,
  // and its own dependency set beside the operations' one.
  private flexible: FlexibleShape | undefined;
  // The document's bindings table, document-scoped (design D2):
  // `EMPTY_BINDINGS` for a document with nothing shared, so a version
  // 1-3 document -- or any construction site that omits this parameter,
  // tree.test.ts's and flexible.test.ts's own included -- follows the
  // path it followed before this change.
  private bindings: BindingTable;

  /** What this part CARRIES on its surface, in document order (OpenSpec
   * `draw-what-a-part-carries`, design D2). Empty for a node that
   * declares none, which builds no group and adds no object: its scene
   * graph is byte-for-byte the one it had before this viewer could draw
   * a marking. */
  markings: LoadedMarking[] = [];
  // The decals' own child group inside this node's group -- built
  // lazily, only for a node that carries markings.
  //
  // Membership in the part's group is what buys everything: the part's
  // local matrix is the decal's PARENT matrix, so pose, `$t` animation
  // and a run's committed bank carry the decal with no new code, which
  // is exactly why the producer publishes no placement. A group rather
  // than tagged meshes because three existing sites filter the DIRECT
  // mesh children of a node's group, and two of them would be wrong for
  // a decal: `removeMesh` would destroy the decals whenever the part's
  // own model was replaced, and `setColor` would repaint a decal in the
  // part's inherited colour. A group is correct by construction at both,
  // and at every site written later.
  private decals: THREE.Group | undefined;

  // Resolves when this node's mesh (if any) and all descendants
  // finished loading, so the camera can be fit to the actual bounds.
  loaded: Promise<void>;

  constructor(data: ManifestNode, baseUrl: string,
              inheritedColor: string | null = null,
              bindings: BindingTable = EMPTY_BINDINGS) {
    this.group = new THREE.Group();
    this.group.matrixAutoUpdate = false;
    this.name = data.name;
    this.operations = data.operations;
    this.children = [];
    this.bindings = bindings;

    const color = data.color ?? inheritedColor;
    this.color = color;
    this.model = data.model;
    this.mtime = data.mtime;
    const pending: Promise<void>[] = [];

    if (data.model) {
      pending.push(this.loadModel(baseUrl + data.model, color));
    }

    if ((data.markings ?? []).length > 0) {
      pending.push(this.loadMarkings(data.markings!, baseUrl));
    }

    // Nothing to fetch: the geometry is the spec, and the first update
    // fills it. That update is the mount's own (`replaceTree` calls it
    // before the camera frames anything), so a flexible node is on
    // screen at the driver defaults exactly as a rigid one is.
    if (data.flexible) {
      this.flexible = new FlexibleShape(data.name, data.flexible, color, bindings);
      this.group.add(this.flexible.mesh);
    }

    for (const childData of data.children ?? []) {
      const child = new WidgetTree(childData, baseUrl, color, bindings);
      this.children.push(child);
      this.group.add(child.group);
      pending.push(child.loaded);
    }

    this.loaded = Promise.all(pending).then(() => undefined);
  }

  private async loadModel(url: string, color: string | null): Promise<void> {
    this.group.add(await loadMesh(url, color));
  }

  /** Fetch every decal, then add them in DOCUMENT order -- the order
   * the producer declared them in, which no race between fetches may
   * disturb. */
  private async loadMarkings(entries: ManifestMarking[],
                             baseUrl: string): Promise<void> {
    const group = this.markingGroup();
    this.markings = await Promise.all(entries.map(async (entry) => markingRecord(
      entry, await loadDecal(baseUrl + entry.model, entry.color))));
    this.markings.forEach((record) => group.add(record.mesh));
  }

  private markingGroup(): THREE.Group {
    if (this.decals === undefined) {
      this.decals = new THREE.Group();
      this.group.add(this.decals);
    }
    return this.decals;
  }

  /** Replace every mesh that names this artifact.  Unknown artifacts are
   * deliberately harmless: a manifest update is authoritative for removals. */
  async artifactChanged(path: string, baseUrl: string): Promise<void> {
    const replacements: Array<{ tree: WidgetTree; mesh: THREE.Mesh }> = [];
    // The markings that name this artifact, beside the nodes that do
    // (design D5). Routing is exact string match, so there is no
    // ambiguity -- and in practice no collision is even possible, the
    // producer naming a decal `<basepath>.marking-<name>.stl`.
    const decals: Array<{ tree: WidgetTree; record: LoadedMarking;
                          mesh: THREE.Mesh }> = [];
    const collect = (node: WidgetTree) => {
      if (node.model === path) {
        replacements.push({ tree: node, mesh: undefined as unknown as THREE.Mesh });
      }
      node.markings.filter((record) => record.model === path)
        .forEach((record) => decals.push({
          tree: node, record, mesh: undefined as unknown as THREE.Mesh,
        }));
      node.children.forEach(collect);
    };
    collect(this);
    await Promise.all([
      ...replacements.map(async (replacement) => {
        replacement.mesh = await loadMesh(baseUrl + path, replacement.tree.color);
      }),
      ...decals.map(async (decal) => {
        decal.mesh = await loadDecal(baseUrl + path, decal.record.color);
      }),
    ]);
    replacements.forEach(({ tree, mesh }) => {
      tree.replaceMesh(mesh);
      tree.freshFromArtifact = true;
    });
    decals.forEach(({ tree, record, mesh }) => {
      tree.markingGroup().remove(record.mesh);
      disposeMesh(record.mesh);
      record.mesh = mesh;
      record.freshFromArtifact = true;
      tree.orderMarkings();
    });
  }

  /** Fetch every stale mesh before changing the live tree.  This makes a
   * rejected document update leave the previously rendered scene intact. */
  async reconcile(data: ManifestNode, baseUrl: string,
                  inheritedColor: string | null = null,
                  bindings: BindingTable = EMPTY_BINDINGS): Promise<void> {
    const apply = await this.prepareReconcile(data, baseUrl, inheritedColor, bindings);
    apply();
  }

  private async prepareReconcile(data: ManifestNode, baseUrl: string,
                                 inheritedColor: string | null,
                                 bindings: BindingTable): Promise<() => void> {
    const nextColor = data.color ?? inheritedColor;
    const skipMtimeCheck = this.freshFromArtifact;
    const modelChanged = this.model !== data.model || (this.mtime !== data.mtime && !skipMtimeCheck);
    const replacement = data.model && modelChanged
      ? await loadMesh(baseUrl + data.model, nextColor) : undefined;

    // Built here rather than below for the reason the mesh above is:
    // a `tech` this viewer cannot evaluate must be refused BEFORE the
    // live tree is touched, so a rejected document leaves the scene it
    // was going to replace intact. A spec that did not change needs no
    // replacement at all -- only the expressions are rebound, and the
    // buffers behind them survive the republish.
    const nextFlexible = data.flexible
      && !this.flexible?.describes(data.flexible)
      ? new FlexibleShape(data.name, data.flexible, nextColor, bindings) : undefined;

    // A decal's identity is its own `model` path and its own `mtime`,
    // exactly as a node's is, and the two are INDEPENDENT: the
    // producer's currency split exists so that editing artwork moves
    // the marking's stamp and leaves the part's STL current. Matched
    // across a republish BY NAME -- a marking's name is its declaring
    // attribute, so it is unique on its node -- and fetched here,
    // before the live tree is touched, so a decal that will not fetch
    // leaves the whole previous scene standing.
    const held = new Map(this.markings.map((record) => [record.name, record]));
    const nextMarkings = await Promise.all((data.markings ?? []).map(
      async (entry) => {
        const current = held.get(entry.name);
        const stale = current === undefined
          || current.model !== entry.model
          || (current.mtime !== entry.mtime && !current.freshFromArtifact);
        return {
          entry,
          current,
          mesh: stale
            ? await loadDecal(baseUrl + entry.model, entry.color) : undefined,
        };
      }));

    const existing = uniqueByName(this.children);
    const incoming = uniqueDataByName(data.children ?? []);
    const nextChildren = await Promise.all((data.children ?? []).map(async (childData) => {
      const child = existing.get(childData.name);
      if (!child || !incoming.has(childData.name)) {
        const created = new WidgetTree(childData, baseUrl, nextColor, bindings);
        await created.loaded;
        return { tree: created, apply: () => undefined };
      }
      return {
        tree: child,
        apply: await child.prepareReconcile(childData, baseUrl, nextColor, bindings),
      };
    }));

    // OpenSpec `read-expression-bindings`, design D6: what an expression
    // READS follows the table it is read through, so a republish whose
    // table differs from the one this node holds -- the D3 map
    // comparison, reused here -- invalidates the free set EVEN WHEN the
    // operations' own text did not change (an operation naming "_b3"
    // stays exactly "_b3" while what "_b3" reads changes underneath it).
    // A republish that changed neither invalidates nothing.
    const operationsChanged = !operationsEqual(this.operations, data.operations);
    const bindingsChanged = !bindingRootsEqual(this.bindings.roots(), bindings.roots());

    return () => {
      // All nested fetches succeeded.  Only now is it safe to mutate the
      // live tree, including its children.
      nextChildren.forEach((child) => child.apply());
      if (replacement) {
        this.replaceMesh(replacement);
      } else if (!data.model && this.model) {
        this.removeMesh();
      }
      this.name = data.name;
      this.model = data.model;
      this.mtime = data.mtime;
      this.freshFromArtifact = false;
      this.operations = data.operations;
      this.bindings = bindings;
      if (operationsChanged || bindingsChanged) {
        this.freeVars = undefined;
      }
      this.setColor(nextColor);

      if (nextFlexible) {
        this.removeFlexible();
        this.flexible = nextFlexible;
        this.group.add(nextFlexible.mesh);
      } else if (data.flexible) {
        this.flexible!.rebind(data.flexible, bindings);
      } else {
        this.removeFlexible();
      }

      this.applyMarkings(nextMarkings);

      const retained = new Set(nextChildren.map((child) => child.tree));
      this.children.filter((child) => !retained.has(child)).forEach((child) => {
        this.group.remove(child.group);
        child.dispose();
      });
      this.children = nextChildren.map((child) => child.tree);
      this.children.forEach((child) => {
        this.group.remove(child.group);
        this.group.add(child.group);
      });
    };
  }

  /** Swap, add and remove this node's decals, from records whose meshes
   * are already fetched. Order follows the DOCUMENT, never the order
   * the fetches happened to finish in. */
  private applyMarkings(next: Array<{
    entry: ManifestMarking;
    current: LoadedMarking | undefined;
    mesh: THREE.Mesh | undefined;
  }>): void {
    const records = next.map(({ entry, current, mesh }) => {
      if (mesh !== undefined) {
        if (current !== undefined) {
          this.decals?.remove(current.mesh);
          disposeMesh(current.mesh);
        }
        return markingRecord(entry, mesh);
      }
      // Retained: only the colour can have moved, and colour is not
      // geometry identity, so the material is replaced in place and the
      // old one disposed, with no refetch (design D4).
      const record = current!;
      if (record.color !== entry.color) {
        const previous = record.mesh.material;
        record.mesh.material = markingMaterial(entry.color);
        (Array.isArray(previous) ? previous : [previous])
          .forEach((material) => material.dispose());
      }
      record.color = entry.color;
      record.mtime = entry.mtime;
      record.model = entry.model;
      record.freshFromArtifact = false;
      return record;
    });

    const survivors = new Set(records.map((record) => record.mesh));
    this.markings.filter((record) => !survivors.has(record.mesh))
      .forEach((record) => {
        this.decals?.remove(record.mesh);
        disposeMesh(record.mesh);
      });
    this.markings = records;

    if (records.length === 0) {
      if (this.decals !== undefined) {
        this.group.remove(this.decals);
        this.decals = undefined;
      }
      return;
    }
    this.orderMarkings();
  }

  /** Re-seat every decal in the group in document order. */
  private orderMarkings(): void {
    const group = this.markingGroup();
    this.markings.forEach((record) => {
      group.remove(record.mesh);
      group.add(record.mesh);
    });
  }

  private replaceMesh(mesh: THREE.Mesh): void {
    this.removeMesh();
    this.group.add(mesh);
  }

  private removeFlexible(): void {
    if (!this.flexible) return;
    this.group.remove(this.flexible.mesh);
    this.flexible.dispose();
    this.flexible = undefined;
  }

  private removeMesh(): void {
    this.group.children.filter((child): child is THREE.Mesh => child instanceof THREE.Mesh)
      .forEach((mesh) => {
        this.group.remove(mesh);
        mesh.geometry.dispose();
        const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
        materials.forEach((material) => material.dispose());
      });
  }

  private setColor(color: string | null): void {
    if (this.color === color) return;
    this.color = color;
    if (this.flexible) {
      // Its own material, because a swept indexed surface is shaded
      // flat to match the rigid parts an STL already renders that way.
      this.flexible.setColor(color);
      return;
    }
    this.group.children.filter((child): child is THREE.Mesh => child instanceof THREE.Mesh)
      .forEach((mesh) => {
        const previous = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
        mesh.material = materialForColor(color);
        previous.forEach((material) => material.dispose());
      });
  }

  /** Whether anything under here reads `$t`, and therefore whether the
   * document has a timeline to play. Driver-driven motion is not this:
   * a machine posed by its drivers has no period to scrub. */
  get animated(): boolean {
    return (
      this.free.has(TIME_ID) ||
      (this.flexible?.free.has(TIME_ID) ?? false) ||
      this.children.some((child) => child.animated)
    );
  }

  /** Every input this node's own operations read, `$t` included -- a
   * binding name closed over the document's table (design D5, D6), so
   * an operation that is only a binding name resolving through to `$t`
   * counts as reading `$t`, though the text never mentions it. */
  private get free(): ReadonlySet<string> {
    if (this.freeVars === undefined) {
      const found = new Set<string>();
      for (const operation of this.operations) {
        const expressions = operation[0] === 'r'
          ? [operation[1]] : operation[1];
        for (const expression of expressions) {
          for (const name of freeVariables(expression)) {
            found.add(name);
          }
        }
      }
      this.freeVars = this.bindings.closure(found);
    }
    return this.freeVars;
  }

  private needsUpdate(changed: Changed): boolean {
    return touchedBy(this.free, changed);
  }

  assembly(path: AssemblyPath = []): AssemblyNode {
    return {
      name: this.name,
      path: [...path],
      color: this.color,
      model: this.model !== undefined,
      children: this.children.map((child) => child.assembly([...path, child.name])),
    };
  }

  hasPath(path: AssemblyPath): boolean {
    try {
      this.requirePath(path);
      return true;
    } catch {
      return false;
    }
  }

  requirePath(path: AssemblyPath): WidgetTree {
    let current: WidgetTree = this;
    for (const name of path) {
      const matches = current.children.filter((child) => child.name === name);
      if (matches.length !== 1) {
        const reason = matches.length === 0 ? 'Unknown' : 'Ambiguous';
        throw new Error(`${reason} assembly path: ${path.join('/') || '<root>'}`);
      }
      current = matches[0];
    }
    return current;
  }

  applyVisibility(focusedPath: AssemblyPath | null,
                  hiddenPaths: ReadonlySet<string>): void {
    const visit = (node: WidgetTree, path: string[]) => {
      const inFocusedSubtree = focusedPath === null
        || isPathPrefix(focusedPath, path);
      const preservesFocusedTransform = focusedPath !== null
        && isPathPrefix(path, focusedPath);
      node.group.visible = (inFocusedSubtree || preservesFocusedTransform)
        && !hiddenPaths.has(assemblyPathKey(path));
      node.group.children
        .filter((child): child is THREE.Mesh => child instanceof THREE.Mesh)
        .forEach((mesh) => { mesh.visible = inFocusedSubtree; });
      // The one line the sub-group costs (design D2). The case that
      // matters is a part that is an ANCESTOR of the focused node: its
      // group stays visible to preserve the transform, while its own
      // surface must not be drawn -- and its decals are its own surface.
      if (node.decals !== undefined) {
        node.decals.visible = inFocusedSubtree;
      }
      node.children.forEach((child) => visit(child, [...path, child.name]));
    };
    visit(this, []);
  }

  // Recompute local matrices under `scope` (animation time 0..1 plus the
  // document's driver values). `changed` bounds the work: a node whose
  // free variables none of it touches keeps the matrix it has.
  update(scope: EvalScope, changed: Changed = 'all'): void {
    if (this.needsUpdate(changed)) {
      this.group.matrix.copy(operationsMatrix(this.operations, scope));
    }
    // Shape follows the same rule pose does, off its own dependency
    // set: a spring is re-evaluated on the frames its `params`
    // expressions name a changed input, and a driver none of them names
    // costs it nothing.
    if (this.flexible && touchedBy(this.flexible.free, changed)) {
      this.flexible.evaluate(scope);
    }
    for (const child of this.children) {
      child.update(scope, changed);
    }
  }

  dispose(): void {
    this.group.traverse((object) => {
      if (!(object instanceof THREE.Mesh)) {
        return;
      }
      object.geometry.dispose();
      const materials = Array.isArray(object.material)
        ? object.material : [object.material];
      materials.forEach((material) => material.dispose());
    });
  }
}

/** Whether `changed` touches anything in `free`.
 *
 * The one rule, applied to both dependency sets a node has: the free
 * variables of its operations decide whether its MATRIX recomputes, and
 * the free variables of a flexible part's `params` decide whether its
 * GEOMETRY does. */
function touchedBy(free: ReadonlySet<string>, changed: Changed): boolean {
  if (changed === 'all') return true;
  if (changed.time && free.has(TIME_ID)) return true;
  for (const id of changed.drivers) {
    if (free.has(id)) return true;
  }
  return false;
}

/** Value equality for one node's own operations (design D6): a republish
 * always hands `reconcile` a FRESH array parsed from JSON, so a
 * reference comparison would report "changed" every time even when the
 * text is byte-identical -- exactly the case (an operation naming "_b3"
 * that stays "_b3") this equality exists to tell apart from a genuine
 * edit. `RawOperation` is plain JSON-safe data, so structural equality
 * is exactly `JSON.stringify` equality. */
function operationsEqual(a: readonly RawOperation[], b: readonly RawOperation[]): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

function isPathPrefix(prefix: AssemblyPath, path: AssemblyPath): boolean {
  return prefix.length <= path.length
    && prefix.every((part, index) => part === path[index]);
}

async function loadMesh(
  url: string, color: string | null,
  material: (color: string | null) => THREE.Material = materialForColor,
): Promise<THREE.Mesh> {
  const geometry = await stlLoader.loadAsync(url);
  geometry.computeVertexNormals();
  return new THREE.Mesh(geometry, material(color));
}

/** Weld the sheet, average its normals, and lift it (design D3).
 *
 * The welding is not cosmetic. An STL arrives NON-INDEXED -- one private
 * copy of each corner per facet -- so `computeVertexNormals` gives every
 * copy its own FACE normal, and lifting each along that normal pulls
 * adjacent facets APART. The sheet tears along every internal edge and
 * the part shows through the cracks: measured on the fixture's wrapped
 * decal (448 facets on R = 9.45 at a 0.05 mm deflection, an 11.8-degree
 * turn between neighbours), the tear is 2 * 0.15 * sin(5.9 deg) = 0.031
 * mm, which draws a visible grid over the digits from 30 mm away and
 * widens with the lift.
 *
 * Design D3 says AVERAGED vertex normals, and averaging is exactly what
 * welding buys: co-located corners become one vertex carrying the mean
 * of the facet normals around it, the whole sheet moves off the surface
 * together, and the lift stays perpendicular to it. */
export function liftDecal(geometry: THREE.BufferGeometry): THREE.BufferGeometry {
  // The normal attribute is dropped BEFORE welding because
  // `mergeVertices` merges only vertices agreeing in every attribute,
  // and the per-facet normals are precisely what disagrees.
  const welded = mergeVertices(geometry.clone().deleteAttribute('normal'));
  welded.computeVertexNormals();
  liftAlongNormals(welded);
  return welded;
}

/** A decal, through exactly the path a model takes (design D1): the
 * artifact is a binary STL like any other, and nothing about it needs a
 * second loader, a second cache or a second failure mode. What is added
 * is the viewer's own rendering constant, and only that. */
async function loadDecal(url: string, color: string): Promise<THREE.Mesh> {
  const mesh = await loadMesh(url, color,
                              (own) => markingMaterial(own as string));
  const loadedGeometry = mesh.geometry;
  mesh.geometry = liftDecal(loadedGeometry);
  loadedGeometry.dispose();
  return mesh;
}

function uniqueByName(children: WidgetTree[]): Map<string, WidgetTree> {
  const names = new Map<string, WidgetTree>();
  const duplicate = new Set<string>();
  children.forEach((child) => names.has(child.name)
    ? duplicate.add(child.name) : names.set(child.name, child));
  duplicate.forEach((name) => names.delete(name));
  return names;
}

function uniqueDataByName(children: ManifestNode[]): Set<string> {
  const seen = new Set<string>();
  const duplicate = new Set<string>();
  children.forEach((child) => seen.has(child.name)
    ? duplicate.add(child.name) : seen.add(child.name));
  duplicate.forEach((name) => seen.delete(name));
  return seen;
}

// Operations listed [op1, op2, ...] apply to the solid in order:
// v' = opN(...(op1(v))), i.e. matrix = M_opN * ... * M_op1
export function operationsMatrix(ops: RawOperation[], scope: EvalScope): THREE.Matrix4 {
  const matrix = new THREE.Matrix4();
  const step = new THREE.Matrix4();
  const axis = new THREE.Vector3();

  for (const op of ops) {
    if (op[0] === 'r') {
      const angle = evalExpr(op[1], scope) * (Math.PI / 180);
      axis.set(op[2][0], op[2][1], op[2][2]).normalize();
      step.makeRotationAxis(axis, angle);
    } else {
      step.makeTranslation(
        evalExpr(op[1][0], scope),
        evalExpr(op[1][1], scope),
        evalExpr(op[1][2], scope),
      );
    }
    matrix.premultiply(step);
  }
  return matrix;
}
