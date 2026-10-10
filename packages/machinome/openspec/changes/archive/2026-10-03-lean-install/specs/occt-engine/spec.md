## MODIFIED Requirements

### Requirement: The engine imports the kernel and nothing above it

The engine SHALL perform every operation on the OCCT kernel through OCP, with
numpy for arrays. Importing it, and running any of its operations, SHALL NOT
import `cadquery`, `build123d` or `trimesh`. From the framework it SHALL import
only the core's exact engine contract module, for the error types it raises,
and the core's extras module, for the refusal it raises when OCP cannot be
found; never a framework internal such as artifact publication, currency or a
cache.

Before it imports OCP, the engine SHALL check that OCP can be found, without
importing it, and refuse an absent OCP with the `kernel-extras` capability's
refusal naming the exact engine and `pip install "machinome[occt]"`.

The engine SHALL keep no state between calls: every operation is a function of
its arguments, and caching the results is its caller's choice.

#### Scenario: The engine runs without a front end

- **WHEN** a fresh interpreter imports the engine and reads, places, fuses,
  intersects, measures and writes a shape with it
- **THEN** neither `cadquery`, `build123d` nor `trimesh` is among the imported
  modules

#### Scenario: The engine without its kernel refuses by its extra

- **WHEN** `machinome.occt.engine` is imported where `OCP` cannot be found
- **THEN** a `ModuleNotFoundError` is raised whose `name` is `OCP` and whose
  message names the exact engine and `pip install "machinome[occt]"`
