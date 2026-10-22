# NHL 27 optimizations

This folder records each optimization that we try on NHL 27 (PPSA34063) with AnyPS5.
The target is a stable 30 FPS, then 60 FPS, then 144 FPS. The plan is in [NHL 27 at 144 FPS](../NHL%2027%20at%20144%20FPS.md).

## Improvement summary

All numbers are from the NHL 27 menu on the RTX 4070 (i7-14700K, Windows 11), unless the row says otherwise. Each step adds to the step above it.

| Step | Bench | Menu FPS | Change from start | Kept |
|---|---|---|---|---|
| Start: first full nhl27 menu run (cold cache) | base-180 | 0.82 | | |
| Warm cache, loop guard on, 8 MiB import window | win8 | 2.02 | +146% | yes |
| + 256 MiB host import window | win256 | 4.04 | +393% | yes |
| + skip CPU read-backs (diagnostic switches) | skipall | 4.94 | +502% | diagnostic only |
| + float contraction | contract2 | 5.15 | +528% | no (inside spread, not exact) |
| + native FP16 FMA | f16fma-4, f16fma-5 | 1.2-1.5 (later, heavier scene) | not comparable | testing |
| Goal | | 30 | +3559% | |

Shader GPU time per dispatch, same menu programs:

| Program | Start (stage1g) | Now | Change | By |
|---|---|---|---|---|
| 0x1152fa6000 | 20.68 ms | 9.76 ms | -53% | native FP16 FMA |
| 0x1150e42000 | 17.19 ms | 14.86 ms | -14% | native FP16 FMA |
| 0x1161544500 | 16.72 ms | 13.87 ms | -17% | same run (no f16 change; scene difference) |
| 0x115258a000 | 339.48 ms | 338.52 ms | 0% | FP32 FMA mix fix not measured yet |

Each area has its own folder. Read the area INDEX.md for the summary of its optimizations.

| Area | Summary |
|---|---|
| [Memory bus](memory-bus/INDEX.md) | Data moves between system RAM and VRAM. The 256 MiB host import window gave the largest gain (2.0 to 4.0 FPS in the menu). |
| [CPU-GPU sync](cpu-gpu-sync/INDEX.md) | The CPU waits for GPU results. Skipping some read-backs gave a small gain (4.04 to 4.94 FPS). These are diagnostic experiments only. |
| [Shaders](shaders/INDEX.md) | Translated shaders are large and slow. Native fused FP16 FMA made shader 0x1152fa6000 2x faster. |
| [Tooling](tooling/INDEX.md) | Measure shaders without the game. A GPU replay timer is researched. |
| [Queues](queues/INDEX.md) | All PS5 queues use one Vulkan queue. A separate async compute queue is researched, not implemented. |

## Rules

- Do the research and write the record before you change code.
- One folder per optimization. One subfolder per option or variant.
- Each INDEX.md links only to the INDEX.md files of its direct child folders.
- Run `python3 fork-tools/optimizations/check_index.py` after each change to these files.
