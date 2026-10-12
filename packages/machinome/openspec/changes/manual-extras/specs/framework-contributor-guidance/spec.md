## ADDED Requirements

### Requirement: The contributor guide says a manual page declares its extras

`CONTRIBUTING.rst`, in the step of its pull request procedure that asks for
the documentation a change touches, SHALL say that every page of the manual
under `packages/machinome/docs/` begins, under its title, with
`.. needs::` and the extras the page needs, or `none`.

#### Scenario: A contributor adds a page to the manual

- **WHEN** a contributor follows the guide's pull request steps to document
  a change on a new page
- **THEN** the guide tells them to begin the page with `.. needs::`, and the
  layout test fails if the guide stops naming it
