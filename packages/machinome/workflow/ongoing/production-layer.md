# Production: independent, nested assets over a model

**Status:** Design direction locked by the pilot on 2026-10-03, including
nested subproductions and lazy access with no public `evaluate()` step.
This is the pre-spec working record of that agreement, not a ratified OpenSpec
specification or a published API promise. The first bundled implementation is
recorded by the production-layer cycle below. Baseline specs and accepted ADRs
remain authoritative; the original examples below retain illustrative units
and catalogue spellings that are not the implemented API.

**Cycle update, 2026-10-04:** [production-layer](../../openspec/changes/archive/2026-10-04-production-layer/proposal.md)
now records the bundled `machinome.production` direction and a narrow public
model-reading facade, not an independent distribution. The cycle is on
`v0.8-production` at base `e570068287c56e84f6ccb4ed73f0bae7bed5a07c`, the
completed `v0.8-scad-presentation` HEAD. The pilot explicitly directed the
rebase from the original `63c887ed69ebccd2d5a78af4dc75ebeee1acdab1` before
implementation. The original dirty-source exception left its unrelated
untracked load-projects report untouched.
Integration is not authorized. The pilot's instruction to orchestrate proposal,
apply and independent adversarial reviews authorizes the complete in-scope
cycle. The pilot explicitly confirmed that authority after the orchestrator
incorrectly introduced a second ratification pause. Reviewed planning may
proceed to implementation without another approval.

The cycle implements independent, nested, lazy production assets and a public
rest-only consumption facade, with separate Curta3x and Studio API-skill work.
Its [implementation review](../../openspec/changes/archive/2026-10-04-production-layer/implementation-review.md)
and [evidence](../../openspec/changes/archive/2026-10-04-production-layer/evidence.md)
record validation and exact content identities. It is development work, not a
release or an integrated branch. This note remains in `ongoing/` because the
broader intrinsic-requirement declaration and illustrative unit vocabulary
were not taken up. CLI discovery, individual repeat-member selection and
profile inheritance remain outside this cycle, not promised follow-up work.

Only Curta-Type-I-3x supplies current Curta evidence. Curta2x is future work,
not an implemented second model, a shared-catalogue demonstration or scope.
The actual 3x operating root is `simulation.mechanistic:MechanisticCurta`;
its clearing-loop mounting is simulation-only and whole-machine geometry
acceptance is open. Production acceptance is a real project-owned partial
slice with attributed source BOM/instructions and explicit reconciliation
gaps, not a fabrication-ready root. Two profiles over this same 3x instance
are controlled regressions, not author-approved workshop alternatives.
The author's one retaining spring is represented by five geometric patches;
terminal coverage cannot certify finished-part completeness. Fifteen carry
springs are made from music wire and cannot be labelled purchased finished
springs merely because the author lists them on a nonprinted sheet.

The proposal resolves explicit unit suffixes, direct-binding provenance,
tuple references for named siblings, deterministic recipe grouping, lazy
geometry demand and draft bundle contracts. Cut uses the existing exact-sheet
representative fixture with ADR-053's historical metamaquina-rebuild origin;
the live Metamaquina2 ScadPart is not silently migrated or claimed to supply
nominal DXF. The new API's exact proposed modules are in the change design;
the illustrative units/catalogue spellings below are not current APIs.

This note supersedes the production sketch and the part-versus-production
ownership question in [the 0.8 roadmap](roadmap-0.8.md). It keeps the
roadmap's typed declarations, model references, shared catalogues, and
maker instructions. It refines the BOM boundary and the meaning of mass,
and records the pilot's subsequent decisions about composition and laziness.

## The governing idea

Production is like a video: there is a model, and a project can build as
many independent production assets over it as it needs. Each asset owns
its choices, instructions, supporting files, and generated outputs.

The model has no current production. It does not import, register, or
select its profiles. Adding a profile requires no model edit. Several
profiles can bind the same model instance concurrently without changing
its geometry, parameters, intrinsic requirements, or simulation behavior.

