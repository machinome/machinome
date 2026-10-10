## MODIFIED Requirements

### Requirement: Actual nested delegation and traceable quantity

Nested declarations SHALL bind actual compatible child instances, including repeated parameterized children, and SHALL retain hierarchy. Explicit references, repeats and tuples of references SHALL select actual active occurrences; no manual copied count SHALL replace model-derived quantity. A repeated or tuple child binding SHALL be a tuple at every count, zero and one included, and SHALL name each member in declaration paths by its index in the selection (`kids-0`), so a declaration path keeps its shape when the count changes; a single reference that is not a repetition SHALL bind one production named without an index. A child subtotal or Step SHALL add no extra BOM item.

#### Scenario: Differently sized repeated children
- **WHEN** one profile delegates differently parameterized child occurrences to the same child production definition
- **THEN** each receives its actual bound values and each contributing item appears once in the consolidated root BOM with its occurrence path

#### Scenario: A count moves from one to two
- **WHEN** a profile delegates a repeated child, or a tuple of child references, whose selection has one member, and the same profile binds a model whose selection has two
- **THEN** the binding is a tuple in both, its first member's item declaration path is `kids-0/<item>` in both, the BOM, steps and draft manifest carry the same path, and a single non-repeated reference is still named `kid/<item>`

### Requirement: Honest exclusive ownership

Each physical candidate SHALL have at most one ownership declaration. Sourcing a whole assembly SHALL cover its descendants as one obtained item. Delegation SHALL reserve its subtree. Overlaps SHALL produce deterministic findings naming all competitors and SHALL refuse ambiguous outputs with ProductionConflictError, while findings remains inspectable. A binding's bom, stock, steps, mass and export SHALL be refused for an overlap finding that names an occurrence within that binding's scope, and SHALL NOT be refused for an overlap whose occurrences all lie outside it; the root's scope holds every occurrence. Missing coverage and absent targets SHALL remain explicit nonfatal findings in partial outputs. Flexible candidates SHALL remain represented even when absent from the rigid inventory.

#### Scenario: Parent reaches inside a delegated subtree
- **WHEN** a parent Item selects an occurrence reserved to a child production
- **THEN** findings names both owners and ambiguous BOM/export are refused irrespective of declaration order

#### Scenario: Purchase replaces internal delegation
- **WHEN** a controlled profile selects a whole assembly with Sourced instead of delegating its internals
- **THEN** its purchased quantity counts each selected assembly once with no simultaneous internal part count

#### Scenario: An overlap under one child leaves its sibling readable
- **WHEN** two declarations of one child production claim the same occurrences, or a parent Item reaches inside one child's subtree, and a sibling child's subtree holds none of the claimed occurrences
- **THEN** the sibling's bom, stock, steps, mass and export read normally, the overlapping child's and the root's reports are refused with ProductionConflictError naming the overlap, and every binding's findings stays readable

### Requirement: Instructions remain local and ordered

Step subjects SHALL be declarations owned by the same profile. Markdown and mass evidence paths SHALL resolve within the declaring source directory, refusing canonical traversal/symlink escape. Nested output SHALL preserve subjects, local declaration order and child-before-parent assembly order. Referencing a subproduction SHALL mean its assembled boundary, not extra acquisition. Missing referenced files SHALL refuse requested steps/export contextually. Version 1 SHALL preserve plain Markdown, external http/https links and same-document fragments; local links/images, raw HTML dependencies, file/data URLs and unresolved referenced dependencies SHALL be refused rather than exported with broken paths. A raw HTML dependency SHALL be a tag whose element embeds, loads or executes content or that carries an attribute naming a resource; other text, an inequality included, SHALL NOT be refused as HTML. Text in code spans and fenced code blocks SHALL NOT be read for dependencies, while an HTML block SHALL be read whole. Exported project instructions SHALL retain source attribution without copying unlicensed complete manuals.

#### Scenario: A local image would break the bundle
- **WHEN** a Step Markdown contains a relative local image or reference-style local file link
- **THEN** steps/export refuses the unsupported dependency naming its declaration and source, without publishing a partial target or copying unrelated files

#### Scenario: Child and parent use the same filename
- **WHEN** two nested profiles each declare assembly.md from different source directories
- **THEN** each resolves its own file, both contents survive export and subjects retain their scopes

#### Scenario: An inequality is not a dependency
- **WHEN** a Step Markdown reads `if a<b then c>d ok` or names an element such as `<kbd>` that loads nothing
- **THEN** steps returns the text unchanged and export copies it, while a tag such as `<img src>`, `<a href>`, `<link>` or `<script>` in the same position is still refused

#### Scenario: Markup quoted in code is not a dependency
- **WHEN** a Step Markdown quotes `<img src="x.png">` or a local Markdown link in a code span or a fenced code block
- **THEN** steps and export accept it, while the same tag written inside an HTML block, or before a backtick that would otherwise open a code span, is refused
