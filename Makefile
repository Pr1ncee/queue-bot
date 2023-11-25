.EXPORT_ALL_VARIABLES:
COMPOSE_FILE ?= ./docker-compose.yml
DOCKER_FILE ?= ./Dockerfile
IMAGE_NAME ?= queue_bot

DOTENV_BASE_FILE ?= .env
-include $(DOTENV_BASE_FILE)


.PHONY: test
test:
	docker compose -f $(COMPOSE_FILE) exec $(IMAGE_NAME) pytest -rP

.PHONY: docker-build-redis
docker-build-redis:
	docker build \
		--tag=redis \
		--file=Dockerfile-redis \
		.
