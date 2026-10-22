# VRAM staging

Status: `no-gain`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| Menu FPS | 4.24 (htileskip) | 3.36 (stagereads) | -21 | worse |

## Cause

The GPU reads guest memory over PCIe. Staging that data in VRAM could make the reads faster.

## Options

| Option | Pros | Cons |
|---|---|---|
| Stage reads up to 1 GiB (`APS5_EXPERIMENT_STAGE_READS_MIB`) | Reads come from VRAM. | Extra copies. More VRAM. |

## Result

No FPS change.

## Why

The copy into VRAM costs about as much as the PCIe reads it saves. The limit was elsewhere (CPU waits, shader time).

## Evidence

### Original

GPU reads of guest memory go over PCIe.

### Change

`APS5_EXPERIMENT_STAGE_READS_MIB=64` (branch `diag/copy-reason`, `Graphics/src/GuestBufferMemory.cpp`).

### Reason

Faster reads from VRAM.

### Improvement

None. FPS fell.

### Timings

| Bench | Setting | Menu FPS | GPU busy ms/frame |
|---|---|---|---|
| htileskip | no staging | 4.24 | 178.88 |
| stagereads | staging 64 MiB | 3.36 | 229.82 |

### Reports

- [report-stagereads.txt](report-stagereads.txt)
