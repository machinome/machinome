## Context

### Who renders a rigid internal node, and where the result is kept

Three paths render a non-assembly internal node (a `FusionNode`, or any
`InternalNode` subclass that is not an `AssemblyNode`):

- **Preparation.** `AbstractBaseNode._prepare()` (`machinome/node/base.py:891-916`)
  runs once per instance: an internal node never skips
  (`_prepare_can_be_skipped()` is `False` on the base), so it calls
  `render()`, validates the result, keeps it in `self._prepared_rendered`
  and materializes it. `trigger_stl()` (the build's per-node step, `:1163-1169`)
  and `assemble()` (`:849-889`) both start with `_prepare()`, and
  `assemble()` reads the same list again through `_require_rendered()`
  (`:918-923`), which renders only when `_prepared_rendered` is `None`.
- **The facade's walk.** `ModelSnapshot.occurrences`
  (`machinome/model.py:291-424`), in its `walk`, for a non-assembly internal
  node (`:353-365`):

  ```python
  if "_production_rest" not in node.__dict__:
      from machinome.node import phase

      token = phase._structure_only.set(True)
      try:
          children = node.render()
          node.validate(children)
      finally:
          phase._structure_only.reset(token)
      node.__dict__["_production_rest"] = tuple(children)
  children = node.__dict__["_production_rest"]
  node._link_children(children)
  ```

- **Every later `render()`.** The declarative wrapper
  (`machinome/node/internal.py:65-70`) returns `_production_rest` whenever
  it exists, so once the facade has read a node, preparation and every other
  caller reuse the facade's placements.

The facade knows its own cache and not preparation's. When the facade reads
first, preparation's `render()` returns `_production_rest` and the author's
code ran once. When preparation reads first, the facade does not see
`_prepared_rendered` and runs the author's `render()` a second time; a
`render()` that positions a child (`self.b.translate([1, 0, 0])`) appends a
second operation to the same child instance, and the wrapper then hands
that doubled list to every later caller.

Assemblies are not affected: `_rest` (`machinome/node/assembly.py:40-77`)
keeps a rest render on first call, and `_rest_children`, which the walk uses
for an assembly, goes through `_rest`.

### What the snapshot observes at construction

`ModelSnapshot.__init__` (`machinome/model.py:119-142`) observes the
loader's generation (when there is one) and then every existing node's
sources through `_capture_existing` (`:144-156`): `self._sources(node)` is
the node's `files` plus each class file of its MRO, all absolute
(`:196-203`). `observe_input` (`:205-227`) observes a path not seen before
with `_observe`, which opens it; any exception there becomes
`self._fail(f"input observation failed: {path}: {error}")`, which records
the snapshot as invalid and raises `ModelInputChangedError` (`:235-237`).
A path already observed is compared with its observation and refused as
`input changed`; `validate()` (`:239-257`) compares every observed path the
same way, and turns a failure to stat one (a deleted file) into `input
validation failed`.

So a path that never existed and a path that existed and changed reach the
same error and the same word, "changed".

### The production error taxonomy

`machinome/production/errors.py` defines five errors.
`DeclarationError` is a malformed declaration, at definition.
`BindingError` (a `ValueError`) is "a supplied instance or reference is
incompatible with its profile": the wrong model type at binding.
`ProductionConflictError` is overlapping ownership.
`ProductionInputChangedError` is "a shared binding generation changed;
construct a fresh binding".
`ProductionExportError` is "a requested instruction or export input cannot
be consumed".

The `production-assets` spec settles the changed case
(`ProductionInputChangedError`) and the missing instruction or evidence file
("Missing referenced files SHALL refuse requested steps/export
contextually", which the code does with `ProductionExportError`). It does
not name the error for a missing model source at binding. The constructor
already maps an input it cannot observe to `ProductionExportError`
(`machinome/production/profile.py:281-288`), and refuses an instruction that
escapes its directory at binding with `ProductionExportError` too
(`tests/test_production.py`,
`test_source_instruction_and_symlink_changes_invalidate_binding`).

## Goals / Non-Goals

**Goals:**

- The author's `render()` of a rigid internal node runs at most once per
  instance whether the lifecycle or the facade reads first, so a child's
  operations, every later `render()` and a regenerated fused artifact are
  the same in all four orders.
- A node source that does not exist when a model is bound is refused as
  missing, naming the node and the path: by the facade with
  `FileNotFoundError`, by `Production(model)` with `ProductionExportError`.
- A source that was observed and then changed or vanished keeps its
  existing refusal, `ModelInputChangedError` from the facade and
  `ProductionInputChangedError` from a production read.

**Non-Goals:**

- Changing the lifecycle, the declarative wrapper or `assemble()`.
- Changing `observe_input`'s public contract or the lazy walk's refusal of a
  source first met there (Open Question 2).
- Mapping a changed source at binding to `ProductionInputChangedError`
  (Open Question 3).
- Any item of the review's section other than the two named.

## Decisions

### 1. The walk reuses preparation's render

In the non-assembly branch of `walk` in `ModelSnapshot.occurrences`
(`machinome/model.py:353-365`), the render is taken from preparation when
preparation has one:

```python
                    else:
                        if "_production_rest" not in node.__dict__:
                            # Preparation already ran this instance's render
                            # and positioned its children; running it again
                            # would apply every placement a second time.
                            children = node.__dict__.get("_prepared_rendered")
                            if children is None:
                                from machinome.node import phase

                                token = phase._structure_only.set(True)
                                try:
                                    children = node.render()
                                finally:
                                    phase._structure_only.reset(token)
                            node.validate(children)
                            node.__dict__["_production_rest"] = tuple(children)
                        children = node.__dict__["_production_rest"]
                        node._link_children(children)
```

`node.validate(children)` moves out of the `try` so it validates both
branches; it reads only the children's types and rigidity, never the
structure-only flag. The failure cleanup is unchanged: it already saves and
restores `_production_rest`, and this branch writes nothing else
(`_prepared_rendered` is read, never written).

A Stage P probe in the scratchpad (`probe_remedy.py`), which seeds
`_production_rest` from `_prepared_rendered` after `trigger_stl()` and
before the facade reads, as this branch will, gives one operation on the
translated child, one from a later `render()`, and a regenerated fused STL
with the built content `f435a10c`, for the fusion alone and inside an
assembly.

Alternatives considered:

- **Render at most once in the declarative wrapper**, for every internal
  node. It would fix this walk and every other, but it changes the contract
  of `render()` for every tree walker (the serializer, the driver walk,
  state propagation), which re-render internal nodes by design, and it is
  not where the defect is.
- **Have the facade call `node._require_rendered()`.** One cache instead of
  two, but `_require_rendered()` writes `_prepared_rendered`, which the
  facade's failure cleanup does not restore, and it renders outside the
  structure-only flag.
- **Restore the operations after a second render.** It would hide the
  double render rather than avoid it, and the author's `render()` may do
  more than place.

### 2. The facade refuses a missing source at construction

`ModelSnapshot._capture_existing` (`machinome/model.py:144-156`) checks a
path before observing it:

```python
        for path in self._sources(node):
            if path not in self._inputs and not path.exists():
                raise FileNotFoundError(
                    errno.ENOENT,
                    f"{type(node).__name__} '{node.name}' names an input "
                    f"file that does not exist",
                    str(path),
                )
            self.observe_input(path)
```

with `import errno` among the module's imports. `str(error)` is then
`[Errno 2] Nut 'nut' names an input file that does not exist: '<path>'`;
`error.strerror` names the node and `error.filename` is the path.

- `path not in self._inputs`: a path the snapshot already observed (a
  loader generation's observation, or the same file named by two nodes) is
  never called missing here. A generation's file that vanished after the
  load is refused earlier, by `validate()` in `__init__`, as changed.
- `not path.exists()`: a dangling symlink is missing too. A file that
  vanishes between the check and the observation reaches `observe_input`
  and is refused as today, which is honest: it existed when checked.
- The snapshot is not marked invalid: the constructor raises, so no
  snapshot exists to poison.

Alternatives considered:

- **A new `ModelInputMissingError`** in `machinome.model`: new public
  vocabulary for one condition a builtin already names.
- **Change `observe_input`** to raise `FileNotFoundError` for any first
  observation of a missing path. It would also cover a child created inside
  `render()`, first met by the lazy walk, but there the walk's handler turns
  every non-`ModelInputChangedError` into `ValueError("model structure
  cannot be read: …")`, and production reads pass a `ValueError` through
  unmapped, so that case needs its own decision (Open Question 2). It would
  also change what a consumer gets from `observe_input` on a missing
  evidence path.
- **Leave the facade as it is and parse the message in `Production`**:
  string matching on another module's message.

### 3. `Production(model)` maps it to `ProductionExportError`

`Production.__init__` (`machinome/production/profile.py:281-288`) keeps its
`try` and its single `except OSError` branch, which now catches the facade's
`FileNotFoundError`, and rewords the message so it does not call every
unobservable input a profile input:

```python
            except OSError as error:
                reason = (
                    f"{error.strerror}: {error.filename}"
                    if error.filename
                    else str(error)
                )
                raise ProductionExportError(
                    f"{type(self).__name__} cannot bind: {reason}"
                ) from error
```

The production refusal reads
`HolderProduction cannot bind: Nut 'nut' names an input file that does not
exist: <path>`.

Why `ProductionExportError` (Open Question 1): it is the family the
constructor already uses for an input it cannot observe and for an
instruction that escapes its directory at binding, and the spec's family for
a missing instruction or evidence file at `steps` or `export`. A missing
model source is the same kind of fact: an input the binding cannot consume.
`BindingError` says the supplied instance is incompatible with the profile's
model type, which a missing file does not make it.
`ProductionInputChangedError` would repeat the defect's word.

### 4. The tests

In `tests/test_model_consumption.py`, after
`test_rigid_rest_placements_reused_by_normal_lifecycle`, with `os`,
`Path` (`from pathlib import Path`) and `_digest_bytes` (`from
machinome.core.pieces import _digest_bytes`) imported where they are used:

```python
class MeshBox(LeafNode):
    """A box that publishes its own STL: no renderer, no kernel."""

    def render(self):
        import trimesh

        return trimesh.creation.box(extents=(2, 3, 4))

    def materialize(self, rendered):
        self.publish_artifact(
            self.stl_file, lambda path: rendered.export(path, file_type="stl")
        )


class OffsetPair(FusionNode):
    a = MeshBox()
    b = MeshBox()

    def render(self):
        self.b.translate([1, 0, 0])


class HeldPair(AssemblyNode):
    pair = OffsetPair()


@pytest.mark.parametrize("kind", [OffsetPair, HeldPair])
def test_binding_after_a_build_keeps_rest_placements(
    kind, tmp_path, monkeypatch
):
    monkeypatch.setenv("SOLID_BUILD_DIR", str(tmp_path))
    model = kind()
    fusion = model if kind is OffsetPair else model.pair
    model.trigger_stl()
    built = _digest_bytes(Path(fusion.stl_file).read_bytes())
    operations = list(fusion.b.operations)
    assert len(operations) == 1
    snapshot = ModelSnapshot(model)
    occurrence = next(
        o for o in snapshot.occurrences if o.model_type is OffsetPair
    )
    assert fusion.b.operations == operations
    assert list(fusion.render()) == [fusion.a, fusion.b]
    assert fusion.b.operations == operations
    os.remove(fusion.stl_file)
    assert snapshot.geometry(occurrence).content_id == built
```

RED today for both kinds at the first operations comparison ("Left contains
one more item: <machinome.node.operations.Translation …>"). The regenerated
content identity is the end-to-end proof: with the doubling, the
reproduction's fused STL changed from `f435a10c…` to `fd3b003d…`.

```python
def test_missing_source_is_refused_at_construction(tmp_path):
    missing = tmp_path / "never-existed.txt"
    model = Machine()
    model.compound.files.add(str(missing))
    with pytest.raises(FileNotFoundError, match="Compound 'compound'") as refused:
        ModelSnapshot(model)
    assert refused.value.filename == str(missing)


def test_source_deleted_after_binding_is_still_a_change(tmp_path):
    from machinome.model import ModelInputChangedError

    present = tmp_path / "present.txt"
    present.write_text("observed")
    model = Machine()
    model.compound.files.add(str(present))
    snapshot = ModelSnapshot(model)
    present.unlink()
    with pytest.raises(ModelInputChangedError):
        snapshot.occurrences
```

The first is RED today (`ModelInputChangedError: input observation failed`);
the second is a guard, green before and after. `Machine` and `Compound` are
the module's existing fixtures; at Stage P `Machine().compound.name` is
`'compound'`.

In `tests/test_production.py`, beside
`test_bad_constructor_inputs_fail_immediately`:

```python
def test_missing_model_source_is_refused_at_binding(tmp_path):
    from machinome.model import ModelInputChangedError
    from machinome.production.errors import ProductionExportError

    missing = tmp_path / "never-existed.txt"
    model = Root()
    model.left.nuts[0].files.add(str(missing))
    with pytest.raises(ProductionExportError) as refused:
        RootProduction(model)
    message = str(refused.value)
    assert "RootProduction cannot bind" in message
    assert "Nut 'nuts-0'" in message
    assert str(missing) in message
    assert not isinstance(refused.value, ModelInputChangedError)
```

RED today (`ModelInputChangedError` is raised, not `ProductionExportError`).
At Stage P `Root().left.nuts[0].name` is `'nuts-0'`.

Each red test is run and seen red, for the reason named, before the code
changes.

### 5. Records

Changelog, appended to the one `Unreleased` section of
`docs/project/changelog.rst` after its existing bullets:

```rst
* **A production bound after a build reads the machine as built.** Binding
  a ``Production`` or a ``ModelSnapshot`` to a model that was already
  built, snapshotted or served no longer runs a fusion's ``render()`` a
  second time: the children it positions keep their one placement, a later
  ``render()`` returns them as they were, and a fused STL made again is the
  one the build made. A file a node names that does not exist is refused
  when the model is bound, as missing and naming the node and the path,
  with ``ProductionExportError`` from ``Production(model)`` and
  ``FileNotFoundError`` from ``ModelSnapshot(model)``; it used to be
  reported as an input that had changed (production-reads-once).
```

`workflow/warts.md`: the two items move verbatim to
`workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
`` ## `production-reads-once` `` with a "What shipped" paragraph; the
section's other items stay. Open Questions 2 and 3 are filed as a new
section "## Findings from the framework cycle `production-reads-once`
(2026-10-07)", placed after the section "## Findings from the framework
cycle `clocked-snapshot-identity` (2026-10-07)".

No manual page changes (proposal, Impact). No ADR.

## Proof plan

1. Baseline on the unmodified tree: the scratchpad scripts
   `repro_doubling.py` and `repro_missing.py` print the outputs quoted in
   the proposal; the focused suites `tests/test_model_consumption.py
   tests/test_production.py tests/test_production_documentation.py` pass
   (52 passed in 7.55 s at Stage P); the Curta production slice, run as
   the proposal's Impact describes, passes 6 tests (119.02 s at Stage P,
   wall 120.10 s, warm build directory).
2. The four red tests are seen red for the reasons above; the guard is
   green.
3. After the change: the four are green, the guard and every focused test
   still pass; `repro_doubling.py` prints one operation and the built
   content identity in all four orders, and `repro_missing.py` prints
   `ProductionExportError` and `FileNotFoundError` naming `Nut 'nut'` (the
   child case) and `Root 'Root'` (the root case).
4. The Curta slice passes the same 6 tests, timed against the same warm
   build directory as the baseline.
5. `black --check`, `flake8 --max-line-length=89` on the touched files;
   the full suite once, alone.

## Risks / Trade-offs

- **A node rendered by preparation and later changed by its author's own
  code** before binding would be read as preparation left it. That is the
  instance's actual rest, which is what the facade reads.
- **`FileNotFoundError` from `ModelSnapshot`** is a new exception type for
  a direct facade consumer that caught `ModelInputChangedError` for this
  case. No project constructs a `ModelSnapshot` over a model naming a
  missing file; the only project consumer is the Curta slice's test.
- **The check-then-observe window** at construction can let a file that
  vanishes in between be reported as changed. It existed when checked, so
  the report is not false.

## Open Questions

1. **Which production error refuses a missing model source at binding?**
   The spec names none. Recommendation, and what these artifacts deliver:
   `ProductionExportError`, the family the constructor already uses for an
   input it cannot observe and the spec's family for a missing instruction
   or evidence file (Decision 3). The other candidate, `BindingError`,
   would say the instance is of an incompatible type. Answered by the
   orchestrator at review (7 October 2026): `ProductionExportError`.
2. **A missing source on a child that only `render()` creates** is first
   met by the lazy structural walk, not at construction, and still reads as
   `ModelInputChangedError: input observation failed` (and
   `ProductionInputChangedError` from a production read). Reproduced at
   Stage P with an assembly whose `render()` returns a freshly constructed
   leaf naming `/nonexistent/render-made.txt`. Recommendation: leave it to
   a later cycle and file it as a finding; refusing it as missing needs a
   choice of how the walk's `ValueError` wrapping and production's reads
   carry it, and the review did not meet the case. Answered at review
   (7 October 2026): filed as a finding.
3. **A source changed between a verified load and binding** escapes
   `Production(model)` as `ModelInputChangedError`, not
   `ProductionInputChangedError`: `ModelSnapshot.__init__` refuses the
   changed generation (as
   `tests/test_model_consumption.py::VerifiedModelGenerationTest::test_changed_executed_source_cannot_be_bound_as_verified`
   shows) and `Production.__init__` catches only `OSError`.
   Recommendation: file it as a finding; the brief keeps the facade's error
   for a file that did change as it is, and mapping it changes the type a
   caller of `Production(model)` catches. Answered at review (7 October
   2026): filed as a finding, confirmed by the applier (tasks 6.2).
