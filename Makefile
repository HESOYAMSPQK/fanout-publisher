.PHONY: help build up down restart logs clean test init-db

help: ## Показать эту справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Собрать Docker образы
	docker compose build

up: ## Запустить все сервисы
	docker compose up -d

down: ## Остановить все сервисы
	docker compose down

restart: ## Перезапустить все сервисы
	docker compose restart

logs: ## Показать логи всех сервисов
	docker compose logs -f

logs-api: ## Показать логи API
	docker compose logs -f api

logs-worker: ## Показать логи Worker
	docker compose logs -f worker

logs-bot: ## Показать логи Bot
	docker compose logs -f bot

clean: ## Удалить все контейнеры и volumes
	docker compose down -v

init-db: ## Инициализировать базу данных
	docker compose exec api python scripts/init_db.py

test: ## Запустить тесты
	docker compose exec api pytest

test-api: ## Тестировать API
	docker compose exec api python scripts/probe_ingest.py

shell-api: ## Открыть shell в API контейнере
	docker compose exec api bash

shell-worker: ## Открыть shell в Worker контейнере
	docker compose exec worker bash

shell-bot: ## Открыть shell в Bot контейнере
	docker compose exec bot bash

shell-db: ## Открыть psql в БД
	docker compose exec postgres psql -U fanout_user -d fanout_publisher

redis-cli: ## Открыть Redis CLI
	docker compose exec redis redis-cli

ps: ## Показать статус контейнеров
	docker compose ps

youtube-token: ## Получить YouTube refresh token
	docker compose exec api python scripts/get_youtube_token.py


