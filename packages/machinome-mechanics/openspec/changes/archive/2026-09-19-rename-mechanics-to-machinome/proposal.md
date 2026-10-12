## Why

The independent mechanics helpers belong to the renamed Machinome ecosystem
and otherwise retain the same ambiguous solid-node identity as the framework.
They are founded but unpublished, so their first public release can use the
final name without a published-package compatibility burden.

## What Changes

- Rename the repository and distribution to `machinome-mechanics`, the Python
  package to `machinome_mechanics`, and its repository URL to
  `github.com/machinome/machinome-mechanics`.
- **BREAKING**: replace imports of `solid_node.math` with `machinome.math` and
  public imports from `solid_node_mechanics` with `machinome_mechanics`; ship
  no legacy alias because version 0.1.0 has not been published.
- Depend on `machinome>=0.7.0` and integrate through the framework's
  `machinome[mechanics]` extra without reversing the dependency direction.
- Update current specs, tests, extraction narrative, README, changelog,
  metadata and distribution checks while preserving the formula APIs,
  conventions and numeric/symbolic parity.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `distribution`: Rename the distribution, import package, framework
  dependency and source repository without changing formula behavior.

## Impact

Packaging, import paths, tests, docs, current OpenSpec baselines, repository
path and remote change. The twelve formulas and their mathematical contracts
do not. No publication or push is authorized.
