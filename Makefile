check:
	poetry run ruff check .

format:
	poetry run ruff format .

types:
	poetry run mypy .

yaml:
	poetry run python -m src.yatl.run

test:
	poetry run pytest

clear_env:
	poetry env remove --all 