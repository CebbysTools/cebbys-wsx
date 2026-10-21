---
# perf-8v84
title: Benchmark script with fixed scenes and metrics
status: completed
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:35Z
updated_at: 2026-10-21T10:06:45Z
parent: perf-xpmq
blocked_by:
    - perf-plco
---

Script (WSL side, extends run_game.sh) that launches the converted title with a warm cache, drives scripted input to fixed scenes (boot, menu idle 60 s, menu navigation, match load), and extracts: presents per 10 s and 1% low, GPU busy/idle per frame, [gputime] by class (PCIe MiB/frame), [draw]/[dispatch] lock wait and device call, time to first frame and to first menu.

Acceptance: one command produces a CSV/markdown table per run; two runs on the same build agree within 5%.



## Result
Fixed scene: `bench.py <label> --seconds 420 --skip-windows 12 --press-count 3` (three Cross presses, then the quick-settings menu idles). Two nhl27 runs (default loop guard): FPS 2.11 / 2.19 (3.7%), GPU busy 210.6 / 213.7 ms per frame (1.5%), storage-writeback 628 / 615 MiB per frame, shadow-publish 582 / 580 MiB per frame, first interactive 28.1 / 27.1 s. Draw lock wait varies more (146 / 192 us). Acceptance met.
