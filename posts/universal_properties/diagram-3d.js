// Interactive 3D commutative diagrams for "Universal properties in category
// theory simply explained", built with three.js. LaTeX labels are real
// KaTeX-rendered DOM elements positioned in 3D space via CSS2DRenderer (not
// baked into a flat texture), so they stay crisp at any zoom level.
//
// Usage in the page: a single
//   <script type="module" src="./diagram-3d.js"></script>
// is enough. Every element with a `data-diagram="<name>"` attribute is
// mounted automatically once the DOM is ready; optional per-instance
// options are read from a `data-opts='{"...json..."}'` attribute.

// Imported by fully-qualified URL everywhere (including inside the two
// vendored addon files below) rather than via the bare "three" specifier:
// an import map would have to be declared before *every* module script on
// the page — including Quarto's own quarto.js/tabsets.js in <head> — which
// isn't something a post can control, so bare specifiers are unreliable here.
import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";
import { OrbitControls } from "./vendor/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "./vendor/CSS2DRenderer.js";
import { GLTFLoader } from "./vendor/loaders/GLTFLoader.js";
import { DRACOLoader } from "./vendor/loaders/DRACOLoader.js";
import katex from "https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.mjs";

// Shared across every model load: the Draco decoder (WASM) only needs to
// spin up once. Decoder binaries aren't part of the JS module graph, so
// pointing this at a CDN is just a runtime fetch, not an import-resolution
// concern like the bare "three" specifier was.
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath(
  "https://unpkg.com/three@0.160.0/examples/jsm/libs/draco/gltf/",
);

// ---------------------------------------------------------------------
// Low-level helpers
// ---------------------------------------------------------------------

function makeLabelObject(tex, { className = "diagram-label" } = {}) {
  const div = document.createElement("div");
  div.className = className;
  katex.render(tex, div, { throwOnError: false });
  return new CSS2DObject(div);
}

function addLabel(scene, tex, pos, opts = {}) {
  const obj = makeLabelObject(tex, opts);
  obj.position.set(pos[0], pos[1], pos[2]);
  scene.add(obj);
  return obj;
}

function addNode(scene, pos, tex, opts = {}) {
  const {
    color = 0x475569,
    radius = 0.11,
    offset = [0, 0.4, 0],
    className = "diagram-label diagram-label-node",
  } = opts;
  const geo = new THREE.SphereGeometry(radius, 20, 20);
  const mat = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.45,
    metalness: 0.05,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(pos[0], pos[1], pos[2]);
  scene.add(mesh);

  const label = makeLabelObject(tex, { className });
  label.position.set(
    pos[0] + offset[0],
    pos[1] + offset[1],
    pos[2] + offset[2],
  );
  scene.add(label);

  return { mesh, label };
}

function addArrow(scene, from, to, opts = {}) {
  const {
    color = 0x2563eb,
    radius = 0.028,
    headLength = 0.22,
    headRadius = 0.075,
    shorten = 0.16,
    label,
    labelOffset = [0, 0, 0],
  } = opts;

  const start = new THREE.Vector3(...from);
  const end = new THREE.Vector3(...to);
  const dir = new THREE.Vector3().subVectors(end, start);
  dir.normalize();

  const s = start.clone().addScaledVector(dir, shorten);
  const e = end.clone().addScaledVector(dir, -shorten);
  const len = s.distanceTo(e);
  const shaftLen = Math.max(len - headLength, 0.02);

  const group = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.5,
    metalness: 0.05,
  });

  const shaftGeo = new THREE.CylinderGeometry(radius, radius, shaftLen, 10);
  shaftGeo.translate(0, shaftLen / 2, 0);
  group.add(new THREE.Mesh(shaftGeo, mat));

  const headGeo = new THREE.ConeGeometry(headRadius, headLength, 16);
  headGeo.translate(0, shaftLen + headLength / 2, 0);
  group.add(new THREE.Mesh(headGeo, mat));

  const up = new THREE.Vector3(0, 1, 0);
  group.quaternion.copy(new THREE.Quaternion().setFromUnitVectors(up, dir));
  group.position.copy(s);
  scene.add(group);

  const midpoint = s.clone().addScaledVector(dir, len / 2);
  let labelObj = null;
  if (label) {
    labelObj = makeLabelObject(label);
    labelObj.position.set(
      midpoint.x + labelOffset[0],
      midpoint.y + labelOffset[1],
      midpoint.z + labelOffset[2],
    );
    scene.add(labelObj);
  }

  return {
    group,
    midpoint: [midpoint.x, midpoint.y, midpoint.z],
    label: labelObj,
  };
}

