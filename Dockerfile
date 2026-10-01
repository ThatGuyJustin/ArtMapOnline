FROM python:3.12-alpine AS python-poetry-build-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=2.4.1 \
    POETRY_HOME="/opt/poetry" \
    VIRTUAL_ENV="/opt/pysetup/venv" \
    PYTHONCACHEPREFIX=/tmp/ArtmapOnineCache

RUN APKG_UPDATE=1 \
    && apk add --no-cache --virtual .build-deps \
        build-base \
        curl \
        git \
        libffi-dev \
        openssl-dev \
        python3-dev \
        py3-pip

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Vite build
FROM node:24-alpine AS vite-build-base
COPY frontend/package.json frontend/package-lock.json /frontend/
WORKDIR /frontend
RUN npm ci

FROM vite-build-base AS vite-build
COPY frontend/ /frontend/
RUN npm run build

FROM python-poetry-build-base AS builder-base

COPY api/poetry.lock api/pyproject.toml ./
RUN poetry install

RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S -D -H -G appgroup appuser

FROM builder-base AS artmaponline

WORKDIR /opt/artmaponline

USER appuser

COPY --chown=appuser:appgroup api/ .
COPY --chown=appuser:appgroup --from=vite-build /frontend/build/client ./static

ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=8000 \
    FLASK_DEBUG=0

CMD ["flask", "run"]