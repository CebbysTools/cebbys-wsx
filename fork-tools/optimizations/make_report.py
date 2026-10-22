#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / "bench" / "results" / "results.csv"
LOGS = Path("/mnt/c/Games/NHL 27/logs")
FIELDS = ("label", "fps_mean", "fps_min_window", "fps_max_window", "gpu_busy_ms_per_frame", "gpu_idle_ms_per_frame", "cache_misses", "failure", "env")
PROGRAM = re.compile(r"0x([0-9a-f]+) x(\d+) (\d+)ms")


def summary(label: str, rows: dict[str, dict[str, str]]) -> list[str]:
    row = rows.get(label)
    if row is None:
        return [f"bench {label}: no row in results.csv"]
    return [f"bench {label}: " + ", ".join(f"{field}={row.get(field, '')}" for field in FIELDS[1:])]


def programs(label: str, wanted: list[str], top: int) -> list[str]:
    log = LOGS / f"bench-{label}.log"
    if not log.is_file():
        return [f"log {log.name}: not found"]
    count: dict[str, int] = defaultdict(int)
    total: dict[str, int] = defaultdict(int)
    windows = 0
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("[gputime]"):
            continue
        windows += 1
        for address, dispatches, milliseconds in PROGRAM.findall(line):
            key = address[-7:]
            count[key] += int(dispatches)
            total[key] += int(milliseconds)
    keys = [key for key in wanted if key in total] if wanted else sorted(total, key=total.get, reverse=True)[:top]
    lines = [f"log {log.name}: {windows} [gputime] windows of 10 s"]
    for key in keys:
        lines.append(f"  program ...{key}: {count[key]} dispatches, {total[key]} ms, {total[key] / count[key]:.2f} ms each")
    for key in wanted:
        if key not in total:
            lines.append(f"  program ...{key}: not in this log")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy the bench numbers used by an optimization record into a report file")
    parser.add_argument("labels", nargs="+")
    parser.add_argument("--programs", default="", help="comma-separated program address suffixes (last 7 hex digits)")
    parser.add_argument("--top", type=int, default=6)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rows: dict[str, dict[str, str]] = {}
    if RESULTS.is_file():
        with RESULTS.open(encoding="utf-8") as file:
            for row in csv.DictReader(file):
                rows[row["label"]] = row
    wanted = [item for item in args.programs.split(",") if item]
    lines = [f"source: {RESULTS.name} and {LOGS}"]
    for label in args.labels:
        lines += summary(label, rows)
        lines += programs(label, wanted, args.top)
    text = "\n".join(lines) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
