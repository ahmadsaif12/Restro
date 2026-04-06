.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser fmt lint precommit-install precommit-run

COMPOSE = docker compose --env-file .env

help:
	@echo "Targets:"
	@echo "  make up                Start containers"
	@echo "  make build             Build app image"
	@echo "  make down              Stop containers"
	@echo "  make logs              Tail app logs"
	@echo "  make shell             Bash into app container"
	@echo "  make migrate           Run Django migrations"
	@echo "  make makemigrations    Create migrations"
	@echo "  make createsuperuser   Create admin user"
	@echo "  make fmt               Format with black"
	@echo "  make lint              Lint with flake8"
	@echo "  make precommit-install Install git hooks"
	@echo "  make precommit-run     Run pre-commit on all files"

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
