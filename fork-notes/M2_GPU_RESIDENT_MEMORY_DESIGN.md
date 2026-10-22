# M2: GPU-resident memory model

## Problem (measured, NHL 27 team-versus menu, RTX 4070)

- Frame 222 ms; queue worker 0x0 busy 95 %; GPU executes a small part of the frame.
- ~120 ms per frame are CPU waits for the GPU: the driver reads guest memory that recorded GPU work will write, to decide how to build the next resource.
- Sites (sync time per 10 s window share): `StorageTexture::FlushPending` (pending-write), `currentDccKeys` / `WaitForKeyWriters` (DCC keys), `FlushForAccess` (hook), `storeBackClearedHtile` (HTILE), `BoundKeptBytes` / `WaitSerial`.
- Removing any one site moves the wait to the next: the build path depends on GPU results several dozen times per frame.

PS5: CPU and GPU share one memory; reading GPU results costs nothing beyond the GPU finishing. PC: each read is a GPU round trip (submit, execute, fence, wake) of ~2-6 ms under the queue-0 path.

## Target model

1. Device state is authoritative for GPU-produced data. Guest memory is updated only when the title's CPU code or a CPU-only consumer reads it (lazy coherence, already partly present as write-back on access).
2. The driver decides from recorded state, not from guest bytes:
   - DCC keys: every GPU key writer (draw into a DCC target, key store, fill, storage write-back, title compute that writes key memory) records the resulting key state per range in the recorder at record time. `currentDccKeys` answers from that state; a read is needed only for ranges whose last writer was the CPU.
   - HTILE: same, per depth surface (`storeBackClearedHtile` uses recorded fill/clear state; GPU depth writes mark "not cleared").
   - Storage results: a texture or buffer built over a range with pending storage results binds or copies from the resident image on the GPU (FindPending path) instead of flushing to guest memory and reading it.
3. A CPU wait remains only where the title's CPU reads (hook) or the driver must hand bytes to the CPU (scan-out fallback, CPU-only consumers).

## Stages (each measured in a 2-minute menu run; screenshots compared)

| Stage | Change | Exit measure |
|---|---|---|
| S1 | Recorder keeps a per-range key-state map written by every GPU key writer; `currentDccKeys`/`WaitForKeyWriters` consult it | DCC key syncs per 10 s -> ~0, text and scene intact |
| S2 | HTILE state recorded per depth surface; `storeBackClearedHtile` reads only after CPU writes | HTILE syncs -> 0 |
| S3 | `FlushPending` callers that feed GPU consumers take the resident-image path; flush only for CPU readers | pending-write syncs in builds -> ~0 |
| S4 | `BoundKeptBytes`: budget sized from memory, release by timeline value without blocking the recorder | WaitSerial/kept syncs -> 0 |
| S5 | Re-measure critical path; next limiter expected: per-draw/dispatch recording cost (M3) | queue-0 busy without waits |

## Risks

- Wrong recorded state means wrong texels: every stage keeps the old read path behind a switch and is compared by screenshot.
- Recorder state must be updated under the GPU mutex at record time; completion-time updates stay as today.
