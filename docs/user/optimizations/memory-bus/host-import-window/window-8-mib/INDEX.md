# 8 MiB import window

Status: `rejected`

## Cause

The upstream default window is 8 MiB.

## Options

Keep the default. No code change.

## Result

Menu at about 2.0 FPS (bench `win8`).

## Why

Render targets cross many 8 MiB allocations, so the driver copies them with the CPU.
