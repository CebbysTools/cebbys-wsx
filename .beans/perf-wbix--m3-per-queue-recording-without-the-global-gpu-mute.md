---
# perf-wbix
title: M3 Per-queue recording without the global GPU mutex
status: todo
type: epic
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:38Z
updated_at: 2026-10-21T07:55:38Z
parent: perf-jvvo
blocked_by:
    - perf-5v4y
---

Section 4.2: one recorder per guest queue/host thread, preparation outside locks, short submit lock. Exit: lock wait < 20 us/draw, device call < 50 us/dispatch.

## Findings 2026-10-21 (menu, 180 s, nhl27)
- 72,000 resource builds; stage A 2.5 s, stage B 45.5 s (0.63 ms per build), inside it guest memory upload 31.7 s and images 14.2 s; all under `GpuMutex` in the dispatch device call.
- Staging: ~1.1 GB per 10 s of buffer regions staged device-local and copied back (GPU copies, not CPU).
- Target: move stage B preparation (upload planning, image lookups) before the lock; the lock should cover only command recording. Needs a reviewable design for recorder hazards first.

## Findings 2026-10-21 evening (soak log, match)
- GPU mutex held ~9.5-13 s per 10 s: saturated. Holders: queue 0 dispatches ~3.7 s (7000 x 0.53 ms), indirect dispatches ~2.3 s (204 x 11 ms device call), draw thread ~3 s (6500 x 0.45 ms).
- Resource builds over 2 h: images phase 2390 s, guest memory upload 1779 s, stage B 4030 s (all under the lock).
- Storage images: 1.17 M created (2113 s create time, 29% of the run). Per 10 s: 805 cache-eviction write-backs (4.7 GB) and 1760 first uploads (8.2 GB). Device heap ~10/11.2 GB used, storage cache budget squeezed to 512 MiB: thrash.
- `APS5_TEXTURE_CACHE_MIB=4096`: eviction write-backs 0, first uploads 90/10 s, but vkAllocateMemory OOM (heap 0 11526/11242 MiB) at match load; NVIDIA GPU lost afterwards (reboot needed).
- Partial `APS5_TRACE_DEVICE_MEMORY` (branch diag/device-memory-by-site): createHostPointerImport 2.3 GB and BufferPool::AllocateMemory 1.5 GB live at boot; memory type split added, not yet run.
- Next: full-match device memory trace after reboot; cap the largest device-local consumer; reserve storage cache budget; measure.

## Findings 2026-10-22 (menu, 120 s runs)
- `perf/agc-host-import-window` (256 MiB windows): menu 2.0 -> 4.0 FPS; render targets read as buffers no longer CPU-copied.
- Remaining hook syncs were `storeBackClearedHtile` CPU-reading 640 KiB HTILE over pending GPU writes (DepthSurface.cpp): skipping it (`APS5_EXPERIMENT_SKIP_PENDING_HTILE_READ`, diag) cuts syncs 4.5 s -> 0.5 s per 10 s, FPS ~4.2 (frames now GPU-bound).
- GPU time per menu frame ~180 ms; 5 compute programs ~95 ms. `0x1152fa6000` 240x135 groups (4K, 16x16), 0x16e0 bytes RDNA, 244k SPIR-V words, ~23 ms per dispatch, not address-based.
- Ruled out for that program: buffer placement (written regions staged to VRAM: no change; read-only regions staged: no change), SPIR-V optimisation (SPIRV-Tools ON: optimiser far too slow for 26k shaders and the run hung; not measured), `APS5_FAST_FLOAT` (27 ms both, no-cache runs), loop guard 4096 (inconclusive).
- Frostbite DRS strings exist (`DynamicResolutionScale*`) but command-line `-Render.ResolutionScale`/`-WorldRender.ResolutionScale` had no effect; passes stay 4K (PS5_4K preset forced by `ANYPS5_OUTPUT_RESOLUTION=2160p`).
- Next: shader-level profile of 0x1152fa6000 (Nsight real-time shader profiler on the menu frame), and a way to render below 4K.
