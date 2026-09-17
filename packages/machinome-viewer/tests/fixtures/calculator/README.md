# The Curta-shaped calculator, as a version 8 fixture

`viewer.json` is the framework's own test machine
`tests/clocked_project/calculator.py:Calculator`, exported **verbatim**
from a throwaway copy of solid-node at branch `play-the-instruction` head
`2ab9505` — 15,159 bytes, md5 `d1d1aad665d22a734767ca7a7bdb5872`, a
**version 8** document: five drivers (`crank`, `feed`, `operand`, `ring`,
`setting`), five **states** (`halved`, `w0.digit` … `w3.digit`), 39
bindings, two pieces, and a `clocked` object carrying **six committing
relations and three bounds**. No `program`, and no `controls`: a root
publishes one machine or the other, and ADR-128 §14 keeps a `Control`
refused under a clocked root.

It declares TWO INSTRUCTIONS, which is why it was re-exported for the
cycle `play-the-instruction` (solid-node ADR-129):

```json
"instructions": {"Set four": {"targets": {"operand": 4}, "duration": 0.5},
                 "Stroke": {"by": {"crank": 360.0}, "duration": 2.0}}
```

`'Stroke'` is the Curta's own `'Turn crank'` on a fixture that also
carries three bounds, and `'Set four'` is its absolute twin — the
`targets=` form, which the Curta does not exercise and the corpus
requires this runtime to reproduce. The previous export of this same
class (15,000 bytes, md5 `0884b61fe1ee8c8a79b0d4b78b28767a`, from branch
`clocked-machine` head `1a959d3`) published `"instructions": {}`; the two
differ in that key and in the `mtime` fields alone, and **both meshes are
byte for byte the same files**, which is why they were not re-copied.

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
`979b1a0ef4fe214106f329844ef1c5af789dd18608b5d883eaf22bfdc73ba684` —
unchanged by the re-export, because an instruction table is not part of
what `Clocked.described` hashes — while
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
