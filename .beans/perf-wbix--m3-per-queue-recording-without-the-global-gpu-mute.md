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
