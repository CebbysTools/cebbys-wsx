# NHL 27 optimizations

This folder records each optimization that we try on NHL 27 (PPSA34063) with AnyPS5.
The target is a stable 30 FPS, then 60 FPS, then 144 FPS. The plan is in [NHL 27 at 144 FPS](../NHL%2027%20at%20144%20FPS.md).

## Improvement summary

All numbers are from the NHL 27 menu on the RTX 4070 (i7-14700K, Windows 11), unless the row says otherwise.
Improvement % = (now / start - 1) x 100 for FPS, and (start / now - 1) x 100 for times. Higher is better. A negative value means worse.

### Cumulative menu FPS

Each step adds to the step above it.

| Step | Bench | Menu FPS | Improvement % from start | Kept |
|---|---|---|---|---|
| Start: first full nhl27 menu run (cold cache) | base-180 | 0.82 | 0 | |
| Warm cache, loop guard on, 8 MiB import window | win8 | 2.02 | 146 | yes |
| 256 MiB host import window | win256 | 4.04 | 393 | yes |
| Skip CPU read-backs (diagnostic switches) | skipall | 4.94 | 502 | diagnostic only |
| Float contraction | contract2 | 5.15 | 528 | no (inside spread, not exact) |
| Native FP16 FMA | f16fma-4, f16fma-5 | 1.2-1.5 (later, heavier scene) | not comparable | testing |
| Goal | | 30 | 3559 | |

### All optimizations

| Optimization | Status | Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|---|---|
| [CPU-GPU sync](cpu-gpu-sync/INDEX.md): Skip read-backs | `testing` | Menu FPS | 4.04 (win256) | 4.94 (skipall) | 22 | diagnostic switches only |
| [Memory bus](memory-bus/INDEX.md): GDS copy on GPU | `no-gain` | Menu FPS | 0.82 (base-180) | not measured | not measured | device drains per 10 s: 1050 to 0 |
| [Memory bus](memory-bus/INDEX.md): Host import window / 256 MiB import window | `applied` | Menu FPS | 2.02 (win8) | 4.04 (win256) | 100 |  |
| [Memory bus](memory-bus/INDEX.md): Host import window / 64 MiB import window | `rejected` | Menu FPS | 2.02 (win8) | 3.48 (win64) | 72 |  |
| [Memory bus](memory-bus/INDEX.md): Host import window / 8 MiB import window | `rejected` | Menu FPS | 2.02 (win8) | 2.02 (win8) | 0 | baseline |
| [Memory bus](memory-bus/INDEX.md): Skip store re-uploads | `rejected` | Menu FPS | 4.04 (win256) | 1.54-2.80 (devnext-skipstore) | -62 to -31 | worse, text glyphs lost |
| [Memory bus](memory-bus/INDEX.md): Storage cache priority | `applied` | Menu FPS | not measured | not measured | not measured | report not kept |
| [Memory bus](memory-bus/INDEX.md): VRAM staging | `no-gain` | Menu FPS | 4.24 (htileskip) | 3.36 (stagereads) | -21 | worse |
| [Queues](queues/INDEX.md): Async compute queue | `researched` | Graphics wait behind 0x115258a000 | about 340 ms per run | not implemented | not measured |  |
| [Shaders](shaders/INDEX.md): Ambient occlusion shader | `researched` | 0x115258a000 GPU ms per run | 339.48 (stage1g) | 339.48 | 0 | cause found, fix in testing |
| [Shaders](shaders/INDEX.md): Float emulation / Fast float | `no-gain` | 0x1152fa6000 GPU ms per dispatch | 20.91 (htileskip) | 27.33 (fastfloat) | -23 | run without shader cache |
| [Shaders](shaders/INDEX.md): Float emulation / Float contraction | `no-gain` | Menu FPS | 4.94 (skipall) | 5.15 (contract2) | 4 | inside run-to-run spread |
| [Shaders](shaders/INDEX.md): Float emulation / Native FP16 FMA | `testing` | 0x1152fa6000 GPU ms per dispatch | 20.68 (stage1g) | 9.76 (f16fma-5) | 112 |  |
| [Shaders](shaders/INDEX.md): FMA mix without FP64 / FP32 round-to-odd | `testing` | 0x115258a000 GPU ms per run | 338.52 (f16fma-5) | not measured | not measured | tests pass |
| [Shaders](shaders/INDEX.md): FMA mix without FP64 / Keep FP64 | `rejected` | 0x115258a000 GPU ms per run | 339.48 (stage1g) | 338.52 (f16fma-5) | 0 | baseline |
| [Shaders](shaders/INDEX.md): FMA mix without FP64 / Native f16 when all operands are f16 | `researched` | 0x115258a000 GPU ms per run | 338.52 (f16fma-5) | not implemented | not measured |  |
| [Shaders](shaders/INDEX.md): Loop guard / Default loop guard | `applied` | GPU resets in a match | yes (nvlddmkm 153) | none | not a timing | stability fix |
| [Shaders](shaders/INDEX.md): Loop guard / Loop guard 64 test | `researched` | 0x115258a000 GPU ms per run | 338.52 (f16fma-5) | 257.75 (guard64b) | 31 | test only, not a fix |
| [Shaders](shaders/INDEX.md): SPIR-V optimizer | `rejected` | 0x1152fa6000 GPU ms per dispatch | 20.68 (stage1g) | 21.01-27.38 (opt5, opt-warm) | -24 to -2 | worse |
| [Tooling](tooling/INDEX.md): Offline shader timing | `researched` | Time to measure one shader change | 3-15 min (game run) | not implemented | not measured |  |

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
