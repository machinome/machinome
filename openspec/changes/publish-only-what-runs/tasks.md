## 1. Red first: the fixtures and what they must publish

- [ ] 1.1 The baseline is already in `evidence.md` (section "The base
      suite"): `tests/test_running_document.py`,
      `tests/test_running_simulation.py` and
      `tests/test_running_corpus.py` green on the planning commit. Re-run
      them before touching anything and confirm the same counts, so the
      "green unchanged" of 4.1 has something to mean.
- [ ] 1.2 In `tests/running_project/machine.py`, three fixtures — no new
      module, beside the existing running machines:
      - `SpringBank`: a running root with a driver, one leaf on a
        `Prismatic`, and a `.repeat(3)` child owning a plain
        `TranslationalPort` the driver drives (`evidence/probe_repeat_port.py`'s
        `Bank`, renamed). Its body `SpringBankBody` without
        `Time.running()`, for the untimed comparison.
      - `Optional`/`OptionalBody`: a running root with a `Flag`, two
        arbors, a driver driving both turns, and a `render()` that
        `omit()`s the second when the flag is false
        (`evidence/probe_omitted.py`'s `Machine`).
      - `OptionalRead`: the same shape with the relations CHAINED —
        `crank.drives(spare.turn)` and `spare.turn.drives(first.turn)` —
        so both edges are kept and the omitted node's coordinate stays a
        coordinate the program computes (`evidence/probe_omitted.py`'s
        `Reader`). This is the machine that must still be refused.
      Adding them changes no existing fixture and adds no entry to
      `tools/generate_running_corpus.py`'s `CORPUS`.
- [ ] 1.3 In `tests/test_running_document.py`, one test per spec
      scenario, all red before task 2:
      - `SpringBank()` publishes; `program['intermediates']` is `[]`;
        `program['sources']` has exactly the driver and the joint
        coordinate; no key of `program` mentions `PenSpring`, `height`
        or `springs-0`; and the document's `root` still carries all
        three copies as children named `springs-0`…`springs-2`.
      - `Optional(fitted=False)` publishes; the omitted coordinate is in
        neither `coordinates`, `intermediates` nor `sources`; and
        `Optional(fitted=True)` publishes it as a bank coordinate — the
        same assertion both ways, so the test says what omission
        changes.
      - `OptionalRead(fitted=False)` is REFUSED with `UnsupportedLaw`
        naming `Arbor.turn`, and `OptionalRead(fitted=True)` publishes.
        Assert the exception message names the node.
      - `Gauged` publishes `intermediates == []` and no `gauge.angle`
        entry in `sources`, while
        `test_a_plain_port_follows_the_bank`'s assertion — the hand's
        pose resolving to `first.turn` — is unchanged. Same for
        `PortDrivenJoint` and `register`.
      - `PortDrivenSmooth` publishes `register` in `intermediates`, in
        `sources` with `['crank']`, and in the `gives` of one edge: the
        intermediate the program DOES compute is untouched.
      - Add `SpringBank`, `Optional` and `PortDrivenSmooth` to
        `test_every_free_name_the_document_reads_is_declared`'s list, so
        the narrowed declared set is guarded.
- [ ] 1.4 In `tests/test_running_simulation.py`, that the RUN is
      unchanged by any of it: `Sim(SpringBank(), dt)` steps, every copy's
      `height` follows the driver on every tick exactly as the untimed
      `SpringBankBody` poses it, and `program.identity` of `SpringBank`
      equals the identity the same tree compiles to — take the second
      reading from a program compiled in the same process, not from a
      stored digest, and assert the identity of `Train` against the
      digest the corpus carries so the "identity does not move" claim is
      tested against committed data.

## 2. The change

- [ ] 2.1 In `compile_program` (`solid_node/simulation/program.py`),
      after `kept = _reaching_the_bank(candidates, bank_keys)` and before
      `_refuse_opaque`, reduce `nodes` to `bank_keys` plus every key the
      kept edges read or give. Comment it with WHY, in the module's own
      voice: a coordinate no compiled edge touches is not part of the
      program, and `_register` cannot know that until the pruning has
      run.
- [ ] 2.2 Extend `_Node`'s and `Program.nodes`' docstrings to say what
      the table now holds, and check that `published`'s docstring,
      `published_names`' and `_refuse_unqualified`'s still describe what
      they do.
- [ ] 2.3 Nothing else in `program.py` changes. Confirm by reading, and
      say so in `evidence.md`: `_refuse_opaque`, `_ordered`,
      `_reaching_inputs`, `_constraint_table`, `values_of`, `deltas_of`,
      `described` and `run.py`'s three `program.nodes[...]` reads all
      address keys that survive.

## 3. The recorded documents

- [ ] 3.1 Recapture `tests/base_documents/running_train.json` with
      `tests/test_running_document.py`'s own `document()` helper and the
      `mtime` normalization `ByteIdentityTest.normalized` does. Show the
      diff in `evidence.md` and confirm it is the `intermediates` list
      and the `wheel.turn` entry of `sources`, and nothing else.
- [ ] 3.2 Regenerate `tests/running-corpus.json` with
      `python tools/generate_running_corpus.py`. Show the diff in
      `evidence.md` and confirm it is the two `Train` entries' documents
      and nothing else — no tick, no script, no machine.
- [ ] 3.3 Confirm the other six base documents are byte-identical and
      that `ByteIdentityTest` passes over all seven.

## 4. Proof

- [ ] 4.1 `tests/test_running_document.py`,
      `tests/test_running_simulation.py`, `tests/test_running_stops.py`,
      `tests/test_running_jumps.py` and `tests/test_running_corpus.py`
      green; then the whole suite, with the counts in `evidence.md`
      against the baseline of 1.1.
- [ ] 4.2 Re-run `evidence/probe_repeat_port.py`,
      `evidence/probe_omitted.py` and `evidence/probe_repeat_joint.py`
      against the changed worktree and paste the output beside the
      before, so the two refusals are shown gone and the third —
      the repeat copy that owns a JOINT — is shown unchanged.
      `evidence/probe_pruned.py` becomes redundant at that point: record
      that its predictions matched, and say where they did not.
- [ ] 4.3 Publish the originating project's machine: build
      `projects/Locks/Pin_tumbler_lock` with its springs restored to a
      `.repeat()` and record that `solid build` succeeds. If the project
      is not restorable inside this cycle, say so and record the reduced
      fixture as the only evidence.

## 5. The record

- [ ] 5.1 `docs/architecture.md`: the running-program synthesis says what
      the compiled program's coordinates are.
- [ ] 5.2 `docs/changelog.rst`.
- [ ] 5.3 `workflow/warts.md`: mark the two findings fixed by this
      change, naming it, and leave the repeat-JOINT half filed with what
      `evidence/probe_repeat_joint.py` measured about it.
- [ ] 5.4 Report for the pilot, outside this repository: the shop's
      `shop-skills/solid-node-api/SKILL.md` says a `.repeat()` child
      under a running root may own neither a joint nor a port a relation
      drives; the port half is now false and the joint half is true for
      a reason the skill does not give (the id grammar, at bank
      enumeration, not publication).
