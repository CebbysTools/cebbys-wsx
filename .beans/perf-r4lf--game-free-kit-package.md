---
# perf-r4lf
title: Game-free kit package
status: completed
type: task
priority: normal
tags:
    - nhl27-perf
created_at: 2026-10-21T07:55:44Z
updated_at: 2026-10-21T07:55:44Z
parent: perf-gzrj
---

Zip with built libs (+ runtime DLLs), relinker, unwrap/convert script, launcher, patch files, README; built by a script from a tagged nhl27 commit.

Acceptance: < 500 MB; contains no game data (script checks).

## Result 2026-10-21
`fork-tools/kit/make_kit.py` builds `NHL27-AnyPS5-kit-<commit>.zip` (94 MiB from nhl27 2791b15cc): libs, relinker, unwrap_self.py, setup.ps1, launcher, README, BUILD.txt, LICENSE. The script refuses game data (.bin/.elf/.self/.guest.prx/app0) and kits over 500 MiB. Tested: extracted to a fresh folder, setup.ps1 against the dump, game reached the title screen.
