# machinome-mechanics

[![CI](https://github.com/machinome/machinome-mechanics/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/machinome/machinome-mechanics/actions/workflows/ci.yml)

Mechanics helpers for the [Machinome framework](https://machinome.readthedocs.io/en/latest/),
licensed Apache-2.0. Calculate gear angles, screw travel, piston positions,
delta carriage heights, cam lifts, belt paths and linkage geometry with the
same formulas for numeric poses and symbolic motion.

Version 0.1.0 was released on 20 September 2026 with Machinome 0.7.0. It
requires Machinome 0.7 or newer.

[User manual](https://machinome-mechanics.readthedocs.io/en/latest/) ·
[Getting started](https://machinome-mechanics.readthedocs.io/en/latest/getting-started.html) ·
[Helper reference](https://machinome-mechanics.readthedocs.io/en/latest/reference/index.html)

The manual source is in [`docs/`](docs/index.rst); to build it locally, follow
[documentation maintenance](workflow/documentation.md).

The runtime import dependency goes one way: **mechanics imports machinome**.
The default machinome installation does not require this package. Its optional
`mechanics` extra installs it, but framework code never imports or re-exports
these helpers. The formulas use `machinome.math` for degree-based numeric
computation and for the symbolic expressions machinome's animation paths
already understand.

## Install

With Python 3.11 or newer, the framework's `mechanics` extra installs both
packages:

```sh
python -m pip install 'machinome[mechanics]'
# Or with the browser viewer as well:
python -m pip install 'machinome[viewer,mechanics]'
```

If Machinome is already installed, `pip install machinome-mechanics` adds the
helpers. The extra selects a package to install; helpers are imported from
`machinome_mechanics`. solid-node 0.6.0, the framework's earlier name, has no
mechanics extra and does not satisfy this package's dependency.

To work on the helpers themselves, install this checkout beside a framework
checkout:

```sh
python -m pip install -e '/path/to/machinome[mechanics]' -e /path/to/machinome-mechanics
```

## Use

```python
from machinome_mechanics import meshed_angle, piston_height, screw_travel

assert screw_travel(360, 2) == 2
assert piston_height(0, 15, 60) == 75
assert meshed_angle(0, 12, 24, driver_gap=15) == 172.5
```

The same functions accept symbolic driving values. A relation law can
call them inside its project's law:

```python
from machinome_mechanics import piston_height

def piston_law(crank, piston):
    radius, length = crank.radius, piston.rod_length
    return lambda angle: piston_height(angle, radius, length)

crank.turn.drives(piston.rise, law=piston_law)
```

This package supplies formulas. The project supplies dimensions, reference
frames, signs, branch selection and assembly facts; machinome supplies
motion coordinates and relation evaluation.

## Formula families

| Module | Helpers |
| --- | --- |
| `gears` | `meshed_angle`, `driving_angle`, `cycloidal_ratio`, `internal_mesh_angle` |
| `screws` | `screw_travel`, `screw_angle` |
| `cranks` | `crank_pin`, `crank_rod_angle`, `piston_height` |
| `cams` | `harmonic_cam_lift` |
| `indexing` | `indexed_advance` |
| `deltas` | `delta_carriage`, `delta_rod` |
| `linkages` | `circle_intersection`, `triangle_angle`, `link_rise`, `two_link_angles`, `four_bar_pose` |
| `rolling` | `rolling_travel`, `rolling_angle` |
| `belts` | `pulley_pitch_radius`, `belt_tangent_points`, `belt_path_metrics`, `belt_pulley_angle` |

All twenty-four names are exported from `machinome_mechanics`, with family
imports such as `machinome_mechanics.gears` also available.

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

Before 0.7 the framework's development versions carried twelve of these
functions as `machinome.mechanisms`. After installing this package, change
imports:

```python
# Previously: from machinome.mechanisms import delta_carriage
from machinome_mechanics import delta_carriage
```

Names, signatures and formulas are preserved. See
[provenance and decisions](workflow/extraction.md) and the framework's
[upgrading guide](https://machinome.readthedocs.io/en/latest/project/upgrading.html).

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest
python scripts/check-dist
```

The formula suite tests reference values, inverse identities, geometric closure
and numeric/symbolic agreement. Integration tests exercise the framework's
relation and declaration APIs. The distribution check builds wheel and sdist,
validates their metadata and installs each in a temporary environment outside
the repository. It uses the invoking environment's installed machinome and
uploads nothing.

User documentation belongs in `docs/`; internal development and release records
belong in [`workflow/`](workflow/README.md). See
[documentation maintenance](workflow/documentation.md) for HTML builds, example
checks and the Read the Docs setup, and [release 0.1](workflow/release-0.1.md)
for how the release was checked.
