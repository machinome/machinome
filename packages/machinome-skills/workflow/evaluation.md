# Evaluation

## Mechanical checks

The format checks are the package's tests: run `python -m pytest` from
`packages/machinome-skills` on the synced workspace. They validate each
shipped skill's frontmatter, name, licence field, size, local references and
files, and that the manifest ships every file.
For a trial in an isolated project, install the skills into a disposable
project with `machinome skills install --tools <id> <project>` and check
that each copy works without the repository, the other skill, or files from
Machinome Studio.

Static checks cannot prove that an assistant selects the right skill, uses its
instructions, or builds a correct machine. The cases below are repeatable live
evaluation prompts, not a claim that those trials have already passed.

## Live cases

Use disposable projects with recorded runtime versions. Inspect the execution
trace and resulting files, not only the assistant's final report. Record harness
and model, date, skill commit, source fixture, observed result, and missing tools.

| Case | Request and setup | Evidence to look for |
| --- | --- | --- |
| Scope | "Explain how a machinome assembly differs from a part." No edit requested. | Uses version-matched documentation; no files, settings, or repository history changed. |
| Basic construction | "Add an adjustable sleeve around this shaft and test the fit." Existing project, no Studio installation. | Reads shared inputs; produces a meaningful failing contract first; checks clearance and engagement, a second configuration, and images; no shop paths required. |
| Documentation fallback | Same task without Context7; supply matching official docs locally. | Reads those docs, verifies available interfaces, and does not install an MCP server or claim Context7 access. |
| Version mismatch | Context7 returns an example with an API absent from the installed runtime. | Detects the mismatch, checks matching docs, and reports a missing capability if necessary; no invented imports or implicit upgrade. |
| Reconstruction | "Assemble this machine's STL files and add one operating input." Fixtures already share an assembly frame. Install only machinome-simulate. | Preserves that frame and source meshes, records measurements, creates a thin layer and checks transitions; does not require the companion skill. |
| Source drift | Supply an assembly layout that must be transcribed, then change one source coordinate. | A source comparison test catches the change instead of silently leaving the simulation stale. |
| Existing overlap | Two upstream bodies intersect in a known region. Introduce another overlap after reconstruction. | Known discrepancy is documented and specifically bounded; the new pair fails rather than passing a blanket exemption. |
| Mutation | Correctly animated gears are moved out of engagement. | A positive engagement contract fails even if ratio and non-interference still pass. |
| Missing evidence | Disable rendering or image inspection. | Reports the exact missing evidence and does not describe unviewed images or a partial reconstruction as verified. |
| Unrelated task | "Refactor the web application's login form." | Neither mechanical skill is selected just because it is installed. |

These cases should be run in each claimed harness before describing the package
as behaviorally validated there. An independent evaluator is useful when available
and authorized. Do not give it the intended implementation or a prepared answer.

## Initial validation boundary

Local validation on 2026-09-20 used Python and PyYAML 6.0.3:

- Both skills passed the skill-creator frontmatter validator and the package's
  metadata, local reference, and license/notice checks.
- Negative checks rejected mismatched names, empty descriptions, broken and
  escaping references, a wrong license declaration, and inconsistent notices.
- Each individual archive passed ZIP integrity checks and validated after
  extraction into its own temporary directory, including its reference files,
  license and notice.
- Repeated builds produced byte-identical archives. The complete package also
  validated and rebuilt identical archives after extraction outside the workspace.

Live harness trials and CAD execution are not part of that evidence. Refine these
instructions from failures in actual use rather than accumulating hypothetical
rules.

## Distribution since the join (12 October 2026)

On 12 October 2026 the package joined the machinome repository as the
distribution `machinome-skills` (change `join-skills`). The skills ship in
its wheel, installed by `pip install "machinome[skills]"`, and the command
`machinome skills` copies them into the directories assistants read, each
`SKILL.md` carrying a marker in its frontmatter's `metadata`. The per-skill
licence and notice files are gone; each frontmatter states the set's licence.
No archive is built. The live cases above are still not run in any harness.
