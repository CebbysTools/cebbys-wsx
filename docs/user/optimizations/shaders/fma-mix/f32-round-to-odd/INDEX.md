# FP32 round-to-odd

Status: `testing`

## Improvement summary

| Metric | Start | Now | Change |
|---|---|---|---|
| 0x115258a000 ms per run | 338.52 | not measured | pending |

## Cause

The result must be `round_f16(a * b + c)` with one rounding. A fused FP32 FMA rounds to f32 first. Rounding that f32 to f16 again can give a different result (double rounding).

## Options

| Step | Operation |
|---|---|
| 1 | `r = OpFmaKHR(a, b, c)` in f32 (fused, round to nearest even). |
| 2 | Find if `r` is exact, and the sign of the error. Use the error-free FMA error terms (Boldo-Muller ErrFma, FP32 only). |
| 3 | If not exact, set `r` to round-to-odd: move toward zero if needed, then set the last mantissa bit. |
| 4 | Convert `r` to f16 with round to nearest even. |

Pros: exact for all inputs, because f32 has at least 2 more bits than f16 (Boldo-Melquiond round-to-odd theorem). FP32 only. Same method as `fmaF16RoundedToOdd` uses for `v_fma_f16`.
Cons: more operations than one FMA. Denormal, overflow and NaN cases need the same handling as today.

## Result

Implemented on branch `perf/shader-fma-mix-fp32` (stacked on `perf/shader-native-f16-fma`). Seven interpolation and mix tests pass bit-exact against the reference. The AO shader now runs `OpFmaKHR` in its inner loop; the f64 helper stays as the fallback branch. Game timing is not measured yet.

## Why

This option removes all FP64 from the helper. It keeps exact console results, which upstream requires.

## Evidence

### Original

Every `v_fma_mix*` and f16 interpolation calls `interpolate_f16_mode_0` (f64, 235 instructions, 34 f64 results).

### Change

Branch `perf/shader-fma-mix-fp32`, commit `perf(shader): fp32 fast path for fma mix and f16 interpolation`. Files: `SpirvAluEmitterFloat64.cpp` (`InterpolateFast`, `EmitInterpolate`), `VulkanDevice.cpp` (enable `shaderFmaFloat32`).

### Reason

About 816 f64 operations per inner step of the AO shader 0x115258a000 (340 ms per run).

### Improvement

Exactness kept: 2048 random rows and 32 hardware rows in 32 float modes match the reference. GPU time: not measured yet.

### Timings

| Item | Before | After |
|---|---|---|
| SPIR-V words (AO shader) | 66,695 | 81,945 |
| `OpFmaKHR` in module | 60 | 136 |
| Inner loop instructions (static) | 2,613 | 4,417 |
| f64 helper calls in inner loop | 24, always run | 24, only on the fallback branch |
| GPU ms per run | 338.52 (bench f16fma-5) | not measured |

### Reports

- [report-replay-tests.txt](report-replay-tests.txt)
- [report-f64.txt](../keep-f64/report-f64.txt) is in a sibling folder; the before GPU time is in it.
