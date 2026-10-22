# CPU-GPU sync

Status: `testing`

## Cause

The CPU reads GPU results back (DCC keys, HTILE, pending writes). Each read is a GPU round trip under one global mutex. In the menu there are about 250 syncs per 10 s, each 2-6 ms.

## Options

| Option | Pros | Cons |
|---|---|---|
| [Skip read-backs (experiments)](skip-readbacks/INDEX.md) | Shows the possible gain. | Not correct in general. Diagnostic only. |
| Decide from recorded state (M2 S1-S4) | Correct. Removes the waits. | Large design work. Not started. |

## Result

The experiments together raised the menu to about 5.2 FPS (bench `contract2`, 5.15 FPS).

## Why

Each read-back removed alone gives a small gain. Queue 0 then waits for the GPU (`memory_wait` about 86 ms per frame). The real fix is M2: keep this state on the GPU or record it.
