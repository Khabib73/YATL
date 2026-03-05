check:
	poetry run ruff check . --fix

format:
	poetry run ruff format .

make run_server:
	poetry run python src/yatl/test_server.py

make run_tests:
	poetry run python src/yatl/parser.py