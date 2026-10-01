## ADDED Requirements

### Requirement: The renderer serves the export files the viewer reads, and only those

`preview` and `render` SHALL serve to the stage, from the model's export,
exactly the files the viewer reads: the `model` reference of every node of
the manifest's `root` tree and the `model` of every entry of a node's
`markings` list, as the framework's export document defines them, each once.
They MUST NOT serve or open any other string of the manifest, whatever its
extension: the printed-piece inventory (`pieces[].models`, `pieces[].sources`)
and every provenance string are not files the viewer reads. Before a browser
opens, a file the viewer reads that the export does not hold, or that lies
outside the export directory, SHALL be refused naming its field path in the
manifest, the node it belongs to and the path the field gives, and saying
that the model must be exported again. The URLs served for an export whose
manifest holds no other file-like string SHALL be those served before, in
the same order, with the same hashes.

#### Scenario: A provenance source the export does not hold

- **WHEN** the fixture movie `minimal` is previewed and rendered over an
  export whose `pieces[0].sources` names `STLs/absent.stl`, which exists
  nowhere
- **THEN** both commands succeed, and `STLs/absent.stl` is neither served
  nor opened.

#### Scenario: A model file lost from the export

- **WHEN** the export's manifest gives the part `Plank` the model
  `models/models/lost.stl`, which the export does not hold
- **THEN** `preview` and `render` are refused before a browser opens,
  naming `root.children[2].children[0].model`, `Plank`,
  `models/models/lost.stl` and that the model must be exported again.

#### Scenario: A marking's artifact lost from the export

- **WHEN** a marking's artifact named in the counter's manifest is absent
  from its export
- **THEN** the refusal names that marking's field,
  `root.children[…].markings[0].model`, and its path.

#### Scenario: A model outside the export

- **WHEN** a node's `model` resolves outside the export directory
- **THEN** it is refused naming the field, the node and the path, and
  nothing outside the export is served.

#### Scenario: The served set of a real export is unchanged

- **WHEN** the files of the fixture exports `seesaw` and `counter` are
  collected
- **THEN** they are the distinct `root` model and marking paths in the
  manifest's depth-first order, the same URLs in the same order as the
  extension walk served before this change.
