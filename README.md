# TripCare QA Portfolio

Единый учебный QA-портфолио репозиторий для TripCare: тестовый стенд, ручная QA-документация и автотесты в одной структуре.

## Структура

- `platform` - TripCare Platform: FastAPI, React/Vite Web, Expo Mobile, Docker Compose, Swagger/OpenAPI и QA_BUG_MODE.
- `qa-docs` - ручное QA-портфолио: требования, test plan, risk matrix, 100 test cases, 15 bug reports, evidence и traceability matrix.
- `autotests` - автоматизация: 72 API Pytest, 36 Playwright specs и 10 Maestro mobile flows.

## Быстрый запуск

Backend и Web:

```bash
cd platform
docker compose up --build
```

Локальные проверки без Docker:

```bash
cd platform/services/api
python -m pytest -q

cd ../../apps/web
npm ci
npm run lint
npm run typecheck
npm test -- --run
npm run build
```

Проверка QA-документации:

```bash
cd qa-docs
python scripts/validate_portfolio.py
```

Автотесты:

```bash
cd autotests
python -m pytest api-tests -q
python scripts/count_tests.py

cd web-tests
npm ci
npm run list
```

## Фактические счетчики

- Manual QA cases: Web 38, Mobile 22, API 28, E2E 12, Total 100.
- Bug reports: 15.
- API autotests: 72.
- Web Playwright specs: 36.
- Mobile Maestro flows: 10.

Проект учебный: данные, пользователи и дефекты предназначены для локальной демонстрации QA-практик.