The dependency points from production to model. Production consumes the
model's declarations, occurrences, intrinsic requirements, and geometry
artifacts. It owns its production document and outputs. A profile can use
another profile for a submodel, just as a machine uses subassemblies.

## Evidence and precedent

- `projects/Calculators/Curta-Type-I-3x` is the originating production
  example. Its `simulation/standard/parts.py` imports both fasteners and
  printable components from STEP. Geometry provenance alone therefore
  cannot decide whether something is purchased or made.
- The author's [Curta BOM](https://docs.google.com/spreadsheets/d/16EJePozXW-uC6UFISzyT2eMk7c8wh6v-EP5L1U8fzfM/edit?usp=sharing),
  inspected on 2026-10-03, specifies differing infill percentages, including
  changes with height within one part. It also describes a printed pin
  screw that is subsequently filed and threaded. A process label and solid
  volume alone do not describe the finished part or its mass.
- That project's `Mods/Metal Main Shaft/README.md` describes purchasing
  stock, cutting, drilling, deburring, and reaming during assembly. It is
  evidence for instructions and distinct stock requirements. The mod also
  changes geometry; it is not evidence that every production alternative
  fits an unchanged model.
- The roadmap's Curta2x is future work, not current evidence. The pilot
  separately requires multiple productions over the same actual 3x model.
- Videomaker's `docs/declaring-a-movie.md`, in the workspace's independent
  `videomaker/` repository, provides the asset precedent: project-owned
  declarations reference model parts, and referenced files resolve relative
  to the declaring source file.
- The pilot identified the authoring problem with a flat production class:
  a top-level machine should delegate submodels rather than repeat deeply
  qualified part references for every internal component.

The actuator, gearbox, drive, and machine names used below are illustrative
authoring examples, not additional empirical projects or implemented APIs.

## The public shape

The agreed concepts have these responsibilities:

| Concept | Question it answers |
| --- | --- |
| `Production[Model]` | How is this model produced under this profile? |
| `Item(target, recipe)` | Which model occurrences are units the maker obtains or manufactures? |
| `Printed`, `Cut`, `Sourced` | How is an item primarily obtained? |
| A bound child `Production` | Which profile owns production of this submodel? |
| `Step` | What work does the maker perform on the referenced items or subassemblies? |
| `Material` and stock values such as `Sheet` | What substance and starting stock are chosen? |
| `Standard`, `Product`, `Offer` | What specification, manufacturer's component, and supplier listing are involved? |
| `MeasuredMass`, `SolidMass` | What is the mass evidence or calculation assumption? |

Names are imported from their defining modules. The
`machinome.production` package root exports no names. A declaration's type
and its explicit target give it behavior; its attribute name belongs to
the author. No dispatch recognizes a node by a class-name string, following
[ADR-166](../../docs/adrs/NODE/ADR-166-the-core-recognises-no-node-type-by-the-spelling-of-its-class-name.md).

```python
from machinome.production.profile import Production
from machinome.production.item import Item
from machinome.production.process import Printed, Cut, Sourced
from machinome.production.instruction import Step, Markdown

from models.actuator import Actuator
from production.catalogue import (
    PLA, PETG, ACRYLIC_3MM, ALUMINIUM_3MM, M4X12, LOCAL_M4X12,
)


class Home(Production[Actuator]):
    enclosure = Item(Actuator.housing, Printed(PLA))
    panels = Item(Actuator.sides, Cut(ACRYLIC_3MM))
    fasteners = Item(Actuator.screws, Sourced(M4X12))

    finish = Step(enclosure, instructions=Markdown("finish-housing.md"))
    assemble = Step(
        enclosure, panels, fasteners,
        instructions=Markdown("assembly.md"),
    )


class Workshop(Production[Actuator]):
    enclosure = Item(Actuator.housing, Printed(PETG))
    panels = Item(Actuator.sides, Cut(ALUMINIUM_3MM))
    fasteners = Item(Actuator.screws, Sourced(M4X12, offer=LOCAL_M4X12))

    assemble = Step(
        enclosure, panels, fasteners,
        instructions=Markdown("assembly.md"),
    )
```

