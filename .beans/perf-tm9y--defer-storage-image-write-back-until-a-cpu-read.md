---
# perf-tm9y
title: Defer storage-image write-back until a CPU read
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:37Z
updated_at: 2026-10-21T07:55:37Z
parent: perf-5v4y
blocked_by:
    - perf-odi7
---

Implement GPU-owned storage images: no write-back after the dispatch; download on CPU read or guest-layout consumer; async batched downloads (shadPS4).

Acceptance: storage-writeback MiB/frame drops > 90% in menus with no rendering change (frame dumps compared).
