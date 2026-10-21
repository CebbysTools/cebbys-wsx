---
# perf-32ss
title: Map everything GpuMutex protects
status: todo
type: task
priority: high
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:38Z
updated_at: 2026-10-21T07:55:38Z
parent: perf-wbix
---

List the state guarded by GuestMemory::GpuMutex (recorder, resource caches, guest memory tracking, imports) and which of it is per-queue vs global.

Acceptance: document with call sites and contention numbers from the harness.
