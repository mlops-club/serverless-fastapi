# This Dockerfile is used for local development of the serverless FastAPI

FROM python:3.9

WORKDIR /app

RUN pip install uvicorn

COPY setup.cfg setup.py ./
COPY src/example_rest_api/__init__.py ./src/example_rest_api/
RUN pip install --editable ./

COPY ./ ./

# Expose our access port
EXPOSE ${DEV_PORT}
CMD uvicorn "example_rest_api.main:create_default_app" --reload --factory --workers 1 --host 0.0.0.0 --port ${DEV_PORT}
