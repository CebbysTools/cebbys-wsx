---
# perf-8v84
title: Benchmark script with fixed scenes and metrics
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:35Z
updated_at: 2026-10-21T07:55:35Z
parent: perf-xpmq
---

Script (WSL side, extends run_game.sh) that launches the converted title with a warm cache, drives scripted input to fixed scenes (boot, menu idle 60 s, menu navigation, match load), and extracts: presents per 10 s and 1% low, GPU busy/idle per frame, [gputime] by class (PCIe MiB/frame), [draw]/[dispatch] lock wait and device call, time to first frame and to first menu.

Acceptance: one command produces a CSV/markdown table per run; two runs on the same build agree within 5%.
