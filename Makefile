# Makefile untuk development workflow

.PHONY: help install run test lint format clean docker-up docker-down pipeline dashboard

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make pipeline      - Run data pipeline"
	@echo "  make dashboard     - Run Streamlit dashboard"
	@echo "  make db-init       - Initialize database"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Lint code"
	@echo "  make format        - Format code with black"
	@echo "  make docker-up     - Start Docker services"
	@echo "  make docker-down   - Stop Docker services"
	@echo "  make clean         - Clean up cache files"

install:
	pip install -r requirements.txt

pipeline:
	python -m src.main

dashboard:
	streamlit run dashboard.py

db-init:
	python -m src.database.init_db

test:
	pytest tests/ -v --cov=src

lint:
	flake8 src/ tests/
	mypy src/ --ignore-missing-imports || true

format:
	black src/ tests/

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f postgres

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf build/ dist/ *.egg-info/
