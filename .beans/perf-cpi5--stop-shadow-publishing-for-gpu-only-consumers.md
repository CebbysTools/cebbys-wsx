---
# perf-cpi5
title: Stop shadow publishing for GPU-only consumers
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:38Z
updated_at: 2026-10-21T07:55:38Z
parent: perf-5v4y
blocked_by:
    - perf-odi7
---

Shadow publish only when the consumer reads guest memory on the CPU or through an address-based shader that cannot bind the resident resource.

Acceptance: shadow-publish MiB/frame drops > 90%; no stalls like APS5_NO_UNIT_SHADOW showed.
