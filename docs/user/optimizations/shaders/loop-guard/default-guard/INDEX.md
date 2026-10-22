# Default loop guard

Status: `applied`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| GPU resets in a match | yes (nvlddmkm 153) | none | not a timing | stability fix |

## Cause

Programs 0x11507f2800, 0x115150c000 and 0x11525e9400 looped without end.

## Options

Branch `fix/shader-default-loop-guard`: guard on by default, limit 2^17 evaluations. `APS5_LOOP_GUARD=0` turns it off.

## Result

GPU resets stopped. Full match completed.

## Why

The loop exits before the TDR limit of 2 s.

## Evidence

### Original

Loops not guarded. Programs 0x11507f2800, 0x115150c000, 0x11525e9400 hung the GPU (nvlddmkm 153).

### Change

Branch `fix/shader-default-loop-guard`: guard on by default, 2^17 evaluations.

### Reason

Windows reset the GPU during matches.

### Improvement

No GPU resets. A 37-minute CPU vs CPU match and a 2-hour soak passed. No FPS change expected.

### Timings

| Bench | Build | Menu FPS | GPU busy ms/frame | 0x1152fa6000 ms/run |
|---|---|---|---|---|
| baseline-nhl27-a | before | 1.02 | 415.18 | 24.21 |
| guarddefault-a | guard, cold cache | 1.11 | 367.95 | 23.73 |
| guarddefault-b | guard, warm | 2.12 | 213.48 | 22.77 |

### Reports

- [report-guarddefault.txt](report-guarddefault.txt)
- GPU reset logs (Windows event 153) and the soak: report not kept.
