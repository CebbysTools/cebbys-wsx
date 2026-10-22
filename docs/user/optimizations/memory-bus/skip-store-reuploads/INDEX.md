# Skip store re-uploads

Status: `rejected`

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
