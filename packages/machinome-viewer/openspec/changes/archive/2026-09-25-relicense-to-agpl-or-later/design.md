## Decisions

**D1. The grant is the SPDX expression, stated everywhere the old one
was.** `AGPL-3.0-or-later` replaces `AGPL-3.0-only` in every header, both
manifests and the banner the bundle carries, so a recipient of any file, of
the wheel or of a conveyed bundle reads the same grant. The `LICENSE` file
stays the AGPL version 3 text as the FSF publishes it; the version-or-later
choice is not part of that text.

**D2. No `License ::` classifier**, as before: the SPDX `license` field in
`pyproject.toml` is the declaration.

**D3. The 0.7.0 record states the grant it ships with.** 0.7.0 is
unpublished and its tag is re-cut on the integrated head, so the changelog's
0.7.0 "Identity and licensing" bullet and the release record say
`AGPL-3.0-or-later`; no unreleased section is opened.
