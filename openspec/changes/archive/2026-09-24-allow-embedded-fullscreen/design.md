## Context

A document may go full screen from inside a frame only if the frame allows
it (`allowfullscreen`, or `allow="fullscreen"`). The viewer reads
`document.fullscreenEnabled` and hides its full-screen control when it is
false, so without the attribute the manual's embeds simply lack the control.

## Decisions

- **Always allow, no option.** Full screen happens only on the reader's own
  gesture, so permitting it takes nothing from a page. An option to withhold
  it would have no user.
- **`allowfullscreen`, not `allow="fullscreen"`.** Both are honoured by
  current browsers; the boolean attribute is the one machinome.org's own
  iframe uses and the one the viewer manual's embedding example gives.

## Risks

None known: the attribute is inert until the framed page asks for full screen.
