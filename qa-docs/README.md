# TripCare QA Docs

Ручное QA-портфолио для учебного приложения TripCare Platform из папки `../platform`.

Проект учебный. Формулировки описывают демонстрационный QA-стенд и не выдают учебный опыт за коммерческий.

## Навигация

- [Product requirements](requirements/product-requirements.md)
- [Use cases](requirements/use-cases.md)
- [Test plan](planning/test-plan.md)
- [Risk matrix](planning/risk-matrix.md)
- [Scope and estimation](planning/scope-and-estimation.md)
- [Traceability CSV](planning/requirements-traceability-matrix.csv)
- [Traceability XLSX](planning/requirements-traceability-matrix.xlsx)
- [Test cases](test-cases/index.md)
- [Bug reports](bug-reports/)
- [Test summary report](reports/test-summary-report.md)

## Фактическая статистика

Блок ниже проверяется командой python scripts/validate_portfolio.py и должен совпадать с фактическими файлами.

<!-- stats:start -->
- Web test cases: 38
- Mobile test cases: 22
- API test cases: 28
- E2E test cases: 12
- Total test cases: 100
- Bug reports: 15
<!-- stats:end -->

## Проверка целостности

Запуск из корня репозитория:

    python scripts/validate_portfolio.py
