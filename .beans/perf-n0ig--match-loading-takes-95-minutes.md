---
# perf-n0ig
title: Match loading takes ~9.5 minutes
status: in-progress
type: task
priority: critical
tags:
    - nhl27-perf
created_at: 2026-10-21T11:42:57Z
updated_at: 2026-10-21T15:10:00Z
parent: perf-zurs
---

CPU vs CPU match (press sequence 50:cross,65:cross,80:cross,110:triangle,125:cross,140:cross,155:cross): start pressed ~160 s, VS loading screen at ~1.5 FPS (320 ms GPU per frame) until ~730 s, then the tunnel cutscene. On a PS5 this takes seconds. Find what the load waits on (file reads, decompression, uploads, or rendering of the loading screen starving the loader) with APS5_TRACE_APR and APS5_SAMPLE_THREADS, then fix.

Acceptance: match load < 60 s (R1).

## Findings 2026-10-21 (load-diag, 603 s, APR trace + thread samples)

- 14,625 APR reads spread evenly over the run; no long read stall. Not I/O bound.
- Busiest guest thread is busy in 6% of 41,729 sample rounds; the rest wait in `TimedWait::AlertableWait` / `SleepUntil`. Not CPU bound.
- FPS during the load: 0.39. The load advances per presented frame / GPU completion, so load time scales with frame time.
- User run: the ice loaded and the match nearly started with no freeze.

Conclusion: blocked on M2 (per-frame copy traffic, ~1.2 GB/frame). No separate load fix.
