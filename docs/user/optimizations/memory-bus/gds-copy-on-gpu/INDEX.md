# GDS copy on GPU

Status: `no-gain`

## Cause

A `DMA_DATA` copy from memory to GDS drained the whole device. The menu had 1052 drains per 120 s, all for 4-byte copies.

## Options

| Option | Pros | Cons |
|---|---|---|
| Record the copy as a GPU buffer copy (applied) | No device drain. Keeps queue order. | None found. |
| Keep the drain | Simple. | Stalls the CPU. |

## Result

Branch `perf/agc-gds-copy-on-gpu`. Drains went from 1052 to 0 per 120 s. FPS did not change (0.78 vs 0.82 over 180 s).

## Why

The drains were real, but they were not the frame limit. The change stays because it is correct and removes stalls.
