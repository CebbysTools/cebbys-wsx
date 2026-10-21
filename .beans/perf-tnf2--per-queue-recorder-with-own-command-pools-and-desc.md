---
# perf-tnf2
title: Per-queue recorder with own command pools and descriptor caches
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:39Z
updated_at: 2026-10-21T07:55:39Z
parent: perf-wbix
blocked_by:
    - perf-32ss
---

Split Recorder per guest queue; per-thread command pools reset per frame (Khronos pattern); cross-queue ordering through the memory-order table.

Acceptance: draws and dispatches of different queues record concurrently.