These profiles would live in separate modules with their own instruction
files. Renaming `enclosure` does not change its target: `Actuator.housing`
does the binding. A catalogue is ordinary shared project code. Defining a
second profile does not add a mode or a switch to the model.

## Composition and delegation

A production field either assigns an item's recipe or delegates a
submodel to another production. Profiles can nest to the depth the author
finds useful. They need not mirror every grouping in the model tree.

```python
class GearboxWorkshop(Production[Gearbox]):
    enclosure = Item(Gearbox.housing, Printed(PETG))
    bearings = Item(Gearbox.bearings, Sourced(BEARING_608))
    gears = Item(Gearbox.gears, Printed(NYLON))

    assemble = Step(
        enclosure, bearings, gears,
        instructions=Markdown("assemble-gearbox.md"),
    )


class DriveWorkshop(Production[Drive]):
    transmission = GearboxWorkshop(Drive.gearbox)
    motor = Item(Drive.motor, Sourced(MOTOR_PRODUCT))

    couple = Step(
        transmission, motor,
        instructions=Markdown("couple-motor.md"),
    )


class MachineWorkshop(Production[Machine]):
    chassis = Item(Machine.frame, Cut(FRAME_STOCK))
    left = DriveWorkshop(Machine.left_drive)
    right = DriveWorkshop(Machine.right_drive)

    install = Step(
        chassis, left, right,
        instructions=Markdown("install-drives.md"),
    )
```

The constructor accepts a declaration reference inside a profile and a
concrete model instance when used by a caller. A declaration binding is
resolved in its enclosing production's model context.

- `DriveWorkshop` knows only `Drive`. It can produce the left drive, the
  right drive, a drive in another machine, or a standalone drive.
- A child binds the actual existing submodel with its resolved parameters.
  It does not construct a fresh `Drive()` or `Gearbox()` with default values.
- Reusing a profile definition creates independent bindings. Left and
  right retain their own occurrences, quantities, findings, and outputs.
- Delegation transfers coverage of that subtree. A parent assignment
  reaching into the delegated subtree is an overlap error. Declaration
  order never decides which assignment wins.
- Missing assignments inside a child remain findings for that child and
  for the complete production. Delegation alone does not certify coverage.
- A subproduction is an organizational and assembly boundary, not an
  additional thing to purchase. Its items contribute to the BOM exactly
  once; a drive subtotal does not add another physical item to its parts.
- A parent `Step` can reference a child production to mean its assembled
  submodel. Internal assembly instructions belong to the child; installation
  instructions belong to the parent. Referencing it in a step adds no items.

The output preserves the hierarchy and supports a BOM for any subtree as
well as a consolidated whole-machine BOM. Consolidated quantities retain
references to their contributing occurrences.

Buying a whole assembly is another profile at the same boundary:

```python
class MachineWithPurchasedDrives(Production[Machine]):
    chassis = Item(Machine.frame, Cut(FRAME_STOCK))
    left = Item(Machine.left_drive, Sourced(DRIVE_PRODUCT))
    right = Item(Machine.right_drive, Sourced(DRIVE_PRODUCT))

    install = Step(
        chassis, left, right,
        instructions=Markdown("install-drives.md"),
    )
```

Here each drive is one purchased item covering its modelled internals.
There is no simultaneous subproduction of those internals. The model can
still show and simulate them.

## Items, coverage, and BOM identity

An `Item` declares one unit handled by the maker for each selected model
occurrence. A reference to a declared repetition selects its occurrences;
the quantity comes from the bound model, not a copied count in the profile.
A flexible spring is an item regardless of its current deformation or
whether the rigid-piece inventory has an entry for it.

Purchased assemblies may cover multiple model components. A manufactured
item must resolve to geometry its process can consume: selecting an
arbitrary assembly does not automatically fuse it into one printable solid.
The production boundary must also respect the model's existing distinction
between a physical piece and geometry used to construct that piece.

