# Baseline actual-canvas readback

Allocation `root-declared-lamp-browser-memory-20261108-01-baseline-readback`
completed successfully: code 0, **97.341 seconds including cleanup**, and
zero remaining owned processes. The ordinary Inspector mounted the unchanged
version-4 document in **7.7892 seconds**, with a **1.7263-second** next-frame
observation. All **572/572** model requests completed without fetch/HTTP errors.

The authorized observer called public `viewer.setView(viewer.view())`, then
the actual canvas's `toDataURL('image/png')` in that same page task. There
were no compositor screenshot calls. Redraw took 16.6 ms; PNG readback took
55.3144 seconds. The exact nonblank 1367×1000 PNG is retained, SHA-256
`df6e96eaf71620f8a50e90137eb4db060da961667f0574b0f94103721f4b3265`.

Peak aggregate RSS was **4,626,784,256 bytes** and peak sampled PSS
**4,330,867,712 bytes**, below the expanded 8 GiB test ceiling. Fresh host
MemAvailable exceeded 10 GiB. Normal DOM, control fields and URL are recorded
separately. The earlier screenshot timeout remains in its original directory.
