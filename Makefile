check:
	poetry run ruff check .

format:
	poetry run ruff format .

make run:
	poetry run python src/yatl/test_server.py