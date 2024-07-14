.EXPORT_ALL_VARIABLES:
COMPOSE_FILE ?= ./build/docker-compose/docker-compose.yml
SERVICE_NAME ?= queue_bot

DOTENV_BASE_FILE ?= .env
-include $(DOTENV_BASE_FILE)


.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: start
start: build-queue-bot up # Build all the images and spin up the bot

.PHONY: restart
restart: down up # Restart the bot

.PHONY: up
up: # Run the docker-compose.yml file with all built docker images
	docker compose --profile mongodb -f $(COMPOSE_FILE) up -d
	docker compose --profile mongodb ps

.PHONY: down
down: # Shut down all the running docker services
	docker compose --profile mongodb -f $(COMPOSE_FILE) down

.PHONY: logs
logs: # Connect to the docker logs. You can see all the stuff happening inside
	docker compose --profile mongodb -f $(COMPOSE_FILE) logs --follow

.PHONY: test
test: # Start tests
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pytest -rP

.PHONY: build-queue-bot
build-queue-bot: # Build main docker image for queue-bot
	docker build \
		--tag=queue-bot \
		--file=build/docker/queue-bot/Dockerfile \
		.
