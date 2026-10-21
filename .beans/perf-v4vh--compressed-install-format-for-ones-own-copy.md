---
# perf-v4vh
title: Compressed install format for one's own copy
status: completed
type: task
priority: low
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:45Z
updated_at: 2026-10-21T07:55:45Z
parent: perf-gzrj
---

Investigate reading app0 from a compressed archive (ZArchive/zstd submodules are present) or filesystem-level compression; measure load-time cost.

Acceptance: measured size reduction and load time; recommendation.

## Result 2026-10-21
- Dump: 204.7 GiB, 197 `cas` files of up to 1 GiB. Samples: 32% zero bytes; zlib-6 ratio 0.19-0.21.
- NTFS `compact /exe:lzx` on a 1 GiB `cas` copy: 128 MB on disk (8.4:1), 12 s to compress; cached reads 7.0 GB/s compressed vs 6.2 GB/s plain (cold reads not measured).
- Recommendation: transparent NTFS LZX on `Data\` (no code change, reversible with `compact /u /exe`), offered as `setup.ps1 -Compress`. Estimated 30-45 GB on disk. A ZArchive reader is not worth it: match load is frame-bound, not I/O-bound (perf-n0ig).
- Not measured: full-dump size and load time with the whole Data folder compressed.
