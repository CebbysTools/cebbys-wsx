---
# perf-tl9i
title: Baseline numbers for nhl27 and exp/dev-next-on-nhl27
status: in-progress
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:35Z
updated_at: 2026-10-21T10:06:45Z
parent: perf-xpmq
blocked_by:
    - perf-8v84
---

Run M0.1 on `nhl27` and on `exp/dev-next-on-nhl27` (default switches). Record in the research doc.

Acceptance: baseline table committed.



## nhl27 baseline (fixed scene, 2026-10-21, loop guard default)
| Metric | Value |
|---|---|
| First present / first interactive | ~19 s / 27-28 s |
| FPS (menu idle) | 2.1-2.2 |
| GPU busy / idle per frame | 211-214 ms / 260-267 ms |
| Draw lock wait | 146-192 us per draw |
| storage-writeback | 615-628 MiB per frame |
| shadow-publish | 580-582 MiB per frame |
