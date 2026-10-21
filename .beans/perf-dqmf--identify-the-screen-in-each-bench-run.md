---
# perf-dqmf
title: Identify the screen in each bench run
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T10:48:48Z
updated_at: 2026-10-21T10:48:48Z
parent: perf-xpmq
---

Bench runs land on different screens (licence, VS team select, SIGN IN REQUIRED dialog) with the same timed presses. Dump a few late frames per run, compute a small image signature, and label the run with the matching reference screen; compare FPS only between runs on the same screen.

Acceptance: results.csv has a scene column; two runs on the same scene agree within 5%.
