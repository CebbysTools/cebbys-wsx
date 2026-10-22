---
# perf-0ykc
title: Promote helpful experiments to default-on patches
status: completed
type: task
priority: normal
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:36Z
updated_at: 2026-10-21T15:10:00Z
parent: perf-r6u9
blocked_by:
    - perf-7gf6
---

Turn each switch that helps without breaking rendering into a clean default behaviour on its own branch (upstream-quality, tests where the area has them), tracked in FORK_PATCHES.md.

Acceptance: nhl27 gains the improvement without APS5_EXPERIMENT_* switches.

## Result
Only the loop guard proved helpful without breaking rendering; it is now default-on in `fix/shader-default-loop-guard`. `APS5_SKIP_STORE_UPLOADS` broke text (rejected); fast-float gave no gain. Nothing else to promote.
