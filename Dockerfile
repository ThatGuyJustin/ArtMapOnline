FROM python:3.12-alpine AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONCACHEPREFIX=/tmp/ArtmapOnineCache

FROM python-base AS python-poetry-build-base

ENV POETRY_VERSION=2.4.1 \
    POETRY_HOME="/opt/poetry" \
    VIRTUAL_ENV="/opt/pysetup/venv"

RUN APKG_UPDATE=1 \
    && apk add --no-cache --virtual .build-deps \
        curl \
        py3-pip

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN poetry self add poetry-plugin-export

FROM python-poetry-build-base AS python-poetry-export

# export requirements.txt for pip install
WORKDIR /opt/poetry-export

COPY api/poetry.lock api/pyproject.toml ./
RUN poetry export -f requirements.txt --output requirements-build.txt --without-hashes

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements-build.txt


# Vite build
FROM node:24-alpine AS vite-build-base
COPY frontend/package.json frontend/package-lock.json /frontend/
WORKDIR /frontend
RUN npm ci

FROM vite-build-base AS vite-build
COPY frontend/ /frontend/
RUN npm run build

FROM python-base AS artmaponline

ENV PATH="/opt/venv/bin:$PATH"

RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S -D -H -G appgroup appuser

WORKDIR /opt/artmaponline

USER appuser

COPY --chown=appuser:appgroup api/ .
COPY --chown=appuser:appgroup --from=python-poetry-export /opt/venv /opt/venv
COPY --chown=appuser:appgroup --from=vite-build /frontend/build/client ./static

ENV HOME=/tmp

CMD ["gunicorn", "app:app"]