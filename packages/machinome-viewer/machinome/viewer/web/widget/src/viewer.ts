/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { frameBounds, ViewerView } from './camera';
import { AssemblyNavigation } from './assembly';
import {
  controlPlan, resolveBaseUrl, resolveOptions, showsDriverChrome,
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
import { API_VERSION } from './version';

export type AnimationMode = 'inline' | 'toggle' | 'none' | 'external';
// Whether the widget presents the driver chrome itself. A host building
// its own instrument panel on the driving API asks for 'none' and keeps
// every method below (ADR-056 stage 3c, design D9).
export type DriverControlsMode = 'inline' | 'none';
export type View = ViewerView;
export type { AssemblyNode, AssemblyPath } from './tree';
export type VectorInput = THREE.Vector3 | readonly [number, number, number];
export interface ViewInput {
  camera: VectorInput;
  target: VectorInput;
}

export interface ViewerOptions {
  baseUrl?: string;
  animation?: AnimationMode;
  driverControls?: DriverControlsMode;
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

export interface ViewerHandle {
  dispose(): void;
  view(): View;
  reload(): Promise<void>;
  artifactChanged(path: string): Promise<void>;
  manifestChanged(): Promise<void>;
  assembly(): AssemblyNode;
  setRoot(path: AssemblyPath | null): void;
  setVisible(path: AssemblyPath, visible: boolean): void;
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
   * at its published rest bank before the first tick is ever taken. */
  const startRuntime = async (document: Manifest,
                             program: LoadedProgram | null) => {
    runtime?.dispose();
    runtime = undefined;
    loadedProgram = program;
    elapsedSeconds = 0;
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
      renderer.render(scene, camera);
    });
    // Awaited before the tree is built, so the handle a host receives
    // answers for a run that has loaded its program -- and so a program
    // the ENGINE refuses (rather than the loader) refuses the mount.
    await started.ready;
  };

  const replaceTree = async (view: View | null) => {
    const { document, table, program } = await loadDocument(sourceUrl);
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

    refreshControls(document);
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
    renderer.render(scene, camera);
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
      driverChrome?.remove();
      driverChrome = undefined;
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
      await tree?.artifactChanged(path, baseUrl);
      if (tree) {
        assemblyNavigation.reconcile(tree);
      }
      renderer.render(scene, camera);
    },
    async manifestChanged() {
      const { document, table, program } = await loadDocument(sourceUrl);
      drivers.reconcile(document.drivers ?? {}, document.instructions ?? {});
      // Installed before the update that follows (design D6): a
      // republish carrying a different table invalidates the free set
      // of every node that reads it differently, whether or not that
      // node's own operations changed.
      bindingsTable = table;
      await startRuntime(document, program);
      await tree?.reconcile(document.root, baseUrl, null, bindingsTable);
      if (tree) {
        const rootChanged = assemblyNavigation.reconcile(tree);
        tree.update(scope());
        refreshControls(document);
        if (rootChanged) {
          applyFrame(null);
        }
      }
      renderer.render(scene, camera);
    },
    assembly() {
      if (!tree) {
        throw new Error('Viewer assembly is unavailable');
      }
      return tree.assembly();
    },
    setRoot(path: AssemblyPath | null) {
      focusOn(path);
    },
    setVisible(path: AssemblyPath, visible: boolean) {
      if (!tree) {
        throw new Error('Viewer assembly is unavailable');
      }
      assemblyNavigation.setVisible(tree, path, visible);
      renderer.render(scene, camera);
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
// mechanical `program`) joins it too, and a version 6 document is
// refused by name and by list -- the same sentence a version 5 document
// got from every viewer released so far.
//
// Exported so `version.test.ts` can pin it against the ONE declaration
// the bundle and `bundle.py` both read (`solidNodeDocumentVersions` in
// package.json): the number this viewer reports and the versions it
// refuses by must not be able to drift apart.
export const RENDERED_VERSIONS: readonly number[] = [1, 2, 3, 4, 5];

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
  // A document DECLARING the running version must carry one, whether or
  // not the key is there: that is the first thing design §4 refuses.
  const program = document.version === 5
      || (document as RunDocument).program !== undefined
    ? loadProgram(document as RunDocument, sourceUrl, table)
    : null;
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

  return { table, program };
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
  const { table, program } = assertRenderable(document, sourceUrl);
  return { document, table, program };
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

  panel.append(buildBreadcrumb(layer, actions));

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

function buildBreadcrumb(
  layer: ControlLayer,
  actions: DriverChromeActions,
): HTMLElement {
  const nav = document.createElement('nav');
  nav.className = 'driver-breadcrumb';
  nav.setAttribute('aria-label', 'Assembly focus');
  nav.style.cssText =
    'display:flex;flex-wrap:wrap;align-items:center;gap:4px;';

  layer.breadcrumb.forEach((segment, index) => {
    if (index > 0) {
      nav.append(separator('/'));
    }
    nav.append(buildBreadcrumbStep(segment, actions));
  });

  const focused = layer.breadcrumb[layer.breadcrumb.length - 1].path;
  layer.children.forEach((name) => {
    nav.append(separator('|'));
    const button = document.createElement('button');
    button.className = 'driver-descend';
    button.textContent = `${name} ▸`;
    button.setAttribute('aria-label', `Focus ${name}`);
    button.style.cssText = BUTTON_STYLE;
    button.addEventListener('click', () => {
      actions.focus([...focused, name]);
    });
    nav.append(button);
  });

  return nav;
}

function buildBreadcrumbStep(
  segment: BreadcrumbSegment,
  actions: DriverChromeActions,
): HTMLElement {
  const button = document.createElement('button');
  button.className = 'driver-breadcrumb-step';
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
    actions.focus(segment.path.length === 0 ? null : segment.path);
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
