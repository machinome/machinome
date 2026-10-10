# vet-the-project: execution index

- **Note:** `vet.md` (this directory), the design settled with the pilot on
  2026-09-26 and revised the same day with the reads decision.
- **OpenSpec change:** `openspec/changes/archive/2026-09-26-vet-the-project/`
  (proposal, design with its Decisions section, delta specs, tasks,
  evidence with every red and green run and the read-only catalogue run).
- **ADR:** `docs/adrs/BUILD/ADR-149-vet-checks-a-project-against-a-versioned-universe.md`.
- **Worktree and branch:** `machinome/WTs/vet-the-project`, branch
  `vet-the-project`, base d791eaa (main). Planning commit 669ee02
  (amended once after review with the bound-name and import-step
  rulings); the implementation commit is the one that follows it on the
  branch.
- **Tests:** base 3816 passed; final 3920 passed, 4 skipped, 2575
  subtests, one run, green.
- **Catalogue (read only, 2026-09-26):** 24 project roots vetted; after
  the review closure 15 pure and 9 not. Findings: the OpenSCAD echo
  probes (Metamaquina2, snappy-reprap), fetch and preparation tooling
  inside `simulation/` (openvmp, Internal-Cycloidal-Actuator, Curta,
  OpenCycloid), the clocks' shared library importing
  `cadquery.exporters` (all 49 models), YouCanBuildDog's model importing
  its STEP-splitting tool, fender-bender's `sys.path`.
- **Left for other repositories:** the studio's
  `shop-skills/machinome-api/SKILL.md` gains `machinome vet` and source
  containment; machinome.org intake and the studio floor adopt vet as
  their gates.
