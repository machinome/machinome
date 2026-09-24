## ADDED Requirements

### Requirement: The inspector goes full screen as one layout

When a viewer is mounted as part of the inspector layout, its full-screen
root SHALL be the whole inspector layout, not only the viewer's pane.
Entering full screen from the viewer's full-screen control or the `f` key
SHALL bring the assembly rail, the sidebar in whatever state it was in,
and the viewer with its chrome to the screen together. Opening and
closing the sidebar SHALL keep working in full screen, and the canvas
SHALL follow the pane's size. The standalone export page and the
development page, which mount this layout, SHALL behave the same way.

#### Scenario: An export goes full screen with its sidebar

- **WHEN** the maker presses the full-screen button on a standalone export
  page
- **THEN** the document's full-screen element is the inspector layout, the
  sidebar toggle is on screen, and opening the sidebar narrows the canvas
  within the full-screen view

#### Scenario: A plain viewer goes full screen alone

- **WHEN** a host mounts the plain viewer into its own element and the
  maker presses the full-screen button
- **THEN** the document's full-screen element is that host element
