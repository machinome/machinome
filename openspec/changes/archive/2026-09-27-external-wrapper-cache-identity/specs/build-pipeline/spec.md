## ADDED Requirements

### Requirement: External wrappers own independent current artifacts

Different source-bound wrapper classes distinguished by their defining Python
source and qualname SHALL own independent cached artifacts even when they
refer to the same external asset with identical parameters. A build containing
those wrappers SHALL terminate with each wrapper's geometry and currency
record current simultaneously, rather than repeatedly overwriting and
invalidating another wrapper's artifact. Artifact layout and existing source
and producer-recipe currency checks SHALL otherwise remain unchanged.

#### Scenario: Different STL adjustments remain independently cached

- **WHEN** two same-qualname wrappers defined in different Python files import
  one STL, apply different geometry adjustments and have different tracked
  source mtimes and digests, and a model containing both is built
- **THEN** the build terminates, each cached STL contains its own adjusted
  geometry, and both artifacts and currency records are current together
- **AND** rebuilding the unchanged model does not regenerate either STL

#### Scenario: STEP wrappers retain both exact and faceted artifacts

- **WHEN** two same-qualname wrappers defined in different Python files select
  one STEP source and apply different adjustments, and both are built
- **THEN** each wrapper has its own correct STL and BREP artifacts, each pair
  is current together, and rebuilding does not regenerate either pair

#### Scenario: Source edits still invalidate through ordinary currency

- **WHEN** one wrapper's geometry-affecting Python source or tracked helper is
  edited after both wrappers' artifacts are current
- **THEN** its existing key is unchanged and its affected artifacts rebuild
  according to existing source currency, without accepting the old geometry
- **AND** the other wrapper is invalidated only if its tracked sources or
  recipe changed under those same existing rules
