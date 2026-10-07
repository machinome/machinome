.. _changelog:

Changelog
=========

Unreleased
----------

* **A direction a few millionths off an axis stays unit.** A joint's axis,
  and a frame's directions when ``z`` or ``x`` is omitted, snap to a
  principal axis only as a whole: a direction whose every component lies
  within ``1e-9`` of ``0``, ``1`` or ``-1`` is that axis in integers, as
  before, and any other keeps its components, only those within ``1e-9`` of
  ``0`` becoming ``0``. A direction such as the ``z`` a URDF's
  ``rpy="1.57079 0 0"`` states, ``(0, -0.99999999998, 6.33e-6)``, used to
  have its second component made ``-1`` and read ``1 + 2e-11`` long; it now
  reads unit to ``1e-12``, and a mate stating no axis turns its child about
  exactly the ``z`` ``resolved_frames`` reads for the moving frame
  (snap-keeps-the-triad-unit).
* **A build of a fresh checkout finishes.** ``machinome build`` and
  ``machinome develop`` no longer start over without end when a file a
  part reads, such as an ``StlNode``'s mesh, is newer than the module
  declaring it, as a fresh clone or worktree leaves a mesh checked out
  after its module. Each source is compared with what the build first
  saw of it, so a build stands down only for a file that changed after
  the build read it (build-settles-on-a-grown-source-set).
* **A refusal names what it refused.** A ``Prismatic`` or an ``Orbit``
  written with ``axis=None`` is refused naming its own kind and saying its
  axis is required everywhere, where it used to be called a ``Revolute``
  that a mate's moving frame could complete; written at a declaration site
  or as a mate's freedom, the refusal names the class or the mate the
  author wrote. A binding outside the range of a mate's freedom is refused
  naming the mate on the assembly that states it, the one place it can be
  bound, as ``arm.link2.link3.link4.link5: mate 'left_travel' declares the
  range -11.0 to 20.0 mm``, rather than the joint the mate installed on the
  moving child. And a relation naming one coordinate as its one source and
  its one driven end, ``wheel.turn.drives(wheel.turn)``, is refused when
  the class is defined, saying so, where it used to be refused only when
  the machine was solved, as an unreached or doubly bound coordinate
  (name-what-is-refused).
* **A read of children before they are linked is refused.** Inside an
  assembly's ``render()`` or ``simulate()``, a read of an internal node's
  ``children`` before the framework has linked them is refused with a
  ``StructureError`` naming the assembly, the phase, the read and the
  declared attributes to address instead (``self.near, self.far``). It used to
  answer an empty list, so a loop over it did nothing and said nothing:
  a shin rotated that way never turned, and a dial's parts coloured that
  way stayed uncoloured. A read after linking, or outside any phase,
  answers as before (children-refuse-early-reads).
* **A repeated copy reads its index while it is constructed.** A
  ``repeat()`` copy's ``index`` is readable from the start of the copy's
  own construction, so a joint's ``axis``, ``at``, ``range`` or
  ``carries``, a frame argument and ``check()``, declared on the repeated
  class, can read ``node.index`` and resolve per copy, where realization
  used to refuse with ``... has no attribute 'index'``. A function given
  where the child is declared is still handed the parent
  (resolve-repeated-joints-per-copy).
* **``machinome snapshot --preview`` draws.** The OpenSCAD renderer used
  to hand OpenSCAD a bare ``--preview``, which OpenSCAD 2021.01 reads as
  taking the model's ``.scad`` path for its value, so it printed its usage
  and the snapshot failed with no message. It now passes
  ``--preview=throwntogether``, the ThrownTogether preview the option has
  always been documented to select (tooling-paths-and-flags).
* **A camera vector beginning with a negative component photographs.** Under
  ``--renderer web``, a ``--camera`` resolving to an eye or an up direction
  whose first component is negative, such as ``0,0,0,65,0,35,1400``, was
  refused by the viewer's command line (``argument --up: expected one
  argument``); the framework now hands the viewer each camera vector in
  one token with its option (tooling-paths-and-flags).
* **A failing assertion names a part by its path.** Every assertion of
  ``machinome.test`` names a part by its path below the node under test,
  the path the viewer's tree shows and a qualified driver id is built
  from, so two instances of one class read apart: ``centre.wheel should
  not interfere with third.wheel``, where it used to read ``wheel should
  not interfere with wheel``. A direct child of the node under test reads
  as before (name-solids-by-path).
* **The running corpus keeps a stop made after a restore.**
  ``tools/generate_running_corpus.py``, and the suite's replay of
  ``tests/running-corpus.json``, counted a step's crossings and stops from
  where the run's record stood before a scripted restore, although the
  restore clears that record. A crossing or stop that the same step then
  made was left out of the step's entry, and the replay agreed with the
  omission. Both now count from the cleared record, as the time-drive
  generator already did. No committed corpus has such a step, and none
  changes (keep-the-corpus-cursor-honest).
* **A reused Follow prefix carries its paths.** When the two Bounds of a
  ``Follow`` target share one walk of their sub-program at a fraction of
  the stretch, the walk is stored as a read-only copy of the propagation
  it produced, with its source motions, Follow cuts and closures, and
  the walk that stores it reads the same copy. It used to be stored as a
  bare mapping of displacements, so a later Bound received a different
  kind of object than the first one. No level, stop or bank changes, and
  the Curta's crank tick costs the same (snapshot-the-follow-prefix).
* **A clocked snapshot restores only into the machine it was taken
  from.** ``sim.snapshot()`` under a clocked root carries the machine's
  identity, the string ``sim.identity`` returns and an export publishes
  as ``clocked.identity``, and ``sim.restore()`` refuses a snapshot whose
  identity differs, naming both, before touching anything. It used to
  compare the class name and the bank's ids only, so a snapshot restored
  into a same-named machine whose joint range or commit law had changed,
  or into a same-named class from another module. ``ClockedSnapshot``
  takes the identity as its third argument (clocked-snapshot-identity).
* **A production bound after a build reads the machine as built.** Binding
  a ``Production`` or a ``ModelSnapshot`` to a model that was already
  built, snapshotted or served no longer runs a fusion's ``render()`` a
  second time: the children it positions keep their one placement, a later
  ``render()`` returns them as they were, and a fused STL made again is the
  one the build made. A file a node names that does not exist is refused
  when the model is bound, as missing and naming the node and the path,
  with ``ProductionExportError`` from ``Production(model)`` and
  ``FileNotFoundError`` from ``ModelSnapshot(model)``; it used to be
  reported as an input that had changed (production-reads-once).
* **A production reports what is in its scope.** An instruction's
  Markdown is refused for an HTML tag only when the tag can carry a
  dependency, an element that embeds or loads content or an attribute
  that names a resource, and code spans and fenced code blocks are not
  read for dependencies, so ``if a<b then c>d`` and a quoted
  ``<img src>`` in code no longer refuse ``steps`` and ``export``. A
  child binding's reports are refused only for an overlap that claims an
  occurrence within its scope, so an overlap under one child no longer
  refuses its sibling; the root still refuses on any overlap. And the
  members of a repeated or tuple child binding are named by index at
  every count: a one-member repetition's member is ``kids-0``, as the
  first of two is, where it used to be ``kids``, in every declaration
  path and in the draft manifest (production-reports-in-scope).
