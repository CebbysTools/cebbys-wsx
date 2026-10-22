# 64 MiB import window

Status: `rejected`

## Improvement summary

| Metric | Start | Now | Change |
|---|---|---|---|
| Menu FPS (win8 → win64) | 2.02 | 3.48 | +72% |

## Cause

A larger window lets more allocations import in place.

## Options

`APS5_HOST_IMPORT_WINDOW_MIB=64`.

## Result

Better than 8 MiB, worse than 256 MiB (bench `win64`).

## Why

Some render targets are still larger than the window.

## Evidence

### Original

8 MiB import window.

### Change

`APS5_HOST_IMPORT_WINDOW_MIB=64` (branch `perf/agc-host-import-window`, `Execution/src/VulkanDevice.cpp`).

### Reason

Large render targets did not fit in 8 MiB and were copied by the CPU.

### Improvement

Menu FPS +72% against 8 MiB.

### Timings

| Bench | Window | Menu FPS | GPU busy ms/frame |
|---|---|---|---|
| win8 | 8 MiB | 2.02 | 242.48 |
| win64 | 64 MiB | 3.48 | 183.80 |

### Reports

- [report-win64.txt](report-win64.txt)
