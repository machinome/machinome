# Changelog

Videomaker is unversioned (0.0.0) and unpublished. A change adds its entry
here in the same cycle that lands it.

## Unreleased

- A movie can be declared in Python and evaluated to the `machinome-movie/0.1`
  document: the `machinome-movie` package (`python/`) provides `Movie`,
  `Chapter`, `Shot`, `Narration`, `Cue`, the take `Loop` with its cameras,
  layers, source excerpts and stills, the `Paper`, `PaperSplit` and
  `SourceOnly` sets, the view and source-panel elements with their actions,
  titles, annotations, pictures and joins. Movies are listed under
  `[tool.machinome.movies]` and evaluated with `python -m machinome_movie
  evaluate`; mistakes are refused by name before speech. The document's JSON
  Schema is `schema/machinome-movie-0.1.json`, and the shared fixtures gain
  the `minimal` and `tour` documents and seven invalid documents
  (`declarative-movie`).
