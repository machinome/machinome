## ADDED Requirements

### Requirement: A movie is evaluated again when its project changes

`python -m machinome_movie watch <project> <movie> [--out FILE] [--interval
SECONDS]` SHALL evaluate the movie as `evaluate` does, printing the
document's path or the refusal, and then evaluate it again, once, each time
a file under the project changes, is added or is removed, found by
comparing the files' status at every interval (0.5 s unless given), until
it is interrupted, when it SHALL exit 0. Files under directories named
`_build`, `.git` and `__pycache__` SHALL NOT start an evaluation. A refusal
SHALL be printed and the watch SHALL go on. Each evaluation SHALL be the
`evaluate` command's, in a process of its own, so no declaration imported
before is read again. An interval that is not a positive number of seconds
SHALL be refused naming `--interval`. The watch SHALL use the standard
library only.

#### Scenario: A change, then none

- **WHEN** the watch of a project whose files keep their status steps
  through three intervals, and then a module's size changes
- **THEN** it evaluated once when it started, not during the three
  intervals, and once after the change.

#### Scenario: The tool's products

- **WHEN** files are written under the project's `_build`, `.git` and
  `__pycache__` directories
- **THEN** the watch does not evaluate again.

#### Scenario: On the command line

- **WHEN** `python -m machinome_movie watch <project> minimal --interval
  0.1` runs on a copy of the fixture project, a module of the movie is
  written again with another byte, and the process is interrupted
- **THEN** it printed the document's path twice and exited 0.

#### Scenario: An interval refused

- **WHEN** `watch` is given `--interval 0`
- **THEN** it is refused naming `--interval`.
