## 0. Order of work

- [x] 0.1 Note that tasks 1–4 were completed in commit `ea1fff6` before this
      change existed, and that section 5 records the specs afterwards

## 1. Public identity

- [x] 1.1 Rename package, plugin, marketplace, and descriptive metadata, including repository URLs
- [x] 1.2 Rename runtime service, agent, session, and temporary-resource identifiers

## 2. Project runtime configuration

- [x] 2.1 Read and write the project runtime table as `[tool.libresolid-studio]` with no fallback
- [x] 2.2 Migrate the workspace catalogue's projects to the new key

## 3. Customer-facing product

- [x] 3.1 Present LibreSolid Studio in the browser document and visible title bar
- [x] 3.2 Rebuild the served frontend so the shipped brand matches
- [x] 3.3 Update automated coverage for public metadata and browser branding

## 4. Repository contract and documentation

- [x] 4.1 Update the operating contract, README, architecture overview, ADRs, design material, and skills
- [x] 4.2 Leave archived changes, archived sprint records, and spike evidence under their original name

## 5. Completion

- [x] 5.1 Extract the delta specifications from the committed baseline so the two agree
- [x] 5.2 Review every residual former-name occurrence and justify or migrate it
- [x] 5.3 Run OpenSpec validation and the automated test suite
