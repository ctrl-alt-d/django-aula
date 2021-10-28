COMPOSE_FILE := docker-compose.yml

.PHONY: build start stop


build:
	${INFO} "Creating builder image..."
	@ docker-compose -f $(COMPOSE_FILE) build --no-cache web
	${INFO} "Build completed"

start:
	${INFO} "Running services"
	@ docker-compose up

serve:
	${INFO} "Running services"
	@ docker-compose up -d

stop:
	${INFO} "Stoping services"
	@ docker-compose down


# Aesthetics
YELLOW := "\e[1;33m"
NC := "\e[0m"

# Shell Functions
INFO := @bash -c '\
  printf $(YELLOW); \
  echo "=> $$1"; \
  printf $(NC)' SOME_VALUE