# AGC driver performance: why NHL 27 runs at 1-2 FPS

Fork-only notes. Upstream's conventions check rejects this file; keep it out of upstream branches (AGENTS.md section 9).

Measured on 2026-10-21 with NHL 27 (PPSA34063, v01.003.001), fork branch `nhl27` (upstream `9a97ac784` plus the patches in [FORK_PATCHES.md](../FORK_PATCHES.md)), Windows 11, Intel i7-14700K, NVIDIA GeForce RTX 4070, 1920x1080 window at 120 Hz, game internal resolution 2348x1320 (dynamic, 4K profile via `ANYPS5_OUTPUT_RESOLUTION=2160p`). Scene: boot, licence and quick-settings menus.

## Symptoms

- 11-12 presents per 10 s in the menus (1.1-1.2 FPS); 17-20 per 10 s only when loops are cut by a debug guard.
- GPU frame time 397-412 ms (Nsight GPU Trace); AnyPS5 present stats: GPU busy 230-580 ms and idle 300-330 ms per presented frame.
- Windows GPU watchdog (TDR, NVIDIA event 153) resets the device after 3-9 minutes: `vkWaitForFences recorder: Vulkan result -4`.
- The upstream Game bring-up thread #4275 reports the same 1.3-2 FPS on AMD (RX 6700 XT), so the limit is not vendor-specific.

## What the measurements show

### 1. The GPU is starved: about half of every frame is idle

Nsight GPU Trace (2 frames, `Top-Level Triage`, Ada):

| Metric | Value |
|---|---|
| `gr__cycles_active` | 53% of the frame |
| `sm__throughput` | 10% of peak |
| compute warps active | 20% of peak |
| front end stalled waiting for idle (`fe__cycles_stalled_cmd_wfi`) | 5.7% |

Labelled compute dispatches (`APS5_DEBUG_LABELS`) total 42 ms of a ~400 ms GPU frame. The GPU is not busy enough to be the limit; it waits for the CPU-side driver.

### 2. One global GPU mutex serialises all recording

`[draw]` and `[dispatch]` profiles (`APS5_PROFILE_DRAW`, 10 s windows):

- Draw packets: 4,862 per 10 s, **962 us per packet waiting for the GPU mutex** (4.9 s per 10 s on the draw thread); actual draw work 12.6 us per packet.
- Direct dispatches: 2,915 per 10 s, **980 us per dispatch inside the Vulkan device call** under the mutex, 139 us prologue.
- `[lock]` lines: the presenter, queue workers and the draw committer all contend for `GuestMemory::GpuMutex`.

Every queue (graphics, each compute queue) records into one `Recorder` under one mutex, and the device call of a dispatch (descriptor build, barriers, staging, pipeline bind) happens while holding it. The console runs these queues concurrently.

### 3. Guest memory is mirrored and copied every frame

`[gputime] by class` per presented frame:

| Class | Per frame | GPU time per frame |
|---|---|---|
| `shadow-publish` | 586-600 MiB | 58-65 ms |
| `storage-writeback` | 606-620 MiB | 4.7 ms |
| `staging-in` / `staging-out` | 38 / 26 MiB | 3.7 / 3.1 ms |
| `storage-upload` | 41 MiB | 2.3 ms |

Nsight: 1.8 GB PCIe writes and 0.77 GB PCIe reads in 2 frames. Every storage image a shader writes is stored back into guest memory (system RAM) after the dispatch, and the unit shadow republishes the guest bytes the next consumer may read, even when only the GPU reads them next. On the console, guest memory and GPU memory are the same memory, so none of this traffic exists.

Experiments: `APS5_UNIT_SHADOW_MIB=4096` changes nothing (not budget churn). `APS5_NO_UNIT_SHADOW` raises presents to 13-14 per 10 s for a while, then stalls for tens of seconds (GPU idle 33.7 s in one window), so the shadow avoids stalls but costs the bandwidth.

### 4. Synchronisation points wait for the GPU on the CPU

- Indirect dispatches during loading took 79 ms each in `PrepareDispatch` (`prepare: other`), 7.27 s in one 10 s window.
- `[recipe]` and `[presync]` lines: presyncs and recorder `Sync()` calls wait for recorded batches before the CPU can read results (labels, indirect arguments, CMASK and DCC keys).
- Each draw that hits a pending GPU write to memory it reads triggers a flush hook (`SyncThrough`) that waits on the GPU.

### 5. Shader translation is large; a few shaders are register-bound

Not the main limit in the menus, but it caps occupancy:

