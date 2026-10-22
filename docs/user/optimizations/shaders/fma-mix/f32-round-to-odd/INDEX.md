# FP32 round-to-odd

Status: `researched`

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

Not implemented.

## Why

This option removes all FP64 from the helper. It keeps exact console results, which upstream requires.
