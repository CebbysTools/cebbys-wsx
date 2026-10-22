# Native FP16 FMA

Status: `testing`

## Cause

`v_fma_f16`, `v_fmac_f16`, `v_fmamk_f16`, `v_fmaak_f16`, `v_pk_fma_f16` and `v_pk_fmac_f16` were emulated in FP32 with round-to-odd (about 13 operations per lane). Plain Vulkan `Fma` is not guaranteed to be fused, so a native path was not allowed.

## Options

| Option | Pros | Cons |
|---|---|---|
| `OpFmaKHR` on `f16vec2` with `SPV_KHR_fma` (applied) | Fused by definition, one rounding, as RDNA. Exact. | Needs `shaderFmaFloat16`. NaN, overflow and clamp fix-ups stay. |
| GLSL `Fma` on `half` | No extension. | Not guaranteed fused. Not exact. |
| Keep the emulation | Exact on every GPU. | Large and slow code. |

## Result

Branch `perf/shader-native-f16-fma`. RTX 4070, driver 610.88, `shaderFmaFloat16 = true`.

| Program | Before | After |
|---|---|---|
| `0x1152fa6000` | 20.5-23 ms, 244k words | 9.0-9.8 ms, 167k words |
| `0x1150e42000` | 17.2 ms, 355k words | 14.9-17.9 ms, 172k words, 253 registers |
| `0x115258a000` | 82.6k words | 65.5k words |

Nine FP16 execution tests pass. Native results are bit-exact with the emulation (NaN payloads excepted). Tests with validation layers are not done yet.

## Why

The FMA emulation was the largest part of the FP16 code. One native operation replaced about 13. `0x1150e42000` gained less, because it now uses 253 registers, and occupancy fell.
Shader validation needed `FMAKHR` and `SPV_KHR_fma` in its allow lists.
