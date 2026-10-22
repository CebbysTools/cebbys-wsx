# Keep FP64

Status: `rejected`

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
