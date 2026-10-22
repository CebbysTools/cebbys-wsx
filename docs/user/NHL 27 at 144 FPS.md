[00Verdict](#verdict) [01Three-stage plan](#stages) [02Achieved](#progress) [03Where it stands](#gap) [04What limits the frame](#perf) [05Routes past 60](#paths) [06Milestones](#roadmap) [07Task backlog](#tasks) [08Acceptance test](#accept) [09Risks](#risks) [10Sources](#sources)

Implementation plan · AnyPS5 · NHL 27 (PPSA34063)

# NHL 27: 30, then 60, then 144 FPS

Your fork plays a full CPU vs CPU match. The measurements in it settle the main question: frames are slow because driver work is serialized behind one GPU mutex and the CPU keeps waiting for GPU results. Copy bandwidth is not the limit. This page now follows your fork’s milestones (M0–M9) and ranks the next steps by that data.

As of 22 Oct 2026Fork [CebbysTools/cebbys-wsx](https://github.com/CebbysTools/cebbys-wsx), integration PR [#9](https://github.com/CebbysTools/cebbys-wsx/pull/9)RTX 4070, i7-14700K, Windows 11Frostbite engine, EA Vancouver

00 · Verdict

## Your data confirms the limit is serialization: one GPU mutex, and the CPU waiting on the GPU

**\~80%**of each frame the GPU sits idle in the menus

**962 µs**wait for the global GPU mutex per draw packet; the draw work itself takes 12.6 µs

**\~250**CPU↔GPU syncs per 10 s, each a GPU round trip of about 2–6 ms

**2.02 → 4.04**menu FPS from the 256 MiB host import window, the largest gain so far

- **Today:** menus run at 1–4 FPS (0.82 FPS on the 180 s baseline bench, 4.04 FPS with the import window), a match at about 1 FPS. A full CPU vs CPU match completes, and a 2-hour soak ran with no GPU reset.
- **Copies are not the limiter yet.** Turning off write-back, unit shadows, store-at-flip or GDS drains does not raise FPS. About 1.2 GiB per frame still crosses PCIe, but it only becomes the limit once the serialization is gone.
- **Stage 1, 30 FPS:** shorten the serial path under the GPU mutex and remove CPU reads of GPU results, then cut the GPU-side copies (shadow-publish alone is 51 ms per frame).
- **Stage 2, 60 FPS:** per-queue recording, GPU-side synchronisation, VRAM placement and leaner shaders.
- **Stage 3, 144 FPS:** frame generation from a locked 72 or 60, or a native unlock if the game’s timestep allows it.

**Three numbers that would sharpen the ranking**

1. The **sum of GPU mutex hold time** per 10 s, split by holder (`[lock]` lines; hold profiling is on unless `APS5_NO_HOLD_PROFILE` is set). Waits overlap across threads; hold time is the serial path that caps FPS.
2. Whether the slow programs `0x115258a000` and `0x1152fa6000` read their data through buffer device addresses (pointer reads with a page-table walk) or through typed descriptors.
3. The `attribute3` value in NHL 27’s `param.json`: bit `0x40` means a native 120 Hz mode exists.

01 · Plan

## Three stages: 30 FPS first, then console-level 60, then 144

Each stage has a frame budget. CPU work on the serial path and GPU work per frame must both fit inside it. Today a menu frame is about 250 ms of serial CPU work, and 110–165 ms of GPU work.

The GPU numbers matter from stage 1 on. Removing every CPU stall would still leave 110–165 ms of GPU work per frame, which caps the game at 6–9 FPS. Half of that GPU time is copies (shadow-publish 51 ms per frame), so the copy work your data deprioritizes today becomes the stage-1 limiter once the lock is fixed.

30 FPS

33.3 ms per frame · bare minimum · 8× from 4 FPS menus, 30× from the match

#### CPU serial path → under 25 ms

- N1 measure the mutex hold path (M3)
- N2 stage-B uploads out of the lock, as GPU copies from the 256 MiB imports (M3)
- N3 decide from recorded state: DCC keys, HTILE, pending writes, kept bytes (M2 S1–S4)

#### GPU work → under 30 ms

- Stop shadow-publish for GPU-only consumers: 51 ms per frame (perf-cpi5)
- Defer storage-image write-back to CPU reads (perf-tm9y, T12)
- N6 check the slow programs for pointer reads (44 ms per frame for 0x1152fa6000)
- Lever if short: lower internal resolution below the 2348×1320 dynamic target (M6)

#### No stalls

- N7 non-blocking first use of a pipeline (0.5–3 s stalls today)
- N8 keep TDR safety: loop guard, submissions under \~1 s

**Exit:** menus and a CPU vs CPU match average 30 FPS or more with 1% lows of 25 or more, warm cache, same bench scenes. Match loading under 2 minutes (it scales with frame time).

60 FPS

16.7 ms per frame · console parity · 2× from stage 1

#### CPU → parallel, not serial

- N5 per-queue recorders: lock wait under 20 µs per draw, device call under 50 µs per dispatch (M3)
- N4 and M4: labels and `WAIT_REG_MEM` as timeline semaphores, no CPU wait inside a frame
- Async compute on its own Vulkan queue, overlapping graphics
- Host priorities and affinity for flip, vblank and submit threads (T7)

#### GPU → under 14 ms

- PCIe under 50 MiB per frame: render targets and storage images in VRAM (perf-tajp)
- No module at 255 registers or spilling (perf-pfs4)
- Tiered specialization of the hottest pipelines (T14); SPIR-V optimizer measured
- Per-opcode cache keys so each shader experiment costs minutes, not a 40 GB rebuild (N7)

#### Feel

- Warm start under 15 s, match load under 60 s
- Present mode and pacing on a 120–144 Hz display (T11)
- 1080p and 1440p output with an internal resolution setting (M6)

**Exit:** a full match at a locked 60 with 1% lows of 55 or more. For reference, players report the console itself dropping to 48 FPS in some arenas.

144 FPS

6.94 ms per presented frame · beat the console

#### Decide the route

- T2 find NHL 27’s time source: delta time, vblank count or fixed 60 Hz step
- Check `attribute3 & 0x40` for a native 120 Hz mode (R2)
- T9 configurable guest vblank clock to test 72, 120 and 144 Hz

#### Route A: frame generation (safe)

- Render a locked 72 (13.9 ms), present 144 with interpolation on the final image (T10, perf-2pcs)
- Or 60 rendered → 120 presented, with VRR filling to the display
- Measure input latency against stage 2

#### Route B: native unlock (if timing allows)

- Vblank override plus a timestep patch, RPCS3-style; reject if game speed or physics change
- Native render at 6.94 ms needs another 2.4× GPU and CPU headroom over stage 2

**Exit:** the acceptance test in section 08: median present interval 6.94 ms, 99th percentile under 7.2 ms, game speed matches real time within 1%.

02 · Achieved

## Twelve blockers fixed or worked around; three structural problems remain open

From your list, the fork’s `FORK_PATCHES.md` and PR #9. Fork PR links point to [CebbysTools/cebbys-wsx](https://github.com/CebbysTools/cebbys-wsx/pulls).

| Area | Problem | Fix | Result | Status |
| --- | --- | --- | --- | --- |

03 · Where it stands

## The best menu rate is 4 FPS, a fifteenth of a locked 60

Bars use one scale, 0 to 144 FPS. All numbers are from your fork on the RTX 4070.

04 · What limits the frame

## Every draw and dispatch passes one lock, and about 25 times a second the CPU waits for the GPU

Menu scene, 10-second windows, from your `AGC_DRIVER_PERFORMANCE.md`, `M2` and `M3` design notes. The waits on different threads overlap, so the rows do not add up to the frame time. What caps FPS is the time the mutex is *held*, plus the round trips on the queue-0 thread.

| Measured | Per 10 s | Each | Thread time |
| --- | --- | --- | --- |
| Draw packets waiting for the mutex | 4,862 | 962 µs wait, 12.6 µs work | 4.7 s on the draw thread |
| Direct dispatches | 2,915 | \~1,050 µs: 499 µs wait + 444 µs device call under the lock | \~3.1 s |
| Resource builds (stage B, under the lock) | \~4,000 | 0.63 ms; 70% of it guest-memory upload | \~2.5 s |
| CPU↔GPU syncs (`recorded store`, `pending write`) | \~250 | 2–6 ms round trip | 0.5–1.5 s on queue 0 |
| GPU busy | largest classes: draw 25 ms, shadow-publish 51 ms, program 0x1152fa6000 44 ms per frame | 1.9 s |  |

Stage-B builds per 10 s are derived from your M3 note (72,000 builds in 180 s). Sync round-trip times are from your M2 note.

### Earlier hypotheses on this page, checked against your data

| Earlier item | What your data shows | Decision |
| --- | --- | --- |
| CPU waits for GPU | Confirmed: \~250 syncs per 10 s, \~120 ms of waits per frame on the team-versus menu. | Top priority N3, N4 |
| Storage-image write-back | Real traffic (\~180 write-backs, \~585 MiB per frame), but switching it off does not raise FPS today. | After the lock work perf-tm9y |
| Texture uploads and compares | Stage-B guest upload is 31.7 s of 180 s, done under the mutex. | High N2 |
| Vertex and index copies | Not among the measured top costs. | Low |
| Host-placed images after VRAM refusal | Device loss came from a full C: drive (shader caches), not VRAM placement. | Low |
| Shaders rebuilt during play | Pipeline creation stalls of 0.5–3 s per shader. | High N7 |
| Float emulation in shaders | `APS5_FAST_FLOAT` (#8): no gain on the slow program (3,711 vs 3,737 ms per 10 s). | Drop for now |
| Wave64 on 32-lane NVIDIA | `APS5_SINGLE_LANE`: under 1% change. | Drop for now |
| Pointer (BDA) access instead of descriptors | Slow program is bound by L1TEX load latency (`long_scoreboard`) at 96 registers with no spills. A software page-table walk before each load would look exactly like this. | Test N6 |
| SPIR-V optimizer, tiered specialization | Unmeasured; each try rebuilds \~26,000 shaders (\~5 min, \~40 GB). | After N7 cache keys |

### Next steps, ranked (stage 1 first)

05 · Routes past 60

## Four routes past 60 FPS; which one works depends on how NHL 27 steps its simulation

| Route | How | Works if | Pros | Cons | Host cost at 144 | Fit |
| --- | --- | --- | --- | --- | --- | --- |
| **R1 Faster guest vblank** | Run the emulated vblank at 144 Hz (or 288 ticks with the existing half-rate logic) so flips with flip rate 0 land every 6.94 ms. | Game uses measured delta time for simulation and animation. | Real 144 rendered frames; small code change. | If gameplay is tied to vblank count, the match runs 2.4× too fast. | 144 full frames | Test first |
| **R2 Native 120 Hz mode + R1** | Let the title select output mode 15, then raise that clock from 119.88 to 144 Hz. | `attribute3 & 0x40` is set and the game has a 120 Hz path. | Game logic already expects frames shorter than 16.7 ms. | Sports titles often ship without 120 Hz modes; 144 is still above what the game was tested at. | 144 full frames | Best if available |
| **R3 Frame generation** | Keep the game at a locked 72, present one interpolated frame between each pair using the game’s depth and velocity buffers. | Game runs at 72 without speed change, or at 60 with 60→120 instead. | Game timing untouched; only half the frames are rendered. | About one frame of added input latency; artefacts on fast puck motion and UI. | 72 full + 72 interpolated | Safest |
| **R4 Binary patch of the frame cap** | Find the frame-time constant or flip-rate argument and change it with a `relinker-patches.toml` entry. | The cap is one constant and simulation uses a variable step. | Precise; survives AnyPS5 updates. | Per content version; needs disassembly of your own dump. | 144 full frames | Pairs with R1 |

At 60 Hz the guest vblank loop in `VideoOutDriver::vblankLoop` ticks at 119.88 Hz and drops odd ticks. `processFlip` waits for `lastFlipVblank + flipRate + 1`, so the guest can never present faster than its vblank clock, whatever the host GPU can do.

06 · Roadmap

## Your milestones M0–M9, with status as of 22 Oct 2026

| Milestone | Stage | Content | Exit measure | Status |
| --- | --- | --- | --- | --- |
| **M0** Harness | Setup | `fork-tools/bench`: fixed scenes, FPS, GPU busy and idle, PCIe MiB per frame, lock waits; Nsight trace recipe | Comparable numbers per change | Done |
| **M1** Quick wins | 1 | Import window 256 MiB, GDS copies on the GPU, storage cache priority, loop guard; dev-next experiments measured | First FPS gain | In progress 2 → 4 FPS menus |
| **M2** Decide from recorded state | 1 | S1 DCC keys, S2 HTILE, S3 `FlushPending` via resident image, S4 kept bytes; then GPU-resident storage and shadow data | Syncs per 10 s → \~0; PCIe \< 50 MiB per frame | Designed |
| **M3** Per-queue recording | 1–2 | Plan without the lock, validate by tracker generation, record under a short lock; per-queue recorders | Lock wait \< 20 µs per draw; device call \< 50 µs per dispatch | Designed |
| **M4** GPU-side sync | 2 | Labels and `WAIT_REG_MEM` as timeline semaphores; indirect args and metadata on the GPU | No CPU wait inside a frame | Open |
| **M5** Startup and shaders | 1–2 | Non-blocking first use, per-opcode cache keys, smaller cache, register pressure | Warm start \< 15 s; no compile wait > 50 ms; cache \< 10 GB | Open |
| **M6** Display | 2 | Internal resolution independent of the reported 4K mode; window modes | 1080p and 1440p displays | Open |
| **M7** 120–144 Hz | 3 | Frame generation on the presented image (T10); optional timestep patch with vblank override (T2, T9) | Section 08 acceptance | Open |
| **M8** Stability | All | TDR-safe submissions, stencil-plane sampling, local multiplayer, 2-hour soak | No resets | Soak passed |
| **M9** Game-free kit | After 2 | Setup from each player’s own dump; no game files shared | Kit under 500 MB | Open |

07 · Task backlog

## Fourteen tasks from the first draft, now marked against your progress

Tasks already covered by your fork are marked. Code is a sketch against `a6dcea9`; adapt names to current `main`. Per project convention, unsupported values throw instead of being ignored.

08 · Acceptance

## “Stable 144” passes when 99% of frames finish within 7.2 ms over a full 20-minute period

| Check | Threshold | How measured |
| --- | --- | --- |
| Median present interval | 6.94 ms ± 0.1 | T1 flip statistics, warm caches, exhibition game, one 20-minute period |
| 99th percentile interval | ≤ 7.2 ms | Same run |
| Hitches | ≤ 0.1% of frames over 13.9 ms | Same run, excluding the first 30 s after a load |
| Game speed | Period clock and wall clock agree within 1% | Stopwatch against the in-game 20:00 period clock at default period length |
| Stability | 3 of 3 full games with no abort | Cold start, warm shader cache |
| Latency (R3 only) | Record and compare | Input-to-photon with and without frame generation |

09 · Risks

## Game-speed coupling is the risk most likely to rule out native 144

| Risk | Likelihood | Effect | Mitigation |
| --- | --- | --- | --- |
| Simulation tied to vblank count or a fixed 60 Hz step | High | R1 runs the match too fast | Measure in T2; fall back to R3 (your M7 order) |
| Per-frame translation cost stays above 6.94 ms | High | No native 144 even with an unlocked clock | R3 halves the frames rendered |
| Frostbite thread pool sized for 8 console cores | Medium | Uneven CPU load, hitches | T7 affinity mapping; pick a CPU with 8+ fast cores |
| Memory pressure (23 GiB working set seen on NHL 26) | Medium | Paging hitches | T8 budgets; 64 GB RAM |
| Online-only features | Medium | EA and PSN modes unavailable | Test offline exhibition and franchise modes only |
| Content updates move patched addresses | Low | R4 patch stops applying | Patch file pins `expected` bytes, so conversion fails loudly |

Run only a copy of NHL 27 you own and dumped yourself. This plan does not cover keys, decryption or online services.

10 · Sources

## Sources opened for this plan

1. [CebbysTools/cebbys-wsx](https://github.com/CebbysTools/cebbys-wsx): `FORK_PATCHES.md`, `fork-notes/AGC_DRIVER_PERFORMANCE.md`, `M2_GPU_RESIDENT_MEMORY_DESIGN.md`, `M3_DISPATCH_LOCK_DESIGN.md`, `MILESTONE_144FPS_RESEARCH.md`, `.beans` tasks, and [integration PR #9](https://github.com/CebbysTools/cebbys-wsx/pull/9) (read 22 Oct 2026).
2. AnyPS5 source at `a6dcea9`: `libSceVideoOut/src/VideoOutDriver.cpp`, `Output.cpp`, `libSceAgcDriver/Execution/include/PresentMode.hpp`, `docs/dev/ARCHITECTURE.md`, `docs/dev/ENVIRONMENT.md`, `docs/user/USAGE.md`, `docs/dev/debt/libSceVideoOut.md`.
3. [AnyPS5 issue #7700: NHL 26 Heartbeat thread crash](https://github.com/boykopovar/AnyPS5/issues/7700).
4. [AnyPS5 discussion #7304: NHL 26 bring-up](https://github.com/boykopovar/AnyPS5/discussions/7304).
5. [anyps5.org compatibility list](https://anyps5.org/compatibility/) (community, unofficial): NHL 27 entry.
6. [Wikipedia: NHL 27](https://en.wikipedia.org/wiki/NHL_27).
7. [EA Forums: NHL 27 True Broadcast Legacy frame rate](https://forums.ea.com/idea/nhl-27-bug-reports-en/true-broadcast-legacy-frame-rate/13702101/comments/13721373).
8. [AMD FidelityFX SDK](https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK) and [GamingOnLinux: FSR 3 open source](https://gamingonlinux.com/2023/12/amd-fidelityfx-super-resolution-3-fsr3-is-now-open-source).
9. [Vulkan: VK_EXT_map_memory_placed proposal](https://docs.vulkan.org/features/latest/features/proposals/VK_EXT_map_memory_placed.html) and [Phoronix: Wine uses it to remove a Vulkan penalty](https://www.phoronix.com/news/Wine-Vulkan-Map-Memory-Placed) (Linux drivers).
10. AnyPS5 docs for memory traffic and shaders: `docs/dev/debt/libSceAgcDriver.md` (storage-image write-back, storage tables, host placement), `docs/dev/debt/shader.md` (registration modules, SPIR-V optimization, spanned wave64, load guards), `docs/dev/BUILD.md`, `docs/dev/ENVIRONMENT.md` (profilers) at commit `d6eafa5`.