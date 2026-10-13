## ADDED Requirements

### Requirement: Every page states the extras it needs

Every page of the manual but the release notes under `docs/releases/` SHALL
begin, as the first element under its title, with the declaration
`.. needs::` naming the extras a reader installs, beyond `pip install
machinome`, to follow the page as written, or `none`. The manual's own
Sphinx extension, `docs/_ext/manual_extras.py`, SHALL render a declaration
that names extras as one line at the top of the page: `Needs pip install
"machinome[<extras>]"`, the extras in the order of the manual's table of
extras, followed by what those extras need outside pip, each such need once;
"Needs" SHALL link to the installation page's list of extras. It SHALL
render nothing for `none`. The extension SHALL import nothing but Sphinx,
docutils, `packaging` and the standard library, so the manual still builds
from `docs/requirements.txt` alone.

The build SHALL fail, under warnings as errors, on a page that declares
nothing, a declaration naming an extra the table lacks, naming an extra
twice or naming `none` with another, a declaration that is not the first
element under the title, and a second declaration. The suite SHALL hold the
same before any build, and SHALL hold the declarations to these rules: every
page of a product's reference section (the viewer's, the movie's, the
mechanics helpers', the studio's) declares that product's extra alone; the
index, the why page, the examples page, the installation page, every
concept page, every project page and the core's command, API, assertion and
sibling-manual references declare `none`; and every tutorial chapter, every
how-to guide but the guide that chooses among the node types, and the first
machine's page declare at least the extras their code needs, read from
their code blocks and the modules they include: the node type of every
`machinome.node.<type>` module named, `mechanics` for `machinome.mechanics`,
`movie` for `machinome.movie` or a `machinome movie` command, `skills` for a
`machinome skills` command, `studio` for a `machinome studio` command,
`build123d` for `Svg` artwork, and `web-snapshot` for a photograph through
the web viewer. The manual's contributing page SHALL state the declaration
as the rule for a page.

#### Scenario: A reader lands on a page from a search

- **WHEN** a reader opens "Film a movie of your machine" without having
  read the installation page
- **THEN** the first thing under the title is the line `Needs pip install
  "machinome[movie]"`, then Node 22 or newer with `machinome movie setup`,
  the Chromium it names and FFmpeg with ffprobe, its "Needs" linking to the
  installation page's list

#### Scenario: A page of the bare framework

- **WHEN** a reader opens a concept page, which declares `none`
- **THEN** no line about extras appears under its title

#### Scenario: An author adds a page without a declaration

- **WHEN** the manual is built with warnings as errors and one page has no
  `.. needs::` under its title
- **THEN** the build fails with a warning naming the page, and the
  documentation structure test fails naming it before any build

#### Scenario: A declaration names an extra the manifest does not declare

- **WHEN** a page declares `.. needs:: viewr`
- **THEN** the build fails with an error naming the page, its line and the
  name, and the structure test fails naming the page

#### Scenario: A tutorial chapter's code needs an undeclared extra

- **WHEN** a tutorial chapter includes a module whose relative imports reach
  `Svg` artwork and the chapter's declaration does not name `build123d`
- **THEN** the structure test fails naming the chapter and `build123d`

#### Scenario: A reader follows the tutorial from its own declarations

- **WHEN** an environment installs the extras chapters 1 to 9 declare and no
  other node package, and builds and tests the tutorial's project
- **THEN** every chapter's model builds and every companion test passes,
  and chapter 4's model, built without the `build123d` node package, is
  refused naming `machinome.node.build123d`

### Requirement: The installation page lists the extras from the manifest

The installation page SHALL list every extra a reader installs, which is
every extra of the framework's manifest but `dev` and `docs`, through the
extension's directive `.. extras::` under the label `extras`, and SHALL keep
no hand-written table or paragraph enumerating them. Each entry SHALL give
the extra's install name, the distribution the manifest's requirement names
(with that requirement's own extras), or each member extra for an extra
that names other extras of `machinome`, what the extra is for, what it needs
outside pip, and the pages that declare it, the tutorial once and a
reference section once by its index. What an extra is for and what it needs
outside pip SHALL come from the manual's table of extras,
`docs/_ext/manual_extras.toml`, whose extras SHALL be the manifest's: the
build SHALL fail, and the suite SHALL fail, naming both sets when they
differ, and the table SHALL hold no cross-reference. The page's install line
for the tutorial SHALL name exactly the extras declared by the tutorial
chapters that include a module of the tutorial's machine. The list SHALL fit
a phone's width without scrolling the page sideways.

#### Scenario: The manifest gains an extra

- **WHEN** an extra is added to the framework's manifest and not to the
  manual's table
- **THEN** the manual's build fails naming the table's extras and the
  manifest's, and the structure test fails the same way

#### Scenario: A reader looks up what an extra installs

- **WHEN** a reader reads the installation page's entry for `machinome[web-snapshot]`
- **THEN** it says the extra installs `machinome-viewer` with its
  `snapshot` extra, what it is for, that it needs Chromium for Playwright
  outside pip, and which pages need it, each a link

#### Scenario: The tutorial's install line

- **WHEN** a reader installs from the installation page's first install
  line to follow the tutorial
- **THEN** the line is `python -m pip install
  "machinome[viewer,cadquery,build123d]"`, the extras chapters 1 to 9
  declare, and the structure test fails if the line and those declarations
  differ

#### Scenario: The list on a phone

- **WHEN** the built installation page is opened 390 pixels wide
- **THEN** the page's width is the viewport's, every entry's text wrapping
  within it
