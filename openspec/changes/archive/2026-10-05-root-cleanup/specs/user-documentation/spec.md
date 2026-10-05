## ADDED Requirements

### Requirement: The manual imports every name from its module

The node package's root resolves no name (`node-model`, "The node package's
root exports nothing"), so the documentation SHALL show and state one import
path per name, the module that defines it:

- every example a reader is sent to -- the tutorial's modules, the how-to
  guides, the concept pages, the API reference and `README.rst` -- SHALL import
  each node class and declaration from its module, and no page a reader is sent
  to SHALL spell `from machinome.node import <name>` or `machinome.node.<name>`
  for a name the root resolved until the OpenSpec change `root-cleanup`; the
  decision records under `docs/adrs/` keep the names they used;
- the API reference SHALL document each node class under its module address
  and SHALL NOT say that node classes are importable from `machinome.node`;
- the upgrading page SHALL state that the root exports nothing and that nothing
  aliases a former spelling, show the refusal a former spelling meets, and map
  each of the twenty-one names to its module;
- the installation page SHALL list the extra of every node type of the table of
  supported node types, `machinome[jscad]` and `machinome[stl]` among them, with
  what each installs, and the how-to guide on choosing a part backend SHALL list
  every node class with its module and the extra that installs it;
- the changelog SHALL record the change under its unreleased section.

#### Scenario: A reader copies an example

- **WHEN** a reader copies the import block of any example in the manual into a
  project
- **THEN** every node name in it is imported from its module, and the project
  imports it

#### Scenario: A reader looks up a node class in the reference

- **WHEN** a reader opens the API reference for `CadQueryNode`, `StlNode` or
  `AssemblyNode`
- **THEN** the class is documented as `machinome.node.cadquery.CadQueryNode`,
  `machinome.node.stl.StlNode` and `machinome.node.assembly.AssemblyNode`, and
  the section states that each class is imported from its module

#### Scenario: A reader upgrades a project that imports from the root

- **WHEN** a reader whose project writes `from machinome.node import
  AssemblyNode, CadQueryNode` reads the upgrading page
- **THEN** they find that the root exports nothing, the error their import line
  meets, and the module of each of the twenty-one names

#### Scenario: A reader picks the extra of a node type

- **WHEN** a reader looks up what to install for `JScadNode` or `StlNode`
- **THEN** the installation page names `machinome[jscad]` and `machinome[stl]`,
  says that neither installs anything beyond the package, and that `JScadNode`
  needs the `jscad` command, which no extra installs

## MODIFIED Requirements

### Requirement: The declarative authoring surface is documented

The documentation SHALL cover the three layers of a value (parameter,
constant, port), the parameter kinds and the dimension algebra including the
`machinome.math` functions, derived formulas, class-body child declarations,
literal lists and `repeat`, a class-body list comprehension over module-level
values, an internal `render()` that positions and returns nothing, `omit()`,
root overrides from Python and from `--set` on the command line, a parameter
without a default, `check()` for guards over several parameters, the
lifecycle split — `render()` builds the machine at rest and places what
does not move, `simulate()` reads drivers, time and ports and moves what
does, motion composing innermost — the deprecation of driver reads in
`render()` with the warning a reader will see, and the two pitfalls:
class-level names are invisible to a class-body comprehension, and
structure that depends on time. It SHALL NOT recommend placement in
`__init__`. It SHALL state that a driver cannot be qualified on a repeated
or list-held child and that ports are the drive path for identical units.
The tutorial's dimensions chapter introduces parameters; the concept pages on
values and on rest and motion, and the how-to guide on repeating a unit and
varying a design, carry the rest.

Every example that declares a parameter SHALL import the kinds from the
dedicated build-parameter module, and every example that declares a port
or a time base SHALL import them from `machinome.motion.ports`. The concept
page on values SHALL state that build parameters come from that module while
node classes come from their own modules under the node package
(`machinome.node.assembly`, `machinome.node.cadquery`, ...), ports and the
declared time base from the motion package, and drivers from the simulation
package. Every
tutorial chapter, how-to guide, concept page and the API reference SHALL read
drivers and time in `simulate()`, the node-tree, part and CLI pages SHALL
cross-reference the values page, and the changelog SHALL record the lifecycle
with the deprecation.

The API reference SHALL document the build-parameter module: the kinds, the
`Quantity` base a project subclasses, and the enumerator over a class's
declarations, in a section of its own beside the node, port, simulation and
testing sections. Its port section SHALL state `machinome.motion.ports`
as the import path for the port kinds and the time base.

#### Scenario: A reader learns where a kind comes from

- **WHEN** a reader looks up how to declare a parameter
- **THEN** the import line in the example names the build-parameter module,
  and the page says which module answers for parameters, for node classes
  and for drivers

#### Scenario: A reader looks up a kind in the reference

- **WHEN** a reader opens the API reference for `Length` or `Flag`
- **THEN** the reference documents it under the build-parameter module, with
  the module's import path stated in the section

#### Scenario: A reader replaces an `__init__`

- **WHEN** a reader who knows the constructor form looks up how to declare
  a leaf's parameters
- **THEN** the page shows the declared form beside the constructor form it
  replaces, states that identity is derived by the framework, and shows the
  value read back as a plain number in `render()`

#### Scenario: A reader repeats a unit

- **WHEN** a reader needs eight identical parts placed differently
- **THEN** the page shows `repeat` with per-unit placement in `render()`
  through `enumerate` and constants, states that the units share one
  artifact, and warns that a class-body list comprehension cannot see
  class-level names while one over a module-level table declares

#### Scenario: A reader guards two parameters against each other

- **WHEN** a reader has a rule that one declared dimension must exceed
  another
- **THEN** the page shows `check()` raising for the bad pair, states when
  the framework calls it and that a refused instance realizes no child,
  and that it is not called on a class that declares nothing

#### Scenario: A reader places a stationary part

- **WHEN** a reader asks where a once-only placement goes
- **THEN** the page shows it in `render()`, shows the moving part's
  operation in `simulate()`, states that the framework runs `render()`
  once and `simulate()` per instant, and that motion composes inside the
  rest placement

#### Scenario: A reader varies a design from the shell

- **WHEN** a reader wants to build the model at another size
- **THEN** the CLI page shows `--set name=value`, how a value is parsed by
  its kind, and what happens for a parameter with no default

#### Scenario: A reader migrates a render that reads time

- **WHEN** a reader's build prints the deprecation warning
- **THEN** the page shows the warning, the `render()` that caused it, and
  the same class with the read and its operations moved to `simulate()`

#### Scenario: A reader learns where a port comes from

- **WHEN** a reader looks up how to declare a port or a time base
- **THEN** the import line in the example names `machinome.motion.ports`,
  and the page says which module answers for parameters, for node classes,
  for ports and the time base, and for drivers
