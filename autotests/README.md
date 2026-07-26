# TripCare Autotests

Автотесты для учебного QA-стенда TripCare Platform из папки `../platform`.

Цель репозитория - показать API, Web и Mobile automation, кроссбраузерные прогоны, Allure artifacts и воспроизводимый запуск. Основной набор рассчитан на QA_BUG_MODE=false и не содержит постоянных skip/xfail.

## Быстрый старт

1. Установить зависимости:

    make bootstrap

2. Поднять TripCare Platform:

    make up

3. Запустить проверки:

    make test-api
    make test-web
    make test-mobile
    make test-all

## Фактические счетчики

Команда scripts/count_tests.py считает реальные тесты из коллекции pytest, Playwright specs и Maestro flows.

<!-- stats:start -->
- API tests: 72
- Web tests: 36
- Mobile flows: 10
<!-- stats:end -->

## Команды

- make bootstrap - инициализирует submodule, Python и Node зависимости.
- make up - запускает TripCare Platform.
- make test-api - запускает Pytest API набор с Allure results.
- make test-web - запускает Playwright Chromium/Firefox/WebKit/mobile emulation.
- make test-mobile - запускает Maestro flows локально на Android/Expo окружении.
- make report - собирает Allure report, если установлен allure CLI.
- make clean - удаляет локальные артефакты прогонов.

Mobile CI оставлен отдельным manual/smoke контуром, потому что стабильный Android emulator на GitHub-hosted runner требует отдельной инфраструктуры.
