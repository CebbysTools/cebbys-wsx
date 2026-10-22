@AGENTS.md

## Claude Code

- `AGENTS.md` above is the source of truth. This file only adds Claude Code specifics.
- Project commands live in `.claude/commands/`: `/precheck` before a push, `/export <library> <function>` to implement an export, `/debt <library>` to review a library's debt, `/optimization <area>/<name>` to research and record an optimization before any code change.
- Prefer the relinker-only build (`build-relinker`) unless the change touches `core/libs`, `core/shader` or `3rdparty`. Full builds and submodule checkout are slow; run them in the background and wait for the notification.
- Do not write code comments, not even temporary ones. The conventions check fails on them.
- Mark every commit you author for an upstream PR with `AI-assisted: yes` in the PR body.
- This file, `.claude/`, `FORK_PATCHES.md`, `fork-patches/`, `docs/user/optimizations/` and `docs/user/NHL 27 at 144 FPS.md` are fork-only. Never include them in a branch meant for upstream (AGENTS.md section 9).
- Any patch you make: create its own feature branch from `upstream/main`, add or update its row in `FORK_PATCHES.md` on `main`, and merge it into `nhl27` for testing.

## Optimization records

These rules apply to all performance work on NHL 27 (FPS, GPU time, memory, shaders).

### Research first

1. Do the research before you change code.
2. Write the record in `docs/user/optimizations/` before you write the patch.
3. Set the status to `researched` in the record.
4. Then make the change. Do not make a change that has no record.
5. After each measurement, update the record. Write the numbers and the bench label, and add the evidence (see Evidence).
6. Record failed and rejected options too. A failed option is a result.

### Folder structure

- Each area has a folder below `docs/user/optimizations/`, for example `memory-bus/` or `shaders/`.
- Each optimization has its own folder in its area.
- If an optimization has more than one option or variant, give each option its own subfolder.
- Use lower-case words joined by `-` for folder names (`native-f16-fma`).
- Each folder contains one `INDEX.md`.

### INDEX.md content

Each `INDEX.md` below the root has these parts, in this order:

1. A `# ` title.
2. A status line: ``Status: `<value>` ``. Use one value: `planned`, `researched`, `testing`, `applied`, `rejected` or `no-gain`.
3. `## Improvement summary`: a table that shows the start value, the current value and the change.
4. `## Cause`: the problem, with measured numbers.
5. `## Options`: each option, with its pros and cons. Use a table.
6. `## Result`: what you measured. Give the bench label, the scene and the numbers.
7. `## Why`: why the option worked or did not work.

### Improvement summary

- Every `INDEX.md` has a `## Improvement summary` table, the root included.
- A record without child folders shows its own metric: start value, current value, change.
- A record with child folders shows one row for each child, with status, metric, start, current value and change.
- The root shows all optimizations together: one row for each step, from the first measurement to now, with the FPS and the change from the start. It also shows the goal.
- Update all summaries on the path to the root after each new measurement.

### Percentages

- Use one measure for every change: the improvement %.
- For FPS, and for any value where higher is better: improvement % = (now / start - 1) x 100.
- For times, and for any value where lower is better: improvement % = (start / now - 1) x 100.
- Higher is better. A time cut to half and an FPS that doubles both give 100.
- Do not write a plus sign. Write a negative value only when the result is worse.
- Do not write reductions ("fell by 22%", "-21%"). Write the improvement % instead.
- Put the value in an `Improvement %` column, or write "improvement N%" in the text.
- Every optimization gets a row with its improvement %, not only shaders. Use "not measured" when there is no number.

### Evidence

A record without child folders and with status `testing`, `applied`, `rejected` or `no-gain` must prove its result. A record with child folders gives a summary only; its children hold the evidence. Add `## Evidence` after `## Why`, with these subsections in this order:

1. `### Original`: what the code or setting was before the change.
2. `### Change`: what you changed. Give the branch, the commit and the files.
3. `### Reason`: why you changed it. Refer to the measured cause.
4. `### Improvement`: what improved, or why nothing improved.
5. `### Timings`: a table of timings, before and after. Use the same scene and the same bench settings for each column.
6. `### Reports`: links to the report files that you used for the numbers.

Rules for the reports:

- Copy the lines that you used (bench summary, `[gputime]` lines, pipeline stats, test output) into a text file in the record folder. Name it `report-<bench label>.txt`.
- Do not copy full logs, traces or game files.
- Each number in `### Timings` must come from a linked report file.
- If a report is missing for an old result, write "report not kept" in its row.

### Links

- An `INDEX.md` links to the `INDEX.md` of each direct child folder. It must link all of them.
- An `INDEX.md` does not link to deeper folders.
- The parent `INDEX.md` gives a short summary of each child.
- The root `INDEX.md` links only to the area `INDEX.md` files.

### Check

- Run `python3 fork-tools/optimizations/check_index.py` after each change to these files.
- Do not commit when the check fails.
- Use `/optimization <area>/<name>` to start a new record.

### Writing style

- Write the records in ASD-STE100 Simplified Technical English (about 80% compliance).
- Use short sentences: at most 20 words in an instruction, at most 25 words in a description.
- Use the active voice and the present tense.
- Use one instruction in each sentence.
- Use the same word for the same thing.
- Technical names (`APS5_*`, program addresses, branch names) are allowed.
