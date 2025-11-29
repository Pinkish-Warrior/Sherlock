#!/usr/bin/env python3
"""
sherlock.py

All-in-one project inventory and summary tool.
Automatically removes old CSV reports before generating new ones.
"""

import os
import csv
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# -------------- Config ----------------
DEAD_THRESHOLD_YEARS = 2
LARGE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB

# -------------- Project markers --------------
PROJECT_MARKERS = {
    "python": {"pyproject.toml", "requirements.txt", "setup.py", ".venv", "Pipfile"},
    "node": {"package.json", "package-lock.json", "yarn.lock", "node_modules"},
    "go": {"go.mod", "go.sum"},
    "rust": {"Cargo.toml", "Cargo.lock"},
    "c/cpp": {"Makefile", "CMakeLists.txt", ".c", ".h"},
    "git": {".git"},
    "web": {"index.html", "webpack.config.js"},
    "java": {"pom.xml", "build.gradle"},
    "ruby": {"Gemfile"},
    "dotnet": {"*.csproj", "*.sln"},
}

PATTERN_MARKERS = {"*.csproj", "*.sln"}
FLAT_MARKERS = {m for v in PROJECT_MARKERS.values() for m in v if "*" not in m}
MARKER_TO_LANG = {m: lang for lang, markers in PROJECT_MARKERS.items() for m in markers}

# -------------- Helpers --------------
def iso_from_ts(ts):
    try:
        return datetime.fromtimestamp(ts).isoformat()
    except:
        return ""

def find_project_for_dir(dirpath, markers_cache, stop_at):
    original = Path(dirpath).resolve()
    key = str(original)
    if key in markers_cache:
        return markers_cache[key]

    cur = original
    stop_at = stop_at.resolve()
    while True:
        try:
            entries = set(os.listdir(cur))
        except PermissionError:
            entries = set()

        # Exact markers
        for m in FLAT_MARKERS:
            if m in entries:
                markers_cache[key] = (str(cur), MARKER_TO_LANG.get(m, "unknown"))
                return markers_cache[key]

        # Pattern markers
        for patt in PATTERN_MARKERS:
            suffix = patt.lstrip("*")
            for e in entries:
                if e.endswith(suffix):
                    markers_cache[key] = (str(cur), MARKER_TO_LANG.get(patt, "unknown"))
                    return markers_cache[key]

        if cur == stop_at or cur.parent == cur:
            break
        cur = cur.parent

    markers_cache[key] = (None, "unknown")
    return markers_cache[key]

def default_home_dirs():
    home = Path.home()
    return [str(home / "Desktop"), str(home / "Downloads"), str(home / "Documents")]

# -------------- Report cleanup --------------
def cleanup_report_folder(report_dir: Path):
    """
    Deletes all CSV files in the report folder to prevent clutter.
    """
    removed = 0
    for f in report_dir.glob("*.csv"):
        try:
            f.unlink()
            removed += 1
        except Exception:
            pass
    print(f"🧹 Cleaned {removed} old report file(s).")

