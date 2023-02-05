# This Dockerfile is used for local development of the serverless FastAPI

FROM python:3.9

WORKDIR /app

RUN pip install uvicorn

COPY setup.cfg setup.py ./
COPY src/example_rest_api/__init__.py ./src/example_rest_api/
RUN pip install --editable ./[base]
RUN pip install -r ./aws-lambda/requirements.txt
RUN pip install gunicorn
RUN opentelemetry-bootstrap --action install

COPY ./ ./

# Expose our access port
EXPOSE ${DEV_PORT}

# opentelemetry entrypoint
ENV OTEL_SERVICE_NAME=example-rest-api--local
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
ENV OTEL_PYTHON_LOG_CORRELATION=true
ENV OTEL_PYTHON_LOG_LEVEL=info
# ENTRYPOINT opentelemetry-instrument

# CMD \
#     OTEL_PYTHON_LOG_CORRELATION=true \
#     OTEL_PYTHON_LOG_LEVEL=info \
#     opentelemetry-instrument uvicorn "example_rest_api.main:create_default_app" --reload --factory --workers 1 --host 0.0.0.0 --port ${DEV_PORT}

CMD \
    OTEL_PYTHON_LOG_CORRELATION=true \
    OTEL_PYTHON_LOG_LEVEL=info \
    opentelemetry-instrument -- gunicorn "example_rest_api.main:create_default_app()" \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 1 \
    --bind 0.0.0.0:${DEV_PORT} \
    --reload
