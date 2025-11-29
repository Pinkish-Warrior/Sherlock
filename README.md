# Sherlock

Sherlock is an all-in-one Python tool to inventory, analyze, and summarize your projects on macOS.  
It scans folders, detects project roots (Python, Node.js, Go, Rust, C/C++, Git, etc.), generates a full file inventory, and produces a project summary with alerts for dead, large, or duplicate-name projects.

---

## Features

- Full file-level inventory with:
  - project name
  - project root path
  - language
  - file path
  - file size
  - creation date
  - last opened date
- Project summary CSV with:
  - file count
  - total size
  - oldest and newest file
  - alert for:
    - dead projects (not opened > 2 years)
    - large projects (> 500MB)
    - possible duplicate project names
- Stage-based scanning: Desktop, Downloads, Documents, or any folder
- Single script (`sherlock.py`) handles everything

---

## Requirements

- Python 3.x
- macOS (uses file creation and access timestamps)
- Terminal access

---

## Installation / Setup

1.0 **Clone the repository** (or copy the folder to your machine):

```bash
git clone <repo-url> sherlock
cd sherlock
```

2.0 **Make sure the script is executable** (optional):

```bash
chmod +x sherlock.py
```

## Usage

1.0 **Scan default folders** (Desktop, Downloads, Documents):

```script
python3 sherlock.py --scan home
```

2.0 **Scan custom folders** (target):

```script
python3 sherlock.py --dirs ~/Projects /Users/you/Downloads
```

3.0 **Output files**

By default, Sherlock produces two CSVs in your home folder:
  • ~/projects_inventory.csv – full file-level inventory
  • ~/projects_summary.csv – project-level summary with alerts

3.1 You can override paths

```script
python3 sherlock.py --scan home --inventory ~/my_inventory.csv --summary ~/my_summary.csv
```

3.2 Optional Parameter

- **--stop-at** : Stop searching for project root above this folder (default: your home directory)

- **--scan all** : Scan the entire filesystem (may be slow)

- **--dirs** : Specify exact folders to scan

---

Next Steps / Recommendations

- Open the CSVs in Excel, Numbers, or Google Sheets;
- Sort and filter projects by:
  - dead_or_duplicate_alert
  - total_size_bytes
  - language or last_opened_iso
  - Use this to identify projects to archive, delete, or reorganize


