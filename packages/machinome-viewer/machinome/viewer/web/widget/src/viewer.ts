/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { frameBounds, ViewerView } from './camera';
import {
  AssemblyChangeNotifier, AssemblyListener, AssemblyNavigation,
  AssemblyNavigationState,
} from './assembly';
import {
  controlPlan, resolveBaseUrl, resolveOptions, showsDriverChrome,
  showsPartControls, showsRunControls,
} from './options';
import {
  BreadcrumbSegment, ControlLayer, controlLayer, DriverControl,
  driverControl, formatDisplay, formatReadout,
} from './controls';
import {
  DriverListener, DriverStore, TriggerHandle, toNative,
} from './drivers';
import {
  Animation, advance, assertSpeed, cycleSecondsFor, formatMachineTime,
  ladderFor, timelinePosition, timelineTime,
} from './playback';
import {
  DEFAULT_NUDGE, formatOutcome, runControlLayer, runInputControl,
  transportPlan,
} from './runControls';
import type {
  JogPlan, NudgePlan, OutcomeReport, RunControlLayer, RunControlsInput,
  RunInputControl, RunInstructionControl, TransportPlan,
} from './runControls';
import { republishPlan } from './run/republish';
import type { RunIdentity } from './run/republish';
import { EvalScope, freeVariables, TIME_ID } from './evaluator';
import { releaseExpressions, retainExpressions } from './expressions';
import { BindingTable, bindingTable, EMPTY_BINDINGS } from './bindings';
import { loadProgram, uncomputedValues } from './run/program';
import type {
  LoadedProgram, ProgramCoordinate, RunDocument,
} from './run/program';
import { RunRuntime } from './run/runtime';
import type { CommittedFrame, Outcome } from './run/runtime';
import type { RunState } from './run/run';
import { posed, poseScope } from './run/pose';
import { evaluatesTech, knownTechnologies, specRefusal } from './flexible';
import { AssemblyNode, AssemblyPath, WidgetTree } from './tree';
import { Manifest, ManifestDriver, ManifestInstruction, ManifestNode } from './types';
import {
  chooseMode, intersectPlane, MIN_RADIUS, normalize3, readControls,
  sub3, sweepAngle, TurnPlanner, visibleUpTo, worldLine,
} from './partControls';
import type {
  LoadedControl, Ray, SweepMode, Vec3, WorldLine,
} from './partControls';
import { API_VERSION } from './version';

export type AnimationMode = 'inline' | 'toggle' | 'none' | 'external';
// Whether the widget presents the driver chrome itself. A host building
// its own instrument panel on the driving API asks for 'none' and keeps
// every method below (ADR-056 stage 3c, design D9).
export type DriverControlsMode = 'inline' | 'none';
// Whether the widget makes the parts a document's `controls` table
// names touchable (OpenSpec `drive-the-run-by-touch`, design D14).
// INDEPENDENT of `driverControls`, because a host that builds its own
// instrument panel still wants the dial pressable. What it gates is the
// cursor, the highlight, the title and the pick; `controls()` answers
// and the run API is whole either way.
export type PartControlsMode = 'inline' | 'none';
export type View = ViewerView;
export type { AssemblyNode, AssemblyPath } from './tree';
export type { AssemblyChange, AssemblyListener, AssemblyNavigationState } from './assembly';
export type VectorInput = THREE.Vector3 | readonly [number, number, number];
export interface ViewInput {
  camera: VectorInput;
  target: VectorInput;
}

export interface ViewerOptions {
  baseUrl?: string;
  animation?: AnimationMode;
  driverControls?: DriverControlsMode;
  partControls?: PartControlsMode;
  time?: number;
  /** Playback speed as a multiple of real time, for a document whose
   * `animation.loop` says what a turn is; default 1. */
  speed?: number;
  autoplay?: boolean;
  view?: ViewInput;
  up?: VectorInput;
  fov?: number;
  className?: string;
  role?: string;
  ariaLabel?: string;
  /** The run's own options, for a document carrying a program
   * (OpenSpec `run-in-the-worker`). The step size is settable ONCE,
   * here, and never afterwards. */
  run?: {
    dt?: number;
    record?: number | null;
    autostart?: boolean;
    /** What the on-screen nudge and jog controls ASK FOR (OpenSpec
     * `drive-the-run-on-screen`): a relative travel over a duration,
     * and a rate in design units per simulated second. They configure
     * the request, never a coordinate. */
    nudge?: { amount?: number; seconds?: number };
    jog?: { rate?: number };
  };
}

/** What a host drives a running document with (design §7). `move`,
 * `rate` and `trigger` resolve when the command RETIRES, with its final
 * status and the travel it admitted -- the one thing the pilot's model
 * insists every request reports. */
export interface RunHandle {
  identity(): string;
  dt(): number;
  tick(): number;
  /** Elapsed simulation seconds, which never wrap. */
  elapsed(): number;
  state(): Record<string, number>;
  coordinates(): Record<string, ProgramCoordinate>;
  start(): void;
  pause(): void;
  running(): boolean;
  /** Integrate exactly `ticks` ticks, whether or not the run is started
   * -- which is what makes a headless or a scripted drive
   * deterministic. */
  step(ticks?: number): Promise<void>;
  move(input: string, request: { by?: number; to?: number;
                                 duration?: number }): Promise<Outcome[]>;
  rate(input: string, rate: number): Promise<Outcome[]>;
  trigger(name: string): Promise<Outcome[]>;
  cancel(input: string): void;
  reset(): Promise<void>;
  snapshot(): Promise<RunState>;
  restore(state: RunState): Promise<void>;
  onCommit(listener: (frame: CommittedFrame) => void): () => void;
  onOutcome(listener: (outcome: Outcome) => void): () => void;
  /** False when the page could not create the worker and the same
   * engine is running on the rendering thread instead. */
  runsInWorker: boolean;
}

/** One declared control, as a host reads it (OpenSpec
 * `drive-the-run-by-touch`, design D15): its declaration carried
 * through, where its part stands on screen right now, and a point at
 * which a press actually reaches it right now.
 *
 * Positions are in VIEWPORT CSS pixels -- the frame every `DOMRect`
 * around them uses, and the frame a test's `page.mouse.click(x, y)`
 * takes -- so a host or a test acts on them without converting. */
export interface PartControlView {
  /** The table's key: the control's qualified display name. */
  name: string;
  kind: 'button' | 'turn';
  part: string[];
  /** A button's instruction. */
  instruction?: string;
  /** A turn's input. */
  input?: string;
  /** A turn's published ratio. */
  perUnit?: number;
  joint: string[];
  coordinate: string;
  /** The part's on-screen bounds, or null when the part is not visible
   * or is wholly off screen. */
  rect: { x: number; y: number; width: number; height: number } | null;
  /** A point a press reaches this control at right now, or null when
   * none does. Found the way a press finds it -- by raycasting under
   * the same nearest-visible-hit rule -- because the centre of a dial's
   * bounding rectangle is its axle, which may be a hole. */
  point: { x: number; y: number } | null;
}

export interface ViewerHandle {
  dispose(): void;
  view(): View;
  reload(): Promise<void>;
  artifactChanged(path: string): Promise<void>;
  manifestChanged(): Promise<void>;
  assembly(): AssemblyNode;
  setRoot(path: AssemblyPath | null): void;
  setVisible(path: AssemblyPath, visible: boolean): void;
  /** The navigation state: the focused root and the explicitly hidden
   * paths, as a serializable snapshot the handle does not later modify
   * (design D1). Needs no tree and so never throws. */
  navigation(): AssemblyNavigationState;
  /** Subscribe to every accepted operation that publishes a tree or
   * moves the focused root or the visibility state -- a host call, the
   * widget's own breadcrumb, or a targeted update -- and returns a
   * function that cancels the subscription. The notification means the
   * state last read may be stale; it observes and must not be used to
   * drive the viewer from inside itself (design D4-D6, ADR-049). */
  onAssemblyChange(listener: AssemblyListener): () => void;
  setTime(time: number): void;
  /** The playback speed, a multiple of real time (1 without a loop). */
  speed(): number;
  /** Set the playback speed; a non-positive or non-finite value is
   * refused. Accepted for a loop-less document, where it has no effect
   * on playback until a republish brings a loop. */
  setSpeed(speed: number): void;
  // The driving API (ADR-056 stage 3b). Values are NATIVE driver units
  // and ids are verbatim from the document; `range` never clamps.
  drivers(): Record<string, ManifestDriver>;
  driver(id: string): number;
  setDriver(id: string, value: number): void;
  onDriverChange(listener: DriverListener): () => void;
  instructions(): Record<string, ManifestInstruction>;
  trigger(name: string): TriggerHandle;
  /** The run of a document carrying a program, or `null` for one that
   * carries none -- which is every document of versions 1 to 4, so a
   * host asks one question and gets a truthful answer. */
  run(): RunHandle | null;
  /** The controls the loaded document declares (design D15), with each
   * part's current on-screen rectangle and a point a press reaches it
   * at. `[]` for a document that declares none, and the FULL listing
   * even when the affordance is suppressed: what a presentation choice
   * gates is the pixels and the pointer, never the interface. */
  controls(): PartControlView[];
  apiVersion: number;
}

/** Runs `action`, then retains the shared expression table (D8) --
 * ONLY once `action` has already succeeded, never before. `action` is
 * `mount()`'s initial document load (`loadDocument` -> `assertRenderable`,
 * the D10 refusal surface: an unreadable document version, an
 * unevaluable flexible technology, an undeclared driver id, or an
 * unsupported expression form). Retaining first and releasing only in
 * `dispose()` would hold the table forever for a refused document --
 * no handle, so no dispose() ever runs to release it, and a `solid
 * develop` session that republishes a broken document and then a good
 * one leaks a hold the good document's own eventual dispose() cannot
 * clear either, since it is one mount, one retain. Retaining only
 * after success keeps the pairing obvious: every retain call sees the
 * handle it belongs to actually get built.
 *
 * Exported (rather than inlined in `mount()`) for its own test:
 * `mount()` needs a DOM/WebGL environment this package's suite does
 * not set up. */
export async function mountRetained<T>(action: () => Promise<T>): Promise<T> {
  const result = await action();
  retainExpressions();
  return result;
}

