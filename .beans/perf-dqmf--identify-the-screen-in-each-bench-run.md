---
# perf-dqmf
title: Identify the screen in each bench run
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T10:48:48Z
updated_at: 2026-10-21T11:42:58Z
parent: perf-xpmq
---

Bench runs land on different screens (licence, VS team select, SIGN IN REQUIRED dialog) with the same timed presses. Dump a few late frames per run, compute a small image signature, and label the run with the matching reference screen; compare FPS only between runs on the same screen.

Acceptance: results.csv has a scene column; two runs on the same scene agree within 5%.



## Result
bench.py saves a preview of the last frame per run (C:\\Games\\NHL 27\\traces\\scenes\\<run>.png) and a 16x9 signature; automatic matching works for static screens only (two frames of the moving tunnel cutscene differ by 33.6 against a threshold of 12). Runs are compared when they use the same --sequence and their previews show the same phase. New benchmark scene: CPU vs CPU match via --sequence (reaches the pre-game tunnel cutscene).
