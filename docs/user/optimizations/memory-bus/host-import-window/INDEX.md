# Host import window

Status: `applied`

## Improvement summary

| Optimization | Status | Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|---|---|
| [256 MiB import window](window-256-mib/INDEX.md) | `applied` | Menu FPS | 2.02 (win8) | 4.04 (win256) | 100 |  |
| [64 MiB import window](window-64-mib/INDEX.md) | `rejected` | Menu FPS | 2.02 (win8) | 3.48 (win64) | 72 |  |
| [8 MiB import window](window-8-mib/INDEX.md) | `rejected` | Menu FPS | 2.02 (win8) | 2.02 (win8) | 0 | baseline |

## Cause

The driver imports guest memory into Vulkan with `VK_EXT_external_memory_host` in windows of 8 MiB.
Render targets at `0x11c...` span many 8 MiB allocations. The driver could not import them and copied them with the CPU each frame.

## Options

| Option | Pros | Cons |
|---|---|---|
| [8 MiB window](window-8-mib/INDEX.md) | Upstream default. Small pinned size. | Large targets are copied by the CPU. |
| [64 MiB window](window-64-mib/INDEX.md) | Fewer CPU copies. | Some targets still do not fit. |
| [256 MiB window](window-256-mib/INDEX.md) | Large targets import in place. Largest gain. | More pinned memory. Needs the resident-run fix. |

## Result

Branch `perf/agc-host-import-window` sets the default to 256 MiB (`APS5_HOST_IMPORT_WINDOW_MIB`). Menu FPS went from 2.0 to 4.04.

## Why

The CPU copies were on the critical path. Import in place removed them. The GPU now reads these targets over PCIe, which is slower than VRAM, but faster than a CPU copy each frame.
