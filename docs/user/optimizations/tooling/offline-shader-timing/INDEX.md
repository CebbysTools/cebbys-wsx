# Offline shader timing

Status: `researched`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| Time to measure one shader change | 3-15 min (game run) | not implemented | not measured |  |

## Cause

Each shader change needs a game run to measure its GPU time. A game run takes 3-5 minutes, and a translator change rebuilds the shader cache (about 45 GB, 5-10 minutes). Game runs also stress the GPU: it was lost two times on 2026-10-22.

## Options

| Option | What it gives | Pros | Cons |
|---|---|---|---|
| `agc_shader_replay --spv` (exists) | SPIR-V of a saved request, offline | No game, no GPU. Seconds. | No GPU time. No register count. |
| GPU unit tests (exist) | Exact results against a reference | Proves correctness. | No timing of real game shaders. |
| GPU replay timer (new tool) | GPU time and register count of a saved request | No game. One shader at a time. Repeatable. | Texture contents are not saved; data-dependent loops can differ. Needs work. |
| Nsight GPU Trace on the game | Full per-dispatch metrics | Real scene. | Slow. Memory-heavy. Lost the GPU once. |

## Result

Not implemented. The first two options are in use (see `shaders/fma-mix`).

## Why

A GPU replay timer gives most of the answer without the game: it compiles the saved request, creates the pipeline, reads the driver statistics (registers, binary size) and times N dispatches with timestamp queries.
The AO shader is a good first case: its loop counts come from constants in the request, not from texture contents.
