# Foreman event delivery

The active foreman does not poll or run a broker receive command. One
non-model shop orchestrator owns the Codex app-server and subscribes to broker
events asynchronously.

When maker direction or a specialist report is addressed to the foreman, the
orchestrator records it before delivery and then:

- starts a turn when the foreman is idle; or
- steers the active turn when the foreman is working, so Codex presents the
  queued input after the current tool call and before the next task action.

The foreman publishes to the maker with:

```text
python -m floor.foreman --text "<message>"
```

It assigns, directs, and receives specialist reports through the role-neutral
`python -m floor.agent` command surface. While idle, the foreman has no active
model turn, pending receive tool, polling interval, or token consumption.