export async function mount(
  target: HTMLElement | string,
  sourceUrl: string,
  options: ViewerOptions = {},
): Promise<ViewerHandle> {
  const container = resolveContainer(target);
  const resolved = resolveOptions(options);
  const baseUrl = resolveBaseUrl(sourceUrl, resolved.baseUrl ?? undefined);
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x556677, 1.2));
  const sun = new THREE.DirectionalLight(0xffffff, 1.5);
  sun.position.set(1, -1, 2);
  scene.add(sun);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  container.style.position = 'relative';
  renderer.domElement.style.display = 'block';
  if (resolved.className !== null) {
    renderer.domElement.className = resolved.className;
  }
  if (resolved.role !== null) {
    renderer.domElement.setAttribute('role', resolved.role);
  }
  if (resolved.ariaLabel !== null) {
    renderer.domElement.setAttribute('aria-label', resolved.ariaLabel);
  }
  container.appendChild(renderer.domElement);

  const camera = new THREE.PerspectiveCamera(resolved.fov, 1, 0.1, 10000);
  camera.up.copy(resolved.up);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.rotateSpeed = 0.5;

  let tree: WidgetTree | undefined;
  // The loaded document's bindings table (OpenSpec `read-expression-bindings`,
  // design D6): `EMPTY_BINDINGS` until the first successful load, and
  // installed into this field before the `tree.update(scope())` that
  // follows a (re)load -- the same place and order `drivers.reconcile(...)`
  // already runs before that update -- so no node can read a value
  // memoized against a table it no longer carries.
  let bindingsTable: BindingTable = EMPTY_BINDINGS;
  let time = resolved.time;
  let playing = false;
  let slider: HTMLInputElement | undefined;
  let controlElements: HTMLElement[] = [];
  let cycleSeconds = 1;
  // Real-time playback (OpenSpec `real-time-playback`): the document's
  // animation block as last loaded, the maker's or host's speed, and the
  // bar's speed control and machine-time readout when the block carries
  // a loop. `speed` survives a republish exactly as `time` does.
  let animation: Animation = { fps: 30, frames: 360 };
  let speed = resolved.speed;
  let speedControl: HTMLSelectElement | undefined;
  let readout: HTMLElement | undefined;
  let disposed = false;
  // The driver chrome, rebuilt whenever the focused layer or the
  // document changes and updated in place while values move.
  let driverChrome: DriverChrome | undefined;
  // True while a control of ours is writing a value, so the change we
  // hear back does not fight the input the maker is dragging.
  let drivingFromChrome = false;
  const assemblyNavigation = new AssemblyNavigation();
  // The public channel a host and this package's own future navigator
  // both read (design D4, ADR-049): no private path into the store,
  // mirroring drivers.ts's onDriverChange (`:709-714`). Notified once,
  // at the end of each operation that can move the state -- never from
  // inside AssemblyNavigation itself, which runs mid-update.
  const assemblyChanges = new AssemblyChangeNotifier();
  const notifyAssemblyChange = (): void => {
    if (!tree) {
      return;
    }
    assemblyChanges.notify({
      assembly: tree.assembly(),
      navigation: assemblyNavigation.state(),
    });
  };
  // One driver state for this mount, reconciled (not replaced) when the
  // document is republished, so a host's listeners and its current pose
  // survive a live rebuild.
  const drivers = new DriverStore();
  // The run of a version 5 document (OpenSpec `run-in-the-worker`). A
  // document carrying no program never builds one, and every version 1
  // to 4 mount is untouched by all of this.
  let runtime: RunRuntime | undefined;
  let loadedProgram: LoadedProgram | null = null;
  let bank: Record<string, number> = {};
  let elapsedSeconds = 0;
  // The running chrome (OpenSpec `drive-the-run-on-screen`). What a
  // maker has typed into the amount and rate fields is a REQUEST
  // setting, not a coordinate: it survives a republish and moves
  // nothing by itself. `outcomes` is the last report of each control,
  // by input id or instruction name; `refusal` is the run's own message
  // for a tick it refused, shown across the panel until the next tick
  // commits.
  let runChrome: RunChrome | undefined;
  const nudgeSettings: Record<string, NudgePlan> = {};
  const jogSettings: Record<string, JogPlan> = {};
  let outcomes: Record<string, OutcomeReport | null> = {};
  // How many requests each control still has in flight. A control
  // indicates the run until its OWN commands retire, which is a
  // different question from what its last report said: pressing an
  // instruction whose input the previous press still owns is refused
  // at once, and the movement already running is untouched.
  let pending: Record<string, number> = {};
  let refusal: string | null = null;
  let republishNotice: string | null = null;
  // The widest elapsed reading shown so far: the readout widens once and
  // never narrows, so the digits hold still as the run grows.
  let elapsedWidth = 0;

  // The PART controls (OpenSpec `drive-the-run-by-touch`). Everything
  // here is empty and inert for a document that declares none, which is
  // every document published before this viewer could read one.
  //
  // `partMeshes` is rebuilt at the three places a mesh can be replaced
  // -- `replaceTree`, `manifestChanged` and `artifactChanged` -- rather
  // than stamped onto meshes at construction, because a `userData`
  // field survives into `artifactChanged`'s freshly loaded replacement
  // only if every construction site remembers to set it (design D4).
  let loadedControls: LoadedControl[] = [];
  let partMeshes = new Map<THREE.Mesh, LoadedControl[]>();
  let partOf = new Map<string, THREE.Mesh[]>();
  const raycaster = new THREE.Raycaster();

  // Under a run the BANK is what poses the geometry, and the program's
  // clock name binds to elapsed simulation seconds beside it. `$t` stays
  // 0 for a version 5 document, because no expression in one reads it.
  const scope = (): EvalScope => (loadedProgram === null
    ? { time, drivers: drivers.scope(), bindings: bindingsTable.roots() }
    : poseScope(bank, loadedProgram.clock, elapsedSeconds, bindingsTable));

  // One door for a driver value, whether the maker moved a slider or
  // the host called setDriver: identical store semantics, identical
  // re-evaluation, and a listener cannot tell the two apart.
  const driveTo = (id: string, value: number) => {
    drivers.setDriver(id, value);
    // The set is answered this frame: only the operations naming this
    // driver are re-evaluated, and the rest keep the matrices they
    // have.
    tree?.update(scope(), { time: false, drivers: drivers.tick() });
    renderer.render(scene, camera);
  };

  const setTime = (next: number) => {
    time = Math.min(Math.max(next, 0), 1);
    if (slider) {
      slider.value = String(timelinePosition(time, animation.frames));
    }
    if (readout && animation.loop !== undefined) {
      readout.textContent = formatMachineTime(time * animation.loop, animation.loop);
    }
    tree?.update(scope(), { time: true, drivers: EMPTY });
    renderer.render(scene, camera);
  };

  const setSpeed = (next: number) => {
    speed = assertSpeed(next);
    cycleSeconds = cycleSecondsFor(animation, speed);
    // Speed keeps its one meaning -- a multiple of real time -- and
    // under a run it changes how many TICKS a wall second earns, never
    // the step size (design D7).
    runtime?.setSpeed(speed);
    if (speedControl && speedControl.value !== String(speed)) {
      fillSpeedControl(speedControl, speed);
    }
    refreshTransport();
  };

  /** The transport bar, from where the run actually stands. Called on
   * every committed frame and after anything a control did. */
  const refreshTransport = () => {
    if (runChrome === undefined) {
      return;
    }
    const plan = transportPlan({
      running: runtime?.running() ?? false,
      speed,
      elapsedSeconds: runtime?.elapsedSeconds() ?? 0,
      tick: runtime?.tick() ?? 0,
      refusal,
      elapsedWidth,
    });
    elapsedWidth = Math.max(elapsedWidth, plan.elapsed.length);
    runChrome.transport(plan);
  };

  /** Issue one request and report its outcome AT THE CONTROL that made
   * it (design D7), whatever the run answers.
   *
   * `key` is the input id or the instruction name -- the control the
   * maker pressed. A request made here goes through the same handle a
   * host would call, so the two are indistinguishable to the run, to
   * its listeners and to a readback.
   */
  const request = (key: string, unit: string | null,
                   issue: () => Promise<Outcome[]>,
                   at?: { x: number; y: number }): Promise<OutcomeReport | null> => {
    // A request into a paused run would report nothing, forever, which
    // is indistinguishable from a broken button: pressing a control is
    // asking the machine to move (design D5).
    if (runtime !== undefined && !runtime.running()) {
      runtime.start();
    }
    const started: OutcomeReport = {
      status: 'active', admitted: null, unit, message: null,
    };
    pending[key] = (pending[key] ?? 0) + 1;
    outcomes[key] = started;
    runChrome?.outcome(key, started, true);
    // The SAME report, in a second place, when the request was made at
    // a point on the model rather than on a panel control (design D9).
    // One code path, two places, and `formatOutcome` is the existing
    // function, so a press that is blocked says exactly what a nudge
    // that is blocked says.
    if (at !== undefined) {
      partLabel.show(started, at);
    }
    refreshTransport();
    return issue().then(
      (settled) => { outcomes[key] = summarise(settled, unit); },
      (error: unknown) => {
        // A request the run DECLINED -- a second command on an input
        // another one already owns, an unknown instruction, a duration
        // that is not a whole number of ticks. Reported in place, so a
        // manual control never appears to have taken over an input it
        // did not.
        outcomes[key] = {
          status: 'refused', admitted: null, unit,
          message: error instanceof Error ? error.message : String(error),
        };
      },
    ).then(() => {
      pending[key] = Math.max((pending[key] ?? 1) - 1, 0);
      runChrome?.outcome(key, outcomes[key], pending[key] > 0);
      if (at !== undefined) {
        partLabel.show(outcomes[key], at);
      }
      refreshTransport();
      // What it became, for the gesture's planner: a quantum that
      // completed advances the sweep origin, and one that did not
      // leaves it exactly where it was (design D11).
      return outcomes[key] ?? null;
    });
  };

  // -------------------------------------------------------------------
  // The PART controls (OpenSpec `drive-the-run-by-touch`, design
  // D4-D15). Everything here is three.js and the DOM: the pick, the
  // highlight's materials, the gesture's world line and where a part
  // stands on screen. Every DECISION is in `partControls.ts`, and the
  // gesture's own DOM behaviour is in `partSurfaceWith` below, which
  // this hands its collaborators to -- the seam `inspector.test.ts`
  // already uses for `mount`, because jsdom can give no WebGL context
  // and an untestable decision is a decision nobody checks.

  /** Whether this mount PRESENTS the affordance: the cursor, the
   * highlight, the title and the pick. `controls()` answers and the run
   * API is whole either way (design D14). */
  const presentsPartControls = (): boolean =>
    showsPartControls(resolved.partControls, loadedControls.length > 0);

  /** The transient report beside the pointer (design D9). */
  const partLabel = outcomeLabelIn(container);

  /** The ray through a client point, in plain tuples. */
  const rayAt = (x: number, y: number): Ray => {
    const bounds = renderer.domElement.getBoundingClientRect();
    raycaster.setFromCamera(new THREE.Vector2(
      ((x - bounds.left) / bounds.width) * 2 - 1,
      -((y - bounds.top) / bounds.height) * 2 + 1,
    ), camera);
    const { origin, direction } = raycaster.ray;
    return {
      origin: [origin.x, origin.y, origin.z],
      direction: [direction.x, direction.y, direction.z],
    };
  };

  /** Where a world point lands, in viewport CSS pixels. */
  const toClient = (world: Vec3): Point => {
    const bounds = renderer.domElement.getBoundingClientRect();
    const projected = new THREE.Vector3(world[0], world[1], world[2])
      .project(camera);
    return {
      x: bounds.left + ((projected.x + 1) / 2) * bounds.width,
      y: bounds.top + ((1 - projected.y) / 2) * bounds.height,
    };
  };

  /** The nearest VISIBLE hit's mesh, and the controls naming it -- or
   * null (design D5).
   *
   * The cast is against the whole tree, not against control meshes
   * only, and the NEAREST hit decides: a part standing in front of a
   * control is in front of it, and a dial under a closed lid is not
   * pressed through the lid. three.js's raycaster does not consult
   * `visible` at all in this version, so that filter is ours. */
  const pickAt = (x: number, y: number): readonly LoadedControl[] | null => {
    if (tree === undefined || partMeshes.size === 0) {
      return null;
    }
    rayAt(x, y);
    for (const hit of raycaster.intersectObject(scene, true)) {
      if (!(hit.object instanceof THREE.Mesh)
          || !visibleUpTo(hit.object, scene)) {
        continue;
      }
      return partMeshes.get(hit.object) ?? null;
    }
    return null;
  };

  /** Lift the emissive colour of every mesh of every hovered part, and
   * answer the function that puts it back.
   *
   * A node with no declared colour renders through
   * `MeshNormalMaterial`, which HAS no `emissive`: it gets the cursor
   * and the title and no lift, which is said out loud rather than
   * worked around (design D7). */
  const liftParts = (naming: readonly LoadedControl[]): (() => void) => {
    const lifted: { emissive: THREE.Color; was: THREE.Color }[] = [];
    for (const control of naming) {
      for (const mesh of partOf.get(control.name) ?? []) {
        const materials = Array.isArray(mesh.material)
          ? mesh.material : [mesh.material];
        for (const material of materials) {
          const glow = (material as { emissive?: THREE.Color }).emissive;
          if (glow instanceof THREE.Color) {
            lifted.push({ emissive: glow, was: glow.clone() });
            glow.setHex(HOVER_EMISSIVE);
          }
        }
      }
    }
    return () => { lifted.forEach(({ emissive, was }) => emissive.copy(was)); };
  };

  /** The world line the control turns about, from the JOINT node's own
   * world matrix (ADR-112 §3, design D6). */
  const lineOf = (control: LoadedControl): WorldLine | null => {
    if (tree === undefined) {
      return null;
    }
    scene.updateMatrixWorld(true);
    const joint = tree.requirePath(control.joint);
    return worldLine(joint.group.matrixWorld.elements as unknown as number[],
                     control.axis, control.origin);
  };

  /** How THIS gesture will measure its sweep, decided once from the
   * pointerdown ray and fixed for the gesture (design D10): orbiting is
   * suspended, so the camera cannot move and the measurement cannot
   * change meaning half-way through. The reader carries its own
   * previous reading, so the surface only accumulates what it returns.
   */
  const sweepReaderFor = (control: LoadedControl,
                          x: number, y: number): SweepReader | null => {
    const line = lineOf(control);
    if (line === null) {
      return null;
    }
    const choice = chooseMode(rayAt(x, y), line,
                              [camera.position.x, camera.position.y,
                                camera.position.z]);
    if (choice.mode === 'plane') {
      let reference = choice.reference;
      return {
        read(nextX: number, nextY: number): number {
          const met = intersectPlane(rayAt(nextX, nextY), line);
          if (met === null || reference === null) {
            return 0;
          }
          const radius = sub3(met, line.origin);
          if (Math.hypot(radius[0], radius[1], radius[2]) <= MIN_RADIUS) {
            return 0;
          }
          const now = normalize3(radius);
          const delta = sweepAngle(reference, now, line.axis);
          reference = now;
          return delta;
        },
      };
    }
    const pivot = toClient(line.origin);
    let from: Point = { x, y };
    return {
      read(nextX: number, nextY: number): number {
        const delta = turnedBy(from, { x: nextX, y: nextY }, pivot);
        from = { x: nextX, y: nextY };
        return delta * choice.screenSign;
      },
    };
  };

  /** The gesture's own DOM behaviour, given the collaborators above. */
  const partSurface = partSurfaceWith({
    container,
    canvas: renderer.domElement,
    orbit: controls,
    pick: pickAt,
    highlight: liftParts,
    reader: sweepReaderFor,
    nudge: (id: string) => nudgeSettings[id] ?? DEFAULT_NUDGE,
    trigger: (name: string, at: Point) => {
      const started = runtime;
      return started === undefined
        ? null : request(name, null, () => started.trigger(name), at);
    },
    move: (id: string, by: number, seconds: number, at: Point) => {
      const started = runtime;
      return started === undefined ? null : request(
        id, loadedProgram?.drivers[id]?.unit ?? null,
        () => started.move(id, { by, duration: seconds }), at);
    },
  });

  /** Rebuild the mesh -> control map from the tree, at each of the
   * three places a mesh can be replaced (design D4). `tree.ts` is not
   * touched at all: `requirePath` already returns the part's subtree
   * and refuses an unknown path by name. */
  const rebuildPartControls = (): void => {
    partSurface.clear();
    partMeshes = new Map();
    partOf = new Map();
    if (tree !== undefined) {
      for (const control of loadedControls) {
        const meshes: THREE.Mesh[] = [];
        tree.requirePath(control.part).group.traverse((object) => {
          if (object instanceof THREE.Mesh) {
            meshes.push(object);
          }
        });
        partOf.set(control.name, meshes);
        for (const mesh of meshes) {
          const naming = partMeshes.get(mesh);
          if (naming === undefined) {
            partMeshes.set(mesh, [control]);
          } else {
            naming.push(control);
          }
        }
      }
    }
    partSurface.refresh(loadedControls, presentsPartControls());
  };

  /** The part's on-screen bounds, in viewport CSS pixels, or null when
   * it is not visible or is wholly off screen (design D15). */
  const partRect = (control: LoadedControl): PartRect | null => {
    const meshes = (partOf.get(control.name) ?? [])
      .filter((mesh) => visibleUpTo(mesh, scene));
    if (meshes.length === 0) {
      return null;
    }
    const bounds = new THREE.Box3();
    for (const mesh of meshes) {
      if (mesh.geometry.boundingBox === null) {
        mesh.geometry.computeBoundingBox();
      }
      const box = mesh.geometry.boundingBox;
      if (box !== null) {
        bounds.union(box.clone().applyMatrix4(mesh.matrixWorld));
      }
    }
    if (bounds.isEmpty()) {
      return null;
    }
    const canvas = renderer.domElement.getBoundingClientRect();
    const corner = new THREE.Vector3();
    let left = Infinity;
    let right = -Infinity;
    let top = Infinity;
    let bottom = -Infinity;
    let anyInFront = false;
    for (let index = 0; index < 8; index += 1) {
      corner.set(index & 1 ? bounds.max.x : bounds.min.x,
                 index & 2 ? bounds.max.y : bounds.min.y,
                 index & 4 ? bounds.max.z : bounds.min.z);
      // Behind the camera a projection is meaningless, so such a corner
      // is left out rather than folded back into the rectangle.
      if (corner.clone().applyMatrix4(camera.matrixWorldInverse).z >= 0) {
        continue;
      }
      anyInFront = true;
      const projected = corner.clone().project(camera);
      const x = canvas.left + ((projected.x + 1) / 2) * canvas.width;
      const y = canvas.top + ((1 - projected.y) / 2) * canvas.height;
      left = Math.min(left, x);
      right = Math.max(right, x);
      top = Math.min(top, y);
      bottom = Math.max(bottom, y);
    }
    if (!anyInFront || right < canvas.left || left > canvas.right
        || bottom < canvas.top || top > canvas.bottom) {
      return null;
    }
    return { x: left, y: top, width: right - left, height: bottom - top };
  };

  /** A point at which a press actually REACHES this control right now,
   * found the way a press finds it (design D15): the rect's centre
   * first -- which on a real dial may be the axle's hole -- and then a
   * bounded grid inside the rect, under the same nearest-visible-hit
   * rule. `null` says honestly that nothing does. */
  const partPoint = (control: LoadedControl,
                     rect: PartRect): Point | null => {
    const canvas = renderer.domElement.getBoundingClientRect();
    const reaches = (point: Point): boolean => {
      if (point.x < canvas.left || point.x > canvas.right
          || point.y < canvas.top || point.y > canvas.bottom) {
        return false;
      }
      return pickAt(point.x, point.y)?.includes(control) ?? false;
    };
    const centre = { x: rect.x + rect.width / 2,
      y: rect.y + rect.height / 2 };
    if (reaches(centre)) {
      return centre;
    }
    for (let row = 0; row < POINT_GRID; row += 1) {
      for (let column = 0; column < POINT_GRID; column += 1) {
        const point = {
          x: rect.x + (rect.width * (column + 0.5)) / POINT_GRID,
          y: rect.y + (rect.height * (row + 0.5)) / POINT_GRID,
        };
        if (reaches(point)) {
          return point;
        }
      }
    }
    return null;
  };

  const partControlViews = (): PartControlView[] => {
    scene.updateMatrixWorld(true);
    return loadedControls.map((control) => {
      const rect = partRect(control);
      const view: PartControlView = {
        name: control.name,
        kind: control.kind,
        part: [...control.part],
        joint: [...control.joint],
        coordinate: control.coordinate,
        rect,
        point: rect === null ? null : partPoint(control, rect),
      };
      if (control.instruction !== null) {
        view.instruction = control.instruction;
      }
      if (control.input !== null) {
        view.input = control.input;
      }
      if (control.perUnit !== null) {
        view.perUnit = control.perUnit;
      }
      return view;
    });
  };

  const applyFrame = (view: View | null) => {
    scene.updateMatrixWorld(true);
    const framed = frameBounds(visibleBounds(scene), camera.fov, view, resolved.up);
    if (!framed) {
      return;
    }
    camera.position.copy(framed.position);
    camera.up.copy(framed.up);
    camera.near = framed.near;
    camera.far = framed.far;
    camera.updateProjectionMatrix();
    controls.target.copy(framed.target);
    controls.update();
  };

  const captureView = (): View => ({
    camera: camera.position.clone(),
    target: controls.target.clone(),
  });

  /** Start (or restart) the run of a document carrying a program, posed
   * at its published rest bank before the first tick is ever taken.
   *
   * `republished` marks the targeted document update `solid develop`
   * drives, where a live run may stand rather than restart: it keeps
   * its bank, its active commands, its step count and its elapsed clock
   * only when the republished program's identity and the run's step
   * size are both unchanged (OpenSpec `drive-the-run-on-screen`, §3).
   * A coordinate is never carried across because an identifier matched.
   */
  const startRuntime = async (document: Manifest,
                              program: LoadedProgram | null,
                              republished = false) => {
    const current: RunIdentity | null =
      runtime === undefined || loadedProgram === null
        ? null : { identity: runtime.identity(), dt: resolved.run.dt };
    const next: RunIdentity | null = program === null
      ? null : { identity: program.identity, dt: resolved.run.dt };
    const plan = republished ? republishPlan(current, next) : null;
    republishNotice = plan === null ? null : plan.message;
    if (plan !== null && plan.keep) {
      // The same machine: only the geometry and the chrome reconcile.
      loadedProgram = program;
      return;
    }
    runtime?.dispose();
    runtime = undefined;
    loadedProgram = program;
    elapsedSeconds = 0;
    outcomes = {};
    pending = {};
    refusal = null;
    elapsedWidth = 0;
    if (program === null) {
      bank = {};
      return;
    }
    bank = { ...program.initial };
    const started = RunRuntime.start(document as RunDocument, {
      dt: resolved.run.dt,
      record: resolved.run.record,
      autostart: resolved.run.autostart,
      sourceUrl,
    });
    runtime = started;
    started.setSpeed(speed);
    started.onFrame((frame) => {
      bank = frame.bank;
      elapsedSeconds = frame.clock;
      // Rendering never advances the run, and the run never renders: a
      // dropped frame drops DISPLAY, not mechanics.
      tree?.update(scope(), posed(frame.moved));
      // The readouts FOLLOW committed state and never feed a movement
      // back into the run. Only the controls whose input moved are
      // written; a refusal shown across the panel clears here, because
      // a tick has committed.
      if (refusal !== null) {
        refusal = null;
        runChrome?.refuse(null);
      }
      runChrome?.commit(frame);
      refreshTransport();
      renderer.render(scene, camera);
    });
    started.onRefusal((reply) => {
      // A tick that committed nothing: the whole machine disagreeing
      // with itself. Its message names the relation as its author wrote
      // it, it is shown across the panel rather than on one control,
      // and the run pauses on it rather than repeating the refused step
      // sixty times a second.
      refusal = reply.message;
      runChrome?.refuse(reply.message);
      refreshTransport();
    });
    // Awaited before the tree is built, so the handle a host receives
    // answers for a run that has loaded its program -- and so a program
    // the ENGINE refuses (rather than the loader) refuses the mount.
    await started.ready;
  };

  const replaceTree = async (view: View | null) => {
    const { document, table, program, controls: declared } =
      await loadDocument(sourceUrl);
    drivers.reconcile(document.drivers ?? {}, document.instructions ?? {});
    // Installed before the update that follows (design D6), in the same
    // place and order `drivers.reconcile(...)` already runs before it.
    bindingsTable = table;
    await startRuntime(document, program);
    const next = new WidgetTree(document.root, baseUrl, null, bindingsTable);
    next.update(scope());
    await next.loaded;
    if (disposed) {
      next.dispose();
      return;
    }
    if (tree) {
      scene.remove(tree.group);
      tree.dispose();
    }
    tree = next;
    scene.add(tree.group);
    assemblyNavigation.reconcile(tree);
    applyFrame(view);
    // One of the three places a mesh can be replaced (design D4).
    loadedControls = declared;
    rebuildPartControls();

    refreshControls(document);
    // Mount calls this before the handle exists, so no listener can be
    // subscribed yet and this notifies nobody by construction -- not a
    // flag, a property of the ordering (design D5). reload() reaches
    // this with the handle already returned, and notifies whoever is
    // subscribed.
    notifyAssemblyChange();
  };

  const refreshControls = (document: Manifest) => {
    controlElements.forEach((element) => element.remove());
    controlElements = [];
    slider = undefined;
    const plan = controlPlan(resolved.animation, tree!.animated);
    playing = tree!.animated && !plan.hostDriven && resolved.autoplay;
    animation = document.animation;
    cycleSeconds = cycleSecondsFor(animation, speed);
    speedControl = undefined;
    readout = undefined;
    if (plan.bar) {
      const built = buildControls(
        container,
        animation,
        speed,
        plan,
        () => playing,
        (nextPlaying) => { playing = nextPlaying; },
        setTime,
        setSpeed,
      );
      slider = built.slider;
      speedControl = built.speedControl;
      readout = built.readout;
      controlElements = built.elements;
      slider.value = String(timelinePosition(time, animation.frames));
      if (readout && animation.loop !== undefined) {
        readout.textContent = formatMachineTime(time * animation.loop, animation.loop);
      }
    }
    // After the store and the navigation have reconciled, so the chrome
    // reflects the values that survived the republish and a focus the
    // update may have reset (design D10).
    rebuildDriverChrome();
    rebuildRunChrome();
  };

  // The ONE place focus moves, whether the host called `setRoot` or the
  // maker clicked the breadcrumb (design D8). Navigation, camera and
  // chrome move together, so the widget and the host can never disagree
  // about what is focused.
  const focusOn = (path: AssemblyPath | null) => {
    if (!tree) {
      throw new Error('Viewer assembly is unavailable');
    }
    assemblyNavigation.setRoot(tree, path);
    applyFrame(null);
    rebuildDriverChrome();
    rebuildRunChrome();
    renderer.render(scene, camera);
    // Whether a host called setRoot or the maker clicked the
    // breadcrumb, this is the one place that moved -- so this is the
    // one place that notifies. `setRoot` throws from `requirePath`
    // above for an unknown path, before any of this runs.
    notifyAssemblyChange();
  };

  const nativeValues = (): Record<string, number> => {
    const values: Record<string, number> = {};
    for (const id of Object.keys(drivers.drivers())) {
      values[id] = drivers.driver(id);
    }
    return values;
  };

  function rebuildDriverChrome(): void {
    driverChrome?.remove();
    driverChrome = undefined;
    const table = drivers.drivers();
    // A document carrying a program has NO on-screen control in this
    // change (design §11): its inputs are moved by commands, not by a
    // slider over a driver value the bank no longer poses from. The
    // chrome is `drive-the-run-on-screen`.
    if (loadedProgram !== null) {
      return;
    }
    if (!showsDriverChrome(resolved.driverControls,
                           Object.keys(table).length > 0)) {
      return;
    }
    driverChrome = buildDriverChrome(container, controlLayer({
      drivers: table,
      instructions: drivers.instructions(),
      values: nativeValues(),
      focus: assemblyNavigation.root(),
      rootLabel: tree?.name ?? 'root',
    }), {
      setDriver(id: string, value: number) {
        // Marked so the change we hear back does not write over the
        // input the maker is still dragging.
        drivingFromChrome = true;
        try {
          driveTo(id, value);
        } finally {
          drivingFromChrome = false;
        }
      },
      trigger: (name: string) => drivers.trigger(name),
      focus: focusOn,
    });
  }

  /** What the running chrome is looking at right now: the loaded
   * program's tables, the committed bank, the focused layer, the
   * maker's own request settings, and where each control's last request
   * got to. */
  const runLayerInput = (): RunControlsInput => ({
    program: loadedProgram,
    values: runtime === undefined ? { ...(loadedProgram?.initial ?? {}) }
      : runtime.bank(),
    focus: assemblyNavigation.root(),
    rootLabel: tree?.name ?? 'root',
    nudge: nudgeSettings,
    jog: jogSettings,
    outcomes,
    transport: {
      running: runtime?.running() ?? false,
      speed,
      elapsedSeconds: runtime?.elapsedSeconds() ?? 0,
      tick: runtime?.tick() ?? 0,
      refusal,
      elapsedWidth,
    },
  });

  function rebuildRunChrome(): void {
    runChrome?.remove();
    runChrome = undefined;
    const started = runtime;
    if (loadedProgram === null || started === undefined) {
      return;
    }
    // The same switch as the posed chrome's, gating the pixels only: a
    // host that suppresses them keeps the whole run API.
    if (!showsRunControls(resolved.driverControls, true)) {
      return;
    }
    const unit = (id: string): string | null =>
      (loadedProgram as LoadedProgram).drivers[id]?.unit ?? null;
    runChrome = buildRunChrome(container, runControlLayer(runLayerInput()), {
      nudge(id: string, amount: number, seconds: number) {
        void request(id, unit(id),
                     () => started.move(id, { by: amount, duration: seconds }));
      },
      jogStart(id: string, rate: number) {
        void request(id, unit(id), () => started.rate(id, rate));
      },
      jogStop(id: string) {
        // The release itself reports nothing: the outcome a maker reads
        // is the one the RATE command retires with, under the handle
        // the press created.
        started.rate(id, 0).catch(() => undefined);
      },
      trigger(name: string) {
        void request(name, null, () => started.trigger(name));
      },
      setNudge(id: string, plan: NudgePlan) {
        // Configures the next request; nothing moves (design D3).
        nudgeSettings[id] = plan;
      },
      setJog(id: string, plan: JogPlan) {
        jogSettings[id] = plan;
      },
      play() {
        if (started.running()) {
          started.pause();
        } else {
          started.start();
        }
        refreshTransport();
      },
      step() {
        // Exactly one tick, whether or not the run is started, which is
        // what makes a jump or a stop inspectable.
        started.step(1).catch(() => undefined).then(refreshTransport);
      },
      reset() {
        // The initial snapshot: the rest bank, tick zero, no commands.
        // The readouts follow, because they follow committed state.
        outcomes = {};
        pending = {};
        elapsedWidth = 0;
        started.reset().catch(() => undefined).then(() => {
          runChrome?.clearOutcomes();
          refreshTransport();
        });
      },
      setSpeed,
      focus: focusOn,
    });
    runChrome.notice(republishNotice);
    refreshTransport();
  }

  // The initial load: retains the shared expression table (D8)
  // ONLY once it has succeeded (mountRetained above), so a refused
  // document -- an unreadable version, an unevaluable tech, an
  // undeclared driver id, or D10's unsupported-form refusal, all
  // raised inside replaceTree's loadDocument/assertRenderable --
  // never leaves a hold behind: no handle is ever produced for such
  // a mount, so no dispose() would ever exist to release it.
  await mountRetained(() => replaceTree(resolved.view));

  // The public channel, subscribed once per mount: a ramp moving a
  // driver reaches its slider exactly the way it reaches a host's
  // listener, with no private path into the store (design D7).
  const unsubscribeDrivers = drivers.onDriverChange((id, value) => {
    driverChrome?.apply(id, value, drivingFromChrome);
  });

  const resize = () => {
    if (disposed) {
      return;
    }
    const width = container.clientWidth;
    const height = container.clientHeight;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  resize();
  const observer = new ResizeObserver(resize);
  observer.observe(container);

  let lastTimestamp: number | undefined;
  renderer.setAnimationLoop((timestamp: number) => {
    const elapsed = lastTimestamp === undefined
      ? 0 : (timestamp - lastTimestamp) / 1000;
    lastTimestamp = timestamp;
    // Ramps advance on wall-clock elapsed time, in the same loop: their
    // endpoints and duration are exact, and only the sampling between
    // them varies with the frame rate (design D4 -- this is an
    // animation, and determinism stays with the Python simulation).
    const movedDrivers = drivers.tick();
    // At most ONE hover cast per animation frame, and none at all
    // while a gesture is engaged or for a document that declares no
    // control (design D5).
    partSurface.pollHover();
    if (runtime !== undefined) {
      // The render loop drives the CADENCE and the worker owns the
      // mechanics: one advance in flight, and a committed bank poses the
      // tree from the frame listener above (design D2).
      runtime.frame(elapsed);
      renderer.render(scene, camera);
      return;
    }
    if (playing) {
      setTime(advance(time, elapsed, cycleSeconds));
    }
    tree?.update(scope(), { time: playing, drivers: movedDrivers });
    renderer.render(scene, camera);
  });

  return {
    apiVersion: API_VERSION,
    dispose() {
      if (disposed) {
        return;
      }
      disposed = true;
      renderer.setAnimationLoop(null);
      observer.disconnect();
      controls.dispose();
      unsubscribeDrivers();
      // Releases every subscription; disposal itself notifies nobody
      // (design D5, mirroring drivers.dispose()).
      assemblyChanges.dispose();
      driverChrome?.remove();
      driverChrome = undefined;
      runChrome?.remove();
      runChrome = undefined;
      // The pointer surface, the highlight and the transient label all
      // go with the mount (design D13).
      partSurface.dispose();
      partLabel.remove();
      partMeshes = new Map();
      partOf = new Map();
      loadedControls = [];
      // Nothing will advance the ramps again, so their promises settle
      // here rather than never.
      drivers.dispose();
      runtime?.dispose();
      runtime = undefined;
      tree?.dispose();
      renderer.dispose();
      container.replaceChildren();
      // Releases this mount's hold on the shared expression table
      // (D8): emptied once the last mounted viewer on the page is gone.
      releaseExpressions();
    },
    view: captureView,
    async reload() {
      await replaceTree(captureView());
    },
    async artifactChanged(path: string) {
      partSurface.clear();
      await tree?.artifactChanged(path, baseUrl);
      if (tree) {
        assemblyNavigation.reconcile(tree);
      }
      // The third place a mesh can be replaced: the controls are the
      // same, the meshes carrying them are not (design D4).
      rebuildPartControls();
      renderer.render(scene, camera);
      notifyAssemblyChange();
    },
    async manifestChanged() {
      const { document, table, program, controls: declared } =
        await loadDocument(sourceUrl);
      drivers.reconcile(document.drivers ?? {}, document.instructions ?? {});
      // Installed before the update that follows (design D6): a
      // republish carrying a different table invalidates the free set
      // of every node that reads it differently, whether or not that
      // node's own operations changed.
      bindingsTable = table;
      await startRuntime(document, program, true);
      // Cleared BEFORE the reconcile, because `setColor` replaces
      // materials and a lifted emissive would be restored onto a
      // material nothing is showing any more (design D7).
      partSurface.clear();
      await tree?.reconcile(document.root, baseUrl, null, bindingsTable);
      if (tree) {
        const rootChanged = assemblyNavigation.reconcile(tree);
        tree.update(scope());
        refreshControls(document);
        if (rootChanged) {
          applyFrame(null);
        }
      }
      loadedControls = declared;
      rebuildPartControls();
      renderer.render(scene, camera);
      notifyAssemblyChange();
    },
    assembly() {
      if (!tree) {
        throw new Error('Viewer assembly is unavailable');
      }
      return tree.assembly();
    },
    navigation: () => assemblyNavigation.state(),
    onAssemblyChange: (listener: AssemblyListener) =>
      assemblyChanges.subscribe(listener),
    setRoot(path: AssemblyPath | null) {
      focusOn(path);
    },
    setVisible(path: AssemblyPath, visible: boolean) {
      if (!tree) {
        throw new Error('Viewer assembly is unavailable');
      }
      assemblyNavigation.setVisible(tree, path, visible);
      renderer.render(scene, camera);
      notifyAssemblyChange();
    },
    setTime,
    speed: () => speed,
    setSpeed,
    drivers: () => drivers.drivers(),
    driver: (id: string) => drivers.driver(id),
    setDriver(id: string, value: number) {
      driveTo(id, value);
    },
    onDriverChange: (listener: DriverListener) =>
      drivers.onDriverChange(listener),
    instructions: () => drivers.instructions(),
    trigger: (name: string) => drivers.trigger(name),
    controls: partControlViews,
    run(): RunHandle | null {
      const started = runtime;
      const program = loadedProgram;
      if (started === undefined || program === null) return null;
      return {
        identity: () => started.identity(),
        dt: () => resolved.run.dt,
        tick: () => started.tick(),
        elapsed: () => started.elapsedSeconds(),
        state: () => started.bank(),
        coordinates: () => started.coordinates(),
        start: () => started.start(),
        pause: () => started.pause(),
        running: () => started.running(),
        step: (ticks = 1) => started.step(ticks),
        move: (input, request) => started.move(input, request),
        rate: (input, rate) => started.rate(input, rate),
        trigger: (name) => started.trigger(name),
        cancel: (input) => started.cancel(input),
        reset: () => started.reset().then(() => undefined),
        snapshot: () => started.snapshot(),
        restore: (state) => started.restore(state).then(() => undefined),
        onCommit: (listener) => started.onFrame(listener),
        onOutcome: (listener) => started.onOutcome(listener),
        runsInWorker: started.runsInWorker,
      };
    },
  };
}

