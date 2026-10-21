---
# perf-odi7
title: 'Design: resource ownership states and CPU-read detection'
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:37Z
updated_at: 2026-10-21T07:55:37Z
parent: perf-5v4y
blocked_by:
    - perf-4re2
---

Write the design: per-unit states (CPU-owned, GPU-owned, both clean), transitions on GPU write, CPU access (guard page or write-watch at sync points: label waits, flips, DMA to CPU memory), eviction. Reuse unit shadow units as granule. Review against Ryujinx TextureGroup and yuzu buffer cache.

Acceptance: design section added to the research doc and reviewed.
