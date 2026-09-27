# Stable mate rotation conversion

Status: provisional pre-spec intent, 27 September 2026. This is evidence and
intent, not an implemented capability; the OpenSpec change will govern the
fix. The pilot explicitly ratified this no-interface-change numerical fix
and the empirical ratification process for such fixes; interface changes
still require prior presentation to the pilot.

Curta selector 6's pure Z -95.6-degree rotation obtains false X/Y axis
components from diagonal cancellation followed by square roots. The unchanged
physical-basis test detects about 1.0524e-8 mm pose error, not a proven fit
failure. See `../warts.md` for the precise witness and project files.

Keep the existing rotation angle, operation order, identity omission and
`1e-9` snap contracts. Recover nondominant axis components stably rather than
enlarging snap or loosening caller tolerance. A dominant-component square root
with symmetric off-diagonal recovery is a candidate; exact half-turn equal
components need explicit compatibility proof, not an assumed algorithm.

Require red-first pure-matrix and public-mate regressions, all signed principal
axes, genuine small components above snap, near/exact half-turns, existing
equal-component tests and the unchanged Curta caller comparison. No new API,
viewer/Studio change, global numerical cleanup or gratuitous ADR belongs here.
