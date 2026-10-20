---
description: Run the upstream checks a branch must pass before it is pushed or opened as a PR
---

Check the current branch against the rules in AGENTS.md.

1. Find the base: `upstream/main` if that remote exists, otherwise `origin/main`. Run `git fetch` for it.
2. `python3 tools/check_main_sync.py` and report whether the branch is behind.
3. `git diff --name-only <base>...HEAD`. If it lists `CLAUDE.md` or anything under `.claude/`, stop and report: the branch is not fit for upstream.
4. `python3 tools/check_conventions.py --base <base>` and show every failure with the rule it cites.
5. `python3 tools/pr_overlap.py --branch $(git branch --show-current)` and list overlapping PRs.
6. Say which build covers the change (relinker-only or full) and which ctest pattern to run. Do not run a full build unless asked.

Report results plainly. Do not fix anything unless $ARGUMENTS says `fix`.
