## Context

The broker retains a bounded deque of compact event records and exposes that
history through the run API and the shop-floor stream. The browser presently
renders the recorded order (oldest first) and displays only each record's
sequence number. The events sit directly below the live agent roster in a
scrolling sidebar.

## Goals / Non-Goals

**Goals:**

- Keep the latest activity directly below the agent roster.
- Let a maker identify when every displayed event was recorded.
- Keep an event's timestamp stable across live updates and reloads.
- Preserve the existing bounded history and event privacy behavior.

**Non-Goals:**

- Persist broker history across a shop restart.
- Add filtering, grouping, relative-time updates, or a clock to the sidebar.
- Change agent state or event-retention semantics.

## Decisions

### Record the event time at publication

The broker will add a machine-readable UTC timestamp to every `BrokerEvent`
when it assigns its sequence number, then include it in existing snapshot and
SSE event values. This makes the value authoritative, stable, and available on
initial load as well as live delivery.

Recording a client-side receipt time was considered, but it would differ after
a reload and would describe browser delivery rather than broker activity.

### Render a local readable representation from the recorded timestamp

The browser will format the broker timestamp in the maker's locale and time
zone, while preserving the raw value in the event data supplied by the broker.
This is more useful for a person operating the local shop than an unlabelled
UTC string. An ISO string was considered but is less immediately scannable in
the compact sidebar.

### Reverse only the display order

The broker continues to retain and transmit events in recorded (oldest-first)
order. The menu renders a non-mutating newest-first view, so retention,
sequence behavior, event delivery, and other consumers do not change.

Reversing storage or transport was considered but would make the broker's
natural chronological history less clear and expand the change beyond the UI
need.

## Risks / Trade-offs

- [Locale formatting varies between browsers] → Tests will assert the presence
  and ordering of timestamp-bearing entries rather than a platform-specific
  formatted string.
- [Clock changes or clock skew affect displayed absolute time] → The timestamp
  remains an honest record of the broker host's publication time and is paired
  with the existing monotonic event sequence.
- [Old or malformed data lacks a timestamp] → The browser will tolerate it
  without failing the event log, while all newly published events carry one.

## Migration Plan

Deploy the broker and browser together. Existing in-memory events disappear on
shop restart, so no data migration is needed. Rollback consists of restoring
the previous broker record and menu renderer; no persistent data is affected.

## Open Questions

None.