const EMPTY: ReadonlySet<string> = new Set();

// ---------------------------------------------------------------------
// The part gesture's own constants and record (OpenSpec
// `drive-the-run-by-touch`, design D7-D9, D13, D15).

/** CSS pixels of travel a press is allowed. The same order as a native
 * click's slop, and small enough that a dial's quantum -- 36 degrees of
 * sweep -- is never reached inside it (design D8). */
const PRESS_SLOP = 4;

/** The grey a hovered part's emissive colour is lifted to.
 *
 * `Color.setHex` reads sRGB and stores linear, so the lift a viewer
 * actually SEES is much smaller than the hex suggests: 0x333333
 * measured about 10/255 on the acceptance model's own materials, which
 * is not the "visible change" the spec asks for. 0x777777 measures
 * about 60/255 there -- unmistakable beside the parts around it, and
 * still a grey rather than a colour of its own. */
const HOVER_EMISSIVE = 0x777777;

/** How long a transient outcome label stays before it is taken away. */
const OUTCOME_LINGER = 4000;

/** How finely `controls()` searches a part's rectangle for a point a
 * press reaches (design D15). Bounded on purpose: the answer is `null`
 * rather than an unbounded hunt. */
const POINT_GRID = 7;

const PART_OUTCOME_STYLE =
  'position:absolute;pointer-events:none;z-index:2;'
  + 'padding:2px 6px;border-radius:3px;max-width:24em;'
  + 'background:rgba(30,33,38,0.85);color:#fff;'
  + 'font:12px system-ui,sans-serif;';

