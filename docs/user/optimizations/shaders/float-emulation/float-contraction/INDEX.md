# Float contraction

Status: `no-gain`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| Menu FPS | 4.94 (skipall) | 5.15 (contract2) | 4 | inside run-to-run spread |

## Cause

About 3,381 operations carry `NoContraction`. The driver cannot fuse them.

## Options

| Option | Pros | Cons |
|---|---|---|
| `APS5_EXPERIMENT_CONTRACT` (drop `NoContraction`) | Driver can fuse multiply and add. | Results can differ from the console. New shader cache (86 GB). |

## Result

+0.21 FPS (4.94 to 5.15), inside the run-to-run spread. The cache was deleted.

## Why

Contraction saves few instructions on these shaders. The cost is in FP16 emulation and memory latency.

## Evidence

### Original

About 3,381 operations decorated `NoContraction`.

### Change

`APS5_EXPERIMENT_CONTRACT=1` (branch `diag/copy-reason`, `SpirvAluEmitterMath.cpp` `Exact()`).

### Reason

Let the driver fuse multiply and add.

### Improvement

+0.21 FPS (4.94 to 5.15). This is inside the run-to-run spread (the same flags gave 3.56 FPS in `stage1g`). Results can differ from the console. Not kept.

### Timings

| Bench | Setting | Menu FPS | GPU busy ms/frame |
|---|---|---|---|
| skipall | no contraction | 4.94 | 171.78 |
| contract | contraction, cold cache | no FPS | |
| contract2 | contraction, warm | 5.15 | 171.35 |

### Reports

- [report-contract2.txt](report-contract2.txt)
