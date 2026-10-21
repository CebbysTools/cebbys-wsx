---
# perf-4re2
title: Map every write-back and shadow publish to its consumer
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:37Z
updated_at: 2026-10-21T09:10:21Z
parent: perf-5v4y
---

Instrument storage-writeback and shadow-publish with the reason and the next reader (CPU read, GPU read in guest layout, nothing). Use APS5_DEBUG_LABELS plus counters.

Acceptance: table of bytes per frame by reason in the menu scene; identifies the GPU-only traffic.



## Findings so far (2026-10-21)
- Copy GPU time is recorded at `Texture.cpp` write-back sites (~3342 `StorageWriteBack` for storage images, ~5200 second path) and `UnitShadow.cpp:237` (`ShadowPublish`).
- Baseline menu: ~180 storage write-backs per frame (~3.4 MiB each, ~585 MiB/frame) and shadow publishing ~512 MiB/frame, but the `[storage]` reason line accounts only a few hundred MiB per 10 s: the gputime byte counts and the reason accounting disagree -> first step: tag BeginGpuTiming bytes with the write-back reason.
- Mechanism behind `store`-reason re-uploads (dev-next SKIP_STORE_UPLOADS): images aliasing the same pooled render-target memory write back into it and the other image sees the stamped blocks as changed and re-uploads (Texture.cpp `StorageTexture::Refresh`, uploadReason 'store'). On the console the memory is shared and this costs nothing. M2.2 must handle aliases GPU-to-GPU.

## Findings 2026-10-21 (menu, nhl27 build, same machine)

Copy-off experiments (menu, presents per 10 s; baseline 17-20):
- `APS5_GPU_NO_WRITEBACK=1`: 14-15. `APS5_NO_UNIT_SHADOW=1`: 5-14. Neither helps; copies are not the limiter by themselves.

Where frame time goes (baseline `bench-scenes-a`, 10 s window, 17 presents):
- GPU busy 1.9 s of 10 s (GPU idle ~80%). Largest classes: draw 25 ms/frame, shadow-publish 51 ms/frame; top program 0x1152fa6000 ~44 ms/frame.
- Dispatch CPU path ~1050 us per dispatch: GPU mutex lock wait 499 us + `VulkanDevice::Dispatch` device call 444 us. Lock holder is mostly `dispatch` (max hold 30.6 ms).
- Recorder: ~250 CPU-GPU syncs per 10 s, mostly `recorded store` and `pending write` (CPU reads GPU-written guest memory), each draining the GPU. vkQueueSubmit itself is cheap (43 us mean).
- Thread samples: 9 driver worker threads blocked on the pipeline/GPU mutex ~95% of the time; the active thread spends ~25% in the NVIDIA driver under `Recorder::finish` and waits in `CommandBatch::Wait`.
- `ShaderRecompiler::HashBytes` hot spot is the startup `RegistrationPreparePool` hashing the cache file, not per-frame.

Conclusion: the limiter is serialized CPU work plus CPU-GPU round trips, not PCIe bytes. Order: M4 (remove `recorded store` / `pending write` syncs on the frame path) and M3 (shorter GPU mutex holds in dispatch) before the M2 memory redesign.

- `APS5_STORE_AT_FLIP=1` (menu): 1.11 FPS mean vs ~2.1 baseline, GPU busy 427 ms/frame; syncs not reduced. Rejected.

- GDS drains: 1052 device drains per 120 s were all 4-byte memory->GDS `DMA_DATA`; `perf/agc-gds-copy-on-gpu` removes them, FPS unchanged (menu 0.78 vs 0.82 over 180 s). Patched run reached the pre-game tunnel within 180 s; baseline was still at the versus screen (single run).
