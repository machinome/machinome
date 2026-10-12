# ADR 0003: Separate the porter lifecycle role from the foreman

**Status:** Superseded by ADR 0005

**Date:** 2026-07-20

## Context

Shop-floor introduces a browser conversation between the maker and the active
foreman. That conversation must not blur the two levels of management already
present: the Codex CLI agent that starts the floor and launches agents, and
the foreman agent that manages work inside the floor.

Calling the first role a *shop runner* would misleadingly suggest that it is
the manager of the shop's work. Routing maker messages through it would also
give a routine lifecycle agent an unnecessary decision-making role.

## Decision

The Codex CLI lifecycle role is named the **porter**. The porter starts and
stops shop-floor and launches or ends the foreman and its specialist agents.
It obeys lifecycle instructions and makes no project, design, or shop-work
decisions.

The **foreman** is the distinct agent launched by the porter. It manages
shop-floor agents and directly receives maker messages from, and publishes
messages to, the shop-floor broker. The porter is not a conversation relay.

## Consequences

- Browser conversation and broker operations belong to the maker ↔ foreman
  path, not a Codex CLI user interface.
- Foreman listener instructions use the broker command directly and retain the
  foreman's choice of whether and when to communicate.
- Future role adapters and documentation must preserve the porter/foreman
  distinction.
