## MODIFIED Requirements

### Requirement: Distributions carry the built frontends

Source distributions and wheels of `solid-node-viewer` SHALL contain the
built viewer bundle and the pages the package authors over it: the
standalone export page and the development page. The bundle SHALL be the
only built frontend: creating a source distribution SHALL build it, and
creating a wheel SHALL build it only when the checkout does not already
contain its output, keeping an existing one. The pages SHALL be carried as
they are written, needing no build step of their own. Installing either
distribution SHALL need no npm.

An export directory SHALL keep carrying exactly two files beside the
document and its models — the standalone page and the one bundle — so a
framework copying an export copies the same two names it copies today.

#### Scenario: A source distribution is created

- **WHEN** a source distribution is built from a checkout with no built
  bundle
- **THEN** the bundle is built during packaging and is present in the
  distribution beside both pages

#### Scenario: A wheel is created from a checkout that already built the viewer

- **WHEN** a wheel is built from a checkout containing a built bundle
- **THEN** packaging does not rebuild it, runs no second frontend build,
  and the wheel contains that bundle and both pages

#### Scenario: An export directory is published

- **WHEN** a maker publishes an export directory
- **THEN** it carries exactly the standalone page and the one bundle, and
  the layout the page selects needs no further file
