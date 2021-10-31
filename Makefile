.PHONY: build start serve stop down load_demo_data


build:
	${INFO} "Creating builder image..."
	@ docker-compose build --no-cache web
	${INFO} "Build completed"

start:
	${INFO} "Running services"
	@ docker-compose up

serve:
	${INFO} "Running services"
	@ docker-compose up -d

stop:
	${INFO} "Stoping services"
	@ docker-compose stop

down:
	${INFO} "Stoping services and deleting the db"
	@ docker-compose down

load_demo_data:
	${INFO} "Load demo data"
	@ docker-compose exec web python manage.py loaddata aula/apps/*/fixtures/dades.json
	@ docker-compose exec web python manage.py loaddemodata

# Aesthetics
YELLOW := "\e[1;33m"
NC := "\e[0m"

# Shell Functions
INFO := @bash -c '\
  printf $(YELLOW); \
  echo "=> $$1"; \
  printf $(NC)' SOME_VALUE