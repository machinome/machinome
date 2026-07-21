import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
import { evaluate as jokEvaluate, tokenize } from "jokenizer";

export type RawOperation = ["r", string, number[]] | ["t", string[]];
export type ViewerNode = {
  name: string;
  color: string | null;
  model?: string;
  children?: ViewerNode[];
  operations: RawOperation[];
};
export type ViewerSnapshot = {
  version: number;
  animation: { fps: number; frames: number };
  root: ViewerNode;
};
export type ViewerView = { camera: THREE.Vector3; target: THREE.Vector3 };
export type MountedViewer = { dispose: () => void; view: () => ViewerView };

const expressionContext: Record<string, unknown> = {};
for (const name of Object.getOwnPropertyNames(Math)) expressionContext[name] = Math[name as keyof Math];
expressionContext.ln = Math.log;
expressionContext.log = (base: number, value: number) => Math.log(value) / Math.log(base);
expressionContext.mod = (left: number, right: number) => left % right;
expressionContext.sin = (degrees: number) => Math.sin(degrees * Math.PI / 180);
expressionContext.cos = (degrees: number) => Math.cos(degrees * Math.PI / 180);
expressionContext.tan = (degrees: number) => Math.tan(degrees * Math.PI / 180);
expressionContext.asin = (value: number) => Math.asin(value) * 180 / Math.PI;
expressionContext.acos = (value: number) => Math.acos(value) * 180 / Math.PI;
expressionContext.atan = (value: number) => Math.atan(value) * 180 / Math.PI;
expressionContext.atan2 = (y: number, x: number) => Math.atan2(y, x) * 180 / Math.PI;
const tokenCache = new Map<string, ReturnType<typeof tokenize>>();

function powify(node: unknown): unknown {
  if (node === null || typeof node !== "object") return node;
  if (Array.isArray(node)) return node.map(powify);
  const result = Object.fromEntries(Object.entries(node).map(([key, value]) => [key, powify(value)]));
  if (result.type === "Binary" && result.operator === "^") return { type: "Call", callee: { type: "Variable", name: "pow" }, args: [result.left, result.right] };
  return result;
}

function evalExpr(expression: string, time: number): number {
  let tokens = tokenCache.get(expression);
  if (!tokens) {
    tokens = powify(tokenize(expression)) as ReturnType<typeof tokenize>;
    tokenCache.set(expression, tokens);
  }
  const value = jokEvaluate(tokens, { ...expressionContext, $t: time });
  return typeof value === "number" ? value : Number(value);
}

function materialForColor(color: string | null): THREE.Material {
  return color === null
    ? new THREE.MeshNormalMaterial()
    : new THREE.MeshStandardMaterial({ color: new THREE.Color(color), metalness: 0.1, roughness: 0.6 });
}

class ViewerTree {
  readonly group = new THREE.Group();
  readonly children: ViewerTree[] = [];
  readonly loaded: Promise<void>;
  readonly animated: boolean;
  private readonly operations: RawOperation[];

  constructor(data: ViewerNode, baseUrl: string, inheritedColor: string | null = null) {
    this.group.matrixAutoUpdate = false;
    this.operations = data.operations ?? [];
    const color = data.color ?? inheritedColor;
    const pending: Promise<void>[] = [];
    if (data.model) pending.push(this.loadModel(`${baseUrl}${data.model}`, color));
    for (const childData of data.children ?? []) {
      const child = new ViewerTree(childData, baseUrl, color);
      this.children.push(child);
      this.group.add(child.group);
      pending.push(child.loaded);
    }
    this.loaded = Promise.all(pending).then(() => undefined);
    this.animated = this.operations.some((operation) => JSON.stringify(operation).includes("$t")) || this.children.some((child) => child.animated);
  }

  private async loadModel(url: string, color: string | null): Promise<void> {
    const geometry = await new STLLoader().loadAsync(url);
    geometry.computeVertexNormals();
    this.group.add(new THREE.Mesh(geometry, materialForColor(color)));
  }

