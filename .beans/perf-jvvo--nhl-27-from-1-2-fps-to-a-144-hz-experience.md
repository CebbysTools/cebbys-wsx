---
# perf-jvvo
title: 'NHL 27: from 1-2 FPS to a 144 Hz experience'
status: todo
type: milestone
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:35Z
updated_at: 2026-10-21T07:55:35Z
---

Refactor the AGC driver and its surroundings so NHL 27 starts quickly, renders a stable 60 FPS natively and presents 120-144 FPS, works on 1080p displays, and can be set up from a game-free kit.

Research and architecture: `fork-notes/MILESTONE_144FPS_RESEARCH.md`. Measurements: `fork-notes/AGC_DRIVER_PERFORMANCE.md`.

Requirements: R1 warm first frame < 15 s, cold < 90 s; R2 stable 60 native, 120-144 presented; R3 1080p/1440p displays, internal resolution setting; R4 game-free kit < 500 MB (no game files shared); R5 local 4-controller play, no TDR in 2 h, cache < 10 GB, play a match.
