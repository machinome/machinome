## MODIFIED Requirements

### Requirement: Profile prompts and skills are contained and allowlisted
Each agent prompt SHALL be a regular file contained by its profile directory.
Its frontmatter SHALL identify the same agent ID and SHALL explicitly list the
skills that agent requires. Every listed skill SHALL resolve through that
profile's `skills/<skill>/SKILL.md` allowlist.

A profile-local skill SHALL be contained by the profile. A shared skill SHALL
be exposed by an individual symlink resolving to one skill directory directly
beneath `shop-skills/`. The loader MUST reject broken links, file links,
transitive filesystem escapes, links into repository `skills/`, links into
another profile, and prompt skill names absent from the profile allowlist.
Runtime agents MUST NOT resolve skills from the repository-development
`skills/` namespace.

Every allowlisted skill SHALL describe itself: its `SKILL.md` frontmatter
SHALL declare a `name` equal to the allowlisted skill name and a non-empty
`description`, and the loader SHALL resolve that name, description, and
directory together. A skill whose frontmatter is missing, unterminated,
mismatched, or without a description SHALL fail profile validation, because a
skill that cannot be announced cannot be chosen.

#### Scenario: A profile exposes a shared shop skill
- **WHEN** `profiles/builder/skills/solid-node` is an individual symlink resolving to `shop-skills/solid-node`
- **THEN** a Builder prompt that declares `solid-node` passes skill validation

#### Scenario: A prompt names an unavailable skill
- **WHEN** an agent prompt declares a skill not present in its profile's `skills/` directory
- **THEN** profile validation fails before starting the project or runtime

#### Scenario: A skill link escapes its runtime namespace
- **WHEN** a profile skill link resolves into repository `skills/`, another profile, or any location outside `shop-skills/<one-skill>`
- **THEN** profile validation fails

#### Scenario: An allowlisted skill does not describe itself
- **WHEN** an allowlisted skill's `SKILL.md` has no frontmatter, a `name` other
  than the allowlisted skill name, or an empty or missing `description`
- **THEN** profile validation fails before starting the project or runtime

#### Scenario: A validated skill carries its announcement
- **WHEN** a profile agent's skills are resolved
- **THEN** each resolved skill carries the name and description its `SKILL.md`
  declares alongside its directory