  update(time: number): void {
    const matrix = new THREE.Matrix4();
    const step = new THREE.Matrix4();
    const axis = new THREE.Vector3();
    for (const operation of this.operations) {
      if (operation[0] === "r") {
        axis.set(operation[2][0], operation[2][1], operation[2][2]).normalize();
        step.makeRotationAxis(axis, evalExpr(operation[1], time) * Math.PI / 180);
      } else {
        step.makeTranslation(...operation[1].map((value) => evalExpr(value, time)) as [number, number, number]);
      }
      matrix.premultiply(step);
    }
    this.group.matrix.copy(matrix);
    for (const child of this.children) child.update(time);
  }
}

export async function mountViewer(container: HTMLElement, snapshotUrl: string, preservedView?: ViewerView): Promise<MountedViewer> {
  const response = await fetch(snapshotUrl);
  if (!response.ok) throw new Error(`Failed to load build snapshot: ${response.status}`);
  const snapshot = await response.json() as ViewerSnapshot;
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x556677, 1.2));
  const sun = new THREE.DirectionalLight(0xffffff, 1.5);
  sun.position.set(1, -1, 2);
  scene.add(sun);
  const tree = new ViewerTree(snapshot.root, "/artifacts/");
  scene.add(tree.group);
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.domElement.className = "functional-model";
  renderer.domElement.setAttribute("aria-label", "Functional model");
  renderer.domElement.setAttribute("role", "img");
  container.appendChild(renderer.domElement);
  const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 10000);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.rotateSpeed = 0.5;
  let time = 0;
  let playing = tree.animated;
  let slider: HTMLInputElement | undefined;
  let button: HTMLButtonElement | undefined;
  if (tree.animated) {
    const bar = document.createElement("div"); bar.className = "animation-controls";
    bar.hidden = true;
    const toggle = document.createElement("button");
    toggle.className = "timeline-toggle";
    toggle.textContent = "Timeline";
    toggle.setAttribute("aria-expanded", "false");
    toggle.addEventListener("click", () => {
      bar.hidden = !bar.hidden;
      toggle.setAttribute("aria-expanded", String(!bar.hidden));
    });
    button = document.createElement("button");
    slider = document.createElement("input"); slider.type = "range"; slider.min = "0"; slider.max = "1"; slider.step = String(1 / snapshot.animation.frames);
    const updateButton = () => { if (button) button.textContent = playing ? "Pause" : "Play"; };
    button.addEventListener("click", () => { playing = !playing; updateButton(); });
    slider.addEventListener("input", () => { playing = false; time = Number(slider?.value); updateButton(); });
    updateButton(); bar.append(button, slider); container.append(toggle, bar);
  }
  tree.update(time); await tree.loaded;
  scene.updateMatrixWorld(true);
  const bounds = new THREE.Box3().setFromObject(scene);
  const center = bounds.getCenter(new THREE.Vector3());
  const distance = (bounds.getSize(new THREE.Vector3()).length() / 2) / Math.tan((camera.fov * Math.PI) / 360) * 1.2;
  camera.near = distance / 100; camera.far = distance * 100; camera.updateProjectionMatrix(); controls.target.copy(center); controls.update();
  if (preservedView) {
    camera.position.copy(preservedView.camera);
    controls.target.copy(preservedView.target);
    controls.update();
  } else {
    camera.position.copy(center).addScaledVector(new THREE.Vector3(1, -1, 0.8).normalize(), distance);
    controls.target.copy(center);
    controls.update();
  }
  const resize = () => { renderer.setSize(container.clientWidth, container.clientHeight); camera.aspect = container.clientWidth / container.clientHeight; camera.updateProjectionMatrix(); };
  const observer = new ResizeObserver(resize); observer.observe(container); resize();
  let previous: number | undefined;
  renderer.setAnimationLoop((timestamp) => { const elapsed = previous === undefined ? 0 : (timestamp - previous) / 1000; previous = timestamp; if (playing) { time = (time + elapsed / (snapshot.animation.frames / snapshot.animation.fps)) % 1; if (slider) slider.value = String(time); } tree.update(time); renderer.render(scene, camera); });
  return {
    view: () => ({ camera: camera.position.clone(), target: controls.target.clone() }),
    dispose: () => { renderer.setAnimationLoop(null); observer.disconnect(); controls.dispose(); renderer.dispose(); container.replaceChildren(); },
  };
}