* **A leaf that names no source file is refused in one shape.** A
  subclass of ``StlNode``, ``StepNode``, ``JScadNode`` or ``OpenScadNode``
  that does not declare its source attribute, or declares it empty, is
  refused when constructed with a ``ValueError`` naming the class, the
  attribute and the module to set it in: ``BareStl does not declare
  stl_source. Set stl_source in .../parts.py to the path of the file its
  part is read from, relative to that module's directory or absolute.``
  ``JScadNode`` used to raise a bare ``Exception`` naming
  ``OpenJScadNode``, a class that no longer exists, and ``OpenScadNode`` a
  ``TypeError`` from ``os.path.join`` naming neither. A leaf written outside
  machinome gets the same refusal by calling
  ``require_source_file(type(self), attribute, declared)`` with the declared
  value alone: it resolves the value beside the declaring module and
  returns the path, and the four-argument call keeps its meaning. And a
  build that fails before anything is built names the model and what was
  being done with it, ``The model assembly:Rig could not be loaded: ...``
  (or its sources could not be read, or it could not be assembled), where
  it used to read ``assembly:Rig: failed to load project: ...``
  (refuse-the-undeclared-file-by-name).
* **A failing test names the instant it failed at, and a set-up that
  raises is an error.** ``machinome test`` prints the traceback of a
  method's first failing instant, where it used to print the last one's,
  and a method that declares its instants names it on its line, with how
  many failed: ``FAIL! at instant 0.0 (8 of 8 instants failed)``, or, under
  ``--failfast``, ``(--failfast stopped the sweep at instant 1 of 3)``; the
  instant is written so that ``@testing_instant`` given it runs that
  instant. A method declaring no instant reads ``FAIL!`` as before. An
  exception from a test case's ``setUp`` is reported on the method's line
  as ``ERROR! (setUp raised)`` with its traceback, and one from its
  ``setUpClass`` as ``ERROR! (setUpClass raised)`` on each of the class's
  methods, where either used to end the run with a bare traceback and no
  summary line: the method does not run, the matching tear-down is not
  called, the run goes on, the summary line counts ``, E errors`` after
  ``F failed``, and the run exits 1. A ``unittest.SkipTest`` raised from
  ``setUpClass`` skips the class's methods with its reason, where it used
  to end the run (report-the-instant).

Machinome 0.8.0
---------------

Released on 05/Oct/2026

**A lean core.** A project installs only the CAD kernels its parts use,
imports every name from the one module that defines it, and compares its
parts on one of two engines named for what they consume: the B-rep engine,
over boundary representations, and the mesh engine, over triangle meshes.
OpenSCAD is one family of node types among the others, no longer part of
every install. Leaves written outside machinome have a declared, versioned
contract; production profiles turn a model into a bill of materials and
maker instructions; and a second test run of an unchanged project is served
the verdicts the first one decided. No verdict, golden value or artifact
byte changes, and the published document does not move: exports declare
document versions 1 to 13, as 0.7's do, so a 0.7 viewer reads them.

**Breaking changes**, each with what to change on :doc:`the upgrading page
<upgrading>`:

- a bare ``pip install machinome`` carries no CAD kernel, no SolidPython and
  no manifold3d; install the extras your parts use;
- the root of ``machinome.node`` exports nothing: each of its twenty-one
  names is imported from its module;
- ``machinome.node.adapters`` is dissolved: ``machinome.node.adapters.<x>``
  is ``machinome.node.<x>``;
- ``machinome test --exact`` and ``--faceted`` are ``--brep`` and
  ``--mesh``, and ``SOLID_TEST_KERNEL`` is refused for ``SOLID_TEST_ENGINE``;
- ``machinome.exact`` and ``machinome.mesh_engine`` are removed: the B-rep
  operations are ``machinome.engine.brep``'s and the seams and errors
  ``machinome.engine``'s;
- ``shape()`` returns the kernel's own ``TopoDS_Shape``, not a CadQuery
  ``Shape``;
- the B-rep leaf base is ``BrepLeafNode`` at ``machinome.node.brep_leaf``, a
  node's flag ``brep``, and the leaf contract is version 3; the sheet and
  flexible hooks lose their underscore;
- ``Solid2Node``, ``OpenScadNode`` and the OpenSCAD renderer of
  ``machinome snapshot`` need their extras; the SCAD members belong to the
  family's leaf base, and ``as_scad`` is ``present``;
- a build writes the ``.scad`` of an OpenSCAD-family part only;
- ``machinome.scad_expression`` and ``machinome.openscad`` are removed, and a
  symbolic value is machinome's own type;
- ``machinome new`` and ``machinome import-step`` write imports from the
  modules;
- every project's kept verdicts recompute once, every mesh fusion's STL is
  written again once to the same bytes, and a part whose module was rewritten
  rebuilds once.

* **Licence:** from this release Machinome is licensed
  |framework_licence|, at the recipient's choice. The browser viewer,
  ``machinome-viewer``, is a separate package under AGPL-3.0-or-later.

* **Install only what your parts use.** Each CAD kernel is an extra named for
  the last component of the module that needs it: ``machinome[cadquery]``,
  ``[build123d]``, ``[step]``, ``[molejo]``, ``[brep]`` (the B-rep engine's
  OCCT kernel, which the first four install too), ``[mesh]`` (manifold3d, for
  the mesh engine), ``[openscad]`` (SolidPython), ``[solid2]`` (which installs
  ``[openscad]``), ``[jscad]`` and ``[stl]``, which install nothing today, so
  that every node type has the extra of its name and a manifest naming one
  stays valid when the node types become packages of their own, and
  ``[all]``. Without its extra a module refuses at import with the line that
  installs it: ``machinome.node.cadquery (CadQueryNode) needs cadquery, which
  is not installed; install it with 'pip install "machinome[cadquery]"'``.
  ``machinome import-step`` without the ``step`` extra answers ``Error:
  machinome import-step needs the step extra: ...`` and exits 1, and is still
  listed by ``machinome -h``. Declaring a marking needs no kernel; building a
  stale ``Svg`` marking needs ``machinome[build123d]`` and without it is
  refused naming the part, the marking and the artwork. Without the mesh
  engine, each path that needs it (a part without B-rep geometry compared,
  ``machinome test --mesh``, ``assertAssemblySupported``, a mesh fusion, a
  project calling manifold3d or ``trimesh.boolean`` itself) refuses naming
  ``pip install "machinome[mesh]"``, and ``machinome test`` on the mesh
  engine refuses at its start, before building anything; an all-B-rep project
  needs it only for those. A project with its extras installed sees no
  change, and no artifact byte changes (ADR-167, ADR-168, ADR-176).

  **Breaking (install):** a bare ``pip install machinome`` carries no CAD
  kernel, no SolidPython and no manifold3d; the tutorial's machine needs
  ``machinome[cadquery]``. **Breaking (framework API):**
  ``machinome.node.adapters`` is dissolved, and importing anything under it
  fails at the import line naming the rule, ``machinome.node.adapters.<x>``
  is now ``machinome.node.<x>``; for example ``from
  machinome.node.adapters.step import StepAssembly`` becomes ``from
  machinome.node.step import StepAssembly``. A node whose class is one of
  the leaf classes itself, rather than a project's subclass, rebuilds once,
  because its module is part of its recipe (:doc:`/start/install`).

* **One path for every name.** Every leaf type is one module directly under
  ``machinome.node``, named for its technology: ``machinome.node.cadquery``,
  ``.build123d`` (which holds ``Build123dSheetNode`` too, and the reducer of
  ``Svg`` artwork), ``.step`` (``StepNode``, ``StepAssembly``,
  ``solids_from_faces``, ``cached_document``), ``.molejo``, ``.solid2``,
  ``.openscad``, ``.jscad`` and ``.stl``. The root of ``machinome.node`` is
  the package's path, its refusals and its submodules (``from machinome.node
  import supported`` still imports the module), and exports no other name:
  ``from machinome.node.assembly import AssemblyNode``, ``from
  machinome.node.step import StepNode``, ``from machinome.node.frames import
  Frame``. Importing one of the twenty-one names the root used to resolve,
  or reading it off the root, raises ``ImportError`` naming its module and
  the line to write. ``machinome new`` and ``machinome import-step`` write
  their import lines per module (ADR-169, ADR-181).

  **Breaking (framework API):** the twenty-one names fail at ``from
  machinome.node import ...`` with nothing aliasing them, a star import from
  the root binds nothing, and ``machinome.node.__all__`` is empty.
  **Breaking (generated source):** a project ``machinome new`` or
  ``machinome import-step`` writes imports from the modules. Each part whose
  module a rewrite touches rebuilds once, to the same bytes
  (:doc:`upgrading` maps all twenty-one).

