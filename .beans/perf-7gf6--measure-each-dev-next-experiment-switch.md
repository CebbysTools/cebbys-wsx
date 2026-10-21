---
# perf-7gf6
title: Measure each dev-next experiment switch
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:36Z
updated_at: 2026-10-21T07:55:36Z
parent: perf-r6u9
blocked_by:
    - perf-tl9i
---

Switches: SKIP_STORE_UPLOADS, LARGE_CLASSES/LARGE_POOL_MIB, HTILE_FILL_KNOWN, USER_VALUE_FILL, NO_COPY_SNAPSHOT, GDS_STORES, GDS_GPU_COPY, PRESYNC_IMPORT, NO_PROBE_DRAIN, DISPATCH_MISS_ITEMS (known abort risk), SMALL_POOL_MIB. One at a time, then the best combination.

Acceptance: table of FPS, PCIe MiB/frame, stability per switch.
