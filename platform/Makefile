.PHONY: up down reset seed test lint backend-test frontend-test frontend-build screenshots

up:
	docker compose up --build

down:
	docker compose down

reset:
	python services/api/scripts/reset_db.py

seed:
	python services/api/scripts/seed_db.py

test: backend-test frontend-test

lint:
	cd services/api && python -m ruff check tripcare_api tests
	cd apps/web && npm run lint

backend-test:
	cd services/api && python -m pytest -q

frontend-test:
	cd apps/web && npm test -- --run

frontend-build:
	cd apps/web && npm run build

screenshots:
	node scripts/capture-screenshots.mjs