function addCurvedArrow(scene, p0, p1, p2, opts = {}) {
  const {
    color = 0x7c3aed,
    radius = 0.032,
    headLength = 0.28,
    headRadius = 0.1,
    segments = 32,
  } = opts;

  const curve = new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(...p0),
    new THREE.Vector3(...p1),
    new THREE.Vector3(...p2),
  );
  const mat = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.5,
    metalness: 0.05,
  });

  // Tube follows the full curve; the solid cone head placed at t=1 below
  // covers the last stretch, so there is no visible seam.
  const tubeGeo = new THREE.TubeGeometry(curve, segments, radius, 8, false);
  const tube = new THREE.Mesh(tubeGeo, mat);
  scene.add(tube);

  const end = curve.getPoint(1);
  const tangent = curve.getTangent(1).normalize();
  const headGeo = new THREE.ConeGeometry(headRadius, headLength, 16);
  headGeo.translate(0, headLength / 2, 0);
  const head = new THREE.Mesh(headGeo, mat);
  const up = new THREE.Vector3(0, 1, 0);
  head.quaternion.copy(new THREE.Quaternion().setFromUnitVectors(up, tangent));
  head.position.copy(end);
  scene.add(head);

  const mid = curve.getPoint(0.5);
  return { midpoint: [mid.x, mid.y, mid.z] };
}

// Functor-style arrow: two parallel curved rails converging on a single
// arrowhead, to visually set it apart from the plain single-shaft morphism
// arrows drawn by addArrow/addCurvedArrow.
function addDoubleCurvedArrow(scene, p0, p1, p2, opts = {}) {
  const {
    color = 0x7c3aed,
    radius = 0.022,
    gap = 0.2,
    headLength = 0.42,
    headRadius = 0.24,
    segments = 32,
  } = opts;

  const P0 = new THREE.Vector3(...p0);
  const P1 = new THREE.Vector3(...p1);
  const P2 = new THREE.Vector3(...p2);
  const mat = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.5,
    metalness: 0.05,
  });

  // Offset the two rails within the XY (screen) plane rather than along
  // world "up" crossed with the chord: these diagrams are viewed nearly
  // head-on down the Z axis, so a Z-ward offset foreshortens to nothing —
  // crossing with the Z axis instead keeps the separation visible on screen.
  const chord = new THREE.Vector3().subVectors(P2, P0).normalize();
  const viewAxis = new THREE.Vector3(0, 0, 1);
  const perp = new THREE.Vector3().crossVectors(chord, viewAxis);
  if (perp.lengthSq() < 1e-6) perp.set(0, 1, 0);
  perp.normalize().multiplyScalar(gap);

  for (const sign of [1, -1]) {
    const offset = perp.clone().multiplyScalar(sign);
    const railCurve = new THREE.QuadraticBezierCurve3(
      P0.clone().add(offset),
      P1.clone().add(offset),
      P2.clone().add(offset),
    );
    const tubeGeo = new THREE.TubeGeometry(
      railCurve,
      segments,
      radius,
      8,
      false,
    );
    scene.add(new THREE.Mesh(tubeGeo, mat));
  }

  // A single head, centered on the undisplaced curve, ties the two rails
  // together at the tip.
  const centerCurve = new THREE.QuadraticBezierCurve3(P0, P1, P2);
  const end = centerCurve.getPoint(1);
  const tangent = centerCurve.getTangent(1).normalize();
  const headGeo = new THREE.ConeGeometry(headRadius, headLength, 16);
  headGeo.translate(0, headLength / 2, 0);
  const head = new THREE.Mesh(headGeo, mat);
  head.quaternion.copy(
    new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 1, 0),
      tangent,
    ),
  );
  head.position.copy(end);
  scene.add(head);

  const mid = centerCurve.getPoint(0.5);
  return { midpoint: [mid.x, mid.y, mid.z] };
}

