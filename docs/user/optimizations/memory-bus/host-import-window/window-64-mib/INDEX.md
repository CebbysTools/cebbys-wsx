# 64 MiB import window

Status: `rejected`

## Cause

A larger window lets more allocations import in place.

## Options

`APS5_HOST_IMPORT_WINDOW_MIB=64`.

## Result

Better than 8 MiB, worse than 256 MiB (bench `win64`).

## Why

Some render targets are still larger than the window.