* **Two engines, named for what they consume.** The B-rep engine and the
  mesh engine are the modules ``machinome.engine.brep`` and
  ``machinome.engine.mesh`` of one engine package, ``machinome.engine``,
  which holds both seams (``brep_engine``, ``require_brep_engine``,
  ``mesh_engine``, ``require_mesh_engine``, their error types and contract
  versions) and admits a provider installed later. Every operation on a B-rep
  shape lives in ``machinome.engine.brep``, written on the OCCT kernel alone
  with no CadQuery, and every comparison on meshes in
  ``machinome.engine.mesh``, the core calling none of manifold3d's API: a
  model with no B-rep part never loads the B-rep engine, and a part whose
  artifacts are current is reused without it. The operations a project calls
  directly, ``intersect_shapes``, ``fuse_shapes``, ``placed_shape``,
  ``solid_count`` and ``solid_volume``, keep their names and signatures in
  ``machinome.engine.brep``, and the errors are
  ``machinome.engine.BrepCommonInconsistency`` and
  ``BrepCommonVerificationError``. ``shape()`` and those operations return
  the kernel's own ``TopoDS_Shape``, so a B-rep part may render it directly
  and build, fuse and test without CadQuery or build123d. A test run compares
  on an engine: ``machinome test --brep`` (the default) or ``--mesh``, else
  ``SOLID_TEST_ENGINE``, ``brep`` or ``mesh``; its line, summary note and
  messages say "the B-rep engine" and "the mesh engine". Every verdict,
  every artifact byte and every golden value is what it was (ADR-160,
  ADR-161, ADR-162, ADR-180; :ref:`comparison-engine`).

  **Breaking (command line):** ``--exact`` and ``--faceted`` are
  unrecognised, and ``SOLID_TEST_KERNEL`` is refused whenever it is set,
  naming ``SOLID_TEST_ENGINE``: rename it in a checkout's ``.env``.
  **Breaking (framework API):** ``machinome.exact`` and
  ``machinome.mesh_engine`` are removed with no alias; a project that calls
  CadQuery's methods on a ``shape()`` wraps it,
  ``cadquery.Shape.cast(node.shape())``. Every project's kept verdicts
  recompute once, and every mesh fusion's STL is written again once, to the
  same bytes, because its recorded recipe is renamed.

* **The leaf bases are a declared contract.** ``LeafNode``, ``BrepLeafNode``,
  ``SheetLeafNode`` and ``FlexibleNode``, each imported from the module that
  defines it (``machinome.node.leaf``, ``.brep_leaf``, ``.sheet_leaf``,
  ``.flexible``), are the extension points a node type written outside
  machinome subclasses, and the API reference documents what each declares.
  A leaf declares its kind as one set the core reads directly (``rigid``,
  ``flexible``, ``brep``, ``optimize``, ``present``, ``presentation``,
  ``kept_artifacts``, ``generate_stl``, ``base_mesh``,
  ``declared_markings``). The contract is versioned:
  ``machinome.node.leaf.CONTRACT`` is ``3``, and a class declaring
  ``leaf_contract`` in its own body is refused when it is created if the
  numbers differ. A leaf writes an artifact of its own through one call,
  ``publish_artifact(path, write)``, which stamps, records and replaces it
  atomically and does nothing when it is current; a node states what decides
  its artifacts beyond its tracked files as ``source_recipe``, and changing
  it alone rebuilds them; the external-file identity mixin is public as
  ``machinome.node.sources.ExternalSourceIdentity``. A loaded ``shape()`` is
  keyed on its ``.brep``'s observation, so a ``.brep`` replaced under an
  unchanged source stamp is never served stale. The core no longer decides
  anything about a node by the spelling of its class name: the refusal
  raised when OpenSCAD is missing names the node and its own class, ``node
  housing (FacetedBox) requires the OpenSCAD binary because its STL is
  rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is
  on PATH``. Artifacts, source records and identities are unchanged for a
  node declaring no recipe (ADR-163, ADR-164, ADR-165, ADR-166). Born of a
  B-rep leaf written outside machinome, reading FreeCAD's files, which
  imported CadQuery only to cast its shape, evicted a private cache and
  overrode the core's private currency.

  **Breaking (framework API):** the B-rep leaf base is ``BrepLeafNode`` at
  ``machinome.node.brep_leaf``, where it was ``ExactLeafNode`` at
  ``machinome.node.exact_leaf``, and a node's flag is ``brep`` where it was
  ``exact``. For subclasses of the two specialised bases only, the sheet
  hooks ``_profile_faces``, ``_lies_on_xy_plane``, ``_extrude`` and
  ``_write_dxf`` are ``profile_faces``, ``lies_on_xy_plane``, ``extrude`` and
  ``write_dxf(face, path)``, which writes to the path it is given, and the
  flexible hooks ``_shape_parameters``, ``_shape_spec``, ``_snapshot_mesh``,
  ``_snapshot_stl`` and ``_snapshot_shape`` lose their underscore. A leaf
  whose STL is not current after its materialization is refused naming it,
  instead of being handed to OpenSCAD.

* **OpenSCAD is one family among the node types.** ``OpenScadNode``, the
  family's leaf base ``ScadLeafNode`` (``machinome.node.openscad.leaf``), the
  SCAD writer (``.writer``) and the OpenSCAD binary contract (``.binary``)
  are the package ``machinome.node.openscad``, and ``Solid2Node`` is
  ``machinome.node.solid2`` over it, which registers the adoption of
  SolidPython values with the expression graph when it is imported. The core
  names no technology: one table of supported node types,
  ``machinome.node.supported``, is where it names node types, for the node
  root's refusals, ``import-step`` and the snapshot renderers. A node's
  presentation is machinome's own description (``present``,
  ``presentation()``, ``assemble()``), which the family's writer turns into
  SCAD text, byte for byte the text it was: ``assemble()`` needs neither
  SolidPython nor the family, and a project of B-rep, STEP or STL parts
  builds, tests, exports and publishes without them. A build keeps an
  artifact because a node declares it in ``kept_artifacts()``, and removes on
  every build one published as transient, such as the root ``.scad`` an
  interrupted OpenSCAD snapshot left. ``machinome new`` scaffolds a
  ``Solid2Node`` where SolidPython is installed, a ``CadQueryNode`` where only
  CadQuery is, and refuses naming both extras with neither (ADR-170 to
  ADR-173, ADR-177, ADR-178, ADR-179).

  **Breaking (install):** ``Solid2Node`` needs ``machinome[solid2]``, and
  ``OpenScadNode`` and the OpenSCAD renderer of ``machinome snapshot``
  ``machinome[openscad]``; without it importing the node type, and
  ``machinome snapshot`` with its default renderer, refuse naming the extra.
  **Breaking (build output):** ``machinome build`` writes the ``.scad`` of an
  OpenSCAD-family part (a ``Solid2Node``, an ``OpenScadNode``), from which
  OpenSCAD renders its STL, and no other: not the ``.scad`` of an assembly,
  of a fusion, of a flexible part or of a B-rep, STEP, STL, JSCAD or sheet
  part, nor a flexible part's per-pose snapshot STL, and the next build
  removes those an earlier build left. A machine's SCAD text is
  ``scad_code(node)`` from ``machinome.node.openscad.writer``, for any node;
  ``machinome snapshot --renderer openscad`` writes the root's ``.scad`` for
  the pose it renders only while OpenSCAD draws it. The file of a coloured
  OpenSCAD-family part declaring ``optimize = False`` is no longer
  overwritten with its coloured presentation after the render, and a later
  build, test or export process no longer replaces the ``.scad`` of a
  current OpenSCAD-family part with an import of its own STL. **Breaking
  (framework API):** the SCAD members (``scad_file``, ``scad_code``,
  ``generate_scad``, ``fn``) leave the node and leaf bases for
  ``ScadLeafNode``; ``as_scad`` is ``present``, and a project leaf that only
  overrode ``as_scad`` subclasses ``Solid2Node``; ``assemble()``,
  ``present()`` and ``artifact_import()`` return machinome's presentation
  description instead of a SolidPython object (render it with the writer's
  ``scad_text``); ``Rotation.scad()`` and ``Translation.scad()`` are removed,
  and ``Builder`` no longer takes ``scad_output``; the OpenSCAD binary
  helpers ``require_openscad``, ``openscad_binary`` and
  ``OpenScadUnavailable`` are imported from ``machinome.node.openscad.binary``
  where they were ``machinome.openscad``'s.

