## Context

The workspace currently puts artifact inspection above a 40%-high,
`foreman-conversation` pane. That pane has a visible "Foreman conversation"
heading, padded message cards, a labelled textarea, and a foreman-specific
send button. Its transcript scrolls independently, but live messages do not
move the viewport to the latest entry.

The existing broker and browser stream already provide ordered entries with an
author and sequence. This change is a presentation and interaction update; it
does not extend the broker's current maker/foreman author model.

## Goals / Non-Goals

**Goals:**

- Make the bottom half of the desktop workspace an efficient chat surface for
  reading several messages and composing the next one.
- Preserve participant attribution while keeping the visual structure ready
  for additional participant types.
- Make a newly published foreman message immediately visible in the transcript.
- Replace fragile geometry acceptance coverage with behavior-focused coverage.

**Non-Goals:**

- Adding direct chat with another agent or changing the conversation API.
- Adding unread indicators, message timestamps, delivery state, persistence
  beyond the existing conversation ledger, or configurable pane resizing.
- Redesigning the left menu or artifact viewer.

## Decisions

### Use an even desktop workspace split without a geometry assertion

The content grid will allocate equal flexible rows to artifact inspection and
chat on desktop. The responsive narrow-window layout remains reachable. The
browser test will verify the continued presence and usability of both areas,
not their measured dimensions.

An exact CSS ratio test is rejected because it couples acceptance behavior to
an implementation detail while providing little confidence that the chat is
usable.

### Render one compact chat transcript, not a titled card panel

The visible section heading and composer label are removed. The transcript
becomes the primary surface, with compact participant-attributed message rows
and its own vertical scroll. The message field has a concise accessible name,
but no visible foreman-directed label; the submit control reads `Send`.

Keeping per-message author metadata rather than visually privileging the
foreman preserves the current maker/foreman distinction and leaves the
component adaptable to later participants. Removing all author attribution is
rejected because readers need to identify who sent each entry.

### Use Enter for dispatch and Ctrl+Enter for a newline

The composer will intercept an unmodified Enter keypress and submit the
non-empty draft through the same path as the `Send` button. Ctrl+Enter keeps
the textarea's normal newline behavior and does not dispatch. This makes the
single-key action match a chat while retaining a deliberate multiline path.

Requiring the button for all sends is rejected because it makes routine chat
entry slower. Sending on Ctrl+Enter is rejected because it conflicts with the
requested multiline shortcut.

### Reveal live foreman messages with transcript-owned scrolling

The transcript element will hold a ref. When the rendered conversation gains a
foreman-authored newest entry, the component will scroll that element to its
bottom after render. Scrolling the page or the surrounding workspace is
rejected because it would disrupt artifact inspection and the menu; the
transcript alone owns chat navigation.

## Risks / Trade-offs

- [A reader is reviewing older messages when a foreman update arrives] → The
  requested behavior prioritizes making foreman updates visible; the change is
  limited to the transcript and does not move the rest of the workspace.
- [Reduced chrome makes the composer less obvious] → Keep a conventional
  textarea and clearly labelled `Send` control, with an accessible name for
  the field.
- [Future participant types need different visual treatment] → Keep
  author-derived data attributes and generic transcript layout rather than
  hard-coding a foreman-centered structure.
