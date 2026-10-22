# SPIR-V optimizer

Status: `rejected`

## Improvement summary

| Metric | Start | Now | Improvement % | Note |
|---|---|---|---|---|
| 0x1152fa6000 GPU ms per dispatch | 20.68 (stage1g) | 21.01-27.38 (opt5, opt-warm) | -24 to -2 | worse |

## Cause

Translated modules are large. `spirv-opt` could make them smaller.

## Options

| Option | Pros | Cons |
|---|---|---|
| `-DANYPS5_ENABLE_SPIRV_TOOLS=ON` | Smaller modules. | Optimizing takes hours. Runs hung. |

## Result

Reverted to OFF.

## Why

The modules are too large for the optimizer to finish in time.

## Evidence

### Original

No SPIR-V optimizer pass.

### Change

`-DANYPS5_ENABLE_SPIRV_TOOLS=ON` and `APS5_OPTIMIZE_PROGRAMS` for the heavy programs.

### Reason

Smaller modules for the heaviest programs.

### Improvement

None. The optimizer took hours and the runs did not reach a steady menu. Per-run times did not fall.

### Timings

| Bench | Setting | 0x1152fa6000 ms/run | 0x1150e42000 ms/run | Menu FPS |
|---|---|---|---|---|
| stage1g | no optimizer | 20.68 | 17.19 | 3.56 |
| opt-warm | optimizer | 27.38 | 17.44 | no FPS |
| opt5 | optimizer | 21.01 | 20.68 | no FPS |

### Reports

- [report-opt.txt](report-opt.txt) (includes the stage1g baseline lines)
