PYTHON ?= $(shell if command -v uv >/dev/null 2>&1; then echo "uv run --python 3.11 python"; else echo "python3"; fi)

.PHONY: test lint check run test-cli test-vfs help

help:
	@echo "Доступные команды:"
	@echo "  make test      - запуск unit-тестов"
	@echo "  make lint      - проверка оформления кода"
	@echo "  make check     - проверка оформления и unit-тесты"
	@echo "  make test-cli  - запуски эмулятора с параметрами CLI (окна GUI)"
	@echo "  make test-vfs  - запуски эмулятора с вариантами VFS (окна GUI)"
	@echo "  make run       - запуск эмулятора с VFS и демо-скриптом"

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) check_code_style.py

test-cli:
	bash os_scripts/test_cli_args.sh

test-vfs:
	bash os_scripts/test_vfs_variants.sh

check: lint test

run:
	./run.sh --vfs vfs_data/vfs_medium.json \
		--script emulator_scripts/stage5_demo.txt
