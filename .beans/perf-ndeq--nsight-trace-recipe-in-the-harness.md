---
# perf-ndeq
title: Nsight trace recipe in the harness
status: completed
type: task
priority: normal
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:36Z
updated_at: 2026-10-21T07:55:36Z
parent: perf-xpmq
blocked_by:
    - perf-8v84
---

Optional harness step that runs `trace.cmd` (GPU Trace, debug labels) on a chosen scene and extracts per-label times, SM throughput, gr active, PCIe bytes.

Acceptance: one command, exported tables summarised.

## Result 2026-10-21
`trace.py menu-validate`: elevated GPU Trace ran, export summarised. Frame 2: GPU frame 120.6 ms, graphics engine active 4.4%, SM throughput 3.5%; labelled dispatches listed (top 0x11523e7000 60x2160x1 1.3 ms).
