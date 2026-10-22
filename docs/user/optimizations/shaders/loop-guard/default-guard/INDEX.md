# Default loop guard

Status: `applied`

## Cause

Programs 0x11507f2800, 0x115150c000 and 0x11525e9400 looped without end.

## Options

Branch `fix/shader-default-loop-guard`: guard on by default, limit 2^17 evaluations. `APS5_LOOP_GUARD=0` turns it off.

## Result

GPU resets stopped. Full match completed.

## Why

The loop exits before the TDR limit of 2 s.
