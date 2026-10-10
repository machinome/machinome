# Game assets: a machinome model as a rigged, budgeted GLB

Provisional, 2026-10-04. Working record, not a promise: nothing here is
ratified, no OpenSpec change exists for it, and a baseline spec or an
accepted ADR outranks every sentence below. It records a direction the
pilot opened on 4 October 2026, the measurements that shaped it, and the
spike that proved its first form; it supersedes the standalone spike note
of the same day (`game-asset-spike.md`), whose text it keeps in full under
"The spike" and whose evidence stays in `game-asset-spike/` beside this
file. Written from the code as it stands at Machinome 0.7.1 on `main`.

## Where this came from

The framework produces three things from one model: the viewer bundle, a
front-end application; the production bundle, on its unmerged branch; and
videos, through the videomaker that mounts the viewer headless. On
4 October the pilot asked for a fourth: a 3D gallery to experiment in like
a game, and the models themselves as outputs for games.

The first assessment that day put both as a View in 0.8 terms and leaned on
the viewer's running engine, some 13,500 lines of TypeScript with no
three.js in it, as the runtime a game would embed. The pilot's correction
set the actual shape: a game cannot carry six hundred pieces of a Curta in
the same scene as four thousand from a printer, nor the running program;
what it wants is what an artist makes in Blender. A few bodies, coarse
meshes, a rig, clips. That is this note's subject. The gallery, a walkable
scene of many live machines on the viewer's own runtime, is a different
output and is not planned here.

## The shape of the output

One GLB per model, three layers in one file, each usable without the next:

- **Bodies.** The tree cut at every placement that reads a variable;
  everything between two cuts is one rigid body with one merged mesh per
  colour, at a triangle budget. The joint chain is the node hierarchy.
- **Clips.** The model's instructions, or a gesture recorded from the
  Python runtime, sampled into glTF animation channels on the joint nodes.
  An engine without any machinome code plays them.
- **Formulas.** The drivers, the bindings and each joint's expression in the
  file's extras, so a consumer that wants to pose from state rather than
  from clips can do it in a line of script. The program's own affine flags
  say which joints are a constant times a state value and which are not.

What it is not: the viewer, a runtime, a simulation. It carries no stops,
no contact, no verdicts. Fidelity is set by budgets, the deflection, the
triangle count, which inputs are exposed, whether interiors are dropped,
and in 0.8 terms those budgets are a fact of the View layer, not of the
model. The asset is data and travels under the design's licence.

## What the catalogue says

Pieces grouped by what moves together, measured on the built documents on
4 October (`Thor` remeasured after a rebuild from source; the first reading
on a stale document gave 36):

| machine | pieces placed | co-moving bodies | placed triangles |
|---|---|---|---|
| Thor | 438 | 41 | 1.46 M |
| Curta 3x | 390 | 165 | 0.7 M |
| Prusa3 | 207 | 17 | 1.05 M |
| Kossel | 373 | 20 | 64 k |
| Voron 2 | 1565 | 106 | 2.0 M |
| 3DPrintedClocks | 57 | 29 | 235 k |

The body count is the upper bound of independent motion, every freedom
included; a game that exposes fewer inputs merges further. The triangles
are the real excess, tessellation at a tenth of a millimetre being
simulation precision. In the Curta's running document the laws split 183
affine to 85 non-affine, and placements 94 bare coordinates to 91
expressions; its clocked document has 18 states and 39 commits, each a
transition a game's animation state machine can hold.

## The spike

A spike, 2026-10-04. Status: design evidence for the output above. It
created no requirement and changed nothing in any repository: the code
ran in a throwaway venv in the session scratchpad against the Thor arm's
built document, and only this record and the evidence directory
`game-asset-spike/` were committed. The project is
`projects/Robotic-Arms/Thor`, the upstream design CC-BY-SA-4.0, the
framework at Machinome 0.7.1 on `main`.

### The question

**Can the document be reduced to bodies, clips and per-body formulas, at a
game triangle budget, with no machinome code in the engine, and still pose
exactly as the viewer does?**

Thor was chosen over the Curta because its motion is almost entirely the
game-friendly kind: six joint angles that are bare driver coordinates, every
shaft and pulley an affine multiple of one, and one non-affine piece, the
gripper's four-bar. The Curta's question, whether a gesture's clip is
independent of machine state, is not answered here.

### Verdict

**The design holds for Thor.** One GLB of 2.7 MB carries 41 bodies under a
40-node rig, five clips and the formulas, and a stock glTF loader with
forty lines of JavaScript poses it identically to the viewer: zero
deviation in every body frame at four poses by matrix comparison, and
silhouettes within two percent of the viewer's own renders at five poses.
Blender imports the rig, the clips and the extras; Godot imports the rig and
the clips but drops the extras. The whole pipeline from document to GLB runs
in about five seconds.

What did not hold as first planned: mesh decimation on the document's own
STLs stalls at about forty percent on STEP-born parts, whatever the
decimator, so the reduction has to start from the B-rep at a coarser
deflection, which the build directory already keeps beside every STL.

### Measurements

