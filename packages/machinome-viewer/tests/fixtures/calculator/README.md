# The Curta-shaped calculator, as a version 8 fixture

`viewer.json` is the framework's own test machine
`tests/clocked_project/calculator.py:Calculator`, exported **verbatim**
from a throwaway copy of solid-node at branch `clocked-machine` head
`1a959d3` — 15,000 bytes, md5 `0884b61fe1ee8c8a79b0d4b78b28767a`, a
**version 8** document: five drivers (`crank`, `feed`, `operand`, `ring`,
`setting`), five **states** (`halved`, `w0.digit` … `w3.digit`), 39
bindings, two pieces, and a `clocked` object carrying **six committing
relations and three bounds**. No `program`, and no `controls`: a root
publishes one machine or the other, and ADR-128 §14 keeps a `Control`
refused under a clocked root.

Nothing here edited the document and nothing here regenerates it. It was
produced with

```
PYTHONPATH="$PWD" solid export \
    tests/clocked_project/calculator.py:Calculator -o <dir> --no-widget
```

and the file `solid export` wrote — `manifest.json` — is what sits here
under the name `viewer.json`, byte for byte. The rename is the only thing
done to it, as it is for every other fixture in this repository.

`solid export` **warned** while writing it:

> this model needs document version 8, and the installed browser viewer
> renders 1, 2, 3, 4, 5, 6, 7 (solid-node-viewer 0.1.0). The export is
> written anyway: an export is an artifact a LATER viewer may open …

which is ADR-128 §15 working, and is why this fixture can exist at all.

## The machine

Four `Wheel`s of one class, each carrying a `Dial` solid, a `Dial` crank
and a `Slide` knob. A stroke of the crank adds the `operand` across four
digits with the carry inside the law; a clearing relation per wheel
returns its digit to zero as the `ring` sweeps past its rack; the
selector is wired to the knob through a `TranslationalPort`; an
anti-reversal ratchet bounds the crank dial from below at the last seated
tooth; and an off-rest FREEZE bounds the knob's travel on both sides
while the crank is off rest.

Those three bounds are why this is the acceptance fixture: a page that
only turned dials would prove the event solve and nothing of the clip.

## The identity is NOT the corpus's, and that is a finding

`clocked.identity` here is
`979b1a0ef4fe214106f329844ef1c5af789dd18608b5d883eaf22bfdc73ba684`, while
the same class in `src/clocked-corpus.json` publishes
`6eb8e57724cde8a15bc10a2966d02e039ba6fa4aee8c3392bb02c951064eb4a7`.
Every other field of the two `clocked` objects — `clock`, `own`, all six
`commits`, all three `bounds`, `limits` — and the `drivers`, `states`,
`instructions` and `bindings` tables are **identical**, byte for byte.

The difference is the identity's own first line. `Clocked.described`
opens with `root {klass.__module__}.{klass.__qualname__}`, and the two
producers import the same class under two module paths: the corpus
generator as `tests.clocked_project.calculator`, and `solid export
<path>:Calculator` as whatever its loader names the file. So the same
machine, exported two ways, gets two identities — and a snapshot taken
against one is refused against the other. Recorded for the pilot as a
producer-side finding; nothing here works around it.
