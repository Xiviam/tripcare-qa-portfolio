# TripCare Platform

Учебный QA-стенд для сервиса самообслуживания пассажиров: Web, Mobile, REST API, PostgreSQL, Swagger/OpenAPI, Docker Compose и контролируемый режим учебных дефектов.

## Быстрый запуск

1. Скопируйте переменные окружения:

~~~bash
cp .env.example .env
~~~

2. Запустите стенд:

~~~bash
docker compose up --build
~~~

3. Откройте:

- Web: http://localhost:5173
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Healthcheck: http://localhost:8000/health

Если Docker недоступен, backend можно запустить локально:

~~~bash
cd services/api
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m uvicorn tripcare_api.main:app --reload
~~~

Web-клиент отдельно:

~~~bash
cd apps/web
npm install
npm run dev
~~~

Mobile-клиент запускается отдельно от Docker Compose:

~~~bash
cd apps/mobile
npm install
npm run start
~~~

## Тестовые аккаунты

| Роль | Email | Пароль |
|---|---|---|
| customer | customer@example.com | Customer123! |
| support_agent | agent@example.com | Agent123! |
| admin | admin@example.com | Admin123! |

## Команды проверки

~~~bash
make backend-test
make frontend-test
make frontend-build
make lint
docker compose config
~~~

## QA Bug Mode

По умолчанию QA_BUG_MODE=false, и приложение работает корректно. При QA_BUG_MODE=true включаются ровно 15 детерминированных учебных дефектов Web/API. Список идентификаторов находится в [docs/bug-mode.md](docs/bug-mode.md). Детали дефектов не выводятся в пользовательском интерфейсе.

## Документация

- [Архитектура](docs/architecture.md)
- [API и роли](docs/api.md)
- [Тестовые данные](docs/test-data.md)
- [QA Bug Mode](docs/bug-mode.md)
- [Скриншоты](docs/screenshots/)

## Структура

~~~text
apps/web        React + TypeScript + Vite
apps/mobile     Expo React Native + TypeScript
services/api    FastAPI + SQLAlchemy + Alembic
services/db     PostgreSQL через Docker Compose
docs            Архитектура, API, тестовые данные, скриншоты
scripts         Healthcheck, reset/seed, screenshots
~~~

Проект учебный: тестовые пользователи и данные предназначены только для локальной демонстрации QA-практик.
