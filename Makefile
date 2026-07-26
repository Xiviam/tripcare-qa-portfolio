.PHONY: platform-test platform-web qa-docs-test autotests-api autotests-count test

platform-test:
	cd platform/services/api && python -m pytest -q

platform-web:
	cd platform/apps/web && npm run lint && npm run typecheck && npm test -- --run && npm run build

qa-docs-test:
	cd qa-docs && python scripts/validate_portfolio.py

autotests-api:
	cd autotests && python -m pytest api-tests -q

autotests-count:
	cd autotests && python scripts/count_tests.py

test: platform-test platform-web qa-docs-test autotests-api autotests-count

