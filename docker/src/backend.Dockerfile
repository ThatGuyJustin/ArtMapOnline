FROM python:3.12-alpine AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONCACHEPREFIX=/tmp/ArtmapOnineCache \
    POETRY_VERSION=2.4.1 \
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

FROM python-base AS artmap-live-runner

WORKDIR /opt/artmaponline

COPY api/pyproject.toml api/poetry.lock /opt/artmaponline/
RUN poetry install

RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S -D -H -G appgroup appuser

USER appuser

ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=8000 \
    FLASK_DEBUG=1

CMD ["python", "app.py"]
