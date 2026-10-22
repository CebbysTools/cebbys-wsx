# Native FP16 FMA

Status: `testing`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| 0x1152fa6000 GPU ms per dispatch | 20.68 (stage1g) | 9.76 (f16fma-5) | 112 |  |

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

Nine FP16 execution tests pass. Native results are bit-exact with the emulation (NaN payloads excepted). With `VK_LAYER_KHRONOS_validation`, all nine pass with 0 `VUID-` errors (2026-10-22).

## Why

The FMA emulation was the largest part of the FP16 code. One native operation replaced about 13. `0x1150e42000` gained less, because it now uses 253 registers, and occupancy fell.
Shader validation needed `FMAKHR` and `SPV_KHR_fma` in its allow lists.

## Evidence

### Original

`v_fma_f16`, `v_fmac_f16`, `v_fmamk_f16`, `v_fmaak_f16`, `v_pk_fma_f16`, `v_pk_fmac_f16` emulated in f32 with round-to-odd (`fmaF16RoundedToOdd`, about 13 operations per lane).

### Change

Branch `perf/shader-native-f16-fma`, 2 commits. `OpFmaKHR` on f16vec2 (`SpirvAluEmitterMath.cpp`, new IR op `FPFma16x2`, `FloatInstructions.cpp`), `VK_KHR_shader_fma` in `VulkanDevice.cpp`, `FMAKHR` and `SPV_KHR_fma` in `ShaderValidation.cpp`, tests `Float16Native.cpp`, `PackedFloat16Native.cpp`.

### Reason

The two heaviest menu programs are 53% f16 instructions. FMA was the largest emulated part.

### Improvement

Improvement: 0x1152fa6000 112%, 0x1150e42000 16%, 0x1161544500 21% (f16fma-5 scene; 0x1161544500 has no f16 change, so its value shows the scene difference). Tests: 9 pass, 0 `VUID-` errors.

### Timings

| Program | stage1g (before) | win256 (before) | stagereads (before) | f16fma-4 (after) | f16fma-5 (after) |
|---|---|---|---|---|---|
| 0x1152fa6000 | 20.68 | 21.3 | 20.5 | 9.5 | 9.76 |
| 0x1150e42000 | 17.19 | 17.3 | 17.2 | 17.9 | 14.86 |
| 0x1161544500 | 16.72 | 16.7 | 15.8 | 17.8 | 13.87 |

Values are ms per dispatch. The menu FPS of f16fma-4 and f16fma-5 (1.2 and 1.5) come from a later scene with other heavy programs, so they are not compared here.

### Reports

- [report-f16fma.txt](report-f16fma.txt)