export interface Point {
  x: number;
  y: number;
}

export interface PartRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

/** The transient outcome label beside a pointer (design D9).
 *
 * Its own factory so jsdom can test its text and its lifetime without a
 * WebGL context: the element is created on first use, moved and
 * rewritten by each report, and taken away after `linger` milliseconds
 * or when the mount is disposed. */
export function outcomeLabelIn(container: HTMLElement,
                               linger = OUTCOME_LINGER): {
  show(report: OutcomeReport | null, at: Point): void;
  remove(): void;
} {
  let element: HTMLElement | undefined;
  let timer: ReturnType<typeof setTimeout> | undefined;
  const remove = (): void => {
    if (timer !== undefined) {
      clearTimeout(timer);
      timer = undefined;
    }
    element?.remove();
    element = undefined;
  };
  return {
    show(report: OutcomeReport | null, at: Point) {
      if (element === undefined) {
        element = document.createElement('div');
        element.className = 'part-outcome';
        // A report a screen reader is told about once, where it was
        // made -- the same `formatOutcome` words the panel writes.
        element.setAttribute('role', 'status');
        element.style.cssText = PART_OUTCOME_STYLE;
        container.append(element);
      }
      const bounds = container.getBoundingClientRect();
      element.style.left = `${Math.round(at.x - bounds.left + 12)}px`;
      element.style.top = `${Math.round(at.y - bounds.top + 12)}px`;
      element.textContent = formatOutcome(report);
      if (timer !== undefined) {
        clearTimeout(timer);
      }
      timer = setTimeout(remove, linger);
    },
    remove,
  };
}

/** How a gesture reads its sweep. The reader carries its own previous
 * reading, so the surface only accumulates what it returns -- which is
 * what makes the sweep UNWRAPPED across more than half a turn. */
export interface SweepReader {
  /** The signed degrees this pointer position adds to the sweep. */
  read(x: number, y: number): number;
}

/** What the part surface needs from the mount it belongs to: the
 * three.js, the run and the DOM elements. Every one of them is a
 * collaborator a test substitutes, which is the seam `inspector.ts`
 * already uses -- `mount()` builds a `THREE.WebGLRenderer`, so jsdom
 * can never call it. */
export interface PartSurfaceHost {
  container: HTMLElement;
  canvas: HTMLElement;
  /** OrbitControls, or anything carrying its `enabled` flag. */
  orbit: { enabled: boolean };
  /** The controls naming the nearest VISIBLE mesh at a client point. */
  pick(x: number, y: number): readonly LoadedControl[] | null;
  /** Lift the affordance on these controls; the returned function puts
   * it back. */
  highlight(controls: readonly LoadedControl[]): () => void;
  /** How this gesture measures its sweep, or null when there is no
   * geometry to measure with. */
  reader(control: LoadedControl, x: number, y: number): SweepReader | null;
  /** What one quantum of this input asks for. */
  nudge(input: string): NudgePlan;
  /** Submit the declared instruction; null when there is no run. */
  trigger(name: string, at: Point): Promise<OutcomeReport | null> | null;
  /** Ask the input to move; null when there is no run. */
  move(input: string, by: number, seconds: number,
       at: Point): Promise<OutcomeReport | null> | null;
}

export interface PartSurface {
  /** A new set of controls, and whether the affordance is presented at
   * all -- called at each of the three places a mesh can be replaced. */
  refresh(controls: readonly LoadedControl[], present: boolean): void;
  /** Settle at most one hover cast; the caller's animation loop is the
   * throttle. */
  pollHover(): void;
  engaged(): boolean;
  /** Clear the cursor, the title and the highlight. */
  clear(): void;
  dispose(): void;
}

/** One engagement on a touchable part, from `pointerdown` to whichever
 * of the five sides ends it. */
interface Gesture {
  pointerId: number;
  /** Where it came down, in client pixels: the press threshold. */
  downX: number;
  downY: number;
  /** Where the pointer stands now: the label's place, and the point a
   * quantum issued on retire is reported at. */
  at: Point;
  /** True once the pointer has travelled past `PRESS_SLOP`, and then
   * true for the rest of the gesture. */
  dragging: boolean;
  button: LoadedControl | null;
  turn: LoadedControl | null;
  /** The turn's input id, hoisted so the pump needs no null dance. */
  turnId: string | null;
  /** The duration each quantum asks for, captured at pointerdown. */
  seconds: number;
  planner: TurnPlanner | null;
  reader: SweepReader | null;
}

/** The press, the turn, the hover affordance and the five release
 * paths (design D5, D7, D8, D12, D13), given the host's collaborators.
 *
 * Nothing here writes a coordinate, poses a part or measures anything:
 * the measurement is the host's reader and every decision is the
 * planner's. What this owns is the DOM -- listeners, the cursor, the
 * title, the capture and the camera's suspension.
 */
