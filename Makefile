.PHONY: help setup start stop test clean network monitoring-up monitoring-down load-test

help:
	@echo "Available commands:"
	@echo "  make setup            - Initialize project"
	@echo "  make start            - Start all services"
	@echo "  make stop             - Stop all services"
	@echo "  make test             - Run tests"
	@echo "  make clean            - Clean up"
	@echo "  make network          - Create shared docker network"
	@echo "  make monitoring-up    - Start app + monitoring stack"
	@echo "  make monitoring-down  - Stop monitoring stack"
	@echo "  make load-test        - Generate traffic against the running app"

setup:
	./scripts/setup/init_project.sh

start:
	docker-compose -f docker/docker-compose.yml up -d

stop:
	docker-compose -f docker/docker-compose.yml down

test:
	pytest tests/

clean:
	docker-compose -f docker/docker-compose.yml down -v
	rm -rf data/*.csv data/*.json

network:
	./scripts/setup/create_network.sh

monitoring-up: network
	docker-compose -f docker-compose.yml up -d
	docker-compose -f monitoring/docker-compose.monitoring.yml up -d
	@echo "Grafana:    http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"
	@echo "Loki:       http://localhost:3100"

monitoring-down:
	docker-compose -f monitoring/docker-compose.monitoring.yml down
	docker-compose -f docker-compose.yml down

load-test:
	python scripts/testing/load_test.py