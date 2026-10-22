# Float emulation

Status: `testing`

## Cause

The recompiler keeps PS5 float results exact. It emulates FP16 math in FP32, flushes denormals in software and fixes NaN values after each operation. This adds about 20 SPIR-V instructions per packed FP16 operation.

## Options

| Option | Pros | Cons |
|---|---|---|
| [Native FP16 FMA](native-f16-fma/INDEX.md) | Exact (fused, one rounding). 2x faster on FP16-heavy shaders. | Needs `VK_KHR_shader_fma`. |
| [Fast float](fast-float/INDEX.md) | Less code. | Not exact for NaN and denormals. No gain. |
| [Float contraction](float-contraction/INDEX.md) | Lets the driver fuse operations. | Not exact. No gain. New cache. |

## Result

Only native FP16 FMA gave a gain.

## Why

The two heaviest menu shaders are 53% FP16 instructions. FMA was the largest emulated part. Fast float and contraction removed checks that were not on the slow path.
