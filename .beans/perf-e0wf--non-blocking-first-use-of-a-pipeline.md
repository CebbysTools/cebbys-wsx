---
# perf-e0wf
title: Non-blocking first use of a pipeline
status: todo
type: task
priority: normal
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:41Z
updated_at: 2026-10-21T07:55:41Z
parent: perf-zurs
blocked_by:
    - perf-njf5
---

When a pipeline is not ready, defer the draw (skip one frame) instead of blocking; background compile ordered by first use recorded in the pipeline journal.

Acceptance: no frame waits > 50 ms on compilation after the first menu.
