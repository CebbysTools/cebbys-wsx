# M3: dispatch work outside the global GPU mutex

## Measured (NHL 27 menu, 180 s, nhl27 build)

| Item | Value |
|---|---|
| Dispatch CPU path | ~1050 us: lock wait 499 us + device call 444 us |
| Resource builds | 72,000; stage B 45.5 s total (0.63 ms each), of which guest memory upload 31.7 s, images 14.2 s |
| GPU busy | ~20% of wall time |
| Driver threads | ~95% of samples blocked on the pipeline / GPU mutex |

Source: `Execution/src/Driver/Dispatch/Dispatch.cpp` takes `GuestMemory::GpuMutex()` before `VulkanDevice::Dispatch`, which runs `ShaderResources` stage B (`Graphics/src/ShaderResources.cpp`) under it.

## Split

1. Plan (no lock): read descriptors, resolve image and buffer identities, look up host imports, decide per region whether it binds in place, stages, or copies. Output: an immutable `DispatchPlan` with the tracker generation it was taken at.
2. Validate (lock): compare the plan's generation with `GuestMemory::TrackerGeneration()` for its ranges. Unchanged: use it. Changed: rebuild under the lock (today's path).
3. Record (lock): descriptors, barriers, copies and the dispatch into the active recorder. This is the only part that orders against other queues.

Stage A already runs before the lock (`prepare:` phases), so the plan extends it.

## Ordering rules kept

- Writes a plan depends on are covered by the generation check; a mismatch falls back, never reuses.
- Imports and staging buffers made during planning are leased and retired through the existing hold (`KeepThroughHold`).
- Recorder hazard tracking (`NoteAccess`, `NotePendingWrites`) stays in the record step.

## Tests

- Existing `libSceAgcDriver` execution tests with `ANYPS5_REQUIRE_VULKAN=1` and validation layers, before and after.
- New: two queues dispatching over overlapping buffers; a CPU write between plan and record must take the rebuild path.
- Game: bench menu and CPU match; text and scene screenshots compared with `main`.

## Expected effect

If stage B leaves the lock, the serialized part per dispatch falls from ~0.94 ms to the record step (estimate 0.1-0.2 ms, to be measured); GPU idle time should fall accordingly.
