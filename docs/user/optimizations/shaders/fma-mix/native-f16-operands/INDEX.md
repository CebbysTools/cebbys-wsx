# Native f16 when all operands are f16

Status: `researched`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| 0x115258a000 GPU ms per run | 338.52 (f16fma-5) | not implemented | not measured |  |

## Cause

When `op_sel_hi` marks all three operands as f16, `v_fma_mix*` equals `v_fma_f16`.

## Options

| Option | Pros | Cons |
|---|---|---|
| Emit `OpFmaKHR` on f16 for this case | One operation. Exact. Already tested for `v_fma_f16`. | Does not help when any operand is f32. |

## Result

Not implemented. The AO inner loop mixes f32 sample results, so this case does not apply there.

## Why

Useful as a second step for other shaders. It does not fix `0x115258a000`.
