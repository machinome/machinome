# Scripted camera for the Leonardo sawmill video

The pilot commissioned Videomaker and its first narrated hydraulic-sawmill
video on 19 September 2026. Its existing YAML screenplay requires camera
transitions between the wheel, saw, feed train and whole assembly. Mount-time
camera options and read-only `view()` cannot express them on one loaded viewer.

Add a public `setView({camera, target})` operation, preserving model state and
rendering the new view synchronously. Keep Three.js private as ADR-035 requires.
No framework, document, time or machine contract changes. API 21 adds this host
capability. The user's request authorizes this narrowly required implementation.
