# Ambient occlusion shader

Status: `researched`

## Improvement summary

| Metric | Start | Now | Change |
|---|---|---|---|
| 0x115258a000 ms per run | 339.48 | 339.48 | cause found, fix in testing |

## Cause

Program 0x115258a000 is a GTAO-style ambient occlusion pass at 2348x1320. It has an outer loop over slices and an inner loop over steps, with two texture samples per step. It takes about 340 ms per run. In one menu scene it used about 40% of all GPU time.

## Options

| Option | Pros | Cons |
|---|---|---|
| Find why samples are slow (SPIR-V via `APS5_DUMP_SHADERS` and `agc_shader_replay --spv`) | Fixes the cause. | Not done yet. |
| Run it on a separate queue (see [Queues](../../queues/INDEX.md)) | Graphics does not wait. | Large driver change. |

## Result

Cause found (offline replay): each inner step runs about 816 FP64 operations in the `v_fma_mix*` emulation. See `shaders/fma-mix` in the shaders INDEX.md.

## Why

On the PS5 this pass takes a few ms. A 100x difference points to how its textures are bound or sampled. The SPIR-V is still needed.
