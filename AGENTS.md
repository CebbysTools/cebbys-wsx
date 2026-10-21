# AGENTS.md

Instructions for coding agents working on this fork of [boykopovar/AnyPS5](https://github.com/boykopovar/AnyPS5).
The upstream rules live in [CONTRIBUTING.md](CONTRIBUTING.md) and [CONVENTIONS](docs/dev/CONVENTIONS.md).
This file restates them for agents, adds the context an agent needs to work alone, and lists the mistakes agents make most.
When this file and an upstream document disagree, the upstream document wins; fix this file.

## 1. What the project is

AnyPS5 converts PS5 executables into native x86-64 programs for Linux and Windows (Mach-O output exists for the relinker only).
It is **not an emulator**. There is no interpreter, no JIT, no separate runtime process.

1. The **relinker** (`core/relinker`) rewrites the PS5 ELF (`eboot.elf`) and its bundled modules (`sce_module/*.prx`) into a host ELF or PE. It reads imports by NID, checks syscalls, drops unused NIDs, builds a SysV dynamic section and, with `--to-intel`, lowers AMD-only instructions.
2. The **system libraries** (`core/libs/prx/<library>`) are native reimplementations of PS5 system libraries (`libkernel`, `libc`, `libSceAgc`, `libScePad`, ...). Each builds as a shared library. After the build, `nid_patcher` (`core/libs/nid`) renames every export to its NID, so the host OS loader binds the game's imports directly.
3. The **shader recompiler** (`core/shader/recompiler`) decodes RDNA shader binaries and emits SPIR-V for the Vulkan backend of the AGC driver (`core/libs/prx/libSceAgcDriver`).
4. The **web converter** (`demo/web`, `core/relinker/wasm`) runs the relinker in the browser through Emscripten. Files never leave the user's device.

Scope:

- In scope: system libraries that reach the kernel or the hardware; the relinker; the GPU path (AGC, shader recompiler, VideoOut); input, audio, saves, networking stubs needed to boot titles; tooling for tests, tracing and progress.
- Out of scope: engine or middleware modules that titles ship themselves (Cohtml, FMOD, GOG Galaxy) and SDK libraries that only wrap other system libraries. The relinker converts and loads the title's own copy. Do not reimplement them.
- Never added: copyrighted firmware, keys, proprietary libraries, game files, decryption. The project only consumes legally dumped, already decrypted ELFs.

Progress is measured as the share of *known* functions (declared in `core/libs/prx`) that are implemented, see [PROGRESS](docs/dev/PROGRESS.md) and `tools/progress.py`.

## 2. Repository map

| Path | Holds |
|---|---|
| `core/relinker/` | The converter. C++20 standard library only, no third-party code. |
| `core/relinker/cli/` | Argument parsing and the command-line front end. |
| `core/relinker/relinker/src/{analysis,guest,output,parsing,patching,pipeline}` | `RelinkerPipeline`, `GuestModuleBuilder`, game patches (`GamePatch.cpp`), output manifests. |
| `core/relinker/elfpatcher/` | `LinuxElfPatcher`, `WindowsPePatcher`, ELF constants. |
| `core/relinker/codegen/` | `--to-intel` instruction lowering and trampolines. |
| `core/relinker/io/`, `core/relinker/domain/` | File and path I/O, shared types. |
| `core/relinker/wasm/` | Emscripten bindings for the web converter. |
| `core/libs/prx/<library>/` | One system library: `Export.cpp` or subfolders, its own `CMakeLists.txt`. About 350 libraries. |
| `core/libs/prx/libc/include/` | Shared helpers every library uses: `General.hpp` (`NotImplemented_nid_no_patch`), `general/VabiMacros.hpp` (`APS5_VABI`), `general/ExportMacros.hpp` (`APS5_EXPORT`). |
| `core/libs/prx/libkernel/` | Kernel: `Pthread`, `Equeue`, `File`, `DirectMemory`, `Socket`, `Time`, ... |
| `core/libs/prx/libSceAgcDriver/` | The Vulkan GPU driver: `Graphics`, `Submit`, `Resource`, `State`, `Execution`. |
| `core/libs/nid/` | `nid_patcher`: renames exports to NIDs after the link. |
| `core/libs/allocator/` | Guest memory arena and Windows allocator. |
| `core/libs/tests/` | Guest-side tests of the libraries (`Guest*.cpp`), one executable per area. |
| `core/libs/SceTypes.hpp`, `SceShaders.hpp`, `HitLog.hpp` | Types shared between libraries. |
| `core/shader/recompiler/` | `RdnaDecoder`, `IntermediateRepresentation`, `ControlFlow`, `Optimization`, `Translation`, `SpirvBackend`, shader disk cache. |
| `core/Decoder/` | PNG and JPEG decoders used by the libraries. |
| `tools/` | Python 3 tooling (conventions check, PR overlap, stub generation, NID names, tracing, progress, release packaging). Tests in `tools/tests/`. |
| `tools/hw-oracle/` | Runs shader instruction snippets on a real GPU to measure semantics, see [HW_ORACLE](docs/dev/HW_ORACLE.md). |
| `demo/web/` | Web converter frontend (plain ES modules) and its `node --test` tests. |
| `cmake/` | Tracy, ZArchive, system dependency resolution, Windows test helpers. |
| `3rdparty/` | Git submodules only (SDL2, Vulkan-Headers, SPIRV-*, glslang, VMA, LibAtrac9, ffmpeg-core, freetype, stb, tracy, mimalloc, libjpeg-turbo, libusb, mbedtls, zstd, ZArchive). |
| `docs/dev/` | Developer docs. `TechnicalDebt.md` is the index; `debt/<name>.md` holds one file per library or component. |
| `docs/user/` | `USAGE.md`, `INPUT_MAPPING.md`. |
| `.github/` | CI workflows, PR template, issue and discussion forms. |

Read before you change an area:

| Area | Read first |
|---|---|
| anything | [ARCHITECTURE](docs/dev/ARCHITECTURE.md), [CONTRIBUTING](CONTRIBUTING.md) |
| building, flags, test helpers | [BUILD](docs/dev/BUILD.md) |
| any `APS5_*` / `ANYPS5_*` variable | [ENVIRONMENT](docs/dev/ENVIRONMENT.md) |
| running a converted title | [GAME_TESTING](docs/dev/GAME_TESTING.md), [USAGE](docs/user/USAGE.md) |
| performance, traces | [TRACING](docs/dev/TRACING.md), BUILD "Performance trace" |
| shader instruction semantics | [HW_ORACLE](docs/dev/HW_ORACLE.md), `tools/rdna_isa.txt` |
| a library | its `docs/dev/debt/<library>.md`, if present |

## 3. Hard rules

These are enforced by `tools/check_conventions.py` in CI or by reviewers. A pull request that breaks one is rejected.

### Behaviour

- Every function either does exactly what the console does or throws. Unsupported or unexpected states throw `std::runtime_error`; the process prints `what()` and ends.
- An export you cannot implement calls `NotImplemented_nid_no_patch(__func__);`. Never return a made-up success, a zero, or `SCE_OK` to "get further".
- Implement the general behaviour for every input. Never special-case a value, ID, path or title seen in one trace. If the general behaviour is unknown, throw and record the gap in `docs/dev/debt/<library>.md`.
- A silent stub is allowed only when it unblocks a title **and** affects only the UI. List it under `### Silent stubs` in the library's debt file.
- A missing import fails at startup with a clear error. Do not add fallbacks that keep running.
- Do not add tests that only check that a symbol is exported.
- Shader instruction semantics name their source in the PR: measured on hardware (GPU and what was checked) or an exact reference (ISA section, LLVM, ACO or Mesa file). Cases the source does not settle throw. Behaviour not verified on hardware goes in technical debt.

### Code

- **No comments in code.** The only allowed comments are `#endif` ends, namespace ends, and technical-debt markers that a human adds together with a change to `docs/dev/TechnicalDebt.md` or `docs/dev/debt/`. This applies to C++, CMake and Python. Do not "explain" code with comments; name things instead.
- Prefer standard C++ over extensions (`__attribute__`, builtins) when standard C++ is enough. Existing macros such as `APS5_VABI` already wrap the required ones.
- Helper symbols in a library that must not become NIDs end in `_nid_no_patch` or `_nid_no_patch_cut`.
- The relinker uses only the C++20 standard library.
- Only UTF-8 text files. No BOM. No binaries, no images (images for docs go in the [gist](https://gist.github.com/boykopovar/0e53f2e1426f29ecd41e3b51540b8a90) comments).
- Every `APS5_*` or `ANYPS5_*` name you start reading has a row in `docs/dev/ENVIRONMENT.md`; a name you stop reading loses its row.

### Files

- New third-party code is a submodule: `git submodule add <url> 3rdparty/<name>`, built from source with CMake. Never `find_package` it, never copy sources in. The only system resolution is `ANYPS5_USE_SYSTEM_DEPS=ON` in `cmake/SystemDeps.cmake`.
- Do not add notes, reports, logs, investigation `.md` files or agent files to the repository. They go in the pull request. Markdown is allowed only in `README.md`, `CONTRIBUTING.md`, `.github/`, `docs/dev/` and `docs/user/`.
- **Only the root `AGENTS.md` is allowed as an agent file upstream.** `CLAUDE.md` and `.claude/*.md` in this fork fail the upstream check (see section 9).
- Known gaps go in `docs/dev/debt/<name>.md`, named after the first `core/` path the entry links: `<library>` for `core/libs/prx/<library>/...`, otherwise `<component>` for `core/<component>/...`. Use the same `###` sections as the index (`Silent stubs`, `Unknown function info`, `Functional`, ...). Entries that link neither stay in `docs/dev/TechnicalDebt.md`. An entry is at most 1000 characters.

### Git and pull requests

- Commit subjects and PR titles are [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/): `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`, optional `(scope)`, then `: ` and text. Scope is the area: `fix(libkernel): ...`, `feat(agc): ...`, `fix(relinker): ...`, `perf(gpu): ...`. Write the subject in lower case, imperative, describing the behaviour (`fire EVFILT_WRITE on a socket once free send space reaches NOTE_LOWAT`).
- One branch per topic, based on current `main`. Follow-ups go in a new PR.
- PR body: copy [the template](.github/pull_request_template.md), keep every line, tick every box, and fill `What`, `Tested`, `Depends on` (#N or none), `Fixes` (#N or none), `Unblocks` (title ID and discussion, or none), `GPUs tested` (vendor, model, driver, OS for AGC, shader recompiler or VideoOut; otherwise n/a) and `AI-assisted` (**yes** for agent work).
- Before pushing: `python3 tools/check_conventions.py --base origin/main` (use `upstream/main` once remotes are set as in section 9).
- Before opening: `python3 tools/pr_overlap.py --branch <branch>`; agree an order with overlapping PRs and declare it with `Depends on`.
- A speed claim shows `tools/trace_digest.py` summary lines of `main` and of the change, from the same machine and scene, with the traces attached.

## 4. Code style

There is no `.clang-format`. Match the file you are in. The common style:

- 4-space indent, no tabs. Opening brace on the same line. `case` indented inside `switch`. Short single-statement `case` bodies may share a line.
- Includes at the top, project headers first, then standard headers, sorted roughly alphabetically. Relinker sources include with angle brackets from the module root (`#include <relinker/patching/GamePatch.hpp>`); libraries include with quotes from `core/libs` (`#include "prx/libc/include/General.hpp"`).
- Naming (from CONVENTIONS):
  - Interfaces (only pure virtual methods) start with `I`.
  - Classes, structs and public methods: `PascalCase`. Public struct fields in the relinker: `PascalCase` (`RawValue::IsString`).
  - Private methods and fields, function arguments, locals: `camelCase`.
  - Template parameters: `TKey`, `TValue`, `TCall`.
  - Constants: `kPascalCase` in the relinker (`kEntryKeys`); console error codes in libraries: `UPPER_SNAKE` (`AUDIO_IN_ERROR_INVALID_HANDLE`).
  - File-scope globals in libraries: `g_camelCase` (`g_mutex`, `g_ports`).
  - Exports keep the console name exactly (`sceAudioInOpen`). Their parameters often keep the SDK's `snake_case` names; leave existing ones as they are.
- File-local helpers go in an anonymous `namespace { }`. Relinker code lives in `namespace Relinker::...`.
- Use `std::` fixed-width types (`std::uint32_t`) in new code; existing exports use `int`, `int32_t`, `uint32_t` to match the SDK signature.
- Console error codes are `constexpr int NAME = static_cast<int>(0x8026xxxx);` near the top of the file.
- Keep functions small and direct. No speculative abstraction, no unused parameters "for later", no dead code.

### Shape of a library export

```cpp
#include "SceTypes.hpp"
#include "prx/libc/include/General.hpp"
#include <mutex>

namespace {

constexpr int FOO_ERROR_INVALID_HANDLE = static_cast<int>(0x80AB0001);

std::mutex g_mutex;

}

extern "C" {

int APS5_VABI sceFooOpen(int userId, std::uint32_t type) {
    std::lock_guard lock(g_mutex);
    ...
}

int32_t APS5_VABI sceFooGetSomething(int32_t handle) {
    NotImplemented_nid_no_patch(__func__);
}

}
```

- Every export is `extern "C"` and `APS5_VABI` (System V ABI on Windows hosts).
- When the symbol name of a NID is unknown, define a function with a descriptive name and bind it with `APS5_EXPORT("<11-char NID>", function);`. `tools/nid_names.py` suggests real names for unknown NIDs; `tools/stubgen.py --module <lib> --nids <file>` generates `Export.cpp` skeletons and debt lines for a list of missing NIDs.
- A new library: `core/libs/prx/<library>/CMakeLists.txt` with `add_library(<library> SHARED EXCLUDE_FROM_ALL ...)`, `target_include_directories(... ${LIBS_INCLUDE_DIR})`, `configure_windows_unwind(<library>)`, and the `--exclude-libs,ALL` link option when it links static dependencies. Copy a neighbour such as `libSceAudioIn`.

### Shape of a test

- Library tests are executables in `core/libs/tests/Guest<Area>.cpp`, registered in the library's `CMakeLists.txt` under `if(BUILD_TESTING)` with `add_test_executable` and one `add_test(NAME guest_<area>_<case> COMMAND <exe> <case>)` per case. On Windows, prepend the library directory to `PATH` with `ENVIRONMENT_MODIFICATION`.
- A test declares the exports it calls in `extern "C"`, checks with a local `Require(bool)` that calls `std::abort()`, and asserts throws through helpers like `ReportsNotImplemented`.
- Every built test executable must be run by some `add_test` (`tools/check_test_registration.py`). Every `tools/tests/test_*.py` must be registered too.
- Each test finishes in 30 s on CI runners, Vulkan tests included (lavapipe, empty shader cache, parallel ctest). Split or shrink a slow test; never raise its timeout.
- Python tool tests use `unittest` in `tools/tests/test_<tool>.py`; web tests are `demo/web/tests/*.test.mjs`.

## 5. Build and test

Requirements: x86-64, Git, CMake 3.22.1+, Ninja, a C++20 compiler (GCC on Linux; on Windows only WinLibs MinGW-w64 GCC 15.2.0 UCRT posix-seh). Linux also needs the X11/Xext, Wayland/xkbcommon/EGL, libdecor, XRandR and PipeWire/PulseAudio/ALSA development packages listed in [BUILD](docs/dev/BUILD.md). Python 3.9+ for tools and Python-backed tests.

Relinker only (no submodules, no GPU; also on macOS). Use this for any change under `core/relinker` or `tools/`:

```sh
cmake -S . -B build-relinker -G Ninja -DCMAKE_BUILD_TYPE=Release -DANYPS5_RELINKER_ONLY=ON -DBUILD_TESTING=ON
cmake --build build-relinker --parallel
ctest --test-dir build-relinker --output-on-failure
```

Full build (libraries, shader recompiler, GPU):

```sh
git submodule update --init --recursive
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build --parallel
cmake --build build --target libs --parallel
ctest --test-dir build --output-on-failure
```

- `libs` is a custom target; every library is `EXCLUDE_FROM_ALL`. Titles load the patched `.prx` files from `build/core/libs/libs`. A library change tested without rebuilding `libs` tests the old binary.
- Keep `build-relinker` and `build` as separate directories.
- Fast feedback: `python3 tools/check_compile.py --build build <file.cpp>` compiles single files with their real flags. It does not replace a build and test run.
- Run only the affected tests: `python3 tools/select_tests.py select ...` then `python3 tools/select_tests.py ctest ...`, or `ctest --test-dir build -R <pattern> --output-on-failure`.
- Useful flags: `-DANYPS5_ENABLE_SPIRV_TOOLS=ON` (validate SPIR-V), `-DANYPS5_ENABLE_ASAN=ON`, `-DAPS5_ENABLE_TRACY=ON`, `-DCMAKE_CXX_COMPILER_LAUNCHER=ccache`. Full table in BUILD.
- Python tools: `python3 -m unittest discover -s tools/tests`. Web: `node --test demo/web/tests`.

GPU changes (AGC driver, shader recompiler, VideoOut): run the same focused tests on `main` and on the change, same machine and GPU:

```sh
ANYPS5_REQUIRE_VULKAN=1 ANYPS5_NO_SHADER_CACHE=1 VK_INSTANCE_LAYERS=VK_LAYER_KHRONOS_validation \
    ctest --test-dir build -R <pattern> -V > run.log 2>&1
```

Confirm neither log contains `was not found but was requested by env var VK_INSTANCE_LAYERS`, then confirm the change adds no new `VUID-` errors. `ctest` reports `Passed` even when validation errors are logged, so read the log.

## 6. Workflows

### Implement or fix an export

1. Find the library in `core/libs/prx/<library>`. Read its debt file and its existing tests.
2. Check that no open upstream PR implements the same functions (`python3 tools/pr_overlap.py --branch <branch>` after your first commit, or search open PRs).
3. Find the signature and semantics from public references (SDK headers in open projects, shadPS4, KytyPS5, prosper, SharpProspero, ps5-payload-dev), never from a single title's call site alone. Record what each reference says when they disagree.
4. Implement every input path. Validate arguments the way the console does and return its error codes. Throw on what you cannot settle.
5. Add or extend a `Guest<Area>` test that exercises behaviour, including error paths.
6. Update `docs/dev/debt/<library>.md`: remove the entry you closed, or cut it to what is still open. Do not rewrite it to describe the new behaviour.
7. Build `libs`, run the tests, run `check_conventions.py`.

### Bring up a title

Follow [GAME_TESTING](docs/dev/GAME_TESTING.md): unwrap with `tools/unwrap_self.py`, convert with `relinker --registry`, convert every bundled module, run `tools/import_audit.py` on the registries, launch with `APS5_PROFILE_DRAW=1` and the other variables from that page. A stop becomes a general fix in a library, never a title check. The PR names the title in `Unblocks: <title ID> #<discussion>`. Logs and screenshots go in the PR or the Game bring-up discussion, never the repository.

### Performance work

Capture with `APS5_TRACE_FRAMES` / `APS5_TRACE_SECONDS` ([TRACING](docs/dev/TRACING.md)), summarise with `tools/trace_digest.py`, compare `main` and the change with `tools/performance_compare.py` on the same machine and scene. A `perf(...)` PR without two valid summary lines is labelled `perf numbers missing`.

### Shader recompiler

Decode in `RdnaDecoder`, lower through `IntermediateRepresentation` and `Translation`, emit in `SpirvBackend`. Semantics need a hardware measurement (`tools/hw-oracle`) or an exact ISA/LLVM/ACO/Mesa reference. Bump nothing in the shader cache versioning by hand unless the source of cache keys changed (`ShaderCacheVersion.cmake`).

## 7. Documentation style

Dry, strict, concise. State facts, not intentions. A debt entry states the gap first (what differs from the console, what is unverified, what throws), describes implemented behaviour only as far as the gap needs, and may end with `Closes when: <measurement, title or test>`. Link the source file with a relative path (`../../../core/libs/prx/<library>/Export.cpp`). No new documentation files unless upstream asked for them.

## 8. Agent behaviour

- Do not invent. If you do not know a signature, a structure layout or an error code, say so, throw in code, and record it in debt.
- Do not widen scope. One topic per change. Do not reformat files you did not need to touch.
- Do not delete or loosen a test to make a change pass. Do not raise a test timeout.
- Do not commit build directories, logs, traces (`aps5-trace-*.json.gz`), game files or converted executables.
- Run the narrowest build that covers your change and say exactly what you ran and what passed. "Not tested" is an acceptable answer; a false "tested" is not.
- Never push, open a PR, or comment upstream without the user's go-ahead.

## 9. This fork

- Upstream: `https://github.com/boykopovar/AnyPS5`, default branch `main`, license GPL-2.0-only. Keep the license and copyright notices.
- Recommended remotes: `upstream` = boykopovar/AnyPS5, `origin` = your fork. `tools/check_main_sync.py` prefers `upstream/main`.

  ```sh
  git remote rename origin upstream
  git remote add origin git@github.com:<you>/AnyPS5.git
  ```

- Sync often: `git fetch upstream && git rebase upstream/main` (upstream merges dozens of PRs a day).
- Every patch is tracked in [FORK_PATCHES.md](FORK_PATCHES.md): one feature branch per patch from `upstream/main`, one row per branch, updated as its status changes. `nhl27` is the integration branch that merges them for game runs. Game byte patches (relinker `--patches` files) go in `fork-patches/`.
- Fork-only files: `CLAUDE.md`, `.claude/`, `FORK_PATCHES.md`, `fork-patches/`, `fork-notes/`, `fork-tools/`, `.beans/` and `.beans.yml` exist only in this fork. Upstream's conventions check rejects them (`notes-file`). Keep them in a separate commit on the fork's `main`, and build every branch meant for an upstream PR from `upstream/main` so they never appear in its diff. Before opening an upstream PR, `git diff --name-only upstream/main...HEAD` must not list them. This file (`AGENTS.md`) does exist upstream; do not send this rewrite upstream unless the user asks.
