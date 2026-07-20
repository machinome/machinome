# Foreman conversation listener

The active foreman listens directly to the local shop-floor broker; the porter
does not relay maker messages or decide how the foreman responds.

The foreman's normal conversation loop is:

1. Run `python -m floor.foreman receive --after <sequence>`.
2. Handle each returned maker message in its current foreman context.
3. When the foreman judges that communication is warranted, run
   `python -m floor.foreman publish --text "..."`.
4. Run `receive` again with the returned `sequence`.

`receive` waits until a later maker message exists and then returns every
currently queued later maker message in order. Messages arriving while the
foreman is handling an earlier batch are returned by the next receive.
