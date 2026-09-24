## MODIFIED Requirements

### Requirement: Iframe rendering

For HTML builders the directive SHALL emit a lazy-loading `<iframe>`
(width 100%, configured height, no border) pointing at
`_machinome/<dest>/index.html`, mapping `:t:` to `?t=…` and
`:autoplay: no` to `autoplay=0` — enabling static single-pose embeds.
The iframe SHALL carry `allowfullscreen`, so the embedded viewer may go full
screen when the reader asks. Non-HTML builders SHALL skip the node.

#### Scenario: Static figure in docs

- **WHEN** a doc uses `:t: 0.3` and `:autoplay: no`
- **THEN** the built page embeds the widget paused at that pose

#### Scenario: A reader watches an embedded model full screen

- **WHEN** a doc embeds an export with `.. machinome::`
- **THEN** the emitted iframe carries `allowfullscreen`
