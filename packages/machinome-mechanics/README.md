# machinome-mechanics

Mechanics helpers for the [Machinome framework](https://machinome.readthedocs.io/en/latest/),
licensed Apache-2.0. Calculate gear angles, screw travel, piston positions,
delta carriage heights and linkage geometry with the same formulas for numeric
poses and symbolic motion.
Version 0.1.0 is founded locally and **not published**.

[User manual](https://machinome-mechanics.readthedocs.io/en/latest/) ·
[Getting started](https://machinome-mechanics.readthedocs.io/en/latest/getting-started.html) ·
[Helper reference](https://machinome-mechanics.readthedocs.io/en/latest/reference/index.html)

The manual source is in [`docs/`](docs/index.rst). To build it locally before
hosting is enabled, follow [documentation maintenance](workflow/documentation.md).

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

This requires machinome 0.7.0 or newer. The formulas also passed a historical
check against solid-node 0.6.0 math, but that differently named package does
not satisfy this distribution's dependency. Publication of the Machinome
release set is still pending; see [release preparation](workflow/release-0.1.md).

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
python -m pip install -e '/path/to/machinome[mechanics]' -e /path/to/machinome-mechanics
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
| `rolling` | `rolling_travel`, `rolling_angle` |
| `belts` | `pulley_pitch_radius`, `belt_tangent_points`, `belt_path_metrics`, `belt_pulley_angle` |

All listed names are exported from `machinome_mechanics`, with family imports
such as `machinome_mechanics.gears` also available.

Angles are degrees. The [user reference](https://machinome-mechanics.readthedocs.io/en/latest/reference/index.html)
documents every helper's parameters, return value, frame, zero, sign and domain,
with runnable examples. Read the [conventions](https://machinome-mechanics.readthedocs.io/en/latest/conventions.html)
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
See [provenance and decisions](workflow/extraction.md).

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

User documentation belongs in `docs/`; internal development and release records
belong in [`workflow/`](workflow/README.md). See
[documentation maintenance](workflow/documentation.md) for HTML builds, example
checks and the one-time Read the Docs setup.
