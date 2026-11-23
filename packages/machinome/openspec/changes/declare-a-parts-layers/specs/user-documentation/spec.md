## ADDED Requirements

### Requirement: Showing one layer of a machine is documented as a how-to

The manual SHALL carry a how-to that shows one layer of a machine, declaring
the extras it needs: defining each layer once with `machinome.layers.Layer`
and importing it where parts declare it; declaring `layers` on a part or a
subsystem, one layer or a tuple; that a subtree is on its ancestors' layers,
that a child or a subclass adds layers and that none is removed; that a part
fused into another and an omitted child contribute nothing; each refusal; that
declaring a layer on a part's class rebuilds that part once while declaring it
on an assembly rebuilds none; and, from the viewer's side, how the model's app
shows a layer. The API reference SHALL document `Layer` and list `layers`
among a node class's reserved declarations. The examples SHALL use the public
contract alone and import every name from its module.

#### Scenario: A maker tags the electrical path

- **WHEN** a maker follows the how-to on a machine with an electrical
  subsystem
- **THEN** they define the layer once, declare it on the subsystem and on the
  parts outside it that carry the current, and see only those parts in the
  model's page when its app shows the layer, with no file of the framework's
  or the viewer's edited

#### Scenario: A maker meets a refusal

- **WHEN** a maker defines a second layer with a key already used and looks
  the refusal up in the manual
- **THEN** the how-to says that one key names one layer in a machine and that
  the layer is defined once and imported
