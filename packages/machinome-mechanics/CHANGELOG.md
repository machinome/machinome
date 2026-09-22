# Changelog

All notable changes to Machinome Mechanics.

## 0.1.0 — 22 September 2026

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

- Package `machinome-mechanics`, import `machinome_mechanics`, Apache-2.0,
  depending on `machinome>=0.7.0` and using `machinome.math` as its
  expression provider. The framework's optional `mechanics` extra selects
  it; the framework never imports or re-exports the helpers.
- Twelve of the helpers were extracted from the framework's unreleased
  `machinome.mechanisms` package with their names, signatures and formulas
  preserved; the other twelve were added from the needs of real projects
  during release preparation. No `solid_node_mechanics` compatibility
  package is provided, because no earlier mechanics version was published.
