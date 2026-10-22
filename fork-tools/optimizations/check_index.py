#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "docs" / "user" / "optimizations"
LEAF_SECTIONS = ("## Cause", "## Options", "## Result", "## Why")
STATUSES = ("planned", "researched", "testing", "applied", "rejected", "no-gain")
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK = re.compile(r"\]\(([^)#\s]+)\)")


def check_folder(folder: Path, root: Path, errors: list[str]) -> None:
    relative = folder.relative_to(root.parent)
    if folder != root and not NAME.match(folder.name):
        errors.append(f"{relative}: folder name must be lower-case words joined by '-'")
    index = folder / "INDEX.md"
    if not index.is_file():
        errors.append(f"{relative}: INDEX.md is missing")
        return
    text = index.read_text(encoding="utf-8")
    if not text.startswith("# "):
        errors.append(f"{relative}/INDEX.md: the first line must be a '# ' title")
    children = sorted(path for path in folder.iterdir() if path.is_dir())
    links = {link for link in LINK.findall(text) if not link.startswith("http")}
    expected = {f"{child.name}/INDEX.md" for child in children}
    for link in sorted(expected - links):
        errors.append(f"{relative}/INDEX.md: link to direct child {link} is missing")
    for link in sorted(links):
        if link.endswith(".md") and link not in expected and not link.startswith("../"):
            errors.append(f"{relative}/INDEX.md: link {link} is not a direct child INDEX.md")
    if folder != root:
        status = re.search(r"^Status: `([a-z-]+)`", text, re.MULTILINE)
        if status is None or status.group(1) not in STATUSES:
            errors.append(f"{relative}/INDEX.md: needs a 'Status: `<value>`' line with one of {', '.join(STATUSES)}")
        for section in LEAF_SECTIONS:
            if section not in text:
                errors.append(f"{relative}/INDEX.md: section '{section}' is missing")
    for child in children:
        check_folder(child, root, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the structure of docs/user/optimizations")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"{root}: folder is missing")
        return 1
    errors: list[str] = []
    check_folder(root, root, errors)
    for error in errors:
        print(error)
    if errors:
        print(f"{len(errors)} problem(s)")
        return 1
    print("optimization docs: structure OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