export function partSurfaceWith(host: PartSurfaceHost): PartSurface {
  let declared: readonly LoadedControl[] = [];
  let presented = false;
  let listeners: (() => void) | null = null;
  let hovered: readonly LoadedControl[] | null = null;
  let restore: (() => void) | null = null;
  let hoverAt: Point | null = null;
  let hoverDue = false;
  let gesture: Gesture | null = null;

  const clearHighlight = (): void => {
    restore?.();
    restore = null;
  };

  const clear = (): void => {
    clearHighlight();
    hovered = null;
    host.canvas.style.cursor = '';
    host.canvas.removeAttribute('title');
  };

  const applyHover = (naming: readonly LoadedControl[] | null): void => {
    const same = hovered !== null && naming !== null
      && hovered.length === naming.length
      && hovered.every((control, index) => naming[index] === control);
    if (same) {
      return;
    }
    clearHighlight();
    hovered = naming;
    if (naming === null) {
      host.canvas.style.cursor = '';
      host.canvas.removeAttribute('title');
      return;
    }
    host.canvas.style.cursor = 'pointer';
    // The display names of EVERY control naming this part: a dial that
    // is both pressed and turned says so.
    host.canvas.setAttribute('title',
                             naming.map((one) => one.name).join(' · '));
    restore = host.highlight(naming);
  };

  /** Issue the next quantum, if the planner says there is one -- and
   * ask again when it retires, which is how a fast drag catches up.
   *
   * At most ONE is ever in flight, because `Run.claim` throws when an
   * input already has an active command: "an input has one owner at a
   * time". */
  const pump = (current: Gesture): void => {
    if (current.planner === null || current.turnId === null) {
      return;
    }
    const asked = current.planner.next();
    if (asked === null) {
      return;
    }
    const settling = host.move(current.turnId, asked.by, current.seconds,
                               { ...current.at });
    if (settling === null) {
      // No run to ask: nothing was issued, so nothing is outstanding.
      current.planner.retire('refused');
      return;
    }
    void settling.then((report) => {
      // A gesture that has already ended keeps neither its planner nor
      // its right to ask again: the movement is left to retire and
      // report on its own, and nothing follows it.
      if (gesture !== current || current.planner === null) {
        return;
      }
      current.planner.retire(
        report === null || report.status === 'completed'
          ? 'completed'
          : report.status as 'blocked' | 'refused' | 'cancelled');
      pump(current);
    });
  };

  /** Every side a gesture can end on (design D13). Each restores the
   * camera, releases the capture and clears the affordance. */
  const endGesture = (): void => {
    const current = gesture;
    gesture = null;
    host.orbit.enabled = true;
    if (current !== null) {
      try {
        (host.canvas as Element & {
          releasePointerCapture(id: number): void;
        }).releasePointerCapture(current.pointerId);
      } catch {
        // Already released, or never captured: nothing to undo.
      }
    }
    clear();
  };

  const onPointerDown = (event: PointerEvent): void => {
    if (!presented || gesture !== null || event.button !== 0) {
      return;
    }
    const naming = host.pick(event.clientX, event.clientY);
    if (naming === null || naming.length === 0) {
      return;
    }
    // Capture phase on the CONTAINER, an ancestor of the canvas, so
    // this runs strictly before OrbitControls' own listener on the
    // canvas whatever registration order would otherwise decide.
    event.stopPropagation();
    host.orbit.enabled = false;
    try {
      (host.canvas as Element & {
        setPointerCapture(id: number): void;
      }).setPointerCapture(event.pointerId);
    } catch {
      // A browser that cannot capture still releases on pointerup.
    }
    const button = naming.find((one) => one.kind === 'button') ?? null;
    const turn = naming.find((one) => one.kind === 'turn') ?? null;
    const turnId = turn?.input ?? null;
    const plan = turnId === null ? DEFAULT_NUDGE : host.nudge(turnId);
    const reader = turn === null || turn.perUnit === null
      ? null : host.reader(turn, event.clientX, event.clientY);
    gesture = {
      pointerId: event.pointerId,
      downX: event.clientX,
      downY: event.clientY,
      at: { x: event.clientX, y: event.clientY },
      dragging: false,
      button,
      turn,
      turnId,
      seconds: plan.seconds,
      // The quantum is the input's CURRENT nudge amount times the
      // published ratio: a maker who sets the nudge to 5 digits drags
      // in fives (design D11).
      planner: reader === null || turn?.perUnit == null
        ? null : new TurnPlanner(plan.amount, turn.perUnit),
      reader,
    };
    applyHover(naming);
  };

  const onPointerMove = (event: PointerEvent): void => {
    if (gesture === null) {
      hoverAt = { x: event.clientX, y: event.clientY };
      hoverDue = true;
      return;
    }
    if (event.pointerId !== gesture.pointerId) {
      return;
    }
    const current = gesture;
    current.at = { x: event.clientX, y: event.clientY };
    if (!current.dragging
        && Math.hypot(event.clientX - current.downX,
                      event.clientY - current.downY) > PRESS_SLOP) {
      // A press until here, a drag for the rest of the gesture.
      current.dragging = true;
    }
    if (current.planner !== null && current.reader !== null) {
      current.planner.advance(current.reader.read(event.clientX,
                                                  event.clientY));
    }
    if (current.dragging) {
      pump(current);
    }
  };

  const onPointerUp = (event: PointerEvent): void => {
    if (gesture === null || event.pointerId !== gesture.pointerId) {
      return;
    }
    const current = gesture;
    const instruction = current.button?.instruction ?? null;
    // A press on a part carrying only a turn does nothing and reports
    // nothing: there is no instruction to submit, and inventing one
    // would move the machine in a way nobody declared (design D8).
    if (!current.dragging && instruction !== null) {
      host.trigger(instruction, { x: event.clientX, y: event.clientY });
    }
    endGesture();
  };

  const onRelease = (event: PointerEvent): void => {
    if (gesture !== null && event.pointerId === gesture.pointerId) {
      endGesture();
    }
  };

  const onBlur = (): void => { endGesture(); };
  const onVisibility = (): void => {
    if (document.hidden) {
      endGesture();
    }
  };

  /** Install the pointer surface -- or take it away again. Nothing of
   * it exists for a document that declares no control, or for a host
   * that suppressed the affordance (design D2, D14). */
  const install = (wanted: boolean): void => {
    if (wanted === (listeners !== null)) {
      return;
    }
    if (!wanted) {
      endGesture();
      listeners?.();
      listeners = null;
      return;
    }
    host.container.addEventListener('pointerdown', onPointerDown, true);
    host.canvas.addEventListener('pointermove', onPointerMove);
    host.canvas.addEventListener('pointerup', onPointerUp);
    host.canvas.addEventListener('pointercancel', onRelease);
    host.canvas.addEventListener('lostpointercapture', onRelease);
    window.addEventListener('blur', onBlur);
    document.addEventListener('visibilitychange', onVisibility);
    listeners = () => {
      host.container.removeEventListener('pointerdown', onPointerDown, true);
      host.canvas.removeEventListener('pointermove', onPointerMove);
      host.canvas.removeEventListener('pointerup', onPointerUp);
      host.canvas.removeEventListener('pointercancel', onRelease);
      host.canvas.removeEventListener('lostpointercapture', onRelease);
      window.removeEventListener('blur', onBlur);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  };

  return {
    refresh(controls: readonly LoadedControl[], present: boolean) {
      declared = controls;
      presented = present && declared.length > 0;
      clear();
      install(presented);
    },
    pollHover() {
      if (!hoverDue) {
        return;
      }
      hoverDue = false;
      if (gesture !== null || !presented || hoverAt === null) {
        return;
      }
      applyHover(host.pick(hoverAt.x, hoverAt.y));
    },
    engaged: () => gesture !== null,
    clear,
    dispose() {
      endGesture();
      install(false);
      declared = [];
      presented = false;
    },
  };
}

/** How far a point turned about a pivot, between two client positions,
 * in degrees and in a y-up frame -- which is the CSS frame with `dy`
 * negated. Wrapped into (-180, 180], because a single move is never
 * meant to be half a turn. */
export function turnedBy(from: Point, to: Point, pivot: Point): number {
  const angle = (point: Point): number =>
    Math.atan2(-(point.y - pivot.y), point.x - pivot.x) * (180 / Math.PI);
  let delta = angle(to) - angle(from);
  while (delta > 180) delta -= 360;
  while (delta <= -180) delta += 360;
  return delta;
}



function visibleBounds(root: THREE.Object3D): THREE.Box3 {
  const bounds = new THREE.Box3();
  root.updateWorldMatrix(true, true);
  const visit = (object: THREE.Object3D) => {
    if (!object.visible) {
      return;
    }
    if (object instanceof THREE.Mesh) {
      if (object.geometry.boundingBox === null) {
        object.geometry.computeBoundingBox();
      }
      if (object.geometry.boundingBox !== null) {
        bounds.union(object.geometry.boundingBox.clone().applyMatrix4(object.matrixWorld));
      }
    }
    object.children.forEach(visit);
  };
  visit(root);
  return bounds;
}

// Every schema version this viewer renders. The producer emits the
// LOWEST version its content needs -- a document holding no flexible
// node is byte-identical to the version 2 it always was -- so this set
// is exactly what the producer can emit and this build can read.
// OpenSpec `read-expression-bindings`: version 4 (a document carrying a
// shared-subexpression `bindings` table) joins it. OpenSpec
// `run-in-the-worker`: version 5 (a document carrying a compiled
// mechanical `program`) joins it too; `execute-the-self-read` added
// version 6 (a law that reads the coordinate it drives); and
// `execute-the-selection` adds version 7 (a program some of whose law
// edges form a BLOCK, ordered per piece of a tick from the published
// edges rather than run in the published listing). A version 8 document
// is refused by name and by list -- the same sentence a version 5
// document got from every viewer released so far.
//
// Exported so `version.test.ts` can pin it against the ONE declaration
// the bundle and `bundle.py` both read (`solidNodeDocumentVersions` in
// package.json): the number this viewer reports and the versions it
// refuses by must not be able to drift apart.
export const RENDERED_VERSIONS: readonly number[] = [1, 2, 3, 4, 5, 6, 7];

// The document schema this viewer evaluates. Version 2 added the
// `drivers` table, and since ADR-056 stage 3b this viewer EVALUATES
// driver-referencing expressions rather than refusing them: a non-empty
// table is now a document to render at its declared defaults and drive,
// not one to turn away. Version 3 added the `flexible` node shape, whose
// geometry this viewer evaluates from the embedded spec. Version 4 added
// the `bindings` table (`bindings.ts`, ADR-044): a name a document's
// expressions resolve through it before it is ever judged a driver id
// (design D1, D7).
//
// What is still refused is a document that contradicts itself: an
// expression naming a qualified id neither its own drivers table nor its
// bindings table declares has no value to bind, and rendering it anyway
// would show a wrong machine instead of an error. The producer
// guarantees every referenced id appears in one of the two; this is what
// makes a broken producer loud. A `params` expression, and an entry's own
// expression, are expressions like any other and are held to the same
// tables -- what a `params` expression would get wrong is the SHAPE
// rather than the pose. Beside it stand two refusals of the same kind: a
// schema version this build cannot read, and a flexible technology it
// cannot evaluate; the table itself is validated first, by `bindingTable`
// (D7), so a table this viewer cannot resolve is refused before a single
// expression is walked.
export interface LoadedDocument {
  table: BindingTable;
  /** The compiled program a version 5 document carries, or `null` for
   * every version 1 to 4 document -- so a host asks one question and
   * gets a truthful answer. */
  program: LoadedProgram | null;
  /** The controls a version 5 document's parts carry, parsed and
   * checked, in the document's own key order (OpenSpec
   * `drive-the-run-by-touch`, design D1). `[]` for a document with no
   * key, which is every document published before this viewer could
   * read one. */
  controls: LoadedControl[];
}

/** `#RRGGBB`, and nothing else. The producer REQUIRES a colour on a
 * marking (solid-node design D6: "a decal with no colour is invisible,
 * which means the declaration did nothing"), so a shorthand, a name or a
 * number is a producer bug rather than a value to guess at. */
const HEX_COLOR = /^#[0-9a-fA-F]{6}$/;

/** Refuse a `markings` list this viewer cannot read, by name (OpenSpec
 * `draw-what-a-part-carries`, design D6).
 *
 * Why refuse rather than ignore: the framework blesses a consumer that
 * ignores `markings` entirely -- it renders today's picture, which is a
 * TRUTHFUL picture. This viewer does not ignore them, and one that read
 * nine digits and silently dropped the tenth would show a FALSE
 * register. Half-reading is the failure mode; refusing names the
 * producer bug where it can be fixed.
 *
 * `mtime` is the one optional field, accepted absent exactly as a
 * node's own optional `mtime` is. */
export function assertMarkings(node: ManifestNode, sourceUrl: string): void {
  const markings = (node as { markings?: unknown }).markings;
  if (markings === undefined) {
    return;
  }
  const refuse = (reason: string): never => {
    throw new Error(
      `${sourceUrl} carries the node "${node.name}", whose ${reason}. ` +
      'Refusing the document rather than drawing part of what the part ' +
      'carries: a marking read in part is a false answer printed on a ' +
      'machine.',
    );
  };
  if (!Array.isArray(markings)) {
    refuse('"markings" is not a list');
  }
  // A marking is a region of a PART's surface: the producer cannot emit
  // one on a node carrying children or a flexible spec, and drawing a
  // decal on either would put it somewhere the document never said.
  if ((markings as unknown[]).length > 0
      && (node.children !== undefined || node.flexible !== undefined)) {
    refuse('markings sit on a node that is not rigid (it carries '
           + `${node.flexible !== undefined ? 'a flexible spec' : 'children'})`);
  }
  const seen = new Set<string>();
  (markings as unknown[]).forEach((entry, index) => {
    if (typeof entry !== 'object' || entry === null || Array.isArray(entry)) {
      refuse(`marking at index ${index} is not an object`);
    }
    const marking = entry as Record<string, unknown>;
    if (typeof marking.name !== 'string' || marking.name === '') {
      refuse(`marking at index ${index} declares no name`);
    }
    const name = marking.name as string;
    if (seen.has(name)) {
      refuse(`markings declare the name "${name}" twice`);
    }
    seen.add(name);
    if (typeof marking.model !== 'string' || marking.model === '') {
      refuse(`marking "${name}" names no artifact`);
    }
    if (typeof marking.color !== 'string' || !HEX_COLOR.test(marking.color)) {
      refuse(`marking "${name}" declares the colour `
             + `${JSON.stringify(marking.color)}, which is not a six-digit `
             + '#RRGGBB');
    }
    if (marking.mtime !== undefined && typeof marking.mtime !== 'number') {
      refuse(`marking "${name}" declares an mtime that is not a number`);
    }
  });
}

export function assertRenderable(document: Manifest,
                                 sourceUrl: string): LoadedDocument {
  if (!RENDERED_VERSIONS.includes(document.version)) {
    throw new Error(
      `${sourceUrl} declares document version ${document.version}, which ` +
      `this viewer does not render; it renders versions ` +
      `${RENDERED_VERSIONS.join(', ')}. The document is written to a ` +
      'schema this build cannot read: refusing it rather than rendering ' +
      'part of a machine it does not understand.',
    );
  }

  // Built and validated FIRST (D7): a malformed table -- a bad shape, a
  // duplicate name, a forward-only violation, a name colliding with a
  // declared driver id, or an entry whose own expression this evaluation
  // cannot support -- is refused here, before any operation or `params`
  // expression is walked. `bindingTable` throws bare; nothing here
  // catches or rewords it.
  const table = bindingTable(document, sourceUrl);

  // The compiled program, loaded and validated by name (design §4)
  // before the tree's expressions are walked, so a program this engine
  // cannot execute is refused before a single pose is evaluated. A
  // document below version 5 carries none and loads exactly as it did.
  // A document DECLARING A RUNNING VERSION -- 5, or the 6 a self-read
  // law moves it to -- must carry one, whether or not the key is there:
  // that is the first thing design §4 refuses, and a version 6 document
  // with no `program` key must meet THAT sentence rather than be read
  // as a treeful document with nothing to run.
  const program = document.version >= 5
      || (document as RunDocument).program !== undefined
    ? loadProgram(document as RunDocument, sourceUrl, table)
    : null;
  // The `controls` table, read and checked HERE (design D1): after the
  // program its entries reference, and before the tree walk, so a table
  // this viewer cannot resolve is refused before a single thing is
  // rendered -- the surface an undeclared driver id, an unreadable
  // bindings table and an inexecutable program already stand on. A
  // document with no key gets `[]` and reaches exactly the code it
  // reached before (D2).
  const controls = readControls(document, sourceUrl, program);

  const uncomputed = program === null
    ? EMPTY : uncomputedValues(program);

  // Under version 5 the identifiers an expression may name widen with
  // the program: its clock, its bank coordinates and the values it
  // publishes as computed. A jump plan's branch placeholders are legal
  // only INSIDE that plan's own expressions -- which `loadProgram` has
  // already checked -- and are deliberately not admitted here.
  const declared = new Set([
    ...Object.keys(document.drivers ?? {}),
    ...(program === null ? [] : program.declaredNames),
  ]);
  const missing = new Set<string>();
  const unreadable = new Set<string>();

  // A name a document's expressions read, closed over the table (D5): a
  // binding name resolves away to what it transitively reads -- $t, a
  // declared driver id, or (a dangling reference) itself, unchanged --
  // BEFORE it is judged against the declared drivers. That is what makes
  // a binding name never reported as an undeclared driver, and what
  // still catches a name that is genuinely neither.
  const note = (expression: string) => {
    for (const name of table.closure(freeVariables(expression))) {
      if (name !== TIME_ID && !declared.has(name)) {
        missing.add(name);
      } else if (uncomputed.has(name)) {
        // A published computed value is not stored anywhere: one no edge
        // determines has no number to read, so a pose that reads it
        // would be posed from a number that was never produced.
        unreadable.add(name);
      }
    }
  };

  const visit = (node: ManifestNode) => {
    // Read FIRST for this node (OpenSpec `draw-what-a-part-carries`,
    // design D6): a `markings` list this viewer cannot read is refused
    // before anything is rendered, on the surface the bindings table,
    // the program and the controls table already stand on. A node with
    // no key reaches exactly the validation it reached before.
    assertMarkings(node, sourceUrl);
    for (const operation of node.operations) {
      const expressions = operation[0] === 'r'
        ? [operation[1]] : operation[1];
      for (const expression of expressions) {
        note(expression);
      }
    }
    if (node.flexible) {
      if (!evaluatesTech(node.flexible.tech)) {
        throw new Error(
          `${sourceUrl} carries the flexible node "${node.name}", whose ` +
          `technology "${node.flexible.tech}" this viewer cannot ` +
          `evaluate; it evaluates: ${knownTechnologies()}. Refusing the ` +
          'document rather than rendering a wrong shape.',
        );
      }
      const refusal = specRefusal(node.flexible.spec);
      if (refusal !== null) {
        throw new Error(
          `${sourceUrl} carries the flexible node "${node.name}", whose ` +
          `spec this viewer's ${node.flexible.tech} cannot read: ` +
          `${refusal}. Refusing the document rather than rendering a ` +
          'wrong shape.',
        );
      }
      Object.values(node.flexible.params).forEach(note);
    }
    (node.children ?? []).forEach(visit);
  };
  visit(document.root);

  // Entries the document never references are validated too (D7): an
  // entry naming an undeclared driver is a malformed table by the
  // producer's own rule, and checking it costs one closure lookup per
  // entry.
  //
  // One name more is legal HERE than in an operation: a jump plan's
  // BRANCH PLACEHOLDER (design §15 finding 2). A version 5 document
  // shares the subexpressions of its plans' skeletons into the same
  // table -- the acceptance document publishes `_b33 = (360.0 * _j0)`
  // and five more like it -- and a placeholder has a value only while
  // the plan that mints it is being integrated. This viewer never
  // evaluates the table forward: a binding resolves through the shared
  // DAG WHERE IT IS READ, so an entry nothing reads is never evaluated,
  // and `loadProgram` has already checked that each plan's own
  // expressions, closed over this table, name only that plan's
  // placeholders and that edge's sources. What stays refused is a
  // placeholder reached from an OPERATION, which no scope binds.
  const insidePlan = new Set([
    ...declared,
    ...(program === null ? [] : program.placeholders.keys()),
  ]);
  (document.bindings ?? []).forEach((entry) => {
    for (const name of table.closure(freeVariables(entry.expression))) {
      if (name !== TIME_ID && !insidePlan.has(name)) missing.add(name);
      else if (uncomputed.has(name)) unreadable.add(name);
    }
  });

  if (missing.size > 0) {
    const known = [...declared].sort().join(', ') || 'none';
    throw new Error(
      `${sourceUrl} has expressions naming undeclared drivers ` +
      `(${[...missing].sort().join(', ')}); its drivers table declares: ` +
      `${known}. The document is malformed: refusing it rather than ` +
      'rendering a wrong pose.',
    );
  }

  if (unreadable.size > 0) {
    throw new Error(
      `${sourceUrl} has expressions reading the published computed ` +
      `value(s) ${[...unreadable].sort().join(', ')}, which no edge of its ` +
      'program determines. A computed value is not stored anywhere: one ' +
      'nothing computes has no number to read. Refusing the document ' +
      'rather than posing the model from a number that was never ' +
      'produced.',
    );
  }

  return { table, program, controls };
}

async function loadDocument(
  sourceUrl: string,
): Promise<{ document: Manifest } & LoadedDocument> {
  let response: Response;
  try {
    response = await fetch(sourceUrl);
  } catch (error) {
    throw new Error(`Failed to load ${sourceUrl}: ${String(error)}`);
  }
  if (!response.ok) {
    throw new Error(`Failed to load ${sourceUrl}: ${response.status}`);
  }
  let document: Manifest;
  try {
    document = await response.json() as Manifest;
  } catch (error) {
    throw new Error(`Failed to parse ${sourceUrl}: ${String(error)}`);
  }
  const { table, program, controls } = assertRenderable(document, sourceUrl);
  return { document, table, program, controls };
}

function resolveContainer(target: HTMLElement | string): HTMLElement {
  if (typeof target !== 'string') {
    return target;
  }
  const element = document.querySelector<HTMLElement>(target);
  if (!element) {
    throw new Error(`solid-widget: no element matches "${target}"`);
  }
  return element;
}

// ---------------------------------------------------------------------
// The driver chrome's DOM (ADR-056 stage 3c). Everything below RENDERS a
// `ControlLayer` and calls back through the same driving API a host
// uses; it decides nothing itself, because there is no DOM test
// framework in this bench and an untestable decision is a decision
// nobody checks (design D1). Its proof is the live browser drive.

interface DriverChromeActions {
  setDriver(id: string, value: number): void;
  trigger(name: string): TriggerHandle;
  focus(path: AssemblyPath | null): void;
}

interface DriverChrome {
  /** A driver moved: update its readout, and its input unless the
   * maker's own hand is what moved it. */
  apply(id: string, value: number, fromChrome: boolean): void;
  remove(): void;
}

type ControlUpdate = (value: number, fromChrome: boolean) => void;

const PANEL_STYLE =
  'position:absolute;left:0;top:0;display:flex;flex-direction:column;' +
  'gap:6px;padding:8px 10px;max-width:75%;' +
  'background:rgba(30,33,38,0.65);color:#fff;' +
  'font:13px system-ui,sans-serif;';

const BUTTON_STYLE =
  'background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.25);' +
  'color:inherit;cursor:pointer;border-radius:4px;padding:2px 8px;' +
  'font:inherit;';

function buildDriverChrome(
  container: HTMLElement,
  layer: ControlLayer,
  actions: DriverChromeActions,
): DriverChrome {
  const panel = document.createElement('div');
  panel.className = 'driver-controls';
  panel.style.cssText = PANEL_STYLE;

  panel.append(buildBreadcrumb(layer.breadcrumb, layer.children,
                               actions.focus, 'driver'));

  if (layer.instructions.length > 0) {
    const row = document.createElement('div');
    row.className = 'driver-instructions';
    row.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;';
    layer.instructions.forEach((entry) => {
      row.append(buildInstructionButton(entry.name, entry.label, actions));
    });
    panel.append(row);
  }

  const updates = new Map<string, ControlUpdate>();
  layer.drivers.forEach((control) => {
    panel.append(buildDriverRow(control, actions, updates));
  });

  container.append(panel);

  return {
    apply(id: string, value: number, fromChrome: boolean) {
      updates.get(id)?.(value, fromChrome);
    },
    remove() {
      panel.remove();
    },
  };
}

// One breadcrumb, for either chrome: the posed one and the running one
// follow the SAME focused layer, so they navigate it through the same
// element rather than through two that could drift apart. `prefix`
// keeps the class names each chrome's own.
function buildBreadcrumb(
  trail: BreadcrumbSegment[],
  children: string[],
  focus: (path: AssemblyPath | null) => void,
  prefix: string,
): HTMLElement {
  const nav = document.createElement('nav');
  nav.className = `${prefix}-breadcrumb`;
  nav.setAttribute('aria-label', 'Assembly focus');
  nav.style.cssText =
    'display:flex;flex-wrap:wrap;align-items:center;gap:4px;';

  trail.forEach((segment, index) => {
    if (index > 0) {
      nav.append(separator('/'));
    }
    nav.append(buildBreadcrumbStep(segment, focus, prefix));
  });

  const focused = trail[trail.length - 1].path;
  children.forEach((name) => {
    nav.append(separator('|'));
    const button = document.createElement('button');
    button.className = `${prefix}-descend`;
    button.textContent = `${name} ▸`;
    button.setAttribute('aria-label', `Focus ${name}`);
    button.style.cssText = BUTTON_STYLE;
    button.addEventListener('click', () => {
      focus([...focused, name]);
    });
    nav.append(button);
  });

  return nav;
}

function buildBreadcrumbStep(
  segment: BreadcrumbSegment,
  focus: (path: AssemblyPath | null) => void,
  prefix: string,
): HTMLElement {
  const button = document.createElement('button');
  button.className = `${prefix}-breadcrumb-step`;
  button.textContent = segment.label;
  button.setAttribute('aria-label', `Focus ${segment.label}`);
  button.style.cssText = BUTTON_STYLE;
  if (segment.current) {
    button.setAttribute('aria-current', 'true');
    button.disabled = true;
    button.style.cssText += 'opacity:0.75;cursor:default;';
    return button;
  }
  button.addEventListener('click', () => {
    // The document root is `null` to the focus API, not an empty path.
    focus(segment.path.length === 0 ? null : segment.path);
  });
  return button;
}

function separator(mark: string): HTMLElement {
  const span = document.createElement('span');
  span.textContent = mark;
  span.setAttribute('aria-hidden', 'true');
  span.style.cssText = 'opacity:0.5;';
  return span;
}

function buildInstructionButton(
  name: string,
  label: string,
  actions: DriverChromeActions,
): HTMLButtonElement {
  const button = document.createElement('button');
  button.className = 'driver-instruction';
  button.textContent = label;
  button.setAttribute('aria-label', `Run ${label}`);
  button.style.cssText = BUTTON_STYLE;
  // Which run this button is showing. A re-press is the ratified
  // last-wins replacement, so the older run's `done` -- which settles
  // when the new one takes its drivers over -- must not clear the busy
  // state the newer press owns. Nothing is debounced: the maker asked
  // twice and the machine obeys twice.
  let latest = 0;
  button.addEventListener('click', () => {
    const run = ++latest;
    button.setAttribute('aria-busy', 'true');
    button.style.cssText = BUTTON_STYLE + 'background:rgba(127,209,255,0.35);';
    actions.trigger(name).done.then(() => {
      if (run !== latest) {
        return;
      }
      button.removeAttribute('aria-busy');
      button.style.cssText = BUTTON_STYLE;
    });
  });
  return button;
}

function buildDriverRow(
  control: DriverControl,
  actions: DriverChromeActions,
  updates: Map<string, ControlUpdate>,
): HTMLElement {
  const row = document.createElement('div');
  row.className = 'driver-control';
  row.style.cssText = 'display:flex;align-items:center;gap:8px;';

  const name = document.createElement('span');
  name.textContent = control.label;
  name.style.cssText = 'min-width:5em;';

  const input = document.createElement('input');
  input.setAttribute('aria-label', control.unit === null
    ? control.label : `${control.label} (${control.unit})`);
  if (control.slider !== null) {
    input.type = 'range';
    input.min = String(control.slider.min);
    input.max = String(control.slider.max);
    // An integer driver stops on whole native units; a float one is
    // continuous, and 'any' is how that is spelled.
    input.step = control.slider.step === null
      ? 'any' : String(control.slider.step);
    input.value = String(control.slider.position);
    input.style.cssText = 'flex:1;margin:0;min-width:120px;';
  } else {
    // No declared range, so no bounds to travel between: a number field
    // is the honest control, rather than a slider spanning a guess.
    input.type = 'number';
    input.value = formatDisplay(control.display);
    input.style.cssText = 'width:8em;font:inherit;';
  }

  // A readout that holds still under a drag. The number and the unit
  // are separate elements so the alignment box is the NUMBER's: writing
  // them as one right-aligned string pins the unit and lets the digits
  // walk about underneath it. Tabular figures make every digit the same
  // width -- the panel's system font is otherwise proportional, so even
  // a constant digit count would shift -- and that is also what makes
  // the `ch` reservation exact, since `ch` is the width of `0`. Ten:
  // sign, four integer digits, point, four decimals. The passive form uses
  // a minimum; the temporary editor occupies the same stable box.
  const readout = document.createElement('span');
  readout.className = 'driver-readout';

  // A bounded driver keeps the old passive number beside its range input.
  // Activating that number temporarily opens an exact-entry text field. It
  // is deliberately not type=number: native spinner arrows are visual noise
  // here, and range remains a presentation bound only, so there are no
  // min/max attributes to copy to the editor.
  const exact = control.slider === null
    ? null : document.createElement('input');
  const figure = document.createElement('span');
  figure.className = 'driver-readout-value';
  figure.style.cssText = 'display:inline-block;min-width:10ch;text-align:right;'
    + 'font-variant-numeric:tabular-nums;';
  if (exact !== null) {
    figure.tabIndex = 0;
    figure.setAttribute('role', 'button');
    figure.setAttribute('aria-label', control.unit === null
      ? `Edit ${control.label} exact value`
      : `Edit ${control.label} exact value (${control.unit})`);
    exact.className = 'driver-readout-editor';
    exact.type = 'text';
    exact.inputMode = 'decimal';
    exact.style.cssText = 'display:none;box-sizing:border-box;width:10ch;'
      + 'text-align:right;font:inherit;font-variant-numeric:tabular-nums;'
      + 'background:transparent;color:inherit;border:0;padding:0;';
    exact.setAttribute('aria-label', control.unit === null
      ? `${control.label} exact value`
      : `${control.label} exact value (${control.unit})`);
  }

  // The separating space lives in the text, not in a flex gap, so the
  // readout still READS as "12.3457 mm" to a screen reader and to
  // anyone who copies it. A single space is a constant width, so it
  // costs the alignment nothing.
  const unit = document.createElement('span');

  readout.append(figure);
  if (exact !== null) {
    readout.append(exact);
  }
  readout.append(unit);

  let current = control;
  const show = (state: DriverControl) => {
    current = state;
    figure.textContent = formatReadout(state.display);
    if (exact !== null && document.activeElement !== exact) {
      exact.value = formatReadout(state.display);
    }
    unit.textContent = state.unit === null ? '' : ` ${state.unit}`;
    // Pinned thumb, truthful readout: the value is outside the declared
    // travel and the chrome says so instead of hiding it.
    readout.style.color = state.pinned ? '#ffd166' : 'inherit';
    readout.title = state.pinned
      ? 'outside the declared range' : '';
  };
  show(control);

  const write = (source: HTMLInputElement) => {
    const design = source.valueAsNumber;
    if (!Number.isFinite(design)) {
      return;
    }
    // Through the same conversion an instruction target takes and into
    // the same store call the host API makes -- one door, so a value
    // set on screen and one set programmatically are the same event.
    actions.setDriver(control.id, toNative(design, control.driver));
  };
  input.addEventListener('input', () => write(input));
  input.addEventListener('change', () => write(input));
  if (exact !== null) {
    let cancelEdit = false;
    const beginEdit = () => {
      exact.value = formatReadout(current.display);
      figure.style.display = 'none';
      exact.style.display = 'inline-block';
      exact.focus();
      exact.select();
    };
    const commitEdit = () => {
      const text = exact.value.trim();
      const design = text === '' ? Number.NaN : Number(text);
      if (Number.isFinite(design)) {
        actions.setDriver(control.id, toNative(design, control.driver));
      }
    };
    const finishEdit = () => {
      exact.style.display = 'none';
      figure.style.display = 'inline-block';
      exact.value = formatReadout(current.display);
    };
    figure.addEventListener('click', beginEdit);
    figure.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        beginEdit();
      }
    });
    exact.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        exact.blur();
      } else if (event.key === 'Escape') {
        event.preventDefault();
        cancelEdit = true;
        exact.blur();
      }
    });
    exact.addEventListener('blur', () => {
      if (!cancelEdit) {
        commitEdit();
      }
      cancelEdit = false;
      finishEdit();
    });
  }

  updates.set(control.id, (value: number, fromChrome: boolean) => {
    const state = driverControl(control.id, control.driver, value);
    show(state);
    if (!(fromChrome && document.activeElement === input)) {
      input.value = state.slider === null
        ? formatDisplay(state.display) : String(state.slider.position);
    }
  });

  row.append(name, input, readout);
  return row;
}

