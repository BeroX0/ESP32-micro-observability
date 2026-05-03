help:
	@echo "Targets: help up-core down-core logs ps"

up-core:
	docker compose --env-file .env -f backend/compose/compose.core.yml up -d

down-core:
	docker compose --env-file .env -f backend/compose/compose.core.yml down

logs:
	docker compose --env-file .env -f backend/compose/compose.core.yml logs -f

ps:
	docker compose --env-file .env -f backend/compose/compose.core.yml ps
