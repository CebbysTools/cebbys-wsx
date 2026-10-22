# Loop guard

Status: `applied`

## Improvement summary

| Optimization | Status | Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|---|---|
| [Default loop guard](default-guard/INDEX.md) | `applied` | GPU resets in a match | yes (nvlddmkm 153) | none | not a timing | stability fix |
| [Loop guard 64 test](guard-64-test/INDEX.md) | `researched` | 0x115258a000 GPU ms per run | 338.52 (f16fma-5) | 257.75 (guard64b) | 31 | test only, not a fix |

## Cause

Some shader loops ran without end on the PC and reset the GPU (Windows TDR, nvlddmkm 153).

## Options

| Option | Pros | Cons |
|---|---|---|
| [Default guard](default-guard/INDEX.md) | No more GPU resets. | A guarded loop exits early. |
| [Guard 64 test](guard-64-test/INDEX.md) | Shows if a slow shader loops too long. | Not a fix. New shader cache. |

## Result

The default guard stopped the GPU resets. A 37-minute CPU vs CPU match ran.

## Why

The runaway loops came from data the PC did not match yet. A guard ends them before Windows resets the GPU.
