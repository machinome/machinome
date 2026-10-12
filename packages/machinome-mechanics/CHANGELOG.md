# Changelog

All notable changes to Machinome Mechanics.

## Unreleased

- The tests recognise a symbolic result by Machinome's own predicate,
  `machinome.expression_graph.symbolic`, instead of by solid2's
  `OpenSCADConstant` class, which Machinome's symbolic values no longer
  derive from on its 0.8 line. No helper changes.
- Machinome Mechanics is part of the Machinome repository,
  <https://github.com/machinome/machinome>, at
  `packages/machinome-mechanics/`, with its history. The helpers are
  imported from `machinome.mechanics` (formerly `machinome_mechanics`), a
  portion of the `machinome` package; names, signatures and formulas are
  unchanged, and no module of the former name is provided. The package is
  licensed as every package of the repository, GPL-2.0-or-later or
  CERN-OHL-S-2.0-or-later, at the recipient's choice, and requires
  Machinome 0.8 or newer. Its manual is part of Machinome's,
  <https://machinome.readthedocs.io>: "Mechanics helpers" under Reference
  and "Use a mechanism formula in a machine" among the how-to guides.
- The tests take their symbolic time from
  `machinome.expression_graph.get_animation_time()` and import
  `AssemblyNode` from `machinome.node.assembly`. The specifications name the
  new import and the manual's address, with no change of behaviour.

## 0.1.0 — 23 September 2026

The first release of Machinome Mechanics, released with Machinome 0.7.0.
It requires Machinome 0.7 or newer and installs with
`pip install 'machinome[mechanics]'`.

### What a project gets

Twenty-four kinematic formulas in nine families, each with one definition
that computes a number for a posed machine and a deferred expression when
its input is a symbolic driver or the timeline, through `machinome.math`.
Every helper states its frame, zero, sign and domain in the manual, with
a runnable example.

- **Gears:** `meshed_angle` and `driving_angle` for an external spur pair
  with tooth registration; `cycloidal_ratio` for a fixed-ring cycloidal
  reducer; `internal_mesh_angle` for a ring, carrier and pinion.
- **Lead screws:** `screw_travel` and `screw_angle`.
- **Slider-cranks:** `crank_pin`, `crank_rod_angle` and `piston_height`.
- **Cam followers:** `harmonic_cam_lift`, a periodic half-cosine rise,
  return and dwell.
- **Indexed advance:** `indexed_advance`, completed turns accumulated
  around a caller-authored within-turn stroke.
- **Linear deltas:** `delta_carriage` and `delta_rod`.
- **Planar linkages:** `circle_intersection`, `triangle_angle`,
  `link_rise`, `two_link_angles` and `four_bar_pose`.
- **Rolling motion:** `rolling_travel` and `rolling_angle`.
- **Belt geometry:** `pulley_pitch_radius`, `belt_tangent_points`,
  `belt_path_metrics` and `belt_pulley_angle`.

A Sphinx manual covers installation, coordinate conventions, a worked
Machinome relation law and the complete reference, in the framework's
Read the Docs theme.

### Identity and provenance

- Package `machinome-mechanics`, import `machinome_mechanics`, depending
  on `machinome>=0.7.0` and using `machinome.math` as its
  expression provider. The framework's optional `mechanics` extra selects
  it; the framework never imports or re-exports the helpers.
- Twelve of the helpers were extracted from the framework's unreleased
  `machinome.mechanisms` package with their names, signatures and formulas
  preserved; the other twelve were added from the needs of real projects
  during release preparation. No `solid_node_mechanics` compatibility
  package is provided, because no earlier mechanics version was published.
