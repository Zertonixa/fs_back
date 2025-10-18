.PHONY: format lint check

format:
	@echo "🧹 Running isort & black to format code..."
	isort .
	black .

lint:
	@echo "🔍 Running ruff to lint code..."
	ruff check .

check:
	@echo "🧪 Checking formatting (ruff, isort, black)..."
	ruff check .
	isort --check-only .
	black --check .

fix:
	@echo "🛠 Auto-fixing with ruff (if possible)..."
	ruff check . --fix
