PYTHON ?= $(shell if command -v uv >/dev/null 2>&1; then echo "uv run --python 3.11 python"; else echo "python3"; fi)

.PHONY: test lint check run help

help:
	@echo "Доступные команды (Этап 1: REPL):"
	@echo "  make test   - Запуск unit-тестов"
	@echo "  make lint   - Проверка стандартов оформления кода"
	@echo "  make check  - Проверка стиля и запуск тестов"
	@echo "  make run    - Запуск эмулятора"

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) check_code_style.py

check: lint test

run:
	./run.sh