function fillSpeedControl(select: HTMLSelectElement, speed: number): void {
  select.replaceChildren();
  for (const value of ladderFor(speed)) {
    const option = document.createElement('option');
    option.value = String(value);
    option.textContent = `\u00d7${value}`;
    select.append(option);
  }
  select.value = String(speed);
}

function buildControls(
  container: HTMLElement,
  animation: Animation,
  speed: number,
  plan: ReturnType<typeof controlPlan>,
  isPlaying: () => boolean,
  setPlaying: (playing: boolean) => void,
  setTime: (time: number) => void,
  setSpeed: (speed: number) => void,
): {
  slider: HTMLInputElement;
  speedControl?: HTMLSelectElement;
  readout?: HTMLElement;
  elements: HTMLElement[];
} {
  const frames = animation.frames;
  const bar = document.createElement('div');
  bar.className = 'animation-controls';
  if (plan.styled) {
    bar.style.cssText =
      'position:absolute;left:0;right:0;bottom:0;display:flex;' +
      'align-items:center;gap:8px;padding:6px 10px;' +
      'background:rgba(30,33,38,0.65);color:#fff;' +
      'font:13px system-ui,sans-serif;';
  }

  const button = document.createElement('button');
  if (plan.styled) {
    button.style.cssText =
      'background:none;border:none;color:inherit;cursor:pointer;' +
      'font-size:15px;padding:0 4px;line-height:1;';
  }
  const updateButton = () => {
    button.textContent = isPlaying() ? '⏸' : '▶';
    button.title = isPlaying() ? 'Pause' : 'Play';
  };
  updateButton();
  button.addEventListener('click', () => {
    setPlaying(!isPlaying());
    updateButton();
  });

  const slider = document.createElement('input');
  slider.type = 'range';
  slider.min = '0';
  slider.max = String(Math.max(frames - 1, 0));
  slider.step = '1';
  slider.value = '0';
  if (plan.styled) {
    slider.style.cssText = 'flex:1;margin:0;';
  }
  slider.addEventListener('input', () => {
    setPlaying(false);
    updateButton();
    setTime(timelineTime(Number(slider.value), frames));
  });

  bar.append(button, slider);
  // A declared loop earns two more elements: the speed the maker
  // watches at, and the machine time the slider stands at. Without a
  // loop the bar is exactly the one it always was.
  let speedControl: HTMLSelectElement | undefined;
  let readout: HTMLElement | undefined;
  if (animation.loop !== undefined) {
    readout = document.createElement('span');
    readout.className = 'machine-time';
    readout.setAttribute('aria-live', 'off');
    if (plan.styled) {
      readout.style.cssText =
        'font-variant-numeric:tabular-nums;min-width:6ch;text-align:right;';
    }
    speedControl = document.createElement('select');
    speedControl.className = 'playback-speed';
    speedControl.setAttribute('aria-label', 'Playback speed');
    speedControl.title = 'Playback speed, as a multiple of real time';
    if (plan.styled) {
      speedControl.style.cssText =
        'background:none;border:1px solid rgba(255,255,255,0.4);' +
        'border-radius:3px;color:inherit;font:inherit;padding:1px 4px;';
    }
    fillSpeedControl(speedControl, speed);
    speedControl.addEventListener('change', () => {
      setSpeed(Number(speedControl!.value));
    });
    bar.append(readout, speedControl);
  }
  const elements: HTMLElement[] = [bar];
  if (plan.toggle) {
    const toggle = document.createElement('button');
    toggle.className = 'timeline-toggle';
    toggle.textContent = 'Timeline';
    toggle.setAttribute('aria-expanded', 'false');
    bar.hidden = true;
    toggle.addEventListener('click', () => {
      bar.hidden = !bar.hidden;
      toggle.setAttribute('aria-expanded', String(!bar.hidden));
    });
    container.append(toggle);
    elements.unshift(toggle);
  }
  container.append(bar);
  return { slider, speedControl, readout, elements };
}

