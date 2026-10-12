# The pendulum regulator, as a version 8 ELAPSED fixture

`viewer.json` is the framework's own test machine
`tests/clocked_project/pendulum.py:Regulator`, exported **verbatim** from
a throwaway copy of machinome at branch `clocked-machine` head
`1a959d3` — 2,116 bytes, md5 `2f3fbfa80f4f125c5915c7f4ae74cc66`, a
**version 8** document: one driver (`engaged`), one **state** (`count`),
no bindings, one piece, and a `clocked` object carrying **one committing
relation and no bounds** — with `clocked.clock: "time"`, which is what
makes it this cycle's fixture rather than cycle 5's.

No `program` and no `controls`: a root publishes one machine or the
other, and ADR-128 §14 keeps a `Control` refused under a clocked root. It
does publish an ordinary `animation` object (`fps: 30`, `frames: 360`),
and **nothing in it reads `$t`** — the bob's pose is a formula of the
BANK — so the document has a clock transport and no timeline.

Nothing here edited the document and nothing here regenerates it. It was
produced with

```
PYTHONPATH="$PWD" machinome export \
    tests/clocked_project/pendulum.py:Regulator -o <dir> --no-widget
```

and the file `machinome export` wrote — `manifest.json` — is what sits here
under the name `viewer.json`, byte for byte. The rename is the only thing
done to it, as it is for every other fixture in this repository.

`machinome export` **warned** while writing it, exactly as it warned for the
calculator:

> this model needs document version 8, and the installed browser viewer
> renders 1, 2, 3, 4, 5, 6, 7 (machinome-viewer 0.1.0). The export is
> written anyway: an export is an artifact a LATER viewer may open …

which is ADR-128 §15 working. (The installed viewer the warning names is
the workspace's published `0.1.0`, not this worktree.)

## The machine

One `Bob` — a 2 × 2 × 40 box on a revolute joint about `z` — posed by

```
bob.swing = 12.0 * sin(360.0 * time / 2.0)
```

published as the operation `("r", "(12.0 * sin(((360.0 * time) / 2.0)))",
[0, 0, 1])`, which reads the free name `time`: the BANK's own clock, in
seconds, and not `$t`. Playing the clock swings it, which is a thing a
person can see.

Beside it, one committing relation on the clock:

```
(time & engaged & count).commits(count, at=release, law=advance)
```

whose level is `floor((time + 0.5) / 1.0)` — affine in the clock, so its
crossings are solved by one division — and whose law is
`count + engaged`. With `T = 2.0 s` the level rises at `t = T/4 + k·T/2`,
which is every **1 second**: the swing's own extremes, twice a period,
where an escapement releases. `engaged` is a declared driver defaulting
to 1, so a disengaged escapement counts nothing.

The first release lands on `0.49999999999999994`, one representable value
below the ideal instant. That is the far-side landing rule working rather
than a rounding error, and `src/clocked/clocked-corpus.test.ts` proves it
by moving that very number and watching the replay go red.

## The identity is NOT the corpus's, and that is the same finding

`clocked.identity` here is
`281dfdc2e4e32c0c86f195c2896faed54c6ea534e9557027890f61f132505814`, while
the same class in `src/clocked-corpus.json` publishes
`2e172caadb36e7a531d000a95ebbd99d13492a6f6e17dbd31abe2788445e65e4`. Every
other field of the two `clocked` objects — `clock`, `own`, the one
`commits` entry, `bounds`, `limits` — and the `drivers`, `states` and
`instructions` tables are **identical**.

The difference is the identity's own first line, exactly as
`tests/fixtures/calculator/README.md` records it: `Clocked.described`
opens with `root {klass.__module__}.{klass.__qualname__}`, and the two
producers import the same class under two module paths. So the same
machine, exported two ways, gets two identities — and a snapshot taken
against one is refused against the other. This fixture is never replayed
against corpus numbers; ADR-062's finding F2 stands, recorded for the
pilot, and nothing here works around it.
