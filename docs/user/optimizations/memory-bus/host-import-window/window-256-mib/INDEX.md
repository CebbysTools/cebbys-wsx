# 256 MiB import window

Status: `applied`

## Cause

All measured render targets fit in a 256 MiB window.

## Options

`APS5_HOST_IMPORT_WINDOW_MIB=256`, now the default in the fork. It needs `fix/agc-import-alias-resident-run-outside`, because a wide window can cut a resident direct-memory run.

## Result

Menu went from 2.0 to 4.04 FPS (bench `win256`).

## Why

The CPU copies of large render targets stopped.
