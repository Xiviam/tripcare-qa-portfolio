# Automation Strategy

## API
Pytest проверяет авторизацию, роли, поиск бронирований, контакты, багаж, возвраты, базу знаний, support tickets, пагинацию, HTTP-коды и schema validation.

## Web
Playwright использует locators по role, label и text. Трассы, видео и screenshots включаются только при падениях. В CI retries не больше 1.

## Mobile
Maestro flows покрывают smoke/E2E сценарии Expo Android. Запуск требует Android emulator или реальное устройство с Expo Go.