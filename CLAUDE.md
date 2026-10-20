@AGENTS.md

## Claude Code

- `AGENTS.md` above is the source of truth. This file only adds Claude Code specifics.
- Project commands live in `.claude/commands/`: `/precheck` before a push, `/export <library> <function>` to implement an export, `/debt <library>` to review a library's debt.
- Prefer the relinker-only build (`build-relinker`) unless the change touches `core/libs`, `core/shader` or `3rdparty`. Full builds and submodule checkout are slow; run them in the background and wait for the notification.
- Do not write code comments, not even temporary ones. The conventions check fails on them.
- Mark every commit you author for an upstream PR with `AI-assisted: yes` in the PR body.
- This file and `.claude/` are fork-only. Never include them in a branch meant for upstream (AGENTS.md section 9).
