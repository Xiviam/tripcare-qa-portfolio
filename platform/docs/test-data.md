# Тестовые данные

## Пользователи

| Роль | Email | Пароль |
|---|---|---|
| customer | customer@example.com | Customer123! |
| support_agent | agent@example.com | Agent123! |
| admin | admin@example.com | Admin123! |

## Бронирования

| PNR | Фамилия | Статус | Часовой пояс | Особенности |
|---|---|---|---|---|
| TC1001 | Ivanov | confirmed | Europe/Moscow | Один пассажир, прямой рейс |
| TC1002 | Petrova | changed | Europe/Samara | Два пассажира, измененный рейс |
| TC1003 | Smirnov | cancelled | Asia/Yekaterinburg | Отмененное бронирование |
| TC1004 | Kuznetsova | refund_pending | Europe/Moscow | Возврат в обработке |
| TC1005 | Sokolov | refunded | Europe/Kaliningrad | Возврат завершен |
| TC1006 | Popova | confirmed | Asia/Novosibirsk | Три пассажира |
| TC1007 | Lebedev | changed | Europe/Moscow | Дополнительный багаж |
| TC1008 | Kozlova | confirmed | Asia/Irkutsk | Обращение в поддержку |
| TC1009 | Morozov | cancelled | Europe/Moscow | Отмена до вылета |
| TC1010 | Novikova | confirmed | Asia/Vladivostok | Международный рейс |
| TC1011 | Fedorov | refund_pending | Europe/Moscow | Несколько обращений |
| TC1012 | Mikhailova | refunded | Europe/Samara | История багажа и возврата |

## Наборы данных

- valid-customer-flow: TC1001, customer@example.com, валидные email и телефон.
- refund-flow: TC1004 и TC1011, статусы refund_pending.
- support-flow: TC1008 и TC1011, обращения с разными приоритетами.
