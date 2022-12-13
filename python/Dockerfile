FROM python:3.11.1
ENV PIP_NO_CACHE_DIR=1
WORKDIR /work
COPY pyproject.toml .
RUN python3 -m pip install --upgrade pip && python3 -m pip install .
