PYTHON ?= python3

.PHONY: run test migrate

run:
	$(PYTHON) main.py

test:
	pytest

migrate:
	alembic upgrade head

