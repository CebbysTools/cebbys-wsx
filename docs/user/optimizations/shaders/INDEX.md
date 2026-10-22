# Shaders

Status: `testing`

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
