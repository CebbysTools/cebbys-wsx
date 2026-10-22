# SPIR-V optimizer

Status: `rejected`

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
