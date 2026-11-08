# Authorized baseline comparison

Root authorized one sequential baseline/candidate comparison, raising the
test allocation from 4 GiB to 8 GiB aggregate RSS. The earlier 4 GiB guard
was a test budget, not a user hardware requirement. This baseline used the
unchanged main version-4 document and the same frozen official API-30 bundle
as the candidate; it made no product, model or geometry changes.

Allocation: `root-declared-lamp-browser-memory-20261108-01-baseline`.
Host MemAvailable was **13,322,883,072 bytes**, above the required 10 GiB.
The supervisor recorded per-process RSS at approximately 0.2-second intervals
and PSS approximately once per second, with PID/birth ownership, an 8 GiB
RSS ceiling, a host-pressure guard and a 180-second inclusive wall budget.

The ordinary official Inspector **mounted successfully in 8.0164 seconds**;
its next two-frame observation took **1.7588 seconds**. All **572/572 STL
requests completed**, with no recorded request or HTTP errors. Its full-root
`Page.screenshot` then timed out after 30 seconds, after fonts loaded. No PNG
or successful visual acceptance is claimed.

The probe returned 1. Total wall time including browser shutdown and owned
cleanup was **71.865989 seconds**. Peak aggregate RSS was **4,629,803,008
bytes**; peak sampled aggregate PSS was **4,343,998,464 bytes**. Neither the
expanded memory guard nor host-pressure guard stopped it. **Zero owned
processes remained.**

Root's instruction required reporting a baseline failure before proceeding.
The candidate allocation was therefore **not launched**, and there was no
automatic retry. These results do not establish a color-change regression
or prescribe a product fix.