* **Symbolic values are machinome's own.** Animation time, driver reads and
  what ``machinome.math`` returns for them are
  ``machinome.expression_graph.GraphValue``, a type the core defines, and
  importing ``machinome.math`` imports no SolidPython. Arithmetic,
  comparisons, degree math and their text are unchanged, and so is every
  SCAD file and published document, byte for byte; the expression modules
  are documented as machinome's expression language. Asking a symbolic value
  for its truth raises ``SymbolicTruthError``, an ``Exception``, naming it.
  The animation time a part reads is ``self.time`` inside ``simulate()``.
  SolidPython's own values (``solid2.get_animation_time()``,
  ``scad_inline(...)``) are accepted by ``machinome.math``, laws and bounds
  in a process that imported ``machinome.node.solid2``; with one on the LEFT
  of an operator, SolidPython builds the result as its own text, which
  machinome reads back wherever it is used (ADR-170, ADR-171).

  **Breaking (framework API):** ``machinome.scad_expression`` is removed and
  its names (``get_animation_time``, ``GraphValue``, ...) are imported from
  ``machinome.expression_graph``; ``scad_expression`` is
  ``closed_expression`` in ``machinome.core.expressions``, and
  ``OPENSCAD_FOV`` is ``DEFAULT_FOV``. A SolidPython value is an expression
  only in a process that imported ``machinome.node.solid2``.

* **Independent production profiles:** bind typed acquisition choices and
  nested maker instructions to the actual existing model, then read BOM,
  stock, mass and coverage findings directly. Printed material and mass can
  stay unknown; whole sourced assemblies replace their internal acquisition.
  Geometry and instruction fingerprints govern manufactured consolidation,
  while explicit component requirements govern sourced consolidation.
  Atomic portable exports retain diagnostic gaps and pinned STL/DXF bytes
  and are always draft. A read-only model facade supports actual active
  children without simulation or a model rewrite (:doc:`/reference/api`,
  ADR-174, ADR-175). Born of a mechanical calculator whose printed and
  bought parts come from one STEP file and whose author's bill of materials
  states quantities, infill and finishing that geometry cannot.

* **Verdicts kept between runs:** a second ``machinome test`` of an
  unchanged project is served every intersection verdict the first one
  decided, without running a boolean. Verdicts are kept in the build root's
  ``.verdicts`` directory, shared by every declared model, and are
  identified by state, never by a path or a time: the content of each rigid
  part's artifact, a flexible part's bound values and specification, and
  the pair's quantised relative placement. A flexible pair is now remembered
  within a run as well. Each verdict is bound to the framework's source, the
  installed kernels and molejo, and the platform, so an upgrade starts the
  store afresh; no verdict changes, and a damaged or unwritable store is
  ignored. The store is on by default and silent; ``--no-verdict-store`` or
  ``SOLID_TEST_VERDICT_STORE=off`` runs without it and says so on the summary
  line, and deleting ``.verdicts`` is always safe (:ref:`verdict-store`,
  ADR-156). Born of a 3D-printed wall clock whose tests took minutes in
  every fresh process and take seconds in the next one, with the same
  results, and of a walking linkage's demo, likewise.

* **An export records its revision:** when the project is a Git repository
  with a commit, ``machinome export`` writes a ``source`` object into
  ``manifest.json``, the full hash of the commit checked out and ``dirty``,
  true when ``git status`` lists a changed tracked file or an untracked file
  the project does not ignore. A dirty project is exported all the same.
  Outside a repository, or without ``git``, the manifest is unchanged; the
  record moves no document version and a viewer needs nothing new
  (:doc:`/concepts/publishing`, ADR-158). Born of filming a mechanical
  calculator, whose film is held to the model it shows by that revision.

* **A clocked simulation names its machine:** ``sim.identity`` is the
  machine's identity, the string an export of the same model carries as
  ``clocked.identity``, whatever the bank holds, so a recording made through
  ``Sim`` can be refused against an export whose machine differs; a ``Sim``
  that is not clocked refuses it by name (:doc:`/reference/api`). Born of a
  film of a clocked calculator whose take could read the identity only from
  a private attribute.

* **Correction:** a project reached through a symbolic link builds in its
  own build root. A node whose module was imported through a path containing
  a symbolic link, such as a symlinked ``PYTHONPATH``, measured its build
  directory from the link to the project's resolved root and landed outside
  the build root, or failed to create it. A node's source is now taken as a
  resolved path, like the project root and every tracked source, so both
  spellings of a project share one build directory and what is built through
  one is current through the other. Found while filming a clocked
  calculator reached through a linked directory.

Machinome 0.7.1
---------------

Released on 27/Sep/2026

**Parts placed by relation.** A part names its connectors and an
assembly says how two connectors meet; the rest placement, the joint
and the coordinate follow from that one sentence. A new command checks
that a project stays inside the framework's universe. Nothing changes in
the published document: a 0.7.0 viewer reads a 0.7.1 export, and the
matching viewer 0.7.1 is 0.7.0 renumbered, API 27, schemas 1–13.
:doc:`/concepts/joints` teaches frames and mates and :ref:`vet` the
command.

* **Frames and mates:** a part declares its connectors as frames,
  ``hinge = Frame(at=..., z=..., x=...)``, in its own frame; an assembly
  relates two of them in one sentence,
  ``elbow = forearm.hinge.on(elbow_pin, Revolute(range=(-135, 135)))``,
  which places the child at rest, gives it a revolute joint about the
  frame's line and gives the assembly a coordinate named ``elbow``. The
  placement, the joint and the constants that kept them in agreement are
  no longer written by hand. ``Revolute`` may leave out its ``axis`` only
  as a mate's freedom (ADR-147). Born of a robot arm whose every link
  stated one pin twice.
* **A mate's freedom may state its own line:** a design's connectors are
  attachment frames, and the line a part turns about need not be the
  connector's ``z``: ``Revolute(axis=(0, 0, 1), at=(0, 0, 0))`` as a
  mate's freedom turns the part about that line, stated in numbers in
  the moving part's own frame, while the frames still fix where it rests.
  Each of ``axis`` and ``at`` left out is the moving frame's, so a mate
  that states no line is unchanged (ADR-148).
* **A mate may slide:** a mate's freedom may be a ``Prismatic``,
  ``left_grip = left_finger.origin.on(left_seat, Prismatic(axis=(0, 1, 0), range=(-11, 20)))``,
  which slides the part along the line it states, in the part's own
  frame, by the rules a ``Revolute`` freedom follows: the frames fix
  where it rests, ``at`` and ``range`` are taken the same way, and a
  ``Prismatic`` states its ``axis`` as it does anywhere. The part gets a
  ``Prismatic`` joint, the mate's coordinate is a length, in ``'mm'``
  unless the freedom states a unit, and the slide is published as the
  translation a class-declared ``Prismatic`` publishes (ADR-151). Born
  of a gripper's fingers.