function addFace(scene, pts, opts = {}) {
  const { color = 0x16a34a, opacity = 0.2 } = opts;
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(pts.flat());
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geo.setIndex([0, 1, 2]);
  geo.computeVertexNormals();
  const mat = new THREE.MeshBasicMaterial({
    color,
    transparent: true,
    opacity,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
  const mesh = new THREE.Mesh(geo, mat);
  scene.add(mesh);
  return mesh;
}

function addPaper(scene, { size = [7, 6], center = [0, 0, 0] } = {}) {
  const geo = new THREE.PlaneGeometry(size[0], size[1]);
  const mat = new THREE.MeshBasicMaterial({
    color: 0x94a3b8,
    opacity: 0.14,
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.set(center[0], center[1] - 0.02, center[2]);
  scene.add(mesh);
  return mesh;
}

function addSlider(
  container,
  { label = "", min = 0, max = 1, step = 0.01, value = 0, onInput } = {},
) {
  const wrap = document.createElement("div");
  wrap.className = "diagram3d-controls";
  const span = document.createElement("span");
  span.textContent = label;
  const input = document.createElement("input");
  input.type = "range";
  input.min = String(min);
  input.max = String(max);
  input.step = String(step);
  input.value = String(value);
  input.addEventListener("input", () => onInput(parseFloat(input.value)));
  wrap.appendChild(span);
  wrap.appendChild(input);
  container.appendChild(wrap);
  return input;
}

// Loads a GLB/GLTF model, re-centers and rescales it to `targetSize` based
// on its own bounding box (so it's framed consistently regardless of the
// original export scale/origin), then places it at `position`/`rotation`
// inside a wrapper group. `onLoad(wrapper, model)` fires once it's in the
// scene, e.g. so a standalone viewer can reframe its camera around it.
function loadModel(scene, url, opts = {}) {
  const {
    position = [0, 0, 0],
    rotation = [0, 0, 0],
    targetSize = 2.4,
    onLoad,
  } = opts;

  const loader = new GLTFLoader();
  loader.setDRACOLoader(dracoLoader);
  loader.load(
    url,
    (gltf) => {
      const model = gltf.scene;
      const box = new THREE.Box3().setFromObject(model);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      model.position.sub(center);

      const maxDim = Math.max(size.x, size.y, size.z) || 1;
      model.scale.setScalar(targetSize / maxDim);

      const wrapper = new THREE.Group();
      wrapper.add(model);
      wrapper.position.set(...position);
      wrapper.rotation.set(...rotation);
      scene.add(wrapper);

      if (onLoad) onLoad(wrapper, model);
    },
    undefined,
    (err) => {
      console.error("diagram-3d: failed to load " + url, err);
    },
  );
}

// ---------------------------------------------------------------------
// Scene bootstrap: WebGL renderer + CSS2D label renderer + orbit controls,
// with resize handling and an intersection-observer pause so off-screen
// diagrams don't keep rendering.
// ---------------------------------------------------------------------

function initScene(container, opts = {}) {
  const {
    cameraPos = [3, 2, 7],
    lookAt = [0, 0, 0],
    fov = 45,
    enableRotate = true,
    upVector = [0, 1, 0],
  } = opts;
  container.classList.add("diagram3d");

  const width = container.clientWidth || 600;
  const height = container.clientHeight || 420;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(fov, width / height, 0.1, 200);
  // Must be set before OrbitControls is constructed below — it captures
  // camera.up once at that point to align its internal orbit axis, so
  // changing it afterwards (e.g. for a straight-down top view) wouldn't
  // take effect.
  camera.up.set(...upVector);
  camera.position.set(...cameraPos);
  camera.lookAt(...lookAt);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(width, height);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  const labelRenderer = new CSS2DRenderer();
  labelRenderer.setSize(width, height);
  Object.assign(labelRenderer.domElement.style, {
    position: "absolute",
    top: "0",
    left: "0",
    pointerEvents: "none",
  });
  container.appendChild(labelRenderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  controls.enableRotate = enableRotate;
  controls.minDistance = 2;
  controls.maxDistance = 40;
  controls.target.set(...lookAt);
  controls.update();

  scene.add(new THREE.AmbientLight(0xffffff, 1.0));
  const dl = new THREE.DirectionalLight(0xffffff, 0.55);
  dl.position.set(4, 6, 5);
  scene.add(dl);

  const hint = document.createElement("div");
  hint.className = "diagram3d-hint";
  hint.textContent = "↻ ziehen · scrollen zum zoomen";
  container.appendChild(hint);

  function resize() {
    const w = container.clientWidth;
    const h = container.clientHeight;
    if (!w || !h) return;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    labelRenderer.setSize(w, h);
  }
  new ResizeObserver(resize).observe(container);

  let running = true;
  new IntersectionObserver(
    (entries) => {
      running = entries[0].isIntersecting;
    },
    { threshold: 0.01 },
  ).observe(container);

  function animate() {
    requestAnimationFrame(animate);
    if (!running) return;
    controls.update();
    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
  }
  animate();

  return { scene, camera, renderer, labelRenderer, controls };
}

// ---------------------------------------------------------------------
// The six diagrams
// ---------------------------------------------------------------------

// Abbildung 1 — just a GLB model on a turntable, orbit-rotatable.
function buildNotebook(container, opts = {}) {
  const { url = "./assets/notebook.glb", targetSize = 2.4 } = opts;
  // Straight top-down view: camera sits directly above on the Y axis, so
  // "up" can't be the default (0,1,0) — that's parallel to the view
  // direction and leaves the on-screen roll undefined. Using -Z as "up"
  // instead (a common top-down/map convention) keeps the orientation
  // well-defined and gives OrbitControls a sane axis to orbit around.
  const { scene, camera, controls } = initScene(container, {
    cameraPos: [0, targetSize * 2, 0],
    lookAt: [0, 0, 0],
    fov: 40,
    upVector: [0, 0, -1],
  });

  const fill = new THREE.DirectionalLight(0xffffff, 0.35);
  fill.position.set(-4, 2, -3);
  scene.add(fill);

  loadModel(scene, url, { targetSize });
}

// fig:diagramm — the index category J together with a functor D into the
// target category, which is now just the Abbildung-1 notebook model rather
// than a redrawn triangle.
function buildFunctor(container, opts = {}) {
  const { url = "./assets/notebook.glb" } = opts;
  // Closer camera + wider FOV than a plain "fit the wide scene" framing
  // would need: at long camera distance, perspective distortion becomes
  // negligible (near-orthographic), so a genuinely 3D-tilted flat model
  // reads as a plain in-plane rotation — the corners stay ~90° and the
  // sides stay parallel. Halving the distance while widening the FOV to
  // compensate keeps the same framing but makes the tilt's foreshortening
  // actually visible.
  const { scene } = initScene(container, {
    cameraPos: [0.4, 1.3, 8],
    lookAt: [0.7, 0.3, 0],
    fov: 56,
  });

  const fill = new THREE.DirectionalLight(0xffffff, 0.35);
  fill.position.set(2, 3, -3);
  scene.add(fill);

  const J1 = [-6, 1.6, 0],
    J2 = [-6, -1.4, 0],
    J3 = [-3, 0.1, 0];
  addNode(scene, J1, "\\underline{1}", { offset: [-0.1, 0.58, 0] });
  addNode(scene, J2, "\\underline{2}", { offset: [-0.1, -0.58, 0] });
  addNode(scene, J3, "\\underline{3}", { offset: [0.55, 0, 0] });
  addArrow(scene, J1, J2, {});
  addArrow(scene, J1, J3, {});
  addArrow(scene, J2, J3, {});

  const { midpoint } = addDoubleCurvedArrow(
    scene,
    [-2.2, 0.1, 0],
    [0.7, 1.6, 1.2],
    [3.6, 0.1, 0],
  );
  addLabel(scene, "D", [midpoint[0], midpoint[1] + 0.55, midpoint[2]], {
    className: "diagram-label diagram-label-node",
  });

  loadModel(scene, url, {
    position: [6.0, 0.1, 0],
    rotation: [Math.PI / 2, 0, 0],
    targetSize: 3.4,
  });
}

// Universal cone: a "sheet of paper" carrying the base diagram, with N
// floating above it and a slider to fill in the commuting triangles with
// tip N.
function buildCone1(container) {
  const { scene } = initScene(container, {
    cameraPos: [0.6, 3.4, 8.6],
    lookAt: [0, 1.2, 0],
  });
  const A = [-1.2, 0, -2],
    B = [-1.1, 0, 1.4],
    C = [1.8, 0, 1.4];
  const N = [0, 3.4, 0.1];
  const url = "./assets/notebook.glb";

  // addPaper(scene, { size: [7, 6] });
  // addNode(scene, A, "\\mathbb{R}^3", { offset: [-0.5, 0.05, 0.35] });
  // addNode(scene, B, "\\mathbb{R}^3", { offset: [-0.5, 0.05, -0.35] });
  // addNode(scene, C, "\\mathbb{R}^2", { offset: [0.5, 0.05, -0.35] });
  addNode(scene, N, "N", { offset: [0, 0.58, 0] });

  // addArrow(scene, A, C, {});
  // addArrow(scene, A, B, {});
  // addArrow(scene, B, C, {});
  // addFace(scene, [A, B, C], { color: 0x16a34a, opacity: 0.16 });

  addArrow(scene, N, A, { color: 0xf59e0b });
  addArrow(scene, N, B, { color: 0xf59e0b });
  addArrow(scene, N, C, { color: 0xf59e0b });

  const fNAB = addFace(scene, [N, A, B], { color: 0xf59e0b, opacity: 0 });
  const fNAC = addFace(scene, [N, A, C], { color: 0xf59e0b, opacity: 0 });
  const fNBC = addFace(scene, [N, B, C], { color: 0xf59e0b, opacity: 0 });
  loadModel(scene, url, {
    position: [0, 0, -1],
    rotation: [0, 0, 0],
    targetSize: 9.4,
  });

  addSlider(container, {
    label: "kommutative Dreiecke einzeichnen",
    value: 0,
    onInput: (v) => {
      fNAB.material.opacity = v * 0.35;
      fNAC.material.opacity = v * 0.35;
      fNBC.material.opacity = v * 0.35;
    },
  });
}

// Two cones N1, N2 over the same base diagram, with a comparison arrow
// N1 -> N2. `initialFill` lets the same builder serve both the "unfilled"
// and "filled" callouts from the post; either slider can still be dragged.
function buildCone2(container, opts = {}) {
  const initialFill = opts.initialFill ?? 0;
  const { scene } = initScene(container, {
    cameraPos: [0.8, 4.6, 11.5],
    lookAt: [0, 2.1, 0],
  });
  const { url = "./assets/notebook.glb" } = opts;
  const A = [-1.2, 0, -2],
    B = [-1.1, 0, 1.4],
    C = [1.8, 0, 1.4];
  const N2 = [0, 2.6, 0.1];
  const N1 = [0, 5.2, 0.25];

  // addPaper(scene, { size: [7, 6] });
  // addNode(scene, A, "\\mathbb{R}^3", { offset: [-0.5, 0.05, 0.35] });
  // addNode(scene, B, "\\mathbb{R}^3", { offset: [-0.5, 0.05, -0.35] });
  // addNode(scene, C, "\\mathbb{R}^2", { offset: [0.5, 0.05, -0.35] });
  addNode(scene, N2, "N_2", { offset: [0.42, 0.1, 0] });
  addNode(scene, N1, "N_1", { offset: [0.42, 0.1, 0] });

  addArrow(scene, A, C, {});
  addArrow(scene, A, B, {});
  addArrow(scene, B, C, {});
  addFace(scene, [A, B, C], { color: 0x16a34a, opacity: 0.16 });

  addArrow(scene, N2, A, { color: 0xf59e0b });
  addArrow(scene, N2, B, { color: 0xf59e0b });
  addArrow(scene, N2, C, { color: 0xf59e0b });
  addArrow(scene, N1, A, { color: 0xea580c });
  addArrow(scene, N1, B, { color: 0xea580c });
  addArrow(scene, N1, C, { color: 0xea580c });
  addArrow(scene, N1, N2, { color: 0xdc2626, radius: 0.034 });

  const fN1AB = addFace(scene, [N1, A, B], { color: 0xdc2626, opacity: 0 });
  const fN1AC = addFace(scene, [N1, A, C], { color: 0xdc2626, opacity: 0 });
  const fN1BC = addFace(scene, [N1, B, C], { color: 0xdc2626, opacity: 0 });
  const fN2AB = addFace(scene, [N2, A, B], { color: 0xf59e0b, opacity: 0 });
  const fN2AC = addFace(scene, [N2, A, C], { color: 0xf59e0b, opacity: 0 });
  const fN2BC = addFace(scene, [N2, B, C], { color: 0xf59e0b, opacity: 0 });

  loadModel(scene, url, {
    position: [0, 0, -1],
    rotation: [0, 0, 0],
    targetSize: 9.4,
  });

  addSlider(container, {
    label: "kommutative Dreiecke einzeichnen",
    value: initialFill,
    onInput: (v) => {
      fN1AB.material.opacity = v * 0.35;
      fN1AC.material.opacity = v * 0.35;
      fN1BC.material.opacity = v * 0.35;
      fN2AB.material.opacity = v * 0.35;
      fN2AC.material.opacity = v * 0.35;
      fN2BC.material.opacity = v * 0.35;
    },
  });
}

// The colimit dual of buildCone2 (Abbildung 4): same model, same A/B/C
// anchor points on it (already calibrated to sit on the drawn triangle),
// but N1 and N2 now hang *below* the model instead of floating above it,
// and every arrow that used to point from N1/N2 onto the model now points
// the other way — from the model out to N1/N2. The N2->N1 comparison arrow
// is flipped too (instead of Abbildung 4's N1->N2): dualizing a limit into
// a colimit reverses every arrow, so the "more universal" cocone (N2, the
// one closer to the model) now maps *out* to the other cocone N1, rather
// than N1 mapping into N2.
function buildCocone(container, opts = {}) {
  const initialFill = opts.initialFill ?? 0;
  const { url = "./assets/notebook_dual.glb" } = opts;
  const { scene } = initScene(container, {
    cameraPos: [0.8, 4.6, 11.5],
    lookAt: [0, -2.1, 0],
  });
  const A = [-1.2, 0, -2],
    B = [-1.1, 0, 1.4],
    C = [1.8, 0, 1.4];
  const N2 = [0, -2.6, 0.1];
  const N1 = [0, -5.2, 0.25];

  addNode(scene, N2, "N_2", { offset: [0.42, 0.1, 0] });
  addNode(scene, N1, "N_1", { offset: [0.42, 0.1, 0] });

  addArrow(scene, A, N2, { color: 0xf59e0b });
  addArrow(scene, B, N2, { color: 0xf59e0b });
  addArrow(scene, C, N2, { color: 0xf59e0b });
  addArrow(scene, A, N1, { color: 0xea580c });
  addArrow(scene, B, N1, { color: 0xea580c });
  addArrow(scene, C, N1, { color: 0xea580c });
  addArrow(scene, N2, N1, { color: 0xdc2626, radius: 0.034 });

  const fN1AB = addFace(scene, [N1, A, B], { color: 0xdc2626, opacity: 0 });
  const fN1AC = addFace(scene, [N1, A, C], { color: 0xdc2626, opacity: 0 });
  const fN1BC = addFace(scene, [N1, B, C], { color: 0xdc2626, opacity: 0 });
  const fN2AB = addFace(scene, [N2, A, B], { color: 0xf59e0b, opacity: 0 });
  const fN2AC = addFace(scene, [N2, A, C], { color: 0xf59e0b, opacity: 0 });
  const fN2BC = addFace(scene, [N2, B, C], { color: 0xf59e0b, opacity: 0 });

  loadModel(scene, url, {
    position: [0, 0, -1],
    rotation: [0, 0, 0],
    targetSize: 9.4,
  });

  addSlider(container, {
    label: "kommutative Dreiecke einzeichnen",
    value: initialFill,
    onInput: (v) => {
      fN1AB.material.opacity = v * 0.35;
      fN1AC.material.opacity = v * 0.35;
      fN1BC.material.opacity = v * 0.35;
      fN2AB.material.opacity = v * 0.35;
      fN2AC.material.opacity = v * 0.35;
      fN2BC.material.opacity = v * 0.35;
    },
  });
}

// The tensor-product sketch (V x W -> Z_phi, V x W -> Z_psi), tilted -pi/4
// about X, with a universal cone (N1, N2) drawn above it — same structure
// as buildCone2, just anchored to this model's own drawn nodes instead of
// the matrix triangle. The anchor points are picked out in the model's
// local (pre-rotation) frame from where the sketch places "V x W", "Z_phi"
// and "Z_psi" on the page, then rotated by the same angle as the model
// itself so they stay glued to the sketch once it's tilted.
function buildTensorCone(container, opts = {}) {
  const initialFill = opts.initialFill ?? 0;
  const { url = "./assets/notebook_tensor.glb" } = opts;
  const { scene } = initScene(container, {
    cameraPos: [0.8, 6.4, 13.5],
    lookAt: [0, 2.6, 0],
  });

  const rotX = 0;
  const cosT = Math.cos(rotX);
  const sinT = Math.sin(rotX);
  function rotateAroundX([x, y, z]) {
    return [x, y * cosT - z * sinT, y * sinT + z * cosT];
  }
  const VxW = rotateAroundX([0, 0, -2.55]);
  const Zphi = rotateAroundX([-2.36, 0, 2.63]);
  const Zpsi = rotateAroundX([2.49, 0, 2.63]);

  const N2 = [0, 4.0, 0.1];
  const N1 = [0, 6.6, 0.25];

  // N2 stands in for the (hypothesized) tensor product itself, N1 for an
  // arbitrary other cone over the same diagram.
  addNode(scene, N2, "V \\otimes W", { offset: [0.85, 0.1, 0] });
  addNode(scene, N1, "N", { offset: [0.32, 0.1, 0] });

  addArrow(scene, N2, VxW, { color: 0xf59e0b });
  addArrow(scene, N2, Zphi, { color: 0xf59e0b });
  addArrow(scene, N2, Zpsi, { color: 0xf59e0b });
  addArrow(scene, N1, VxW, { color: 0xea580c });
  addArrow(scene, N1, Zphi, { color: 0xea580c });
  addArrow(scene, N1, Zpsi, { color: 0xea580c });
  addArrow(scene, N1, N2, { color: 0xdc2626, radius: 0.034 });

  const fN1a = addFace(scene, [N1, VxW, Zphi], { color: 0xdc2626, opacity: 0 });
  const fN1b = addFace(scene, [N1, VxW, Zpsi], { color: 0xdc2626, opacity: 0 });
  const fN2a = addFace(scene, [N2, VxW, Zphi], { color: 0xf59e0b, opacity: 0 });
  const fN2b = addFace(scene, [N2, VxW, Zpsi], { color: 0xf59e0b, opacity: 0 });

  // Many more faces between Zphi and Zpsi, each sharing an edge with the
  // next, to suggest that there are infinitely many commuting triangles
  // between the two cones (one for every bilinear map between phi and psi),
  // not just the two at the endpoints.
  const inbetween = 7;
  const endpoint = (i) => [
    Zphi[0] + ((Zpsi[0] - Zphi[0]) * (i + 1)) / (inbetween + 1),
    Zphi[1] + ((Zpsi[1] - Zphi[1]) * (i + 1)) / (inbetween + 1),
    Zphi[2] + ((Zpsi[2] - Zphi[2]) * (i + 1)) / (inbetween + 1),
  ];
  const additionalFacesN1 = [...Array(inbetween)].map((_, i) =>
    addFace(scene, [N1, VxW, endpoint(i)], { color: 0xdc2626, opacity: 0 }),
  );
  const additionalFacesN2 = [...Array(inbetween)].map((_, i) =>
    addFace(scene, [N2, VxW, endpoint(i)], { color: 0xf59e0b, opacity: 0 }),
  );

  loadModel(scene, url, {
    position: [0, 0, 0],
    rotation: [rotX, 0, 0],
    targetSize: 9.4,
  });

  addSlider(container, {
    label: "kommutative Dreiecke einzeichnen",
    value: initialFill,
    onInput: (v) => {
      fN1a.material.opacity = v * 0.35;
      fN1b.material.opacity = v * 0.35;
      fN2a.material.opacity = v * 0.35;
      fN2b.material.opacity = v * 0.35;
      additionalFacesN1.forEach((face) => {
        face.material.opacity = v * 0.35;
      });
      additionalFacesN2.forEach((face) => {
        face.material.opacity = v * 0.35;
      });
    },
  });
}

// The plain X -> Y -> Z commuting triangle used to translate diagrams into
// logic: h f = g.
function buildTriangleXYZ(container) {
  const { scene } = initScene(container, {
    cameraPos: [0.4, 0.6, 6.2],
    lookAt: [0, 0.1, 0],
  });
  const X = [-2, 1.6, 0],
    Y = [-2, -1.4, 0],
    Z = [2, -1.4, 0];

  addNode(scene, X, "X", { offset: [-0.1, 0.58, 0] });
  addNode(scene, Y, "Y", { offset: [-0.1, -0.58, 0] });
  addNode(scene, Z, "Z", { offset: [0.1, -0.58, 0] });

  addArrow(scene, X, Y, { label: "f", labelOffset: [-0.42, 0, 0] });
  addArrow(scene, X, Z, { label: "g", labelOffset: [0.4, 0.18, 0] });
  addArrow(scene, Y, Z, { label: "h", labelOffset: [0, -0.58, 0] });

  const face = addFace(scene, [X, Y, Z], { color: 0x16a34a, opacity: 0 });
  addSlider(container, {
    label: "zeige h ∘ f = g",
    value: 0,
    onInput: (v) => {
      face.material.opacity = v * 0.3;
    },
  });
}

// ---------------------------------------------------------------------
// Auto-mount
// ---------------------------------------------------------------------

const registry = {
  notebook: buildNotebook,
  functor: buildFunctor,
  cone1: buildCone1,
  cone2: buildCone2,
  cocone: buildCocone,
  tensorcone: buildTensorCone,
  trianglexyz: buildTriangleXYZ,
};

function mountAll() {
  document.querySelectorAll("[data-diagram]").forEach((el) => {
    if (el.dataset.mounted) return;
    const fn = registry[el.dataset.diagram];
    if (!fn) return;
    el.dataset.mounted = "1";
    let opts = {};
    if (el.dataset.opts) {
      try {
        opts = JSON.parse(el.dataset.opts);
      } catch (e) {
        /* ignore */
      }
    }
    // One diagram failing (e.g. no WebGL in this browser) must not stop the
    // rest of the page's diagrams from mounting.
    try {
      fn(el, opts);
    } catch (err) {
      console.error(
        "diagram-3d: could not mount '" + el.dataset.diagram + "'",
        err,
      );
      el.classList.add("diagram3d-fallback");
      const msg = document.createElement("div");
      msg.className = "diagram3d-fallback-msg";
      msg.textContent =
        "Diese interaktive 3D-Grafik benötigt WebGL, das in diesem Browser gerade nicht verfügbar ist.";
      el.appendChild(msg);
    }
  });
}

if (document.readyState !== "loading") {
  mountAll();
} else {
  document.addEventListener("DOMContentLoaded", mountAll);
}

export {
  buildNotebook,
  buildFunctor,
  buildCone1,
  buildCone2,
  buildCocone,
  buildTensorCone,
  buildTriangleXYZ,
};