- About 10 compute pipelines compile to **255 registers** with 1.8-2 KB of per-thread local memory (spills); the largest are 380k-690k SPIR-V words (1.1 MB of GPU code). Nsight: warp launches stalled on register allocation for 651M (compute) and 877M (pixel) cycles in 2 frames; average compute warp latency 53k cycles; top issue stall `long_scoreboard` on L1TEX.
- About 85% of those modules is semantic emulation: `Select`, `BitwiseOr`, `Bitcast` and compares around each float operation (NaN-aware min/max/med3, software f32 denormal flush, packed f16 NaN propagation).
- The slowest single program in one scene, `0x115258a000` (74x42 groups over 2348x1320, 82,610 SPIR-V words, 96 registers, no spill, 19,968 B shared memory), took ~340 ms per run. Removing the float emulation (`APS5_FAST_FLOAT`), host-memory imports (`APS5_NO_HOST_IMPORT`) or the wave64 layout (`APS5_SINGLE_LANE`) did not change it by more than 1%; a 2000-evaluation loop guard never tripped. Its time is load latency (L1TEX) inside a loop with two texture samples per iteration; the per-instruction profile is still open.

### 6. Long dispatches trip the Windows watchdog

With frames of 400-900 ms of GPU work and single dispatches of 340 ms, a burst occasionally exceeds the 2 s TDR limit and Windows resets the device. This is a consequence of points 1-5, not a separate bug.

## Requirements to reach a stable, playable frame rate

Ordered by expected gain. Each needs design work in the AGC driver (`core/libs/prx/libSceAgcDriver`) and upstream agreement; none is a local patch.

1. **Recording without one global GPU mutex.**
   - Per-queue recorders that build command buffers in parallel, with the global lock held only for submission and for cross-queue memory ordering.
   - Descriptor and resource preparation (`PrepareDispatch`, stage A/B, captures) moved fully outside the lock, and the "device call" split into a lock-free build and a short locked submit.
   - Target: draw lock wait under 20 us per packet (now 962 us), dispatch device call under 50 us (now 980 us).

2. **GPU-resident guest memory for GPU-only data.**
   - Treat surfaces and buffers that only the GPU reads after a GPU write as resident: no `storage-writeback` and no `shadow-publish` until the CPU actually reads them (write-watch or access fault on the guest pages, or an explicit CPU-visible label or wait).
   - Coalesce the remaining write-backs per frame instead of per dispatch.
   - Target: PCIe traffic under 50 MiB per frame (now ~1.2 GiB).

3. **Asynchronous CPU readback.**
   - Indirect dispatch arguments, labels and fast-clear metadata read through GPU-side paths (indirect buffers, GPU label stores, compute-side CMASK/DCC expansion) instead of `Recorder::Sync()` plus CPU reads.
   - Presyncs that wait on a timeline value without blocking the recording thread.
   - Target: no CPU wait on the GPU inside a frame except the frame pacing at present.

4. **Overlap of queues on the host GPU.**
   - Map the title's async compute queues to Vulkan compute queues with timeline-semaphore dependencies derived from the PM4 waits (`WAIT_REG_MEM`, `RELEASE_MEM`), instead of one serial stream.

5. **Smaller translated shaders.**
   - An opt-in or measured relaxation of float semantics where the title does not depend on NaN payloads or denormals: native NMin/NMax/NClamp, hardware flush-to-zero declared for all f32 operations (not only add/mul/fma), native packed f16 for sub/mad/min/max.
   - Splitting very large straight-line programs, or reducing live ranges, so NVIDIA stays under 128 registers.
   - Target: no pipeline at 255 registers or with local-memory spills in this title. Prototype: branch `feat/shader-fast-float` (no gain on its own in the menus).

6. **Watchdog safety while the above lands.**
   - Split very long compute dispatches into chunks with submission points so no single submission exceeds the Windows TDR limit.
   - Or document `TdrDelay` (registry, administrator, reboot) as a user workaround.

## Related upstream work (from the community blocker map)

