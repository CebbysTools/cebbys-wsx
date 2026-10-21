---
# perf-3mns
title: Move dispatch and draw preparation out of the lock
status: todo
type: task
priority: normal
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:39Z
updated_at: 2026-10-21T07:55:39Z
parent: perf-wbix
blocked_by:
    - perf-tnf2
---

PrepareDispatch, stage A/B, captures and descriptor writes without the global lock; lock only for submit.

Acceptance: [draw] lock wait < 20 us, [dispatch] device call < 50 us.
