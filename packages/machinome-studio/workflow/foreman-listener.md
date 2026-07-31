# User-facing agent delivery

The selected profile's user-facing agent does not poll or run a broker receive
command. The non-model orchestrator records a broker envelope before delivery,
starts an idle backend delivery, or steers that same active delivery at its
next backend work boundary. The broker publishes ordinary non-empty backend
output from only that configured agent into the user conversation.

Direct profiles carry no assignment identity and derive activity only from the
matching backend turn. Delegated profiles use the declared assignment and
reporting graph; assignment acknowledgement and matching completion, not a
backend turn, control specialist work state. `python -m floor.agent` provides
the profile-neutral broker command surface.
