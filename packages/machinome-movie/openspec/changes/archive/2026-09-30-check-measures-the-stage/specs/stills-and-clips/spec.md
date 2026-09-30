## MODIFIED Requirements

### Requirement: Pixels are never enlarged beyond the author's allowance

A raster still or clip MUST NOT be drawn larger than one output pixel per
source pixel at the output size unless its production entry allows more with
`upscale`. `check` MUST refuse a picture whose peak enlargement over its
interval exceeds its allowance, naming the picture, the shot, the enlargement,
the source and area sizes and the ways to resolve it; `render` at a larger
width MUST refuse the same way before capturing. `upscale` on an SVG MUST be
refused. For a YAML episode the area is the paper page's; for a movie
document it is the box the stage draws for the picture's slot, which `check`
measures at the output size before any take is read (`movie-document`,
"`check` measures a document's set layouts"), and a slot whose box depends on
what it holds is judged by preview and render against the box the stage
reports.

#### Scenario: The museum photograph fills the frame
- **WHEN** the 1175×781 photograph is shown with `area: frame` in a 1920×1080
  film without an allowance
- **THEN** `check` refuses it as a 1.38× enlargement; with `upscale: 1.4` on the
  still it passes and the manifest records 1.38 and 1.4; with `area: stage` it
  passes without an allowance.

#### Scenario: A still too small for a project's plate
- **WHEN** a movie document shows a still in the `plate` slot of the
  project's set, and the box the set draws for `plate` at the output size
  enlarges it beyond its allowance at its view's largest zoom
- **THEN** `check` refuses it before any take is read, naming the still, the
  shot, the enlargement, the source size, the slot's measured box and set,
  and the allowance.
