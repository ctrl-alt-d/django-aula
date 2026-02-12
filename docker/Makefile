.PHONY: build serve stop down logs \
		dev-build dev-serve dev-stop dev-down dev-logs dev-load_demo_data\
		dev-setup dev-makemigrations dev-shell dev-bash

# --- VARIABLES ---
COMPOSE_DEMO = docker-compose.yml
COMPOSE_DEV  = docker-compose.dev.yml

# ----------- Aesthetics -----------
YELLOW := "\e[1;33m"
GREEN  := "\e[1;32m"
NC     := "\e[0m"

# Funció per a missatges informatius (Groc)
INFO := @bash -c '\
  printf $(YELLOW); \
  echo "=> $$1"; \
  printf $(NC)' SOME_VALUE

# Funció per a missatges d'èxit (Verd)
EXITO := @bash -c '\
  printf $(GREEN); \
  echo "✅ $$1"; \
  printf $(NC)' SOME_VALUE

# --- COMANDES DE LA DEMO (AUTOMÀTICA) ---

build:
	$(INFO) "Construint imatge de la Demo..."
	docker compose -f $(COMPOSE_DEMO) build

serve:
	$(INFO) "Aixecant serveis de la Demo..."
	docker compose -f $(COMPOSE_DEMO) up -d
	$(EXITO) "Demo en marxa al port 8000"

stop:
	$(INFO) "Aturant serveis de la Demo..."
	docker compose -f $(COMPOSE_DEMO) stop

down:
	$(INFO) "Eliminant contenidors i xarxes de la Demo..."
	docker compose -f $(COMPOSE_DEMO) down

logs:
	docker compose -f $(COMPOSE_DEMO) logs -f web

# --- COMANDES DE DESENVOLUPAMENT (DEV) ---

dev-build:
	$(INFO) "Construint imatge de Desenvolupament..."
	docker compose -f $(COMPOSE_DEV) build

dev-serve:
	$(INFO) "Aixecant serveis de Desenvolupament (amb volums en viu)..."
	docker compose -f $(COMPOSE_DEV) up -d
	$(EXITO) "Entorn de Dev en marxa al port 8000"

dev-stop:
	$(INFO) "Aturant serveis de Dev..."
	docker compose -f $(COMPOSE_DEV) stop

dev-down:
	$(INFO) "Eliminant contenidors i xarxes de Dev..."
	docker compose -f $(COMPOSE_DEV) down

dev-logs:
	docker compose -f $(COMPOSE_DEV) logs -f web

# Carrega dades usant el mètode tradicional de fixtures i comandes Django
dev-load_demo_data:
	$(INFO) "Carregant fixtures i dades de demo (mètode tradicional)..."
	@docker compose -f $(COMPOSE_DEV) exec web python manage.py loaddata aula/apps/*/fixtures/dades.json
	@docker compose -f $(COMPOSE_DEV) exec web python manage.py loaddemodata
	$(EXITO) "Dades tradicionals carregades."

# --- GESTIÓ DE DADES I DJANGO (DEV) ---

dev-setup:
	$(INFO) "Executant script de càrrega inicial de dades..."
	docker exec -it dev_web docker/carrega_inicial.sh

dev-makemigrations:
	$(INFO) "Comprovant canvis als models i creant migracions..."
	docker exec -it dev_web python manage.py makemigrations

dev-shell:
	$(INFO) "Entrant a la consola de Django..."
	docker exec -it dev_web python manage.py shell

dev-bash:
	$(INFO) "Entrant al terminal del contenidor web..."
	docker exec -it dev_web bash
