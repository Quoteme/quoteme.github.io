// Interactive 3D diagram for "Limits, Products, and Equalizers", built with
// three.js. Mirrors the turntable-model setup used for Figure 1 in the
// "Universal properties" post (posts/universal_properties/diagram-3d.js),
// trimmed down to just that one diagram type since this post only needs it.
//
// Usage in the page: a single
//   <script type="module" src="./diagram-3d.js"></script>
// is enough. Every element with a `data-diagram="<name>"` attribute is
// mounted automatically once the DOM is ready; optional per-instance
// options are read from a `data-opts='{"...json..."}'` attribute.

// Imported by fully-qualified URL everywhere (including inside the vendored
// addon files below) rather than via the bare "three" specifier: an import
// map would have to be declared before *every* module script on the page —
// including Quarto's own quarto.js/tabsets.js in <head> — which isn't
// something a post can control, so bare specifiers are unreliable here.
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
// Low-level helpers, ported from posts/universal_properties/diagram-3d.js
// (kept to just what the cone diagrams below need).
// ---------------------------------------------------------------------

function makeLabelObject(tex, { className = "diagram-label" } = {}) {
  const div = document.createElement("div");
  div.className = className;
  katex.render(tex, div, { throwOnError: false });
  return new CSS2DObject(div);
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

  return group;
}

// `pts` is always the apex and the two base points, e.g. [N, X, Y] for a
// cone's commuting "triangle" over base objects X, Y. With `curveRadius: 0`
// (the default) that's a flat triangle, same as before. A nonzero
// `curveRadius` bows the p1-p2 edge sideways instead, so the face hugs a
// curved morphism arrow drawn on the page rather than cutting a straight
// line across it — the bow direction is perpendicular to the p1-p2 edge
// *within the XZ "paper" plane* (not the triangle's own plane) since that's
// the plane the hand-drawn curve actually bows in, regardless of how high
// the apex floats above it, and the sign of `curveRadius` picks which of
// the two sides to bow toward.
//
// `curvePoints` controls how many points are sampled along that bow between
// p1 and p2 (not counting p1/p2 themselves) — 1 is a single midpoint (a
// 2-triangle fan, the previous behavior), 2 adds two more, etc., each
// additional point making the fan hug a smoother arc instead of a sharp
// bend. Points are placed via a sine profile (0 at p1 and p2, full
// curveRadius at the arc's midpoint) so they all sit on the same curve
// regardless of how finely it's sampled.
function addFace(scene, pts, opts = {}) {
  const {
    color = 0x16a34a,
    opacity = 0.2,
    curveRadius = 0,
    curvePoints = 1,
  } = opts;
  let vertices = pts;
  let indices = [0, 1, 2];

  if (curveRadius !== 0 && pts.length === 3) {
    const [apex, p1, p2] = pts.map((p) => new THREE.Vector3(...p));
    const base = new THREE.Vector3().subVectors(p2, p1);
    const perp = new THREE.Vector3(-base.z, 0, base.x).normalize();

    const n = Math.max(0, Math.round(curvePoints));
    const arc = [p1];
    for (let i = 1; i <= n; i++) {
      const t = i / (n + 1);
      const bulge = Math.sin(t * Math.PI) * curveRadius;
      arc.push(
        new THREE.Vector3().lerpVectors(p1, p2, t).addScaledVector(perp, bulge),
      );
    }
    arc.push(p2);

    vertices = [apex.toArray(), ...arc.map((v) => v.toArray())];
    indices = [];
    for (let i = 0; i < arc.length - 1; i++) {
      indices.push(0, i + 1, i + 2);
    }
  }

  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(vertices.flat());
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geo.setIndex(indices);
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
// inside a wrapper group.
function loadModel(scene, url, opts = {}) {
  const { position = [0, 0, 0], rotation = [0, 0, 0], targetSize = 2.4 } = opts;

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
    },
    undefined,
    (err) => {
      console.error("diagram-3d: failed to load " + url, err);
    },
  );
}

// Scene bootstrap: WebGL renderer + CSS2D label renderer + orbit controls,
// with resize handling and an intersection-observer pause so off-screen
// diagrams don't keep rendering.
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
  hint.textContent = "↻ drag · scroll to zoom";
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

