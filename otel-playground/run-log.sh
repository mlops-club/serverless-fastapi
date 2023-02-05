#!/bin/bash

THIS_DIR=$(cd $(dirname $0); pwd)

# This env var must be set to true in order to enable trace context injection into logs
# by calling logging.basicConfig() and setting a logging format that makes use of the injected tracing variables.
export OTEL_PYTHON_LOG_CORRELATION=true

# export OTEL_PYTHON_LOG_FORMAT

# This env var can be used to set a custom logging level: info, error, debug, warning
export OTEL_PYTHON_LOG_LEVEL=info

OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=0.0.0.0:4317 \
OTEL_TRACES_EXPORTER=console,otlp \
OTEL_METRICS_EXPORTER=console \
OTEL_SERVICE_NAME=otel-playground-app \
opentelemetry-instrument -- python ${THIS_DIR}/log.py
