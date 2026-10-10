## Context

Bench `fix-warts-3` at `47cfc89`. Interpreter check:
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/python -c 'import machinome; print(machinome.__file__)'`
prints `<bench>/machinome/__init__.py`. Binaries: OpenSCAD 2021.01
(`/usr/bin/openscad`), git 2.43.0, `xvfb-run` on the PATH, no `DISPLAY`.
The viewer package is installed editable from the workspace's
`machinome-viewer` checkout (`24d9ad2`).

`<bench>` = `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, and
`<scratch>` is the campaign scratchpad's `cycle5/` directory. Every command
below ran against the unmodified bench.

### 1. The generator's default path

`tools/generate_parity_fixture.py:70-79` computes, at import:

```python
ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
...
FIXTURE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, '..', 'machinome-viewer', 'machinome_viewer', 'widget', 'src',
    'parity-fixture.json')
```

and `main()` (`:478`) builds the whole fixture before it opens `FIXTURE`.
`ROOT/..` is the workspace only when `ROOT` is the primary checkout. From
`machinome/WTs/<name>/` it is `machinome/WTs/`:

```
$ env -C <bench> PYTHONPATH=<bench> .venv/bin/python tools/generate_parity_fixture.py
...
FileNotFoundError: [Errno 2] No such file or directory: '/home/asa/devel/machinome/machinome/WTs/machinome-viewer/machinome_viewer/widget/src/parity-fixture.json'
exit 1          (4.5 s, after the full build)
```

Git's common directory names the primary checkout from either place:

```
$ git -C <bench> rev-parse --git-common-dir
/home/asa/devel/machinome/machinome/.git
$ git -C /home/asa/devel/machinome/machinome rev-parse --git-common-dir
.git
```

From a worktree it is absolute. From the primary checkout it is relative
to the directory `-C` names. Joined to that directory, both give
`<primary>/.git`, whose parent is the primary checkout and whose
grandparent is the workspace.

The docstring's run instruction (`:56-59`) names
`machinome/viewers/widget/tools/generate_parity_fixture.py`, a path the
tool has not had since it moved to `tools/`.

`tests/test_generate_parity_fixture.py` already loads the tool with
`spec_from_file_location` and calls `uncovered_builtins`, `build` and
`sharing_cases`. Loading it evaluates `FIXTURE` from pytest's own
`sys.argv`. That is harmless only because nothing calls `main()`.

With an explicit path the tool works from the bench today:
`... tools/generate_parity_fixture.py <scratch>/parity-fixture.json`
writes 451 expression cases, 22 conversions and 4 flexible bindings of
3858 vertices. That file differs from the viewer's committed
`machinome_viewer/widget/src/parity-fixture.json`, last changed at the
viewer's `8495d74`:

- both have the same 451 keys and the same expected values;
- the conversions and flexible bindings are identical;
- 249 case expressions differ, because the bench shares subexpressions
  through a 145-entry `bindings` table where the committed fixture has 4
  entries.

The kinematics requirement "The parity corpus covers every symbolic
function" allows exactly that rewrite. Refreshing the viewer's file is
the viewer repository's business (Open Question 3).

### 2. `--preview`

`OpenScadRenderer.build_command` (`machinome/viewers/openscad.py:166`)
appends a bare `--preview` (`:180`) when `args.preview` is set, and then
the root's `.scad` path last. `args.render` is never read.

OpenSCAD 2021.01's own help:

```
  --render arg                 for full geometry evaluation when exporting png
  --preview arg                [=throwntogether] -for ThrownTogether preview
                               png
```

Direct probes on a `difference(){cube(10,center=true); sphere(6.5);}`:

| arguments before the file | exit | result |
|---|---|---|
| (none) | 0 | OpenCSG preview |
| `--preview` | 1 | usage dump on stdout, nothing on stderr |
| `--preview=` | 1 | usage dump |
| `--preview=opencsg` | 0 | byte-identical to the default image |
| `--preview=throwntogether` | 0 | ThrownTogether: the subtracted sphere drawn as a green body |
| `--preview throwntogether` | 0 | the same |
| `--render` | 1 | usage dump |
| `--render=cgal`, `--render=1` | 0 | CGAL render |

