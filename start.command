#!/bin/zsh
set -eu
cd -- "${0:A:h}"
exec .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765
