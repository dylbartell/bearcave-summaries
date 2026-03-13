#!/bin/bash
# sync_summary.sh — rebuild site from local sources and push to GitHub Pages
# Usage: ./sync_summary.sh [commit message]
# Run this after adding/updating markdown files in any source directory.

set -e

SITE_DIR="$(cd "$(dirname "$0")" && pwd)"

# Remove stale lock if present
rm -f "$SITE_DIR/.git/index.lock" 2>/dev/null || true

# Rebuild site from all configured sources
cd "$SITE_DIR"
python3 build.py

# Stage the built output and build infrastructure only
git add _site/index.html
git add build.py sync_summary.sh .github/ .gitignore

MSG="${1:-site rebuild $(date +%Y-%m-%d_%H-%M)}"
git commit -m "$MSG" || { echo "Nothing to commit"; exit 0; }

# Push
git push origin main
