---
description: Summarise the open technical debt of a library and propose what to close next
argument-hint: <library>
---

Read `docs/dev/debt/$ARGUMENTS.md` and `core/libs/prx/$ARGUMENTS/`.
List each entry as: section, function, what is missing, `Closes when` if given.
Count the exports that still call `NotImplemented_nid_no_patch`.
Propose up to three items that can be closed from public references without hardware, and say what each needs. Change no files.