// ---------------------------------------------------------------------
// The RUNNING chrome's DOM (OpenSpec `drive-the-run-on-screen`).
// Everything below RENDERS a `RunControlLayer` and calls back through
// the same `run()` handle a host uses; it decides nothing itself,
// because every decision lives in `runControls.ts` where plain node can
// test it. Its proof is the live browser drive.
//
// What a maker meets is one row per declared input -- its committed
// position, a nudge pair, a hold-to-jog pair and the amount and rate
// those two will ask for -- one button per declared instruction, and a
// transport bar. There is no slider and no timeline, because a slider
// writes a position into a coordinate and a coordinate under a run
// carries history.

interface RunChromeActions {
  nudge(id: string, amount: number, seconds: number): void;
  jogStart(id: string, rate: number): void;
  jogStop(id: string): void;
  trigger(name: string): void;
  setNudge(id: string, plan: NudgePlan): void;
  setJog(id: string, plan: JogPlan): void;
  play(): void;
  step(): void;
  reset(): void;
  setSpeed(speed: number): void;
  focus(path: AssemblyPath | null): void;
}

interface RunChrome {
  /** A committed frame: the readouts follow it, and only the controls
   * whose input moved are written. */
  commit(frame: CommittedFrame): void;
  /** What became of the last request one control made, and whether
   * that control still has one in flight. */
  outcome(key: string, report: OutcomeReport | null, busy?: boolean): void;
  /** The run's own message for a tick it refused, or null to clear it. */
  refuse(message: string | null): void;
  /** Everything the transport shows. */
  transport(plan: TransportPlan): void;
  /** What a republish did to the run, or null. */
  notice(message: string | null): void;
  clearOutcomes(): void;
  remove(): void;
}

// A running document's panel carries more per row than a posed one --
// a readout, two control pairs and the three fields those pairs will
// ask with -- so it is given the width to keep one input on one line.
const RUN_PANEL_STYLE = PANEL_STYLE.replace('max-width:75%;',
                                            'max-width:96%;');

const RUN_FIELD_STYLE =
  'width:3.6em;font:inherit;background:rgba(255,255,255,0.08);'
  + 'border:1px solid rgba(255,255,255,0.25);border-radius:3px;'
  + 'color:inherit;padding:1px 3px;';

const RUN_LEGEND_STYLE = 'opacity:0.6;font-size:11px;';

const RUN_OUTCOME_STYLE =
  'opacity:0.85;font-size:11px;min-height:13px;max-width:32em;';

/** What became of one request, from the handles it created.
 *
 * A `trigger` claims one command per input it moves, so the honest
 * summary is the first one that did NOT simply complete -- a blocked or
 * refused half of an instruction is the half worth reading. */
function summarise(settled: readonly Outcome[],
                   unit: string | null): OutcomeReport {
  const notable = settled.find((one) => one.status !== 'completed');
  const chosen = notable ?? settled[settled.length - 1];
  if (chosen === undefined) {
    return { status: 'completed', admitted: null, unit, message: null };
  }
  return {
    status: chosen.status as OutcomeReport['status'],
    admitted: chosen.admitted,
    unit,
    message: null,
  };
}