The document, rebuilt from source during the spike (see "Findings"):

| Thor | value |
|---|---|
| pieces placed | 438 |
| distinct meshes | 90, every one with its `.brep` beside it |
| placed triangles at 0.1 mm / 0.1 rad | 1,461,220 |
| drivers | 7: six angles in degrees, one grip in millimetres |
| named poses (instructions) | 6 |
| flexible parts | 3 belts, molejo |

The partition, by cutting the tree at every placement that reads a
variable:

| after partition | value |
|---|---|
| co-moving bodies with a mesh | 41 |
| joint nodes | 40 |
| of which bare joint coordinate | 6 |
| of which affine in one driver | 20 |
| of which a formula | 14, all reading `grip` |
| glTF nodes in the rig | 129 |

The 14 formula nodes are the gripper's four-bar and the fasteners riding its
arms: an arc cosine of the grip distance, one line of script in any engine.

The reduction:

| step | distinct triangles | placed triangles | time |
|---|---|---|---|
| document STLs, 0.1 mm / 0.1 rad | 795,704 | 1,461,220 | — |
| re-tessellated from B-rep, 0.5 mm / 0.5 rad | 134,724 | 225,550 | 3.9 s |
| re-tessellated, 1.0 mm / 0.8 rad | 87,538 | — | 2.5 s |
| decimated to the 100,000 budget | — | 100,285 | 0.8 s |

The file: 2,691,784 bytes, binary glTF 2.0, 11 materials (one per node
colour), 5 clips (Park, Pick, Place, Reach, Ready; Home is the rest pose
and yields no channel), extras on the root node carrying the drivers table,
the 28 bindings and every joint's operation, axis, expression and class.

The proof of pose, `verify_rig.py`: every body node's world frame from the
GLB hierarchy against the same node's frame composed from the document's
operation chains, at Home, Park, Place and one pose with all seven drivers
off their defaults. Maximum probe deviation 0.000000 mm at all four. The
page's JavaScript scope against Python's at Place: 35 names, maximum
difference 0.

The proof of pixels: the asset page captured headless with the viewer's own
camera rule (fov 50, from (1, −1, 0.8), 1.2 × the half diagonal over
tan(fov/2)) beside `machinome snapshot --renderer web` at the same drivers.
Silhouette intersection over union:

| pose | IoU |
|---|---|
| Home | 0.983 |
| Park | 0.997 |
| Place | 0.987 |
| wrist roll alone | 0.983 |
| base turn alone | 0.983 |

The residual is the coarse mesh and the dropped belts, visible in
`game-asset-spike/comparison.png`: the big bodies read as the viewer's; the
gripper's organic surfaces at this budget look quilted, which is decimation
over a coarse tessellation under smooth normals, and is where an artist or
interior removal would earn their keep.

Engines, both headless on this machine:

| engine | result |
|---|---|
| Blender 4.2, `import_scene.gltf` | 129 objects: 41 meshes, 88 empties; the joint chain shoulder → art2 → art3 → art4 → art56 → output intact; the 5 clips arrive as 106 actions, one per animated object per clip, with the first clip bound to 28 objects; extras arrive as custom properties; Cycles renders at Home and at the Park clip's last frame match the viewer |
| Godot 4.3, `GLTFDocument.append_from_file` + `generate_scene` | 131 nodes, 41 `MeshInstance3D`, 100,285 triangles, the same chain, the 5 animations in an `AnimationPlayer`; node extras are not kept as metadata |
| three.js 0.156 `GLTFLoader` | the asset page: extras in `userData`, clips as `AnimationClip`s, no console errors |

### How it was made

1. **Partition.** Walk the document; a node whose operations read a
   variable starts a body; constant nodes fold into the body above them.
2. **Rig.** Each variable placement becomes up to three glTF nodes: a
   `pivot` holding the constant operations applied after it, the joint
   node holding only the variable rotation or translation as TRS, and an
   `offset` holding the constant operations applied before it. The
   viewer's rule, matrix = M_opN … M_op1, is reproduced exactly; constant
   leaf placements are folded into the merged vertices.
3. **Meshes.** Every leaf's B-rep re-tessellated with OCP at 0.5 mm /
   0.5 rad, merged per body and per colour, then decimated with quadric
   collapse to a proportional share of the budget. Colour is one PBR
   material per node colour. Normals are per-vertex.
4. **Clips.** Each instruction sampled at 30 fps from the drivers' defaults
   to its targets, linearly, every joint node's TRS written as a LINEAR
   sampler.
5. **Extras.** The drivers, bindings, joint formulas and instruction table
   on the root node, so a consumer can pose without clips.
6. **Root.** One node turning Z-up millimetres into Y-up metres.

The scripts are in `game-asset-spike/`: `thor_glb.py` (partition, rig,
merge, decimate, write), `retess.py` (B-rep re-tessellation, workspace
venv), `verify_rig.py` (the matrix proof), `verify_page.py` (the scope
proof), `capture.py` (headless captures), `blender_check.py` and
`import_check.gd` (the engine imports), `compose.py` (the sheet), and the
page `index.html`. Reports: `measurements.json`, `retess.json`,
`blender-report.json`, `godot-report.json`, `comparison.png`,
`gripper-diagnostics.png`. The GLB itself is regenerated by the scripts in
seconds and is not committed.

