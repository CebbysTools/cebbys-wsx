---
description: Research and record an NHL 27 optimization before any code change
argument-hint: <area>/<optimization>[/<variant>]
---

Follow the "Optimization records" rules in `CLAUDE.md`. Write in ASD-STE100 Simplified Technical English (about 80%).

1. Read `docs/user/optimizations/INDEX.md` and the INDEX.md files on the path to `$ARGUMENTS`. Read the plan in `docs/user/NHL 27 at 144 FPS.md`.
2. Do the research. Find the cause in the code and in the bench logs. Write the measured numbers.
3. Create `docs/user/optimizations/$ARGUMENTS/INDEX.md`, with the title, the status line (`researched`), `## Cause`, `## Options` (a table with pros and cons), `## Result` and `## Why`.
4. If there is more than one option, make one subfolder for each option, each with its own INDEX.md.
5. Add a link and a one-line summary to the INDEX.md of each parent folder, up to the root. Link only direct children.
6. Run `python3 fork-tools/optimizations/check_index.py`. Correct all problems.
7. Show the record to the user. Do not change code in this command.
