# Float contraction

Status: `no-gain`

## Cause

About 3,381 operations carry `NoContraction`. The driver cannot fuse them.

## Options

| Option | Pros | Cons |
|---|---|---|
| `APS5_EXPERIMENT_CONTRACT` (drop `NoContraction`) | Driver can fuse multiply and add. | Results can differ from the console. New shader cache (86 GB). |

## Result

No FPS change. The cache was deleted.

## Why

Contraction saves few instructions on these shaders. The cost is in FP16 emulation and memory latency.
