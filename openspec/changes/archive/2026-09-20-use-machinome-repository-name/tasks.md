## 1. Correct source identity

- [x] 1.1 Change the existing homepage assertion to machinome/machinome and record its failure against unchanged metadata.
- [x] 1.2 Update package metadata and current documentation/source references, preserving historical records and runtime/version contracts.
- [x] 1.3 Run identity and release/docs-focused checks and record results.

## 2. Verify release artifacts

- [x] 2.1 Build a new explicit 0.7.0 wheel/sdist set and check metadata, README and strict distribution validation.
- [x] 2.2 Coordinate viewer/mechanics current README corrections in their owning repositories and rebuild affected companion artifacts at their existing versions.
- [x] 2.3 Install the corrected combined wheel set and source distribution set outside the checkouts, run the retained release smoke and dependency checks, and record hashes.
- [x] 2.4 Rebuild the current manual and inspect source links; record any environmental limits without reusing stale validation claims.

## 3. Complete the repository change

- [x] 3.1 Synchronize the identity delta, update current architecture/release handoff and validate OpenSpec.
- [x] 3.2 Archive the completed change and create the implementation commit with the complete test/artifact evidence.

## 4. Authorized local rollout after integration

Fast-forward into framework main after rechecking the selected base. Coordinate the
shop-owned folder move, refresh origin to the renamed GitHub repository and verify
the final import/artifact paths and hashes. Record final content commit IDs in local
handoff evidence where needed. Do not push, tag or publish. Keep previous release
artifacts distinguishable from the newly verified release set.

