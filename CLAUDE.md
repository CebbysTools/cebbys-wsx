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
5. After each measurement, update the record. Write the numbers and the bench label.
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
3. `## Cause`: the problem, with measured numbers.
4. `## Options`: each option, with its pros and cons. Use a table.
5. `## Result`: what you measured. Give the bench label, the scene and the numbers.
6. `## Why`: why the option worked or did not work.

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
