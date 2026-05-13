.PHONY: help build up down restart logs shell db-shell db-query migrate makemigrations createsuperuser fmt lint precommit-install precommit-run backup frontend-logs frontend-shell

COMPOSE = docker compose --env-file .env
DB_CONTAINER = db
DB_NAME = $(shell grep DB_NAME .env | cut -d '=' -f2)
DB_USER = $(shell grep DB_USER .env | cut -d '=' -f2)
DB_PASSWORD = $(shell grep DB_PASSWORD .env | cut -d '=' -f2)

help:
	@echo "Targets:"
	@echo "  make up              - Start all services"
	@echo "  make build           - Build all images"
	@echo "  make down            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - Tail backend logs"
	@echo "  make frontend-logs   - Tail frontend logs"
	@echo "  make shell           - Open backend shell"
	@echo "  make frontend-shell  - Open frontend shell"
	@echo "  make db-shell        - Open database shell"
	@echo "  make db-query q='SQL'"
	@echo "  make migrate"
	@echo "  make makemigrations"
	@echo "  make createsuperuser"
	@echo "  make fmt"
	@echo "  make lint"
	@echo "  make precommit-install"
	@echo "  make precommit-run"
	@echo "  make backup"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

restart: down up

logs:
	$(COMPOSE) logs -f app

shell:
	$(COMPOSE) exec app bash

db-shell:
	$(COMPOSE) exec -e PGPASSWORD=$(DB_PASSWORD) $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)

db-query:
	$(COMPOSE) exec -T -e PGPASSWORD=$(DB_PASSWORD) $(DB_CONTAINER) \
	psql -U $(DB_USER) -d $(DB_NAME) -c "$(q)"

migrate:
	$(COMPOSE) exec app python manage.py migrate --noinput

makemigrations:
	$(COMPOSE) exec app python manage.py makemigrations

createsuperuser:
	$(COMPOSE) exec app python manage.py createsuperuser

fmt:
	$(COMPOSE) exec app black .

lint:
	$(COMPOSE) exec app flake8 .

precommit-install:
	pre-commit install

precommit-run:
	pre-commit run --all-files

backup:
	$(COMPOSE) exec -T $(DB_CONTAINER) \
	pg_dump -U $(DB_USER) $(DB_NAME) > db_backup_$(shell date +%Y%m%d_%H%M%S).sql

frontend-logs:
	$(COMPOSE) logs -f frontend

frontend-shell:
	$(COMPOSE) exec frontend sh