On `color("red") cube(10); translate([15,0,0]) color("blue")
sphere(5);`, the default image is red and blue, and the `--render=cgal`
image is all one yellow.

So the bare flag takes the `.scad` path as its value, and OpenSCAD is left
with no input file. `--preview=throwntogether` selects what
`machinome snapshot --preview` is documented to select:

- the `--help` text: "ThrownTogether preview (faster, may show
  artifacts)";
- `docs/reference/cli.rst`;
- ADR-021.

Through the framework:

```
$ env -C <bench> PYTHONPATH=<bench> .venv/bin/machinome snapshot tests/web_snapshot_project.py \
    --viewall --autocenter --imgsize 800x600 --preview -o <scratch>/f2-before-preview.png
INFO - viewers.openscad - Rendering .../tests/_build/web_snapshot_project-AsymmetricSnapshotPart-cbb97835ba9a.scad to ...
OpenSCAD rendering failed:

exit 1
```

The same command without `--preview` exits 0 and writes the image.
`OpenScadRenderer.render` prints only `e.stderr` (`:111`), so the usage
dump on stdout is lost (Open Question 2).

Originating project, 3DPrintedClocks at `ec2a05d`, with the command its
`simulation/early-clocks-2026-09-13.md` documents and `--preview` added:

```
$ env -C <3DPrintedClocks> PYTHONPATH=<bench> .venv/bin/machinome snapshot wall_clock_11 \
    --time 0 --imgsize 1200x1000 --autocenter --viewall --preview -o <scratch>/f2-clock11-before.png
OpenSCAD rendering failed:

exit 1 after 71 s
```

Without `--preview` it exits 0 after 9 s, since the build is now current,
and writes the clock: a long pendulum, with the movement at the top. The
project's `git status --short` was ` M screenshots/wall_clock_03.png`
and `?? WTs/` before and after every run.

A probe (`<scratch>/f2_equals_probe.py`, which patches `build_command` in
its own process to emit `--preview=throwntogether`) wrote both images:

- the fixture: 800x600;
- `wall_clock_11`: exit 0 after 8 s. The image shows the same clock and
  differs from the plain image's bytes.

OpenSCAD takes `--camera -20,0,0,55,0,25,60` as two tokens and renders
it, so the OpenSCAD renderer's camera needs nothing.

### 3. The web renderer's camera options

`BrowserRenderer.capture_command` (`machinome/viewers/browser.py:185`)
emits `"--view", "<6 numbers>"`, `"--up", "<3 numbers>"` and
`"--fov", "<number>"` as pairs of tokens (`:194-196`). The viewer's
parser (`machinome-viewer/machinome_viewer/cli.py:94-109`) declares
`--view` (`type=_view`), `--up` (`type=_triple`) and `--fov`
(`type=float`). argparse takes a separate token that begins with `-` as a
value only when it looks like a negative number (`-0.5`), never when it
is a comma tuple (`-0.24,0.34,0.9`). Through the viewer's own
`build_parser()`:

```
['--up', '-0.24,0.34,0.9']               -> error: argument --up: expected one argument (exit 2)
['--view', '-1,2,3,0,0,0']               -> error: argument --view: expected one argument (exit 2)
['--up=-0.24,0.34,0.9', '--view=-1,2,3,0,0,0']
    -> view=((-1.0, 2.0, 3.0), (0.0, 0.0, 0.0)), up=(-0.24, 0.34, 0.9)
```

As a process, with a staging directory that does not exist, the split
form exits 2 with that error after 0.05 s. The joined form reaches the
viewer's own refusal, `Error: Staged document not found: .../viewer.json`,
with exit 1, and starts no browser.

