#!/usr/bin/env bash
set -euo pipefail
src="$(cd "$(dirname "$0")" && pwd)"
target="${1:-.}"
mkdir -p "$target"
target="$(cd "$target" && pwd)"
python3 "$src/tools/install.py" "$src/template" "$target"
