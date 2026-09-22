# Completion evidence

Base: framework `main` `c81a585f58ca688fb5b4b3a7a05d87b8c601f050`. The pilot explicitly authorized an isolated manual worktree despite primary's pre-existing untracked `docs/examples/v8-engine/`; that path remained untouched.

Red first: `python -m unittest tests.test_port_enumeration_cache -v` failed because the second `declared_ports` call probed the same completed class again (4 reads vs 2). The initial cache then exposed a second red case: `RetainedCarriage.lift` was cached with a temporary `None` key during `Joint.__set_name__`, making real Curta import fail. A focused Bound naming regression reproduced that partial map. The plan was revised and its planning-only commit amended before completion.

Green: focused cache tests pass, including repeated traversal, independent mappings, inherited and site joint ports, generated class collection, and Bound naming. The affected framework suite (`test_port_enumeration_cache`, `test_ports`, `test_joints`, `test_declarative_nodes`, `test_ancestor_constraints`, `test_running_carry_timing`, `test_running_time_drive`, `test_running_stops`) reports 430 passed and 363 subtests passed.

The same mesh-free source-backed OperatingCurta operation (construct `Sim(dt=.1)`, set `digit_1=3`, move crank 18° in 0.1 seconds) was timed with process CPU under `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1` and the project worktree read-only. Baseline → cache: construction 9.542 → 2.290 seconds; selector 3.083 → 2.367 seconds; crank tick 6.983 → 6.874 seconds. The final bank has exactly 213 entries and identical SHA-256 digest `ee8d6f04adcab85a32bf0920951aa375412860c8bd259e52079a06c7540105e2` before and after; result and counter both remain zero at this partial stroke. Concurrent CPU work makes wall times less comparable; process CPU is reported. The unchanged crank cost remains a separate performance finding, not a claim of resolved ordinary operation speed.

No event-search subdivisions, tolerances, source-timing, carry or stop laws changed. The change requires no ADR: the class-local cache preserves existing declarative architecture and adds no public interface or cross-package decision.
