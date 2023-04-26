# syntax=docker.io/docker/dockerfile-upstream:1.2.0
# =========================================================
# === Build Backend Base                                ===
# =========================================================
FROM mcr.microsoft.com/vscode/devcontainers/python:0-3.7
#FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # opencv dependencies
  ffmpeg libsm6 libxext6 \
  # supervisor
  supervisor \
  && rm -rf /var/lib/apt/lists/*

# =========================================================
# === Build Backend Production                          ===
# =========================================================

WORKDIR /app


RUN python -m pip install --upgrade pip

COPY ./requirements.txt .
# Allow user to manage deps in dev container
RUN --mount=type=cache,target=/root/.cache/pip \
  pip install -r ./requirements.txt --default-timeout=1000

COPY ./entrypoints/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./entrypoints/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./ .

# COPY supervisor_services/process_tasks.conf /etc/supervisor/conf.d/gunicorn.conf
# RUN service supervisor force-reload
# RUN supervisorctl reread && supervisorctl update

EXPOSE 9999

WORKDIR /app

ENTRYPOINT ["/entrypoint"]