#!/usr/bin/env bash
################################################################################
# E-commerce Agent System - Docker Network Setup
#
# Module 08: Monitoring & Observability
#
# Idempotently creates the external Docker network shared by the app stack
# (docker-compose.yml) and the monitoring stack
# (monitoring/docker-compose.monitoring.yml), so Prometheus/Loki can reach
# the app containers for scraping/log collection.
#
# Usage: ./scripts/setup/create_network.sh
################################################################################

set -euo pipefail

NETWORK_NAME="mlops-net"

if docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  echo "Docker network '$NETWORK_NAME' already exists."
else
  docker network create "$NETWORK_NAME"
  echo "Created docker network '$NETWORK_NAME'."
fi
