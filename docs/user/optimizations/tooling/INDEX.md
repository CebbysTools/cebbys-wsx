# Tooling

Status: `researched`

## Improvement summary

| Optimization | Status | Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|---|---|
| [Offline shader timing](offline-shader-timing/INDEX.md) | `researched` | Time to measure one shader change | 3-15 min (game run) | not implemented | not measured |  |

## Cause

Measurements need game runs. These are slow and stress the GPU.

## Options

| Option | Pros | Cons |
|---|---|---|
| [Offline shader timing](offline-shader-timing/INDEX.md) | Measure one shader without the game. | Needs a new tool. |

## Result

Researched.

## Why

Faster measurements give more optimization steps per hour, with less risk to the GPU.
