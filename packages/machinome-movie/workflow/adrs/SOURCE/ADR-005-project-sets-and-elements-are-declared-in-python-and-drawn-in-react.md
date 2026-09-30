# ADR-005: Project sets and elements are declared in Python and drawn in React

Status: Proposed (OpenSpec change `declarative-stage`, 30 September 2026)

Numbered 005 because ADR-003 and ADR-004 are taken by the parallel cycles of
the react-stage campaign; a merge that reorders them renumbers.

## Context

ADR-002 made a movie a Python tree evaluated once to the movie document, and
refused a project's own set or element because nothing could draw it: the
sets were the three layouts of the fixed film page, and the document,
`machinome-movie/0.1`, flattened sets, slots and elements into that page's
fields. After inspecting the first film declared that way, the pilot
commissioned the React stage on 30 September 2026: the template owns the
whole screen, nothing is hard-coded, source is shown beside the model. The
validation film *Cut and Advance* (version 2) specifies a root set and a
derived split written in the project's `stage.tsx`, a project element with a
typed action, titles and a picture placed in the template's slots, and source
tokens lit by spoken words. The contract of the document that carries this,
`machinome-movie/0.2`, is `docs/movie-document.md`.

## Decision

A project declares its sets and elements in Python, in the movie's tree, and
draws them in React, in a stage module the declaration names. The Python
declaration is the type; the document carries it to the stage:

- a set is a `Set` subclass with `module`, `Slot()`s and static props (plain
  class attributes, JSON only); its kind is its class name's slug; a derived
  set inherits the chrome and the module, not the layout, and names its base;
- an element is an `Element` subclass with `module` and `Action(param=type)`
  declarations; its props are an instance's keyword arguments; calling an
  action yields a cue's action checked against the declared types;
- the tool's own elements are elements too: `View` with its marks, the source
  panel, `Title`, `Picture`; its own sets are `Frame` and `Split`;
- evaluation emits the stage block (modules, sets, elements with the kinds of
  their props and parameters), from which the stage generates the components'
  prop types, and every refusal that needs no speech is made in Python by
  name.

Python says what and when; React says how it looks. A set does not know what
it holds, and an element does not know which set it is in.

## Options considered

- **Keep the three page layouts and add fields to them.** Every new look is a
  format change again, which is the finding the direction started from.
- **Declare sets and elements only in TypeScript.** The Python tree could not
  name a slot or check an action's parameters where it is written, and the
  document's types would come from the component rather than from the
  declaration the movie is checked against.
- **Declare props on the element class.** No film needs a declared default
  yet; an instance's keyword arguments carry what the film uses, and their
  kinds, taken from use, give the generated types.

## Consequences

- The film's template is the project's code, bundled per movie by the stage;
  nothing in the tool's page decides a pixel the document did not ask for.
- A mistake in a placement, an action or a parameter fails at the line of the
  movie that makes it, before speech is generated.
- Evaluation now opens the source files of the excerpts an emphasis lights,
  to refuse a token absent from or repeated in its excerpt; the document stays
  a pure function of the declarations, the export and those files.
- `machinome-movie/0.1`, the `Paper` sets in Python and the free-standing
  marks and titles leave without a compatibility path, by the pilot's ruling
  that a campaign's intermediate shapes are steps, not protocols.
