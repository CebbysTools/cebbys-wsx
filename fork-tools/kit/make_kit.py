import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME_DLLS = ["libgcc_s_seh-1.dll", "libstdc++-6.dll", "libwinpthread-1.dll"]
LIB_EXTRA_DLLS = ["mimalloc.dll", "mimalloc-redirect.dll"]
GAME_SUFFIXES = {".bin", ".elf", ".self", ".sprx", ".pkg", ".toc", ".sb", ".cas", ".cat"}
KIT_FILES = ["setup.ps1", "Run NHL 27.cmd", "README.txt"]


def git(source, *args):
    return subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True, text=True).stdout.strip()


def check_game_free(root):
    found = []
    for path in root.rglob("*"):
        if path.is_file() and (path.suffix.lower() in GAME_SUFFIXES or path.name.endswith(".guest.prx") or "app0" in path.parts):
            found.append(path)
    if found:
        raise SystemExit("game data in the kit: " + ", ".join(str(p.relative_to(root)) for p in found[:10]))


def main():
    parser = argparse.ArgumentParser(description="Build the game-free NHL 27 kit zip")
    parser.add_argument("--source", default="/mnt/c/Users/valen/anyps5-src")
    parser.add_argument("--toolchain-bin", default="/mnt/c/Users/valen/anyps5-toolchain/mingw64/bin")
    parser.add_argument("--extra-dlls", default="/mnt/c/Games/NHL 27/windows/libs")
    parser.add_argument("--out", default="/mnt/c/Games/NHL 27/kit")
    args = parser.parse_args()
    source = Path(args.source)
    built = source / "build" / "core" / "libs" / "libs"
    relinker = source / "build" / "core" / "relinker" / "relinker.exe"
    out = Path(args.out)
    stage = out / "NHL27-AnyPS5-kit"
    shutil.rmtree(stage, ignore_errors=True)
    (stage / "libs").mkdir(parents=True)
    (stage / "tools").mkdir()
    for prx in sorted(built.glob("*.prx")):
        shutil.copy2(prx, stage / "libs")
    for name in RUNTIME_DLLS:
        shutil.copy2(Path(args.toolchain_bin) / name, stage / "libs")
        shutil.copy2(Path(args.toolchain_bin) / name, stage / "tools")
    for name in LIB_EXTRA_DLLS:
        shutil.copy2(Path(args.extra_dlls) / name, stage / "libs")
    shutil.copy2(relinker, stage / "tools")
    shutil.copy2(source / "tools" / "unwrap_self.py", stage / "tools")
    shutil.copy2(source / "LICENSE", stage / "LICENSE.txt")
    for name in KIT_FILES:
        shutil.copy2(HERE / name, stage / name)
    branch = git(source, "rev-parse", "--abbrev-ref", "HEAD")
    commit = git(source, "rev-parse", "HEAD")
    dirty = git(source, "status", "--porcelain", "--untracked-files=no")
    (stage / "BUILD.txt").write_text(f"branch {branch}\ncommit {commit}\nlocal changes: {'yes' if dirty else 'no'}\nsource https://github.com/CebbysTools/cebbys-wsx/tree/{commit}\n", newline="\r\n")
    check_game_free(stage)
    archive = out / f"NHL27-AnyPS5-kit-{commit[:9]}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(out))
    size = archive.stat().st_size >> 20
    if size >= 500:
        raise SystemExit(f"kit is {size} MiB, over the 500 MiB limit")
    print(f"{archive} {size} MiB, {branch} {commit[:9]}")


if __name__ == "__main__":
    main()
