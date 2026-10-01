#!/usr/bin/env bash
# Запуски эмулятора с различными вариантами VFS (Этап 3).
# Окно закрывается само, если стартовый скрипт дошёл до exit.
# Иначе окно остаётся открытым: закрыть его командой exit.

set -e

cd "$(dirname "${BASH_SOURCE[0]}")/.."

DATA="vfs_data"
SCRIPTS="emulator_scripts"

run_case() {
    echo ""
    echo "--- $1 ---"
    shift
    echo "\$ ./run.sh $*"
    ./run.sh "$@"
}

run_case "Минимальная VFS" \
    --vfs "$DATA/vfs_minimal.json" --script "$SCRIPTS/vfs_minimal_demo.txt"
run_case "VFS с несколькими файлами" \
    --vfs "$DATA/vfs_medium.json" --script "$SCRIPTS/stage4_demo.txt"
run_case "VFS с 3 уровнями вложенности" \
    --vfs "$DATA/vfs_deep.json" --script "$SCRIPTS/vfs_deep_demo.txt"
run_case "Ошибка: файл VFS не найден" --vfs "$DATA/no_such_vfs.json"
run_case "Ошибка: неверный формат VFS" --vfs "$DATA/vfs_corrupted.json"

echo ""
echo "Все запуски с вариантами VFS выполнены."
