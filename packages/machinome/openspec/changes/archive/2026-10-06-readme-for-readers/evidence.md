# Evidence: readme-for-readers

Base 5de66e7 (framework main, 6 October 2026), branch readme-squash in
machinome/WTs/readme-squash, workspace venv
(/home/asa/devel/machinome/.venv/bin/python), openspec 1.6.0. Planning
commit af056b7. Authorized end to end by the pilot's requests of
6 October 2026; the planning artifacts were reviewed by the agent, not by
the pilot, before commit 1.

## Red first

The five tests of ReadmeTest run against the original README.rst (1752
words, 297 lines): **7 failed, 11 passed, 762 subtests passed**.
test_the_readme_has_these_sections red (the headings found began
"Machinome", "Version 0.8: a lean core", "Version 0.7 and the new name");
test_the_readme_fits red (1752 words, at most 1500);
test_the_readme_names_no_version red on both version headings and on the
sentence match "Version 0.8"; test_the_readme_example_is_tutorial_source
red ("README.rst shows no Python"); test_the_readme_example_places_parts_by_mates
red ("no Python block of README.rst states a mate").

## The example, compared

docs/tutorial/counter/readme.py was built beside the chapter's
RatioCounter (machinome build readme, machinome build c04-ratio, in a copy
of the tutorial project with the build directory in the scratch
directory). The two viewer.json documents agree in every operation:
handle rotates by crank about (0, 0, 1); units_drum rotates by
(0.1 * crank) then translates to z = 12.0; tens_drum rotates by a tenth of
that then translates to z = 24.0; base has no operation. The three meshes
carry the same content hashes in both builds (Base ...-8ba03b76c773,
Crank ...-3f5fc2f38c14, Drum ...-ed1a79eec5ec), the same sizes and
volumes; both documents declare the one driver crank, range 0 to 3600
degrees, and the one binding (0.1 * crank). The differences: the README's
drums carry no digits marking, and the translation's components are
written 0.0 where the chapter's are 0.

## Green

pytest tests/test_docs_structure.py tests/test_node_root_exports_nothing.py
tests/test_release_records.py tests/test_machinome_identity.py
tests/test_docs_exports.py -p no:cacheprovider: **66 passed, 939 subtests
passed**. README.rst is **1422 words**. pytest tests/test_tutorial_counter.py
-p no:cacheprovider, which builds every declared model of the tutorial
project, the readme model among them, and runs every companion test:
**3 passed in 58.23 s**. The licence pins (LicenceFactTest), the
stale-name pins (KernelExtrasTest) and the root-exports scan hold on the
new text.

## Distribution, rendering, links

python -m build --outdir <scratch>/dist4 . built machinome-0.8.0.tar.gz
and machinome-0.8.0-py3-none-any.whl outside the checkout; twine check on
both: **PASSED**. The sdist carries README.rst and CONTRIBUTING.rst; it has
never carried the tutorial's modules (MANIFEST.in includes *.rst under
docs/, not *.py), so the README links the module on GitHub. docutils
(html5 writer) reports nothing at WARNING level or above for either file.
Every manual URL in the README maps to a page under docs/ (index, why,
start/install, start/first-machine, tutorial/01-part, howto/backends,
concepts/node-tree, concepts/joints, reference/cli, project/changelog,
project/upgrading, project/status), the GitHub link maps to
docs/tutorial/counter/readme.py, and every relative link (LICENSE,
AI-USE.md, CONTRIBUTING.rst, docs/contributor-briefing.md,
docs/adrs/README.md, docs/architecture.md) exists. The README was read
once whole, as the reader.

## Lint

No line of tests/test_docs_structure.py exceeds 89 characters, the CI
flake8 limit; flake8 is not installed in the workspace venv, and the CI
lint job is continue-on-error.

## Records

Spec delta merged into openspec/specs/user-documentation/spec.md as the
requirement *The README describes the package*, the file's last. No ADR:
a README is not architecture. No changelog bullet: what a project gets
from the package does not change. openspec validate readme-for-readers
--strict: valid.
