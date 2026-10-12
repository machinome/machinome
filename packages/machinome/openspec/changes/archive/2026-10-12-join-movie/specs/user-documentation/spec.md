## ADDED Requirements

### Requirement: Filming a machine is documented in the manual

The manual SHALL document the films by reader intent: three how-to guides,
"Film a movie of your machine" (install, the workflow from a project's movie
or an episode to a rendered film, timing and revisions), "Declare a movie"
(the Python declarations) and "Draw a movie's stage" (the stage module a
movie's sets are drawn by); and a reference section, "Movies", holding the
movie command (each verb, what it checks, proves and prints, and the files it
writes), the movie document and the episode format. The CLI reference SHALL
hold a section `machinome movie` with its verbs and options and SHALL NOT say
that the videomaker is yet to add its command. The installation page SHALL
name `pip install "machinome[movie]"` and `machinome movie setup`, Node 22 or
newer, FFmpeg and Playwright's Chromium as the steps, and the distribution
`machinome-movie` among the packages of the set under the set's licence.
Every page SHALL spell the command `machinome movie` and the import
`machinome.movie`, and none SHALL show `node bin/videomaker.mjs`, `python -m
machinome_movie`, a `--viewer` option, a checkout's path or a project's name
as the way to make a film; the manual builds with warnings as errors from its
own requirements file.

#### Scenario: A reader films a machine from the manual

- **WHEN** a reader follows "Film a movie of your machine"
- **THEN** they install with `pip install "machinome[movie]"` and `machinome
  movie setup`, and run `machinome movie check`, `speech`, `preview` and
  `render` on a project and a movie name, without naming a viewer bundle

#### Scenario: The former command lines are gone from the pages

- **WHEN** the manual's pages are searched for `bin/videomaker.mjs`,
  `machinome_movie` or `--viewer`
- **THEN** none is found outside the changelog's line that names the former
  import, and the documentation test fails naming a page that holds one
