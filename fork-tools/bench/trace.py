import argparse
import csv
import shutil
import subprocess
import time
from pathlib import Path

TOOLCHAIN = Path("/mnt/c/Users/valen/anyps5-toolchain")
TRACE_DIR = Path("/mnt/c/Games/NHL 27/traces/ngfx-trace")
FRAME_METRICS = {
    "FE_B.TriageSCG.gr__cycles_active.avg.pct_of_peak_sustained_elapsed": "graphics engine active %",
    "GPUTrace.sm__throughput.avg.pct_of_peak_sustained_elapsed": "SM throughput % of peak",
    "tpc__warps_active_shader_cs_realtime.avg.pct_of_peak_sustained_elapsed": "compute warps active %",
    "PCI.TriageSCG.pcie__write_bytes.sum": "PCIe write bytes",
    "PCI.TriageSCG.pcie__read_bytes.sum": "PCIe read bytes",
    "tpc__warp_launch_cycles_stalled_shader_cs_reason_register_allocation.sum": "CS launch stalled on registers (cycles)",
    "FE_B.TriageSCG.fe__cycles_stalled_cmd_wfi_queue_sync.avg.pct_of_peak_sustained_elapsed": "front end waiting for idle %",
}


def rows(path):
    with path.open(encoding="utf-8", errors="replace") as handle:
        return list(csv.reader(handle, delimiter="\t"))


def main():
    parser = argparse.ArgumentParser(description="Run the elevated Nsight GPU Trace task and summarise its export")
    parser.add_argument("label")
    parser.add_argument("--timeout", type=int, default=1500)
    parser.add_argument("--top", type=int, default=15)
    args = parser.parse_args()
    log = TOOLCHAIN / "trace.log"
    if log.exists():
        log.unlink()
    if TRACE_DIR.exists():
        shutil.rmtree(TRACE_DIR)
    TRACE_DIR.mkdir(parents=True)
    subprocess.run(["cmd.exe", "/c", "schtasks /run /tn AnyPS5Trace"], cwd=TOOLCHAIN, check=True, stdout=subprocess.DEVNULL)
    start = time.monotonic()
    while time.monotonic() - start < args.timeout:
        if log.exists() and "ngfx exit" in log.read_text(errors="replace"):
            break
        time.sleep(10)
    subprocess.run(["cmd.exe", "/c", "taskkill /F /T /IM eboot.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = TRACE_DIR / "BASE"
    if not (base / "FRAME.xls").exists():
        print("no export; see", log)
        return
    print(f"# {args.label}")
    for row in rows(base / "FRAME.xls"):
        print(f"{row[0]}: {' / '.join(row[1:])} ms")
    frame = {row[0]: row[1:] for row in rows(base / "GPUTRACE_FRAME.xls") if row}
    for key, name in FRAME_METRICS.items():
        if key in frame:
            print(f"{name}: {' / '.join(frame[key])}")
    events = rows(base / "D3DPERF_EVENTS.xls")[1:]
    total = sum(float(row[1]) for row in events if len(row) > 1)
    print(f"labelled dispatches: {len(events)}, {total:.1f} ms over the traced frames")
    for row in sorted(events, key=lambda row: -float(row[1]))[:args.top]:
        print(f"  {float(row[1]):9.3f} ms  {row[0]}")
    saved = TRACE_DIR.parent / f"ngfx-{args.label}"
    if saved.exists():
        shutil.rmtree(saved)
    shutil.copytree(base, saved)


if __name__ == "__main__":
    main()