* **A handed design mates per instance:** a mate's freedom may state its
  ``axis`` and its ``range`` each as one function of the assembly that
  states the mate, ``Revolute(axis=lambda node: ..., range=lambda node:
  ...)``, called once with that assembly as it builds the moving part,
  so one class per joint, mounted on either side, states each side's
  line and limits beside the fixed frame that is already a function of
  the side. The result is taken as numbers written there are; ``at``
  stays three numbers (ADR-150). Born of a two-armed robot mirrored
  side to side.
* **A bought part is held by one statement:** a mate may leave its
  freedom out, ``bolted = servo.ears.on(servo_seat)``, for a part that is
  held rather than freed: it places the part at its seat, connector onto
  connector, and gives it no joint and no coordinate, so a servo, a horn
  or a screw is declared in the class of the part that holds it and
  rides with it. The mate is read with ``freedom`` ``None``, is not a
  port, and publishes only operations (ADR-152). Born of a quadruped's
  forty-eight bought parts.
* **Mate coordinates carry mechanical contracts:** a moving mate's range
  may read sibling coordinates through ``Bound`` in its declaring
  assembly. Its name, or a descendant path to it, may be a Bound read, an
  additive ``constrain(range=...)`` target or an explicit turn, slide or
  button selection. Each uses the existing generated child joint, with
  one retained coordinate and the existing document format (ADR-153).
  Born of a calculator's crank and its pawl.
* **An existing joint attached by its frames:**
  ``ones_mount = ones.axle.on(ones_seat, ones.turn)`` places a dial at its
  connector while preserving its original scalar joint, name, order,
  argument scope, limits and bindings. The handle names that same child
  coordinate for relations, formulas, wiring, constraints and controls;
  it adds no coordinate or document format (ADR-154). Born of a
  calculator's seventeen register dials.
* **Frames and mates read back:** ``resolved_frames(node)``, from
  ``machinome.node.frames``, reads a built node's frames as numbers,
  origin, unit ``x``, ``y``, ``z`` and ``rotation()``, the very ones its
  mates compose, and a mate's ``name``, ``moving`` and ``fixed`` ends
  and its freedom are documented reads off the class through
  ``declared_mates``, so a test can hold a machine's connectors to its
  design without restating how a frame resolves.
* **Frames keep explicit direction precision:** frames supplied with
  both ``x`` and ``z`` keep their normalized attachment directions
  without component snapping, and ``resolved_frames`` reads that same
  basis. Omitting either direction keeps the snapped default; final
  mate rotation and joint axis snapping are unchanged.
* **``machinome vet``:** ``machinome vet [reference] [--tests] [--json]``
  checks, statically, that a project stays inside the machinome
  universe, the framework, its kernels and pure computation: it runs no
  command, opens no socket, imports nothing by a computed name, writes
  no file, and every declared source stays under the project root. It
  reads only the project's bytes and the universe declaration shipped
  with the package, which names the framework version it describes, and
  reports one verdict per model, ``pure`` or the findings by path and
  line. The STL, STEP, OpenSCAD and JSCAD adapters now refuse at
  construction a source outside the declaring project (ADR-149). Born of
  the hosts that run a project they did not write.
* **Corrections:** an imported part wrapped by two classes of the same
  name in two modules of one project no longer shares one cached
  artifact; the artifact identity of ``StlNode``, ``StepNode``,
  ``OpenScadNode`` and ``JScadNode`` wrappers includes the defining
  source file relative to the project, so each wrapper's artifact is
  current on its own, and the affected artifacts rebuild once
  (ADR-155). A mate's rest rotation recovered from its matrix no longer
  carries phantom axis components after a pure principal turn, so a
  placement compares equal to itself. Both found while a calculator's
  dials moved onto mates.

Machinome 0.7.0
---------------

Released on 23/Sep/2026

**Source code for machines.** This release continues solid-node 0.6.0
under a new framework name and GitHub organisation. A machine's source
binds its parts, shared dimensions, movement, controls and memory into
one description that can be built, operated and tested.

* **Rename and migration:** distribution/import/command ``machinome``,
  ``[tool.machinome]``, ``MACHINOME_*``, and repository
  ``machinome/machinome``. There are no old import or command
  aliases. New documents use ``machinome-export``; the matching viewer
  still reads historical ``solid-node-export`` documents.
* **Declarative machines:** typed parameters, derived dimensions,
  guards, child declarations, repeated and optional structure, and root
  overrides with ``--set``.
* **Mechanical relationships:** revolute, prismatic, orbit and free
  joints; scalar and multi-coordinate laws; repeated-child broadcasts;
  and relations resolved across the machine tree. ``render()``
  places the structure at rest; ``simulate()`` expresses its pose.
* **Operation through time:** ``Time(loop=...)`` declares a cycle in
  seconds. ``Time.running()`` selects running mechanics, with
  movement and rate requests, crossings, state-dependent laws and
  mechanical stops. Button, turn and slide declarations associate
  on-screen gestures with the parts they operate.
* **Machines with memory:** ``State``, committing relations and
  ``Sim(machine)`` support event-driven requests without a timestep.
  Clocked instructions make one request over one driver; an elapsed
  clock supplies timed events. Stops limit admitted travel, and refused
  requests retain the previous bank.
* **Existing designs and readable parts:** exact STEP leaves, product
  selection and assembly import, plus flat or wrapped SVG markings
  that contribute no solid.
* **Builds and project organisation:** native geometry preparation,
  named models with separate build directories, shared expression
  graphs, content-verified artifact reuse and fresh build processes.
* **Tests:** selectable exact/faceted comparisons, faster interference
  checks, strict simulation-time validation, and correct skip and
  expected-failure accounting, including failure on unexpected success.
* **Exact comparisons fail closed:** an exact common that OCCT reports
  empty while an independent section and zero-tolerance classification
  find a point strictly inside both parts, resolved farther from every
  face than its native tolerance, raises ``ExactCommonInconsistency``
  instead of passing as clearance; a check that cannot complete raises
  ``ExactCommonVerificationError``. Native Common, Fuse and that witness
  Section receive private copies of their operands, so a part compared
  many times is never altered by an earlier comparison.
  ``machinome.exact.intersect_shapes`` shares both rules. No mesh
  verdict or overlap tolerance is introduced.
* **Independent viewer:** ``machinome[viewer]`` selects the separate
  AGPL-3.0-or-later package. Interactive ``develop`` requires it;
  ``--no-web`` remains available. The matching viewer release 0.7.0,
  numbered with the framework, implements API 27 and schemas 1–13,
  including running, clocked, time-driven and source-timed machines, a
  follower held between two moving surfaces, finite profile contact, and
  two Turn controls on one visible part that select different declared
  joints, each with its own named handle.
* **Retained clearance pickup:** explicit running ``Play`` relations
  collect and release a follower through clearance; document schema 9
  carries that contact law to the viewer.
* **Retained time-driven motion:** the running root's ``time`` can be
  an explicit ``drives`` source, with no synthetic driver or startup rate.
  Stops clip individual drive relations while elapsed time continues;
  gates resume without catch-up. Schema 10 and a separate producer corpus
  describe this contract, and the matching viewer executes it. This adds
  no force solver or historical escapement model.
* **Independent mechanics:** the twelve formula helpers move from
  ``machinome.mechanisms`` to ``machinome_mechanics`` in the independent
  0.1.0 package, which adds twelve more and is installed through
  ``machinome[mechanics]``.
* **Installed joint constraints:** an assembly can state
  ``joint_path.constrain(range=(lo, hi))`` on an existing scalar descendant.
  Scoped contributions intersect with its original stops without changing
  the tree, joint placement, retained state or viewer document format.
