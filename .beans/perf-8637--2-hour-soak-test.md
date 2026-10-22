---
# perf-8637
title: 2-hour soak test
status: completed
type: task
priority: normal
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:44Z
updated_at: 2026-10-21T07:55:44Z
parent: perf-ipy1
blocked_by:
    - perf-plco
    - perf-uq20
---

Menus, matches, replays; record crashes, memory growth, cache growth.

Acceptance: no crash, memory stable.

## Result 2026-10-21 (nhl27 2791b15cc, RTX 4070 610.88)
7203 s CPU vs CPU: no crash, no GPU reset, no device lost. A full match finished (EDM 1-0) and a rematch started. Zero-frame stretches (windows 56-58, 82-111, 137-477) were screens waiting for input; the longest was the first intermission until X was pressed. Mean 0.31 FPS overall.