function buildRunChrome(
  container: HTMLElement,
  layer: RunControlLayer,
  actions: RunChromeActions,
): RunChrome {
  const panel = document.createElement('div');
  panel.className = 'run-controls';
  panel.style.cssText = RUN_PANEL_STYLE;

  panel.append(buildBreadcrumb(layer.breadcrumb, layer.children,
                               actions.focus, 'run'));

  const reports = new Map<string, OutcomeWriter>();
  const rows = new Map<string, (value: number) => void>();
  const releasers = new Set<() => void>();

  if (layer.instructions.length > 0) {
    panel.append(legend('Instructions'));
    const row = document.createElement('div');
    row.className = 'run-instructions';
    row.style.cssText = 'display:flex;flex-wrap:wrap;gap:10px;';
    layer.instructions.forEach((entry) => {
      row.append(buildInstructionControl(entry, actions, reports));
    });
    panel.append(row);
  }

  if (layer.inputs.length > 0) {
    panel.append(legend('Inputs — ask the machine to move'));
    layer.inputs.forEach((control) => {
      panel.append(buildRunInputRow(control, actions, reports, rows,
                                    releasers));
    });
  }

  const refusalLine = document.createElement('div');
  refusalLine.className = 'run-refusal';
  refusalLine.hidden = true;
  refusalLine.setAttribute('role', 'status');
  refusalLine.style.cssText =
    'color:#ffd166;font-size:12px;max-width:40em;';
  panel.append(refusalLine);

  const noticeLine = document.createElement('div');
  noticeLine.className = 'run-notice';
  noticeLine.hidden = true;
  noticeLine.setAttribute('role', 'status');
  noticeLine.style.cssText = 'opacity:0.7;font-size:11px;max-width:40em;';
  panel.append(noticeLine);

  container.append(panel);

  // A jog left engaged is the failure that damages trust, so the same
  // release runs on a pointer that goes away AND on a page that does:
  // the window losing focus, and the page ceasing to be displayed.
  const releaseAll = () => { releasers.forEach((release) => release()); };
  window.addEventListener('blur', releaseAll);
  const onVisibility = () => { if (document.hidden) releaseAll(); };
  document.addEventListener('visibilitychange', onVisibility);

  const bar = buildTransportBar(layer.transport, actions);
  container.append(bar.element);

  return {
    commit(frame: CommittedFrame) {
      for (const id of frame.moved) {
        rows.get(id)?.(frame.bank[id]);
      }
    },
    outcome(key: string, report: OutcomeReport | null, busy = false) {
      reports.get(key)?.(report, busy);
    },
    refuse(message: string | null) {
      refusalLine.hidden = message === null;
      refusalLine.textContent = message === null ? '' : `refused: ${message}`;
    },
    transport: bar.update,
    notice(message: string | null) {
      noticeLine.hidden = message === null;
      noticeLine.textContent = message ?? '';
    },
    clearOutcomes() {
      reports.forEach((write) => write(null, false));
    },
    remove() {
      releaseAll();
      window.removeEventListener('blur', releaseAll);
      document.removeEventListener('visibilitychange', onVisibility);
      panel.remove();
      bar.element.remove();
    },
  };
}

function legend(text: string): HTMLElement {
  const span = document.createElement('span');
  span.className = 'run-legend';
  span.textContent = text;
  span.style.cssText = RUN_LEGEND_STYLE;
  return span;
}

function outcomeElement(): HTMLElement {
  const span = document.createElement('span');
  span.className = 'run-outcome';
  span.setAttribute('aria-live', 'polite');
  span.style.cssText = RUN_OUTCOME_STYLE;
  return span;
}

type OutcomeWriter = (report: OutcomeReport | null, busy: boolean) => void;

/** Writes a report into one element, and marks the control that issued
 * it busy while any request it made is still in flight.
 *
 * The two are deliberately separate questions. A second press on an
 * input the first press still owns is refused AT ONCE -- so the text
 * says so immediately -- while the movement already running is
 * untouched, and the button goes on indicating the run until its own
 * commands retire. */
function outcomeWriter(target: HTMLElement,
                       indicator?: HTMLElement): OutcomeWriter {
  return (report, busy) => {
    target.textContent = formatOutcome(report);
    target.title = report?.message ?? '';
    target.style.color = report !== null
      && (report.status === 'refused' || report.status === 'blocked')
      ? '#ffd166' : 'inherit';
    if (indicator === undefined) {
      return;
    }
    if (busy) {
      indicator.setAttribute('aria-busy', 'true');
      indicator.style.cssText = BUTTON_STYLE
        + 'background:rgba(127,209,255,0.35);';
    } else {
      indicator.removeAttribute('aria-busy');
      indicator.style.cssText = BUTTON_STYLE;
    }
  };
}

function buildInstructionControl(
  entry: RunInstructionControl,
  actions: RunChromeActions,
  reports: Map<string, OutcomeWriter>,
): HTMLElement {
  const cell = document.createElement('div');
  cell.className = 'run-instruction-control';
  cell.dataset.instruction = entry.name;
  cell.style.cssText = 'display:flex;flex-direction:column;gap:2px;';

  const button = document.createElement('button');
  button.className = 'run-instruction';
  button.dataset.instruction = entry.name;
  button.textContent = entry.label;
  // The button REFERENCES the instruction; it does not repeat its
  // definition, and a travel (`by`) and a target are one button apiece.
  button.setAttribute('aria-label', `Run ${entry.label}`);
  button.style.cssText = BUTTON_STYLE;
  button.addEventListener('click', () => { actions.trigger(entry.name); });

  const report = outcomeElement();
  const write = outcomeWriter(report, button);
  write(entry.outcome, entry.outcome?.status === 'active');
  reports.set(entry.name, write);

  cell.append(button, report);
  return cell;
}

function buildRunInputRow(
  control: RunInputControl,
  actions: RunChromeActions,
  reports: Map<string, OutcomeWriter>,
  rows: Map<string, (value: number) => void>,
  releasers: Set<() => void>,
): HTMLElement {
  const row = document.createElement('div');
  row.className = 'run-input';
  row.dataset.input = control.id;
  row.style.cssText =
    'display:flex;flex-wrap:wrap;align-items:center;gap:6px;';

  const name = document.createElement('span');
  name.className = 'run-input-name';
  name.textContent = control.label;
  name.style.cssText = 'min-width:7em;';

  // A follow-only readout: it never becomes an editor, and there is no
  // way to type or drag a position into it. Tabular figures and a fixed
  // `ch` reservation keep the digits still under a jog, the same
  // treatment the posed chrome's passive readout has.
  const readout = document.createElement('span');
  readout.className = 'run-readout';
  const figure = document.createElement('span');
  figure.className = 'run-readout-value';
  figure.style.cssText = 'display:inline-block;min-width:9ch;text-align:right;'
    + 'font-variant-numeric:tabular-nums;';
  const unit = document.createElement('span');
  unit.className = 'run-readout-unit';
  readout.append(figure, unit);
  readout.setAttribute('aria-label', control.unit === null
    ? `${control.label} position`
    : `${control.label} position (${control.unit})`);

  let amount = control.nudge.amount;
  let seconds = control.nudge.seconds;
  let rate = control.jog.rate;

  const nudgeGroup = document.createElement('span');
  nudgeGroup.style.cssText = 'display:inline-flex;gap:2px;';
  const nudge = (sign: number, mark: string, way: string) => {
    const button = document.createElement('button');
    button.className = 'run-nudge';
    button.dataset.direction = sign < 0 ? '-' : '+';
    button.textContent = mark;
    button.setAttribute('aria-label', `Nudge ${control.label} ${way}`);
    button.title = `Ask ${control.label} to move ${way} by the amount beside`;
    button.style.cssText = BUTTON_STYLE;
    button.addEventListener('click', () => {
      actions.nudge(control.id, sign * amount, seconds);
    });
    return button;
  };
  nudgeGroup.append(nudge(-1, '−', 'down'), nudge(1, '+', 'up'));

  const jogGroup = document.createElement('span');
  jogGroup.style.cssText = 'display:inline-flex;gap:2px;';
  const jog = (sign: number, mark: string, way: string) => {
    const button = document.createElement('button');
    button.className = 'run-jog';
    button.dataset.direction = sign < 0 ? '-' : '+';
    button.textContent = mark;
    button.setAttribute('aria-label', `Jog ${control.label} ${way}`);
    button.title = `Hold to move ${control.label} ${way} at the rate beside`;
    button.style.cssText = BUTTON_STYLE;
    let held = false;
    const release = () => {
      if (!held) {
        return;
      }
      held = false;
      button.style.cssText = BUTTON_STYLE;
      actions.jogStop(control.id);
    };
    releasers.add(release);
    button.addEventListener('pointerdown', (event: PointerEvent) => {
      event.preventDefault();
      if (held) {
        return;
      }
      held = true;
      button.style.cssText = BUTTON_STYLE + 'background:rgba(127,209,255,0.35);';
      // Captured on press, so a drag off the button still releases.
      try {
        button.setPointerCapture(event.pointerId);
      } catch {
        // A browser that cannot capture still releases on pointerup.
      }
      actions.jogStart(control.id, sign * rate);
    });
    // Five independent release paths, because a pointer or a page that
    // goes away while the button is held must not leave a machine
    // running. The window's `blur` and the page's `visibilitychange`
    // are registered once, for the whole chrome.
    button.addEventListener('pointerup', release);
    button.addEventListener('pointercancel', release);
    button.addEventListener('lostpointercapture', release);
    return button;
  };
  jogGroup.append(jog(-1, '◂', 'down'), jog(1, '▸', 'up'));

  // The amount, the duration and the rate configure the REQUEST those
  // controls will make. Typing into one moves nothing.
  const field = (
    className: string, value: number, label: string,
    write: (parsed: number) => void,
  ): HTMLInputElement => {
    const input = document.createElement('input');
    input.className = className;
    input.type = 'number';
    input.step = 'any';
    input.value = formatDisplay(value);
    input.setAttribute('aria-label', label);
    input.title = label;
    input.style.cssText = RUN_FIELD_STYLE;
    const commit = () => {
      const parsed = Number(input.value);
      if (Number.isFinite(parsed)) {
        write(parsed);
      }
    };
    input.addEventListener('input', commit);
    input.addEventListener('change', commit);
    return input;
  };

  const amountField = field('run-amount', amount,
    `Nudge ${control.label} by (${control.unit ?? 'design units'})`,
    (parsed) => {
      amount = parsed;
      actions.setNudge(control.id, { amount, seconds });
    });
  const secondsField = field('run-seconds', seconds,
    `Nudge ${control.label} over (seconds)`, (parsed) => {
      seconds = parsed;
      actions.setNudge(control.id, { amount, seconds });
    });
  const rateField = field('run-rate', rate,
    `Jog ${control.label} at (${control.unit ?? 'design units'} per second)`,
    (parsed) => {
      rate = parsed;
      actions.setJog(control.id, { rate });
    });

  const report = outcomeElement();
  const write = outcomeWriter(report);
  write(control.outcome, control.outcome?.status === 'active');
  reports.set(control.id, write);

  const show = (state: RunInputControl) => {
    figure.textContent = state.readout;
    unit.textContent = state.unit === null ? '' : ` ${state.unit}`;
  };
  show(control);
  rows.set(control.id, (value: number) => {
    show(runInputControl(control.id, control.driver, value));
  });

  row.append(name, readout, nudgeGroup, label('by'), amountField,
             label('over'), secondsField, label('s'),
             jogGroup, label('at'), rateField,
             label(control.unit === null ? '/s' : `${control.unit}/s`),
             report);
  return row;
}

function label(text: string): HTMLElement {
  const span = document.createElement('span');
  span.textContent = text;
  span.style.cssText = RUN_LEGEND_STYLE;
  return span;
}

function buildTransportBar(
  plan: TransportPlan,
  actions: RunChromeActions,
): { element: HTMLElement; update: (plan: TransportPlan) => void } {
  const bar = document.createElement('div');
  bar.className = 'run-transport';
  bar.style.cssText =
    'position:absolute;left:0;right:0;bottom:0;display:flex;' +
    'align-items:center;gap:8px;padding:6px 10px;' +
    'background:rgba(30,33,38,0.65);color:#fff;' +
    'font:13px system-ui,sans-serif;';

  const play = document.createElement('button');
  play.className = 'run-play';
  // Words rather than the animation bar's transport glyphs: a headless
  // or minimal font renders ⏸ as an empty box, and a maker meeting a
  // machine for the first time should not have to guess.
  play.style.cssText = BUTTON_STYLE + 'min-width:5em;';
  play.addEventListener('click', () => { actions.play(); });

  const step = document.createElement('button');
  step.className = 'run-step';
  step.textContent = 'Step';
  step.setAttribute('aria-label', 'Step one step of the run');
  step.title = 'Advance exactly one step of the run';
  step.style.cssText = BUTTON_STYLE;
  step.addEventListener('click', () => { actions.step(); });

  const speed = document.createElement('select');
  speed.className = 'run-speed';
  speed.setAttribute('aria-label', 'Playback speed');
  // Speed changes how fast the machine is WATCHED, never how finely it
  // is simulated.
  speed.title = 'How fast the machine is watched, as a multiple of real '
    + 'time. The step size never changes.';
  speed.style.cssText =
    'background:none;border:1px solid rgba(255,255,255,0.4);' +
    'border-radius:3px;color:inherit;font:inherit;padding:1px 4px;';
  speed.addEventListener('change', () => {
    actions.setSpeed(Number(speed.value));
  });

  const elapsed = document.createElement('span');
  elapsed.className = 'run-elapsed';
  elapsed.setAttribute('aria-label', 'Elapsed simulation time');
  elapsed.setAttribute('aria-live', 'off');
  elapsed.style.cssText =
    'font-variant-numeric:tabular-nums;min-width:8ch;text-align:right;';

  const reset = document.createElement('button');
  reset.className = 'run-reset';
  reset.textContent = 'Reset';
  reset.setAttribute('aria-label', 'Reset the run to its initial state');
  reset.title = 'Back to the state the document was mounted at';
  reset.style.cssText = BUTTON_STYLE;
  reset.addEventListener('click', () => { actions.reset(); });

  // Deliberately NO timeline: seeking belongs to recorded history, and a
  // running document has no animation fraction to drag.
  const spacer = document.createElement('span');
  spacer.style.cssText = 'flex:1;';
  bar.append(play, step, spacer, elapsed, speed, reset);

  const update = (next: TransportPlan) => {
    play.textContent = next.running ? 'Pause' : 'Run';
    play.title = next.running ? 'Pause the run' : 'Run';
    play.setAttribute('aria-label', next.running ? 'Pause the run' : 'Run');
    elapsed.textContent = next.elapsed;
    elapsed.title = `step ${next.tick}`;
    if (speed.value !== String(next.speed)) {
      fillSpeedControl(speed, next.speed);
    }
  };
  update(plan);

  return { element: bar, update };
}
