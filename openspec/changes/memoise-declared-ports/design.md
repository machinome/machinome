## Context

`declared_ports` walks every class dictionary in the MRO on every call. Its duck-typed probe of each value can enter a `ChildDeclaration.__getattr__`, which asks for port declarations again. The Curta has many class specializations and repeated lookup in construction and propagation. A bounded cProfile attributed 39.2/77 seconds to this path. The 2026-09-19 performance record measured a prototype speedup on Curta construction and ticks.

## Goals / Non-Goals

**Goals:** Retain port enumeration semantics, fresh caller-owned mappings, and collectible generated classes while avoiding repeated traversal of a completed class.

**Non-Goals:** Change the 64-sample constraint search, source timing, carry, stop laws, or any public declaration syntax.

## Decisions

Store an immutable snapshot of `(name, port)` pairs on the exact class after its first enumeration **after `NodeMeta.__new__` completes**; each call returns a new `dict`. Lookup reads that class's own `__dict__`, so a subclass never inherits a base's cached map. A class owns its cache, so no process-global dictionary retains generated site-joint classes. `NodeMeta` marks each exact class complete as its final action. Enumeration during descriptor `__set_name__` or class validation remains uncached: the Curta's `RetainedCarriage.lift` has a `Bound` that checks reads while `lift.coordinates` still has a `None` key, before `Joint.__set_name__` finishes naming it. A first cache attempt froze that transient result and broke Curta import. Plain classes without `NodeMeta` retain the original uncached traversal. Declaration metadata is fixed after class completion; mutating classes afterward is outside the declaration contract and already does not run descriptor `__set_name__`.

Preserve the current base-first MRO scan and duck-typed `coordinates`/`coordinate` probe for a cache miss. Do not optimize by narrowing accepted declaration types. The cache is populated only after that full scan succeeds, preventing partial results from an exception.

Use a targeted test that counts traversal work, plus inheritance, specialization, returned-map isolation and weak-reference collection checks. Compare a bounded Curta selector and crank tick before and after on the same machine with no mesh build; assert numerical bank and key stop/carry/source-timing framework tests.

## Risks / Trade-offs

- A post-definition class mutation could leave a cached result stale. Such mutation does not invoke descriptor naming or relation validation; the documented declaration boundary is class completion. Tests cover class-body `Bound` checks, completed and specialized classes.
- Cache contents may reference the owning class through port metadata. A class-local cycle is collectable; a weak-reference test proves generated classes are not pinned by a global cache.
- Profiling under concurrent Curta tests changes wall time. Compare CPU process time for the same bounded operation and report both timing and numerical results.
