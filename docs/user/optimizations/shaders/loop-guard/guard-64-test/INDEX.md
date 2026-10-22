# Loop guard 64 test

Status: `researched`

## Cause

Shader 0x115258a000 (ambient occlusion) takes about 340 ms. A loop that runs too long would explain this.

## Options

`APS5_LOOP_GUARD=64` caps each loop at 64 evaluations.

## Result

0x115258a000 went to 258 ms. Its guard never tripped.

## Why

Its loops are short and correct. The cost is texture sample latency, not loop count.
