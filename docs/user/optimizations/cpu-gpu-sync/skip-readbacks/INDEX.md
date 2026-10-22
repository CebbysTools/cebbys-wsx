# Skip read-backs

Status: `testing`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| Menu FPS | 4.04 (win256) | 4.94 (skipall) | 22 | diagnostic switches only |

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

All together: 4.94 FPS in the menu, from 4.04 FPS (bench `skipall`). No rendering errors seen in the menu.

## Why

The waits are real, but each one is small. The gain shows that M2 is worth the work, not that these skips are safe.

## Evidence

### Original

The CPU waits for GPU read-backs (HTILE, DCC keys, flush sync, pre-sync).

### Change

Switches on branch `diag/copy-reason`: `APS5_EXPERIMENT_SKIP_PENDING_HTILE_READ`, `APS5_PIPELINE_DISPATCH`, `APS5_EXPERIMENT_SKIP_KEY_SYNC`, `APS5_EXPERIMENT_SKIP_FLUSH_SYNC`, `APS5_NO_PRESYNC`.

### Reason

About 250 syncs per 10 s, each 2-6 ms.

### Improvement

Each skip added a little. All together: 4.04 to 4.94 FPS (improvement 22%).

### Timings

| Bench | Skips added | Menu FPS | GPU busy ms/frame |
|---|---|---|---|
| win256 | none | 4.04 | 189.24 |
| htileskip | HTILE read | 4.24 | 178.88 |
| keyskip | + pipelined dispatch, key sync | 4.20 | 175.48 |
| flushskip | + flush sync | 4.40 | 181.34 |
| nopresync | + no pre-sync | 4.57 | 213.35 |
| skipall | all | 4.94 | 171.78 |

### Reports

- [report-skipall.txt](report-skipall.txt)
