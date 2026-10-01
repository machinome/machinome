## ADDED Requirements

### Requirement: `check` reports the measured text of each shot

When `check` measures a movie document's set layouts, it SHALL, on the same
page, at the output size and before any take is read, also measure the
text each shot shows: for every shot that places a source panel, the font
size its code is drawn at; for every shot that places a title one of its
cues shows, the number of lines the title's text wraps to and, with a
subtitle, the number of lines of the subtitle. Each element SHALL be
measured wholly shown (a title with all its words, a source panel with its
whole excerpt typed), in its slot of the shot's set. `check` SHALL print one
line per such shot naming the shot and, for each element, its kind, its
key and its slot, with a source panel's size in CSS pixels and in vw of the
output width and a title's lines. It SHALL NOT apply a threshold and SHALL
NOT refuse on what it measured. A movie document that places a source panel
or shows a title, and whose layout `check` does not measure, SHALL be
reported in one line as not measured, saying why; no browser is opened for
it.

#### Scenario: The tour's text
- **WHEN** `check` runs on the fixture tour at 1280×720
- **THEN** it prints `Shot question: title opening.title in headline on 1
  line, its subtitle on 1 line`, a line for `rise` and `rhythm` giving their
  titles' lines, and for `source` and `push` the code panel
  `balance.code` at `13.1 px (1.02 vw)`.

#### Scenario: A headline that wraps
- **WHEN** the tour's headline slot is narrowed by its stylesheet so that no
  two words fit beside each other
- **THEN** `check` prints that `tip.heading` (*Rise and fall*) is on 3 lines
  in `rise` and `tip.beat` (*Up. Down.*) on 2 lines in `rhythm`, and refuses
  nothing.

#### Scenario: Addition's code size
- **WHEN** `check` runs on *Addition*, whose split set draws its source
  panels at `--vm-source-size: .9vw` in a 1920-pixel film
- **THEN** it prints for each of `inputs`, `turn` and `commit` its panel at
  `17.3 px (0.90 vw)`.

#### Scenario: A document check opens no browser for
- **WHEN** `check` runs on the clocked fixture `count`, which shows no
  picture, has no reframe and places a source panel
- **THEN** it launches no browser and prints that the text was not measured
  and why.