* **Moving-contact stops:** a constraint that reads a moving coordinate
  blocks the inputs that push at the located contact, so a long request
  stops at its first obstruction rather than at a later open window; a
  landing on a moving threshold follows the parts' relative motion, and
  exact following contact is certified rather than rounded into a false
  departure. No API, tolerance or document change.
* **Source-timed running motion:** a determined source keeps its actual
  motion, stroke, dwell and landing, through ordinary chains and selected
  blocks instead of a straight line between interval endpoints, so a
  calculator's carry no longer changes when later result stations join
  the graph. Range and contact probes follow the same motion as the
  committed bank. Running exports declare document schema 11 and their
  program identity includes the source-timing generation: re-export
  running models for the matching viewer, and restart endpoint-era
  snapshots from the initial state. Posed, looping and clocked schema
  selection is unchanged.
* **A follower between two moving surfaces:** ``Follow(lower=, upper=)``
  is the running law for a retained coordinate that rests freely between
  two independently moving, authored boundaries and is pushed by either
  only on contact, staying where a retreating surface left it. Its
  sources are inputs, held bank coordinates or unbranched affine chains;
  the matching lower and upper ``Bound`` relations on that coordinate
  locate the first contact at which the surfaces become incompatible,
  checking the certified cuts as well as the uniform samples, so a
  narrow inversion between samples is not passed. Unsupported ancestry
  or a contact too narrow to represent is refused, not approximated. A
  running export carrying one declares document schema 12; exports
  without it are unchanged. Born of the Curta Type I's radial
  positioning ball.
* **Finite profile contact:** ``ConvexProfile`` and ``profile_overlap``,
  imported from ``machinome.simulation.profile``, keep authored planar
  convex polygons as data and evaluate pointwise inclusive contact
  without expanding polygon-pair formulas into a symbolic graph. A
  running ``Bound`` can use the numeric 0/1 result inside its existing
  absolute limit expression; its stop sampling and attribution do not
  change, and any other symbolic use is refused. A running export using
  the predicate declares document schema 13; exports without it are
  unchanged. The operation does not certify contact between sampled
  instants or that a profile covers an installed part. Born of the
  Curta Type I's reverser.
* **Inherited controls survive a compatible child replacement:** a
  subclass that keeps an ancestor's controls under the same names, for
  example ``controls = {**Base.controls, 'deploy loop': Turn(...)}``,
  may replace the child those controls name with a subclass-compatible
  declaration at the same path; each such control resolves its part and
  selected joint on the replacement when the machine is compiled, and
  every existing gesture check still applies. An explicit ``controls``
  table still replaces the inherited one rather than merging with it. A
  new control that borrows another class's child, an incompatible
  replacement and a path missing from the effective tree are refused by
  control name. No syntax, document or viewer change. Born of the Curta
  Type I's loop operating trial.
* **Running performance:** repeated expression evaluation reuses each
  immutable graph's order and operations, running bounds and traced
  constraint searches read determined motion paths instead of replaying
  their prefix, and an exact leaf recovers its native shape after its
  OpenSCAD presentation has been assembled. On the Curta Type I an
  ordinary two-second crank turn fell from 72.6 to 27.9 CPU seconds with
  an identical result bank; laws, tolerances and sample counts are
  unchanged. Four further cycles on the same machine, each accepted only
  on bit-identical bound samples and banks: a running bound reuses the
  proven standing values of its previous successful bind on the same
  run, a path reuses its own identical successful first-point bind, the
  two bounds that replay one ``Follow`` prefix share it within a stretch,
  and identical successful law folds are reused within a tick. Numeric
  graph evaluation skips needless argument lists for scalar leaves and
  binary operations, and repeated profile contacts prune provably
  disjoint polygon pairs through a per-attempt index of each placed
  profile, both with bit-identical results. A full crank revolution is
  still not interactive.
* **Installation:** bound ``ocp-gordon`` below 0.3 so build123d 0.10
  remains compatible with the shared OCP 7.8 runtime in a fresh install.
* **Documentation:** the manual is reorganised by reader intent around
  one tutorial machine, a hand-cranked tally counter built from a part
  to a machine with memory, with how-to guides and concept pages; the
  real machines, posed, running and clocked, are shown on machinome.org,
  and the manual builds from Sphinx and the viewer package alone.
* **Printed pieces:** a piece id digests the artifact's oriented
  triangles, not its raw STL bytes, so one solid that OpenSCAD 2021.01
  writes in a different facet order is still one piece. Every piece id
  changes once and cached piece facts are recomputed.
* **Running corrections from the Curta's reverser trial:** a running
  ``move(to=...)`` lands on its exact converted endpoint instead of a
  reconstructed sum one binary64 step past it, so a request to an
  inclusive bound completes rather than reporting a false stop; and a
  running law that fails its numeric domain or evaluates to a non-finite
  value refuses the tick by name, retiring the command and leaving the
  bank, records and pose as they were before it. The viewer carries the
  same two corrections. No document field or version changes.

See :doc:`upgrading` before changing versions. In addition to the rename,
ports moved to ``machinome.motion.ports``, joint frames changed during
the preview, and hosts must update their viewer bundle. Existing
constructor-based models and direct transforms remain supported.

.. toctree::
   :maxdepth: 1

   ../releases/release-0.8
   ../releases/release-0.7

Releases below retain the names used when they were published.

v0.6.0
------

Released on 01/Sep/2026

The release that makes a model a *machine*. Until now a solid-node model
moved as a function of one looping ``$t``; it can now declare named
inputs, be stepped deterministically in Python, and be driven by hand in
the viewer. Alongside that, three new kinds of part — laser-cut sheets,
imported STL meshes, and flexible parts whose shape is a function of
machine state — and an assembly assertion that knows about gravity. The
build and the CLI also got substantially faster on projects large enough
for it to matter. The narrative announcement is at
`docs/releases/release-0.6.md
<https://github.com/LibreSolid/solid-node/blob/main/docs/releases/release-0.6.md>`_.

**Breaking changes**

* **Reinstall required.** ``cadquery`` moves from 2.5 to 2.7 and
  ``build123d`` 0.10 joins it, so the shared ``cadquery-ocp`` binding
  moves from 7.7 to 7.8. The two versions of that large binary wheel
  cannot coexist: upgrade by reinstalling the environment rather than in
  place. No project source changes.
* The published document schema moves from version 1 to version 2 (a
  ``drivers`` table; operation expressions may name qualified driver ids
  as well as ``$t``), and a document containing a flexible part declares
  version 3. The producer emits the lowest version its content needs, and
  the bundled viewer renders versions 1, 2 and 3 — but a 0.5.x viewer has
  no version gate at all, so pointed at a 0.6 document it silently
  renders only the part of the machine it can evaluate. Hosts pinning
  their own copy of the bundle must upgrade it with the framework. The
  declared viewer API version is 5, and this release's viewer refuses an
  unreadable schema version by name.
* ``export_node`` now leaves the node in symbolic time rather than in
  whatever pose the caller left it. ``solid export`` and the build and
  snapshot paths produce byte-identical output; only a host calling
  ``export_node`` itself and reusing the node sees the difference.

**New features**

* **Named drivers.** An assembly declares its inputs as class attributes
  — ``x = Driver(default=0, range=(0, 200), unit='mm')`` — and reads
  them back as attributes. Assigning to one raises and names
  ``set_state``, reading an unbound one raises and names the driver, and
  a declaration that would shadow a node member fails at class-definition
  time. ``time`` is now one driver among several.
* **Instance-qualified driver ids.** Two instances of one class publish
  their same-named driver distinctly — ``set_state(**{'x_axis.motor':
  12.5})`` — with one dotted id used in the document, the simulation and
  instruction targets alike; an unqualifiable tree fails loudly.
