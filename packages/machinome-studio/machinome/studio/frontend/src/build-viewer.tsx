// Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
// SPDX-License-Identifier: AGPL-3.0-or-later
import { useEffect, useRef, useState } from "react";
import {
  Box3,
  Box3Helper,
  BufferGeometry,
  Color,
  DirectionalLight,
  DoubleSide,
  Float32BufferAttribute,
  Group,
  HemisphereLight,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  MeshStandardMaterial,
  PerspectiveCamera,
  PlaneGeometry,
  Scene,
  SRGBColorSpace,
  Vector3,
  WebGLRenderer,
} from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
import { BUILD_VOLUME } from "./build-data";

function bedGrid(): LineSegments {
  const [width, depth] = BUILD_VOLUME;
  const points: number[] = [];
  for (let x = -width / 2; x <= width / 2; x += 10) points.push(x, -depth / 2, .15, x, depth / 2, .15);
  for (let y = -depth / 2; y <= depth / 2; y += 10) points.push(-width / 2, y, .15, width / 2, y, .15);
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new Float32BufferAttribute(points, 3));
  return new LineSegments(geometry, new LineBasicMaterial({ color: 0x39414b, transparent: true, opacity: .72 }));
}

export function BuildPieceViewer({ modelUrl, pieceName }: { modelUrl: string; pieceName: string }) {
  const host = useRef<HTMLDivElement>(null);
  const reset = useRef<(() => void) | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const target = host.current;
    if (!target) return;
    setError(null);
    let disposed = false;
    const scene = new Scene();
    scene.background = new Color(0x101318);
    const camera = new PerspectiveCamera(38, 1, 1, 4000);
    camera.up.set(0, 0, 1);
    const renderer = new WebGLRenderer({ antialias: true });
    renderer.outputColorSpace = SRGBColorSpace;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.domElement.className = "build-piece-canvas";
    renderer.domElement.setAttribute("role", "img");
    renderer.domElement.setAttribute("aria-label", `${pieceName}, one representative piece on a 250 by 210 millimetre build plate`);
    target.append(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = false;
    controls.screenSpacePanning = true;
    const sceneResources = new Group();
    scene.add(sceneResources);

    const bedMaterial = new MeshStandardMaterial({ color: 0x20262e, roughness: .88, metalness: .05, side: DoubleSide });
    const bed = new Mesh(new PlaneGeometry(BUILD_VOLUME[0], BUILD_VOLUME[1]), bedMaterial);
    sceneResources.add(bed, bedGrid());
    const volume = new Box3(
      new Vector3(-BUILD_VOLUME[0] / 2, -BUILD_VOLUME[1] / 2, 0),
      new Vector3(BUILD_VOLUME[0] / 2, BUILD_VOLUME[1] / 2, BUILD_VOLUME[2]),
    );
    const volumeHelper = new Box3Helper(volume, 0x4f5865);
    sceneResources.add(volumeHelper);
    scene.add(new HemisphereLight(0xdce9ff, 0x24201a, 2.4));
    const key = new DirectionalLight(0xffddb0, 3.2);
    key.position.set(-180, -220, 360);
    scene.add(key);

    const render = () => renderer.render(scene, camera);
    controls.addEventListener("change", render);
    const observer = new ResizeObserver(() => {
      const width = target.clientWidth;
      const height = target.clientHeight;
      if (!width || !height) return;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
      render();
    });
    observer.observe(target);

    let pieceGeometry: BufferGeometry | null = null;
    let pieceMaterial: MeshStandardMaterial | null = null;
    void new STLLoader().loadAsync(modelUrl).then((geometry) => {
      if (disposed) { geometry.dispose(); return; }
      pieceGeometry = geometry;
      geometry.computeVertexNormals();
      geometry.computeBoundingBox();
      const bounds = geometry.boundingBox;
      if (!bounds || !Number.isFinite(bounds.min.x) || bounds.isEmpty()) throw new Error("the representative STL has no renderable geometry");
      const centre = bounds.getCenter(new Vector3());
      geometry.translate(-centre.x, -centre.y, -bounds.min.z);
      geometry.computeBoundingBox();
      pieceMaterial = new MeshStandardMaterial({ color: 0xe0a350, roughness: .58, metalness: .08 });
      const mesh = new Mesh(pieceGeometry, pieceMaterial);
      sceneResources.add(mesh);

      const framed = volume.clone().union(geometry.boundingBox!);
      const centreOfView = framed.getCenter(new Vector3());
      const radius = Math.max(framed.getSize(new Vector3()).length() / 2, 1);
      const direction = new Vector3(1, -1.18, .9).normalize();
      const distance = radius / Math.sin((camera.fov * Math.PI / 180) / 2) * 1.15;
      const home = centreOfView.clone().add(direction.multiplyScalar(distance));
      const resetView = () => {
        camera.position.copy(home);
        camera.near = Math.max(distance / 1000, .1);
        camera.far = Math.max(distance * 8, 4000);
        camera.updateProjectionMatrix();
        controls.target.copy(centreOfView);
        controls.update();
        render();
      };
      reset.current = resetView;
      resetView();
      setError(null);
    }).catch((reason: unknown) => {
      if (!disposed) {
        pieceGeometry?.dispose();
        pieceGeometry = null;
        pieceMaterial?.dispose();
        pieceMaterial = null;
        setError(reason instanceof Error ? reason.message : String(reason));
      }
    });

    return () => {
      disposed = true;
      reset.current = null;
      observer.disconnect();
      controls.removeEventListener("change", render);
      controls.dispose();
      pieceGeometry?.dispose();
      pieceMaterial?.dispose();
      bed.geometry.dispose();
      bedMaterial.dispose();
      const grid = sceneResources.children.find((child) => child instanceof LineSegments) as LineSegments | undefined;
      grid?.geometry.dispose();
      (grid?.material as LineBasicMaterial | undefined)?.dispose();
      volumeHelper.geometry.dispose();
      (volumeHelper.material as LineBasicMaterial).dispose();
      renderer.dispose();
      renderer.forceContextLoss();
      renderer.domElement.remove();
    };
  }, [modelUrl, pieceName]);

  return <div className="build-piece-viewer">
    <div className="build-piece-host" ref={host} />
    <button type="button" onClick={() => reset.current?.()}>Reset view</button>
    <span className="build-gesture">drag to orbit · scroll to zoom</span>
    {error ? <p className="build-viewer-error" role="status">Could not display this STL: {error}</p> : null}
  </div>;
}
