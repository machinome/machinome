## MODIFIED Requirements

### Requirement: The server serves the installed viewer bundle

The system SHALL serve this installation's bundle at `/_viewer/bundle.js`
and report at `/_viewer` whether it is available, its declared API version
and, when absent, the remedy, rather than serving an empty or partial script.

In an installation carrying the widget's sources, the server SHALL serve a
bundle current with them: it SHALL check currency on each bundle request
rather than once at start, so a developer who edits the viewer and reloads
the page receives a bundle built from what they just wrote. When the bundle
is stale and cannot be rebuilt, the route SHALL answer unavailable with that
reason and its remedy, exactly as it answers for an absent bundle, and
`/_viewer` SHALL report the same.

#### Scenario: An installation with a built bundle

- **WHEN** a browser requests the bundle route
- **THEN** it receives JavaScript and the reported API version

#### Scenario: An installation without a built bundle

- **WHEN** a browser requests the bundle route of a source checkout that has
  not built the widget
- **THEN** the route answers unavailable with the build remedy and `/_viewer`
  reports the same remedy

#### Scenario: A developer edits the viewer and reloads

- **WHEN** a browser requests the bundle route after a widget source has
  changed under a running server
- **THEN** the bundle is rebuilt from the changed sources before the
  response is sent, and the browser receives that bundle rather than the one
  the server started with

#### Scenario: A stale bundle that cannot be rebuilt

- **WHEN** a browser requests the bundle route of a checkout whose bundle is
  stale and whose rebuild cannot run
- **THEN** the route answers unavailable naming the stale bundle and its
  remedy, `/_viewer` reports the same, and no stale script is served
