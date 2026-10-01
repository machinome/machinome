## ADDED Requirements

### Requirement: An on-demand viewer poses and draws a clocked machine

A viewer mounted in on-demand render mode, under the conditions that mode
already requires (externally driven animation, no autoplay, no driver
controls and no part controls), SHALL accept a document carrying a clocked
machine, whether or not it declares instructions. It SHALL keep refusing a
document carrying a running program, naming the render mode, and a posed
document that declares instructions.

Under on-demand rendering, an accepted request to move an input, restore a
saved bank or reset the machine SHALL pose the model and draw it before
the call returns, with no frame loop running, so that a capture taken
immediately afterwards shows the new bank. Changing the view SHALL draw as
well, and adopting the view the viewer reports SHALL redraw without
changing it. Posing the same bank twice SHALL draw the same frame.

Under on-demand rendering, playing a declared instruction and starting a
clocked machine's clock SHALL be refused by name, before any request is
made and without changing the bank or the drawn pose, naming the render
mode, because both draw over wall seconds that only a frame loop advances.
Stopping the clock SHALL be accepted. An on-demand viewer SHALL present no
control of its own on a clocked machine: no clocked panel, no part control
and no full-screen control.

#### Scenario: A film poses a stroke mid-path

- **WHEN** a host mounts a clocked machine on demand, restores a bank whose
  crank stands halfway through its stroke and captures the frame
- **THEN** the frame differs from the frame captured at the stroke's
  origin, and equals a second capture taken after restoring the same bank
  again

#### Scenario: A request answers as in continuous mode

- **WHEN** a host makes the same requests on an on-demand mount and on a
  continuous mount of the same clocked document
- **THEN** each request reports the same origin, end, admitted travel,
  commits and stops, and leaves the same bank

#### Scenario: A played instruction is refused on demand

- **WHEN** a host plays a declared instruction on an on-demand mount of a
  clocked machine
- **THEN** the call fails naming the on-demand render mode, and the bank
  and the frame are unchanged

#### Scenario: A running clock is refused on demand

- **WHEN** a host starts the clock of a clocked machine that declares one,
  on an on-demand mount
- **THEN** the call fails naming the on-demand render mode, the clock does
  not play, and advancing the clock by a request still works

#### Scenario: A running program is still refused on demand

- **WHEN** a host mounts a document carrying a running program on demand
- **THEN** the mount fails naming the program and the render mode

#### Scenario: Nothing to press on a filmed machine

- **WHEN** a clocked machine is mounted on demand
- **THEN** the page holds the canvas and no control of the viewer's own

#### Scenario: A host requires an on-demand clocked mount

- **WHEN** a host means to capture a clocked machine frame by frame without
  a frame loop
- **THEN** the declared API version tells it whether this bundle mounts
  one on demand, before it mounts a bundle that would refuse the document
