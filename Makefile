.PHONY: install install-runtime run worker test

install:
	pip install -e .[dev]

install-runtime:
	pip install --no-build-isolation -e .[runtime]

run:
	uvicorn main:app --reload --app-dir src

worker:
	python -m worker

test:
	pytest -q
