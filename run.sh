#!/usr/bin/env bash
# Скрипт запуска эмулятора оболочки

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

if command -v uv >/dev/null 2>&1; then
    exec uv run --python 3.11 python -m src.main "$@"
fi

export TK_SILENCE_DEPRECATION=1
exec python3 -m src.main "$@"
