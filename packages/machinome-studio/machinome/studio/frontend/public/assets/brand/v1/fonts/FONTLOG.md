# Machinome Logo — font adaptation record

Version 1.000 · 20 September 2026 · based on Anta Regular.

The pilot selected Anta after comparing the original signature, integrated-initial variants, six typeface studies, and five rounded-M alternatives. The rounded alternatives softened the identity too far; the final combination deliberately keeps a rounded moving linkage and Anta’s mechanical lettering.

## Changes from Anta

- Family renamed **Machinome Logo**; PostScript name **MachinomeLogo-Regular**. This is a distinct derivative, not an upstream Anta release or endorsement.
- Ordinary capital **M**, Unicode **U+004D**, replaced with the original Machinome linkage. Type `Machinome` to obtain the integrated wordmark; no duplicated initial or private-use character is needed.
- Five dots are true transparent counters. Color comes from the host application; the font contains no color layers.
- M targets Anta’s capital height: **0–1422 font units**, on Anta’s 2048-unit em. Its actual converted outline is **0–1422.3333** (less than 0.02px difference at the 72px specimen size). Its aspect ratio is preserved within integer-grid rounding and cubic-to-quadratic conversion (maximum approximation error 0.25 font units before grid rounding). Control-point bounding boxes are not the visible outline bounds.
- M advance adjusted to preserve Proposal 07’s 0.12-cap-height visible gap to `a` when tracking is −0.01em and kerning is off.
- Subset to exactly **nine encoded characters**: `M a c h i n o m e`, plus the required unencoded `.notdef` glyph. The eight retained lowercase outlines, advances and Unicode mappings are unchanged. Every other character is omitted. Unused layout tables are removed; the wordmark uses explicit tracking, not contextual substitutions.
- Name/version metadata updated; original copyright and OFL information retained, with adaptation attribution added. Timestamp recalculation is disabled for repeatable builds.

TTF is provided for installation in desktop tools; WOFF for web use. Only regular weight exists. No artificial bold, italics, width changes, or case transformations are part of the identity. This is a fixed-wordmark asset, not a body/UI replacement for Anta. Subsetting does not enforce intent: unrelated words can still use the same letters.

The original Anta font remains unchanged in `assets/fonts/Anta-Regular.ttf`. Its pinned distribution and author credits are recorded in `SOURCES.md`. The source builder is `scripts/build_identity.py`.

## License boundary

The complete derived font, **including its new M glyph**, is distributed under SIL OFL 1.1; see [OFL.txt](OFL.txt). A font license is not a grant to impersonate Machinome or a trademark clearance. Separate logo artwork and repository code are not automatically put under OFL by using this font. No repository-wide artwork or trademark license is declared here.

## Supported use and validation boundary

Use the supplied `identity.css` only on the exact isolated text `Machinome`: weight 400, tracking −0.01em, kerning and ligatures off. A logo component must hard-code that word and accept presentation options, never arbitrary text/children. Do not put the font on body, headings, containers, navigation, product qualifiers, user input, or fallback font stacks. Desktop tools need equivalent settings (tracking −10 in applications using 1/1000-em units). The guide deliberately has a fixed specimen, not a text editor. These are integration rules, not additions to the OFL license.

The TTF and WOFF are structurally checked, including exact character coverage and the eight retained lowercase glyphs against Anta. Browser rendering is checked in Chromium; tests also check that the guide’s general text never uses this font. Cross-browser and desktop-editor rendering remain to be checked before an application makes the font its only logo path. Outlined SVGs are the canonical cross-application assets; they require no font loading.