* **Domain-typed ports.** ``Port`` with ``RotationalPort``,
  ``TranslationalPort`` and ``SignalPort``: unit-tagged value slots
  re-bound every render, with declared unit conversion and a causal
  ``connect()``.
* **A stepped simulation layer**, ``solid_node.simulation``: ``Driver``
  declarations and ``RampProgram``; ``Instruction`` targets in design
  units plus a duration; ``Sim``, a fixed-``dt`` loop with integer
  ticks, events, deferred ``at(t)`` actions, an ``every(period, fn)``
  cadence, per-tick snapshot binding and trajectory recording; and
  ``ScenarioTest``, one class running under plain pytest and under
  ``solid test`` alike. Integer-typed drivers ramp integer-exactly and
  land on target.
* **A driveable viewer with on-screen controls.** The widget evaluates
  driver expressions and shows one button per instruction and one slider
  (with numeric readout, in design units) per driver declared at the
  focused assembly layer, with a breadcrumb to move focus. Triggers ramp
  client-side over the declared duration, landing exactly on target.
  Only expressions whose free variables changed re-evaluate. Hosts get
  ``drivers()``, ``instructions()``, ``driver(id)``, ``setDriver(id,
  value)``, ``onDriverChange(fn)`` and ``trigger(name)`` on the mount
  handle, and ``driverControls: 'none'`` to suppress the chrome.
* ``Build123dNode``, a fifth leaf adapter backed by build123d — exact
  OCCT geometry, a ``.brep`` beside its STL, no OpenSCAD binary — and
  exact fusion across backends: CadQuery and build123d children fuse
  exactly together.
* **Sheet parts.** ``SheetLeafNode`` with ``Build123dSheetNode`` as its
  first backend: a laser-cut part authored as a 2D ``profile()`` plus a
  declared ``thickness``, writing a nominal kerf-free ``.dxf`` beside
  its STL and BREP under the same freshness guard.
* **Imported meshes.** ``StlNode`` wraps an ``.stl``; a
  non-watertight mesh fails at build (``require_watertight = False``
  admits one knowingly), a multi-body file is selected by ``body`` with
  a per-body inventory on omission, and ``adjust(self, mesh)`` corrects
  the mesh in code. An ``StlNode`` in a fusion routes that fusion
  through the faceted OpenSCAD/CGAL path.
* **Flexible parts.** ``FlexibleNode`` with ``MolejoNode`` as its first
  adapter: a spring, belt, loom or filament whose geometry is a pure
  function of its declared ports' bound values, travelling as a `molejo
  <https://molejo.readthedocs.io>`_ shape spec plus one expression per
  parameter rather than a mesh, evaluated in the browser only on frames
  its inputs changed. Exact geometry from molejo's OCCT evaluator; the
  OpenSCAD path gets per-binding snapshot meshes.
* **Assemblies are checked against gravity.**
  ``assertAssemblySupported`` proves support reachability (every solid,
  dropped along gravity, lands on something that leads to ground) and
  static equilibrium (push-only contact forces balance every solid's
  gravity wrench, force and torque, via one deterministic linear
  program), naming the unbalanced solids on failure. ``ground``,
  ``supports`` and ``stability_margin`` refine it; friction, adhesion
  and dynamics stay out of scope.

**Fixes**

* Artifact freshness no longer goes through floating-point mtimes:
  source times are read as integer nanoseconds and artifacts stamped
  with the exact value read, fixing spurious full rebuilds on
  millisecond-resolution filesystems. Freshness stays exact equality.
* ``manifold3d`` became a conditional dependency of the faceted mesh
  path, so an all-exact project runs its geometric assertions without
  the compiled wheel — including on platforms with no wheel at all.
* ``clear_keyframe()`` joins ``set_keyframe(time)`` as its explicit
  inverse, returning a subtree to symbolic ``$t``.
* The viewer's driver readout holds still under a drag: fixed decimal
  places, fixed-width figures, the unit in its own segment.
* The viewer reads a leading negative term the way it is written. Its
  expression parser took a unary operator's operand to be the whole
  expression beside it, so ``-100.0 + x`` was read ``-(100.0 + x)`` and
  the sign of a driver's coefficient changed. All 265 distinct
  expressions the Metamaquina 2 example publishes now agree between the
  Python producer and the viewer's parser, where one did not.
* The viewer refuses a flexible part's shape spec its bundled evaluator
  cannot read, by name and once at construction, as it already refused
  an unevaluable ``tech``. Such a spec previously escaped as a raw error
  inside the render loop, naming no node.

**Performance**

* The ``solid`` command imports commands, backends and the test
  framework at the point of use rather than all of them on every
  invocation: ``import solid_node.cli`` 3.48 s → 0.002 s, ``solid
  viewer`` 3.79 s → 0.044 s. Nothing became optional and no grammar,
  help, option, exit code or public API changed.
* The source-closure package lookup is indexed rather than rescanned
  per call. On a 567-node project a cold ``load_node`` goes 19.4 s →
  4.8 s and a no-op ``solid build`` 23.4 s → 8.0 s, every published
  artifact identical by SHA-256.
* An artifact whose sources were rewritten but not changed — by a
  clone, branch switch, stash pop or restore — is restamped rather than
  re-derived, on a digest of exactly the tracked sources consulted only
  when mtime equality fails. A 22-part CadQuery project rebuilt after a
  full timestamp rewrite goes 35.70 s → 5.83 s.

**Packaging and documentation**

* solid-node now depends on `molejo <https://pypi.org/project/molejo/>`_
  with its ``brep`` extra, and the bundled viewer on the ``molejo`` npm
  package, both pinned to molejo's minor — a molejo minor carries the
  shape-spec version it implements.
* molejo 0.2 renamed the token a document declares its spec version
  with, from an integer to the ``MAJOR.MINOR`` string of the release
  that minted it. solid-node never writes that field, and molejo 0.2
  reads both the versions this release can publish.
* The user documentation now tells the 0.6 story rather than the 0.3
  one: the entry surface leads with drivers, simulation and the
  driveable viewer, two new tutorials cover driving a machine and
  scenario testing, the guides' stale claims are corrected throughout,
  and `Metamaquina 2 <https://github.com/LibreSolid/Metamaquina2>`_ —
  a real open-hardware printer — joins the V8 engine as a second worked
  example.

v0.5.1
------

Released on 18/Aug/2026

**Fixes**

* The project's ``Homepage`` metadata named a repository URL that returns
  404. It now points at https://github.com/LibreSolid/solid-node.
* The Read the Docs build passed the ``root`` argument that v0.5.0 removed,
  failing every documentation build with
  ``Error loading node: No module named 'root'``. The V8 example export now
  resolves the model from its ``[tool.solid-node]`` manifest.

v0.5.0
------

Released on 17/Aug/2026

**Breaking changes**

* A project declares its model in a ``[tool.solid-node]`` table of its
  ``pyproject.toml``. The project root is discovered from the nearest
  ancestor manifest instead of the current working directory, so commands
  behave identically from a subdirectory.
* Node-scoped commands take an optional reference — ``package.module:Class``,
  a file path, or a path plus class — defaulting to the manifest's model.
  The fixed ``root/__init__.py`` entry point, the directory argument, and the
  ``NODE`` marker are removed.
* ``solid test`` loads every ``TestCase`` in a companion file instead of the
  first. A case beside a multi-node module MUST declare ``node = <Class>``:
  an undeclared one aborts the whole run before any test executes, naming the
  candidates. Single-node modules are unaffected. Cases that were silently
  not running will run — and may fail — for the first time.
* Intersection and connectivity assertions answer exactly when both compared
  nodes are exact, so verdicts change in both directions: real sub-facet
  interference now fails, and nominally exact fits that failed on facet phase
  now pass. ``volume_epsilon`` is ignored, with a warning, on a fully exact
  call.
