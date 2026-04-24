lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typing:
	poetry run mypy .

integration_tests:
	poetry run python -m src.yatl.run

unit_test:
	poetry run pytest

clear_env:
	poetry env remove --all 