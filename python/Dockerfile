FROM python:3.11.5
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y build-essential libgtk-3-dev
COPY pyproject.toml .
RUN python3 -m pip install --upgrade pip && python3 -m pip install .[dev,gui]
