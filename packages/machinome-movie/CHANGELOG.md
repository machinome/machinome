# Changelog

Videomaker is private and unversioned; entries accumulate under `Unreleased`
until the pilot cuts a version. Each change adds its bullet in the cycle that
lands it.

## Unreleased

- The commands accept a movie document, `machinome-movie/0.1` (JSON, contract
  `docs/movie-document.md`), beside YAML episodes: narration in chapters, one
  take each across several shots; cuts, keys and cues anchored to spoken
  phrases and model times to named marks, resolved from the cached takes and
  written to `_build/movie-resolved.json`; the sets `paper`, `paper-split` and
  `source-only`; the schema `schema/machinome-movie-0.1.json` and shared
  fixtures under `fixtures/`. YAML episodes keep their frames, take keys and
  captions. (`movie-document`, ADR-001)
