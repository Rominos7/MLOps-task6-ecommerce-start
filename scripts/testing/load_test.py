#!/usr/bin/env python3
"""
E-commerce Agent System - Load Test Generator

Module 08: Monitoring & Observability

A small, dependency-light traffic generator used to drive requests against
the running app so students can watch the resulting metrics and logs show
up in Prometheus / Grafana / Loki once they've instrumented the services.

Usage:
    python scripts/testing/load_test.py
    python scripts/testing/load_test.py --url http://localhost:8501 \
        --duration 60 --rate 2 --endpoints /,/health
"""

import argparse
import time

import requests
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ]
)

log = structlog.get_logger("load_test")


def run_load_test(base_url: str, duration: int, rate: float, endpoints: list[str]) -> None:
    """Issue GET requests against the given endpoints, round-robin, at ~rate req/sec."""
    interval = 1.0 / rate if rate > 0 else 1.0
    successes = 0
    failures = 0
    endpoint_index = 0
    start_time = time.monotonic()
    end_time = start_time + duration

    log.info(
        "load_test.start",
        base_url=base_url,
        duration=duration,
        rate=rate,
        endpoints=endpoints,
    )

    while time.monotonic() < end_time:
        endpoint = endpoints[endpoint_index % len(endpoints)]
        endpoint_index += 1
        url = base_url.rstrip("/") + endpoint

        request_start = time.monotonic()
        try:
            response = requests.get(url, timeout=10)
            elapsed_ms = (time.monotonic() - request_start) * 1000
            if response.ok:
                successes += 1
                log.info(
                    "request.success",
                    url=url,
                    status_code=response.status_code,
                    elapsed_ms=round(elapsed_ms, 2),
                    successes=successes,
                    failures=failures,
                )
            else:
                failures += 1
                log.warning(
                    "request.failed",
                    url=url,
                    status_code=response.status_code,
                    elapsed_ms=round(elapsed_ms, 2),
                    successes=successes,
                    failures=failures,
                )
        except requests.RequestException as exc:
            elapsed_ms = (time.monotonic() - request_start) * 1000
            failures += 1
            log.error(
                "request.error",
                url=url,
                error=str(exc),
                elapsed_ms=round(elapsed_ms, 2),
                successes=successes,
                failures=failures,
            )

        # Pace requests to roughly `rate` requests/sec.
        sleep_for = interval - (time.monotonic() - request_start)
        if sleep_for > 0:
            time.sleep(sleep_for)

    total = successes + failures
    log.info(
        "load_test.complete",
        total_requests=total,
        successes=successes,
        failures=failures,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate simple HTTP traffic against the running app for observability testing."
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8501",
        help="Base URL of the target service (default: http://localhost:8501)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Duration of the load test in seconds (default: 60)",
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=2,
        help="Target requests per second (default: 2)",
    )
    parser.add_argument(
        "--endpoints",
        default="/",
        help="Comma-separated list of endpoint paths to hit, round-robin (default: /)",
    )

    args = parser.parse_args()
    endpoints = [e.strip() for e in args.endpoints.split(",") if e.strip()]
    if not endpoints:
        endpoints = ["/"]

    run_load_test(base_url=args.url, duration=args.duration, rate=args.rate, endpoints=endpoints)


if __name__ == "__main__":
    main()
