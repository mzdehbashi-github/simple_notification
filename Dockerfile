# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Poetry files to the container
COPY pyproject.toml poetry.lock /app/

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

# Install Poetry
RUN pip install poetry

RUN poetry config virtualenvs.create false

# Install project dependencies using Poetry
RUN poetry install --no-dev

# Copy the rest of the application code to the container
COPY . /app/