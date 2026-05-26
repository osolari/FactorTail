.DEFAULT_GOAL := help
SHELL := /bin/bash

PY ?= python
PIP ?= pip
PKG := factortail
SRC := src/$(PKG)
TESTS := tests

.PHONY: help install dev lint fmt typecheck test test-fast cov docs docs-serve docs-deploy clean run-all validate

help:  ## Show this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install package (editable).
	$(PIP) install -e .

dev:  ## Install with dev + docs + plot extras and fetch external data.
	$(PIP) install -e ".[dev,docs,plot,realdata]"
	pre-commit install
	$(PY) scripts/fetch_data.py || true   # tolerate offline / no-network installs

data:  ## Just fetch the external data (idempotent).
	$(PY) scripts/fetch_data.py

data-force:  ## Re-download all external data, ignoring cache.
	$(PY) scripts/fetch_data.py --force

lint:  ## Run ruff and black --check.
	ruff check $(SRC) $(TESTS) scripts
	black --check $(SRC) $(TESTS) scripts

fmt:  ## Auto-format with black + ruff --fix.
	ruff check --fix $(SRC) $(TESTS) scripts
	black $(SRC) $(TESTS) scripts

typecheck:  ## Run mypy.
	mypy $(SRC)

test:  ## Run pytest suite.
	pytest $(TESTS) -n auto

test-fast:  ## Quick unit tests (skip slow markers).
	pytest $(TESTS)/unit -m "not slow"

cov:  ## Tests with coverage.
	pytest $(TESTS) --cov=$(PKG) --cov-report=term-missing --cov-report=xml

docs:  ## Build mkdocs site (strict).
	mkdocs build --strict

docs-serve:  ## Serve docs locally on :8000.
	mkdocs serve

docs-deploy:  ## Deploy docs to gh-pages branch.
	mkdocs gh-deploy --force --no-history --remote-branch gh-pages

run-all:  ## Generate every figure/table CSV+PDF (slow).
	$(PY) -m factortail.cli run-all --config configs/all.yaml

validate:  ## Validate every result CSV against SCHEMA.md.
	$(PY) -m factortail.cli validate-schema results/SCHEMA.md

clean:  ## Remove build artifacts and caches.
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache .coverage coverage.xml htmlcov site
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
