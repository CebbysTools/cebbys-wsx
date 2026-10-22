# Skip read-backs

Status: `testing`

## Cause

Each read-back stops the CPU until the GPU finishes.

## Options

| Switch | What it skips |
|---|---|
| `APS5_EXPERIMENT_SKIP_PENDING_HTILE_READ` | The read of a pending cleared HTILE. |
| `APS5_EXPERIMENT_SKIP_KEY_SYNC` | The wait for DCC key writers. |
| `APS5_EXPERIMENT_SKIP_FLUSH_SYNC` | The sync in `FlushPending`. |
| `APS5_NO_PRESYNC` | The pre-sync before submission. |

Pros: measures the cost of each wait. Cons: the results can be wrong. These switches exist only on branch `diag/copy-reason`.

## Result

All together: about 5.2 FPS in the menu, from about 4 FPS. No rendering errors seen in the menu.

## Why

The waits are real, but each one is small. The gain shows that M2 is worth the work, not that these skips are safe.