# -------------- Inventory & Summary --------------
def scan_and_write(directories, inventory_csv, summary_csv, stop_at):
    headers_inv = ["project_name","project_root","language","file_path","size_bytes","created_iso","last_opened_iso"]
    headers_sum = ["project_root","project_name","language","file_count","total_size_bytes","oldest_file","newest_file","dead_or_duplicate_alert"]

    markers_cache = {}
    projects = {}
    name_to_roots = defaultdict(list)
    now = datetime.now()
    seen_roots = set()

    # Inventory CSV
    with open(os.path.expanduser(inventory_csv), "w", newline="", encoding="utf-8") as inv_file:
        writer_inv = csv.writer(inv_file)
        writer_inv.writerow(headers_inv)

        for base in directories:
            base = os.path.expanduser(base)
            if not os.path.exists(base):
                continue

            for root, dirs, files in os.walk(base):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        st = os.stat(fpath)
                    except Exception:
                        continue

                    proj_root, lang = find_project_for_dir(root, markers_cache, stop_at)
                    proj_name = os.path.basename(proj_root.rstrip(os.sep)) if proj_root else ""

                    if proj_root:
                        seen_roots.add(proj_root)

                    if proj_root not in projects:
                        projects[proj_root] = {
                            "project_name": proj_name or "NONE",
                            "language": lang or "unknown",
                            "file_count": 0,
                            "total_size": 0,
                            "oldest_file": None,
                            "newest_file": None
                        }
                        if proj_name:
                            name_to_roots[proj_name].append(proj_root)

                    proj = projects.get(proj_root)
                    if proj:
                        proj["file_count"] += 1
                        proj["total_size"] += st.st_size
                        created_ts = getattr(st, "st_birthtime", st.st_ctime)
                        opened_ts = st.st_atime
                        try:
                            created_dt = datetime.fromtimestamp(created_ts)
                        except:
                            created_dt = None
                        try:
                            opened_dt = datetime.fromtimestamp(opened_ts)
                        except:
                            opened_dt = None

                        if created_dt and (not proj["oldest_file"] or created_dt < proj["oldest_file"]):
                            proj["oldest_file"] = created_dt
                        if opened_dt and (not proj["newest_file"] or opened_dt > proj["newest_file"]):
                            proj["newest_file"] = opened_dt

                    writer_inv.writerow([
                        proj_name,
                        proj_root or "",
                        lang,
                        fpath,
                        st.st_size,
                        iso_from_ts(created_ts),
                        iso_from_ts(opened_ts)
                    ])

    # Summary CSV
    with open(os.path.expanduser(summary_csv), "w", newline="", encoding="utf-8") as sum_file:
        writer_sum = csv.writer(sum_file)
        writer_sum.writerow(headers_sum)

        for root, data in projects.items():
            oldest = data["oldest_file"].isoformat() if data["oldest_file"] else ""
            newest = data["newest_file"].isoformat() if data["newest_file"] else ""

            alerts = []
            if data["newest_file"] and now - data["newest_file"] > timedelta(days=DEAD_THRESHOLD_YEARS*365):
                alerts.append("dead")
            if data["total_size"] > LARGE_SIZE_BYTES:
                alerts.append("large")
            if len(name_to_roots[data["project_name"]]) > 1:
                alerts.append("duplicate")

            writer_sum.writerow([
                root,
                data["project_name"],
                data["language"],
                data["file_count"],
                data["total_size"],
                oldest,
                newest,
                "; ".join(alerts)
            ])

    print(f"Inventory written to {inventory_csv}")
    print(f"Summary written to {summary_csv}")
    print(f"Detected {len([r for r in seen_roots if r])} project roots.")

# -------------- CLI --------------
def main():
    parser = argparse.ArgumentParser(description="Sherlock: Project inventory & summary with alerts")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--scan", choices=["home","all"])
    group.add_argument("--dirs", nargs="+")
    parser.add_argument("--inventory", "-i")
    parser.add_argument("--summary", "-s")
    parser.add_argument("--stop-at", default=str(Path.home()))
    args = parser.parse_args()

    if args.scan == "home" or args.scan is None:
        directories = default_home_dirs()
    elif args.scan == "all":
        directories = ["/"]
    else:
        directories = args.dirs

    script_dir = Path(__file__).resolve().parent
    report_dir = script_dir / "Report"
    report_dir.mkdir(parents=True, exist_ok=True)

    # 🧹 Delete pre-existing old reports
    cleanup_report_folder(report_dir)

    inventory_csv = args.inventory if args.inventory else str(report_dir / "projects_inventory.csv")
    summary_csv = args.summary if args.summary else str(report_dir / "projects_summary.csv")

    stop_at = Path(args.stop_at).resolve()
    print("Scanning:", directories)
    print("Saving to:", str(report_dir))

    scan_and_write(directories, inventory_csv, summary_csv, stop_at)

if __name__ == "__main__":
    main()