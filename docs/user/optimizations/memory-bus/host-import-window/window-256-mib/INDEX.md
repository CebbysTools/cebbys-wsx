# 256 MiB import window

Status: `applied`

## Improvement summary

| Metric | Start | Now | Change |
|---|---|---|---|
| Menu FPS (win8 → win256) | 2.02 | 4.04 | +100% |

## Cause

All measured render targets fit in a 256 MiB window.

## Options

`APS5_HOST_IMPORT_WINDOW_MIB=256`, now the default in the fork. It needs `fix/agc-import-alias-resident-run-outside`, because a wide window can cut a resident direct-memory run.

## Result

Menu went from 2.0 to 4.04 FPS (bench `win256`).

## Why

The CPU copies of large render targets stopped.

## Evidence

### Original

8 MiB import window.

### Change

Default window 256 MiB (branch `perf/agc-host-import-window`, `Execution/src/VulkanDevice.cpp`, `docs/dev/ENVIRONMENT.md`). Needs `fix/agc-import-alias-resident-run-outside`.

### Reason

All measured render targets fit in 256 MiB. The CPU copies stop.

### Improvement

Menu FPS doubled (2.02 to 4.04). GPU busy time per frame fell by 22%.

### Timings

| Bench | Window | Menu FPS | GPU busy ms/frame |
|---|---|---|---|
| win8 | 8 MiB | 2.02 | 242.48 |
| win256 | 256 MiB | 4.04 | 189.24 |

### Reports

- [report-win256.txt](report-win256.txt)