Geometry identity remains the contract of the
[printed-piece inventory](../../openspec/specs/printed-pieces/spec.md).
Production identity answers an additional question. Identical geometry
with different materials or recipes belongs on separate manufacturing
lines. Different meshes representing the same purchased product do not
alone require different purchasing lines. Compatible resolved items may
combine quantities, keeping every occurrence traceable. A subproduction's
grouping does not prevent whole-machine consolidation.

The initial interface uses explicit assignments. It does not infer a
completed production from STEP provenance, a CAD adapter type, a standard
designation, or sheet thickness. Intrinsic geometry and component
requirements stay with the model; the profile owns manufacturing and
purchasing choices. This supersedes the initial idea of automatic `Cut`
and `Sourced` defaults on node bases.

Coverage and consistency checks include:

- A target must belong to the bound model and have a compatible type.
- Every physical component is covered once, or reported as unassigned.
- Competing item assignments, overlapping purchased boundaries, and
  overlaps with delegated subproductions are errors.
- Stock must agree with relevant model dimensions, including sheet
  thickness. A production choice never silently changes model geometry.
- A selected component must satisfy intrinsic requirements the model
  actually declares; conflicting identities are errors.

An incomplete profile can supply a draft BOM with explicit findings.
Production completeness does not affect whether the model can render or
simulate. Unknown mass is separate from missing production coverage.

## Materials, stock, standards, products, and offers

`Material` describes a substance. Density is optional and carries explicit
units when known. A stock value describes the chosen starting form:

```python
ACRYLIC = Material("Acrylic")
ACRYLIC_3MM = Sheet(ACRYLIC, thickness=3 * mm)
```

The unit expression illustrates dimensioned values; its defining module
and relationship to existing parameter declarations remain implementation
design work. It is not the current `Length` parameter API.

Finished-part counts and raw-stock requirements remain distinct. Four cut
panels mean four finished parts. The number of sheets to purchase remains
unknown until an explicit allocation or stock layout supplies it. The same
distinction applies to purchased rod and finished shafts.

Sourcing separates three identities:

```python
M4X12 = Standard("ISO 4762", designation="M4x12", grade="8.8")

SCREW_PRODUCT = Product(
    manufacturer="Example manufacturer",
    part_number="CAP-M4-12-88",
    conforms_to=(M4X12,),
)

LOCAL_M4X12 = Offer(
    product=SCREW_PRODUCT,
    supplier="Local fastener shop",
    sku="12345",
)
```

This is illustrative catalogue data. `Standard` states a specification,
`Product` identifies a manufacturer's component, and `Offer` identifies
a supplier listing for that product. `conforms_to` is an explicit
catalogue assertion, not independently verified certification. Strings
identify things; their wording triggers no hidden interpretation or lookup.

`Sourced(M4X12)` can describe a complete maker's BOM requirement without
choosing a vendor. An exact supplier shopping list additionally needs an
offer. A supplier name alone is not a product identity.

`Standard` and `Product` belong to neutral vocabulary outside
`machinome.production`, so a model can declare an intrinsic requirement
without importing production. `Offer` belongs to production. The exact
neutral module paths and model declaration spelling remain to be designed;
the direction of dependency is settled.

## Instructions and supporting files

`Printed`, `Cut`, and `Sourced` identify primary acquisition. Subsequent
work and assembly are expressed by ordered `Step` declarations:

```python
pin = Item(Curta.crank.pin, Printed(PLA))
thread_pin = Step(pin, instructions=Markdown("file-and-thread-pin.md"))
```

Steps appear in declaration order and reference items or subproductions
directly. Their text can describe printing parameters, varying infill,
orientation, drilling, finishing, tooling, and assembly. These instructions
are maker-authored work, not automatically executed CAD or CAM operations.
Typed process settings are introduced when a named consumer needs to
validate or export them; a universal operation vocabulary is not a
prerequisite for a useful profile.

Paths resolve relative to the source file declaring them. Reusing a
subproduction therefore keeps its own instructions and supporting files.
Parent and child instructions retain their scope in the output.

## Mass with an explicit basis

Mass is unknown by default. A profile may supply evidence or request a
calculation explicitly:

