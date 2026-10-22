# Keep FP64

Status: `rejected`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| 0x115258a000 GPU ms per run | 339.48 (stage1g) | 338.52 (f16fma-5) | 0 | baseline |

## Cause

FP64 has enough precision to compute `a * b + c` exactly before one f16 rounding.

## Options

| Option | Pros | Cons |
|---|---|---|
| No change | Exact. Simple. | About 816 FP64 operations per inner step in the AO shader. |

## Result

About 340 ms per AO run today.

## Why

Consumer GPUs run FP64 slowly. This cost blocks the single queue for a large part of each frame.

## Evidence

### Original

`v_fma_mix*` and f16 interpolation use the f64 helper `interpolate_f16_mode_0`.

### Change

None. This is the current state.

### Reason

Baseline for the FP32 options.

### Improvement

None.

### Timings

| Bench | 0x115258a000 dispatches | ms per run |
|---|---|---|
| stage1g | 54 | 339.48 |
| f16fma-5 | 195 | 338.52 |
| guard64b (loop guard 64) | 4 | 257.75 |

### Reports

- [report-f64.txt](report-f64.txt)
