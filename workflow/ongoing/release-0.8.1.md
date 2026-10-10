# Machinome 0.8.1: release handoff

Status: working record, 10 October 2026, written by the OpenSpec change
`release-0-8-1` (bench `release-0-8-1`, base `31c8507`). Not ratified; the
change's archive is the authority for what was released.

## What the release state is

Version 0.8.1 in the five files of `setup.cfg`'s bumpversion table, dated
10 October 2026 in `docs/conf.py`'s release block, with the matching viewer
0.8.1, API 29, document versions 1 to 13. The changelog's `Machinome 0.8.1`
section, `HISTORY.rst`, the 0.8 release note's last section, the upgrading
page's first part and `context7.json` describe it as released. The `viewer`
and `web-snapshot` extras require `machinome-viewer>=0.8.1`.

The viewer's 0.8.1 is the published 0.8.0 renumbered (viewer change
`release-0-8-1`, tagged `v0.8.1` in its repository).

Machinome 0.8.0 is on PyPI (uploaded 6 October 2026) from the tag `v0.8.0`
(`d22d0a1`); nothing in this record changes it.

## The pilot's steps

1. Upload `machinome-viewer` 0.8.1 first: `machinome[viewer]` 0.8.1 does not
   resolve until it is on the index, and neither does the documentation CI
   job, which installs the viewer from PyPI.
2. Push the framework's `main` and the `v0.8.1` tag.
3. Upload the framework's distributions, built at the tagged commit.
4. The Read the Docs builds of `latest` and `v0.8.1`, for both manuals.
5. The Context7 refresh from `context7.json`, for both packages.
