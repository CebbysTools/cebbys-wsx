# Storage cache priority

Status: `applied`

## Cause

Storage images and sampled textures share one cache budget. Storage images pushed sampled textures out, then came back. This caused evict, write-back and re-upload cycles.

## Options

| Option | Pros | Cons |
|---|---|---|
| Reserve 1 GiB for sampled textures (applied) | Stops the thrash. Simple. | Fixed floor. |
| 4 GiB texture cache | More space for all. | Caused a GPU device loss (out of VRAM). Rejected. |

## Result

Branch `perf/agc-storage-cache-priority`. Unit tests pass. No separate FPS measurement; it is part of the step from 4.0 to about 5 FPS.

## Why

The thrash cost re-uploads. A floor for sampled textures stopped most of them. The FPS effect is small because other limits are larger.
