# Test Plan

## Цель
Проверить критичные пользовательские сценарии TripCare Platform в нормальном режиме QA_BUG_MODE=false и подготовить отдельные bug reports для QA_BUG_MODE=true.

## Scope
- Web: авторизация, поиск, детали, контакты, багаж, возврат, база знаний, поддержка, роли и состояния.
- Mobile: Expo Android smoke, offline/error/loading states.
- API: контракты, роли, HTTP-коды, валидация, пагинация, schema validation.
- E2E: сквозные customer/support/admin сценарии.

## Test design techniques
- Классы эквивалентности для валидных и невалидных PNR, email, phone, query.
- Граничные значения для phone length, baggage pieces, weight_kg, page_size.
- Таблицы решений для baggage price и role permissions.
- Переходы состояний для refund statuses confirmed -> refund_pending -> refunded.
- Pairwise для браузеров, устройств и ролей.
- Error guessing для пустых сообщений, неверных credentials и повторных refund requests.
- Use-case testing для customer self-service и support flow.