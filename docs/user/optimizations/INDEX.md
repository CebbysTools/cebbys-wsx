# NHL 27 optimizations

This folder records each optimization that we try on NHL 27 (PPSA34063) with AnyPS5.
The target is a stable 30 FPS, then 60 FPS, then 144 FPS. The plan is in [NHL 27 at 144 FPS](../NHL%2027%20at%20144%20FPS.md).

Each area has its own folder. Read the area INDEX.md for the summary of its optimizations.

| Area | Summary |
|---|---|
| [Memory bus](memory-bus/INDEX.md) | Data moves between system RAM and VRAM. The 256 MiB host import window gave the largest gain (2.0 to 4.0 FPS in the menu). |
| [CPU-GPU sync](cpu-gpu-sync/INDEX.md) | The CPU waits for GPU results. Skipping some read-backs gave a small gain (to about 5.2 FPS). These are diagnostic experiments only. |
| [Shaders](shaders/INDEX.md) | Translated shaders are large and slow. Native fused FP16 FMA made shader 0x1152fa6000 2x faster. |
| [Queues](queues/INDEX.md) | All PS5 queues use one Vulkan queue. A separate async compute queue is researched, not implemented. |

## Rules

- Do the research and write the record before you change code.
- One folder per optimization. One subfolder per option or variant.
- Each INDEX.md links only to the INDEX.md files of its direct child folders.
- Run `python3 fork-tools/optimizations/check_index.py` after each change to these files.