* A failed build leaves a partially updated model rather than the previous
  complete artifact set; in exchange each artifact is written whole or not at
  all, and a successful build sweeps artifacts its manifest dropped.
* An all-exact ``FusionNode``'s STL bytes change — it is tessellated by OCCT
  rather than compiled through OpenSCAD.
* ``assertNoPairwiseIntersections`` is deprecated in favour of
  ``assertNoSolidInterference`` and warns about its quadratic leaf sweep.

**New features**

* ``solid build [reference]`` builds and publishes once, then exits; an
  unresolvable model exits with status 66 (``MODEL_NOT_FOUND``).
* ``solid develop --no-web`` runs the watch-and-rebuild loop with no viewer,
  and ``--callback URL`` announces each successful publication.
* ``solid snapshot --renderer web`` renders through the packaged viewer in
  headless Chromium with a real alpha channel. Optional install:
  ``pip install "solid-node[web-snapshot]"`` plus ``playwright install
  chromium``. It never falls back to OpenSCAD silently.
* ``solid viewer`` reports the installed viewer bundle's path and API version.
* Exact geometry: a read-only ``exact`` property, ``shape()`` returning the
  node's OCCT solid in its local frame, and a cached ``.brep`` artifact beside
  each exact rigid node's ``.stl``. Exact fusions compose with an OCCT fuse.
* Published documents carry a ``pieces`` inventory keyed on a content
  fingerprint of each built STL, with display name, source files, instance
  count, bounding extents, volume and watertightness, plus a ``piece``
  reference on every rigid node. Additive; no existing field changes meaning.
* New assertions ``assertNoDisconnectedSolids``, ``assertNoSolidInterference``
  and ``assertJoined``. ``solid new`` scaffolds ``test_solid_integrity`` and
  ``test_assembly_integrity``.
* OpenSCAD is required only by the paths that invoke it; an all-exact
  CadQuery project builds, tests and publishes without it, and a path that
  needs it says so instead of raising ``FileNotFoundError``.
* One reusable viewer package serves exports, the Sphinx directive and
  ``solid develop``. ``mount()`` returns a handle with targeted updates,
  assembly metadata, and subtree focus and visibility. Declared viewer API
  version 4; the published bundle, global, auto-mount attribute and query
  parameters are unchanged.
* The development viewer gains inherited colours, lights, a fitted camera and
  the shared animation controls; uncoloured exported models render with the
  normal-based material.
* Every successful build publishes a viewer-readable snapshot including the
  animation cadence (``fps``, ``frames``), so a host can serve the model from
  the build directory with no source import.

**Correctness and reliability**

* A node tracks the project modules its source imports, not just its own file
  (ADR-033), so editing a shared geometry module invalidates the nodes that
  import it. Note that ``assemble()`` may now call ``render()`` zero times,
  and geometry depending on something a static import walk cannot see can look
  current when it is not.
* Concurrent builds of a project are serialized with an advisory ``flock``,
  so a late-finishing build cannot overwrite a newer model. ``solid develop``
  and ``solid test`` release the lock before waiting and before testing.
* Self-contained exports resolve models beside their document rather than at
  the server root, fixing embedded examples served under a subdirectory.
* An explicit reference may name a node class defined in another
  project-local module.
* ``FusionNode`` rejects a non-rigid child instead of silently becoming
  non-rigid and producing no STL.
* A failed targeted viewer update leaves the rendered model on screen and the
  handle usable; geometry just fetched is not refetched.
* ``solid snapshot`` holds the build lock only while preparing its node, and
  defaults ``-o`` from the resolved node.

**Performance**

* The up-to-date check runs before ``render()``: a no-op rebuild of a
  CadQuery-heavy project fell from 19.8 s to 3.2 s.
* The viewer updates in place instead of rebuilding the scene, refetching
  geometry only where ``(model path, mtime)`` moved — an operations-only or
  colour-only edit costs no fetch.
* ``assertNoSolidInterference`` dropped its global volume certificate: 273 ms
  against 2 ms for the spatial path on a 125-solid, 1.02M-triangle assembly.
* Exact ``.brep`` artifacts cache far more cheaply than the STLs beside them
  (4 ms write, 2 ms read, 165 KiB against 112 ms, 9 ms, 469 KiB).

**Packaging, documentation, and maintenance**

* The built viewer bundle ships in source distributions and wheels, so a
  fresh installation has a viewer.
* New optional extra ``solid-node[web-snapshot]``.
* The development loop's per-node HTTP API under ``/node`` and the browser
  modules and dependencies that consumed it are removed. No published
  document, URL or CLI surface changes.
* Scaffolded projects ignore ``__pycache__/`` and ``_build*``; existing
  projects get ``_build*`` in ``.git/info/exclude`` on their next build.
* ``README.rst`` documents OpenSCAD as conditional and covers working on
  solid-node itself; the hosted documentation builds its embedded exports
  from source in CI.

v0.4.0
------

Released on 20/Jul/2026

**Breaking changes**

* The CLI is now command-first: ``solid <command> <node>``.
* ``solid new`` replaces the former solid-seed cloning workflow.

**New features**

* ``solid export`` generates a static viewer manifest and STL exports for a node tree.
* Exported models can be embedded with the standalone viewer widget and the
  ``.. solid-node::`` Sphinx directive.
* Added symbolic degree-aware math functions in ``solid_node.math``.
* Added ``assertBlockedBeyond`` and ``assertFreeWithin`` for kinematic-fit
  tests, plus ``along=`` support for translational perturbations.
* Added the ``NODE`` marker for choosing a node class from modules that define
  more than one.
* Node names now default from their parent attribute name.

**Correctness and reliability**

* Animation rendering is now idempotent across nested assemblies and multiple
  drivers.
* Node identity and artifact keys no longer collide across node classes,
  names, or positional/keyword parameter forms.
* Fixed animated rotation, translation reversal, operation deserialization,
  snapshots, testing-step offsets, and ``--failfast`` behavior.
* ``solid test`` now exits non-zero on failures and reports invalid test paths
  clearly.
* ``solid develop`` remains running after a broken reload and can launch the
  OpenSCAD viewer reliably.
* Improved mesh-intersection checks with configurable volume tolerance.

**Performance**

* Cached base meshes, loaded meshes, and Manifold objects.
* Composed transforms into one world matrix and added AABB broad-phase culling
  before exact intersection tests.

**Packaging, documentation, and maintenance**

* Migrated packaging to ``pyproject.toml`` and ensured compiled frontend assets
  ship in wheels.
* Relicensed the project, with updated attribution and NOTICE.
* Added comprehensive API, CLI, tutorial, testing, embedding, and architecture
  documentation.
* Removed obsolete CI configuration and refreshed contributor guidance.

v0.3.0
------

Released on 14/Jan/2026

**New Features**

* Snapshot CLI command for headless PNG rendering (ADR-019)
* Full CREDITS.md with license attribution for all dependencies

**Architecture Improvements (ADR-018)**

* Removed over-engineered WebSocket IPC (broker.py)
* Moved Git integration to solid-studio (git.py)
* Moved IDE refactoring features to solid-studio (refactor/)
* Removed dead code (exceptions.py, spatial.py)
* Framework is now lean and focused on core CAD functionality

**Maintenance**

* Added license headers to all source files
* Synchronized requirements.txt with setup.py
* Removed unused "unicorn" dependency

v0.2
----

Released on 25/Feb/2025

* JScadNode adapter for JSCAD backend support, plus further work on OpenScadNode
* API reference documentation building on Read the Docs

v0.1
----

After some evolution and several pre-releases (v0.0.1 through v0.0.8),
the project was documented and released as v0.1 with:

* Multi-backend support (SolidPython2, CadQuery, OpenSCAD)
* Web-based 3D viewer with React/Three.js
* Development server with hot-reload
* Test runner for CAD projects
* STL generation and optimization
