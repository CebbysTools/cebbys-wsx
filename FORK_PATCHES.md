# Fork patches

Fork-only file. Every change this fork makes to AnyPS5 is listed here, one row per feature branch.
Upstream's conventions check rejects this file; never include it in a branch meant for upstream (AGENTS.md section 9).

## Rules

- One patch = one feature branch from `upstream/main` (`feat/...`, `fix/...`, `perf/...`), Conventional Commits, upstream rules (CONTRIBUTING.md).
- Add the row when the branch is created; update **Status** and **Evidence** as it moves.
- `nhl27` is the integration branch: `main` plus every branch below with status `testing` or later, merged for game runs. Rebuild it after any patch branch changes:
  `git checkout nhl27 && git reset --hard main && git merge --no-edit <branches...>`
- Game-side byte patches (relinker `--patches` TOML files) are tracked in the second table; their files live in `fork-patches/`.
- Status values: `testing` (in `nhl27`), `ready` (conventions check and tests pass), `upstream-pr #N`, `merged`, `dropped` (say why).

## AnyPS5 patches

| Branch | Area | What it changes | New settings | Evidence | Status |
|---|---|---|---|---|---|
| `feat/call-trace-crashing-thread` | libc (crash report) | Windows crash report lists the traced calls of the crashing thread (from the 65536-call ring), not only the global last 64. `APS5_CRASH_DUMP` dumps memory reached from the faulting registers through pointer paths (`reg+off@-off:len`, `@` loads a pointer). | `APS5_CRASH_DUMP` | NHL 27: showed the crashing `Job` thread made no failing system call before the preset crash; dumps proved the PS5_BASE preset list is empty. | testing |
| `feat/videoout-output-resolution` | libSceVideoOut | `ANYPS5_OUTPUT_RESOLUTION=2160p\|1080p` sets the resolution `sceVideoOutGetOutputStatus` reports, as the console's video output setting. Default unchanged (from registered buffers, so 1080p before any buffer). Debt entry added. | `ANYPS5_OUTPUT_RESOLUTION` | NHL 27 (PPSA34063) ships quality presets only for PS5_4K/TRINITY_4K; with `2160p` it passes the `eboot+0x79289c6` null read at boot. Same root cause as upstream discussion #4275 (`ANYPS5_OUTPUT_4K` on a contributor branch, not in main). | testing |
| `feat/agc-cmask-array-slices` | libSceAgcDriver | Single-sample CMASK fast clears of one slice of a 2D target, and of every slice of a single-mip array view (e.g. cube maps), instead of throwing. Per-slice CMASK stride = one slice's CMASK block run (GFX10 layout, unmeasured; debt entry). Error now names the view. | none | NHL 27: passes `CMASK fast clears of a 3D or array color target` (slice 1 of 512x512, then slices 0-5 of 512x512). | testing |

## Game patches (relinker `--patches`)

| File | Title | What it patches | Status |
|---|---|---|---|
| `fork-patches/PPSA34063-force-ps5-4k.toml` | NHL 27 01.003.001 | `eboot.elf` va 0x1285b56 `sete r15b` -> `mov r15b,1` (platform probe reports 4K). | dropped: a second probe at 0x1285a60 runs first and fills the cache, so it has no effect; replaced by `ANYPS5_OUTPUT_RESOLUTION=2160p`. Kept for reference. |

## Running NHL 27 with the fork

Environment: `ANYPS5_OUTPUT_RESOLUTION=2160p` (required). Build `nhl27`, copy `build/core/libs/libs/*.prx` and the WinLibs runtime DLLs to `libs/`, relink `eboot.elf` with the same build's relinker.
