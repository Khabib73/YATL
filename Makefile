check:
	poetry run ruff check .

format:
	poetry run ruff format .

check-types:
	poetry run mypy .

server:
	poetry run python src/yatl/base_api.py

yaml:
	poetry run python -m src.yatl.run

test:
	poetry run pytest