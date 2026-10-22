# 8 MiB import window

Status: `rejected`

## Improvement summary

| Metric | Start | Now | Change |
|---|---|---|---|
| Menu FPS (win8) | 2.02 | 2.02 | baseline |

## Cause

The upstream default window is 8 MiB.

## Options

Keep the default. No code change.

## Result

Menu at about 2.0 FPS (bench `win8`).

## Why

Render targets cross many 8 MiB allocations, so the driver copies them with the CPU.

## Evidence

### Original

`SetHostImportWindow(8 MiB)` in the AGC driver (upstream default).

### Change

None. This is the baseline.

### Reason

Baseline for the other window sizes.

### Improvement

None. Baseline.

### Timings

| Bench | Window | Menu FPS | GPU busy ms/frame |
|---|---|---|---|
| win8 | 8 MiB | 2.02 | 242.48 |

### Reports

- [report-win8.txt](report-win8.txt)