```python
enclosure = Item(
    Actuator.housing,
    Printed(PLA),
    mass=MeasuredMass(37.2 * g, evidence="measurements/housing.md"),
)

panels = Item(
    Actuator.sides,
    Cut(ALUMINIUM_3MM),
    mass=SolidMass(),
)
```

The measurement is an illustrative value per selected occurrence.
`SolidMass()` requests density times valid geometric volume under a
homogeneous-solid assumption. The result retains that basis. Missing
density or invalid volume yields unknown mass rather than a fabricated
number. Unit conversion is necessary because the existing inventory's
volume is in cubic millimetres.

Printed infill is not implied by `SolidMass()`. The Curta evidence rules
out treating enclosed model volume as actual printed material volume.
Totals and subproduction subtotals must preserve incomplete mass coverage;
unknown items are not silently zero-weight items.

Analysis may explicitly consume a production's mass evidence. Binding a
profile never silently changes a simulation or the support assertion.
Total mass alone does not establish a centre of mass. The existing
[support-equilibrium decision](../../docs/adrs/TEST-FRAMEWORK/ADR-049-static-equilibrium-as-lp-feasibility.md)
continues to describe the implemented uniform-unit-density behavior until
a separately specified integration changes it.

## Lazy access: no public evaluation lifecycle

The bound production is the usable asset. There is no public `evaluate()`
step and no second public evaluated-plan object that a caller must create.

```python
machine = Machine()
production = MachineWorkshop(machine)

production.bom
production.left.bom
production.stock
production.steps
production.mass
production.findings

production.export("_build/production/workshop")

purchased = MachineWithPurchasedDrives(machine)
purchased.bom
purchased.export("_build/production/purchased")
```

Construction binds. Each consumer resolves the facts it needs and later
consumers reuse valid results. Nested productions expose the same access
pattern. Parent and child share the bound model and coherent cached facts.

- Invalid declarations fail when declared; incompatible model types fail
  when bound. Checks needing occurrences or geometry run when that work
  is required, rather than forcing full preparation at construction.
- Occurrence traversal, geometry, and mass work happen on demand. Reading
  one result does not automatically request every other result.
- `export()` resolves and validates its required inputs automatically.
  The caller never has to remember an earlier evaluation call.
- Reuse must preserve one coherent model/profile generation. Changed
  sources or artifacts cannot silently combine old and new facts. The
  cache mechanism is internal and adds no author-facing lifecycle step.

Production output records the model identity, bound parameters, consumed
artifact identities, profile inputs, and referenced instruction files.
The output retains nested structure, occurrence traceability, and findings.
Export destination and supporting files belong to the selected asset;
creating a bundle does not select a global production or publish it.

An illustrative project layout is:

```text
models/actuator.py
videos/assembly/...
production/
    catalogue.py
    home/profile.py
    home/assembly.md
    home/finish-housing.md
    workshop/profile.py
    workshop/assembly.md
_build/production/
    home/...
    workshop/...
```

## Implementation follow-through

The following are settled direction, not questions to reopen during
implementation: independent assets; `Production[Model]`; reference-based
`Item` bindings; nested delegation; one coverage owner per occurrence;
independent reuse; assembly instructions at the owning level; explicit
mass assumptions; and lazy access without `evaluate()`.

Details not settled by this conversation include the exact neutral
specification and units modules, selection of individual members of a
repetition, profile inheritance/replacement semantics, serialized document
schema and version, CLI selection, precise diagnostic/result types, draft
export policy, and cache implementation. They are not additional approved
features. Resolve the details needed by the first empirical implementation
under its OpenSpec cycle without changing the locked direction silently.

Implementation evidence should demonstrate the agreed boundaries: two
profiles over one unchanged model; independent reuse of one subproduction
for differently parameterized children; nested missing/overlap findings;
correct repeated quantities and consolidation without double counting;
a purchased assembly replacing delegation; flexible items in the BOM;
stock consistency; unknown versus measured/estimated mass; local instruction
paths; and child/root lazy access agreeing without an explicit evaluation
call. The Curta's actual BOM and instructions supply the first project
acceptance evidence. This note creates no implementation or release claim.
