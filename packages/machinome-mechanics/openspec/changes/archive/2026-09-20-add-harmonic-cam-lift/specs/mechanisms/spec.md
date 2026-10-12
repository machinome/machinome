## ADDED Requirements

### Requirement: Periodic harmonic cam lift

`harmonic_cam_lift(angle, lift, rise_span=180, return_span=180)` SHALL return
the signed displacement from a cam follower's base, in the units of full peak
lift. Input angle and spans SHALL be degrees. Phase zero SHALL start the rise;
increasing input SHALL rise over rise_span, return over the next return_span,
then dwell at zero through the remaining 360-degree cycle. Negative input
SHALL traverse the same periodic law backwards. Mounting axis, sign and phase
offsets SHALL remain caller-owned. The helper SHALL be exported flat and from cams.

For p=angle-360*floor(angle/360), u=clamp01(p/rise_span), and
v=clamp01((p-rise_span)/return_span), the result SHALL be
`lift*(cos(180*v)-cos(180*u))/2`. Numeric and supported deferred operands SHALL
share this definition. Physical timing SHALL require positive spans whose sum
is at most 360. No span validation or repair SHALL be added: zero numeric spans
SHALL propagate division errors; other out-of-domain values SHALL retain
arithmetic behavior without a physical-envelope claim. Zero and negative lift
SHALL preserve linear scaling. No geometry or dynamic contact SHALL be inferred.

#### Scenario: Symmetric follower uses full peak lift

- **WHEN** lift=10 and both spans are 180
- **THEN** angles 0,90,180,270,360 give 0,5,10,5,0 within floating tolerance
- **AND** Deepseek sawmill passes 2*FEED_THROW to retain its original stroke

#### Scenario: Hammer and physical cam retain different returns

- **WHEN** rise_span=240 and lift=18
- **THEN** return_span=80 gives peak 18 at 240, half lift at 280 and zero at 320
- **AND** return_span=45 gives half lift at 262.5 and zero at 285, preserving
  Leonardo's earlier physical cam retreat independently of its follower motion

#### Scenario: Signed turns and base dwell agree

- **WHEN** a finite phase is offset by representative positive or negative turns
- **THEN** the lift repeats within floating tolerance, including seam neighborhoods
- **AND** zero lift returns zero and negated lift negates the displacement

#### Scenario: Deferred motion retains the same envelope

- **WHEN** supported deferred angle, lift or timing operands are evaluated
  at representative valid samples
- **THEN** results agree with the numeric envelope and independent piecewise oracle

#### Scenario: Zero timing is not repaired

- **WHEN** either span is numeric zero
- **THEN** the helper raises ZeroDivisionError rather than inventing a rise or return
