---
# perf-wbix
title: M3 Per-queue recording without the global GPU mutex
status: todo
type: epic
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:38Z
updated_at: 2026-10-21T07:55:38Z
parent: perf-jvvo
blocked_by:
    - perf-5v4y
---

Section 4.2: one recorder per guest queue/host thread, preparation outside locks, short submit lock. Exit: lock wait < 20 us/draw, device call < 50 us/dispatch.

## Findings 2026-10-21 (menu, 180 s, nhl27)
- 72,000 resource builds; stage A 2.5 s, stage B 45.5 s (0.63 ms per build), inside it guest memory upload 31.7 s and images 14.2 s; all under `GpuMutex` in the dispatch device call.
- Staging: ~1.1 GB per 10 s of buffer regions staged device-local and copied back (GPU copies, not CPU).
- Target: move stage B preparation (upload planning, image lookups) before the lock; the lock should cover only command recording. Needs a reviewable design for recorder hazards first.
