# GDS copy on GPU

Status: `no-gain`

## Improvement summary

| Metric | Start | Now | Change |
|---|---|---|---|
| Device drains per 10 s | 1050 | 0 | -100%; FPS unchanged |

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

## Evidence

### Original

A memory-to-GDS `DMA_DATA` drained the device (`Execution/src/Driver/Packets/PacketMemory.cpp`).

### Change

Branch `perf/agc-gds-copy-on-gpu`: record the copy as a GPU buffer copy in queue order.

### Reason

1050 device drains in one 10 s window, all `DMA_DATA`.

### Improvement

Drains removed. FPS did not change. The first test run (`gds-gpu`) hit the resident-run alias error, fixed later by `fix/agc-import-alias-resident-run-outside`.

### Timings

| Bench | Build | Menu FPS | GPU busy ms/frame | Device drains (10 s) |
|---|---|---|---|---|
| base-180 | before | 0.82 | 452.38 | not traced |
| dma-drain | before, drain trace | 0.77 | 409.97 | 1050 |
| gds-gpu | after | crash (alias error) | | 0 |

### Reports

- [report-gds-gpu.txt](report-gds-gpu.txt)
