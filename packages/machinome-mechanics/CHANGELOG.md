# Changelog

## Unreleased — 0.1.0

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
