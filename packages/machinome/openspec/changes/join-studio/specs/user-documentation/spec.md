## ADDED Requirements

### Requirement: The studio is documented in the manual

The manual SHALL document the studio by reader intent: three how-to guides,
"Open a project in the studio" (what it needs, `pip install
"machinome[studio]"`, `playwright install chromium`, `machinome studio
--projects-dir PATH`, the configuration file, then opening or creating a
project from the hub), "Work in a project's workspace" and "Choose and steer
the studio's agents" (the profiles, the per-agent runtimes, the separate Codex
login); and a reference section, "Studio", holding what the studio is and
runs against with its limits, the studio command (its options, the
configuration file, the order in which option, environment, file and default
apply, the module forms, the exit statuses), the project configuration, the
profiles and troubleshooting. The CLI reference SHALL hold a section
`machinome studio` and SHALL NOT say the studio is yet to add its command.
The installation page SHALL name the `studio` extra with its prerequisites
(the OpenSpec CLI, a logged-in agent backend, Chromium as a second step) and
the distribution `machinome-studio` among the packages of the set under the
set's licence. The status page SHALL state the studio's experimental standing
and, until the set's next release is published, that no index serves it.
Every page SHALL spell the command `machinome studio` and the module forms at
`machinome.studio`; none SHALL show `machinome-studio` as a command, `python -m
floor`, `scripts/setup`, a clone of the studio's former repository or a
project of the catalogue as the way to run the studio. The studio's facts the
pages state (the viewer API it requires, the Claude and Codex models and
efforts, the qualified Codex version, the build volume) SHALL be release facts
of the manual's configuration, held to the studio's source by a test, and the
manual SHALL build with warnings as errors from its own requirements file.

#### Scenario: A reader opens the studio from the manual

- **WHEN** a reader follows "Open a project in the studio"
- **THEN** they install with `pip install "machinome[studio]"` and `playwright
  install chromium`, start the hub with `machinome studio --projects-dir
  PATH`, and open or create a project in the browser, without cloning a
  repository or running a setup script

#### Scenario: The former launcher is gone from the pages

- **WHEN** the manual's pages are searched for `machinome-studio
  --projects-dir`, `python -m floor` or the studio's former repository
- **THEN** none is found outside the changelog's line that names the former
  command, and the documentation test fails naming a page that holds one

#### Scenario: A stated fact drifts from the studio's source

- **WHEN** the studio's required viewer API, a qualified model, an effort,
  the qualified Codex version or the build volume changes in its source and
  the manual's release facts do not
- **THEN** the studio's documentation test fails naming the fact