Through the framework, Voron-2's command against the framework's own
asymmetric fixture:

```
$ env -C <bench> PYTHONPATH=<bench> .venv/bin/machinome snapshot tests/web_snapshot_project.py \
    --renderer web --autocenter --viewall --imgsize 1400x1100 --camera 0,0,0,65,0,35,1400 \
    -o <scratch>/f3-before.png
Error: usage: machinome-viewer capture [-h] -o OUTPUT [--imgsize WxH] [--time TIME]
                                [--view EYE,TARGET] [--up X,Y,Z] [--fov FOV]
                                staging
machinome-viewer capture: error: argument --up: expected one argument
exit 1
```

A probe (`<scratch>/f3_equals_probe.py`, the same patching for
`capture_command`) ran the same command. The viewer received:

- `--view=727.7715070159583,-1039.3654271085456,591.6655664369792,0.0,0.0,0.0`;
- `--up=-0.242403876506104,0.34618861305875415,0.9063077870366499`;
- `--fov 22.5`.

It exited 0 in 2.9 s and wrote a 1400x1100 transparent PNG. The part sits
small at the centre, because the camera's distance is 1400 mm and the part
is 32 mm long. It is seen from above and in front, with its tall block at
the back right.

## Goals / Non-Goals

**Goals:**

- The generator runs with no argument from the primary checkout and from
  any worktree, writing the viewer's committed fixture. With no viewer
  checkout to find, it refuses by name before building.
- `machinome snapshot --preview` writes the ThrownTogether image.
- A camera of any signs reaches the viewer's capture intact.

**Non-Goals:**

- `--render`'s meaning, the snapshot's failure message, machinome's own
  `--camera` parsing, and the viewer's committed fixture (proposal,
  "Deliberately out").
- Any new option, environment variable or configuration key.

## Decisions

### 1. The generator resolves through Git's common directory, and refuses otherwise

