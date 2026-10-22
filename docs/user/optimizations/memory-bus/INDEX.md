# Memory bus

Status: `testing`

## Improvement summary

| Optimization | Status | Metric | Start | Now | Change |
|---|---|---|---|---|---|
| [GDS copy on GPU](gds-copy-on-gpu/INDEX.md) | `no-gain` | Device drains per 10 s | 1050 | 0 | -100%; FPS unchanged |
| [Host import window](host-import-window/INDEX.md): 256 MiB import window | `applied` | Menu FPS (win8 → win256) | 2.02 | 4.04 | +100% |
| [Host import window](host-import-window/INDEX.md): 64 MiB import window | `rejected` | Menu FPS (win8 → win64) | 2.02 | 3.48 | +72% |
| [Host import window](host-import-window/INDEX.md): 8 MiB import window | `rejected` | Menu FPS (win8) | 2.02 | 2.02 | baseline |
| [Skip store re-uploads](skip-store-reuploads/INDEX.md) | `rejected` | Menu FPS (win256 → devnext-skipstore) | 4.04 | 1.54-2.80 | worse, glyphs lost |
| [Storage cache priority](storage-cache-priority/INDEX.md) | `applied` | Menu FPS | not measured | not measured | report not kept |
| [VRAM staging](vram-staging/INDEX.md) | `no-gain` | Menu FPS (htileskip → stagereads) | 4.24 | 3.36 | -21% |

## Cause

On the PS5, the CPU and the GPU use the same memory. On Windows, game memory stays in system RAM, and the GPU reads it over PCIe.
The driver copies or imports guest memory before the GPU can use it. About 1.2 GiB per frame crosses PCIe in the menu.

## Options

| Option | Pros | Cons |
|---|---|---|
| [Host import window](host-import-window/INDEX.md) | GPU reads system RAM in place. Fewer CPU copies. | Reads go over PCIe. Pinned memory is limited. |
| [Storage cache priority](storage-cache-priority/INDEX.md) | Less evict and re-upload of storage images. | Less cache space for sampled textures. |
| [GDS copy on GPU](gds-copy-on-gpu/INDEX.md) | No device drain for small copies. | No FPS change. |
| [VRAM staging](vram-staging/INDEX.md) | Reads come from VRAM. | Extra copies. No FPS change. |
| [Skip store re-uploads](skip-store-reuploads/INDEX.md) | Fewer uploads. | Text glyphs disappear. Rejected. |

## Result

The import window gave the largest gain so far: 2.0 to 4.0 FPS in the menu. The other options gave no measurable FPS gain.

## Why

The menu was limited by CPU copies of render targets that crossed 8 MiB import windows. A larger window removed those copies.
After that change, the limit moved to CPU-GPU sync and shader time, so other memory changes did not show in FPS.
A full fix needs GPU-resident memory (design M2 in `fork-notes/M2_GPU_RESIDENT_MEMORY_DESIGN.md`).
