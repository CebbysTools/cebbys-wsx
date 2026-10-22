# VRAM staging

Status: `no-gain`

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
