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
