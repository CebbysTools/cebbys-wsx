---
# perf-ndeq
title: Nsight trace recipe in the harness
status: todo
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
