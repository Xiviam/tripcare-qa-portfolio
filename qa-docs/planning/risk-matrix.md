# Risk Matrix

| ID | Risk | Probability | Impact | Score | Mitigation | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| RISK-001 | Неверная авторизация открывает чужие данные | 3 | 5 | 15 | P0 API/Web role checks | QA |
| RISK-002 | Поиск бронирования возвращает неверного пассажира | 4 | 5 | 20 | P0 search and data isolation | QA |
| RISK-003 | Ошибки валидации контактов сохраняют некорректные данные | 4 | 4 | 16 | Boundary and negative tests | QA |
| RISK-004 | Стоимость багажа рассчитывается неверно | 3 | 4 | 12 | Decision table for pieces and weight | QA |
| RISK-005 | Повторный возврат ломает состояние бронирования | 3 | 5 | 15 | State transition coverage | QA |
| RISK-006 | Поиск базы знаний не находит релевантные статьи | 3 | 3 | 9 | Equivalence classes and case checks | QA |
| RISK-007 | Обращение в поддержку теряет приоритет или текст | 3 | 4 | 12 | Use-case and negative checks | QA |
| RISK-008 | Admin-функции видны customer | 2 | 5 | 10 | Role-based UI/API tests | QA |
| RISK-009 | Аудит не фиксирует критичные изменения | 3 | 4 | 12 | Integration checks with audit log | QA |
| RISK-010 | Mobile-клиент плохо обрабатывает offline state | 3 | 3 | 9 | Mobile smoke and error-state checklist | QA |