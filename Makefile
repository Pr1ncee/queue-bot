.EXPORT_ALL_VARIABLES:
COMPOSE_FILE ?= ./build/docker-compose/docker-compose.yml
DOCKER_FILE ?= ./Dockerfile
IMAGE_NAME ?= queue_bot

DOTENV_BASE_FILE ?= .env
-include $(DOTENV_BASE_FILE)


.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: start-bot
start-bot: docker-build-all docker-up

.PHONY: docker-build-all
docker-build-all: docker-build-queue-bot docker-build-redis

.PHONY: docker-up
docker-up: # This command run the docker-compose.yml file with all built docker images
	docker compose -f $(COMPOSE_FILE) up -d
	docker compose ps

.PHONY: docker-down
docker-down: # This command shut down all the running docker services
	docker compose -f $(COMPOSE_FILE) down

.PHONY: docker-logs
docker-logs: # This command connects to the docker logs. You can see all the stuff happening inside
	docker compose -f $(COMPOSE_FILE) logs --follow

.PHONY: test
test: # This command starts tests
	docker compose -f $(COMPOSE_FILE) exec $(IMAGE_NAME) pytest -rP

.PHONY: docker-build-queue-bot
docker-build-queue-bot: # This command builds main docker image for queue-bot
	docker build \
		--tag=queue-bot \
		--file=build/docker/queue-bot/Dockerfile \
		.

.PHONY: docker-build-redis
docker-build-redis: # This command builds docker imager for Redis database
	docker build \
		--tag=queue-bot-redis \
		--file=build/docker/redis/Dockerfile-redis \
		.
