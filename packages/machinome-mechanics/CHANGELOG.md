# Changelog

## Unreleased — 0.1.0

- Add `belt_pulley_angle` for contact-referenced CW/CCW pulley orientation.

- Add `belt_path_metrics` for closed directed pitch paths and belt stations.

- Add `belt_tangent_points` for directed outer and inner belt contacts.

- Add `pulley_pitch_radius` for GT2, AT3 and fitted linear belt pitches.

- Add `rolling_angle` for unwrapped pulley, idler and drum rotation from travel.

- Add `rolling_travel` for rack, belt and constant-radius drum displacement.

- Add the Sphinx user manual for all twelve helpers, with installation,
  coordinate conventions, numeric/symbolic examples and Machinome motion laws.
  Match the framework's Read the Docs theme and include hosting configuration.
- Move internal extraction, validation and release preparation records to
  `workflow/`; reserve `docs/` for user documentation.

- Rename the distribution from `solid-node-mechanics` to
  `machinome-mechanics` and the import package from `solid_node_mechanics` to
  `machinome_mechanics` for the Machinome 0.7 transition.

- Support opt-in installation through the framework's unreleased
  `machinome[mechanics]` extra; default installation and runtime imports
  remain independent.

- Found the independent Apache-2.0 helper package for machinome projects.
- Extract twelve gear, screw, crank, delta and linkage functions from the
  unreleased machinome.mechanisms package, preserving their signatures,
  conventions and numeric/symbolic behavior.
- Keep `machinome.math` as the expression provider; depend on
  `machinome>=0.7.0`.
- Transfer formula tests and behavioral specs into this repository.
- No project migration, index publication or remote push has occurred.
