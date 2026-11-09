#!/usr/bin/env bash
# For the starter repo's maintainer only: rebuild .starter-managed (the list of files the
# starter ships, with their content hashes) before each push, so members' maintain.sh can
# tell which of their files are unedited and safe to update.
set -euo pipefail
cd "$(dirname "$0")/.."
git ls-files --cached --others --exclude-standard | grep -vxF .starter-managed | while read -r f; do echo "$(git hash-object "$f") $f"; done > .starter-managed
echo "Wrote .starter-managed ($(wc -l < .starter-managed | tr -d ' ') files). Commit it with your changes."
