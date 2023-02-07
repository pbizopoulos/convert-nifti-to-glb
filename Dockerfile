FROM mcr.microsoft.com/playwright/python:v1.30.0-focal
WORKDIR /usr/src/app
COPY pyproject.toml .
RUN python3 -m pip install --upgrade pip && python3 -m pip install .[dev]
