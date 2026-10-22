# Skip store re-uploads

Status: `rejected`

## Improvement summary

| Metric | Start | Now | Change |
|---|---|---|---|
| Menu FPS (win256 → devnext-skipstore) | 4.04 | 1.54-2.80 | worse, glyphs lost |

## Cause

The driver uploads storage images again over its own write-backs.

## Options

| Option | Pros | Cons |
|---|---|---|
| Skip the re-upload (`APS5_SKIP_STORE_UPLOADS`) | Up to 5 FPS in menus. | Text glyphs disappear. |

## Result

Branch `perf/agc-skip-store-reuploads`. Up to 5 FPS, but text glyphs disappear.

## Why

Some re-uploads carry CPU writes that the GPU needs. The skip loses them. A correct fix needs to know which bytes changed.

## Evidence

### Original

The driver uploads storage images again over its own write-backs.

### Change

`APS5_EXPERIMENT_SKIP_STORE_UPLOADS=1` (branch `perf/agc-skip-store-reuploads`).

### Reason

Fewer uploads per frame.

### Improvement

Not stable: the two runs gave 2.8 and 1.54 FPS. Text glyphs disappeared. Rejected.

### Timings

| Bench | Setting | Menu FPS | GPU busy ms/frame |
|---|---|---|---|
| win256 | no skip | 4.04 | 189.24 |
| devnext-skipstore-a | skip | 2.80 | 166.78 |
| devnext-skipstore-b | skip | 1.54 | 289.04 |

### Reports

- [report-skipstore.txt](report-skipstore.txt)
- Note: the skip runs used the dev-next build; the baseline row uses the nhl27 build.
