PYTHON ?= $(shell if command -v uv >/dev/null 2>&1; then echo "uv run --python 3.11 python"; else echo "python3"; fi)

.PHONY: test lint check run test-cli test-vfs help

help:
	@echo "Доступные команды (Этап 5: touch, mv):"
	@echo "  make test      - Запуск unit-тестов"
	@echo "  make lint      - Проверка стандартов оформления кода"
	@echo "  make test-cli  - Проверка параметров командной строки"
	@echo "  make test-vfs  - Проверка загрузки вариантов VFS"
	@echo "  make check     - Полная проверка (стиль + тесты + скрипты ОС)"
	@echo "  make run       - Запуск эмулятора с VFS и демо-скриптом"

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) check_code_style.py

test-cli:
	bash os_scripts/test_cli_args.sh

test-vfs:
	bash os_scripts/test_vfs_variants.sh

check: lint test test-cli test-vfs

run:
	./run.sh --vfs vfs_data/vfs_medium.json --script emulator_scripts/stage5_demo.txt
