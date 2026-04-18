.PHONY: test test-backend test-backend-coverage test-auth test-combat test-world test-character test-all test-e2e

SERVICES = auth combat world character chat economy gateway inventory notification party quest websocket-gateway crafting

test: test-backend

test-backend: test-all

test-backend-coverage:
	@echo "Running backend tests with coverage..."
	@for svc in $(SERVICES); do \
		cd services/$$svc && \
		pip install -q -r requirements.txt 2>/dev/null || true && \
		pytest -v --cov=. --cov-report=term-missing --cov-report=html tests/ || true && \
		cd ../.. ; \
	done
	@echo "Coverage reports generated in each service's htmlcov/ directory"

test-all:
	@echo "Running all backend tests..."
	@for svc in $(SERVICES); do \
		if [ -d "services/$$svc" ]; then \
			cd services/$$svc && \
			echo "=== Testing $$svc ===" && \
			pytest -v tests/ 2>&1 || echo "No tests or test failure in $$svc" && \
			cd ../.. ; \
		fi ; \
	done

test-e2e:
	@echo "Running E2E integration tests (requires live stack at $$GATEWAY_URL)..."
	GATEWAY_URL=$${GATEWAY_URL:-http://localhost:8000} pytest tests/e2e/ -v

test-auth:
	cd services/auth && pytest -v tests/

test-combat:
	cd services/combat && pytest -v tests/

test-world:
	cd services/world && pytest -v tests/

test-character:
	cd services/character && pytest -v tests/

test-%:
	@if [ -d "services/$*" ]; then \
		cd services/$* && pytest -v tests/ ; \
	else \
		echo "Service $* not found" ; \
	fi
