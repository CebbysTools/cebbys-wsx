# Fast float

Status: `no-gain`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| 0x1152fa6000 GPU ms per dispatch | 20.91 (htileskip) | 27.33 (fastfloat) | -23 | run without shader cache |

## Cause

Software denormal flush and NaN fix-ups add code to each float operation.

## Options

| Option | Pros | Cons |
|---|---|---|
| `APS5_FAST_FLOAT` (branch `feat/shader-fast-float`) | Less code. | Differs from the console for denormal and NaN values. |

## Result

Shader 0x115258a000: 3,711 ms vs 3,737 ms per 10 s. No FPS change.

## Why

The slow shader is limited by texture latency, not by float checks.

## Evidence

### Original

Software f32 denormal flush, NaN-aware `v_min_f32`/`v_max_f32`, packed f16 NaN fix-ups.

### Change

`APS5_FAST_FLOAT=1` (branch `feat/shader-fast-float`).

### Reason

Less emulation code per float operation.

### Improvement

No gain on the slow program. 0x1152fa6000 was slower in the fast-float run (27.3 vs 20.9 ms), but that run had no shader cache, so the scenes differ.

### Timings

| Bench | Setting | 0x115258a000 ms/run | 0x1152fa6000 ms/run | 0x1150e42000 ms/run |
|---|---|---|---|---|
| htileskip | default | 338.84 | 20.91 | 17.14 |
| fastfloat | fast float, no cache | not in log | 27.33 | 15.09 |
| (earlier run) | fast float | 3,711 vs 3,737 ms per 10 s: report not kept | | |

### Reports

- [report-fastfloat.txt](report-fastfloat.txt)
- Earlier 0x115258a000 measurement: report not kept.
