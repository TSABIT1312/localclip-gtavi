#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "==================================================="
echo "  LocalClip GTA VI - Auto Clipper (Linux/macOS)    "
echo "==================================================="
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi
exec python3 -m uvicorn app:app --host 127.0.0.1 --port 8765
