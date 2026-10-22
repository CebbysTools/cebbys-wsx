# Fast float

Status: `no-gain`

## Cause

Software denormal flush and NaN fix-ups add code to each float operation.

## Options

| Option | Pros | Cons |
|---|---|---|
| `APS5_FAST_FLOAT` (branch `feat/shader-fast-float`) | Less code. | Differs from the console for denormal and NaN values. |

## Result

Shader 0x115258a000: 3,711 ms vs 3,737 ms per 10 s. No FPS change.

## Why

The slow shader is limited by texture latency, not by float checks.
