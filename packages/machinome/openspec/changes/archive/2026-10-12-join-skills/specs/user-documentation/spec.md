## ADDED Requirements

### Requirement: The machinome skills are documented as a how-to

The manual SHALL carry a how-to guide, `howto/assistant-skills`, listed in the
how-to section of the navigation, that tells a reader how to give an assistant
that reads Agent Skills the skills `machinome` and `machinome-simulate`: what
each is for; the install lines `pip install "machinome[skills]"` and
`machinome skills install`, with the prompt's pre-selection, `--tools` and
`--personal`; `machinome skills list` for every tool and the directory it
reads, rather than a table copied from the registry; `machinome skills update`
after an upgrade; that the command refuses a skill it did not write unless
`--force`, deletes nothing, and marks each copy, and that a copy whose marker
is removed is left as the user's; and what the assistant needs to do the work.
The installation page SHALL name `machinome[skills]` and the distribution
`machinome-skills`. The command reference SHALL document `machinome skills`
with its three verbs, their options and their exit statuses, and SHALL NOT say
that the skills package is yet to add its command.

#### Scenario: A reader wants an assistant to use machinome

- **WHEN** a reader opens the how-to section of the navigation
- **THEN** it lists the skills guide, which installs the skills with `pip
  install "machinome[skills]"` and `machinome skills install` and names
  `machinome skills update`, `machinome skills list`, `--tools` and
  `--personal`

#### Scenario: A reader looks up the command

- **WHEN** a reader opens the command reference
- **THEN** it has a section `machinome skills` naming `install`, `update`,
  `list`, `--tools`, `--personal` and `--force`, and the section on commands
  from other packages names the skills package's command as added
