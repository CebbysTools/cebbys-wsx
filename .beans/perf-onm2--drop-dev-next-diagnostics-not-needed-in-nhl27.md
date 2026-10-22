---
# perf-onm2
title: Drop dev-next diagnostics not needed in nhl27
status: completed
type: task
priority: low
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:36Z
updated_at: 2026-10-21T15:10:00Z
parent: perf-r6u9
blocked_by:
    - perf-7gf6
---

Keep diagnostic-only commits (dump/trace/watch switches) out of nhl27 unless used by the harness.

## Result
`nhl27` does not merge dev-next; dev-next commits live only on `exp/dev-next-on-nhl27`. Nothing to drop.
