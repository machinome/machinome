## Context

Both entry points already read the project's runtime selection before loading a
profile — `_serve` in `floor/orchestrator.py` and `main` in `floor/__main__.py`
each call `read_project_runtime(...)` and then
`resolve_profile_runtime(load_profile(...), selection)`. ADR 0017 required that
ordering so per-agent selections could be resolved against the profile's roster
without touching the project first. It happens to be exactly the ordering this
change needs: the profile's identity can come out of the same bounded read that
already produces the selections, with no new pass over the project and no new
side effect.

The prohibition being reversed is one sentence in `shop-runtime-profile`: *"A
project repository MUST NOT supply or override a runtime profile."* Its original
reasoning was that a profile is a trusted repository-owned package and a project
must not be able to reach into runtime policy. That reasoning survives intact for
the *contents* of a profile; what changes is that pointing at one of the shop's
own packages is now allowed.

## Goals / Non-Goals

**Goals:**

- A project records the roster it is normally worked under, durably, in the file
  that already records its per-agent runtimes.
- One precedence chain, stated once and shared by both entry points.
- `fordesmac` as the shop default.
- A wrong profile is loud. Never silently substitute a different roster.

**Non-Goals:**

- Separating tool and permission policy from the profile package. Real, raised
  by the pilot, and deliberately not attempted here.
- Making the profile immutable per project, or recording the profile a run
  actually used anywhere other than the pilot's own configuration.
- Any change to the profile schema, topology validation, prompts, or skills.
- Removing `--profile`, which ADR 0017's reasoning about `--backend` would
  otherwise suggest. See the first decision.

## Decisions

### Keep `--profile` as an override rather than removing it

ADR 0017 removed `--backend` on the principle that two sources of truth for one
value is the problem being solved. That principle is not applied here, for two
reasons the backend case did not have.

The first is bootstrapping. The launcher scaffolds a project that does not exist
yet, and the scaffold deliberately carries no shop configuration. If the project
file were the only source, every new project's first floor would open under the
default roster, and reaching another one would mean opening a floor, closing it,
editing `pyproject.toml`, and reopening. The flag makes the first run of a new
project as expressive as the hundredth.

The second is that the profile selects a roster, not a parameter. Opening a
Fordesmac project under a single Builder for one quick fix is a legitimate,
recurring act that leaves nothing about the project changed. A backend swap had
no equivalent motivation.

The cost is accepted honestly: what built a project is now recorded only as
"what normally builds it". A run under an override leaves no trace, exactly as
it does today.

Alternative rejected: error when flag and project disagree. It makes the
override useless for the case that motivates keeping it.

### Validate shape always, resolution only when used

A `profile` value that is not lowercase kebab-case is rejected on every run,
because no invocation could make it meaningful — it is a parse error in the same
class as a malformed agent key, which `read_project_runtime` already rejects
unconditionally. A well-formed value that names a profile this checkout does not
provide is rejected only when the run actually uses it.

This split keeps `read_project_runtime` a pure parse of one file with no
knowledge of the `profiles/` directory, and it keeps a project openable from a
checkout or plugin install that ships a different profile set, as long as the
pilot names one that exists. The visible consequence is that a typo in the
project's profile name stays hidden for as long as every run passes `--profile`.
That is the same tolerance the roster already grants to agent keys outside the
active profile, and it surfaces the moment the flag is dropped.

Alternative rejected: resolve the project's declared profile on every run even
when overridden. It would catch the typo earlier, but it makes a valid explicit
invocation fail for a value it is not using, and it couples the project file to
one checkout's profile set.

### Attribute the error to the file the pilot must edit

`load_profile` raises `ProfileError` today, phrased for a flag-supplied name.
When the name came from the project, the message must name the project's
`pyproject.toml` and the offending value instead, because that is the file the
pilot has to change. The implementation carries the origin alongside the
resolved name rather than inspecting the exception, so the two sources stay
distinguishable at the one place that knows which won.

### Change the default in the same cycle, as its own decision

Flipping the default from `builder` to `fordesmac` is independent of
project-declared profiles: it would stand alone and it is recorded as its own
decision in the ADR. It ships here because both touch the same resolution point
and splitting them would mean two cycles editing one function and the same four
documents. It is the breaking part of this change — a bare
`python -m floor.orchestrator gearbox` now opens four standing sessions where it
opened one.

## Risks / Trade-offs

- **A pilot's habitual bare invocation now opens four sessions and their
  backends.** → The default change is stated as **BREAKING** in the proposal, the
  ADR, and `skills/running-the-shop/SKILL.md`, whose parameter section names the
  default explicitly. There is no silent path: the roster is visible in the
  browser the moment the floor opens.

- **A project declaring a profile is less portable across shop installs**, since
  a plugin install with a different profile set cannot open it without a flag. →
  Accepted, and mitigated by rejecting rather than falling back: the pilot is
  told which file and value to fix instead of getting an unexpected roster.

- **Selecting a profile is indirectly selecting the tool and permission policy
  that profile carries.** → Bounded by the profile set being repository-owned and
  trusted in its entirety: a project can only choose among policies the shop
  already ships, never author one. The spec states this explicitly rather than
  leaving it implied. The layering question the pilot raised remains open work.

- **A typo in a project's profile name can hide behind a habitual `--profile`.**
  → Accepted, per the second decision, and consistent with how out-of-roster
  agent keys already behave. Unlike those keys, the profile is not reported when
  overridden; adding a warning was considered and rejected as noise on every run
  of a legitimately overridden project.

## Open Questions

None blocking. The tool-and-permission layering the pilot raised is recorded as
out of scope rather than as a question this cycle answers.
