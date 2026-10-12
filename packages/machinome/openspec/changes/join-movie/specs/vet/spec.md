## ADDED Requirements

### Requirement: A model that reaches the movie package is refused

The contract's denied modules SHALL include `machinome.movie`: a vetted file
that reaches, through an import statement or an attribute chain on a name
an import bound, `machinome.movie` or a name beneath it SHALL be reported
`framework-internal`, naming the denied name reached, as for the contract's
other denied modules. The former name `machinome_movie` SHALL stay outside the
universe. A project's movie declarations, which no model's closure reaches,
are not vetted, and a project whose films import `machinome.movie` SHALL keep
the verdict its models give.

#### Scenario: The movie is an internal to a model

- **WHEN** a project's model imports `from machinome.movie import Movie` and
  the project is vetted
- **THEN** the model's report holds `framework-internal` naming
  `machinome.movie`, and the model is not pure; and a model importing
  `machinome_movie` instead is reported `outside-universe` naming it

#### Scenario: A project's films do not change its verdict

- **WHEN** a project's `videos/<movie>/movie.py` imports `machinome.movie` and
  its models import nothing of it
- **THEN** the project's verdict is the one its models give
