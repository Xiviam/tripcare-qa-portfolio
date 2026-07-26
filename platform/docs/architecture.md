# Архитектура TripCare

TripCare разделен на клиентские приложения, REST API и PostgreSQL. Backend хранит бронирования, пассажиров, багаж, возвраты, обращения и аудит изменений.

~~~mermaid
flowchart LR
  Web["React Web App"] --> API["FastAPI REST API"]
  Mobile["Expo Mobile App"] --> API
  API --> DB[("PostgreSQL")]
  API --> Swagger["Swagger UI / OpenAPI"]
  API --> Audit["Audit Log"]
  QA["QA_BUG_MODE"] --> API
  QA --> Web
~~~

## Основные решения

- API возвращает единый формат ошибок: {"error": {"code": "...", "message": "...", "details": {}}}.
- В нормальном режиме включена серверная валидация email, телефона, статусов возврата, обязательных полей и ролей.
- JWT используется как учебный механизм авторизации. Секрет задается через JWT_SECRET.
- Docker Compose поднимает web, api и db. Mobile-клиент запускается отдельно через Expo.
- Тестовые данные создаются детерминированно seed-скриптом.