Source: [anyps5-roadmap, NHL 27](https://alxcbtw.github.io/anyps5-roadmap/#/games/nhl-27) and [Game bring-up #4275](https://github.com/boykopovar/AnyPS5/discussions/4275). Checked against this fork's base `9a97ac784` on 2026-10-21.

| Upstream PR | State | Relation to this fork |
|---|---|---|
| [#4563](https://github.com/boykopovar/AnyPS5/pull/4563) keep a finished Windows thread's stack until it is joined or detached | open | Same crash as fork PR #4 (`fix/libkernel-windows-park-exited-thread-stacks`). It holds the host thread until `scePthreadJoin`/`scePthreadDetach`, which matches the console exactly, with a `guest_pthread_finished_stack` test. Prefer it upstream; fork PR #4 keeps up to 256 finished threads instead. |
| [#4508](https://github.com/boykopovar/AnyPS5/pull/4508) honor the declared flexible memory budget | merged, in base | NHL 27 declares `kernel.flexibleMemorySize` 560 MiB; without it the title ran out ~20 minutes after the title screen ([#4617](https://github.com/boykopovar/AnyPS5/pull/4617), duplicate). |
| [#3655](https://github.com/boykopovar/AnyPS5/pull/3655) one inlined BDA page-table walk per read | merged, in base | Needed to link NHL 27's 510k-word main-menu pixel shader on AMD ([#4976](https://github.com/boykopovar/AnyPS5/pull/4976), duplicate). |
| [#4931](https://github.com/boykopovar/AnyPS5/pull/4931), [#4273](https://github.com/boykopovar/AnyPS5/pull/4273), [#4544](https://github.com/boykopovar/AnyPS5/pull/4544), [#4882](https://github.com/boykopovar/AnyPS5/pull/4882), [#4893](https://github.com/boykopovar/AnyPS5/pull/4893), [#5075](https://github.com/boykopovar/AnyPS5/pull/5075), [#1233](https://github.com/boykopovar/AnyPS5/pull/1233) | merged, in base | NHL 27 imports and relinker fixes. |

Next known stop after the menus (match loading, from #4275): `AGC graphics: sampling the stencil plane of depth surface 0x… (2348x1320, vk format 130) as a 2348x1320 texture of guest format 1 (vk 9), tile mode 3` — AGC cannot yet sample the stencil plane of a depth surface as a texture.

The NHL 27 bring-up fork [poonasor/AnyPS5 `dev-next`](https://github.com/poonasor/AnyPS5/tree/dev-next) (48 commits ahead, 608 behind upstream on 2026-10-21) carries experiments in the direction of requirements 1-3 above, mostly marked fork-only or behind `APS5_EXPERIMENT_*` switches: page probes and queued labels that no longer drain the draw pipeline, GPU-written vertex inputs bound in place without a CPU wait, pending counters copied into GDS on the GPU, cache-missed dispatches committed as draw-pipeline items, data-only draw hits, frame-rate experiments, and `require a 64-wide subgroup for compute programs recompiled for 64-wide subgroups`. Start there before designing these requirements from scratch; it needs a rebase onto current upstream.

## Tooling added in this fork for the work above

| Branch | Tool |
|---|---|
| `feat/agc-debug-labels` | `APS5_DEBUG_LABELS`: Vulkan debug labels per compute dispatch (program address and group counts) for Nsight GPU Trace |
| `feat/agc-pipeline-stats-program` | `APS5_PIPELINE_STATS` names the program and SPIR-V size of each compute pipeline |
| `feat/call-trace-crashing-thread` | crash report: calls of the crashing thread; `APS5_CRASH_DUMP` pointer-path memory dumps |
| `feat/shader-fast-float` | `APS5_FAST_FLOAT` prototype of relaxed float semantics |

Nsight Graphics 2026.3.1 is installed. `C:\Users\valen\anyps5-toolchain\trace.cmd` runs a 2-frame GPU Trace (Ada, Top-Level Triage, real-time shader profiler, auto export to `ngfx-trace\`). Do not pass `--platform` to `ngfx.exe`: Qt takes it as its own platform-plugin option. GPU counters need administrator rights or the NVIDIA Control Panel setting "Allow access to the GPU performance counters to all users" (takes effect after a restart). The scheduled task `AnyPS5Trace` runs `trace.cmd` elevated without a prompt.

## Measurement rules

- Compare runs with the same environment: every `APS5_*` switch read by the shader recompiler changes the shader-cache key, so a new combination recompiles about 26,000 shaders (~5 minutes, ~40 GB). Driver switches (`APS5_PROFILE_*`, `APS5_UNIT_SHADOW_*`, `APS5_DEBUG_LABELS`) do not.
- Use `[present] N presents over 10 s`, `[gputime]` per program and per class, and the `[draw]`/`[dispatch]` phase lines, with `APS5_PROFILE_DRAW=1 APS5_PROFILE_GPU=1`.
- Run with a warm cache and the same scene; boot to the quick-settings menu takes about 60 s warm.
