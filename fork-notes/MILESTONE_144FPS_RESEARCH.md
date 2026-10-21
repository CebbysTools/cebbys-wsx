# Milestone research: NHL 27 from 1-2 FPS to a 144 Hz experience

Fork-only. Companion to [AGC_DRIVER_PERFORMANCE.md](AGC_DRIVER_PERFORMANCE.md), which holds the measurements this plan starts from. Tasks live in the beans tracker (`beans list --tag nhl27-perf`).

## 1. Requirements

| # | Requirement | Measurable target |
|---|---|---|
| R1 | Respond sooner | Warm start (shader cache present) to first frame under 15 s; cold start (empty cache) to first interactive menu under 90 s; no multi-second freezes after the menu appears |
| R2 | Run at the display's 144 Hz | Native render at a stable 60 FPS (1% low >= 55) in menus and matches, presented at 120-144 Hz through frame generation; native unlock above 60 only if the title's simulation allows it (see 4.6) |
| R3 | Smaller displays (1080p and below) | Runs on a 1080p (and 1440p) display without the `2160p` workaround's cost: internal resolution chosen by the user, scaled output, windowed / borderless / fullscreen |
| R4 | Shareable, compact | A game-free kit (fork build, converter, launcher, setup script, patches) under 500 MB that turns each player's own dump into a playable install; an optional compressed install format for one's own copy. **No game files are packaged or shared.** |
| R5 | Additional (proposed) | Local multiplayer with up to 4 controllers on one PC; no GPU watchdog resets in a 2-hour session; shader cache under 10 GB; reach and play a match (fix the next known stop: sampling a depth surface's stencil plane); audio in sync at 60 FPS; input latency under 3 frames |

On R4: copying the game for friends is distribution of copyrighted content and is out of scope. Online play goes through EA/PSN services that AnyPS5 does not provide; "play together" is scoped to local multiplayer (R5).

## 2. Where the time goes today (summary of the measurements)

Menus at 1920x1080 output, 2348x1320 internal, RTX 4070, i7-14700K:

- ~400 ms GPU frame, GPU graphics engine active ~53%, SM throughput 10%: the GPU is starved by the CPU-side driver.
- One global `GpuMutex`: ~962 us wait per draw packet, ~980 us per dispatch inside the device call.
- ~1.2 GiB per frame of guest-memory traffic over PCIe (`storage-writeback`, `shadow-publish`, staging): every GPU result is written back to guest memory, whether the CPU reads it or not.
- CPU waits on the GPU inside the frame (`Recorder::Sync`, presyncs, flush hooks, CPU-read indirect arguments).
- Shader translation: some modules use 255 registers with spills (emulation-heavy), not the main limit in menus.
- Startup: ~26,000 shaders, ~5 minutes and ~40 GB cold; ~60 s warm to the menu.
- Long frames occasionally exceed Windows' 2 s TDR and reset the device.

Target: 400 ms -> 16.6 ms is a 24x reduction. No single change gives that; the plan stacks the four architectural fixes (memory, recording, sync, shaders) and measures after each.

## 3. How other projects solved the same problems

| Problem | Project and approach | Fit for AnyPS5 |
|---|---|---|
| Guest/host memory coherence | **yuzu / Ryujinx** buffer and texture caches: GPU-resident copies, CPU/GPU modified ranges tracked at page granularity, **lazy flush on CPU read** ([Ryujinx #1790 lazy flush-on-read](https://bytes.keithhacks.cyou/etc/ryujinx-mirror/commit/5d69d9103ef423719619658dc3378869692a5064); texture groups track each view's accesses, [TextureGroup.cs](https://bytes.keithhacks.cyou/etc/ryujinx-mirror/src/commit/32cad88cc60793f9ee6c11d15e8b5b71c3d725a2/Ryujinx.Graphics.Gpu/Image/TextureGroup.cs)); yuzu's buffer cache rewrite "keeps track of the modified CPU and GPU ranges on a CPU page granularity" ([suyu history](https://forge.k3s.fr/mirrors/suyu/commits/commit/2eff80b47f578b346bb80c5afa2271859cd7943b/src/video_core/dirty_flags.cpp)) | **Best fit.** AnyPS5 already has write watch (`GetWriteWatch`), unit shadows and resident images; what is missing is "GPU-written data stays on the GPU until the CPU reads it". |
| Downloads | **shadPS4**: async download of GPU-modified linear images, upload batching, upload around unmapped pages, garbage collector ([shadPS4 releases](https://github.com/shadps4-emu/shadPS4/releases)) | Async downloads and batching are direct inputs to M2. |
| Zero-copy guest buffers | `VK_EXT_external_memory_host`: import guest pages as Vulkan memory; synchronisation stays the app's job ([spec](https://docs.vulkan.org/refpages/latest/refpages/source/VK_EXT_external_memory_host.html); a translation VM reports copies into host buffers as "a major slowdown", [Qualcomm forum](https://developer.qualcomm.com/forum/qdn-forums/software/adreno-gpu-sdk/68161)) | AnyPS5 imports already. Imported memory is system RAM: right for CPU-shared buffers, wrong for render targets and storage images, which belong in VRAM (M2 policy). |
| Recording throughput | Khronos / Arm guidance: **one command pool per thread** (and per frame), reset whole pools, per-thread descriptor caches; a shared mutex on the command buffer path is the contention point to avoid ([Khronos sample](https://docs.vulkan.org/samples/latest/samples/performance/command_buffer_usage/README.html), [Vulkan threading guide](https://docs.vulkan.org/guide/latest/threading.html), [Arm](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/multi-threading-in-vulkan)) | Replace the global `GpuMutex` recording path with per-queue recorders (M3). |
| Shader stutter / startup | **Dolphin** ubershaders + async compile + disk cache (ubershaders remove most stutter; async alone "reduces the time", [Dolphin #12646](https://bugs.dolphin-emu.org/issues/12646), [GamingOnLinux](https://www.gamingonlinux.com/2017/07/the-gamecube-and-wii-emulator-dolphin-implements-ubershaders-to-solve-stuttering/page=1/)); **DXVK 2.0** `VK_EXT_graphics_pipeline_library`: compile stages when shaders load, link fast at draw ([Khronos blog](https://www.khronos.org/blog/reducing-draw-time-hitching-with-vk-ext-graphics-pipeline-library), [spec](https://docs.vulkan.org/refpages/latest/refpages/source/VK_EXT_graphics_pipeline_library.html)); limits remain in heavy cases ([GamingOnLinux](https://www.gamingonlinux.com/2023/01/ge-proton-removes-the-dxvk-async-patch-in-version-7-45/page=1/)) | AnyPS5 already uses pipeline libraries and a pipeline journal; missing: non-blocking first use (draw skip or fallback until ready), a smaller cache, background precompile ordered by first use. |
| Frame rate above the game's lock | **RPCS3**: raise vblank frequency plus per-game patches that change the game's timestep; without the patch animations and physics break ([RPCS3 blog](https://blog.rpcs3.net/?p=601), [Demon's Souls 60 FPS](https://wccftech.com/rpcs3-demons-souls-60fps-4k/amp/)) | A native unlock needs a title patch; risky for a sports simulation (R2 keeps it optional). |
| Presented frame rate | **AMD FSR 3.1 frame generation**: MIT-licensed, Vulkan backend, frame interpolation decoupled from upscaling, swapchain proxy handles pacing ([GPUOpen FSR 3](https://gpuopen.com/fsr3/), [SDK interpolation](https://gpuopen.com/manuals/fidelityfx_sdk/techniques/super-resolution-interpolation/), [FSR 3.1 Vulkan](https://www.gamingonlinux.com/2024/07/amd-releases-fidelityfx-sdk-110-with-fsr-31-and-vulkan-support/page=1/)); needs motion vectors, which a translator cannot get from the title ([gamescope #1213](https://github.com/ValveSoftware/gamescope/issues/1213)) | Use present-side interpolation with optical flow only (no game motion vectors) on the final image; 60 -> 120 FPS. 144 exact needs 72 rendered FPS or VRR pacing. |
| NHL 27 itself | **poonasor/AnyPS5 `dev-next`**: write-back loop fix (`SKIP_STORE_UPLOADS`, "~10 GB per 10 s"), no drain on page probes, GDS copies on the GPU, GPU-written vertex inputs without CPU waits, dispatches committed as pipeline items ([dev-next](https://github.com/poonasor/AnyPS5/tree/dev-next)) | Already cherry-picked onto `exp/dev-next-on-nhl27`; the quickest measurable step (M1). |

## 4. Chosen architecture (cherry-picked)

### 4.1 Memory: GPU-resident by default, lazily coherent (Ryujinx/yuzu model on AnyPS5's write watch)
- Every surface and buffer the GPU writes stays in VRAM. A write-back to guest memory happens only when (a) the CPU reads the pages (guard-page fault or write-watch query at a sync point the title uses: label wait, `sceAgcDcbWaitUntilSafeForRendering`, flip), or (b) a GPU consumer needs the guest layout (DMA to a CPU-mapped buffer).
- Page-granular CPU-modified and GPU-modified ranges per resource (the existing unit-shadow units become the tracking granule).
- Downloads are asynchronous (shadPS4) and batched per submission.
- Policy: render targets and storage images in VRAM; CPU-shared constant/vertex/index buffers imported in place.
- Exit criterion: PCIe traffic < 50 MiB per frame in menus.

### 4.2 Recording: per-queue recorders, short submit lock
- One recorder (command pool, descriptor cache, staging ring) per guest queue and per host worker thread (Khronos pattern).
- `PrepareDispatch` and draw preparation fully outside any global lock; the global lock covers only `vkQueueSubmit` and the cross-queue memory-order table.
- `dev-next`'s dispatch-as-pipeline-item is the first step.
- Exit criterion: lock wait < 20 us per draw, device call < 50 us per dispatch.

### 4.3 Synchronisation on the GPU
- Guest labels (`RELEASE_MEM`, `WRITE_DATA`) become GPU writes plus timeline-semaphore signals; `WAIT_REG_MEM` across queues becomes semaphore waits.
- Indirect arguments, GDS counters, CMASK/DCC/HTILE expansion resolved by GPU work, not CPU reads.
- The CPU waits only at present (frame pacing) and when the title itself waits on a label from the CPU.
- Exit criterion: zero `Recorder::Sync` inside a frame in the menus.

### 4.4 Shaders and startup
- Background precompile from the pipeline journal, ordered by first use in the previous session; the menu starts with whatever is ready and draws are deferred (one-frame skip) instead of blocking on a missing pipeline.
- Graphics pipeline libraries for every graphics pipeline (fast link at draw).
- Cache size: drop per-run duplicates of IR plans, compress cache files with zstd (submodule already present), garbage-collect entries unused for N sessions.
- Optional `APS5_FAST_FLOAT` when measured useful; reduce register pressure of the emulation-heavy modules (split straight-line code, fewer live temporaries).
- Exit criteria: R1 targets, cache < 10 GB.

### 4.5 Presentation and display (R3)
- Decouple the reported output mode from the host window: report the 4K profile the title needs while rendering at a user-chosen internal resolution (the title's dynamic resolution target, or an override), and scale to the window with a good filter (FSR 1 / bilinear).
- Windowed, borderless, exclusive fullscreen; VRR-aware pacing; present on the presenter thread only.

### 4.6 Reaching 144 Hz (R2)
- Stage 1: stable 60 FPS native (4.1-4.4).
- Stage 2: frame generation on the presented image (FSR 3.1 interpolation, optical flow only) for 120 FPS; 144 needs 72 rendered FPS or VRR.
- Stage 3 (research, optional): find the title's frame timestep and test a vblank/timestep patch (RPCS3 method) for native 120; reject if gameplay speed or physics change.

### 4.7 Stability
- Split very long compute submissions so no single submission exceeds ~1 s (Windows TDR is 2 s); report device-loss context with debug labels.

## 5. Plan: phases, each launchable and measured

| Phase | Content | Expected visible result |
|---|---|---|
| M0 | Benchmark harness: one script, fixed scenes (boot, menu idle, menu navigation, match load), metrics (FPS, 1% low, GPU busy/idle, PCIe MiB/frame, lock wait, startup times); baseline on `nhl27` | Comparable numbers per change |
| M1 | Quick wins: evaluate and tune `dev-next` (`SKIP_STORE_UPLOADS` and the other experiments), keep what helps, upstream-quality versions | First FPS gain, fewer write-backs |
| M2 | GPU-resident memory with lazy coherence (4.1) | Largest gain: PCIe traffic and shadow publishing collapse |
| M3 | Per-queue recording, short locks (4.2) | GPU idle time falls; FPS scales with CPU cores |
| M4 | GPU-side synchronisation (4.3) | No CPU stalls mid-frame; steady frame times |
| M5 | Startup and shaders (4.4) | First frame in seconds; smaller cache |
| M6 | Display options and presentation (4.5) | 1080p/1440p displays, fullscreen, internal resolution setting |
| M7 | 144 Hz (4.6) | 120-144 FPS presented |
| M8 | Stability and content: TDR-safe submissions, stencil-plane sampling (next stop at match loading), 4-controller local play, 2 h soak | Plays a match; sessions without resets |
| M9 | Shareable kit (R4): game-free package, setup script, compressed own-install format | Friends set up their own copies in minutes |

Order rationale: M0 first (every claim needs numbers); M1 is cheap and already coded; M2-M4 are the 24x; M5-M7 build on a fast core; M8-M9 can run in parallel once M2 lands.
