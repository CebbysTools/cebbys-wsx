---
# perf-plco
title: TDR-safe submissions
status: in-progress
type: task
priority: critical
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:43Z
updated_at: 2026-10-21T10:06:46Z
parent: perf-ipy1
---

Split long compute submissions so none exceeds ~1 s; label device-loss reports.

Acceptance: no VK_ERROR_DEVICE_LOST in a 2 h session.



Moved ahead of M1: GPU resets end benchmark runs after 1-3 minutes, so M0 cannot be repeatable until this is fixed. Evidence: NVIDIA event 153 at each crash second; APS5_BATCH_CAP=8 does not help; checkpoint report 'no checkpoint reached' with device fault IP 0x20c980e60 (a shader). Draw checkpoints added on feat/agc-draw-checkpoints.



## Result so far
Default loop guard (fix/shader-default-loop-guard, limit 2^24): warm-up 7 min + two 15 min runs + two 7 min fixed-scene runs without a GPU reset (previously every 1-5 min). Stays in progress until the 2 h soak (perf-8637).
