---
# perf-7gf6
title: Measure each dev-next experiment switch
status: in-progress
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:36Z
updated_at: 2026-10-21T10:48:47Z
parent: perf-r6u9
blocked_by:
    - perf-tl9i
---

Switches: SKIP_STORE_UPLOADS, LARGE_CLASSES/LARGE_POOL_MIB, HTILE_FILL_KNOWN, USER_VALUE_FILL, NO_COPY_SNAPSHOT, GDS_STORES, GDS_GPU_COPY, PRESYNC_IMPORT, NO_PROBE_DRAIN, DISPATCH_MISS_ITEMS (known abort risk), SMALL_POOL_MIB. One at a time, then the best combination.

Acceptance: table of FPS, PCIe MiB/frame, stability per switch.



## Results (2026-10-21)
- dev-next default (with default loop guard): 1.9 FPS, no gain over nhl27; GPU resets in 2 of 3 runs; first interactive 12 s vs 27-28 s.
- SKIP_STORE_UPLOADS on dev-next: 2.8 FPS and shadow-publish 141 MiB/frame in one run; 1.54 FPS with stalls in the other.
- SKIP_STORE_UPLOADS ported to nhl27 (branch perf/agc-skip-store-reuploads, opt-in APS5_SKIP_STORE_UPLOADS): **rejected** — text glyphs go missing (user screenshot: 'PLA NO...', 'S CTSD S', 'K. MILL R' on the VS screen). The re-uploads it skips carry data the title needs (glyph cache written through aliasing memory). Proper fix belongs to M2 (GPU-to-GPU hand-over between aliasing images).
- Harness issue: three timed presses do not land on one screen (licence/VS screen/'SIGN IN REQUIRED' dialog depending on boot timing and the EA online check), so FPS between runs is only comparable with the screen identified. The 4.9 FPS seen on the sign-in dialog is a lighter scene, not a gain.
- New failures seen: 'read-write alias of shared guest memory ... a resident run of direct memory extends outside the range' (without the switch), and a GPU reset with the default loop guard (with the switch).
