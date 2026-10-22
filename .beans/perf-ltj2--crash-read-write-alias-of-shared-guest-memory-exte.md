---
# perf-ltj2
title: 'Crash: read-write alias of shared guest memory extends outside the range'
status: completed
type: bug
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T10:48:48Z
updated_at: 2026-10-21T10:48:48Z
parent: perf-ipy1
---

Seen in NHL 27 menus on nhl27 (2026-10-21): 'read-write alias of shared guest memory 0x11b0ba0000+0x100000: a resident run of direct memory extends outside the range' (and once at 0x11af7c0000). Same aliasing area as the M2 write-back loop.

Acceptance: understood and fixed; no occurrence in a 2 h soak.

## Fix 2026-10-21
Branch `fix/agc-import-alias-resident-run-outside`: the import checks `GuestArenaResidentSpan` and returns a failed import (CPU copy path) when a resident run crosses the window. Reproduced at ~30 s in menu once GDS copies ran on the GPU; 180 s run after the fix had no crash. Closes when: 2 h soak (perf-8637) without it.

No alias crash in the 2 h soak.
