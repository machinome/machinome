## ADDED Requirements

### Requirement: The manual states a model's app

The viewer's pages of the manual SHALL state, as user guidance, that a model
may carry its own app which the viewer shows in place of its automatic panel;
which mounts show it and that suppressing the on-screen chrome suppresses it;
how the app places the picture; the helper `@machinome/viewer/app` and each of
its names, with what it returns and refuses; the handle's notification of a
clocked machine's changes and its answer whether a transition is drawn; what
a reader sees when an app cannot be shown and what each refusal of the
bundling means; that an app is bundled only from a source checkout with its
JavaScript dependencies installed in this release; and the viewer API that
carries the capability. A how-to SHALL walk a maker through giving a model
its app, from the declaration to the page, on the public contract alone.

#### Scenario: A maker looks up the helper

- **WHEN** a maker writing an app looks up `useMachine` in the viewer's
  reference
- **THEN** the reference states what it returns, when it re-renders, and
  that it refuses on a model that is not a clocked machine

#### Scenario: A host embedding the viewer reads about the app

- **WHEN** a developer embedding the viewer with the chrome suppressed reads
  the mount reference
- **THEN** it says the model's app is suppressed with the chrome
