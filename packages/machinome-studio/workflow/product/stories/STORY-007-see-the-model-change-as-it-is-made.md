# STORY-007: See the model change as it is made

Derived from `docs/product/sprints/PRD.md`. That document is the source; this
story states the maker-facing outcome it exists to deliver.

## As a maker

I want the model in front of me to change as the work happens, so that I can
watch a part take shape instead of waiting for a reload and then hunting for
what moved.

## What I experience

I change a dimension, or an agent does, and the part that changed updates. The
rest of the model stays exactly where it was, and so does my camera — I do not
lose the angle I was studying it from. On a large assembly the parts arrive as
they finish rather than the whole model stalling and then jumping.

When a build fails, the model I was looking at is still there and I am told the
build failed. When it succeeds again, the view catches up on its own. I never
have to reload the page to get an updated model, and the view never gets stuck
showing something old without telling me.

This holds whether the change came from an agent, from my own editor, from a
terminal, or from several at once.

## Done when

The acceptance criteria in PRD section 7 pass.
