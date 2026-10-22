# Float emulation

Status: `testing`

## Improvement summary

| Optimization | Status | Metric | Start | Now | Change |
|---|---|---|---|---|---|
| [Fast float](fast-float/INDEX.md) | `no-gain` | 0x1152fa6000 ms per dispatch | 20.91 | 27.33 | no gain (no-cache run) |
| [Float contraction](float-contraction/INDEX.md) | `no-gain` | Menu FPS (skipall → contract2) | 4.94 | 5.15 | +4%, inside spread |
| [Native FP16 FMA](native-f16-fma/INDEX.md) | `testing` | 0x1152fa6000 ms per dispatch | 20.68 | 9.76 | -53% |

## Cause

The recompiler keeps PS5 float results exact. It emulates FP16 math in FP32, flushes denormals in software and fixes NaN values after each operation. This adds about 20 SPIR-V instructions per packed FP16 operation.

## Options

| Option | Pros | Cons |
|---|---|---|
| [Native FP16 FMA](native-f16-fma/INDEX.md) | Exact (fused, one rounding). 2x faster on FP16-heavy shaders. | Needs `VK_KHR_shader_fma`. |
| [Fast float](fast-float/INDEX.md) | Less code. | Not exact for NaN and denormals. No gain. |
| [Float contraction](float-contraction/INDEX.md) | Lets the driver fuse operations. | Not exact. +0.21 FPS, inside the spread. New cache. |

## Result

Only native FP16 FMA gave a gain.

## Why

The two heaviest menu shaders are 53% FP16 instructions. FMA was the largest emulated part. Fast float and contraction removed checks that were not on the slow path.
