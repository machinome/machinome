## MODIFIED Requirements

### Requirement: The manual is reproducible and reviewable

The manual SHALL build with Sphinx and the Read the Docs theme, warning-free
in nitpicky mode, from `docs/requirements.txt` alone, without the floor's
runtime dependencies, the framework, the viewer or a CAD tool. The `docs`
extra of the package SHALL be identical to `docs/requirements.txt`, and
`.readthedocs.yaml` SHALL build the same way with warnings as failures and
no extra build step. The command reference SHALL name the
`machinome-studio` command as the way the hub is started, and SHALL document
every option the launcher entry points accept, other than options they hide
from their own help, and the studio configuration file: where it is looked
for, the variable that names another file, every key it accepts, and the
order in which options, environment, file and defaults are applied. The
README SHALL name the studio and its version, say how it is installed and
opened, and point to the manual and the status page.

#### Scenario: The manual is built from a clean checkout
- **WHEN** the documented build command is run with only the documentation
  requirements installed
- **THEN** a warning-free HTML manual is produced

#### Scenario: A launcher gains an option
- **WHEN** an entry point adds an option that its help shows and the
  command reference does not name it
- **THEN** the documentation test fails naming the option

#### Scenario: The configuration file gains a key
- **WHEN** the studio configuration file accepts a key that the command
  reference does not name
- **THEN** the documentation test fails naming the key

#### Scenario: A page teaches how to start the hub
- **WHEN** a reader-facing page shows how to start the hub
- **THEN** it shows the `machinome-studio` command
