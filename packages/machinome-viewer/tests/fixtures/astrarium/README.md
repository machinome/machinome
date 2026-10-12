# Astrarium running-time acceptance fixture

Copied from the actual `projects/astrarium` finite build at project commit
`d736826`, framework content `0ce71cd`, on 2026-09-20. The document and both
binary STL assets are unmodified producer artifacts, not authored by this test.
The viewer suite imports no framework or project Python code.

This is the deliberately nonhistorical two-cube capability fixture, **not a
reconstruction of Dondi's clock**. It has an explicit retained time drive,
enable and wind inputs, a 10 mm weight range, and a self-read exhaustion gate.
At its diagnostic rate, two seconds yield shaft 2 and drop 2; disabling and
winding by 2 hold shaft 2 and restore drop 0. Resuming adds only new travel.

The browser test checks autonomous stepping, pause, stop/wind/resume, exhaustion,
rewind/restart, snapshot/restore and reset, with worker and in-thread execution.
Screenshots prove the rendered diagnostic placement follows its bank; they make
no claim about historical geometry, supports, tooth contact or force dynamics.