// Just a GLB model on a turntable, orbit-rotatable — same treatment as
// Figure 1 (buildNotebook) in the "Universal properties" post. Shared by
// every "plain model" diagram on this page; the URL is the only thing
// that changes between them.
function buildTurntable(container, opts = {}) {
  const { url, targetSize = 2.4 } = opts;
  // Straight top-down view: camera sits directly above on the Y axis, so
  // "up" can't be the default (0,1,0) — that's parallel to the view
  // direction and leaves the on-screen roll undefined. Using -Z as "up"
  // instead (a common top-down/map convention) keeps the orientation
  // well-defined and gives OrbitControls a sane axis to orbit around.
  const { scene } = initScene(container, {
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

function buildNotebookEqualizer(container, opts = {}) {
  buildTurntable(container, {
    url: "./assets/notebook_equalizer.glb",
    ...opts,
  });
}

function buildNotebookProduct(container, opts = {}) {
  buildTurntable(container, {
    url: "./assets/notebook_product.glb",
    ...opts,
  });
}

// Universal cone over the equalizer diagram — the same picture as Figure 4
// (buildCone2) of the "Universal properties" post: two cones N1, N2 sitting
// above the base diagram with arrows down to every object in it and a
// comparison arrow N1 -> N2, with a slider that fills in the commuting
// triangles. Here the base diagram is just X and Y (the equalizer's two
// objects, sitting on the notebook_equalizer.glb sketch loaded below), in
// place of buildCone2's A/B/C matrix triangle. X and Y's coordinates are
// picked to land on the "X" and "Y" glyphs of that sketch once it's loaded
// with the same position/targetSize used here.
function buildEqualizerCone(container) {
  // X and Y sit almost directly above one another in x (they're both
  // centered on the page, just at different heights on it — see the
  // comment on the coordinates below), so a camera offset mostly in y/z
  // like buildCone2's would view the N1/N2/X/Y "cone" nearly edge-on and
  // collapse all four arrows into what looks like a single line. A much
  // bigger x offset on the camera is needed to actually see the fan shape.
  const { scene } = initScene(container, {
    cameraPos: [5.4, 5.6, 10.4],
    lookAt: [0, 3.0, 0.6],
    fov: 50,
  });
  const url = "./assets/notebook_equalizer.glb";
  const X = [-0.12, 0, -2.0];
  const Y = [0.02, 0, 3.25];
  const Equalizer = [0.05, 3.3, -1.62];
  const N = [0.2, 6.5, -3];

  addNode(scene, Equalizer, "\\text{Eq}(f,g)", { offset: [0.42, 0.1, 0] });
  addNode(scene, N, "N", { offset: [0.42, 0.1, 0] });

  addArrow(scene, Equalizer, X, { color: 0xf59e0b });
  addArrow(scene, Equalizer, Y, { color: 0xf59e0b });
  addArrow(scene, N, X, { color: 0xea580c });
  addArrow(scene, N, Y, { color: 0xea580c });
  addArrow(scene, N, Equalizer, { color: 0xdc2626, radius: 0.034 });

  // The equalizer's cone condition is two commuting triangles per apex —
  // N -> X -> f -> Y and N -> X -> g -> Y both have to equal N -> Y — so
  // each apex gets two curved faces, one bowed out over each arrow, rather
  // than a single flat triangle cutting straight across both of them.
  // curveRadius sign picks the side: positive bows toward f (left, drawn at
  // negative x), negative toward g (right, drawn at positive x).
  const curveRadius = 2.0;
  const curvePoints = 4;
  const fNf = addFace(scene, [N, X, Y], {
    color: 0xdc2626,
    opacity: 0,
    curveRadius,
    curvePoints,
  });
  const fNg = addFace(scene, [N, X, Y], {
    color: 0xdc2626,
    opacity: 0,
    curveRadius: -curveRadius,
    curvePoints,
  });
  const fEqualizerf = addFace(scene, [Equalizer, X, Y], {
    color: 0xf59e0b,
    opacity: 0,
    curveRadius,
    curvePoints,
  });
  const fEqualizerg = addFace(scene, [Equalizer, X, Y], {
    color: 0xf59e0b,
    opacity: 0,
    curveRadius: -curveRadius,
    curvePoints,
  });

  loadModel(scene, url, {
    position: [0, 0, -1],
    rotation: [0, 0, 0],
    targetSize: 9.4,
  });

  addSlider(container, {
    label: "draw commuting triangles",
    value: 0,
    onInput: (v) => {
      fNf.material.opacity = v * 0.35;
      fNg.material.opacity = v * 0.35;
      fEqualizerf.material.opacity = v * 0.35;
      fEqualizerg.material.opacity = v * 0.35;
    },
  });
}

// Universal cone over the product diagram — same treatment as
// buildEqualizerCone above, but anchored to the "A_i" / "A_J" glyphs of
// notebook_product.glb instead of "X" / "Y". Unlike the equalizer, the base
// diagram here is discrete (no arrows between the A's, see Figure 2's
// caption), so there is no commuting triangle to fill in: a cone over a
// discrete diagram is just a family of arrows, nothing has to commute with
// anything else. Accordingly this omits buildEqualizerCone's face/slider.
function buildProductCone(container) {
  // Same x-offset fix as buildEqualizerCone above, and for the same reason:
  // A_i and A_J are both centered on the page in x.
  const { scene } = initScene(container, {
    cameraPos: [5.0, 5.2, 9.4],
    lookAt: [0, 2.8, 0.3],
    fov: 50,
  });
  const url = "./assets/notebook_product.glb";
  const Ai = [-0.18, 0, -1.84];
  const Aj = [0.09, 0, 2.44];
  const Product = [0.05, 3.1, 0.3];
  const N = [0.2, 6.1, 0.42];

  addNode(scene, Product, "\\prod_{i \\in I} A_i", { offset: [0.42, 0.1, 0] });
  addNode(scene, N, "N", { offset: [0.42, 0.1, 0] });

  addArrow(scene, Product, Ai, { color: 0xf59e0b });
  addArrow(scene, Product, Aj, { color: 0xf59e0b });
  addArrow(scene, N, Ai, { color: 0xea580c });
  addArrow(scene, N, Aj, { color: 0xea580c });
  addArrow(scene, N, Product, { color: 0xdc2626, radius: 0.034 });

  loadModel(scene, url, {
    position: [0, 0, -1],
    rotation: [0, 0, 0],
    targetSize: 9.4,
  });
}

const registry = {
  notebook_equalizer: buildNotebookEqualizer,
  notebook_product: buildNotebookProduct,
  equalizer_cone: buildEqualizerCone,
  product_cone: buildProductCone,
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
        "This interactive 3D graphic needs WebGL, which isn't available in this browser right now.";
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
  buildNotebookEqualizer,
  buildNotebookProduct,
  buildEqualizerCone,
  buildProductCone,
};
