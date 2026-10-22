#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "docs" / "user" / "optimizations"
LEAF_SECTIONS = ("## Cause", "## Options", "## Result", "## Why")
EVIDENCE_STATUSES = ("testing", "applied", "rejected", "no-gain")
EVIDENCE_SECTIONS = ("## Evidence", "### Original", "### Change", "### Reason", "### Improvement", "### Timings", "### Reports")
STATUSES = ("planned", "researched", "testing", "applied", "rejected", "no-gain")
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK = re.compile(r"\]\(([^)#\s]+)\)")
SIGNED_PERCENT = re.compile(r"(?<![\w|])[+-]\d+(?:\.\d+)?\s?%")
REDUCTION_PERCENT = re.compile(r"\b(fell|dropped|reduced|decreased|lower|less|faster|slower) by \d+(?:\.\d+)?\s?%", re.IGNORECASE)


def check_evidence(folder: Path, text: str, relative: Path, errors: list[str]) -> None:
    positions = []
    for section in EVIDENCE_SECTIONS:
        position = text.find(section + "\n")
        if position < 0:
            errors.append(f"{relative}/INDEX.md: evidence section '{section}' is missing")
            return
        positions.append(position)
    if positions != sorted(positions):
        errors.append(f"{relative}/INDEX.md: evidence sections are not in the required order")
        return
    timings = text[positions[5]:positions[6]]
    if "|---" not in timings:
        errors.append(f"{relative}/INDEX.md: '### Timings' needs a table")
    reports = text[positions[6]:]
    linked = [link for link in LINK.findall(reports) if not link.startswith("http")]
    if not linked and "report not kept" not in reports:
        errors.append(f"{relative}/INDEX.md: '### Reports' needs a link to a report file or 'report not kept'")
    for link in linked:
        if not (folder / link).is_file():
            errors.append(f"{relative}/INDEX.md: report {link} does not exist")


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
    summary = re.search(r"^## Improvement summary\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if summary is None:
        errors.append(f"{relative}/INDEX.md: section '## Improvement summary' is missing")
    elif "|---" not in summary.group(1):
        errors.append(f"{relative}/INDEX.md: '## Improvement summary' needs a table with the start and the current values")
    elif "Improvement %" not in summary.group(1):
        errors.append(f"{relative}/INDEX.md: '## Improvement summary' needs an 'Improvement %' column")
    for match in SIGNED_PERCENT.finditer(text):
        if match.group(0).startswith("-") and text[:match.start()].lower().endswith("improvement "):
            continue
        errors.append(f"{relative}/INDEX.md: '{match.group(0)}' uses a signed percentage; write the improvement % without a sign (negative only for worse, in an 'Improvement %' column or as 'improvement -N%')")
    for match in REDUCTION_PERCENT.finditer(text):
        errors.append(f"{relative}/INDEX.md: '{match.group(0)}' states a reduction; state the improvement % instead")
    links = {link for link in LINK.findall(text) if not link.startswith("http")}
    expected = {f"{child.name}/INDEX.md" for child in children}
    for link in sorted(expected - links):
        errors.append(f"{relative}/INDEX.md: link to direct child {link} is missing")
    for link in sorted(links):
        if link.endswith(".md") and link not in expected and not link.startswith("../") and "/" in link:
            errors.append(f"{relative}/INDEX.md: link {link} is not a direct child INDEX.md")
    if folder != root:
        status = re.search(r"^Status: `([a-z-]+)`", text, re.MULTILINE)
        if status is None or status.group(1) not in STATUSES:
            errors.append(f"{relative}/INDEX.md: needs a 'Status: `<value>`' line with one of {', '.join(STATUSES)}")
        for section in LEAF_SECTIONS:
            if section not in text:
                errors.append(f"{relative}/INDEX.md: section '{section}' is missing")
        if status is not None and status.group(1) in EVIDENCE_STATUSES and not children:
            check_evidence(folder, text, relative, errors)
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
