---
# perf-f8vp
title: Indirect arguments, GDS and fast-clear metadata on the GPU
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

Indirect dispatch/draw arguments read by the GPU; GDS copies as GPU copies (dev-next GDS_GPU_COPY); CMASK/DCC/HTILE expansion as GPU work.

Acceptance: zero Recorder::Sync per frame in menus.
