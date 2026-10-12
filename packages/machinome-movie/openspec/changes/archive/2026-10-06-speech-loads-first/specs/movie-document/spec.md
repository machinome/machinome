## MODIFIED Requirements

### Requirement: A chapter's narration is one take

A document SHALL group shots into chapters, each with its own narration,
optional speech offset (default 0.2 s), optional direction and its own
elements. `speech` SHALL generate one take per chapter from the narration
alone, before anything in the document is resolved, and place it at the
chapter's start plus its speech offset. Before it requests or reads any
take, `speech` on a document, and `build` without `--silent`, MUST make
every check of the film's load that needs no take, and refuse what it
refuses in the load's words and order: the document's format, schema and
rules; the export's manifest, the source it records and the pinned
revision; the layers and parts the document names against the export, the
emphasised tokens against their excerpts, and a take's identity, inputs and
initial bank against the export; the project repository and the stage
modules; a running program, a clocked export filmed as a loop, a loop of
another length, the output and the cameras; the evidence files; the source
excerpts against the pinned revision; and the stills and clips. Only the
refusals made on the resolved film, whose times come from the takes, MAY
follow generation. The take MUST fit its chapter, ending at least 0.1 s
before the chapter's last shot does; a take that does not is refused after
caching, naming the chapter and its measurement. Captions SHALL follow the
chapter's recorded alignment. A spoken reveal or source emphasis in a shot
SHALL read its chapter's narration and take, at the instant the take starts
relative to that shot.

#### Scenario: A paragraph across a cut
- **WHEN** the `drive` chapter's narration spans the shots `wheel`, `coupling`
  and `stroke`
- **THEN** it is synthesized once, heard without a restart at either cut, and
  its captions follow the one take.

#### Scenario: Emphasis in a later shot of the chapter
- **WHEN** `coupling`, the second shot of `drive`, emphasizes `waterwheel`,
  `drives` and `crankshaft` on the source panel as they are spoken
- **THEN** each token lights at its word's measured onset in the chapter's
  take, counted from the shot's own start.

#### Scenario: An export made from another revision, before any take is bought
- **WHEN** the author runs `speech` on a document none of whose takes is
  cached, and its export's manifest records a `source.revision` other than
  the document's `model.sourceRevision`
- **THEN** `speech` refuses naming `model.sourceRevision` and both
  revisions, in the words `check` uses, and nothing is requested from the
  provider.

#### Scenario: A take recorded on another machine, before any take is bought
- **WHEN** the author runs `speech` on a take document whose `take.identity`
  differs from the `clocked.identity` its export publishes
- **THEN** `speech` refuses naming `take.identity` and `clocked.identity`,
  and nothing is requested from the provider.

#### Scenario: Source that no longer matches its revision, before any take is bought
- **WHEN** a source excerpt's file in the project differs from the file at
  the document's pinned revision, and the author runs `speech` or `build`
- **THEN** the command refuses naming the file, and nothing is requested
  from the provider.

#### Scenario: A document its load accepts
- **WHEN** the document and its project pass every check that needs no take,
  and no chapter's take is cached
- **THEN** `speech` requests one take per chapter, loads the film against
  the takes it cached, and fits, captions and mixes them.
