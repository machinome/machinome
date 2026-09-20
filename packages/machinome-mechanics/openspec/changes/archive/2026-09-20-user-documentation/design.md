## Context

The twelve existing functions and their tests are the API authority. The only
three files in `docs/` are internal records. The framework uses reStructuredText,
Sphinx and `sphinx_rtd_theme`. Both packages await publication.

## Goals / Non-Goals

Goals: a complete, readable user manual, buildable on Read the Docs, with tested
examples and discoverable navigation. Non-goals: formula changes, new helpers,
CAD demonstrations, release/push, or spec sync/archive before pilot approval.

## Decisions

- Use the framework's Sphinx/Read the Docs theme and RST conventions, with a
  landing page, getting started, conventions, framework integration, a reference
  index and five family pages. Document every argument and result with examples.
- Use Sphinx Python-domain function directives with explicit signatures and
  editorial descriptions. Check signatures and coverage against the actual public
  exports. Autodoc would import the framework's CAD stack during an otherwise
  textual build and expose internal provenance prose as user instructions.
- HTML builds need only pinned Sphinx/theme dependencies. A separate doctest
  build uses real installed mechanics/framework code, without mocks. This avoids
  relying on unpublished packages to host the manual while proving its examples.
- Put internal records and maintainer build/hosting instructions in `workflow/`.
  Preserve the three existing records with moves. Fix live links; leave historical
  archived OpenSpec records unchanged. A baseline provenance path correction is
  deferred with spec sync until pilot approval.
- Use `https://machinome-mechanics.readthedocs.io/en/latest/` as the intended
  manual address and link back to `https://machinome.readthedocs.io/en/latest/`.
  Building locally does not prove that the hosted project exists.

## Risks / Trade-offs

- Manual signatures can drift → test all exported names and signatures and run
  all doctests on the real API.
- Numeric examples can hide frame mistakes → state the frame, zero, direction,
  units and branch on each family page; use known geometric identities.
- Hosting needs project configuration → supply the RTD config and document the
  one-time project import and intended slug; do not claim an online deployment.

## Working record and approval

Independent repository worktree: `/home/asa/devel/machinome-studio/WTs/mechanics-user-docs`.
Branch `user-documentation`, base/main `7b8d5bba4b47df88d1e5c459ef4badc9f7593d19`.
Pre-ratified 2026-09-20. Planning is committed before implementation. Keep the
implementation open and serve it for pilot approval before sync/archive.
