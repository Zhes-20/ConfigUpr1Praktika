#!/usr/bin/env bash
# Запуски эмулятора со всеми параметрами командной строки (Этап 2).
# Окно закрывается само, если стартовый скрипт дошёл до exit.
# Иначе окно остаётся открытым: закрыть его командой exit.

set -e

cd "$(dirname "${BASH_SOURCE[0]}")/.."

VFS="vfs_data/vfs_medium.json"
SCRIPTS="emulator_scripts"

run_case() {
    echo ""
    echo "--- $1 ---"
    shift
    echo "\$ ./run.sh $*"
    ./run.sh "$@"
}

run_case "Без параметров"
run_case "Только --vfs" --vfs "$VFS"
run_case "Только --script" --script "$SCRIPTS/stage2_demo.txt"
run_case "--vfs и --script" --vfs "$VFS" --script "$SCRIPTS/stage2_demo.txt"
run_case "Короткие -v и -s" -v "$VFS" -s "$SCRIPTS/stage2_demo.txt"
run_case "Ошибка: скрипт не найден" --script "$SCRIPTS/no_such_script.txt"
run_case "Ошибка в скрипте" --script "$SCRIPTS/script_syntax_error.txt"

echo ""
echo "Все запуски с параметрами командной строки выполнены."
