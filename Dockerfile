FROM python:3.11-alpine

WORKDIR /app

COPY . .

RUN pip install poetry

COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-root --no-dev