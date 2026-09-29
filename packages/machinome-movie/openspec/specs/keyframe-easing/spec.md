# keyframe-easing Specification

## Purpose
Named easing of camera moves and model time from one five-curve vocabulary,
with every key met exactly, in format 0.4, while 0.2 and 0.3 episodes keep their frames.
## Requirements
### Requirement: One named easing vocabulary

Every eased value in an episode SHALL be shaped by one of five named curves:
`linear`, `smooth`, `in`, `out` and `in-out`. `smooth` SHALL be the curve camera
moves have always used. Every curve MUST start exactly at the earlier key's value,
arrive exactly at the later key's value, and never reverse or pass beyond either.
`in` starts from rest, `out` arrives at rest, and `in-out` does both, lingering
visibly longer at each end than `smooth`. Production MUST refuse any other
easing name, naming the shot.

#### Scenario: A curve reaches its key exactly
- **WHEN** a segment of any of the five curves ends at a key
- **THEN** the frame at that key's time shows exactly that key's camera or model
  second, as it would without easing.

#### Scenario: A misspelled or invented curve
- **WHEN** a key says `ease: ease-out` or `ease: bounce`
- **THEN** `check` refuses it, naming the shot and the five accepted names,
  before any frame is rendered.

### Requirement: A camera move eases as its key says

In a format 0.4 episode, the author SHALL be able to give a camera key an
`ease`, naming the curve of the move that ends at that key. Position, target,
field of view and up direction SHALL all follow that curve. A key without
`ease` SHALL move with `smooth`, exactly as camera keys always have. `ease` on
a shot's first camera key MUST be refused, since no move ends there.

#### Scenario: A move that settles on the linkage
- **WHEN** the restaged *Revolutions* `genome` shot keys from `mechanism` at the
  cut to `linkage` with `ease: out`
- **THEN** the camera is already travelling in the first frames after the cut and
  comes to rest on the linkage at the key, where it holds.

#### Scenario: A steady push-in
- **WHEN** a shot pushes in over its whole length to a key with `ease: linear`
- **THEN** the camera approaches at constant speed from the first frame to the
  last.

#### Scenario: A lens change follows the same curve
- **WHEN** a key that narrows the field of view carries `ease: in`
- **THEN** the field of view changes along the same curve as the position, and
  the picture's projected size still matches the requested field of view at each
  key.

### Requirement: A mechanism can start gently or settle into a beat

In a format 0.4 episode, the author SHALL be able to give a model keyframe an
`ease`, naming the curve of the segment that ends at that key. A keyframe
without `ease` SHALL be linear, as model keyframes always have been. Every key
SHALL still be met exactly, so a mechanical beat aligned to a measured word by a
key stays aligned. Model time MUST NOT decrease and MUST NOT pass beyond either
key of a segment, whatever the curve. `ease` on a shot's first model keyframe
MUST be refused.

#### Scenario: Resume motion gently
- **WHEN** the restaged *Revolutions* `machinome` shot holds model second 453
  until 3.733 s and then runs to 461 at 14 s with `ease: in`
- **THEN** the machine leaves the held pose from rest and gathers speed, instead
  of jumping to full speed in one frame.

#### Scenario: Settle into the pause
- **WHEN** the restaged `genome` shot runs from 461 to 466.8 at 6.899 s with
  `ease: out` and then holds
- **THEN** the mechanism slows to rest exactly as the voice says "pause", at model
  second 466.8, instead of stopping dead at full speed.

#### Scenario: Beats keyed to words stay on their words
- **WHEN** the sawmill's cut/advance keys are given any of the five curves
- **THEN** at each key's time the model is at that key's second, and no frame
  between two keys shows an earlier model second than the frame before it.

### Requirement: Eased frames are reproducible

An eased frame MUST depend only on its video time and the episode. Seeking away
and back, or resuming an interrupted render, SHALL yield identical pixels.

#### Scenario: Revisit an eased instant
- **WHEN** preview poses an instant inside an eased camera move and an eased
  model segment, poses another instant, and returns
- **THEN** the pixels match the first capture exactly.

### Requirement: Format 0.4, and older episodes unchanged

Episodes SHALL be accepted in format `machinome-video-draft/0.4`, with
everything format 0.3 means. `ease` SHALL be accepted only in 0.4: a 0.2 or 0.3
episode carrying it MUST be refused and asked to change its format, naming the
shot, never rendered with its curves silently replaced. In 0.4, a shot, its
`simulation`, its model keyframes and its camera keys MUST refuse any field the
format does not define, naming the shot. Episodes in formats 0.2 and 0.3 SHALL
produce exactly the frames they produced before this change, and a 0.4 episode
without `ease` SHALL produce the frames of the same episode in 0.3. Easing alone
MUST NOT raise the Viewer API an episode needs.

#### Scenario: Existing episodes are unchanged
- **WHEN** the sawmill rehearsal (0.2, with model keyframes) and
  `demo-feed-mechanism` (0.3, with camera and lens moves) are previewed with the
  same viewer bundle before and after this change
- **THEN** their stills are byte-for-byte identical.

#### Scenario: Easing in a 0.3 episode
- **WHEN** an episode declaring format 0.3 gives a model keyframe `ease: out`
- **THEN** `check` refuses it, naming the shot and format 0.4.

#### Scenario: A misspelled field in 0.4
- **WHEN** a 0.4 camera key says `eas: out`, or a 0.4 shot carries a field the
  format does not define
- **THEN** `check` refuses it, naming the field and the shot, instead of
  rendering the default curve or dropping the field.

#### Scenario: An eased episode on an older viewer
- **WHEN** a 0.4 episode that only eases its camera and model keys, with one
  field of view and up throughout, is previewed with a Viewer API 27 bundle
- **THEN** it is produced, since easing needs no newer viewer.
