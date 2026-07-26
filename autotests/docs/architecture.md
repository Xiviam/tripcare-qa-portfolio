# Autotest Architecture

~~~mermaid
flowchart LR
  API[Pytest API tests] --> SUT[TripCare Platform]
  WEB[Playwright Web tests] --> SUT
  MOB[Maestro Mobile flows] --> SUT
  SUT --> DB[(PostgreSQL or test SQLite)]
  API --> ALLURE[Allure results]
  WEB --> PW[Playwright report]
~~~