# Storage cache priority

Status: `applied`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| Menu FPS | not measured | not measured | not measured | report not kept |

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

## Evidence

### Original

One cache budget for storage images and sampled textures. Storage images pushed sampled textures out.

### Change

Branch `perf/agc-storage-cache-priority`: `Graphics/src/ShaderResources.cpp` reserves `min(sampledBytes, 1 GiB)` for sampled textures. `tests/Graphics.cpp` updated.

### Reason

Evict, write-back and re-upload cycles of the same textures.

### Improvement

No separate FPS measurement. The 4 GiB cache option (bench `cache4g`) lost the GPU and was rejected.

### Timings

| Bench | Setting | Menu FPS | Note |
|---|---|---|---|
| cache2g | 2 GiB texture cache | no FPS (warm-up run) | |
| cache4g | 4 GiB texture cache | no FPS | GPU device lost |
| prio | 1 GiB sampled floor | report not kept | |

### Reports

- [report-cache4g.txt](report-cache4g.txt)
- Bench `prio`: report not kept.
