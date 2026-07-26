.PHONY: bootstrap up test-api test-web test-mobile test-all report clean count

bootstrap:
	python -m pip install -r ../platform/services/api/requirements-dev.txt -r api-tests/requirements.txt
	cd web-tests && npm install && npx playwright install --with-deps

up:
	cd ../platform && docker compose up --build

test-api:
	python -m pytest api-tests -q --alluredir=allure-results/api

test-web:
	cd web-tests && npm test

test-mobile:
	maestro test mobile-tests/maestro

test-all: test-api test-web

report:
	allure generate allure-results --clean -o allure-report

count:
	python scripts/count_tests.py

clean:
	rm -rf allure-results allure-report playwright-report test-results
