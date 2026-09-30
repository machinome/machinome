# ADR-006: YAML episodes and movie documents load into one resolved document

Status: Accepted (OpenSpec change `react-stage`, 30 September 2026). Amends
[ADR-001](ADR-001-movie-document-and-chapter-narration.md), decision 1.

## Context

ADR-001 loaded a movie document into the internal episode, the YAML format
0.4 shape with chapters, so that nothing after loading told them apart. The
stage draws sets, slots and elements (ADR-004), which that shape cannot
express, and `machinome-movie/0.2` carries them. The eight Leonardo episodes
are YAML and must keep producing.

## Decision

The seam after loading is the **resolved movie document**
(`docs/movie-document.md`, "Resolution"): the 0.2 document with every time
numeric, starts and ends, and `resolved: true`. A movie document resolves to
it against its cached takes; a YAML episode, validated by every rule of its
format as before, converts to it: one chapter per shot, its fields
synthesized into elements and actions, placed in the shipped sets `paper`,
`paper-split` and `source-only`, its measured word timing filled from the
cached takes by the commands that need it. The timeline, the stage, the
renderer, the shot cache and the review packs read only this shape.

## Options considered

- **Keep the episode shape and convert movies into it.** Cannot hold two
  views in a shot, project elements or a template's slots.
- **Two pipelines, one per source.** Doubles the timeline and every proof.

## Consequences

- A YAML episode's refusals keep their words; its pixels change with the
  sets that now draw it.
- A synthesized YAML action keeps its authored identity (`overlay`,
  `annotation`, `highlight`, `picture`, `emphasis`) so refusals and review
  packs still name the authored cue.
