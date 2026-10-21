---
# perf-4re2
title: Map every write-back and shadow publish to its consumer
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:37Z
updated_at: 2026-10-21T07:55:37Z
parent: perf-5v4y
---

Instrument storage-writeback and shadow-publish with the reason and the next reader (CPU read, GPU read in guest layout, nothing). Use APS5_DEBUG_LABELS plus counters.

Acceptance: table of bytes per frame by reason in the menu scene; identifies the GPU-only traffic.
