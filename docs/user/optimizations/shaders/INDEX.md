# Shaders

Status: `testing`

## Improvement summary

| Optimization | Status | Metric | Start | Now | Change |
|---|---|---|---|---|---|
| [Ambient occlusion shader](ambient-occlusion/INDEX.md) | `researched` | 0x115258a000 ms per run | 339.48 | 339.48 | cause found, fix in testing |
| [Float emulation](float-emulation/INDEX.md): Fast float | `no-gain` | 0x1152fa6000 ms per dispatch | 20.91 | 27.33 | no gain (no-cache run) |
| [Float emulation](float-emulation/INDEX.md): Float contraction | `no-gain` | Menu FPS (skipall → contract2) | 4.94 | 5.15 | +4%, inside spread |
| [Float emulation](float-emulation/INDEX.md): Native FP16 FMA | `testing` | 0x1152fa6000 ms per dispatch | 20.68 | 9.76 | -53% |
| [FMA mix without FP64](fma-mix/INDEX.md): FP32 round-to-odd | `testing` | 0x115258a000 ms per run | 338.52 | not measured | pending |
| [FMA mix without FP64](fma-mix/INDEX.md): Keep FP64 | `rejected` | 0x115258a000 ms per run | 339.48 | 338.52 | baseline |
| [FMA mix without FP64](fma-mix/INDEX.md): Native f16 when all operands are f16 | `researched` | 0x115258a000 ms per run | 338.52 | not implemented | n/a |
| [Loop guard](loop-guard/INDEX.md): Default loop guard | `applied` | GPU resets in a match | yes (nvlddmkm 153) | none | fixed |
| [Loop guard](loop-guard/INDEX.md): Loop guard 64 test | `researched` | 0x115258a000 ms per run | 338.52 | 257.75 | test only, not a fix |
| [SPIR-V optimizer](spirv-optimizer/INDEX.md) | `rejected` | 0x1152fa6000 ms per dispatch | 20.68 | 21.01-27.38 | worse |

## Cause

The recompiler translates RDNA shaders to SPIR-V. It emulates PS5 float rules (NaN, denormals, FP16) with many extra instructions. The heavy menu programs have 244k-355k SPIR-V words and 128-255 registers. Heavy menu frames cost about 165 ms of GPU time.

## Options

| Option | Pros | Cons |
|---|---|---|
| [Float emulation](float-emulation/INDEX.md) | Native FP16 FMA made one heavy shader 2x faster. | Each change rebuilds the shader cache (about 45 GB). |
| [Loop guard](loop-guard/INDEX.md) | Stops GPU resets from runaway loops. | No speed gain. |
| [SPIR-V optimizer](spirv-optimizer/INDEX.md) | Could shrink modules. | Build takes hours and runs hung. Rejected. |
| [FMA mix without FP64](fma-mix/INDEX.md) | Removes FP64 from `v_fma_mix*` and f16 interpolation. | Researched, not implemented. |
| [Ambient occlusion shader](ambient-occlusion/INDEX.md) | Largest single cost (about 340 ms per run). | Cause not found yet. |

## Result

Native fused FP16 FMA: shader 0x1152fa6000 went from 20.5-23 ms to 9.0-9.8 ms per dispatch.

## Why

Shaders that are mostly FP16 math gain from native FP16. Other emulation removals gave no gain. The ambient occlusion shader is limited by texture sample latency, not by math.