**Choice:** with no argument, find the primary checkout as the parent of
`git rev-parse --git-common-dir`, run in the tool's own checkout, and
write to `<primary>/../machinome-viewer/machinome_viewer/widget/src/parity-fixture.json`.
That is the rule the workspace contract gives for workspace paths ("from
a workspace worktree, locate it through Git's common directory"). When git
is missing, the directory is no Git checkout, or the viewer's `widget/src`
directory does not exist there, exit before `build()` with one message.
It names the directory looked for and says the output path may be given
as the first argument.

**Alternatives:**

- **Require the argument.** This is the entry's second remedy. It loses
  the no-argument run from the primary checkout, which the tool documents
  and which works today. The brief asks to keep both.
- **Ask the installed `machinome_viewer` where it lives** (`find_spec`).
  This works only for an editable install. Installed from PyPI, it would
  point the tool at `site-packages`, which is not the checkout that
  commits the fixture. It also ties the framework's tool to the viewer's
  installation, where only its source checkout matters.
- **An environment variable.** This is new vocabulary for one script,
  and nobody asks for one.
- **Parse `.git` files by hand** (`gitdir:` and `commondir`). This
  reimplements what one `git rev-parse` answers.

### 2. The generator's code shape

In `tools/generate_parity_fixture.py`:

```python
import subprocess

# The fixture is committed in the machinome-viewer repository, beside the
# evaluator it pins. ... (comment revised: where the default comes from)
VIEWER_FIXTURE = ('machinome_viewer', 'widget', 'src', 'parity-fixture.json')


def default_fixture(root=None):
    """The viewer's committed fixture, in the `machinome-viewer` checkout
    beside this framework's PRIMARY checkout -- found through Git's common
    directory, so the primary checkout and every worktree of it name the
    same file. Exits naming where it looked when there is none."""
    root = root or ROOT
    try:
        answer = subprocess.run(
            ['git', '-C', root, 'rev-parse', '--git-common-dir'],
            capture_output=True, text=True)
    except OSError:
        answer = None
    if answer is None or answer.returncode != 0:
        sys.exit(f'generate_parity_fixture: {root} is not a Git checkout, '
                 'so no machinome-viewer checkout can be found beside it; '
                 'give the fixture path as the first argument')
    common = os.path.normpath(os.path.join(root, answer.stdout.strip()))
    viewer = os.path.join(os.path.dirname(os.path.dirname(common)),
                          'machinome-viewer')
    target = os.path.join(viewer, *VIEWER_FIXTURE)
    if not os.path.isdir(os.path.dirname(target)):
        sys.exit(f'generate_parity_fixture: no machinome-viewer checkout '
                 f'beside the framework checkout (looked for '
                 f'{os.path.dirname(target)}); give the fixture path as '
                 'the first argument')
    return target


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    path = os.path.abspath(argv[0]) if argv else default_fixture()
    fixture = build()
    with open(path, 'w') as handle:
        ...  # unchanged
```

The module-level `FIXTURE` is removed. `if __name__ == '__main__':
main()` is unchanged. The messages may be reworded. What is fixed is
that each names the directory it looked at and the argument remedy, and
that it is raised before `build()`. The docstring's run section becomes:

```
Run from any checkout of the framework -- the primary one or a worktree
under WTs/:

    PYTHONPATH="$PWD" python tools/generate_parity_fixture.py [OUTPUT]

With no OUTPUT it writes machinome_viewer/widget/src/parity-fixture.json
in the machinome-viewer checkout beside the framework's primary checkout,
found through Git's common directory, and refuses before building
anything when there is none.
```

### 3. `--preview=throwntogether`, as one token

In `build_command`, `command.append('--preview')` becomes
`command.append('--preview=throwntogether')`, with a two-line comment:
OpenSCAD's `--preview` takes a value, and given bare it takes the next
token (the `.scad` path) as that value.

**Alternatives:**

- `['--preview', 'throwntogether']`: OpenSCAD accepts it as well. The
  joined form cannot be split by a later edit that inserts an option
  between the two tokens, and it matches Decision 4.
- `--preview=opencsg`: this produces the default image byte for byte, so
  the flag would do nothing, contradicting what it documents.

### 4. `--view=` and `--up=`, one token each

In `capture_command`:

```python
command += [
    "--view=" + ",".join(str(v) for v in (*camera.eye, *camera.target)),
    "--up=" + ",".join(str(v) for v in camera.up),
    "--fov", str(camera.fov),
]
```

with a comment saying why: argparse reads a separate token that begins
with `-` as an option unless it is a single number. `--fov` keeps two
tokens. Its value is one number, which argparse accepts even when
negative, and OpenSCAD's camera always resolves it to 22.5.

**Alternative:** join `--fov`, `--imgsize` and `--time` as well, for one
rule everywhere. None of them can fail, so the change would be larger
than the finding. It is not taken.

### 5. Specs

- `cli` "Snapshot command": one paragraph after the OpenSCAD-renderer
  paragraph, and one scenario.
- `web-snapshot` "A requested camera is honoured or refused, never
  approximated": one sentence and one scenario.
- `kinematics`: one ADDED requirement. The tool is the regeneration that
  "The parity corpus covers every symbolic function" already speaks of
  ("the regeneration fails naming the uncovered builtin").

Every existing scenario of the two modified requirements is carried
verbatim.

### 6. Manual and changelog

No manual page changes, because `docs/reference/cli.rst` already
describes the fixed behaviour. Two bullets go under `Unreleased`, after
the existing ones:

```
* **``machinome snapshot --preview`` draws.** The OpenSCAD renderer used
  to hand OpenSCAD a bare ``--preview``, which OpenSCAD 2021.01 reads as
  taking the model's ``.scad`` path for its value, so it printed its usage
  and the snapshot failed with no message. It now passes
  ``--preview=throwntogether``, the ThrownTogether preview the option has
  always been documented to select (tooling-paths-and-flags).
* **A camera vector beginning with a negative component photographs.** Under
  ``--renderer web``, a ``--camera`` resolving to an eye or an up direction
  whose first component is negative, such as ``0,0,0,65,0,35,1400``, was
  refused by the viewer's command line (``argument --up: expected one
  argument``); the framework now hands the viewer each camera vector in
  one token with its option (tooling-paths-and-flags).
```

The generator is not distributed (`tools/` is outside the package), so it
gets no changelog bullet.

## Proof plan

- **Red, finding 1** (`tests/test_generate_parity_fixture.py`, a new
  `DefaultFixturePathTest`). `setUp` builds, under a temporary `base`:
  - `base/framework`: `git init`, and one empty commit made with the
    environment of `tests/test_export_source.py`'s fixture (no `GIT_*`
    variables inherited, `GIT_CEILING_DIRECTORIES=base`,
    `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`, a fixture
    author and committer, `commit.gpgsign=false`);
  - `base/framework/WTs/bench`, made with `git worktree add -q`;
  - `base/machinome-viewer/machinome_viewer/widget/src/`.

  The tool's own git call runs under `patch.dict(os.environ, <that
  environment>, clear=True)`. The tests:
  - from the worktree, `default_fixture(<worktree>)` is
    `base/machinome-viewer/machinome_viewer/widget/src/parity-fixture.json`;
  - from `base/framework` it is the same path;
  - with the viewer directory removed, `SystemExit` names
    `machinome-viewer`, the directory looked for, and "argument";
  - from a plain directory that is no Git checkout, `SystemExit` names
    the directory and "argument";
  - `main([])`, with `ROOT` patched to that plain directory and `build`
    patched to fail if called, raises `SystemExit` and never calls
    `build`;
  - `main([<tmp>/out.json])`, with `build` patched to return a minimal
    fixture, writes `out.json`.

  On the unmodified tree the first four fail with `AttributeError: ...
  no attribute 'default_fixture'`, and the last two with `TypeError:
  main() takes 0 positional arguments but 1 was given`. These are a
  seam's reds. The behavioural red is the real run in Context §1, which
  stays recorded in evidence.
- **Red, finding 2** (`tests/test_snapshot.py`,
  `SnapshotCommandBuildingTest`):
  - `test_preview_flag` is rewritten to assert `'--preview=throwntogether'
    in cmd` and `'--preview' not in cmd`;
  - a new `test_preview_never_takes_the_scad_path_for_its_value` asserts
    that the token before `cmd[-1]` (the `.scad`) is
    `--preview=throwntogether` when only `preview=True` is set.

  Both fail today because the bare token is there.
- **Red, finding 3** (`tests/test_browser_renderer.py`,
  `CaptureDelegationTest`):
  - a new `test_a_negative_leading_vector_travels_with_its_option`. Its
    subtests are camera `0,0,0,65,0,35,1400`, whose up begins
    `-0.2424...`, and camera `-100,20,30,0,0,0`, whose eye begins `-100`.
    It asserts tokens starting with `--view=` and `--up=`, no bare
    `--view` or `--up` token, and the values parsing back to the
    resolved camera;
  - a new `test_the_viewer_parses_the_command_it_is_handed`, under
    `needs_viewer`. It runs `capture_command(<tmp>/missing, args(camera=
    '0,0,0,65,0,35,1400'), <tmp>/x.png)` as a process and asserts that
    the return code is not 2, that `expected one argument` is not in
    stderr, and that no image was written. Today it exits 2 with that
    error.

  The existing `test_a_requested_camera_is_resolved_here_and_handed_over`
  reads the value after a bare `--view` and `--fov`. It is revised to
  read `--view=` and `--up=`, and keeps its `--fov` checks.
  `test_no_camera_means_no_camera_flags` is revised to assert that no
  token starts with `--view`, `--up` or `--fov`, because `assertNotIn('--view',
  command)` would pass trivially once the tokens are joined.
- **Real runs after the change:**
  - Finding 2: Context §2's fixture command and 3DPrintedClocks'
    `wall_clock_11` command, both with `--preview`, write their images.
    Look at each and say what it shows. Record the project's `git status
    --short` before and after.
  - Finding 3: Context §3's Voron-shaped command writes its PNG. Look at
    it.
  - Finding 1: `python -c` loading the bench's tool prints
    `default_fixture()`, the viewer's committed fixture path, and
    `default_fixture('/home/asa/devel/machinome/machinome')` prints the
    same. That runs only `git rev-parse` in the primary checkout. The
    tool runs with `<scratch>/parity-fixture.json` and writes it. A real
    refusal: `GIT_DIR=<scratch>/no-such-git ... tools/generate_parity_fixture.py`
    exits non-zero with the message, in well under the 4.5 s a build
    takes. **No run without an argument is made**, because it would
    overwrite the viewer repository's committed fixture, which this
    campaign does not edit.
- **Suite:** the three test modules before and after, then the full
  suite once, alone.

## Risks / Trade-offs

- **Another OpenSCAD.** The probes cover 2021.01, the binary on this
  machine, and Ubuntu's `openscad` package, which CI installs on
  `ubuntu-latest` (`.github/workflows/python-app.yml`). Other releases
  were not probed. `throwntogether` is the value 2021.01 documents for
  the ThrownTogether preview, so a binary that rejected it would not
  offer the mode the flag documents in the first place.
- **A viewer that dropped `=` parsing.** argparse always accepts
  `--opt=value`, and the viewer parses with argparse. The process-level
  test under `needs_viewer` would catch a viewer that stopped.
- **The generator's git call** depends on `git` being on the PATH. The
  refusal names that case. CI and the workspace have git.

## Migration Plan

None. No document, identity or default image changes. A caller that
passed `--preview` got no image before, and gets the ThrownTogether
image now. A caller whose camera worked before gets the same image.

## Open Questions

1. **`--render`.** `machinome snapshot --render` is accepted, made
   mutually exclusive with `--preview`, and never forwarded. Its help
   says "Full render (the default, slower but accurate)", and
   `docs/reference/cli.rst` says "OpenSCAD's default". OpenSCAD 2021.01's
   PNG default is the OpenCSG preview. Its full render needs
   `--render=<value>`, is slower, and draws without the model's colours
   (Context §2). There are three choices:
   - **(a)** forward `--render` as `--render=cgal` and correct "the
     default" in the help and the manual. This changes what an existing
     flag draws;
   - **(b)** correct the wording only, saying a snapshot is OpenCSG's
     preview and `--render` changes nothing, or remove the flag;
   - **(c)** leave it here and file a wart.

   **Recommendation:** (c) in this change. These artifacts deliver it as
   tasks.md 7.3. The flag's meaning is a choice about appearance for the
   pilot, no sighting asks for it, and both (a) and (b) leave this
   change's three fixes exactly as they are. Answered by the
   orchestrator at review (6 October 2026): (c); the `--render` flag's
   meaning is recorded for the pilot as a wart.
2. **The empty failure message.** `OpenScadRenderer.render` prints only
   `e.stderr`, so a usage dump on stdout reaches the user as `OpenSCAD
   rendering failed:` and nothing. **Recommendation:** file it (tasks.md
   7.3) and do not fix it here. It is a reporting defect, outside "a
   command the framework composes is one its tool accepts". Answered by
   the orchestrator at review (6 October 2026): file it.
3. **The viewer's committed parity fixture** has fallen behind the
   framework's sharing of subexpressions. It has the same keys and
   values, but 249 expressions differ (Context §1). **Recommendation:**
   the orchestrator records it for the viewer, either in the campaign's
   cycle 19 (outside the framework) or under `warts.md`'s "Not framework
   fixes, still open". This change writes nothing in the viewer
   repository. Answered by the orchestrator at review (6 October 2026):
   recorded in the campaign note's cycle 19, the viewer's own step.
