.PHONY: setup check smoke test lint typecheck compose-config up down postgres-health postgres-connect

setup:
	python -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e ".[dev]"

smoke:
	python -c "from service_ops.health import foundation_status; print(foundation_status())"

test:
	pytest

lint:
	ruff check .

typecheck:
	mypy src

compose-config:
	docker compose --env-file .env.example config

up:
	docker compose --env-file .env.example up -d --wait

down:
	docker compose --env-file .env.example down

postgres-health:
	docker compose --env-file .env.example exec postgres pg_isready -U service_ops_app -d service_ops

postgres-connect:
	docker compose --env-file .env.example exec postgres psql -U service_ops_app -d service_ops -c "SELECT 1 AS connection_ok;"

check: smoke test lint typecheck compose-config
