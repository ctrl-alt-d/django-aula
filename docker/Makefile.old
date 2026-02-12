.PHONY: build serve stop down logs

# ----------- DEMO -----------

build:
	${INFO} "Creating builder image..."
	@ docker compose -f docker-compose.yml build --no-cache web
	${INFO} "Build completed"

serve:
	${INFO} "Running demo services (detached)"
	@ docker compose -f docker-compose.yml up -d

stop:
	${INFO} "Stopping demo services"
	@ docker compose -f docker-compose.yml stop

down:
	${INFO} "Stopping demo services and deleting DB"
	@ docker compose -f docker-compose.yml down -v

logs:
	${INFO} "Showing logs"
	@ docker compose -f docker-compose.yml logs -f

# ----------- Aesthetics -----------
YELLOW := "\e[1;33m"
NC := "\e[0m"

INFO := @bash -c '\
  printf $(YELLOW); \
  echo "=> $$1"; \
  printf $(NC)' SOME_VALUE
