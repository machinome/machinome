# machinome-mechanics

Mechanical formula helpers for machinome projects, licensed Apache-2.0.
Version 0.1.0 is founded locally and **not published**.

The runtime import dependency goes one way: **mechanics imports machinome**.
The default machinome installation does not require this package. Its optional
`mechanics` extra installs it, but framework code never imports or re-exports
these helpers.
The formulas use `machinome.math` for degree-based numeric computation and
symbolic expressions that machinome's animation paths already understand.

## Install from source

With Python 3.11 or newer, in this checkout:

```sh
python -m pip install .
```

This installs machinome if necessary. The required math operations exist in
machinome 0.6.0. Declarative parameters and the newer motion API are features
of machinome's unreleased development line, not promises about 0.6.0.

The framework's unreleased `mechanics` extra follows its viewer installation
pattern. Once both versions are published:

```sh
python -m pip install 'machinome[mechanics]'
# Or install both optional packages:
python -m pip install 'machinome[viewer,mechanics]'
```

For now, supply both local repositories, using a framework checkout that
contains the new extra:

```sh
python -m pip install -e '/path/to/machinome-framework[mechanics]' -e /path/to/machinome-mechanics
```

The extra selects a package to install; helpers still use the
`machinome_mechanics` import. Released solid-node 0.6.0 has no mechanics extra;
the extra begins with Machinome 0.7.0.

## Use

```python
from machinome_mechanics import meshed_angle, piston_height, screw_travel

assert screw_travel(360, 2) == 2
assert piston_height(0, 15, 60) == 75
assert meshed_angle(0, 12, 24, driver_gap=15) == 172.5
```

The same functions accept symbolic driving values. A motion relation can
call them inside its project's law:

```python
from machinome_mechanics import piston_height

def piston_law(crank, piston):
    radius, length = crank.radius, piston.rod_length
    return lambda angle: piston_height(angle, radius, length)

# On a machinome development version with the motion API:
# crank.turn.drives(piston.rise, law=piston_law)
```

This package supplies formulas. The project supplies dimensions, reference
frames, signs, branch selection and assembly facts; machinome supplies
motion coordinates and relation evaluation.

## Formula families

| Module | Helpers |
| --- | --- |
| `gears` | `meshed_angle`, `driving_angle` |
| `screws` | `screw_travel`, `screw_angle` |
| `cranks` | `crank_pin`, `crank_rod_angle`, `piston_height` |
| `deltas` | `delta_carriage`, `delta_rod` |
| `linkages` | `circle_intersection`, `triangle_angle`, `link_rise` |

All twelve names are exported from `machinome_mechanics`, with family imports
such as `machinome_mechanics.gears` also available.

Angles are degrees. Each family module documents its frame, zero, sign and
originating project conventions; those are part of the API. Read those
docstrings and the [formula specification](openspec/specs/mechanisms/spec.md)
before adapting a law to a different machine. No collision, force or dynamic
simulation is implied by these kinematic formulas.

Numeric and symbolic evaluation share one definition. A general dimensional
class-body formula contract is not provided: degree literals such as 180
and 360 do not carry an angle dimension. Use resolved numeric parameters
inside a law factory, or the framework's `.value` escape hatch for a static
class-body calculation. Unreachable configurations retain the underlying
math behavior: numeric domain errors and symbolic NaN, rather than an
invented valid pose.

## Migration

The functions were extracted from the unreleased `machinome.mechanisms`
package. After installing this package, change imports:

```python
# Previously: from machinome.mechanisms import delta_carriage
from machinome_mechanics import delta_carriage
```

Names, signatures and formulas are preserved. Project migration is separate
from this extraction; no project sources were changed to found this package.
See [provenance and decisions](docs/extraction.md).

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest
python scripts/check-dist
```

The formula suite tests reference values, inverse identities, geometric closure
and numeric/symbolic agreement. Integration tests exercise newer machinome
features when available. The distribution check builds wheel and sdist,
validates their metadata and installs each in a temporary environment outside
the repository. It uses the invoking environment's installed machinome and
uploads nothing.
