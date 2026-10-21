---
# perf-wnx1
title: Shrink the shader cache
status: todo
type: task
priority: normal
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:41Z
updated_at: 2026-10-21T07:55:41Z
parent: perf-zurs
blocked_by:
    - perf-njf5
---

Find the largest cache records; compress with zstd; drop duplicate IR plans; garbage-collect entries unused for N sessions; make diagnostic switches not invalidate keys where they do not change code.

Acceptance: cache < 10 GB for NHL 27 after a full session.
