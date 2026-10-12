## 1. Red Distribution Contract

- [x] 1.1 Add failing tests for distribution `machinome-mechanics`, import package `machinome_mechanics`, dependency `machinome>=0.7.0` and repository URL.
- [x] 1.2 Add failing tests that formulas use `machinome.math` and no legacy package is installed.

## 2. Package Rename

- [x] 2.1 Rename the source package directory and every current import, package-discovery rule, test and example.
- [x] 2.2 Update metadata, README, changelog, current specs, extraction narrative and distribution check to Machinome names while retaining historical provenance.
- [x] 2.3 Update framework-extra guidance and preserve the one-way dependency boundary.

## 3. Validation And Completion

- [x] 3.1 Run the full numeric, symbolic and integration suite against the renamed framework.
- [x] 3.2 Build wheel and sdist, inspect them, install each outside the repository and execute representative helpers.
- [x] 3.3 Audit former-name references, allowing only classified historical evidence.
- [x] 3.4 Sync specs, archive the change, revalidate and leave the branch clean for integration.
