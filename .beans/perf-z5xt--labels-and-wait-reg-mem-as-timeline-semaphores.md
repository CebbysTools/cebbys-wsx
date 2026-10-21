---
# perf-z5xt
title: Labels and WAIT_REG_MEM as timeline semaphores
status: todo
type: task
priority: normal
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:40Z
updated_at: 2026-10-21T07:55:40Z
parent: perf-umd0
blocked_by:
    - perf-ywx1
---

Map RELEASE_MEM/WRITE_DATA labels to GPU writes plus semaphore signals and cross-queue waits to semaphore waits; CPU waits only when the title waits from the CPU.

Acceptance: no CPU wait for GPU-to-GPU label dependencies.
