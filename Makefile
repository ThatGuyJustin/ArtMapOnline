IMAGE_NAME := artmaponline
CONTAINER_NAME := artmaponline-local
PORT_MAPPING   := 8080:8000

.PHONY: build run develop


build:
	docker build -t $(IMAGE_NAME):latest .

run:
	docker run -d --name $(CONTAINER_NAME) -p $(PORT_MAPPING) $(IMAGE_NAME):latest

develop: build
	docker run --rm --name $(CONTAINER_NAME) -p $(PORT_MAPPING) $(IMAGE_NAME):latest