## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `videos/addition/`, filming its clocked model
through a `Take`). Its finding is wart 9 of the section "Addition (Curta,
1 October 2026)" of `workflow/warts.md`, the half of it that is still
Videomaker's: the take's identity could not be read from the framework's
`Sim`, so evaluation copied the `take.identity` it writes from the export
manifest's `clocked.identity` and never compared the machine it recorded
with the machine the export carries. What stood in for that comparison was
the document check holding the recorded bank's ids to the export's drivers
and states (`declare-a-take`, evidence finding 2): a model that gained,
lost or renamed a driver or a state since its export was refused in words
about `take.initial`, and a model whose law changed with the same ids was
recorded without a word, its document carrying the export's identity over
banks another machine made. Only the viewer's `restore`, at preview, could
catch that.

The framework now publishes the identity (its `main` 096217f, the
requirement "A clocked simulation publishes its machine's identity" of its
`simulation` spec, installed in the workspace venv): `Sim(model).identity`
is the clocked machine's identity, the same string an export of the same
model carries as `clocked.identity`, whatever the bank holds; a `Sim` that
is not clocked refuses it by name.

## What the film does with the result

The Curta's take is recorded against the machine the framework simulates,
and evaluation refuses it, naming both identities, when that machine is not
the one the export carries: a model edited after its export, or a take
declaring another model than the one the export was made from, is caught
when the movie is evaluated, before speech, and not at preview. The film
has nothing to prove until the orchestrator exports the Curta again on the
renamed project; on a matching export, its document is unchanged.

## What Changes

- **The take's identity is the simulation's.** Evaluation reads
  `take.identity` from `Sim(model).identity`, the simulation it records the
  steps through, and refuses, before making any step, a take whose
  identity differs from the export's `clocked.identity`. The refusal names
  the take, the model (`module:Class`), the export, both identities, and
  what to do: export the model again, or declare the model the export was
  made from.
- **The bank-ids comparison stops standing in for the identity.** The
  document check keeps holding `take.initial` to the drivers and states of
  the machine the export publishes, in both runtimes, because the contract
  says the bank is every driver and state of the machine and nothing else,
  and a document whose identity is right can still break that (a damaged
  or hand-edited document); that is what it refuses that the identity does
  not. Its words no longer say the take "was recorded against another
  machine", which the identity check before it has already ruled out:
  they name the rule. The evaluation test that faked a stale export by
  deleting a state from a copied manifest (its identity unchanged) goes;
  a real stale export, a copy of the fixture project whose model changed
  since its export, takes its place.
- **Both runtimes refuse the same thing, each from its own source of
  truth**: Python evaluation compares the simulation's identity with the
  export's; the Node commands compare the document's `take.identity` with
  the export's (`fixtures/invalid/take-identity-differs.json`, unchanged),
  and the viewer's `restore` holds the viewer to it.
- **Proofs**: layer 1, a copy of the fixture project whose counter changed
  a law (same ids) or renamed a state since its export is refused naming
  the take, the model, the export and both identities (red: recorded, or
  refused about `take.initial`); the matching counter evaluates
  byte-identical to `fixtures/documents/count.json`, whose take is
  `fixtures/takes/count/counting.json`'s. Layer 2, a new invalid fixture
  `take-initial-incomplete` (the count document without `tens` in
  `take.initial`) that both runtimes refuse in the rule's words.
- **Records**: ADR-011 amended in place with a dated section (its rejected
  option "read the simulation's identity" is now the decision); ADR-020
  is not used. `docs/declaring-a-movie.md`, `docs/architecture-overview.md`,
  `fixtures/README.md`, `CHANGELOG.md`; the `declarative-movie` spec.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `declarative-movie`: evaluation takes the take's identity from the
  framework's simulation and refuses a take whose identity differs from
  the export's, naming the model, the export and both identities.

## Impact

Code: `python/machinome_movie/evaluate.py` (`_record`),
`python/machinome_movie/document.py` and `src/movie.mjs` (the words of the
`take.initial` refusals); tests `python/tests/test_take.py`; fixture
`fixtures/invalid/take-initial-incomplete.json`. No schema, document,
fixture document, resolved pin, take, stage or renderer change;
`src/movie.mjs` is not hashed into the shot cache's key, so no film is
recaptured. The contract page `docs/movie-document.md` already says the
identity is the machine's, which the export's manifest publishes, and is
not changed.

## Non-goals

The framework, the viewer, the document format and the Curta (its export
is made again by the orchestrator). No check of the identity in the Node
commands beyond the document's own (they do not run the simulation). No
publication, push or paid request.