### Findings

- **Decimation needs clean input.** On the document's 0.1 mm STLs, both
  quadric decimators tried (fast-simplification and pyfqmr, border
  preservation on or off) stop at about 40 % on STEP-born parts
  (Art1Body: 56,774 → 22,836 faces) while reaching the 7 % target on a
  watertight part (GripperActiveArm: 59,526 → 4,166). The stalled parts
  are not watertight (368 boundary edges on Art1Body) and are built of
  long slivers along curved faces. Re-tessellating from the B-rep is both
  the cleaner reduction and the one that makes the decimator work
  afterwards. A production exporter should take the B-rep route for exact
  leaves and decimate only STL-born ones.
- **The build document can lag the source.** `_build/viewer.json` had 458
  nodes while the source built to 461: the gripper's fasteners had been
  moved into a `gripper` group since the last build, and the snapshot,
  which bakes from source, disagreed with a GLB made from the stale file.
  An exporter must build first, as `machinome export` already does, never
  read a build directory's document as the model.
- **glTF consumers differ in strictness.** Blender's importer rejects an
  accessor whose `min`/`max` are scalars rather than one-element arrays;
  three.js and Godot accept it. The writer was fixed; a real exporter wants
  the Khronos validator in its tests.
- **Blender binds the first clip.** After import, frame 1 is the first
  clip's start and a manual rotation of a joint is overridden at render;
  posing by formula in Blender means clearing the animation data first.
  Godot and three.js leave the rig free until a clip is played.
- **Godot drops node extras** on runtime import, so the formulas need a
  `GLTFDocumentExtension` or a sidecar there. The hierarchy and the clips
  are enough for a game that scripts the six joints itself.
- **Flexible parts have no engine form.** The three belts were dropped and
  recorded. molejo's fixed topology would allow morph targets for short
  clips; nothing was tried.
- **What a camera does to a comparison.** Before the page adopted the
  viewer's camera rule and re-framed per pose, Park and Place compared at
  0.39 and 0.60 IoU and the gripper looked rolled by ninety degrees; with
  the rule, 0.997 and 0.987. Pixel comparisons across renderers need the
  same framing rule, not the same intent.

### What the spike does not claim

- Nothing about running or clocked machines: whether a gesture's clip is
  independent of state (the Curta's question) is untested.
- No interior removal, no textures, no LODs, no physics, no Unity or
  Unreal, no player input beyond sliders and keys.
- No claim about other machines beyond the partition counts above: that
  the partition collapses them is measured; that their motion classes are
  as kind as Thor's is not.
- Not a framework feature.

## The exporter, as the spike suggests it

Where each step would live if a cycle is cut, following the lean-core
plan's seams (`lean-core.md`):

- **Partition and rig** in core. Every input is framework knowledge: the
  tree, the operation chains, the program's affine flags, the controls'
  axes. The joint table a game needs is the same additive document key the
  first assessment named, derived from mates since ADR-147.
- **Meshes** behind the engine seams: re-tessellation of exact leaves
  behind the B-rep provider, decimation of STL-born leaves behind the mesh
  provider, with the decimator an optional dependency the venv does not
  carry today.
- **Clips** from the Python runtime: instructions for posed documents,
  `sim.move` recordings for running ones, commits for clocked ones.
- **The GLB writer** in core. trimesh already writes a scene graph; the
  animation samplers and extras are a small amount of JSON the spike wrote
  by hand.
- **The command.** A format on `machinome export`, or a target of its own;
  budgets as declarations of the View layer once 0.8 has one, flags
  until then.
- **The checks.** The spike's three, kept as tests: the matrix proof
  against the document, the silhouette proof against the viewer with the
  viewer's framing rule, and a glTF validator. Pixels remain evidence.

Nothing above is proposed. A cycle would be cut from the Thor finding
under the framework-change skill, with Thor as the project that validates
it, and would carry the budgets as its first design decision.

## Open questions

- **State-dependent gestures.** The Curta's crank clip should be the same
  from any state while the dials pose by formula from state. Recording the
  same gesture from two states in the Python runtime and diffing the
  clip-driven bodies would settle it; it is the second spike if one is
  wanted, or evidence the first cycle collects.
- **Interior removal.** Most of the Curta's pieces are inside the housing.
  A visibility bake over sampled poses, by ray casting, is the mechanical
  form of what an artist does by eye. Not tried.
- **Flexible parts.** Morph targets from molejo's fixed topology for short
  clips, or dropped with a record, or left to the artist.
- **Textures and LODs.** The asset carries colours only. Engines generate
  LODs on import; textures are artist work in Blender.
- **Godot extras.** A `GLTFDocumentExtension` that reads the formulas, or
  a sidecar JSON, if the formula route matters there.
- **The gallery.** A separate output on the viewer's runtime, needing the
  engine extracted from the renderer and a scene that hosts many
  documents; nothing of it is in this note.
