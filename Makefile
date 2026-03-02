.PHONY: help install lint test clean build run

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies with pip"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with ruff"
	@echo "  make test       - Run tests with coverage"
	@echo "  make build      - Build Docker image"
	@echo "  make clean      - Remove cache files"

install:
	pip install -r requirements.txt

lint:
	ruff check .

format:
	ruff format .

test:
	pytest --cov=src --cov-report=term-missing

test-quick:
	pytest

build:
	docker build -t odm-pipeline -f docker/Dockerfile .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
