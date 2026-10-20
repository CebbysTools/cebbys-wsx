---
description: Implement or fix a system library export the AnyPS5 way
argument-hint: <library> <function>
---

Implement `$ARGUMENTS` following AGENTS.md section 6, "Implement or fix an export".

- Read `core/libs/prx/<library>/`, its `CMakeLists.txt`, `docs/dev/debt/<library>.md` and the tests that cover it.
- Collect the signature, structure layouts and error codes from public references. State each source. If they do not settle a case, that case throws.
- Implement the general behaviour for every input. No title-specific checks, no fake success, no comments.
- Add or extend a `core/libs/tests/Guest*.cpp` test, registered with `add_test`, finishing well under 30 s.
- Update the debt file: remove or cut the closed entry.
- Build with `cmake --build build --target libs` plus the test target, run `ctest --test-dir build -R <pattern> --output-on-failure`, then `/precheck`.
- Finish with a draft PR body from `.github/pull_request_template.md` with every line kept and `AI-assisted: yes`. Do not push.
