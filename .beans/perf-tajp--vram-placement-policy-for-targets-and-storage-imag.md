---
# perf-tajp
title: VRAM placement policy for targets and storage images
status: todo
type: task
priority: normal
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:38Z
updated_at: 2026-10-21T07:55:38Z
parent: perf-5v4y
blocked_by:
    - perf-tm9y
    - perf-cpi5
---

Render targets and storage images allocated device-local; imported host memory only for CPU-shared buffers.

Acceptance: PCIe < 50 MiB/frame; VRAM budget respected on 12 GB GPUs.
