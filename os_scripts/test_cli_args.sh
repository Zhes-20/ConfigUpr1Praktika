#!/usr/bin/env bash
# Тестирование параметров командной строки эмулятора оболочки (Этап 2)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON="python3"
if command -v uv >/dev/null 2>&1; then
    PYTHON="uv run --python 3.11 python"
fi

echo "================================================================"
echo " Тестирование параметров командной строки и стартового скрипта "
echo "================================================================"

echo ""
echo "--- Тест 1: запуск без параметров командной строки ---"
$PYTHON -c "
from src.config import parse_cli_args
cfg = parse_cli_args([])
assert cfg.vfs_path == '', 'vfs_path should be empty'
assert cfg.script_path == '', 'script_path should be empty'
print('[OK] Дефолтная конфигурация корректна')
"

echo ""
echo "--- Тест 2: длинные параметры (--vfs и --script) ---"
$PYTHON -c "
from src.config import parse_cli_args
cfg = parse_cli_args(['--vfs', 'disk.json', '--script', 'emulator_scripts/stage2_demo.txt'])
assert cfg.vfs_path == 'disk.json'
assert cfg.script_path == 'emulator_scripts/stage2_demo.txt'
print('[OK] Длинные флаги успешно разобраны')
"

echo ""
echo "--- Тест 3: короткие параметры (-v и -s) ---"
$PYTHON -c "
from src.config import parse_cli_args
cfg = parse_cli_args(['-v', 'disk.json', '-s', 'start.txt'])
assert cfg.vfs_path == 'disk.json'
assert cfg.script_path == 'start.txt'
print('[OK] Короткие флаги успешно разобраны')
"

echo ""
echo "--- Тест 4: проверка команды conf-dump ---"
$PYTHON -c "
from src.config import Config
from src.shell_core import ShellCore
cfg = Config(vfs_path='my_vfs.json', script_path='run.txt', username='tester', hostname='testhost')
shell = ShellCore(config=cfg)
code, out = shell.execute_line('conf-dump')
assert code == 0, 'conf-dump failed'
assert 'vfs_path: my_vfs.json' in out
assert 'script_path: run.txt' in out
assert 'username: tester' in out
assert 'hostname: testhost' in out
print('[OK] conf-dump вывел все параметры')
"

echo ""
echo "--- Сценарий 1: штатный запуск стартового скрипта ---"
$PYTHON -c "
from src.shell_core import ShellCore
shell = ShellCore()
code, out = shell.execute_script_file('emulator_scripts/stage2_demo.txt')
assert code == 0, f'Expected 0, got {code}'
assert 'vfs_path:' in out
assert 'ls (stub)' in out
print('[OK] Штатный скрипт выполнен успешно:')
print(out)
"

echo ""
echo "--- Сценарий 2: ошибка — файл скрипта не существует ---"
$PYTHON -c "
from src.shell_core import ShellCore
shell = ShellCore()
code, out = shell.execute_script_file('emulator_scripts/nonexistent_file.txt')
assert code != 0, 'Expected non-zero code for missing file'
assert 'file not found' in out
print('[OK] Ошибка несуществующего файла корректно обработана:')
print(out)
"

echo ""
echo "--- Сценарий 3: синтаксическая ошибка в скрипте ---"
$PYTHON -c "
from src.shell_core import ShellCore
shell = ShellCore()
code, out = shell.execute_script_file('emulator_scripts/script_syntax_error.txt')
assert code != 0, 'Expected non-zero code for syntax error'
assert 'unexpected leading whitespace' in out
print('[OK] Синтаксическая ошибка в скрипте прервала выполнение:')
print(out)
"

echo ""
echo "Все тесты параметров командной строки и скриптов успешно пройдены!"
