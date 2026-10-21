import argparse
import csv
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/mnt/c/Games/NHL 27")
ROOT_WIN = r"C:\Games\NHL 27"
GAME_DIR = ROOT / "windows"
GAME_DIR_WIN = ROOT_WIN + r"\windows"
LOG_DIR = ROOT / "logs"
PAD_TOOL = Path(__file__).resolve().parents[2] / "tools" / "pad_input.py"
BASE_ENV = {
    "ANYPS5_OUTPUT_RESOLUTION": "2160p",
    "APS5_LOG_TIMESTAMPS": "1",
    "APS5_PROFILE_DRAW": "1",
    "APS5_PROFILE_GPU": "1",
}

PRESENT = re.compile(r"^\[present\] (\d+) presents over 10 s")
BUSY = re.compile(r"GPU busy ([0-9.]+) ms, idle gaps ([0-9.]+) ms")
GPUTIME_CLASS = re.compile(r"([a-z-]+) x(\d+) ([0-9.]+)ms(?: ([0-9.]+)MiB)?")
DRAW = re.compile(r"^\[draw\] driver phases \(10 s, (\d+) draw packets.*?lock wait ([0-9.]+)")
DISPATCH = re.compile(r"^\[dispatch\] driver phases queue 0 direct \(10 s, (\d+) dispatches.*?device call ([0-9.]+)")
CACHE = re.compile(r"totals: (\d+) hits, (\d+) misses")
FATAL = re.compile(r"what\(\):\s*(.*)|^FATAL: (.*)")


def run_game(log_name, seconds, env, press_after, press_every):
    pad = GAME_DIR / "pad.txt"
    pad.write_text("")
    log = LOG_DIR / log_name
    if log.exists():
        log.unlink()
    sets = "".join(f"set {k}={v}&& " for k, v in env.items())
    sets += f"set APS5_PAD_INPUT_FILE={GAME_DIR_WIN}\\pad.txt&& "
    process = subprocess.Popen(["cmd.exe", "/c", f"{sets}eboot.exe > ..\\logs\\{log_name} 2>&1"], cwd=GAME_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    start = time.monotonic()
    milestones = {}
    next_press = press_after
    seen = 0
    while process.poll() is None:
        elapsed = time.monotonic() - start
        if elapsed >= seconds:
            break
        if press_every > 0 and elapsed >= next_press:
            subprocess.run([sys.executable, "-I", str(PAD_TOOL), "--hold-ms", "150", str(pad), "cross"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            next_press = elapsed + press_every
        if log.exists():
            with log.open("r", errors="replace") as handle:
                handle.seek(seen)
                chunk = handle.read()
                seen = handle.tell()
            for line in chunk.splitlines():
                match = PRESENT.match(line)
                if not match:
                    continue
                count = int(match.group(1))
                if count > 0 and "first_present_s" not in milestones:
                    milestones["first_present_s"] = round(elapsed, 1)
                if count >= 10 and "first_interactive_s" not in milestones:
                    milestones["first_interactive_s"] = round(elapsed, 1)
        time.sleep(1.0)
    subprocess.run(["cmd.exe", "/c", "taskkill /F /T /IM eboot.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process.wait()
    milestones["ran_s"] = round(time.monotonic() - start, 1)
    return log, milestones


def parse(log, skip_windows):
    presents, busy, idle, lock_wait, device_call, classes = [], [], [], [], [], {}
    cache = None
    failure = None
    for line in log.read_text(errors="replace").splitlines():
        match = PRESENT.match(line)
        if match:
            presents.append(int(match.group(1)))
            timing = BUSY.search(line)
            if timing and len(presents) > skip_windows:
                busy.append(float(timing.group(1)))
                idle.append(float(timing.group(2)))
            continue
        if line.startswith("[gputime]") and len(presents) > skip_windows and " by class: " in line:
            frames = presents[-1] or 1
            for name, count, ms, mib in GPUTIME_CLASS.findall(line.split(" by class: ", 1)[1].split(";")[0]):
                entry = classes.setdefault(name, [0.0, 0.0, 0])
                entry[0] += float(ms) / frames
                entry[1] += float(mib or 0) / frames
                entry[2] += 1
            continue
        match = DRAW.match(line)
        if match and len(presents) > skip_windows:
            lock_wait.append(float(match.group(2)))
            continue
        match = DISPATCH.match(line)
        if match and len(presents) > skip_windows:
            device_call.append(float(match.group(2)))
            continue
        match = CACHE.search(line)
        if match:
            cache = (int(match.group(1)), int(match.group(2)))
        match = FATAL.search(line)
        if match and failure is None:
            failure = (match.group(1) or match.group(2)).strip()[:160]
    steady = presents[skip_windows:]
    fps = [count / 10.0 for count in steady]
    mean = lambda values: round(statistics.fmean(values), 2) if values else None
    result = {
        "windows": len(presents),
        "fps_mean": mean(fps),
        "fps_min_window": min(fps) if fps else None,
        "fps_max_window": max(fps) if fps else None,
        "gpu_busy_ms_per_frame": mean(busy),
        "gpu_idle_ms_per_frame": mean(idle),
        "draw_lock_wait_us": mean(lock_wait),
        "dispatch_device_call_us": mean(device_call),
        "cache_hits": cache[0] if cache else None,
        "cache_misses": cache[1] if cache else None,
        "failure": failure,
    }
    for name, (ms, mib, windows) in sorted(classes.items()):
        result[f"{name}_ms_per_frame"] = round(ms / windows, 2)
        if mib:
            result[f"{name}_mib_per_frame"] = round(mib / windows, 1)
    return result


def main():
    parser = argparse.ArgumentParser(description="Measure the converted title with a fixed scene and report the milestone metrics")
    parser.add_argument("label")
    parser.add_argument("--seconds", type=int, default=420)
    parser.add_argument("--skip-windows", type=int, default=12, help="10 s windows excluded from steady-state numbers (boot and loading)")
    parser.add_argument("--press-after", type=int, default=50)
    parser.add_argument("--press-every", type=int, default=15)
    parser.add_argument("--env", action="append", default=[], help="NAME=VALUE added to the base environment")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    parser.add_argument("--parse-only", help="existing log name in the logs folder; no run")
    args = parser.parse_args()
    env = dict(BASE_ENV)
    for item in args.env:
        name, _, value = item.partition("=")
        env[name] = value
    log_name = f"bench-{args.label}.log"
    if args.parse_only:
        log, milestones = LOG_DIR / args.parse_only, {}
    else:
        log, milestones = run_game(log_name, args.seconds, env, args.press_after, args.press_every)
    result = {"label": args.label, **milestones, **parse(log, args.skip_windows), "env": " ".join(f"{k}={v}" for k, v in env.items() if k not in BASE_ENV)}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    table = out / "results.csv"
    rows = list(csv.DictReader(table.open())) if table.exists() else []
    rows = [row for row in rows if row["label"] != args.label] + [{key: "" if value is None else value for key, value in result.items()}]
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with table.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    width = max(len(key) for key in result)
    for key, value in result.items():
        print(f"{key.ljust(width)}  {value}")


if __name__ == "__main__":
    main()
