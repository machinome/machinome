## ADDED Requirements

### Requirement: Giving a model its own app is documented as a how-to

The manual SHALL carry a how-to that gives a model its own app, declaring
the extras it needs: declaring `app` on the root class and where the path is
relative to; where the app's files live and that a project carries only its
TypeScript, JavaScript and CSS files; what `machinome build`, `machinome
develop`, `machinome export` and the Studio do with the app; that only the
published root's declaration is read; each refusal and where it is shown;
that a widget-less export of a model with an app is refused; and that in this
release an app is bundled only from a source checkout of the repository with
its JavaScript dependencies installed. The API reference SHALL list `app`
among a node class's reserved declarations, and the command reference SHALL
state what `export` and `build` do with an app. The examples SHALL use the
public contract alone.

#### Scenario: A maker gives a model its app

- **WHEN** a maker follows the how-to on a clocked model
- **THEN** they declare the app, write it beside the model, and see it in
  `machinome develop`'s page in place of the panel, with no file of the
  framework's or the viewer's edited

#### Scenario: A maker meets a refusal

- **WHEN** a maker's app does not build and they look it up in the manual
- **THEN** the how-to says the model is still shown, where the sentence
  appears, and that the export refuses it
