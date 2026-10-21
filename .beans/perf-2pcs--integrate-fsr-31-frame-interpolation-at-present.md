---
# perf-2pcs
title: Integrate FSR 3.1 frame interpolation at present
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:42Z
updated_at: 2026-10-21T07:55:42Z
parent: perf-lrur
---

FidelityFX SDK (MIT) as a submodule; interpolate the presented image with optical flow (no title motion vectors); swapchain proxy pacing.

Acceptance: 60 rendered -> 120 presented with acceptable artefacts on menus and gameplay.
