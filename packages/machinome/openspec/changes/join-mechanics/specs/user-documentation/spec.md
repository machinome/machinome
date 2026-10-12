## RENAMED Requirements

- FROM: `### Requirement: Mechanics users can reach the independent helper manual`
- TO: `### Requirement: The mechanics helpers are documented in the manual`

## MODIFIED Requirements

### Requirement: The mechanics helpers are documented in the manual

The framework manual SHALL document the mechanics helpers, the package
`machinome.mechanics` of the distribution machinome-mechanics, installed by the
`mechanics` extra: a reference section, `reference/mechanics/`, listed in the
reference part of the navigation, whose index names the distribution, its
version through the `|mechanics_version|` substitution, its install line and
its import, and lists every helper, followed by a conventions page and one
page per formula family stating each helper's signature, frame, zero, sign and
domain with an example; and a how-to guide, `howto/mechanism-formulas`, listed
in the how-to part of the navigation, that installs the helpers, calculates a
pose and connects a helper to a driver through a relation law, explaining
resolved parameters, deferred symbolic inputs and the limit on dimensional
class-body formulas. The installation guide, the helper API reference, the
motion-law guidance and the sibling-manuals page SHALL link those pages
inside the manual. No page SHALL link a separate mechanics manual, and none
SHALL spell the module `machinome_mechanics` but the changelog and the
upgrading page, which record the rename and the 0.7 migration. Every example
of those pages that can run SHALL be run by the mechanics package's tests
against the installed framework, while the manual's own build SHALL import no
runtime package.

#### Scenario: Find a helper from the framework

- **WHEN** a framework user looks for a gear, screw, crank, delta or linkage helper
- **THEN** the manual's reference section lists "Mechanics helpers", whose
  pages give each helper's signature and conventions
- **AND** states that helpers are imported from `machinome.mechanics`

#### Scenario: Follow a motion-law or migration guide

- **WHEN** a reader wants to reuse a mechanical formula or migrate the former
  framework helper imports
- **THEN** they can follow a link inside the manual to the mechanics pages for
  examples and conventions without needing internal workflow records

#### Scenario: The helpers' examples run

- **WHEN** the mechanics package's tests run on a synced workspace
- **THEN** every `>>>` example of the mechanics reference pages and of the
  how-to guide runs against the installed helpers and framework with the
  examples' project on the path, and none fails

#### Scenario: No page sends a reader to the separate manual

- **WHEN** the manual's pages and the framework's README are read
- **THEN** none links `machinome-mechanics.readthedocs.io`, and only the
  changelog, which records the rename, and the upgrading page's 0.7 section
  spell `machinome_mechanics`
