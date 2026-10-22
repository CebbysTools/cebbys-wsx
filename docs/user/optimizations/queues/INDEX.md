# Queues

Status: `researched`

## Cause

All PS5 queues are recorded by one global `Recorder` and submitted to one `VkQueue` under one mutex. Long compute work blocks graphics. 95% of driver thread samples wait for this mutex.

## Options

| Option | Pros | Cons |
|---|---|---|
| [Async compute queue](async-compute-queue/INDEX.md) | Graphics does not wait for async compute. | Needs cross-queue hazard tracking (M4). |
| Per-queue recorders (M3) | Less lock time. Parallel recording. | Large design. |

## Result

Not implemented.

## Why

These are the largest structural limits, but they need design work first. See `fork-notes/M3_DISPATCH_LOCK_DESIGN.md`.
