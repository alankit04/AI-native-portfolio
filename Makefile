.PHONY: install install-runtime bootstrap run worker test

install:
	pip install -e .[dev]

install-runtime:
	pip install --no-build-isolation -e .[runtime]

bootstrap:
	./scripts/bootstrap_env.sh

run:
	uvicorn main:app --reload --app-dir src

worker:
	python -m worker

test:
	pytest -q
