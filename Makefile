PYTHON ?= $(shell if command -v uv >/dev/null 2>&1; then echo "uv run --python 3.11 python"; else echo "python3"; fi)

.PHONY: test lint check run test-cli help

help:
	@echo "Доступные команды (Этап 2: Конфигурация и запуск):"
	@echo "  make test      - Запуск unit-тестов"
	@echo "  make lint      - Проверка стандартов оформления кода"
	@echo "  make test-cli  - Проверка параметров командной строки и скриптов"
	@echo "  make check     - Полная проверка (стиль + тесты + CLI)"
	@echo "  make run       - Запуск эмулятора с демо-скриптом"

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) check_code_style.py

test-cli:
	bash os_scripts/test_cli_args.sh

check: lint test test-cli

run:
	./run.sh --script emulator_scripts/stage2_demo.txt
