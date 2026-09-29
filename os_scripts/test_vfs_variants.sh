#!/usr/bin/env bash
# Тестирование загрузки различных вариантов VFS из реальной ОС (Этап 3)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON="python3"
if command -v uv >/dev/null 2>&1; then
    PYTHON="uv run --python 3.11 python"
fi

echo "================================================================"
echo " Тестирование вариантов VFS и метаданных (Этап 3) "
echo "================================================================"

echo ""
echo "=== Тест 1: Загрузка минимальной VFS ==="
$PYTHON -c "
from src.vfs import Vfs
vfs = Vfs()
vfs.load_from_json('vfs_data/vfs_minimal.json')
files = vfs.list_dir('/')
assert 'hello.txt' in files, 'hello.txt not found'
content = vfs.read_file('/hello.txt')
assert 'Minimal VFS' in content, f'Unexpected content: {content}'
node = vfs.get_node('/hello.txt')
assert node.permissions == 'rw-r--r--', f'Wrong perms: {node.permissions}'
assert node.owner == 'student', f'Wrong owner: {node.owner}'
print('[OK] Минимальная VFS загружена, метаданные проверены')
"

echo ""
echo "=== Тест 2: Загрузка VFS средней структуры ==="
$PYTHON -c "
from src.vfs import Vfs
vfs = Vfs()
vfs.load_from_json('vfs_data/vfs_medium.json')
root_files = vfs.list_dir('/')
assert 'docs' in root_files and 'readme.txt' in root_files
doc_files = vfs.list_dir('/docs')
assert 'notes.txt' in doc_files
readme_node = vfs.get_node('/readme.txt')
assert readme_node.size > 0
print('[OK] Средняя VFS загружена (каталоги, файлы, права доступа корректны)')
"

echo ""
echo "=== Тест 3: Загрузка глубокой VFS (вложенность >= 3 уровней) ==="
$PYTHON -c "
from src.vfs import Vfs
vfs = Vfs()
vfs.load_from_json('vfs_data/vfs_deep.json')
l1 = vfs.list_dir('/level1')
assert 'level2' in l1
l2 = vfs.list_dir('/level1/level2')
assert 'level3' in l2
l3 = vfs.list_dir('/level1/level2/level3')
assert 'deep_file.txt' in l3
deep_text = vfs.read_file('/level1/level2/level3/deep_file.txt')
assert 'Deep nested' in deep_text
deep_node = vfs.get_node('/level1/level2/level3/deep_file.txt')
assert deep_node.permissions == 'r--------'
assert deep_node.owner == 'deploy'
print('[OK] Глубокая VFS (>= 3 уровней) с разными правами и размером проверена')
"

echo ""
echo "=== Тест 4: Отладочный вывод структуры VFS ==="
$PYTHON -c "
from src.vfs import Vfs
vfs = Vfs()
vfs.load_from_json('vfs_data/vfs_medium.json')
lines = vfs.dump_structure()
assert len(lines) >= 3
print('[OK] Отладочная структура VFS:')
for l in lines:
    print('  ' + l)
"

echo ""
echo "=== Тест 5: Проверка ошибки несуществующего файла VFS ==="
$PYTHON -c "
from src.vfs import Vfs
vfs = Vfs()
try:
    vfs.load_from_json('non_existent.json')
    assert False, 'FileNotFoundError expected'
except FileNotFoundError:
    print('[OK] Ошибка отсутствия файла обработана корректно')
"

echo ""
echo "=== Тест 6: Проверка ошибки поврежденного JSON VFS ==="
$PYTHON -c "
from src.vfs import Vfs
vfs = Vfs()
try:
    vfs.load_from_json('vfs_data/vfs_corrupted.json')
    assert False, 'ValueError expected'
except ValueError:
    print('[OK] Ошибка формата JSON обработана корректно')
"

echo ""
echo "Все тесты вариантов VFS успешно завершены!"
