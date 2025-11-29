# Environment Cleanup & Organization Plan

Based on the analysis from the Sherlock reports, this plan provides a structured approach to declutter and organize your development environment. The goal is to improve efficiency, reduce storage usage, and standardize project structures.

---

## Phase 1: Project Deduplication and Archival

The reports indicate the presence of duplicate or outdated projects. Archiving or removing them will reclaim significant space and reduce clutter.

**Action Items:**

1. **Archive `GitHandShake_old`:** This project appears to be an outdated version.
    * **Recommendation:** Move it to a dedicated archive directory.
    * **Command:** `mkdir -p _archive && mv GitHandShake_old _archive/`

2. **Handle Duplicate `pro0930-verbose-train`:** The summary report marks this as a duplicate.
    * **Recommendation:** Review and delete the older or incorrect version. If it's a backup, archive it.
    * **Command (if deleting):** `rm -rf /Users/taniasantana/Desktop/Playground/pro0930-verbose-train`
    * **Command (if archiving):** `mv /Users/taniasantana/Desktop/Playground/pro0930-verbose-train _archive/`

---

## Phase 2: Dependency Cleanup

`node_modules` directories consume a vast amount of space and can be safely removed and re-generated from `package.json` files.

**Action Items:**

1. **Delete all `node_modules` directories:** This is the single most effective way to reclaim storage.
    * **Recommendation:** Run a command to find and delete all `node_modules` folders.
    * **Command:** `find . -name "node_modules" -type d -prune -exec rm -rf '{}' +`

2. **Re-installation:** When you need to work on a project, navigate to its directory and run `npm install` (or `pnpm install`/`yarn install`) to restore its dependencies.

---

## Phase 3: Log File Management

Log files (`*.log`) are scattered across the workspace. They are intended for temporary debugging and should not be committed to version control.

**Action Items:**

1. **Update `.gitignore` files:** Add `*.log` to the global or project-specific `.gitignore` file to prevent them from being tracked.
2. **Delete Existing Log Files:** Remove all current log files.
    * **Command:** `find . -name "*.log" -type f -delete`

---

## Phase 4: Project Standardization

Several utility scripts and project-related documents are located in `ProDevSetup`. A more standard structure would be to place scripts in a central `scripts` directory and move `ProDevSetup`'s contents.

**Action Items:**

1. **Create a Central `scripts` Directory:**
    * **Command:** `mkdir -p scripts`

2. **Move Utility Scripts:**
    * **Command:** `mv ProDevSetup/cleanup_mac.py ProDevSetup/create_hub.sh scripts/`

3. **Consolidate Documentation:** Review the markdown files in `ProDevSetup` and merge them into the relevant project's `docs` folder or a new top-level `docs` folder if they are general.

---

## Phase 5: Automated Cleanup Script

To maintain a clean environment, an automated script can perform the most common cleanup tasks.

**Action Item:**

* **Create `cleanup.sh`:** Create a shell script in the new `scripts/` directory to automate the deletion of `node_modules`, log files, and other temporary build artifacts.

    ```bash
    #!/bin/bash
    echo "Starting cleanup..."

    # Remove all node_modules directories
    echo "Removing node_modules..."
    find . -name "node_modules" -type d -prune -exec rm -rf '{}' +

    # Remove all log files
    echo "Removing log files..."
    find . -name "*.log" -type f -delete

    # Remove Next.js build artifacts
    echo "Removing .next directories..."
    find . -name ".next" -type d -prune -exec rm -rf '{}' +

    # Remove other common build artifacts
    echo "Removing dist, build, and coverage folders..."
    find . -name "dist" -type d -prune -exec rm -rf '{}' +
    find . -name "build" -type d -prune -exec rm -rf '{}' +
    find . -name "coverage" -type d -prune -exec rm -rf '{}' +

    echo "Cleanup complete!"
    ```
