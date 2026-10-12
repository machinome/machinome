## ADDED Requirements

### Requirement: The layout `check` measures is the layout a frame is drawn in

The suite SHALL prove in Chromium, with the stage bundle of the fixture tour,
that the boxes `check` measures for a set equal the boxes the stage reports
when a frame of that set is posed at the same size, for the shipped `frame`
and `split` and for the tour's own `Playbill` and `PlaybillSplit`, the box of
a picture placed in a slot included, and that a slot whose box is as tall as
what it holds is reported as such rather than compared. The pipeline tests
SHALL count the Chromium launches of the command line's own process.

#### Scenario: The plate measured and drawn
- **WHEN** the probe measures `Playbill` at 1280×720 and the tour's frame of
  shot `still`, which places the still in `plate`, is posed at 1280×720
- **THEN** the posed frame's slot boxes equal the probe's for every slot the
  probe trusts, the picture's element box equals the probe's picture box for
  `plate`, and `headline` is reported as sized by what it holds.

#### Scenario: A check without pictures launches nothing
- **WHEN** the command line's `check` runs on the fixture movie `minimal`
- **THEN** its process launches no Chromium, and on the tour it launches one.
