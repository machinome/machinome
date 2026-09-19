## Why

The name LibreSolid collides with Tim Berners-Lee's Solid ecosystem and makes
the studio, framework, and repositories look related to a different project.
The product needs one unambiguous Machinome identity before its experimental
studio and related packages are distributed more widely.

## What Changes

- Rename the product to **Machinome Studio**, its distribution and repository
  to `machinome-studio`, and its GitHub home to
  `github.com/machinome/machinome-studio`.
- Define *machinome* as both the source code of a machine and the collective
  body of source code for machines, and describe the Machinome organization as
  the home for machine-source repositories, resources, and the framework.
- **BREAKING**: replace `libresolid-studio` machine-readable product identity,
  project configuration tables, package metadata, resource prefixes, and
  current user-facing references with `machinome-studio` equivalents.
- Rename current workspace references to the framework, viewer, and mechanics
  repositories and their package/import/command surfaces while retaining
  mechanical shop vocabulary where it describes the workflow.
- Update setup, worktree, profile, launcher, runtime, UI, tests, examples,
  architecture, contribution material, and current OpenSpec baselines. Preserve
  archived changes, accepted ADRs, and past release evidence as historical
  records, adding explicit rename context where a current reader needs it.
- Add the studio side of the cross-repository migration record and validation
  against the renamed framework and viewer.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `product-identity`: Change the canonical customer-facing and machine-readable
  identity from LibreSolid Studio / `libresolid-studio` to Machinome Studio /
  `machinome-studio`, and define which historical records retain the old name.

## Impact

This affects package metadata, project configuration, setup scripts, workspace
paths, runtime messages and environment, browser copy, profiles and skills,
tests, current documentation and specs, and repository remotes. It coordinates
with independent changes in `machinome-framework`, `machinome-viewer`, and
`machinome-mechanics`; no push or publication is part of the change.
