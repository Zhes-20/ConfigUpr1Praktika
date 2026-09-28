#!/usr/bin/env bash
# Скрипт запуска эмулятора оболочки (Этап 1: REPL)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/." && pwd)"
cd "$PROJECT_ROOT"

if command -v uv >/dev/null 2>&1; then
    exec uv run --python 3.11 python -m src.main "$@"
elif [ -x "$HOME/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3" ]; then
    exec "$HOME/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3" -m src.main "$@"
else
    export TK_SILENCE_DEPRECATION=1
    exec python3 -m src.main "$@"
fi
