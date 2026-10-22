# FMA mix without FP64

Status: `testing`

## Improvement summary

| Optimization | Status | Metric | Start | Now | Change |
|---|---|---|---|---|---|
| [FP32 round-to-odd](f32-round-to-odd/INDEX.md) | `testing` | 0x115258a000 ms per run | 338.52 | not measured | pending |
| [Keep FP64](keep-f64/INDEX.md) | `rejected` | 0x115258a000 ms per run | 339.48 | 338.52 | baseline |
| [Native f16 when all operands are f16](native-f16-operands/INDEX.md) | `researched` | 0x115258a000 ms per run | 338.52 | not implemented | n/a |

## Cause

`v_fma_mix_f32`, `v_fma_mixlo_f16` and `v_fma_mixhi_f16` multiply and add f16 and f32 operands, then round once.
The recompiler emulates them with FP64 math (`CallInterpolate`, helper `interpolate_f16_mode_0`). The same helper serves f16 attribute interpolation.
The RTX 4070 runs FP64 at a small fraction of the FP32 rate.

Measured on the ambient occlusion shader `0x115258a000` (offline replay with `agc_shader_replay --spv`, request from bench `reqdump`):

| Item | Value |
|---|---|
| Module | 66,695 SPIR-V words, 13,949 instructions |
| Inner loop body | 2,613 instructions, 4 image samples |
| Helper calls in the inner loop | 24 |
| Helper size | 235 instructions, 34 with FP64 results |
| FP64 operations per inner step | about 816 |
| GPU time per run | about 340 ms (2348x1320) |

## Options

| Option | Pros | Cons |
|---|---|---|
| [FP32 round-to-odd](f32-round-to-odd/INDEX.md) | Exact for all operand types. FP32 only. | About 15-25 FP32 operations per call. Needs `shaderFmaFloat32`. |
| [Native f16 when all operands are f16](native-f16-operands/INDEX.md) | One `OpFmaKHR`. Exact. | Only when no operand is f32. The AO shader mixes f32 operands. |
| [Keep FP64](keep-f64/INDEX.md) | Exact. No work. | Very slow on consumer GPUs. |

## Result

FP32 round-to-odd is implemented and passes the tests. GPU time of `0x115258a000` is not measured yet.

## Why

The hypothesis is that FP64 throughput, not texture latency, makes this shader slow. The earlier Nsight `long_scoreboard` stall can also come from long FP64 sequences. The loop guard test fits this: fewer iterations cut the time in proportion.
