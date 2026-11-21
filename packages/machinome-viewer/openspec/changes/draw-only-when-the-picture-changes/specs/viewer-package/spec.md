## ADDED Requirements

### Requirement: A continuous viewer draws a frame only when its picture has changed

In the `continuous` render mode the canvas SHALL always show the viewer's current state: the pose, the camera, the canvas's size, which parts are shown, their colours and the overlays standing on them, and the geometry loaded. A change SHALL be shown no later than the first animation frame after it, and before the call that made it returns wherever that call draws. An animation frame in which nothing the picture depends on has changed SHALL draw nothing and SHALL re-evaluate no part of the pose, and the picture on screen SHALL stay the last one drawn.

While the timeline plays, a ramp moves a driver, a clocked machine's clock plays, a request's transition is being drawn, a run is started or a gesture on a part is engaged, every animation frame SHALL be drawn as it is without this rule, the frame in which it ends included. From the first frame after it ends nothing SHALL be drawn until something changes.

A change of the container's size, entering and leaving full screen included, SHALL be drawn at the new size in the frame in which the canvas is resized, so that no frame shows a cleared canvas. After the browser restores a lost graphics context, and when a hidden page is shown again, the next animation frame SHALL be drawn. Every call that draws before it returns SHALL still draw before it returns. What an animation advances by SHALL be the wall time between animation frames, whether or not they were drawn.

A script that reads the canvas in the task of a call that draws SHALL read that call's picture. A script that reads the canvas's drawing buffer in an animation frame in which the viewer drew nothing reads what the browser keeps of it once shown, which the viewer's renderer does not preserve.

The `on-demand` render mode SHALL be unchanged: it runs no frame loop and draws exactly where its calls draw.

#### Scenario: A still page draws nothing

- **WHEN** a continuous viewer has drawn its picture and nothing changes for any number of animation frames
- **THEN** no frame is drawn and no part of the pose is re-evaluated, and the canvas keeps showing the last picture drawn

#### Scenario: A turn of the model is drawn

- **WHEN** a maker turns, pans or zooms the model, or a host sets the view
- **THEN** each animation frame in which the camera moved shows the new view, and nothing is drawn once it stands still

#### Scenario: A resize is drawn in its own frame

- **WHEN** the container changes size, including when the viewer enters or leaves full screen and when it is first laid out
- **THEN** the canvas shows the picture at the new size in the frame in which it was resized, never a cleared canvas, and nothing more is drawn until something else changes

#### Scenario: A hover and its end are drawn

- **WHEN** the pointer comes to rest on a touchable part, leaves it, or the window loses focus while a part is lifted
- **THEN** the lift appears or goes in the next animation frame, and nothing more is drawn after it

#### Scenario: Several changes before one frame are drawn once

- **WHEN** more than one thing changes before an animation frame, such as a turn of the model and a hover
- **THEN** that frame is drawn once and shows all of them

#### Scenario: Motion is drawn as before

- **WHEN** the timeline plays, a ramp runs, a clocked machine's clock plays, a pressed instruction's or a gesture's transition is drawn, or a run is started
- **THEN** every animation frame is drawn as before, the frame in which the motion lands or stops included, and from the next frame nothing is drawn until something changes

#### Scenario: A reload and a republish are drawn

- **WHEN** a host reloads the document or a republished document is applied in place
- **THEN** the new picture is shown no later than the next animation frame after it is applied

#### Scenario: A restored context and a page shown again are drawn

- **WHEN** the browser restores the viewer's lost graphics context, or a hidden page is shown again
- **THEN** the next animation frame is drawn

#### Scenario: A call that draws still draws

- **WHEN** a host calls a method that draws before it returns, such as setting the view, a driver, the time or a part's visibility, focusing a subassembly, highlighting and putting back, a clocked machine's move, restore or reset, or an in-place update
- **THEN** the picture is drawn before the call returns, a read of the canvas in that same task returns it, and nothing is drawn in the frames after it unless something else changes

#### Scenario: Still frames take no time from a motion

- **WHEN** a clock is played, an instruction is pressed or a ramp runs after any number of still frames
- **THEN** no still frame's time is taken from it or added to it: the clock's first played frame advances by that frame's wall time, the pressed instruction's drawing stands at its origin on its first frame and lands when its declared duration has passed from that frame, and the ramp lands when its duration has passed from its trigger, exactly as on a page that drew every frame

#### Scenario: On demand is unchanged

- **WHEN** a viewer is mounted with `renderMode: 'on-demand'`
- **THEN** it runs no frame loop, draws exactly where its calls draw as before, and draws nothing when its container is resized
