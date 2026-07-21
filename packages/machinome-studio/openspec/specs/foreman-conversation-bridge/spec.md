# foreman-conversation-bridge Specification

## Purpose

Give the active foreman direct access to the shop-floor broker for queued
maker messages and independently chosen foreman messages.

## Requirements

### Requirement: The foreman directly receives queued maker messages
The shop-floor broker SHALL provide the foreman a direct receive operation that
accepts the last handled conversation sequence, waits until at least one later maker message is
available to the active foreman conversation, then returns all later maker
messages queued at that time in recorded order and the new sequence.

#### Scenario: The foreman waits for maker direction
- **WHEN** the foreman invokes the receive operation before the maker sends a message
- **THEN** the operation waits and returns the maker message after it is submitted

#### Scenario: The foreman resumes listening after work
- **WHEN** multiple maker messages arrive while the foreman is handling an earlier message
- **THEN** the next receive command returns those queued messages in recorded order

#### Scenario: The foreman continues after handled messages
- **WHEN** the foreman invokes the receive operation with the sequence returned by its prior receive operation
- **THEN** the operation does not return maker messages at or before that sequence

### Requirement: The foreman directly publishes independently chosen messages
The shop-floor broker SHALL provide the foreman a direct publish operation that
records a foreman message in the active conversation without requiring a
pending maker message.

#### Scenario: The foreman reports progress
- **WHEN** the foreman decides that progress or clarification warrants a message
- **THEN** it can publish that message to the maker conversation
